from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
from config import db

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


# Create folders if they don't exist

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
    "doc",
    "docx"
}

ALLOWED_CERTIFICATE_EXTENSIONS = {
    "pdf",
    "jpg",
    "jpeg",
    "png"
}


# =========================================================
# HELPER
# =========================================================

def allowed_file(
    filename,
    allowed_extensions
):

    if not filename:
        return False

    extension = filename.rsplit(
        ".",
        1
    )[-1].lower()

    return extension in allowed_extensions


# =========================================================
# UPLOAD RESUME
# =========================================================

@upload_routes.route(
    "/resume/<student_id>",
    methods=["POST"]
)
def upload_resume(student_id):

    # -----------------------------------------------------
    # Check file
    # -----------------------------------------------------

    if "resume" not in request.files:

        return jsonify({
            "success": False,
            "message": "Resume file is required"
        }), 400


    file = request.files["resume"]


    if not file.filename:

        return jsonify({
            "success": False,
            "message": "No resume selected"
        }), 400


    # -----------------------------------------------------
    # Validate extension
    # -----------------------------------------------------

    if not allowed_file(
        file.filename,
        ALLOWED_RESUME_EXTENSIONS
    ):

        return jsonify({
            "success": False,
            "message":
                "Only PDF, DOC and DOCX files are allowed"
        }), 400


    # -----------------------------------------------------
    # Check student
    # -----------------------------------------------------

    from bson import ObjectId
    from bson.errors import InvalidId

    try:

        object_id = ObjectId(
            student_id
        )

    except InvalidId:

        return jsonify({
            "success": False,
            "message": "Invalid student ID"
        }), 400


    student = students_collection.find_one({
        "_id": object_id
    })


    if not student:

        return jsonify({
            "success": False,
            "message": "Student not found"
        }), 404


    # -----------------------------------------------------
    # Generate unique filename
    # -----------------------------------------------------

    original_filename = secure_filename(
        file.filename
    )

    extension = original_filename.rsplit(
        ".",
        1
    )[-1].lower()

    unique_filename = (
        str(uuid.uuid4())
        + "."
        + extension
    )


    filepath = os.path.join(
        RESUME_FOLDER,
        unique_filename
    )


    # -----------------------------------------------------
    # Save file
    # -----------------------------------------------------

    file.save(filepath)


    # -----------------------------------------------------
    # MongoDB metadata
    # -----------------------------------------------------

    resume_data = {

        "has_resume": "yes",

        "resume_name":
            original_filename,

        "stored_filename":
            unique_filename,

        "file_path":
            filepath,

        "file_type":
            extension
    }


    students_collection.update_one(

        {
            "_id": object_id
        },

        {
            "$set": {
                "resume": resume_data
            }
        }

    )


    # -----------------------------------------------------
    # Response
    # -----------------------------------------------------

    return jsonify({

        "success": True,

        "message":
            "Resume uploaded successfully",

        "resume": {
            "original_name":
                original_filename,

            "stored_name":
                unique_filename
        }

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
    # Check file
    # -----------------------------------------------------

    if "certificate" not in request.files:

        return jsonify({
            "success": False,
            "message":
                "Certificate file is required"
        }), 400


    file = request.files["certificate"]


    if not file.filename:

        return jsonify({
            "success": False,
            "message":
                "No certificate selected"
        }), 400


    # -----------------------------------------------------
    # Validate extension
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
    # Check student
    # -----------------------------------------------------

    from bson import ObjectId
    from bson.errors import InvalidId

    try:

        object_id = ObjectId(
            student_id
        )

    except InvalidId:

        return jsonify({
            "success": False,
            "message": "Invalid student ID"
        }), 400


    student = students_collection.find_one({
        "_id": object_id
    })


    if not student:

        return jsonify({
            "success": False,
            "message": "Student not found"
        }), 404


    # -----------------------------------------------------
    # Generate unique filename
    # -----------------------------------------------------

    original_filename = secure_filename(
        file.filename
    )

    extension = original_filename.rsplit(
        ".",
        1
    )[-1].lower()

    unique_filename = (
        str(uuid.uuid4())
        + "."
        + extension
    )


    filepath = os.path.join(
        CERTIFICATE_FOLDER,
        unique_filename
    )


    # -----------------------------------------------------
    # Save certificate
    # -----------------------------------------------------

    file.save(filepath)


    # -----------------------------------------------------
    # Create certificate metadata
    # -----------------------------------------------------

    certificate_data = {

        "original_name":
            original_filename,

        "stored_filename":
            unique_filename,

        "file_path":
            filepath,

        "file_type":
            extension
    }


    # -----------------------------------------------------
    # Add certificate to existing array
    # -----------------------------------------------------

    students_collection.update_one(

        {
            "_id": object_id
        },

        {
            "$push": {
                "uploaded_certificates":
                    certificate_data
            }
        }

    )


    # -----------------------------------------------------
    # Response
    # -----------------------------------------------------

    return jsonify({

        "success": True,

        "message":
            "Certificate uploaded successfully",

        "certificate":
            certificate_data

    }), 200