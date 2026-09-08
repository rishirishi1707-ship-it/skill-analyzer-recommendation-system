# =========================================================
# routes/student_routes.py
# Skill Analyzer & Recommendation System
# =========================================================

from flask import (
    Blueprint,
    request,
    jsonify,
    current_app
)

from config import db

from services.skill_extractor import (
    extract_skills_from_documents
)

from services.llm_worker import (
    start_llm_analysis
)

from services.job_matcher import (
    recommend_jobs
)

from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

from werkzeug.utils import secure_filename

from bson import ObjectId
from bson.errors import InvalidId

import jwt
import os
import uuid
import json

from datetime import (
    datetime,
    timedelta,
    timezone
)

from functools import wraps


# =========================================================
# OPTIONAL DOCUMENT EXTRACTION LIBRARIES
# =========================================================

try:

    from pypdf import PdfReader

    PDF_AVAILABLE = True

except ImportError:

    PDF_AVAILABLE = False


try:

    from docx import Document

    DOCX_AVAILABLE = True

except ImportError:

    DOCX_AVAILABLE = False


# =========================================================
# BLUEPRINT
# =========================================================

student_routes = Blueprint(
    "student_routes",
    __name__
)


# =========================================================
# MONGODB COLLECTIONS
# =========================================================

students_collection = db[
    "students"
]

jobs_collection = db[
    "job_requirements"
]


# =========================================================
# JWT SECRET KEY
# =========================================================

JWT_SECRET_KEY = os.getenv(
    "JWT_SECRET_KEY"
)

if not JWT_SECRET_KEY:

    raise RuntimeError(
        "JWT_SECRET_KEY is not configured"
    )


# =========================================================
# ALLOWED FILE EXTENSIONS
# =========================================================

ALLOWED_RESUME_EXTENSIONS = {
    "pdf",
    "docx"
}


ALLOWED_CERTIFICATE_EXTENSIONS = {
    "pdf",
    "docx"
}


# =========================================================
# MAXIMUM FILE SIZE
# =========================================================

MAX_FILE_SIZE = 10 * 1024 * 1024

# 10 MB per file


# =========================================================
# HELPER - CURRENT UTC TIME
# =========================================================

def utc_now():

    return datetime.now(
        timezone.utc
    )


# =========================================================
# HELPER - FILE EXTENSION
# =========================================================

def get_file_extension(
    filename
):

    if not filename:

        return ""

    filename = filename.lower()

    if "." not in filename:

        return ""

    return filename.rsplit(
        ".",
        1
    )[1]


# =========================================================
# HELPER - CHECK ALLOWED EXTENSION
# =========================================================

def allowed_file(
    filename,
    allowed_extensions
):

    extension = get_file_extension(
        filename
    )

    return (
        extension
        in
        allowed_extensions
    )


# =========================================================
# HELPER - EXTRACT PDF TEXT
# =========================================================

def extract_pdf_text(
    file_path
):

    if not PDF_AVAILABLE:

        print(
            "pypdf is not installed."
        )

        return ""

    try:

        reader = PdfReader(
            file_path
        )

        extracted_text = []

        for page in reader.pages:

            text = page.extract_text()

            if text:

                extracted_text.append(
                    text
                )

        return "\n".join(
            extracted_text
        ).strip()

    except Exception as error:

        print(
            "PDF extraction error:",
            error
        )

        return ""


# =========================================================
# HELPER - EXTRACT DOCX TEXT
# =========================================================

def extract_docx_text(
    file_path
):

    if not DOCX_AVAILABLE:

        print(
            "python-docx is not installed."
        )

        return ""

    try:

        document = Document(
            file_path
        )

        extracted_text = []


        # -------------------------------------------------
        # PARAGRAPHS
        # -------------------------------------------------

        for paragraph in document.paragraphs:

            text = paragraph.text.strip()

            if text:

                extracted_text.append(
                    text
                )


        # -------------------------------------------------
        # TABLES
        # -------------------------------------------------

        for table in document.tables:

            for row in table.rows:

                row_text = []

                for cell in row.cells:

                    text = cell.text.strip()

                    if text:

                        row_text.append(
                            text
                        )

                if row_text:

                    extracted_text.append(
                        " | ".join(
                            row_text
                        )
                    )


        return "\n".join(
            extracted_text
        ).strip()

    except Exception as error:

        print(
            "DOCX extraction error:",
            error
        )

        return ""


