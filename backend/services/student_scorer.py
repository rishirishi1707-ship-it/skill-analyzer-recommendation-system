# =========================================================
# services/student_scorer.py
# =========================================================

"""
Student scoring engine.

Calculates a deterministic student score from 0.0 to 10.0.

Score components:

1. Skills / proficiency        -> 4.0
2. CGPA                        -> 2.0
3. Certifications              -> 1.5
4. Projects                    -> 1.5
5. Resume/document evidence    -> 1.0

The LLM does NOT calculate the numerical score.

The LLM analyzes the student's profile.
This service calculates the score deterministically.
"""


# =========================================================
# PROFICIENCY VALUES
# =========================================================

PROFICIENCY_SCORES = {

    "beginner": 0.25,

    "basic": 0.25,

    "intermediate": 0.50,

    "advanced": 0.75,

    "expert": 1.00,

    # Automatically detected skills
    "detected": 0.50,

    "not specified": 0.50

}


# =========================================================
# NORMALIZE TEXT
# =========================================================

def normalize_text(value):

    if value is None:

        return ""

    return str(
        value
    ).strip().lower()


# =========================================================
# NORMALIZE SKILL NAME
# =========================================================

def normalize_skill_name(value):

    return normalize_text(
        value
    )


# =========================================================
# GET DETECTED SKILLS
# =========================================================

def get_detected_skills(student):

    """
    Retrieve automatically detected skills.

    Expected MongoDB location:

        student
            └── llm_analysis
                    └── detected_skills

    Expected format:

    {
        "skills": [],
        "categorized_skills": {},
        "skill_details": [],
        "document_count": 0
    }
    """

    if not isinstance(
        student,
        dict
    ):

        return {

            "skills": [],

            "categorized_skills": {},

            "skill_details": [],

            "document_count": 0

        }


    llm_analysis = student.get(
        "llm_analysis",
        {}
    )


    if not isinstance(
        llm_analysis,
        dict
    ):

        return {

            "skills": [],

            "categorized_skills": {},

            "skill_details": [],

            "document_count": 0

        }


    detected_skills = llm_analysis.get(
        "detected_skills",
        {}
    )


    if not isinstance(
        detected_skills,
        dict
    ):

        return {

            "skills": [],

            "categorized_skills": {},

            "skill_details": [],

            "document_count": 0

        }


    return detected_skills


# =========================================================
# CONVERT DETECTED SKILLS TO SKILL LIST
# =========================================================

def convert_detected_skills(
    detected_skills
):

    """
    Convert detected skill data into standard skill objects.

    Example output:

    [
        {
            "name": "Python",
            "category": "Programming",
            "proficiency": "Detected",
            "source": "document"
        }
    ]
    """

    if not isinstance(
        detected_skills,
        dict
    ):

        return []


    skill_details = detected_skills.get(
        "skill_details",
        []
    )


    result = []


    # =====================================================
    # USE SKILL DETAILS
    # =====================================================

    if isinstance(
        skill_details,
        list
    ):

        for skill in skill_details:

            if isinstance(
                skill,
                dict
            ):

                name = skill.get(
                    "name",
                    ""
                )


                if not name:

                    continue


                result.append({

                    "name":
                        name,

                    "category":
                        skill.get(
                            "category",
                            "Other"
                        ),

                    "proficiency":
                        skill.get(
                            "proficiency",
                            "Detected"
                        ),

                    "source":
                        "document"

                })


    # =====================================================
    # FALLBACK TO SIMPLE SKILL LIST
    # =====================================================

    if not result:

        skills = detected_skills.get(
            "skills",
            []
        )


        if isinstance(
            skills,
            list
        ):

            for skill in skills:

                if not skill:

                    continue


                if isinstance(
                    skill,
                    dict
                ):

                    name = skill.get(
                        "name",
                        ""
                    )


                    if not name:

                        continue


                    result.append({

                        "name":
                            name,

                        "category":
                            skill.get(
                                "category",
                                "Other"
                            ),

                        "proficiency":
                            skill.get(
                                "proficiency",
                                "Detected"
                            ),

                        "source":
                            "document"

                    })


                elif isinstance(
                    skill,
                    str
                ):

                    result.append({

                        "name":
                            skill,

                        "category":
                            "Other",

                        "proficiency":
                            "Detected",

                        "source":
                            "document"

                    })


    return result


