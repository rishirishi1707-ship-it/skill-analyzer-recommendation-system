# =========================================================
# routes/upload_routes.py
# =========================================================

from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename

from config import db

from services.pdf_extractor import (
    extract_text_from_file
)

from services.skill_extractor import (
    extract_skills_from_documents
)

from bson import ObjectId
from bson.errors import InvalidId

from datetime import datetime, timezone

import os
import uuid


# =========================================================
# BLUEPRINT
# =========================================================

upload_routes = Blueprint(
    "upload_routes",
    __name__
)


# =========================================================
# MONGODB COLLECTION
# =========================================================

students_collection = db["students"]


# =========================================================
# UPLOAD DIRECTORIES
# =========================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)


UPLOAD_FOLDER = os.path.join(
    BASE_DIR,
    "uploads"
)


RESUME_FOLDER = os.path.join(
    UPLOAD_FOLDER,
    "resumes"
)


CERTIFICATE_FOLDER = os.path.join(
    UPLOAD_FOLDER,
    "certificates"
)


os.makedirs(
    RESUME_FOLDER,
    exist_ok=True
)


os.makedirs(
    CERTIFICATE_FOLDER,
    exist_ok=True
)


# =========================================================
# ALLOWED FILE TYPES
# =========================================================

ALLOWED_RESUME_EXTENSIONS = {
    "pdf",
    "docx"
}


ALLOWED_CERTIFICATE_EXTENSIONS = {
    "pdf",
    "docx",
    "jpg",
    "jpeg",
    "png"
}


# =========================================================
# HELPER: CURRENT UTC TIME
# =========================================================

def utc_now():

    return datetime.now(
        timezone.utc
    )


# =========================================================
# HELPER: EMPTY DETECTED SKILLS
# =========================================================

def empty_detected_skills():

    return {

        "skills": [],

        "categorized_skills": {},

        "skill_details": [],

        "document_count": 0

    }


# =========================================================
# HELPER: CHECK ALLOWED FILE
# =========================================================

def allowed_file(
    filename,
    allowed_extensions
):

    if not filename:
        return False


    if "." not in filename:
        return False


    extension = filename.rsplit(
        ".",
        1
    )[-1].lower()


    return extension in allowed_extensions


# =========================================================
# HELPER: GET STUDENT OBJECT ID
# =========================================================

def get_student_object_id(
    student_id
):

    try:

        return ObjectId(
            student_id
        )


    except (
        InvalidId,
        TypeError
    ):

        return None


# =========================================================
# HELPER: GET STUDENT
# =========================================================

def get_student(
    object_id
):

    return students_collection.find_one(

        {
            "_id":
                object_id
        }

    )


# =========================================================
# HELPER: CREATE UNIQUE FILE NAME
# =========================================================

def create_unique_filename(
    original_filename
):

    extension = original_filename.rsplit(
        ".",
        1
    )[-1].lower()


    unique_filename = (

        str(
            uuid.uuid4()
        )

        + "."

        + extension

    )


    return (

        unique_filename,

        extension

    )


# =========================================================
# HELPER: GET RESUME TEXT
# =========================================================

def get_resume_text(
    student
):

    if not isinstance(
        student,
        dict
    ):

        return ""


    resume = student.get(
        "resume",
        {}
    )


    if not isinstance(
        resume,
        dict
    ):

        return ""


    # =====================================================
    # STRUCTURE 1
    #
    # resume.extracted_text
    # =====================================================

    extracted_text = resume.get(
        "extracted_text",
        ""
    )


    if extracted_text:

        return str(
            extracted_text
        )


    # =====================================================
    # STRUCTURE 2
    #
    # resume.file.extracted_text
    # =====================================================

    resume_file = resume.get(
        "file",
        {}
    )


    if isinstance(
        resume_file,
        dict
    ):

        return str(

            resume_file.get(
                "extracted_text",
                ""
            )

            or ""

        )


    return ""


# =========================================================
# HELPER: GET CERTIFICATE TEXTS
# =========================================================