# =========================================================
# HELPER - EXTRACT DOCUMENT TEXT
# =========================================================

def extract_document_text(
    file_path,
    filename
):

    extension = get_file_extension(
        filename
    )

    if extension == "pdf":

        return extract_pdf_text(
            file_path
        )

    if extension == "docx":

        return extract_docx_text(
            file_path
        )

    return ""


# =========================================================
# HELPER - SAVE UPLOADED FILE
# =========================================================

def save_uploaded_file(
    uploaded_file,
    folder,
    allowed_extensions
):

    if not uploaded_file:

        return None


    original_filename = (
        uploaded_file.filename
    )


    if not original_filename:

        return None


    # -----------------------------------------------------
    # CHECK FILE TYPE
    # -----------------------------------------------------

    if not allowed_file(
        original_filename,
        allowed_extensions
    ):

        raise ValueError(
            "Unsupported file type. "
            "Only PDF and DOCX files are supported."
        )


    # -----------------------------------------------------
    # SECURE FILENAME
    # -----------------------------------------------------

    safe_filename = secure_filename(
        original_filename
    )


    if not safe_filename:

        raise ValueError(
            "Invalid filename"
        )


    # -----------------------------------------------------
    # CREATE UNIQUE FILENAME
    # -----------------------------------------------------

    unique_filename = (
        uuid.uuid4().hex
        + "_"
        + safe_filename
    )


    file_path = os.path.join(
        folder,
        unique_filename
    )


    # -----------------------------------------------------
    # SAVE FILE
    # -----------------------------------------------------

    uploaded_file.save(
        file_path
    )


    # -----------------------------------------------------
    # CHECK FILE SIZE
    # -----------------------------------------------------

    file_size = os.path.getsize(
        file_path
    )


    if file_size > MAX_FILE_SIZE:

        try:

            os.remove(
                file_path
            )

        except Exception:

            pass

        raise ValueError(
            "File size exceeds 10 MB"
        )


    # -----------------------------------------------------
    # EXTRACT TEXT
    # -----------------------------------------------------

    extracted_text = (
        extract_document_text(
            file_path,
            original_filename
        )
    )


    return {

        "original_filename":
            original_filename,

        "stored_filename":
            unique_filename,

        "file_path":
            file_path,

        "file_size":
            file_size,

        "file_type":
            get_file_extension(
                original_filename
            ),

        "extracted_text":
            extracted_text,

        "uploaded_at":
            utc_now()

    }


# =========================================================
# JWT TOKEN VERIFICATION
# =========================================================

def token_required(
    function
):

    @wraps(function)
    def decorated(
        *args,
        **kwargs
    ):

        auth_header = request.headers.get(
            "Authorization"
        )


        # -------------------------------------------------
        # TOKEN MISSING
        # -------------------------------------------------

        if not auth_header:

            return jsonify({

                "success": False,

                "message":
                    "Authorization token is required"

            }), 401


        # -------------------------------------------------
        # INVALID FORMAT
        # -------------------------------------------------

        if not auth_header.startswith(
            "Bearer "
        ):

            return jsonify({

                "success": False,

                "message":
                    "Invalid authorization format. "
                    "Use: Bearer <token>"

            }), 401


        token = auth_header.split(
            " ",
            1
        )[1].strip()


        if not token:

            return jsonify({

                "success": False,

                "message":
                    "Authorization token is empty"

            }), 401


        # -------------------------------------------------
        # DECODE TOKEN
        # -------------------------------------------------

        try:

            payload = jwt.decode(

                token,

                JWT_SECRET_KEY,

                algorithms=[
                    "HS256"
                ]

            )


            student_id = payload.get(
                "student_id"
            )


            if not student_id:

                return jsonify({

                    "success": False,

                    "message":
                        "Invalid token: student ID missing"

                }), 401


        except jwt.ExpiredSignatureError:

            return jsonify({

                "success": False,

                "message":
                    "Token has expired. Please login again."

            }), 401


        except jwt.InvalidTokenError:

            return jsonify({

                "success": False,

                "message":
                    "Invalid token"

            }), 401


        # -------------------------------------------------
        # CALL PROTECTED FUNCTION
        # -------------------------------------------------

        return function(
            student_id,
            *args,
            **kwargs
        )


    return decorated


