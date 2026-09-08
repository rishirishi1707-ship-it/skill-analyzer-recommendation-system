# =========================================================
# services/llm_worker.py
# =========================================================

import threading

from datetime import datetime, timezone

from bson import ObjectId
from bson.errors import InvalidId

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
# HELPER: NORMALIZE DETECTED SKILLS
# =========================================================

def normalize_detected_skills(
    detected_skills
):

    if not isinstance(
        detected_skills,
        dict
    ):

        return empty_detected_skills()


    skills = detected_skills.get(
        "skills",
        []
    )


    categorized_skills = detected_skills.get(
        "categorized_skills",
        {}
    )


    skill_details = detected_skills.get(
        "skill_details",
        []
    )


    document_count = detected_skills.get(
        "document_count",
        0
    )


    if not isinstance(
        skills,
        list
    ):

        skills = []


    if not isinstance(
        categorized_skills,
        dict
    ):

        categorized_skills = {}


    if not isinstance(
        skill_details,
        list
    ):

        skill_details = []


    try:

        document_count = int(
            document_count
        )

    except (
        TypeError,
        ValueError
    ):

        document_count = 0


    return {

        "skills":
            skills,

        "categorized_skills":
            categorized_skills,

        "skill_details":
            skill_details,

        "document_count":
            document_count

    }


# =========================================================
# HELPER: GET DETECTED SKILLS
# =========================================================

def get_detected_skills(
    student
):

    """
    Get automatically detected skills.

    Primary location:

        student["llm_analysis"]["detected_skills"]

    Backward compatibility:

        student["detected_skills"]
    """

    if not isinstance(
        student,
        dict
    ):

        return empty_detected_skills()


    # =====================================================
    # PRIMARY LOCATION
    # llm_analysis.detected_skills
    # =====================================================

    llm_analysis = student.get(
        "llm_analysis",
        {}
    )


    if isinstance(
        llm_analysis,
        dict
    ):

        detected_skills = llm_analysis.get(
            "detected_skills"
        )


        if isinstance(
            detected_skills,
            dict
        ):

            return normalize_detected_skills(
                detected_skills
            )


    # =====================================================
    # BACKWARD COMPATIBILITY
    # top-level detected_skills
    # =====================================================

    detected_skills = student.get(
        "detected_skills"
    )


    if isinstance(
        detected_skills,
        dict
    ):

        # ---------------------------------------------
        # Old registration structure
        # ---------------------------------------------

        if "all" in detected_skills:

            return normalize_detected_skills({

                "skills":
                    detected_skills.get(
                        "all",
                        []
                    ),

                "categorized_skills":
                    detected_skills.get(
                        "categorized_skills",
                        {}
                    ),

                "skill_details":
                    detected_skills.get(
                        "details",
                        []
                    ),

                "document_count":
                    detected_skills.get(
                        "document_count",
                        0
                    )

            })


        # ---------------------------------------------
        # Already new structure
        # ---------------------------------------------

        return normalize_detected_skills(
            detected_skills
        )


    return empty_detected_skills()


# =========================================================
# PREPARE STUDENT FOR ANALYSIS
# =========================================================

def prepare_student_for_analysis(
    student
):

    """
    Prepare student data before sending it
    to llm_analyzer.py.

    Detected skills are guaranteed to exist in:

        student["llm_analysis"]["detected_skills"]

    and also temporarily copied to:

        student["detected_skills"]

    for backward compatibility.
    """

    if not isinstance(
        student,
        dict
    ):

        return {}


    # =====================================================
    # COPY STUDENT
    # =====================================================

    analysis_student = dict(
        student
    )


    # =====================================================
    # GET DETECTED SKILLS
    # =====================================================

    detected_skills = get_detected_skills(
        student
    )


    # =====================================================
    # TEMPORARY TOP-LEVEL COPY
    # =====================================================

    analysis_student[
        "detected_skills"
    ] = detected_skills


    # =====================================================
    # ENSURE LLM ANALYSIS STRUCTURE
    # =====================================================

    llm_analysis = analysis_student.get(
        "llm_analysis",
        {}
    )


    if not isinstance(
        llm_analysis,
        dict
    ):

        llm_analysis = {}


    llm_analysis[
        "detected_skills"
    ] = detected_skills


    analysis_student[
        "llm_analysis"
    ] = llm_analysis


    return analysis_student


# =========================================================
# BACKGROUND LLM ANALYSIS
# =========================================================