def get_certificate_texts(
    student
):

    certificate_texts = []


    if not isinstance(
        student,
        dict
    ):

        return certificate_texts


    # =====================================================
    # STRUCTURE 1
    #
    # certifications[]
    # =====================================================

    certifications = student.get(
        "certifications",
        []
    )


    if isinstance(
        certifications,
        list
    ):

        for certification in certifications:

            if not isinstance(
                certification,
                dict
            ):

                continue


            # ------------------------------------------------
            # DIRECT TEXT
            # ------------------------------------------------

            direct_text = certification.get(
                "extracted_text",
                ""
            )


            if direct_text:

                certificate_texts.append(
                    str(
                        direct_text
                    )
                )

                continue


            # ------------------------------------------------
            # NESTED FILE TEXT
            # ------------------------------------------------

            certificate_file = certification.get(
                "file",
                {}
            )


            if isinstance(
                certificate_file,
                dict
            ):

                extracted_text = certificate_file.get(
                    "extracted_text",
                    ""
                )


                if extracted_text:

                    certificate_texts.append(
                        str(
                            extracted_text
                        )
                    )


    # =====================================================
    # STRUCTURE 2
    #
    # uploaded_certificates[]
    # =====================================================

    uploaded_certificates = student.get(
        "uploaded_certificates",
        []
    )


    if isinstance(
        uploaded_certificates,
        list
    ):

        for certificate in uploaded_certificates:

            if not isinstance(
                certificate,
                dict
            ):

                continue


            extracted_text = certificate.get(
                "extracted_text",
                ""
            )


            if extracted_text:

                certificate_texts.append(
                    str(
                        extracted_text
                    )
                )


    return certificate_texts


# =========================================================
# HELPER: EXTRACT RESUME SKILLS
# =========================================================

def extract_resume_skills(
    resume_text
):

    if not resume_text:

        return empty_detected_skills()


    try:

        return extract_skills_from_documents(

            resume_text=
                resume_text,

            certificate_texts=
                []

        )


    except Exception as error:

        print(
            "Resume skill extraction error:",
            error
        )


        return empty_detected_skills()


# =========================================================
# HELPER: EXTRACT CERTIFICATE SKILLS
# =========================================================

def extract_certificate_skills(
    certificate_texts
):

    if not certificate_texts:

        return empty_detected_skills()


    try:

        return extract_skills_from_documents(

            resume_text=
                "",

            certificate_texts=
                certificate_texts

        )


    except Exception as error:

        print(
            "Certificate skill extraction error:",
            error
        )


        return empty_detected_skills()


# =========================================================
# HELPER: UPDATE COMBINED DETECTED SKILLS
# =========================================================

def update_combined_skills(
    object_id
):

    # =====================================================
    # GET LATEST STUDENT DATA
    # =====================================================

    student = get_student(
        object_id
    )


    if not student:

        return empty_detected_skills()


    # =====================================================
    # GET RESUME TEXT
    # =====================================================

    resume_text = get_resume_text(
        student
    )


    # =====================================================
    # GET CERTIFICATE TEXTS
    # =====================================================

    certificate_texts = get_certificate_texts(
        student
    )


    # =====================================================
    # DEBUG OUTPUT
    # =====================================================

    print(
        "\n========================================"
    )

    print(
        "DOCUMENT SKILL EXTRACTION STARTED"
    )

    print(
        "========================================"
    )

    print(
        "Resume text characters:",
        len(
            resume_text
        )
    )

    print(
        "Certificate documents:",
        len(
            certificate_texts
        )
    )

    print(
        "========================================\n"
    )


    # =====================================================
    # EXTRACT RESUME SKILLS
    # =====================================================

    resume_result = extract_resume_skills(
        resume_text
    )


    # =====================================================
    # EXTRACT CERTIFICATE SKILLS
    # =====================================================

    certificate_result = extract_certificate_skills(
        certificate_texts
    )


    # =====================================================
    # EXTRACT ALL DOCUMENT SKILLS
    # =====================================================

    try:

        combined_result = (
            extract_skills_from_documents(

                resume_text=
                    resume_text,

                certificate_texts=
                    certificate_texts

            )
        )


    except Exception as error:

        print(
            "Combined skill extraction error:",
            error
        )


        combined_result = empty_detected_skills()


    # =====================================================
    # CANONICAL DETECTED SKILLS STRUCTURE
    #
    # IMPORTANT:
    #
    # This exact structure is expected by:
    #
    # services/llm_analyzer.py
    # services/llm_worker.py
    # =====================================================

    detected_skills_data = {

        "skills":
            combined_result.get(
                "skills",
                []
            ),

        "categorized_skills":
            combined_result.get(
                "categorized_skills",
                {}
            ),

        "skill_details":
            combined_result.get(
                "skill_details",
                []
            ),

        "document_count":
            combined_result.get(
                "document_count",
                0
            )

    }


    # =====================================================
    # OPTIONAL SOURCE DETAILS
    #
    # Useful for debugging/dashboard display
    # =====================================================

    detected_skills_sources = {

        "resume_skills":

            resume_result.get(
                "skills",
                []
            ),

        "certificate_skills":

            certificate_result.get(
                "skills",
                []
            )

    }


    # =====================================================
    # SAVE DETECTED SKILLS
    #
    # PRIMARY LOCATION:
    #
    # llm_analysis.detected_skills
    #
    # This matches llm_analyzer.py and llm_worker.py
    # =====================================================

    students_collection.update_one(

        {
            "_id":
                object_id
        },

        {
            "$set": {

                "llm_analysis.detected_skills":
                    detected_skills_data,

                "llm_analysis.detected_skill_sources":
                    detected_skills_sources,

                "updated_at":
                    utc_now()

            }
        }

    )


    # =====================================================
    # TERMINAL OUTPUT
    # =====================================================

    print(
        "\n========================================"
    )

    print(
        "DOCUMENT SKILL EXTRACTION COMPLETED"
    )

    print(
        "========================================"
    )

    print(
        "Documents analyzed:",
        detected_skills_data.get(
            "document_count",
            0
        )
    )

    print(
        "Resume skills:"
    )

    print(
        detected_skills_sources.get(
            "resume_skills",
            []
        )
    )

    print(
        "Certificate skills:"
    )

    print(
        detected_skills_sources.get(
            "certificate_skills",
            []
        )
    )

    print(
        "All detected skills:"
    )

    print(
        detected_skills_data.get(
            "skills",
            []
        )
    )

    print(
        "========================================\n"
    )


    return detected_skills_data