# =========================================================
# STUDENT REGISTRATION
# =========================================================

@student_routes.route(
    "/register",
    methods=["POST"]
)
def register_student():

    # =====================================================
    # GET STUDENT DATA
    # =====================================================

    data = None


    # -----------------------------------------------------
    # JSON REQUEST
    # -----------------------------------------------------

    if request.is_json:

        data = request.get_json(
            silent=True
        )


    # -----------------------------------------------------
    # MULTIPART FORM REQUEST
    # -----------------------------------------------------

    else:

        student_data = request.form.get(
            "student_data"
        )


        if student_data:

            try:

                data = json.loads(
                    student_data
                )

            except Exception:

                return jsonify({

                    "success": False,

                    "message":
                        "Invalid student_data JSON"

                }), 400


    # -----------------------------------------------------
    # VALIDATE DATA
    # -----------------------------------------------------

    if not data:

        return jsonify({

            "success": False,

            "message":
                "Invalid JSON data"

        }), 400


    # =====================================================
    # DEBUG
    # =====================================================

    print(
        "\n========================================"
    )

    print(
        "DATA RECEIVED FROM FRONTEND"
    )

    print(
        "========================================"
    )

    print(
        data
    )

    print(
        "========================================\n"
    )


    # =====================================================
    # REQUIRED FIELDS
    # =====================================================

    required_fields = [

        "full_name",

        "register_number",

        "email",

        "password"

    ]


    for field in required_fields:

        if not data.get(field):

            return jsonify({

                "success": False,

                "message":
                    f"{field} is required"

            }), 400


    # =====================================================
    # EXTRACT NESTED DATA
    # =====================================================

    academic_data = data.get(
        "academic",
        {}
    )

    if not isinstance(
        academic_data,
        dict
    ):

        academic_data = {}


    career_data = data.get(
        "career_preferences",
        {}
    )

    if not isinstance(
        career_data,
        dict
    ):

        career_data = {}


    resume_data = data.get(
        "resume",
        {}
    )

    if not isinstance(
        resume_data,
        dict
    ):

        resume_data = {}


    skills_data = data.get(
        "skills",
        []
    )

    if not isinstance(
        skills_data,
        list
    ):

        skills_data = []


    certifications_data = data.get(
        "certifications",
        []
    )

    if not isinstance(
        certifications_data,
        list
    ):

        certifications_data = []


    projects_data = data.get(
        "projects",
        []
    )

    if not isinstance(
        projects_data,
        list
    ):

        projects_data = []


    # =====================================================
    # CHECK EXISTING STUDENT
    # =====================================================

    existing_student = (
        students_collection.find_one({

            "$or": [

                {
                    "personal.email":
                        data["email"]
                },

                {
                    "personal.register_number":
                        data["register_number"]
                }

            ]

        })
    )


    if existing_student:

        return jsonify({

            "success": False,

            "message":
                "Student already registered"

        }), 409


    # =====================================================
    # UPLOAD DIRECTORIES
    # =====================================================

    resume_folder = current_app.config.get(
        "RESUME_FOLDER"
    )


    certificate_folder = current_app.config.get(
        "CERTIFICATE_FOLDER"
    )


    # =====================================================
    # UPLOAD RESUME
    # =====================================================

    uploaded_resume = None


    resume_file = request.files.get(
        "resume"
    )


    if resume_file:

        if not resume_folder:

            return jsonify({

                "success": False,

                "message":
                    "Resume upload folder is not configured"

            }), 500


        try:

            uploaded_resume = (
                save_uploaded_file(

                    resume_file,

                    resume_folder,

                    ALLOWED_RESUME_EXTENSIONS

                )
            )


        except ValueError as error:

            return jsonify({

                "success": False,

                "message":
                    str(error)

            }), 400


    # =====================================================
    # UPLOAD CERTIFICATES
    # =====================================================

    uploaded_certificates = []


    certificate_files = (
        request.files.getlist(
            "certificates"
        )
    )


    if certificate_files:

        if not certificate_folder:

            return jsonify({

                "success": False,

                "message":
                    "Certificate upload folder is not configured"

            }), 500


        for certificate_file in certificate_files:

            if not certificate_file.filename:

                continue


            try:

                certificate_info = (
                    save_uploaded_file(

                        certificate_file,

                        certificate_folder,

                        ALLOWED_CERTIFICATE_EXTENSIONS

                    )
                )


                if certificate_info:

                    uploaded_certificates.append(
                        certificate_info
                    )


            except ValueError as error:

                return jsonify({

                    "success": False,

                    "message":
                        str(error)

                }), 400


    # =====================================================
    # EXTRACT RESUME TEXT
    # =====================================================

    resume_extracted_text = ""


    if uploaded_resume:

        resume_extracted_text = (
            uploaded_resume.get(
                "extracted_text",
                ""
            )
            or ""
        )


    # =====================================================
    # EXTRACT CERTIFICATE TEXT
    # =====================================================

    certificate_extracted_texts = []


    for certificate in uploaded_certificates:

        extracted_text = (
            certificate.get(
                "extracted_text",
                ""
            )
            or ""
        )


        if extracted_text:

            certificate_extracted_texts.append(
                extracted_text
            )


    # =====================================================
    # AUTOMATIC SKILL EXTRACTION
    # =====================================================

    try:

        detected_skills = (
            extract_skills_from_documents(

                resume_text=
                    resume_extracted_text,

                certificate_texts=
                    certificate_extracted_texts

            )
        )


    except Exception as error:

        print(
            "Skill extraction error:",
            error
        )


        detected_skills = {

            "skills": [],

            "categorized_skills": {},

            "skill_details": [],

            "resume_skills": [],

            "certificate_skills": [],

            "document_count": 0

        }


    # =====================================================
    # DEBUG DETECTED SKILLS
    # =====================================================

    print(
        "\n========================================"
    )

    print(
        "AUTOMATICALLY DETECTED SKILLS"
    )

    print(
        "========================================"
    )

    print(
        detected_skills
    )

    print(
        "========================================\n"
    )


    # =====================================================
    # MERGE CERTIFICATE INFORMATION
    # =====================================================

    final_certifications = []


    for index, certification in enumerate(
        certifications_data
    ):

        if not isinstance(
            certification,
            dict
        ):

            continue


        certification_copy = dict(
            certification
        )


        if index < len(
            uploaded_certificates
        ):

            certification_copy[
                "file"
            ] = uploaded_certificates[
                index
            ]


        final_certifications.append(
            certification_copy
        )


    # =====================================================
    # STANDARDIZED CERTIFICATES
    # =====================================================

    standardized_certificates = []


    for certificate in uploaded_certificates:

        standardized_certificate = {

            "original_name":
                certificate.get(
                    "original_filename"
                ),

            "stored_filename":
                certificate.get(
                    "stored_filename"
                ),

            "file_path":
                certificate.get(
                    "file_path"
                ),

            "file_type":
                certificate.get(
                    "file_type"
                ),

            "file_size":
                certificate.get(
                    "file_size"
                ),

            "extracted_text":
                certificate.get(
                    "extracted_text",
                    ""
                ),

            "uploaded_at":
                certificate.get(
                    "uploaded_at"
                )

        }


        standardized_certificates.append(
            standardized_certificate
        )


    # =====================================================
    # RESUME DATA
    # =====================================================

    final_resume = {

        "has_resume":
            uploaded_resume is not None,

        "resume_name": (

            uploaded_resume.get(
                "original_filename"
            )

            if uploaded_resume

            else

            resume_data.get(
                "resume_name"
            )

        ),

        "extracted_text":
            resume_extracted_text,

        "file":
            uploaded_resume

    }


    # =====================================================
    # CREATE STUDENT DOCUMENT
    # =====================================================

    student = {

        # =================================================
        # PERSONAL
        # =================================================

        "personal": {

            "full_name":
                data.get(
                    "full_name"
                ),

            "register_number":
                data.get(
                    "register_number"
                ),

            "roll_number":
                data.get(
                    "roll_number"
                ),

            "email":
                data.get(
                    "email"
                ),

            "mobile":
                data.get(
                    "mobile"
                ),

            "gender":
                data.get(
                    "gender"
                ),

            "date_of_birth":
                data.get(
                    "date_of_birth"
                ),

            "department":
                data.get(
                    "department"
                ),

            "degree":
                data.get(
                    "degree"
                ),

            "year_of_study":
                data.get(
                    "year_of_study"
                ),

            "section":
                data.get(
                    "section"
                ),

            "semester":
                data.get(
                    "semester"
                )

        },


        # =================================================
        # ACADEMIC
        # =================================================

        "academic": {

            "college_name":
                academic_data.get(
                    "college_name"
                ),

            "university":
                academic_data.get(
                    "university"
                ),

            "branch":
                academic_data.get(
                    "branch"
                ),

            "current_cgpa":
                academic_data.get(
                    "current_cgpa"
                ),

            "tenth_percentage":
                academic_data.get(
                    "tenth_percentage"
                ),

            "twelfth_percentage":
                academic_data.get(
                    "twelfth_percentage"
                ),

            "number_of_arrears":
                academic_data.get(
                    "number_of_arrears"
                ),

            "backlog_history":
                academic_data.get(
                    "backlog_history"
                ),

            "academic_year":
                academic_data.get(
                    "academic_year"
                ),

            "graduation_year":
                academic_data.get(
                    "graduation_year"
                )

        },


        # =================================================
        # MANUAL SKILLS
        # =================================================

        "skills":
            skills_data,


        # =================================================
        # DETECTED SKILLS
        # =================================================

        "detected_skills": {

            "resume":
                detected_skills.get(
                    "resume_skills",
                    []
                ),

            "certificates":
                detected_skills.get(
                    "certificate_skills",
                    []
                ),

            "all":
                detected_skills.get(
                    "skills",
                    []
                ),

            "categorized_skills":
                detected_skills.get(
                    "categorized_skills",
                    {}
                ),

            "details":
                detected_skills.get(
                    "skill_details",
                    []
                ),

            "document_count":
                detected_skills.get(
                    "document_count",
                    0
                )

        },


        # =================================================
        # CERTIFICATIONS
        # =================================================

        "certifications":
            final_certifications,


        # =================================================
        # UPLOADED CERTIFICATES
        # =================================================

        "uploaded_certificates":
            standardized_certificates,


        # =================================================
        # RESUME
        # =================================================

        "resume":
            final_resume,


        # =================================================
        # PROJECTS
        # =================================================

        "projects":
            projects_data,


        # =================================================
        # CAREER PREFERENCES
        # =================================================

        "career_preferences": {

            "interested_domain":
                career_data.get(
                    "interested_domain"
                ),

            "preferred_job_role":
                career_data.get(
                    "preferred_job_role"
                ),

            "preferred_location":
                career_data.get(
                    "preferred_location"
                ),

            "internship_preferences":
                career_data.get(
                    "internship_preferences"
                ),

            "career_goal":
                career_data.get(
                    "career_goal"
                ),

            "learning_goal":
                career_data.get(
                    "learning_goal"
                )

        },


        # =================================================
        # LLM ANALYSIS
        # =================================================

        "llm_analysis": {

            "status":
                "pending",

            "skill_summary":
                None,

            "overall_score":
                None,

            "strengths":
                [],

            "skill_gaps":
                [],

            "career_analysis":
                None,

            "learning_recommendations":
                [],

            "overall_assessment":
                None

        },


        # =================================================
        # JOB RECOMMENDATIONS
        # =================================================

        "job_recommendations":
            [],

        "job_recommendations_updated_at":
            None,


        # =================================================
        # PASSWORD
        # =================================================

        "password":
            generate_password_hash(
                data["password"]
            ),


        # =================================================
        # CREATED DATE
        # =================================================

        "created_at":
            utc_now()

    }


    # =====================================================
    # SAVE STUDENT
    # =====================================================

    try:

        result = (
            students_collection.insert_one(
                student
            )
        )


    except Exception as error:

        print(
            "MongoDB insertion error:",
            error
        )


        return jsonify({

            "success": False,

            "message":
                "Failed to save student",

            "error":
                str(error)

        }), 500


    # =====================================================
    # STUDENT ID
    # =====================================================

    student_id = str(
        result.inserted_id
    )


    # =====================================================
    # START BACKGROUND LLM ANALYSIS
    # =====================================================

    try:

        start_llm_analysis(
            student_id
        )


        print(
            "Background LLM analysis "
            "started successfully."
        )


    except Exception as error:

        print(
            "Could not start background "
            "LLM analysis:",
            error
        )


        students_collection.update_one(

            {
                "_id":
                    result.inserted_id
            },

            {
                "$set": {

                    "llm_analysis.status":
                        "failed",

                    "llm_analysis.error":
                        str(error),

                    "llm_analysis.completed_at":
                        utc_now()

                }
            }
        )


    # =====================================================
    # SUCCESS RESPONSE
    # =====================================================

    return jsonify({

        "success": True,

        "message":
            "Student registered successfully",

        "student_id":
            student_id,

        "llm_analysis_status":
            "pending",

        "resume_uploaded":
            uploaded_resume is not None,

        "certificates_uploaded":
            len(
                uploaded_certificates
            ),

        "resume_text_extracted":
            bool(
                uploaded_resume
                and
                uploaded_resume.get(
                    "extracted_text"
                )
            ),

        "certificate_texts_extracted":
            sum(
                1
                for certificate
                in uploaded_certificates
                if certificate.get(
                    "extracted_text"
                )
            ),

        "skills_detected":
            len(
                detected_skills.get(
                    "skills",
                    []
                )
                if isinstance(
                    detected_skills,
                    dict
                )
                else []
            )

    }), 201


