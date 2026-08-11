# =========================================================
# services/llm_worker.py
# =========================================================

import threading
from datetime import datetime, timezone

from bson import ObjectId

from config import db
from services.llm_analyzer import analyze_student


# =========================================================
# MONGODB COLLECTION
# =========================================================

students_collection = db["students"]


# =========================================================
# LLM BACKGROUND WORKER
# =========================================================

def run_llm_analysis(student_id):
    """
    Runs LLM analysis after student registration.

    This function runs independently from the registration
    request so the student does not have to wait for Ollama.
    """

    print("\n========================================")
    print("BACKGROUND LLM ANALYSIS STARTED")
    print("Student ID:", student_id)
    print("========================================\n")

    try:

        # -------------------------------------------------
        # Convert ID
        # -------------------------------------------------

        object_id = ObjectId(student_id)

        # -------------------------------------------------
        # Get student from MongoDB
        # -------------------------------------------------

        student = students_collection.find_one({
            "_id": object_id
        })

        if not student:

            print(
                "Background LLM error: "
                "Student not found"
            )

            return

        # -------------------------------------------------
        # Mark analysis as processing
        # -------------------------------------------------

        students_collection.update_one(

            {
                "_id": object_id
            },

            {
                "$set": {

                    "llm_analysis.status":
                        "processing",

                    "llm_analysis.started_at":
                        datetime.now(
                            timezone.utc
                        )

                }
            }

        )

        # -------------------------------------------------
        # Call Ollama
        # -------------------------------------------------

        result = analyze_student(student)

        print("\n========================================")
        print("BACKGROUND LLM ANALYSIS COMPLETED")
        print("========================================")
        print(result)
        print("========================================\n")

        # -------------------------------------------------
        # Successful analysis
        # -------------------------------------------------

        if isinstance(result, dict):

            if "error" in result:

                students_collection.update_one(

                    {
                        "_id": object_id
                    },

                    {
                        "$set": {

                            "llm_analysis.status":
                                "failed",

                            "llm_analysis.error":
                                result.get(
                                    "error"
                                ),

                            "llm_analysis.raw_response":
                                result.get(
                                    "raw_response"
                                ),

                            "llm_analysis.completed_at":
                                datetime.now(
                                    timezone.utc
                                )

                        }
                    }

                )

            else:

                # -----------------------------------------
                # Store complete LLM result
                # -----------------------------------------

                update_data = dict(result)

                update_data[
                    "status"
                ] = "completed"

                update_data[
                    "completed_at"
                ] = datetime.now(
                    timezone.utc
                )

                students_collection.update_one(

                    {
                        "_id": object_id
                    },

                    {
                        "$set": {

                            "llm_analysis":
                                update_data

                        }
                    }

                )

        else:

            students_collection.update_one(

                {
                    "_id": object_id
                },

                {
                    "$set": {

                        "llm_analysis.status":
                            "failed",

                        "llm_analysis.error":
                            "Invalid LLM response",

                        "llm_analysis.completed_at":
                            datetime.now(
                                timezone.utc
                            )

                    }
                }

            )

    except Exception as error:

        print("\n========================================")
        print("BACKGROUND LLM ANALYSIS ERROR")
        print("========================================")
        print(error)
        print("========================================\n")

        # -------------------------------------------------
        # Save error without breaking registration
        # -------------------------------------------------

        try:

            students_collection.update_one(

                {
                    "_id":
                        ObjectId(student_id)
                },

                {
                    "$set": {

                        "llm_analysis.status":
                            "failed",

                        "llm_analysis.error":
                            str(error),

                        "llm_analysis.completed_at":
                            datetime.now(
                                timezone.utc
                            )

                    }
                }

            )

        except Exception as db_error:

            print(
                "Could not save LLM error:",
                db_error
            )


# =========================================================
# START BACKGROUND WORKER
# =========================================================

def start_llm_analysis(student_id):
    """
    Starts the LLM analysis in a background thread.

    The thread is intentionally NOT marked as daemon.
    """

    worker = threading.Thread(

        target=run_llm_analysis,

        args=(student_id,),

        daemon=False,

        name=f"LLMWorker-{student_id}"

    )

    worker.start()

    return worker