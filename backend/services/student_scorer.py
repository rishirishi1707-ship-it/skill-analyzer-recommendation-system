# =========================================================
# services/student_scorer.py
# =========================================================

"""
Student scoring engine.

Calculates a consistent score from 0.0 to 10.0 using:

1. Skills / proficiency       -> 4.0
2. CGPA                       -> 2.0
3. Certifications             -> 1.5
4. Projects                   -> 1.5
5. Resume/document evidence   -> 1.0

The LLM is NOT responsible for calculating this score.
The LLM analyzes the student; this service calculates
the numerical score deterministically.
"""


# =========================================================
# PROFICIENCY VALUES
# =========================================================

PROFICIENCY_SCORES = {

    "beginner": 0.25,

    "basic": 0.25,

    "intermediate": 0.50,

    "advanced": 0.75,

    "expert": 1.00

}


# =========================================================
# NORMALIZE TEXT
# =========================================================

def normalize_text(value):

    if value is None:

        return ""

    return str(value).strip().lower()


# =========================================================
# SKILL SCORE
# =========================================================

def calculate_skill_score(skills):

    if not isinstance(skills, list):

        return 0.0


    if not skills:

        return 0.0


    total = 0.0

    valid_skills = 0


    for skill in skills:

        # -------------------------------------------------
        # Skill can be:
        #
        # {"name": "Python", "proficiency": "Advanced"}
        #
        # or simply:
        #
        # "Python"
        # -------------------------------------------------

        if isinstance(skill, dict):

            proficiency = normalize_text(
                skill.get(
                    "proficiency"
                )
            )

            score = PROFICIENCY_SCORES.get(
                proficiency,
                0.50
            )

        else:

            score = 0.50


        total += score

        valid_skills += 1


    if valid_skills == 0:

        return 0.0


    # Average proficiency
    average = (
        total / valid_skills
    )


    # Maximum contribution = 4
    return round(
        average * 4.0,
        2
    )


# =========================================================
# CGPA SCORE
# =========================================================

def calculate_cgpa_score(
    cgpa
):

    try:

        cgpa = float(cgpa)

    except (
        TypeError,
        ValueError
    ):

        return 0.0


    # -----------------------------------------------------
    # Expected CGPA range: 0 - 10
    # -----------------------------------------------------

    cgpa = max(
        0.0,
        min(
            cgpa,
            10.0
        )
    )


    # Maximum contribution = 2
    score = (
        cgpa / 10.0
    ) * 2.0


    return round(
        score,
        2
    )


# =========================================================
# CERTIFICATION SCORE
# =========================================================

def calculate_certification_score(
    certifications
):

    if not isinstance(
        certifications,
        list
    ):

        return 0.0


    count = len(
        certifications
    )


    if count == 0:

        return 0.0


    # -----------------------------------------------------
    # Certification scoring
    #
    # 0 certificates = 0
    # 1 certificate  = 0.5
    # 2 certificates = 0.9
    # 3 certificates = 1.2
    # 4+ certificates = 1.5
    # -----------------------------------------------------

    if count == 1:

        score = 0.5

    elif count == 2:

        score = 0.9

    elif count == 3:

        score = 1.2

    else:

        score = 1.5


    return round(
        score,
        2
    )


# =========================================================
# PROJECT SCORE
# =========================================================

def calculate_project_score(
    projects
):

    if not isinstance(
        projects,
        list
    ):

        return 0.0


    count = len(
        projects
    )


    if count == 0:

        return 0.0


    # -----------------------------------------------------
    # Project scoring
    # -----------------------------------------------------

    if count == 1:

        score = 0.6

    elif count == 2:

        score = 1.0

    elif count == 3:

        score = 1.3

    else:

        score = 1.5


    return round(
        score,
        2
    )


# =========================================================
# DOCUMENT EVIDENCE SCORE
# =========================================================

def calculate_document_score(
    resume,
    certifications
):

    score = 0.0


    # -----------------------------------------------------
    # Resume
    # -----------------------------------------------------

    resume_exists = False


    if isinstance(
        resume,
        dict
    ):

        if resume.get(
            "has_resume"
        ):

            resume_exists = True

        if resume.get(
            "file"
        ):

            resume_exists = True

        if resume.get(
            "resume_name"
        ):

            resume_exists = True


    # -----------------------------------------------------
    # Resume contribution
    # Maximum = 0.7
    # -----------------------------------------------------

    if resume_exists:

        score += 0.7


    # -----------------------------------------------------
    # Certificate document evidence
    # -----------------------------------------------------

    certificate_document_count = 0


    if isinstance(
        certifications,
        list
    ):

        for certification in certifications:

            if not isinstance(
                certification,
                dict
            ):

                continue


            if certification.get(
                "file"
            ):

                certificate_document_count += 1


    # -----------------------------------------------------
    # Certificate document contribution
    # Maximum = 0.3
    # -----------------------------------------------------

    if certificate_document_count > 0:

        score += 0.3


    return round(
        min(
            score,
            1.0
        ),
        2
    )


# =========================================================
# COMPLETE STUDENT SCORE
# =========================================================

def calculate_student_score(
    student
):

    if not isinstance(
        student,
        dict
    ):

        return {

            "score": 0.0,

            "components": {},

            "message":
                "Invalid student data"

        }


    # =====================================================
    # GET DATA
    # =====================================================

    academic = student.get(
        "academic",
        {}
    )

    if not isinstance(
        academic,
        dict
    ):

        academic = {}


    skills = student.get(
        "skills",
        []
    )


    certifications = student.get(
        "certifications",
        []
    )


    projects = student.get(
        "projects",
        []
    )


    resume = student.get(
        "resume",
        {}
    )


    # =====================================================
    # CALCULATE COMPONENTS
    # =====================================================

    skill_score = calculate_skill_score(
        skills
    )


    cgpa_score = calculate_cgpa_score(
        academic.get(
            "current_cgpa"
        )
    )


    certification_score = (
        calculate_certification_score(
            certifications
        )
    )


    project_score = (
        calculate_project_score(
            projects
        )
    )


    document_score = (
        calculate_document_score(
            resume,
            certifications
        )
    )


    # =====================================================
    # TOTAL
    # =====================================================

    total_score = (

        skill_score

        + cgpa_score

        + certification_score

        + project_score

        + document_score

    )


    # -----------------------------------------------------
    # Safety limit
    # -----------------------------------------------------

    total_score = max(
        0.0,
        min(
            total_score,
            10.0
        )
    )


    total_score = round(
        total_score,
        1
    )


    # =====================================================
    # RETURN
    # =====================================================

    return {

        "score": total_score,

        "scale": "0-10",

        "components": {

            "skills": {
                "score": skill_score,
                "maximum": 4.0
            },

            "cgpa": {
                "score": cgpa_score,
                "maximum": 2.0
            },

            "certifications": {
                "score": certification_score,
                "maximum": 1.5
            },

            "projects": {
                "score": project_score,
                "maximum": 1.5
            },

            "document_evidence": {
                "score": document_score,
                "maximum": 1.0
            }

        }

    }


# =========================================================
# SCORE LABEL
# =========================================================

def get_score_label(
    score
):

    try:

        score = float(
            score
        )

    except (
        TypeError,
        ValueError
    ):

        return "Not Available"


    if score >= 9.0:

        return "Excellent"

    if score >= 8.0:

        return "Very Strong"

    if score >= 7.0:

        return "Strong"

    if score >= 6.0:

        return "Good"

    if score >= 5.0:

        return "Developing"

    return "Needs Improvement"