# =========================================================
# STUDENT LOGIN
# =========================================================

@student_routes.route(
    "/login",
    methods=["POST"]
)
def login_student():

    data = request.get_json(
        silent=True
    )


    if not data:

        return jsonify({

            "success": False,

            "message":
                "Invalid JSON data"

        }), 400


    email = data.get(
        "email"
    )


    password = data.get(
        "password"
    )


    if not email or not password:

        return jsonify({

            "success": False,

            "message":
                "Email and password are required"

        }), 400


    # =====================================================
    # FIND STUDENT
    # =====================================================

    student = (
        students_collection.find_one({

            "personal.email":
                email

        })
    )


    if not student:

        return jsonify({

            "success": False,

            "message":
                "Invalid email or password"

        }), 401


    # =====================================================
    # CHECK PASSWORD
    # =====================================================

    stored_password = student.get(
        "password"
    )


    if not stored_password:

        return jsonify({

            "success": False,

            "message":
                "Password is not configured"

        }), 500


    try:

        password_valid = (
            check_password_hash(
                stored_password,
                password
            )
        )

    except Exception:

        password_valid = False


    if not password_valid:

        return jsonify({

            "success": False,

            "message":
                "Invalid email or password"

        }), 401


    # =====================================================
    # CREATE JWT TOKEN
    # =====================================================

    payload = {

        "student_id":
            str(
                student["_id"]
            ),

        "email":
            student[
                "personal"
            ][
                "email"
            ],

        "exp":
            utc_now()
            +
            timedelta(
                hours=24
            )

    }


    token = jwt.encode(

        payload,

        JWT_SECRET_KEY,

        algorithm="HS256"

    )


    # =====================================================
    # LOGIN RESPONSE
    # =====================================================

    return jsonify({

        "success": True,

        "message":
            "Login successful",

        "token":
            token,

        "student": {

            "student_id":
                str(
                    student["_id"]
                ),

            "full_name":
                student[
                    "personal"
                ][
                    "full_name"
                ],

            "email":
                student[
                    "personal"
                ][
                    "email"
                ],

            "register_number":
                student[
                    "personal"
                ][
                    "register_number"
                ]

        }

    }), 200