# =========================================================
# UPLOAD RESUME
# =========================================================

@upload_routes.route(
    "/resume/<student_id>",
    methods=[
        "POST"
    ]
)
def upload_resume(
    student_id
):

    # =====================================================
    # CHECK FILE
    # =====================================================

    if "resume" not in request.files:

        return jsonify({

            "success":
                False,

            "message":
                "Resume file is required"

        }), 400


    file = request.files[
        "resume"
    ]


    if not file.filename:

        return jsonify({

            "success":
                False,

            "message":
                "No resume selected"

        }), 400


    # =====================================================
    # VALIDATE FILE TYPE
    # =====================================================

    if not allowed_file(

        file.filename,

        ALLOWED_RESUME_EXTENSIONS

    ):

        return jsonify({

            "success":
                False,

            "message":
                "Only PDF and DOCX files are allowed"

        }), 400


    # =====================================================
    # VALIDATE STUDENT ID
    # =====================================================

    object_id = get_student_object_id(
        student_id
    )


    if not object_id:

        return jsonify({

            "success":
                False,

            "message":
                "Invalid student ID"

        }), 400


    student = get_student(
        object_id
    )


    if not student:

        return jsonify({

            "success":
                False,

            "message":
                "Student not found"

        }), 404


    # =====================================================
    # CREATE FILE NAME
    # =====================================================

    original_filename = secure_filename(
        file.filename
    )


    unique_filename, extension = (
        create_unique_filename(
            original_filename
        )
    )


    filepath = os.path.join(

        RESUME_FOLDER,

        unique_filename

    )


    try:

        # =================================================
        # SAVE FILE
        # =================================================

        file.save(
            filepath
        )


        print(
            "\n========================================"
        )

        print(
            "EXTRACTING RESUME TEXT"
        )

        print(
            "FILE:",
            original_filename
        )

        print(
            "========================================"
        )


        # =================================================
        # EXTRACT TEXT
        # =================================================

        resume_text = extract_text_from_file(
            filepath
        ) or ""


        print(
            "Resume text characters extracted:",
            len(
                resume_text
            )
        )


        # =================================================
        # CREATE RESUME DATA
        # =================================================

        resume_data = {

            "has_resume":
                True,

            "resume_name":
                original_filename,

            "stored_filename":
                unique_filename,

            "file_path":
                filepath,

            "file_type":
                extension,

            "extracted_text":
                resume_text,

            "uploaded_at":
                utc_now()

        }


        # =================================================
        # SAVE TO MONGODB
        # =================================================

        students_collection.update_one(

            {
                "_id":
                    object_id
            },

            {
                "$set": {

                    "resume":
                        resume_data,

                    "updated_at":
                        utc_now()

                }
            }

        )


        # =================================================
        # UPDATE DETECTED SKILLS
        # =================================================

        detected_skills_data = (
            update_combined_skills(
                object_id
            )
        )


        # =================================================
        # SUCCESS MESSAGE
        # =================================================

        if resume_text.strip():

            message = (

                "Resume uploaded successfully. "
                "Text extracted and skills detected."

            )

        else:

            message = (

                "Resume uploaded successfully, but "
                "no readable text could be extracted."

            )


        # =================================================
        # RESPONSE
        # =================================================

        return jsonify({

            "success":
                True,

            "message":
                message,

            "resume": {

                "original_name":
                    original_filename,

                "stored_name":
                    unique_filename,

                "text_characters":
                    len(
                        resume_text
                    )

            },

            "detected_skills":
                detected_skills_data

        }), 200


    except Exception as error:

        print(
            "Resume upload error:",
            error
        )


        if os.path.exists(
            filepath
        ):

            try:

                os.remove(
                    filepath
                )

            except Exception:

                pass


        return jsonify({

            "success":
                False,

            "message":
                "Resume upload failed",

            "error":
                str(
                    error
                )

        }), 500


