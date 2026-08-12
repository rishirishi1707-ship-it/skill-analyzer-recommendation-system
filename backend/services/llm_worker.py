# =========================================================
# services/llm_worker.py
# =========================================================

import threading

from datetime import datetime, timezone

from bson import ObjectId

from config import db

from services.llm_analyzer import (
    analyze_student
)

from services.student_scorer import (
    calculate_student_score,
    get_score_label
)


# =========================================================
# MONGODB COLLECTION
# =========================================================

students_collection = db["students"]


# =========================================================
# BACKGROUND LLM ANALYSIS
# =========================================================

def run_llm_analysis(student_id):

    print(
        "\n========================================"
    )

    print(
        "BACKGROUND LLM ANALYSIS STARTED"
    )

    print(
        "Student ID:",
        student_id
    )

    print(
        "========================================\n"
    )


    try:

        # =================================================
        # CONVERT ID
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

            print(
                "Background LLM error:"
                " Student not found"
            )

            return


        # =================================================
        # MARK ANALYSIS AS PROCESSING
        # =================================================

        students_collection.update_one(

            {
                "_id":
                    object_id
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


        # =================================================
        # RUN LLM ANALYSIS
        # =================================================

        print(
            "Sending student data to Ollama..."
        )


        result = analyze_student(
            student
        )


        print(
            "\n========================================"
        )

        print(
            "LLM ANALYSIS COMPLETED"
        )

        print(
            "========================================"
        )

        print(
            result
        )

        print(
            "========================================\n"
        )


        # =================================================
        # HANDLE LLM ERROR
        # =================================================

        if not isinstance(
            result,
            dict
        ):

            raise ValueError(
                "Invalid LLM response"
            )


        if "error" in result:

            students_collection.update_one(

                {
                    "_id":
                        object_id
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

            return


        # =================================================
        # CALCULATE STUDENT SCORE
        # =================================================

        print(
            "\n========================================"
        )

        print(
            "CALCULATING STUDENT SCORE"
        )

        print(
            "========================================"
        )


        # -------------------------------------------------
        # IMPORTANT
        #
        # The LLM result is temporarily merged into the
        # student data so future scoring can use detected
        # information if needed.
        # -------------------------------------------------

        scoring_student = dict(
            student
        )


        scoring_student[
            "llm_analysis"
        ] = result


        # -------------------------------------------------
        # Calculate deterministic score
        # -------------------------------------------------

        score_result = (
            calculate_student_score(
                scoring_student
            )
        )


        student_score = (
            score_result.get(
                "score",
                0.0
            )
        )


        score_label = (
            get_score_label(
                student_score
            )
        )


        print(
            "Student Score:",
            student_score,
            "/ 10"
        )


        print(
            "Score Label:",
            score_label
        )


        print(
            "========================================\n"
        )


        # =================================================
        # PREPARE LLM ANALYSIS DATA
        # =================================================

        llm_analysis_data = dict(
            result
        )


        llm_analysis_data[
            "status"
        ] = "completed"


        llm_analysis_data[
            "completed_at"
        ] = datetime.now(
            timezone.utc
        )


        # =================================================
        # STORE SCORE
        # =================================================

        llm_analysis_data[
            "student_score"
        ] = student_score


        llm_analysis_data[
            "score_scale"
        ] = "0-10"


        llm_analysis_data[
            "score_label"
        ] = score_label


        llm_analysis_data[
            "score_components"
        ] = score_result.get(
            "components",
            {}
        )


        # =================================================
        # SAVE EVERYTHING
        # =================================================

        students_collection.update_one(

            {
                "_id":
                    object_id
            },

            {
                "$set": {

                    "llm_analysis":
                        llm_analysis_data,

                    "student_score":
                        student_score,

                    "student_score_label":
                        score_label,

                    "student_score_components":
                        score_result.get(
                            "components",
                            {}
                        )

                }
            }

        )


        print(
            "\n========================================"
        )

        print(
            "BACKGROUND PROCESS COMPLETED"
        )

        print(
            "Student Score:",
            student_score,
            "/10"
        )

        print(
            "========================================\n"
        )


    # =====================================================
    # BACKGROUND WORKER ERROR
    # =====================================================

    except Exception as error:

        print(
            "\n========================================"
        )

        print(
            "BACKGROUND LLM ANALYSIS ERROR"
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


        # =================================================
        # SAVE ERROR TO MONGODB
        # =================================================

        try:

            students_collection.update_one(

                {
                    "_id":
                        ObjectId(
                            student_id
                        )
                },

                {
                    "$set": {

                        "llm_analysis.status":
                            "failed",

                        "llm_analysis.error":
                            str(
                                error
                            ),

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

def start_llm_analysis(
    student_id
):

    """
    Starts the LLM analysis in a background thread.

    Registration does NOT wait for Ollama.
    """

    worker = threading.Thread(

        target=run_llm_analysis,

        args=(student_id,),

        daemon=False,

        name=f"LLMWorker-{student_id}"

    )


    worker.start()


    return worker


# =========================================================
# BACKWARD-COMPATIBILITY ALIAS
# =========================================================

def start_background_llm_analysis(
    student_id
):

    """
    Compatibility wrapper.

    This allows student_routes.py to use either:

        start_llm_analysis()

    or:

        start_background_llm_analysis()
    """

    return start_llm_analysis(
        student_id
    )