# =========================================================
# GET LOGGED-IN STUDENT PROFILE
# =========================================================

@student_routes.route(
    "/profile",
    methods=["GET"]
)
@token_required
def get_student_profile(
    student_id
):

    try:

        object_id = ObjectId(
            student_id
        )

    except InvalidId:

        return jsonify({

            "success": False,

            "message":
                "Invalid student ID"

        }), 400


    student = (
        students_collection.find_one({

            "_id":
                object_id

        })
    )


    if not student:

        return jsonify({

            "success": False,

            "message":
                "Student not found"

        }), 404


    # -----------------------------------------------------
    # NEVER RETURN PASSWORD
    # -----------------------------------------------------

    student.pop(
        "password",
        None
    )


    student["_id"] = str(
        student["_id"]
    )


    return jsonify({

        "success": True,

        "student":
            student

    }), 200


# =========================================================
# GET LLM ANALYSIS
# =========================================================

@student_routes.route(
    "/analysis",
    methods=["GET"]
)
@token_required
def get_student_analysis(
    student_id
):

    try:

        object_id = ObjectId(
            student_id
        )

    except InvalidId:

        return jsonify({

            "success": False,

            "message":
                "Invalid student ID"

        }), 400


    student = (
        students_collection.find_one(

            {
                "_id":
                    object_id
            },

            {
                "llm_analysis": 1
            }

        )
    )


    if not student:

        return jsonify({

            "success": False,

            "message":
                "Student not found"

        }), 404


    analysis = student.get(
        "llm_analysis",
        {}
    )


    return jsonify({

        "success": True,

        "analysis":
            analysis

    }), 200


