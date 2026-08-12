# =========================================================
# routes/job_routes.py
# =========================================================

from flask import Blueprint, request, jsonify
from config import db

from datetime import datetime, timezone

from bson import ObjectId
from bson.errors import InvalidId


# =========================================================
# BLUEPRINT
# =========================================================

job_routes = Blueprint(
    "job_routes",
    __name__
)


# =========================================================
# MONGODB COLLECTION
# =========================================================

jobs_collection = db["job_requirements"]


# =========================================================
# CREATE JOB REQUIREMENT
# =========================================================

@job_routes.route(
    "/",
    methods=["POST"]
)
def create_job_requirement():

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
    # REQUIRED FIELDS
    # =====================================================

    required_fields = [

        "company_name",

        "job_role",

        "required_skills",

        "minimum_score"

    ]

    for field in required_fields:

        if field not in data:

            return jsonify({

                "success": False,

                "message":
                    f"{field} is required"

            }), 400


    # =====================================================
    # VALIDATE SKILLS
    # =====================================================

    required_skills = data.get(
        "required_skills"
    )

    preferred_skills = data.get(
        "preferred_skills",
        []
    )


    if not isinstance(
        required_skills,
        list
    ):

        return jsonify({

            "success": False,

            "message":
                "required_skills must be a list"

        }), 400


    if not isinstance(
        preferred_skills,
        list
    ):

        return jsonify({

            "success": False,

            "message":
                "preferred_skills must be a list"

        }), 400


    # =====================================================
    # VALIDATE SCORE
    # =====================================================

    try:

        minimum_score = float(
            data.get(
                "minimum_score"
            )
        )

    except (
        TypeError,
        ValueError
    ):

        return jsonify({

            "success": False,

            "message":
                "minimum_score must be a number"

        }), 400


    if minimum_score < 0 or minimum_score > 10:

        return jsonify({

            "success": False,

            "message":
                "minimum_score must be between 0 and 10"

        }), 400


    # =====================================================
    # CREATE JOB DOCUMENT
    # =====================================================

    job = {

        "company_name":
            data.get(
                "company_name"
            ),

        "job_role":
            data.get(
                "job_role"
            ),

        "job_description":
            data.get(
                "job_description",
                ""
            ),

        "required_skills":
            required_skills,

        "preferred_skills":
            preferred_skills,

        "minimum_score":
            minimum_score,

        "location":
            data.get(
                "location"
            ),

        "employment_type":
            data.get(
                "employment_type"
            ),

        "experience_required":
            data.get(
                "experience_required"
            ),

        "created_at":
            datetime.now(
                timezone.utc
            ),

        "updated_at":
            datetime.now(
                timezone.utc
            )

    }


    # =====================================================
    # SAVE TO MONGODB
    # =====================================================

    try:

        result = (
            jobs_collection.insert_one(
                job
            )
        )

    except Exception as error:

        print(
            "Job requirement insertion error:",
            error
        )

        return jsonify({

            "success": False,

            "message":
                "Failed to save job requirement"

        }), 500


    # =====================================================
    # RESPONSE
    # =====================================================

    return jsonify({

        "success": True,

        "message":
            "Job requirement created successfully",

        "job_id":
            str(
                result.inserted_id
            )

    }), 201


# =========================================================
# GET ALL JOB REQUIREMENTS
# =========================================================

@job_routes.route(
    "/",
    methods=["GET"]
)
def get_job_requirements():

    try:

        jobs = list(
            jobs_collection.find({})
        )

        for job in jobs:

            job["_id"] = str(
                job["_id"]
            )

        return jsonify({

            "success": True,

            "count":
                len(jobs),

            "jobs":
                jobs

        }), 200

    except Exception as error:

        print(
            "Job retrieval error:",
            error
        )

        return jsonify({

            "success": False,

            "message":
                "Failed to retrieve job requirements"

        }), 500


# =========================================================
# GET SINGLE JOB REQUIREMENT
# =========================================================

@job_routes.route(
    "/<job_id>",
    methods=["GET"]
)
def get_job_requirement(
    job_id
):

    try:

        object_id = ObjectId(
            job_id
        )

    except InvalidId:

        return jsonify({

            "success": False,

            "message":
                "Invalid job ID"

        }), 400


    try:

        job = (
            jobs_collection.find_one({

                "_id":
                    object_id

            })
        )

    except Exception as error:

        print(
            "Job retrieval error:",
            error
        )

        return jsonify({

            "success": False,

            "message":
                "Failed to retrieve job"

        }), 500


    if not job:

        return jsonify({

            "success": False,

            "message":
                "Job requirement not found"

        }), 404


    job["_id"] = str(
        job["_id"]
    )


    return jsonify({

        "success": True,

        "job":
            job

    }), 200


# =========================================================
# UPDATE JOB REQUIREMENT
# =========================================================

@job_routes.route(
    "/<job_id>",
    methods=["PUT"]
)
def update_job_requirement(
    job_id
):

    try:

        object_id = ObjectId(
            job_id
        )

    except InvalidId:

        return jsonify({

            "success": False,

            "message":
                "Invalid job ID"

        }), 400


    data = request.get_json(
        silent=True
    )

    if not data:

        return jsonify({

            "success": False,

            "message":
                "Invalid JSON data"

        }), 400


    allowed_fields = [

        "company_name",

        "job_role",

        "job_description",

        "required_skills",

        "preferred_skills",

        "minimum_score",

        "location",

        "employment_type",

        "experience_required"

    ]


    update_data = {}


    for field in allowed_fields:

        if field in data:

            update_data[field] = data[
                field
            ]


    if "minimum_score" in update_data:

        try:

            score = float(
                update_data[
                    "minimum_score"
                ]
            )

        except (
            TypeError,
            ValueError
        ):

            return jsonify({

                "success": False,

                "message":
                    "minimum_score must be a number"

            }), 400


        if score < 0 or score > 10:

            return jsonify({

                "success": False,

                "message":
                    "minimum_score must be between 0 and 10"

            }), 400


        update_data[
            "minimum_score"
        ] = score


    if not update_data:

        return jsonify({

            "success": False,

            "message":
                "No valid update fields provided"

        }), 400


    update_data[
        "updated_at"
    ] = datetime.now(
        timezone.utc
    )


    result = jobs_collection.update_one(

        {
            "_id":
                object_id
        },

        {
            "$set":
                update_data
        }

    )


    if result.matched_count == 0:

        return jsonify({

            "success": False,

            "message":
                "Job requirement not found"

        }), 404


    return jsonify({

        "success": True,

        "message":
            "Job requirement updated successfully"

    }), 200


# =========================================================
# DELETE JOB REQUIREMENT
# =========================================================

@job_routes.route(
    "/<job_id>",
    methods=["DELETE"]
)
def delete_job_requirement(
    job_id
):

    try:

        object_id = ObjectId(
            job_id
        )

    except InvalidId:

        return jsonify({

            "success": False,

            "message":
                "Invalid job ID"

        }), 400


    result = jobs_collection.delete_one({

        "_id":
            object_id

    })


    if result.deleted_count == 0:

        return jsonify({

            "success": False,

            "message":
                "Job requirement not found"

        }), 404


    return jsonify({

        "success": True,

        "message":
            "Job requirement deleted successfully"

    }), 200