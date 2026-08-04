from flask import Blueprint, request, jsonify
from config import db

from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

from bson import ObjectId
from bson.errors import InvalidId

import jwt
import os

from datetime import datetime, timedelta, timezone
from functools import wraps


# =========================================================
# BLUEPRINT
# =========================================================

student_routes = Blueprint(
    "student_routes",
    __name__
)


# =========================================================
# MONGODB COLLECTION
# =========================================================

students_collection = db["students"]


# =========================================================
# JWT SECRET KEY
# =========================================================

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")

if not JWT_SECRET_KEY:

    raise RuntimeError(
        "JWT_SECRET_KEY is not configured"
    )


# =========================================================
# JWT TOKEN VERIFICATION
# =========================================================

def token_required(function):

    @wraps(function)
    def decorated(*args, **kwargs):

        auth_header = request.headers.get(
            "Authorization"
        )

        # Check Authorization header
        if not auth_header:

            return jsonify({
                "success": False,
                "message":
                    "Authorization token is required"
            }), 401

        # Check Bearer format
        if not auth_header.startswith(
            "Bearer "
        ):

            return jsonify({
                "success": False,
                "message":
                    "Invalid authorization format"
            }), 401

        # Extract token
        token = auth_header.split(
            " ",
            1
        )[1]

        try:

            payload = jwt.decode(
                token,
                JWT_SECRET_KEY,
                algorithms=["HS256"]
            )

            student_id = payload.get(
                "student_id"
            )

            if not student_id:

                return jsonify({
                    "success": False,
                    "message":
                        "Invalid token"
                }), 401

        except jwt.ExpiredSignatureError:

            return jsonify({
                "success": False,
                "message":
                    "Token has expired"
            }), 401

        except jwt.InvalidTokenError:

            return jsonify({
                "success": False,
                "message":
                    "Invalid token"
            }), 401

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

    data = request.get_json(
        silent=True
    )

    if not data:

        return jsonify({
            "success": False,
            "message":
                "Invalid JSON data"
        }), 400


    # -----------------------------------------------------
    # Required fields
    # -----------------------------------------------------

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


    # -----------------------------------------------------
    # Check existing student
    # -----------------------------------------------------

    existing_student = students_collection.find_one({

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


    if existing_student:

        return jsonify({
            "success": False,
            "message":
                "Student already registered"
        }), 409


    # -----------------------------------------------------
    # Create student document
    # -----------------------------------------------------

    student = {

        # =================================================
        # PERSONAL INFORMATION
        # =================================================

        "personal": {

            "full_name":
                data.get("full_name"),

            "register_number":
                data.get("register_number"),

            "roll_number":
                data.get("roll_number"),

            "email":
                data.get("email"),

            "mobile":
                data.get("mobile"),

            "gender":
                data.get("gender"),

            "date_of_birth":
                data.get("date_of_birth"),

            "department":
                data.get("department"),

            "degree":
                data.get("degree"),

            "year_of_study":
                data.get("year_of_study"),

            "section":
                data.get("section"),

            "semester":
                data.get("semester")
        },


        # =================================================
        # ACADEMIC INFORMATION
        # =================================================

        "academic": {

            "college_name":
                data.get("college_name"),

            "university":
                data.get("university"),

            "branch":
                data.get("branch"),

            "current_cgpa":
                data.get("current_cgpa"),

            "tenth_percentage":
                data.get("tenth_percentage"),

            "twelfth_percentage":
                data.get("twelfth_percentage"),

            "number_of_arrears":
                data.get("number_of_arrears"),

            "backlog_history":
                data.get("backlog_history"),

            "academic_year":
                data.get("academic_year"),

            "graduation_year":
                data.get("graduation_year")
        },


        # =================================================
        # SKILLS
        # =================================================

        "skills":
            data.get(
                "skills",
                []
            ),


        # =================================================
        # CERTIFICATIONS
        # =================================================

        "certifications":
            data.get(
                "certifications",
                []
            ),


        # =================================================
        # PROJECTS / EXPERIENCE
        # =================================================

        "projects":
            data.get(
                "projects",
                []
            ),


        # =================================================
        # CAREER PREFERENCES
        # =================================================

        "career_preferences": {

            "preferred_job_role":
                data.get(
                    "preferred_job_role"
                ),

            "preferred_location":
                data.get(
                    "preferred_location"
                ),

            "internship_preferences":
                data.get(
                    "internship_preferences"
                )
        },


        # =================================================
        # LLM ANALYSIS
        # =================================================

        "llm_analysis": {

            "skill_summary": None,

            "strengths": [],

            "skill_gaps": [],

            "career_analysis": None
        },


        # =================================================
        # RECOMMENDATIONS
        # =================================================

        "recommendations": [],


        # =================================================
        # PASSWORD
        # =================================================

        "password":
            generate_password_hash(
                data["password"]
            )
    }


    # -----------------------------------------------------
    # Save to MongoDB
    # -----------------------------------------------------

    result = students_collection.insert_one(
        student
    )


    return jsonify({

        "success": True,

        "message":
            "Student registered successfully",

        "student_id":
            str(result.inserted_id)

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


    email = data.get("email")

    password = data.get("password")


    # -----------------------------------------------------
    # Validate input
    # -----------------------------------------------------

    if not email or not password:

        return jsonify({
            "success": False,
            "message":
                "Email and password are required"
        }), 400


    # -----------------------------------------------------
    # Find student
    # -----------------------------------------------------

    student = students_collection.find_one({

        "personal.email":
            email

    })


    if not student:

        return jsonify({
            "success": False,
            "message":
                "Invalid email or password"
        }), 401


    # -----------------------------------------------------
    # Check password
    # -----------------------------------------------------

    password_valid = check_password_hash(

        student["password"],

        password

    )


    if not password_valid:

        return jsonify({
            "success": False,
            "message":
                "Invalid email or password"
        }), 401


    # -----------------------------------------------------
    # Create JWT
    # -----------------------------------------------------

    payload = {

        "student_id":
            str(student["_id"]),

        "email":
            student["personal"]["email"],

        "exp":
            datetime.now(
                timezone.utc
            )
            + timedelta(
                hours=24
            )
    }


    token = jwt.encode(

        payload,

        JWT_SECRET_KEY,

        algorithm="HS256"

    )


    return jsonify({

        "success": True,

        "message":
            "Login successful",

        "token":
            token,

        "student": {

            "student_id":
                str(student["_id"]),

            "full_name":
                student["personal"]["full_name"],

            "email":
                student["personal"]["email"],

            "register_number":
                student["personal"][
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


    # -----------------------------------------------------
    # Find student
    # -----------------------------------------------------

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
    # Never return password
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


    # -----------------------------------------------------
    # Convert student ID
    # -----------------------------------------------------

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


    # -----------------------------------------------------
    # Check student
    # -----------------------------------------------------

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
    # Allowed profile sections
    # -----------------------------------------------------

    allowed_fields = [

        "personal",

        "academic",

        "skills",

        "certifications",

        "projects",

        "career_preferences"

    ]


    update_data = {}


    for field in allowed_fields:

        if field in data:

            update_data[field] = data[field]


    # -----------------------------------------------------
    # Check update data
    # -----------------------------------------------------

    if not update_data:

        return jsonify({
            "success": False,
            "message":
                "No valid profile data provided"
        }), 400


    # -----------------------------------------------------
    # Update MongoDB
    # -----------------------------------------------------

    students_collection.update_one(

        {
            "_id":
                object_id
        },

        {
            "$set":
                update_data
        }

    )


    return jsonify({

        "success": True,

        "message":
            "Student profile updated successfully"

    }), 200