# =========================================================
# GET JOB RECOMMENDATIONS
#
# BOTH URLs ARE SUPPORTED:
#
# /api/students/recommendations
#
# /api/students/job-recommendations
#
# =========================================================

@student_routes.route(
    "/recommendations",
    methods=["GET"]
)
@student_routes.route(
    "/job-recommendations",
    methods=["GET"]
)
@token_required
def get_job_recommendations(
    student_id
):

    try:

        # =================================================
        # CONVERT STUDENT ID
        # =================================================

        object_id = ObjectId(
            student_id
        )


        # =================================================
        # GET STUDENT
        # =================================================

        student = (
            students_collection.find_one({

                "_id":
                    object_id

            })
        )


        if not student:

            return jsonify({

                "success": False,

                "message":
                    "Student not found"

            }), 404


        # =================================================
        # GET LIMIT
        # =================================================

        limit = request.args.get(
            "limit",
            10
        )


        try:

            limit = int(
                limit
            )

        except (
            TypeError,
            ValueError
        ):

            limit = 10


        # -------------------------------------------------
        # KEEP LIMIT BETWEEN 1 AND 50
        # -------------------------------------------------

        limit = max(
            1,
            min(
                limit,
                50
            )
        )


        # =================================================
        # GET ALL JOBS
        # =================================================

        jobs = list(
            jobs_collection.find({})
        )


        # =================================================
        # NO JOBS
        # =================================================

        if not jobs:

            return jsonify({

                "success": True,

                "message":
                    "No jobs available for matching",

                "count":
                    0,

                "recommendations":
                    []

            }), 200


        # =================================================
        # RUN JOB MATCHER
        # =================================================

        recommendations = recommend_jobs(

            student,

            jobs,

            limit=limit

        )


        # =================================================
        # SAVE RECOMMENDATIONS
        # =================================================

        try:

            students_collection.update_one(

                {
                    "_id":
                        object_id
                },

                {
                    "$set": {

                        "job_recommendations":
                            recommendations,

                        "job_recommendations_updated_at":
                            utc_now()

                    }
                }

            )

        except Exception as save_error:

            print(
                "Could not save job recommendations:",
                save_error
            )


        # =================================================
        # RESPONSE
        # =================================================

        return jsonify({

            "success": True,

            "message":
                "Job recommendations generated successfully",

            "student_id":
                student_id,

            "total_jobs_checked":
                len(jobs),

            "count":
                len(
                    recommendations
                ),

            "recommendations":
                recommendations

        }), 200


    # =====================================================
    # INVALID OBJECT ID
    # =====================================================

    except InvalidId:

        return jsonify({

            "success": False,

            "message":
                "Invalid student ID"

        }), 400


    # =====================================================
    # GENERAL ERROR
    # =====================================================

    except Exception as error:

        print(
            "\n========================================"
        )

        print(
            "JOB RECOMMENDATION ERROR"
        )

        print(
            "========================================"
        )

        print(
            error
        )

        print(
            "========================================\n"
        )


        return jsonify({

            "success": False,

            "message":
                "Failed to generate job recommendations",

            "error":
                str(error)

        }), 500


# =========================================================
# GET SAVED JOB RECOMMENDATIONS
# =========================================================

@student_routes.route(
    "/saved-recommendations",
    methods=["GET"]
)
@token_required
def get_saved_job_recommendations(
    student_id
):

    try:

        object_id = ObjectId(
            student_id
        )


    except InvalidId:

        return jsonify({

            "success": False,

            "message":
                "Invalid student ID"

        }), 400


    student = (
        students_collection.find_one(

            {
                "_id":
                    object_id
            },

            {
                "job_recommendations": 1,
                "job_recommendations_updated_at": 1
            }

        )
    )


    if not student:

        return jsonify({

            "success": False,

            "message":
                "Student not found"

        }), 404


    recommendations = student.get(
        "job_recommendations",
        []
    )


    return jsonify({

        "success": True,

        "count":
            len(
                recommendations
            ),

        "updated_at":
            student.get(
                "job_recommendations_updated_at"
            ),

        "recommendations":
            recommendations

    }), 200


# =========================================================
# UPDATE STUDENT PROFILE
# =========================================================

@student_routes.route(
    "/profile",
    methods=["PUT"]
)
@token_required
def update_student_profile(
    student_id
):

    data = request.get_json(
        silent=True
    )


    if not data:

        return jsonify({

            "success": False,

            "message":
                "Invalid JSON data"

        }), 400


    # =====================================================
    # OBJECT ID
    # =====================================================

    try:

        object_id = ObjectId(
            student_id
        )

    except InvalidId:

        return jsonify({

            "success": False,

            "message":
                "Invalid student ID"

        }), 400


    # =====================================================
    # CHECK STUDENT
    # =====================================================

    student = (
        students_collection.find_one({

            "_id":
                object_id

        })
    )


    if not student:

        return jsonify({

            "success": False,

            "message":
                "Student not found"

        }), 404


    # =====================================================
    # ALLOWED PROFILE FIELDS
    # =====================================================

    allowed_fields = [

        "personal",

        "academic",

        "skills",

        "detected_skills",

        "certifications",

        "uploaded_certificates",

        "resume",

        "projects",

        "career_preferences"

    ]


    update_data = {}


    for field in allowed_fields:

        if field in data:

            update_data[
                field
            ] = data[
                field
            ]


    # =====================================================
    # VALIDATE UPDATE
    # =====================================================

    if not update_data:

        return jsonify({

            "success": False,

            "message":
                "No valid profile data provided"

        }), 400


    # =====================================================
    # UPDATE DATE
    # =====================================================

    update_data[
        "updated_at"
    ] = utc_now()


    # =====================================================
    # CLEAR OLD RECOMMENDATIONS
    #
    # Because changing skills / academic data /
    # career preferences can change the ranking.
    # =====================================================

    update_data[
        "job_recommendations"
    ] = []


    update_data[
        "job_recommendations_updated_at"
    ] = None


    # =====================================================
    # UPDATE MONGODB
    # =====================================================

    try:

        result = students_collection.update_one(

            {
                "_id":
                    object_id
            },

            {
                "$set":
                    update_data
            }

        )


    except Exception as error:

        print(
            "Profile update error:",
            error
        )


        return jsonify({

            "success": False,

            "message":
                "Failed to update student profile",

            "error":
                str(error)

        }), 500


    # =====================================================
    # RESPONSE
    # =====================================================

    return jsonify({

        "success": True,

        "message":
            "Student profile updated successfully",

        "modified":
            result.modified_count > 0,

        "recommendations_reset":
            True,

        "message_next_step":
            "Call /api/students/job-recommendations "
            "to generate updated recommendations."

    }), 200