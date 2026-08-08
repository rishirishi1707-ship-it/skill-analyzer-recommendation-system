from flask import Flask, jsonify
from flask_cors import CORS
import os

# =========================================================
# FLASK APP
# =========================================================

app = Flask(__name__)

# =========================================================
# CORS
# =========================================================

CORS(
    app,
    resources={
        r"/api/*": {
            "origins": "*"
        }
    }
)

# =========================================================
# CONFIGURATION
# =========================================================

app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16 MB

# =========================================================
# UPLOAD DIRECTORIES
# =========================================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
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

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["RESUME_FOLDER"] = RESUME_FOLDER
app.config["CERTIFICATE_FOLDER"] = CERTIFICATE_FOLDER


# =========================================================
# REGISTER STUDENT ROUTES
# =========================================================

try:

    from routes.student_routes import student_routes

    app.register_blueprint(
        student_routes,
        url_prefix="/api/students"
    )

    print(
        "Student routes registered successfully."
    )

except Exception as error:

    print(
        "ERROR: Could not load student routes."
    )

    print(error)

    raise


# =========================================================
# HOME / SERVER TEST
# =========================================================

@app.route("/", methods=["GET"])
def home():

    return jsonify({

        "success": True,

        "message":
            "Skill Analyzer Backend is running",

        "status":
            "online"

    }), 200


# =========================================================
# API HEALTH CHECK
# =========================================================

@app.route("/api/health", methods=["GET"])
def health_check():

    return jsonify({

        "success": True,

        "message":
            "API is working",

        "service":
            "Skill Analyzer & Recommendation System"

    }), 200


# =========================================================
# 404 HANDLER
# =========================================================

@app.errorhandler(404)
def not_found(error):

    return jsonify({

        "success": False,

        "message":
            "API endpoint not found",

        "path":
            getattr(
                error,
                "description",
                "Unknown endpoint"
            )

    }), 404


# =========================================================
# GENERAL ERROR HANDLER
# =========================================================

@app.errorhandler(500)
def internal_error(error):

    return jsonify({

        "success": False,

        "message":
            "Internal server error"

    }), 500


# =========================================================
# START SERVER
# =========================================================

if __name__ == "__main__":

    print("\n========================================")
    print(" SKILL ANALYZER BACKEND")
    print("========================================")
    print(
        "Backend folder:",
        BASE_DIR
    )
    print(
        "Resume folder:",
        RESUME_FOLDER
    )
    print(
        "Certificate folder:",
        CERTIFICATE_FOLDER
    )
    print(
        "Student API:",
        "http://127.0.0.1:5000/api/students"
    )
    print(
        "Health API:",
        "http://127.0.0.1:5000/api/health"
    )
    print("========================================\n")

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )