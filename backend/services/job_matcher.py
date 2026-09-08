# =========================================================
# services/job_matcher.py
# =========================================================

import re


# =========================================================
# NORMALIZE TEXT
# =========================================================

def normalize_text(value):
    """
    Convert text into a comparable lowercase format.
    """

    if value is None:
        return ""

    text = str(value).strip().lower()

    text = re.sub(r"\s+", " ", text)

    return text


# =========================================================
# NORMALIZE SKILL
# =========================================================

def normalize_skill(skill):
    """
    Normalize skill names for comparison.
    """

    if not skill:
        return ""

    skill = normalize_text(skill)

    aliases = {
        "c plus plus": "c++",
        "cpp": "c++",
        "c sharp": "c#",
        "csharp": "c#",

        "javascript": "javascript",
        "js": "javascript",

        "typescript": "typescript",
        "ts": "typescript",

        "structured query language": "sql",

        "mongodb": "mongodb",
        "mongo db": "mongodb",

        "rest api": "rest api",
        "restful api": "rest api",

        "data structures and algorithms": "data structures",
        "dsa": "data structures",

        "machine learning": "machine learning",
        "ml": "machine learning",

        "artificial intelligence": "artificial intelligence",
        "ai": "artificial intelligence",

        "powerbi": "power bi",
        "power bi": "power bi",
    }

    return aliases.get(skill, skill)


# =========================================================
# NORMALIZE DEGREE
# =========================================================

def normalize_degree(degree):
    """
    Normalize degree names.
    """

    degree = normalize_text(degree)

    degree = degree.replace(".", "")
    degree = degree.replace(" ", "")
    degree = degree.replace("/", "")

    aliases = {
        "be": "be",
        "bachelorofengineering": "be",

        "btech": "btech",
        "bacheloroftechnology": "btech",

        "me": "me",
        "mtech": "mtech",

        "mca": "mca",

        "bsc": "bsc",
        "msc": "msc",
    }

    return aliases.get(degree, degree)


# =========================================================
# NORMALIZE BRANCH
# =========================================================

def normalize_branch(branch):
    """
    Normalize common engineering branch names.
    """

    branch = normalize_text(branch)

    branch = branch.replace(".", "")

    aliases = {
        "computer science engineering": "cse",
        "computer science and engineering": "cse",
        "computer science": "cse",
        "cse": "cse",

        "information technology": "it",
        "information tech": "it",
        "it": "it",

        "electronics and communication engineering": "ece",
        "electronics communication engineering": "ece",
        "electronics and communication": "ece",
        "ece": "ece",

        "electrical and electronics engineering": "eee",
        "electrical electronics engineering": "eee",
        "eee": "eee",

        "mechanical engineering": "mech",
        "mechanical": "mech",
        "mech": "mech",

        "civil engineering": "civil",
        "civil": "civil",
    }

    return aliases.get(branch, branch)


# =========================================================
# GET STUDENT SKILLS
# =========================================================

def get_student_skills(student):
    """
    Combine manually entered skills and
    automatically detected skills.
    """

    skills = set()

    # -----------------------------------------------------
    # MANUALLY ENTERED SKILLS
    # -----------------------------------------------------

    manual_skills = student.get(
        "skills",
        []
    )

    if isinstance(manual_skills, list):

        for skill in manual_skills:

            normalized = normalize_skill(skill)

            if normalized:
                skills.add(normalized)

    # -----------------------------------------------------
    # AUTOMATICALLY DETECTED SKILLS
    # -----------------------------------------------------

    detected_skills = student.get(
        "detected_skills",
        {}
    )

    if isinstance(detected_skills, dict):

        detected_all = detected_skills.get(
            "all",
            []
        )

        if isinstance(detected_all, list):

            for skill in detected_all:

                normalized = normalize_skill(skill)

                if normalized:
                    skills.add(normalized)

    return skills


# =========================================================
# GET STUDENT PREFERENCES
# =========================================================

