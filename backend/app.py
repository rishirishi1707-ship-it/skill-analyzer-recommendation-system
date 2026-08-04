from flask import Flask
from flask_cors import CORS

from config import db
from routes.student_routes import student_routes


app = Flask(__name__)

CORS(app)


# =========================================================
# STUDENT ROUTES
# =========================================================

app.register_blueprint(
    student_routes,
    url_prefix="/api/students"
)


# =========================================================
# HOME
# =========================================================

@app.route("/")
def home():

    return {
        "message":
            "Skill Analyzer API is running!"
    }


# =========================================================
# MONGODB HEALTH CHECK
# =========================================================

@app.route("/api/health")
def health():

    try:

        db.command("ping")

        return {

            "status":
                "success",

            "mongodb":
                "connected"

        }

    except Exception as e:

        return {

            "status":
                "error",

            "mongodb":
                "not connected",

            "message":
                str(e)

        }, 500


# =========================================================
# START APPLICATION
# =========================================================

if __name__ == "__main__":

    app.run(
        debug=True
    )