# =========================================================
# MERGE MANUAL + DETECTED SKILLS
# =========================================================

def get_all_skills(student):

    """
    Combine manual skills and automatically detected skills.

    Duplicate skills are removed.

    Manual skills have priority because the student
    explicitly entered their proficiency.
    """

    if not isinstance(
        student,
        dict
    ):

        return []


    manual_skills = student.get(
        "skills",
        []
    )


    if not isinstance(
        manual_skills,
        list
    ):

        manual_skills = []


    detected_skills_data = get_detected_skills(
        student
    )


    detected_skills = convert_detected_skills(
        detected_skills_data
    )


    merged_skills = []


    existing_skills = set()


    # =====================================================
    # MANUAL SKILLS FIRST
    # =====================================================

    for skill in manual_skills:

        if isinstance(
            skill,
            dict
        ):

            name = skill.get(
                "name",
                ""
            )


            if not name:

                continue


            skill_key = normalize_skill_name(
                name
            )


            if skill_key in existing_skills:

                continue


            merged_skills.append({

                "name":
                    name,

                "category":
                    skill.get(
                        "category",
                        "Other"
                    ),

                "proficiency":
                    skill.get(
                        "proficiency",
                        "Not specified"
                    ),

                "source":
                    "manual"

            })


            existing_skills.add(
                skill_key
            )


        elif isinstance(
            skill,
            str
        ):

            skill_key = normalize_skill_name(
                skill
            )


            if not skill_key:

                continue


            if skill_key in existing_skills:

                continue


            merged_skills.append({

                "name":
                    skill,

                "category":
                    "Other",

                "proficiency":
                    "Not specified",

                "source":
                    "manual"

            })


            existing_skills.add(
                skill_key
            )


    # =====================================================
    # DETECTED SKILLS
    # =====================================================

    for skill in detected_skills:

        name = skill.get(
            "name",
            ""
        )


        if not name:

            continue


        skill_key = normalize_skill_name(
            name
        )


        if skill_key in existing_skills:

            continue


        merged_skills.append(
            skill
        )


        existing_skills.add(
            skill_key
        )


    return merged_skills


# =========================================================
# SKILL SCORE
# =========================================================

def calculate_skill_score(
    skills
):

    """
    Calculate skill contribution.

    Maximum contribution = 4.0
    """

    if not isinstance(
        skills,
        list
    ):

        return 0.0


    if not skills:

        return 0.0


    total = 0.0

    valid_skills = 0


    for skill in skills:

        # =================================================
        # SKILL AS DICTIONARY
        # =================================================

        if isinstance(
            skill,
            dict
        ):

            name = skill.get(
                "name",
                ""
            )


            if not name:

                continue


            proficiency = normalize_text(

                skill.get(
                    "proficiency",
                    "Not specified"
                )

            )


            score = PROFICIENCY_SCORES.get(

                proficiency,

                0.50

            )


        # =================================================
        # SKILL AS STRING
        # =================================================

        elif isinstance(
            skill,
            str
        ):

            if not skill.strip():

                continue


            score = 0.50


        else:

            continue


        total += score

        valid_skills += 1


    if valid_skills == 0:

        return 0.0


    average = (

        total
        /
        valid_skills

    )


    score = (

        average
        *
        4.0

    )


    return round(
        score,
        2
    )


# =========================================================
# CGPA SCORE
# =========================================================

def calculate_cgpa_score(
    cgpa
):

    try:

        cgpa = float(
            cgpa
        )


    except (

        TypeError,
        ValueError

    ):

        return 0.0


    cgpa = max(

        0.0,

        min(

            cgpa,
            10.0

        )

    )


    score = (

        cgpa
        /
        10.0

    ) * 2.0


    return round(
        score,
        2
    )


# =========================================================
# GET ALL CERTIFICATIONS
# =========================================================