def get_student_preferences(student):
    """
    Get career preferences from student profile.
    """

    preferences = student.get(
        "career_preferences",
        {}
    )

    if not isinstance(preferences, dict):
        preferences = {}

    return {
        "domain": normalize_text(
            preferences.get("interested_domain")
        ),

        "job_role": normalize_text(
            preferences.get("preferred_job_role")
        ),

        "location": normalize_text(
            preferences.get("preferred_location")
        )
    }


# =========================================================
# GET STUDENT LLM SCORE
# =========================================================

def get_student_llm_score(student):
    """
    Get the student's overall score generated
    by the LLM analysis.

    Returns None when analysis is not available.
    """

    llm_analysis = student.get(
        "llm_analysis",
        {}
    )

    if not isinstance(llm_analysis, dict):
        return None

    score = llm_analysis.get(
        "overall_score"
    )

    if score is None:
        return None

    try:

        score = float(score)

        score = max(
            0,
            min(10, score)
        )

        return score

    except (
        TypeError,
        ValueError
    ):

        return None


# =========================================================
# CHECK ELIGIBILITY
# =========================================================

def check_eligibility(student, job):
    """
    Check hard eligibility requirements.

    Graduation year is intentionally NOT checked.

    Eligibility checks:

        1. Degree
        2. Branch
        3. CGPA
        4. Maximum backlogs

    Minimum LLM score is checked separately.

    Returns:

        {
            "eligible": True/False,
            "reasons": [...]
        }
    """

    reasons = []

    personal = student.get(
        "personal",
        {}
    )

    academic = student.get(
        "academic",
        {}
    )

    if not isinstance(personal, dict):
        personal = {}

    if not isinstance(academic, dict):
        academic = {}

    eligibility = job.get(
        "eligibility",
        {}
    )

    if not isinstance(eligibility, dict):
        eligibility = {}

    # =====================================================
    # DEGREE
    # =====================================================

    student_degree = normalize_degree(
        personal.get("degree")
    )

    required_degrees = eligibility.get(
        "degrees",
        []
    )

    if required_degrees:

        normalized_degrees = [
            normalize_degree(degree)
            for degree in required_degrees
            if normalize_degree(degree)
        ]

        if (
            not student_degree
            or student_degree not in normalized_degrees
        ):

            reasons.append(
                "Degree requirement not satisfied"
            )

    # =====================================================
    # BRANCH
    # =====================================================

    student_branch = normalize_branch(
        academic.get("branch")
    )

    required_branches = eligibility.get(
        "branches",
        []
    )

    if required_branches:

        normalized_branches = [
            normalize_branch(branch)
            for branch in required_branches
            if normalize_branch(branch)
        ]

        if (
            not student_branch
            or student_branch not in normalized_branches
        ):

            reasons.append(
                "Branch requirement not satisfied"
            )

    # =====================================================
    # CGPA
    # =====================================================

    minimum_cgpa = eligibility.get(
        "minimum_cgpa"
    )

    student_cgpa = academic.get(
        "current_cgpa"
    )

    if minimum_cgpa is not None:

        try:

            student_cgpa = float(
                student_cgpa
            )

            minimum_cgpa = float(
                minimum_cgpa
            )

            if student_cgpa < minimum_cgpa:

                reasons.append(
                    f"CGPA below required minimum of "
                    f"{minimum_cgpa}"
                )

        except (
            TypeError,
            ValueError
        ):

            reasons.append(
                "CGPA information is invalid or missing"
            )

    # =====================================================
    # GRADUATION YEAR
    # =====================================================
    #
    # INTENTIONALLY REMOVED
    #
    # Jobs are recommended regardless of graduation year.
    #
    # =====================================================

    # =====================================================
    # BACKLOG / ARREARS
    # =====================================================

    maximum_backlogs = eligibility.get(
        "maximum_backlogs"
    )

    student_backlogs = academic.get(
        "number_of_arrears",
        0
    )

    if maximum_backlogs is not None:

        try:

            student_backlogs = int(
                student_backlogs or 0
            )

            maximum_backlogs = int(
                maximum_backlogs
            )

            if student_backlogs > maximum_backlogs:

                reasons.append(
                    f"Maximum allowed backlogs: "
                    f"{maximum_backlogs}"
                )

        except (
            TypeError,
            ValueError
        ):

            reasons.append(
                "Backlog information is invalid"
            )

    # =====================================================
    # RETURN
    # =====================================================

    return {
        "eligible":
            len(reasons) == 0,

        "reasons":
            reasons
    }


