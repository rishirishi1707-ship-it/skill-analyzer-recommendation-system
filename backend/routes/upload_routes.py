from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
from config import db

from services.pdf_extractor import extract_text_from_file
from services.skill_extractor import extract_skills_from_documents

from bson import ObjectId
from bson.errors import InvalidId

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
    "jpg",
    "jpeg",
    "png"
}


# =========================================================
# HELPER: ALLOWED FILE
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

def get_student_object_id(student_id):

    try:

        return ObjectId(
            student_id
        )

    except InvalidId:

        return None


# =========================================================
# HELPER: COMBINE DOCUMENT TEXT
# =========================================================

def get_all_document_text(student):

    document_texts = []

    # -----------------------------------------------------
    # RESUME TEXT
    # -----------------------------------------------------

    resume = student.get(
        "resume",
        {}
    )

    if isinstance(
        resume,
        dict
    ):

        resume_text = resume.get(
            "extracted_text",
            ""
        )

        if resume_text:

            document_texts.append(
                resume_text
            )

    # -----------------------------------------------------
    # CERTIFICATE TEXT
    # -----------------------------------------------------

    certificates = student.get(
        "uploaded_certificates",
        []
    )

    if isinstance(
        certificates,
        list
    ):

        for certificate in certificates:

            if not isinstance(
                certificate,
                dict
            ):
                continue

            certificate_text = certificate.get(
                "extracted_text",
                ""
            )

            if certificate_text:

                document_texts.append(
                    certificate_text
                )

    return document_texts


# =========================================================
# HELPER: UPDATE COMBINED DETECTED SKILLS
# =========================================================

def update_combined_skills(object_id):

    student = students_collection.find_one(
        {
            "_id": object_id
        }
    )

    if not student:

        return {
            "skills": [],
            "categorized_skills": {},
            "skill_details": [],
            "document_count": 0
        }

    # -----------------------------------------------------
    # GET ALL EXTRACTED DOCUMENT TEXT
    # -----------------------------------------------------

    document_texts = get_all_document_text(
        student
    )

    resume_text = ""

    certificate_texts = []

    resume = student.get(
        "resume",
        {}
    )

    if isinstance(
        resume,
        dict
    ):

        resume_text = resume.get(
            "extracted_text",
            ""
        )

    certificates = student.get(
        "uploaded_certificates",
        []
    )

    if isinstance(
        certificates,
        list
    ):

        for certificate in certificates:

            if not isinstance(
                certificate,
                dict
            ):
                continue

            certificate_text = certificate.get(
                "extracted_text",
                ""
            )

            if certificate_text:

                certificate_texts.append(
                    certificate_text
                )

    # -----------------------------------------------------
    # EXTRACT ALL DOCUMENT SKILLS
    # -----------------------------------------------------

    detected_skills_data = (
        extract_skills_from_documents(
            resume_text=resume_text,
            certificate_texts=certificate_texts
        )
    )

    # -----------------------------------------------------
    # SAVE COMBINED SKILLS
    # -----------------------------------------------------

    students_collection.update_one(

        {
            "_id": object_id
        },

        {
            "$set": {

                "llm_analysis.detected_skills":
                    detected_skills_data
            }
        }

    )

    return detected_skills_data


# =========================================================
# UPLOAD RESUME
# =========================================================

@upload_routes.route(
    "/resume/<student_id>",
    methods=["POST"]
)
def upload_resume(student_id):

    # -----------------------------------------------------
    # CHECK FILE
    # -----------------------------------------------------

    if "resume" not in request.files:

        return jsonify({

            "success": False,

            "message":
                "Resume file is required"

        }), 400


    file = request.files[
        "resume"
    ]


    if not file.filename:

        return jsonify({

            "success": False,

            "message":
                "No resume selected"

        }), 400


    # -----------------------------------------------------
    # VALIDATE EXTENSION
    # -----------------------------------------------------

    if not allowed_file(
        file.filename,
        ALLOWED_RESUME_EXTENSIONS
    ):

        return jsonify({

            "success": False,

            "message":
                "Only PDF and DOCX files are allowed"

        }), 400


    # -----------------------------------------------------
    # VALIDATE STUDENT ID
    # -----------------------------------------------------

    object_id = get_student_object_id(
        student_id
    )

    if not object_id:

        return jsonify({

            "success": False,

            "message":
                "Invalid student ID"

        }), 400


    student = students_collection.find_one({

        "_id":
            object_id

    })


    if not student:

        return jsonify({

            "success": False,

            "message":
                "Student not found"

        }), 404


    # -----------------------------------------------------
    # GENERATE UNIQUE FILENAME
    # -----------------------------------------------------

    original_filename = secure_filename(
        file.filename
    )

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


    filepath = os.path.join(

        RESUME_FOLDER,

        unique_filename

    )


    # -----------------------------------------------------
    # SAVE FILE
    # -----------------------------------------------------

    file.save(
        filepath
    )


    # -----------------------------------------------------
    # EXTRACT TEXT
    # -----------------------------------------------------

    print(
        "\n========================================"
    )

    print(
        "EXTRACTING RESUME TEXT"
    )

    print(
        "========================================"
    )


    resume_text = extract_text_from_file(
        filepath
    )


    print(

        "Resume text characters extracted:",

        len(
            resume_text
        )

    )


    # -----------------------------------------------------
    # CREATE RESUME DATA
    # -----------------------------------------------------

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
            resume_text

    }


    # -----------------------------------------------------
    # SAVE RESUME
    # -----------------------------------------------------

    students_collection.update_one(

        {

            "_id":
                object_id

        },

        {

            "$set": {

                "resume":
                    resume_data

            }

        }

    )


    # -----------------------------------------------------
    # UPDATE ALL DOCUMENT SKILLS
    # -----------------------------------------------------

    detected_skills_data = (
        update_combined_skills(
            object_id
        )
    )


    print(
        "Detected skills:"
    )

    print(
        detected_skills_data.get(
            "skills",
            []
        )
    )


    # -----------------------------------------------------
    # RESPONSE
    # -----------------------------------------------------

    return jsonify({

        "success":
            True,

        "message":
            "Resume uploaded and analyzed successfully",

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


# =========================================================
# UPLOAD CERTIFICATE
# =========================================================

@upload_routes.route(
    "/certificate/<student_id>",
    methods=["POST"]
)
def upload_certificate(student_id):

    # -----------------------------------------------------
    # CHECK FILE
    # -----------------------------------------------------

    if "certificate" not in request.files:

        return jsonify({

            "success": False,

            "message":
                "Certificate file is required"

        }), 400


    file = request.files[
        "certificate"
    ]


    if not file.filename:

        return jsonify({

            "success": False,

            "message":
                "No certificate selected"

        }), 400


    # -----------------------------------------------------
    # VALIDATE FILE TYPE
    # -----------------------------------------------------

    if not allowed_file(

        file.filename,

        ALLOWED_CERTIFICATE_EXTENSIONS

    ):

        return jsonify({

            "success": False,

            "message":
                "Only PDF, JPG, JPEG and PNG files are allowed"

        }), 400


    # -----------------------------------------------------
    # VALIDATE STUDENT ID
    # -----------------------------------------------------

    object_id = get_student_object_id(
        student_id
    )


    if not object_id:

        return jsonify({

            "success": False,

            "message":
                "Invalid student ID"

        }), 400


    student = students_collection.find_one({

        "_id":
            object_id

    })


    if not student:

        return jsonify({

            "success": False,

            "message":
                "Student not found"

        }), 404


    # -----------------------------------------------------
    # UNIQUE FILENAME
    # -----------------------------------------------------

    original_filename = secure_filename(
        file.filename
    )


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


    filepath = os.path.join(

        CERTIFICATE_FOLDER,

        unique_filename

    )


    # -----------------------------------------------------
    # SAVE FILE
    # -----------------------------------------------------

    file.save(
        filepath
    )


    # -----------------------------------------------------
    # EXTRACT TEXT / OCR
    # -----------------------------------------------------

    print(
        "\n========================================"
    )

    print(
        "EXTRACTING CERTIFICATE TEXT"
    )

    print(
        "========================================"
    )


    certificate_text = (
        extract_text_from_file(
            filepath
        )
    )


    print(

        "Certificate text characters extracted:",

        len(
            certificate_text
        )

    )


    # -----------------------------------------------------
    # CERTIFICATE DATA
    # -----------------------------------------------------

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
            certificate_text

    }


    # -----------------------------------------------------
    # SAVE CERTIFICATE
    # -----------------------------------------------------

    students_collection.update_one(

        {

            "_id":
                object_id

        },

        {

            "$push": {

                "uploaded_certificates":

                    certificate_data

            }

        }

    )


    # -----------------------------------------------------
    # UPDATE ALL DOCUMENT SKILLS
    # -----------------------------------------------------

    detected_skills_data = (
        update_combined_skills(
            object_id
        )
    )


    print(
        "Detected skills:"
    )

    print(
        detected_skills_data.get(
            "skills",
            []
        )
    )


    # -----------------------------------------------------
    # RESPONSE
    # -----------------------------------------------------

    return jsonify({

        "success":
            True,

        "message":
            "Certificate uploaded and analyzed successfully",

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