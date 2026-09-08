from flask import Blueprint, request, jsonify
from bson import ObjectId
from bson.errors import InvalidId
from datetime import datetime, timezone

from config import db


# ============================================================
# JOB ROUTES
# ============================================================

job_routes = Blueprint("job_routes", __name__)

jobs_collection = db["job_requirements"]


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def validate_skills(skills, field_name):
    """Validate that skills are stored as a list of strings."""

    if skills is None:
        return True, None

    if not isinstance(skills, list):
        return False, f"{field_name} must be a list"

    for skill in skills:
        if not isinstance(skill, str):
            return False, f"Every item in {field_name} must be a string"

    return True, None


def validate_eligibility(eligibility):
    """
    Validate job eligibility requirements.

    Example:

    "eligibility": {
        "degrees": ["B.E", "B.Tech"],
        "branches": ["CSE", "IT"],
        "minimum_cgpa": 6.0,
        "graduation_years": [2026, 2027],
        "maximum_backlogs": 0
    }
    """

    if eligibility is None:
        return True, None

    if not isinstance(eligibility, dict):
        return False, "eligibility must be an object"

    # Degrees
    degrees = eligibility.get("degrees", [])

    if not isinstance(degrees, list):
        return False, "eligibility.degrees must be a list"

    for degree in degrees:
        if not isinstance(degree, str):
            return False, "Every degree must be a string"

    # Branches
    branches = eligibility.get("branches", [])

    if not isinstance(branches, list):
        return False, "eligibility.branches must be a list"

    for branch in branches:
        if not isinstance(branch, str):
            return False, "Every branch must be a string"

    # Minimum CGPA
    minimum_cgpa = eligibility.get("minimum_cgpa", 0)

    try:
        minimum_cgpa = float(minimum_cgpa)
    except (TypeError, ValueError):
        return False, "eligibility.minimum_cgpa must be a number"

    if minimum_cgpa < 0 or minimum_cgpa > 10:
        return False, "eligibility.minimum_cgpa must be between 0 and 10"

    # Graduation years
    graduation_years = eligibility.get("graduation_years", [])

    if not isinstance(graduation_years, list):
        return False, "eligibility.graduation_years must be a list"

    for year in graduation_years:
        try:
            int(year)
        except (TypeError, ValueError):
            return False, "Every graduation year must be a number"

    # Maximum backlogs
    maximum_backlogs = eligibility.get("maximum_backlogs", 0)

    try:
        maximum_backlogs = int(maximum_backlogs)
    except (TypeError, ValueError):
        return False, "eligibility.maximum_backlogs must be an integer"

    if maximum_backlogs < 0:
        return False, "eligibility.maximum_backlogs cannot be negative"

    return True, None


def serialize_job(job):
    """Convert MongoDB values into JSON-safe values."""

    job["_id"] = str(job["_id"])

    if isinstance(job.get("created_at"), datetime):
        job["created_at"] = job["created_at"].isoformat()

    if isinstance(job.get("updated_at"), datetime):
        job["updated_at"] = job["updated_at"].isoformat()

    return job


# ============================================================
# CREATE JOB
# POST /api/jobs/
# ============================================================