# =========================================================
# CALCULATE REQUIRED SKILL MATCH
# =========================================================

def calculate_skill_match(
    student_skills,
    required_skills
):
    """
    Calculate percentage of required skills
    possessed by the student.
    """

    normalized_student_skills = {
        normalize_skill(skill)
        for skill in student_skills
        if normalize_skill(skill)
    }

    normalized_required_skills = [
        normalize_skill(skill)
        for skill in required_skills
        if normalize_skill(skill)
    ]

    normalized_required_skills = list(
        dict.fromkeys(
            normalized_required_skills
        )
    )

    if not normalized_required_skills:

        return {
            "percentage": 100,
            "matched_skills": [],
            "missing_skills": []
        }

    matched_skills = [
        skill
        for skill in normalized_required_skills
        if skill in normalized_student_skills
    ]

    missing_skills = [
        skill
        for skill in normalized_required_skills
        if skill not in normalized_student_skills
    ]

    percentage = (
        len(matched_skills)
        /
        len(normalized_required_skills)
    ) * 100

    return {
        "percentage":
            round(percentage, 2),

        "matched_skills":
            matched_skills,

        "missing_skills":
            missing_skills
    }


# =========================================================
# CALCULATE PREFERRED SKILL MATCH
# =========================================================

def calculate_preferred_skill_match(
    student_skills,
    preferred_skills
):
    """
    Calculate preferred skill match.
    """

    normalized_student_skills = {
        normalize_skill(skill)
        for skill in student_skills
        if normalize_skill(skill)
    }

    normalized_preferred_skills = [
        normalize_skill(skill)
        for skill in preferred_skills
        if normalize_skill(skill)
    ]

    normalized_preferred_skills = list(
        dict.fromkeys(
            normalized_preferred_skills
        )
    )

    if not normalized_preferred_skills:

        return {
            "percentage": 0,
            "matched_skills": [],
            "missing_skills": []
        }

    matched_skills = [
        skill
        for skill in normalized_preferred_skills
        if skill in normalized_student_skills
    ]

    missing_skills = [
        skill
        for skill in normalized_preferred_skills
        if skill not in normalized_student_skills
    ]

    percentage = (
        len(matched_skills)
        /
        len(normalized_preferred_skills)
    ) * 100

    return {
        "percentage":
            round(percentage, 2),

        "matched_skills":
            matched_skills,

        "missing_skills":
            missing_skills
    }


# =========================================================
# CALCULATE ROLE / DOMAIN PREFERENCE
# =========================================================

def calculate_preference_match(
    student,
    job
):
    """
    Calculate how well the job matches the
    student's career preferences.

    Returns a percentage from 0 to 100.
    """

    preferences = get_student_preferences(
        student
    )

    job_role = normalize_text(
        job.get("job_role")
    )

    job_description = normalize_text(
        job.get("job_description")
    )

    job_locations = job.get(
        "location",
        []
    )

    if isinstance(job_locations, str):

        job_locations = [
            job_locations
        ]

    if not isinstance(job_locations, list):

        job_locations = []

    normalized_locations = [
        normalize_text(location)
        for location in job_locations
        if normalize_text(location)
    ]

    score = 0

    # =====================================================
    # JOB ROLE
    # =====================================================

    preferred_role = preferences["job_role"]

    if preferred_role:

        if (
            preferred_role in job_role
            or job_role in preferred_role
        ):

            score += 50

        elif any(
            word in job_role
            for word in preferred_role.split()
            if len(word) > 2
        ):

            score += 25

    # =====================================================
    # DOMAIN
    # =====================================================

    preferred_domain = preferences["domain"]

    if preferred_domain:

        domain_keywords = {

            "software": [
                "software",
                "developer",
                "development",
                "programmer",
                "engineer"
            ],

            "web development": [
                "web",
                "frontend",
                "backend",
                "full stack",
                "fullstack"
            ],

            "data science": [
                "data",
                "analytics",
                "machine learning",
                "data science"
            ],

            "artificial intelligence": [
                "ai",
                "artificial intelligence",
                "machine learning"
            ],

            "cloud computing": [
                "cloud",
                "aws",
                "azure",
                "devops"
            ],

            "cyber security": [
                "security",
                "cyber",
                "cybersecurity"
            ]
        }

        keywords = domain_keywords.get(
            preferred_domain,
            preferred_domain.split()
        )

        domain_match = any(

            keyword in job_role
            or keyword in job_description

            for keyword in keywords

        )

        if domain_match:

            score += 30

    # =====================================================
    # LOCATION
    # =====================================================

    preferred_location = preferences["location"]

    if preferred_location:

        if any(

            preferred_location in location
            or location in preferred_location

            for location in normalized_locations

        ):

            score += 20

    return min(
        score,
        100
    )