def get_all_certifications(
    student
):

    """
    Combine:

    - manually entered certifications
    - uploaded certificates

    Duplicate entries are removed where possible.
    """

    if not isinstance(
        student,
        dict
    ):

        return []


    certifications = student.get(
        "certifications",
        []
    )


    uploaded_certificates = student.get(
        "uploaded_certificates",
        []
    )


    if not isinstance(
        certifications,
        list
    ):

        certifications = []


    if not isinstance(
        uploaded_certificates,
        list
    ):

        uploaded_certificates = []


    result = []

    seen = set()


    # =====================================================
    # MANUAL CERTIFICATIONS
    # =====================================================

    for certification in certifications:

        identifier = str(
            certification
        ).lower()


        if isinstance(
            certification,
            dict
        ):

            identifier = normalize_text(

                certification.get(
                    "name"
                )

                or

                certification.get(
                    "title"
                )

                or

                certification.get(
                    "certificate_name"
                )

                or

                certification.get(
                    "original_name"
                )

            )


        if identifier and identifier in seen:

            continue


        if identifier:

            seen.add(
                identifier
            )


        result.append(
            certification
        )


    # =====================================================
    # UPLOADED CERTIFICATES
    # =====================================================

    for certificate in uploaded_certificates:

        identifier = str(
            certificate
        ).lower()


        if isinstance(
            certificate,
            dict
        ):

            identifier = normalize_text(

                certificate.get(
                    "name"
                )

                or

                certificate.get(
                    "title"
                )

                or

                certificate.get(
                    "certificate_name"
                )

                or

                certificate.get(
                    "original_name"
                )

            )


        if identifier and identifier in seen:

            continue


        if identifier:

            seen.add(
                identifier
            )


        result.append(
            certificate
        )


    return result


# =========================================================
# CERTIFICATION SCORE
# =========================================================

def calculate_certification_score(
    certifications
):

    """
    Maximum contribution = 1.5
    """

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

    """
    Maximum contribution = 1.5
    """

    if not isinstance(
        projects,
        list
    ):

        return 0.0


    valid_projects = []


    for project in projects:

        if isinstance(
            project,
            dict
        ):

            title = (

                project.get(
                    "title"
                )

                or

                project.get(
                    "name"
                )

            )


            description = project.get(
                "description"
            )


            if title or description:

                valid_projects.append(
                    project
                )


        elif isinstance(
            project,
            str
        ):

            if project.strip():

                valid_projects.append(
                    project
                )


    count = len(
        valid_projects
    )


    if count == 0:

        return 0.0


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
# CHECK RESUME EXISTS
# =========================================================

def has_resume(
    resume
):

    """
    Check whether the student has uploaded
    a resume.
    """

    if not isinstance(
        resume,
        dict
    ):

        return False


    possible_fields = [

        "has_resume",

        "file",

        "resume_name",

        "original_name",

        "stored_filename",

        "filename"

    ]


    for field in possible_fields:

        if resume.get(
            field
        ):

            return True


    return False


# =========================================================
# DOCUMENT EVIDENCE SCORE
# =========================================================