@job_routes.route("/", methods=["POST"])
def create_job():

    data = request.get_json(silent=True)

    if not data:
        return jsonify({
            "status": "error",
            "message": "Request body must contain JSON data"
        }), 400

    # --------------------------------------------------------
    # Required fields
    # --------------------------------------------------------

    required_fields = [
        "company_name",
        "job_role",
        "required_skills",
        "minimum_score"
    ]

    missing_fields = [
        field for field in required_fields
        if field not in data
    ]

    if missing_fields:
        return jsonify({
            "status": "error",
            "message": "Missing required fields",
            "missing_fields": missing_fields
        }), 400

    # --------------------------------------------------------
    # Company name
    # --------------------------------------------------------

    company_name = data.get("company_name")

    if not isinstance(company_name, str) or not company_name.strip():
        return jsonify({
            "status": "error",
            "message": "company_name must be a non-empty string"
        }), 400

    # --------------------------------------------------------
    # Job role
    # --------------------------------------------------------

    job_role = data.get("job_role")

    if not isinstance(job_role, str) or not job_role.strip():
        return jsonify({
            "status": "error",
            "message": "job_role must be a non-empty string"
        }), 400

    # --------------------------------------------------------
    # Required skills
    # --------------------------------------------------------

    valid, error = validate_skills(
        data.get("required_skills"),
        "required_skills"
    )

    if not valid:
        return jsonify({
            "status": "error",
            "message": error
        }), 400

    # --------------------------------------------------------
    # Preferred skills
    # --------------------------------------------------------

    valid, error = validate_skills(
        data.get("preferred_skills", []),
        "preferred_skills"
    )

    if not valid:
        return jsonify({
            "status": "error",
            "message": error
        }), 400

    # --------------------------------------------------------
    # Minimum score
    # --------------------------------------------------------

    try:
        minimum_score = float(data.get("minimum_score"))
    except (TypeError, ValueError):
        return jsonify({
            "status": "error",
            "message": "minimum_score must be a number"
        }), 400

    if minimum_score < 0 or minimum_score > 10:
        return jsonify({
            "status": "error",
            "message": "minimum_score must be between 0 and 10"
        }), 400

    # --------------------------------------------------------
    # Eligibility
    # --------------------------------------------------------

    eligibility = data.get("eligibility", {})

    valid, error = validate_eligibility(eligibility)

    if not valid:
        return jsonify({
            "status": "error",
            "message": error
        }), 400

    # --------------------------------------------------------
    # Application URL
    # --------------------------------------------------------

    application_url = data.get("application_url", "")

    if application_url is None:
        application_url = ""

    if not isinstance(application_url, str):
        return jsonify({
            "status": "error",
            "message": "application_url must be a string"
        }), 400

    # --------------------------------------------------------
    # Location
    # --------------------------------------------------------

    location = data.get("location", [])

    if isinstance(location, str):
        location = [location]

    elif location is None:
        location = []

    elif not isinstance(location, list):
        return jsonify({
            "status": "error",
            "message": "location must be a string or list"
        }), 400

    # --------------------------------------------------------
    # Create job document
    # --------------------------------------------------------

    now = datetime.now(timezone.utc)

    job = {
        "company_name": company_name.strip(),

        "job_role": job_role.strip(),

        "job_description": data.get(
            "job_description",
            ""
        ),

        "required_skills": data.get(
            "required_skills",
            []
        ),

        "preferred_skills": data.get(
            "preferred_skills",
            []
        ),

        "minimum_score": minimum_score,

        # Eligibility used by job matcher
        "eligibility": eligibility,

        # Application/career page
        "application_url": application_url,

        "location": location,

        "employment_type": data.get(
            "employment_type",
            "Full-time"
        ),

        "experience_required": data.get(
            "experience_required",
            "Fresher"
        ),

        "created_at": now,
        "updated_at": now
    }

    # --------------------------------------------------------
    # Insert into MongoDB
    # --------------------------------------------------------

    result = jobs_collection.insert_one(job)

    return jsonify({
        "status": "success",
        "message": "Job requirement created successfully",
        "job_id": str(result.inserted_id)
    }), 201


# ============================================================
# GET ALL JOBS
# GET /api/jobs/
# ============================================================

@job_routes.route("/", methods=["GET"])
def get_all_jobs():

    jobs = list(
        jobs_collection.find().sort(
            "created_at",
            -1
        )
    )

    jobs = [
        serialize_job(job)
        for job in jobs
    ]

    return jsonify({
        "status": "success",
        "count": len(jobs),
        "jobs": jobs
    }), 200


# ============================================================
# GET SINGLE JOB
# GET /api/jobs/<job_id>
# ============================================================

@job_routes.route("/<job_id>", methods=["GET"])
def get_job(job_id):

    try:
        object_id = ObjectId(job_id)

    except InvalidId:
        return jsonify({
            "status": "error",
            "message": "Invalid job ID"
        }), 400

    job = jobs_collection.find_one({
        "_id": object_id
    })

    if not job:
        return jsonify({
            "status": "error",
            "message": "Job not found"
        }), 404

    job = serialize_job(job)

    return jsonify({
        "status": "success",
        "job": job
    }), 200


# ============================================================
# UPDATE JOB
# PUT /api/jobs/<job_id>
# ============================================================