# =========================================================
# CHECK MINIMUM LLM SCORE
# =========================================================

def check_minimum_score(
    student,
    job
):
    """
    Check the student's LLM score against
    the job's minimum score.

    If the student's score is unavailable,
    the job is not rejected because of score.
    """

    minimum_score = job.get(
        "minimum_score"
    )

    student_score = get_student_llm_score(
        student
    )

    # =====================================================
    # NO MINIMUM SCORE CONFIGURED
    # =====================================================

    if minimum_score is None:

        return {
            "passed": True,
            "student_score":
                student_score,
            "minimum_score":
                None,
            "reason":
                None
        }

    try:

        minimum_score = float(
            minimum_score
        )

    except (
        TypeError,
        ValueError
    ):

        return {
            "passed": True,
            "student_score":
                student_score,
            "minimum_score":
                None,
            "reason":
                None
        }

    # =====================================================
    # LLM SCORE NOT AVAILABLE
    # =====================================================

    if student_score is None:

        return {
            "passed": True,
            "student_score":
                None,
            "minimum_score":
                minimum_score,
            "reason":
                "LLM score not available yet"
        }

    # =====================================================
    # CHECK SCORE
    # =====================================================

    if student_score < minimum_score:

        return {
            "passed": False,
            "student_score":
                student_score,
            "minimum_score":
                minimum_score,
            "reason":
                f"Student score {student_score} "
                f"is below required score "
                f"{minimum_score}"
        }

    return {
        "passed": True,
        "student_score":
            student_score,
        "minimum_score":
            minimum_score,
        "reason":
            None
    }


# =========================================================
# CALCULATE FINAL SCORE
# =========================================================

def calculate_final_score(
    required_skill_percentage,
    preferred_skill_percentage,
    preference_percentage
):
    """
    Calculate final recommendation score.

    Weighting:

        Required skills   = 65%
        Preferred skills  = 15%
        Career preference = 20%

    Final score = 0 to 100
    """

    final_score = (

        required_skill_percentage * 0.65

        +

        preferred_skill_percentage * 0.15

        +

        preference_percentage * 0.20

    )

    return round(
        final_score,
        2
    )


# =========================================================
# MATCH SINGLE JOB
# =========================================================