# =========================================================
# UPLOAD CERTIFICATE
# =========================================================

@upload_routes.route(
    "/certificate/<student_id>",
    methods=[
        "POST"
    ]
)
def upload_certificate(
    student_id
):

    # =====================================================
    # CHECK FILE
    # =====================================================

    if "certificate" not in request.files:

        return jsonify({

            "success":
                False,

            "message":
                "Certificate file is required"

        }), 400


    file = request.files[
        "certificate"
    ]


    if not file.filename:

        return jsonify({

            "success":
                False,

            "message":
                "No certificate selected"

        }), 400


    # =====================================================
    # VALIDATE FILE TYPE
    # =====================================================

    if not allowed_file(

        file.filename,

        ALLOWED_CERTIFICATE_EXTENSIONS

    ):

        return jsonify({

            "success":
                False,

            "message":
                (
                    "Only PDF, DOCX, JPG, JPEG "
                    "and PNG files are allowed"
                )

        }), 400


    # =====================================================
    # VALIDATE STUDENT ID
    # =====================================================

    object_id = get_student_object_id(
        student_id
    )


    if not object_id:

        return jsonify({

            "success":
                False,

            "message":
                "Invalid student ID"

        }), 400


    student = get_student(
        object_id
    )


    if not student:

        return jsonify({

            "success":
                False,

            "message":
                "Student not found"

        }), 404


    # =====================================================
    # CREATE FILE NAME
    # =====================================================

    original_filename = secure_filename(
        file.filename
    )


    unique_filename, extension = (
        create_unique_filename(
            original_filename
        )
    )


    filepath = os.path.join(

        CERTIFICATE_FOLDER,

        unique_filename

    )


    try:

        # =================================================
        # SAVE FILE
        # =================================================

        file.save(
            filepath
        )


        print(
            "\n========================================"
        )

        print(
            "EXTRACTING CERTIFICATE TEXT"
        )

        print(
            "FILE:",
            original_filename
        )

        print(
            "========================================"
        )


        # =================================================
        # EXTRACT TEXT / OCR
        # =================================================

        certificate_text = (

            extract_text_from_file(
                filepath
            )

            or ""

        )


        print(
            "Certificate text characters extracted:",
            len(
                certificate_text
            )
        )


        # =================================================
        # CREATE CERTIFICATE DATA
        # =================================================

        certificate_data = {

            "original_name":
                original_filename,

            "stored_filename":
                unique_filename,

            "file_path":
                filepath,

            "file_type":
                extension,

            "extracted_text":
                certificate_text,

            "uploaded_at":
                utc_now()

        }


        # =================================================
        # SAVE CERTIFICATE
        # =================================================

        students_collection.update_one(

            {
                "_id":
                    object_id
            },

            {
                "$push": {

                    "uploaded_certificates":
                        certificate_data

                },

                "$set": {

                    "updated_at":
                        utc_now()

                }

            }

        )


        # =================================================
        # UPDATE DETECTED SKILLS
        # =================================================

        detected_skills_data = (
            update_combined_skills(
                object_id
            )
        )


        # =================================================
        # SUCCESS MESSAGE
        # =================================================

        if certificate_text.strip():

            message = (

                "Certificate uploaded successfully. "
                "Text extracted and skills detected."

            )

        else:

            message = (

                "Certificate uploaded successfully, "
                "but no readable text could be extracted."

            )


        # =================================================
        # RESPONSE
        # =================================================

        return jsonify({

            "success":
                True,

            "message":
                message,

            "certificate": {

                "original_name":
                    original_filename,

                "stored_name":
                    unique_filename,

                "text_characters":
                    len(
                        certificate_text
                    )

            },

            "detected_skills":
                detected_skills_data

        }), 200


    except Exception as error:

        print(
            "Certificate upload error:",
            error
        )


        if os.path.exists(
            filepath
        ):

            try:

                os.remove(
                    filepath
                )

            except Exception:

                pass


        return jsonify({

            "success":
                False,

            "message":
                "Certificate upload failed",

            "error":
                str(
                    error
                )

        }), 500