def run_llm_analysis(
    student_id
):

    object_id = None


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
        # CONVERT STUDENT ID
        # =================================================

        try:

            object_id = ObjectId(
                student_id
            )

        except InvalidId:

            raise ValueError(
                "Invalid student ID"
            )


        # =================================================
        # GET STUDENT
        # =================================================

        student = students_collection.find_one(

            {
                "_id":
                    object_id
            }

        )


        if not student:

            raise ValueError(
                "Student not found"
            )


        # =================================================
        # MARK PROCESSING
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
        # REFRESH STUDENT DATA
        # =================================================

        student = students_collection.find_one(

            {
                "_id":
                    object_id
            }

        )


        if not student:

            raise ValueError(
                "Student not found after refresh"
            )


        # =================================================
        # GET DETECTED SKILLS
        # =================================================

        detected_skills = get_detected_skills(
            student
        )


        # =================================================
        # PREPARE STUDENT
        # =================================================

        analysis_student = (
            prepare_student_for_analysis(
                student
            )
        )


        # =================================================
        # DEBUG DETECTED SKILLS
        # =================================================

        print(
            "\n========================================"
        )

        print(
            "DOCUMENT SKILLS SENT TO LLM"
        )

        print(
            "========================================"
        )

        print(
            "Skills:",
            detected_skills.get(
                "skills",
                []
            )
        )

        print(
            "Document count:",
            detected_skills.get(
                "document_count",
                0
            )
        )

        print(
            "========================================\n"
        )


        # =================================================
        # RUN LLM ANALYSIS
        # =================================================

        print(
            "Sending student data to Ollama..."
        )


        result = analyze_student(
            analysis_student
        )


        # =================================================
        # DEBUG RESULT
        # =================================================

        print(
            "\n========================================"
        )

        print(
            "LLM ANALYSIS RESPONSE"
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
        # VALIDATE RESULT
        # =================================================

        if not isinstance(
            result,
            dict
        ):

            raise ValueError(
                "Invalid LLM response"
            )


        # =================================================
        # HANDLE LLM ERROR
        # =================================================

        if result.get(
            "error"
        ):

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


            print(
                "LLM analysis failed:",
                result.get(
                    "error"
                )
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


        # =================================================
        # CREATE SCORING STUDENT
        # =================================================

        scoring_student = dict(
            student
        )


        # -------------------------------------------------
        # Build analysis structure for scorer
        # -------------------------------------------------

        scoring_llm_analysis = dict(
            result
        )


        scoring_llm_analysis[
            "detected_skills"
        ] = detected_skills


        scoring_student[
            "llm_analysis"
        ] = scoring_llm_analysis


        scoring_student[
            "detected_skills"
        ] = detected_skills


        # =================================================
        # CALCULATE SCORE
        # =================================================

        score_result = (
            calculate_student_score(
                scoring_student
            )
        )


        if not isinstance(
            score_result,
            dict
        ):

            score_result = {

                "score":
                    0.0,

                "components":
                    {}

            }


        student_score = score_result.get(
            "score",
            0.0
        )


        try:

            student_score = float(
                student_score
            )

        except (
            TypeError,
            ValueError
        ):

            student_score = 0.0


        # =================================================
        # SCORE LABEL
        # =================================================

        score_label = get_score_label(
            student_score
        )


        print(
            "Student Score:",
            student_score,
            "/10"
        )

        print(
            "Score Label:",
            score_label
        )

        print(
            "========================================\n"
        )


        # =================================================
        # PREPARE FINAL ANALYSIS
        # =================================================

        llm_analysis_data = dict(
            result
        )


        # =================================================
        # STATUS
        # =================================================

        llm_analysis_data[
            "status"
        ] = "completed"


        # =================================================
        # DETECTED SKILLS
        # =================================================

        llm_analysis_data[
            "detected_skills"
        ] = detected_skills


        # =================================================
        # SCORE
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
        # TIMESTAMPS
        # =================================================

        llm_analysis_data[
            "completed_at"
        ] = datetime.now(
            timezone.utc
        )


        # =================================================
        # SAVE FINAL RESULT
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


        # =================================================
        # SUCCESS LOG
        # =================================================

        print(
            "\n========================================"
        )

        print(
            "BACKGROUND LLM ANALYSIS COMPLETED"
        )

        print(
            "========================================"
        )

        print(
            "Student Score:",
            student_score,
            "/10"
        )

        print(
            "Score Label:",
            score_label
        )

        print(
            "Detected Skills:"
        )

        print(
            detected_skills.get(
                "skills",
                []
            )
        )

        print(
            "========================================\n"
        )


    # =====================================================
    # HANDLE BACKGROUND ERROR
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
            str(
                error
            )
        )

        print(
            "========================================\n"
        )


        if object_id:

            try:

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
# START BACKGROUND LLM ANALYSIS
# =========================================================

def start_llm_analysis(
    student_id
):

    """
    Start LLM analysis in a background thread.

    Registration requests do not wait for
    the LLM analysis to complete.
    """

    worker = threading.Thread(

        target=run_llm_analysis,

        args=(

            str(
                student_id
            ),

        ),

        daemon=True,

        name=(
            f"LLMWorker-"
            f"{student_id}"
        )

    )


    worker.start()


    return worker


# =========================================================
# BACKWARD COMPATIBILITY
# =========================================================

def start_background_llm_analysis(
    student_id
):

    return start_llm_analysis(
        student_id
    )