def match_job(
    student,
    job
):
    """
    Match one student against one job.
    """

    # =====================================================
    # ELIGIBILITY
    # =====================================================

    eligibility_result = check_eligibility(
        student,
        job
    )

    # =====================================================
    # MINIMUM SCORE
    # =====================================================

    score_result = check_minimum_score(
        student,
        job
    )

    # If score is available and below minimum,
    # treat the student as not eligible.

    if not score_result["passed"]:

        eligibility_result["eligible"] = False

        eligibility_result["reasons"].append(
            score_result["reason"]
        )

    # =====================================================
    # STUDENT SKILLS
    # =====================================================

    student_skills = get_student_skills(
        student
    )

    # =====================================================
    # REQUIRED SKILLS
    # =====================================================

    required_skills = job.get(
        "required_skills",
        []
    )

    if not isinstance(required_skills, list):

        required_skills = []

    skill_result = calculate_skill_match(
        student_skills,
        required_skills
    )

    # =====================================================
    # PREFERRED SKILLS
    # =====================================================

    preferred_skills = job.get(
        "preferred_skills",
        []
    )

    if not isinstance(preferred_skills, list):

        preferred_skills = []

    preferred_result = calculate_preferred_skill_match(
        student_skills,
        preferred_skills
    )

    # =====================================================
    # CAREER PREFERENCE
    # =====================================================

    preference_percentage = calculate_preference_match(
        student,
        job
    )

    # =====================================================
    # FINAL SCORE
    # =====================================================

    final_score = calculate_final_score(
        skill_result["percentage"],
        preferred_result["percentage"],
        preference_percentage
    )

    # =====================================================
    # COMBINED MISSING SKILLS
    # =====================================================

    missing_skills = list(
        dict.fromkeys(
            skill_result["missing_skills"]
            +
            preferred_result["missing_skills"]
        )
    )

    # =====================================================
    # LEARNING RECOMMENDATIONS
    # =====================================================

    learning_recommendations = [
        f"Learn {skill}"
        for skill in missing_skills
    ]

    # =====================================================
    # RETURN RESULT
    # =====================================================

    return {

        "job_id":
            str(job.get("_id", "")),

        "company_name":
            job.get("company_name"),

        "job_role":
            job.get("job_role"),

        "job_description":
            job.get("job_description", ""),

        "location":
            job.get("location"),

        "employment_type":
            job.get("employment_type"),

        "experience_required":
            job.get("experience_required"),

        "eligible":
            eligibility_result["eligible"],

        "eligibility_reasons":
            eligibility_result["reasons"],

        # =================================================
        # SKILL INFORMATION
        # =================================================

        "skill_match_percentage":
            skill_result["percentage"],

        "matched_skills":
            skill_result["matched_skills"],

        "missing_skills":
            missing_skills,

        "required_missing_skills":
            skill_result["missing_skills"],

        "preferred_matched_skills":
            preferred_result["matched_skills"],

        "preferred_missing_skills":
            preferred_result["missing_skills"],

        "preferred_skill_match_percentage":
            preferred_result["percentage"],

        # =================================================
        # PREFERENCE INFORMATION
        # =================================================

        "preference_match_percentage":
            preference_percentage,

        # =================================================
        # LLM SCORE
        # =================================================

        "student_llm_score":
            score_result["student_score"],

        "minimum_required_score":
            score_result["minimum_score"],

        # =================================================
        # FINAL MATCH
        # =================================================

        "final_score":
            final_score,

        # =================================================
        # JOB REQUIREMENTS
        # =================================================

        "required_skills":
            required_skills,

        "preferred_skills":
            preferred_skills,

        # =================================================
        # LEARNING
        # =================================================

        "learning_recommendations":
            learning_recommendations,

        # =================================================
        # APPLICATION
        # =================================================

        "application_url":
            job.get("application_url")
    }


# =========================================================
# RANK JOBS
# =========================================================

def rank_jobs(
    student,
    jobs
):
    """
    Match and rank all jobs.

    Only eligible jobs are returned.
    """

    matched_jobs = []

    for job in jobs:

        try:

            result = match_job(
                student,
                job
            )

            # ---------------------------------------------
            # ONLY RECOMMEND ELIGIBLE JOBS
            # ---------------------------------------------

            if result["eligible"]:

                matched_jobs.append(
                    result
                )

        except Exception:

            # Ignore malformed job records
            # instead of crashing the recommendation.
            continue

    # =====================================================
    # SORT
    # =====================================================

    matched_jobs.sort(
        key=lambda job: (
            job["final_score"],
            job["skill_match_percentage"],
            job["preferred_skill_match_percentage"]
        ),
        reverse=True
    )

    return matched_jobs


# =========================================================
# RECOMMEND JOBS
# =========================================================

def recommend_jobs(
    student,
    jobs,
    limit=10
):
    """
    Main function used by the API.

    Returns the top eligible job recommendations.
    """

    try:

        limit = int(limit)

    except (
        TypeError,
        ValueError
    ):

        limit = 10

    # Prevent unreasonable values
    limit = max(
        1,
        min(limit, 50)
    )

    ranked_jobs = rank_jobs(
        student,
        jobs
    )

    return ranked_jobs[:limit]