@job_routes.route("/<job_id>", methods=["PUT"])
def update_job(job_id):

    try:
        object_id = ObjectId(job_id)

    except InvalidId:
        return jsonify({
            "status": "error",
            "message": "Invalid job ID"
        }), 400

    data = request.get_json(silent=True)

    if not data:
        return jsonify({
            "status": "error",
            "message": "Request body must contain JSON data"
        }), 400

    # --------------------------------------------------------
    # Fields allowed to update
    # --------------------------------------------------------

    allowed_fields = [
        "company_name",
        "job_role",
        "job_description",
        "required_skills",
        "preferred_skills",
        "minimum_score",
        "eligibility",
        "application_url",
        "location",
        "employment_type",
        "experience_required"
    ]

    update_data = {}

    # --------------------------------------------------------
    # Validate update fields
    # --------------------------------------------------------

    for field in allowed_fields:

        if field not in data:
            continue

        value = data[field]

        # Company name
        if field == "company_name":

            if not isinstance(value, str) or not value.strip():
                return jsonify({
                    "status": "error",
                    "message": "company_name must be a non-empty string"
                }), 400

            value = value.strip()

        # Job role
        elif field == "job_role":

            if not isinstance(value, str) or not value.strip():
                return jsonify({
                    "status": "error",
                    "message": "job_role must be a non-empty string"
                }), 400

            value = value.strip()

        # Required skills
        elif field == "required_skills":

            valid, error = validate_skills(
                value,
                "required_skills"
            )

            if not valid:
                return jsonify({
                    "status": "error",
                    "message": error
                }), 400

        # Preferred skills
        elif field == "preferred_skills":

            valid, error = validate_skills(
                value,
                "preferred_skills"
            )

            if not valid:
                return jsonify({
                    "status": "error",
                    "message": error
                }), 400

        # Minimum score
        elif field == "minimum_score":

            try:
                value = float(value)

            except (TypeError, ValueError):
                return jsonify({
                    "status": "error",
                    "message": "minimum_score must be a number"
                }), 400

            if value < 0 or value > 10:
                return jsonify({
                    "status": "error",
                    "message": "minimum_score must be between 0 and 10"
                }), 400

        # Eligibility
        elif field == "eligibility":

            valid, error = validate_eligibility(value)

            if not valid:
                return jsonify({
                    "status": "error",
                    "message": error
                }), 400

        # Application URL
        elif field == "application_url":

            if value is None:
                value = ""

            if not isinstance(value, str):
                return jsonify({
                    "status": "error",
                    "message": "application_url must be a string"
                }), 400

        # Location
        elif field == "location":

            if isinstance(value, str):
                value = [value]

            elif value is None:
                value = []

            elif not isinstance(value, list):
                return jsonify({
                    "status": "error",
                    "message": "location must be a string or list"
                }), 400

        update_data[field] = value

    # --------------------------------------------------------
    # Nothing to update
    # --------------------------------------------------------

    if not update_data:
        return jsonify({
            "status": "error",
            "message": "No valid fields provided for update"
        }), 400

    # --------------------------------------------------------
    # Update timestamp
    # --------------------------------------------------------

    update_data["updated_at"] = datetime.now(timezone.utc)

    # --------------------------------------------------------
    # Update MongoDB
    # --------------------------------------------------------

    result = jobs_collection.update_one(
        {
            "_id": object_id
        },
        {
            "$set": update_data
        }
    )

    if result.matched_count == 0:
        return jsonify({
            "status": "error",
            "message": "Job not found"
        }), 404

    return jsonify({
        "status": "success",
        "message": "Job updated successfully"
    }), 200


# ============================================================
# DELETE JOB
# DELETE /api/jobs/<job_id>
# ============================================================

@job_routes.route("/<job_id>", methods=["DELETE"])
def delete_job(job_id):

    try:
        object_id = ObjectId(job_id)

    except InvalidId:
        return jsonify({
            "status": "error",
            "message": "Invalid job ID"
        }), 400

    result = jobs_collection.delete_one({
        "_id": object_id
    })

    if result.deleted_count == 0:
        return jsonify({
            "status": "error",
            "message": "Job not found"
        }), 404

    return jsonify({
        "status": "success",
        "message": "Job deleted successfully"
    }), 200