def calculate_document_score(
    student
):

    """
    Calculate document evidence.

    Maximum contribution = 1.0

    Resume:
        0.7

    Certificate evidence:
        0.3
    """

    if not isinstance(
        student,
        dict
    ):

        return 0.0


    score = 0.0


    # =====================================================
    # RESUME
    # =====================================================

    resume = student.get(
        "resume",
        {}
    )


    if has_resume(
        resume
    ):

        score += 0.7


    # =====================================================
    # UPLOADED CERTIFICATES
    # =====================================================

    uploaded_certificates = student.get(
        "uploaded_certificates",
        []
    )


    if not isinstance(
        uploaded_certificates,
        list
    ):

        uploaded_certificates = []


    # =====================================================
    # MANUAL CERTIFICATIONS WITH FILES
    # =====================================================

    certifications = student.get(
        "certifications",
        []
    )


    if not isinstance(
        certifications,
        list
    ):

        certifications = []


    certificate_document_found = False


    # -----------------------------------------------------
    # Uploaded certificate exists
    # -----------------------------------------------------

    if uploaded_certificates:

        certificate_document_found = True


    # -----------------------------------------------------
    # Certification contains file
    # -----------------------------------------------------

    if not certificate_document_found:

        for certification in certifications:

            if not isinstance(
                certification,
                dict
            ):

                continue


            if (

                certification.get(
                    "file"
                )

                or

                certification.get(
                    "original_name"
                )

                or

                certification.get(
                    "stored_filename"
                )

            ):

                certificate_document_found = True

                break


    if certificate_document_found:

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

    """
    Calculate complete deterministic student score.

    Returns:

    {
        "score": 0.0,
        "scale": "0-10",
        "components": {}
    }
    """

    if not isinstance(
        student,
        dict
    ):

        return {

            "score": 0.0,

            "scale": "0-10",

            "components": {},

            "message":
                "Invalid student data"

        }


    # =====================================================
    # GET ACADEMIC DATA
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


    # =====================================================
    # GET ALL SKILLS
    # =====================================================

    all_skills = get_all_skills(
        student
    )


    # =====================================================
    # GET ALL CERTIFICATIONS
    # =====================================================

    all_certifications = (
        get_all_certifications(
            student
        )
    )


    # =====================================================
    # GET PROJECTS
    # =====================================================

    projects = student.get(
        "projects",
        []
    )


    # =====================================================
    # CALCULATE SKILL SCORE
    # =====================================================

    skill_score = calculate_skill_score(
        all_skills
    )


    # =====================================================
    # CALCULATE CGPA SCORE
    # =====================================================

    cgpa_score = calculate_cgpa_score(

        academic.get(
            "current_cgpa"
        )

    )


    # =====================================================
    # CALCULATE CERTIFICATION SCORE
    # =====================================================

    certification_score = (
        calculate_certification_score(
            all_certifications
        )
    )


    # =====================================================
    # CALCULATE PROJECT SCORE
    # =====================================================

    project_score = calculate_project_score(
        projects
    )


    # =====================================================
    # CALCULATE DOCUMENT SCORE
    # =====================================================

    document_score = calculate_document_score(
        student
    )


    # =====================================================
    # TOTAL SCORE
    # =====================================================

    total_score = (

        skill_score

        + cgpa_score

        + certification_score

        + project_score

        + document_score

    )


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
    # RETURN RESULT
    # =====================================================

    return {

        "score":
            total_score,

        "scale":
            "0-10",

        "components": {

            "skills": {

                "score":
                    skill_score,

                "maximum":
                    4.0,

                "skill_count":
                    len(
                        all_skills
                    )

            },


            "cgpa": {

                "score":
                    cgpa_score,

                "maximum":
                    2.0

            },


            "certifications": {

                "score":
                    certification_score,

                "maximum":
                    1.5,

                "count":
                    len(
                        all_certifications
                    )

            },


            "projects": {

                "score":
                    project_score,

                "maximum":
                    1.5,

                "count":
                    len(
                        projects
                    )

                    if isinstance(
                        projects,
                        list
                    )

                    else 0

            },


            "document_evidence": {

                "score":
                    document_score,

                "maximum":
                    1.0

            }

        }

    }


# =========================================================
# SCORE LABEL
# =========================================================

def get_score_label(
    score
):

    """
    Convert numerical score into a label.
    """

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


# =========================================================
# LOCAL TEST
# =========================================================

if __name__ == "__main__":

    test_student = {

        "academic": {

            "current_cgpa":
                8.5

        },


        "skills": [

            {

                "name":
                    "Python",

                "proficiency":
                    "Advanced"

            },

            {

                "name":
                    "Java",

                "proficiency":
                    "Intermediate"

            }

        ],


        "llm_analysis": {

            "detected_skills": {

                "skills": [

                    "Python",

                    "MongoDB",

                    "Flask"

                ],

                "skill_details": [

                    {

                        "name":
                            "Python",

                        "category":
                            "Programming",

                        "proficiency":
                            "Detected"

                    },

                    {

                        "name":
                            "MongoDB",

                        "category":
                            "Databases",

                        "proficiency":
                            "Detected"

                    },

                    {

                        "name":
                            "Flask",

                        "category":
                            "Web Development",

                        "proficiency":
                            "Detected"

                    }

                ],

                "document_count":
                    2

            }

        },


        "certifications": [

            {

                "name":
                    "Python Certificate"

            }

        ],


        "uploaded_certificates": [

            {

                "original_name":
                    "mongodb_certificate.pdf"

            }

        ],


        "projects": [

            {

                "title":
                    "Student Management System"

            },

            {

                "title":
                    "Portfolio Website"

            }

        ],


        "resume": {

            "has_resume":
                True

        }

    }


    result = calculate_student_score(
        test_student
    )


    print(
        "\n========================================"
    )

    print(
        "STUDENT SCORE"
    )

    print(
        "========================================"
    )

    print(
        result
    )

    print(
        "Score Label:",
        get_score_label(
            result.get(
                "score"
            )
        )
    )

    print(
        "========================================\n"
    )