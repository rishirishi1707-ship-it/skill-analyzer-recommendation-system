# ============================================================
# services/skill_extractor.py
# ============================================================

"""
Skill Extractor
---------------

Extracts technical and professional skills from:

- Resume text
- Certificate text
- Project descriptions
- Student-entered information

Features:

- Rule-based skill detection
- OCR-safe matching
- Resume skill extraction
- Certificate skill extraction
- Categorized skills
- Detailed skill information
- Duplicate removal

This service can later be combined with an LLM for:

- Skill-gap analysis
- Job matching
- Career recommendations
"""


import re


# ============================================================
# SKILL DATABASE
# ============================================================

SKILL_DATABASE = {

    # ========================================================
    # PROGRAMMING
    # ========================================================

    "Programming": [

        "C++",

        "Java",

        "Python",

        "JavaScript",

        "TypeScript",

        "SQL",

        "CUDA",

        "Go",

        "Rust",

        "PHP",

        "Kotlin",

        "Swift",

        "R",

        "C"

    ],


    # ========================================================
    # WEB DEVELOPMENT
    # ========================================================

    "Web Development": [

        "HTML",

        "CSS",

        "React",

        "Angular",

        "Vue",

        "Node.js",

        "Express.js",

        "Django",

        "Flask",

        "Spring Boot",

        "Spring",

        "REST API",

        "REST APIs"

    ],


    # ========================================================
    # DATABASES
    # ========================================================

    "Databases": [

        "MySQL",

        "PostgreSQL",

        "MongoDB",

        "Oracle",

        "SQLite",

        "Redis",

        "Firebase"

    ],


    # ========================================================
    # CLOUD
    # ========================================================

    "Cloud": [

        "AWS",

        "Amazon Web Services",

        "Azure",

        "Microsoft Azure",

        "Google Cloud",

        "GCP"

    ],


    # ========================================================
    # DATA SCIENCE
    # ========================================================

    "Data Science": [

        "Pandas",

        "NumPy",

        "Matplotlib",

        "Seaborn",

        "Scikit-learn",

        "Jupyter",

        "Jupyter Notebook"

    ],


    # ========================================================
    # ARTIFICIAL INTELLIGENCE
    # ========================================================

    "Artificial Intelligence": [

        "Artificial Intelligence",

        "Machine Learning",

        "Deep Learning",

        "Natural Language Processing",

        "NLP",

        "Computer Vision",

        "Generative AI",

        "LLM",

        "Large Language Models",

        "Transformers"

    ],


    # ========================================================
    # MACHINE LEARNING
    # ========================================================

    "Machine Learning": [

        "TensorFlow",

        "PyTorch",

        "Keras",

        "XGBoost",

        "LightGBM"

    ],


    # ========================================================
    # CYBERSECURITY
    # ========================================================

    "Cybersecurity": [

        "Cybersecurity",

        "Cyber Security",

        "Network Security",

        "Ethical Hacking",

        "Penetration Testing",

        "Cryptography",

        "OWASP"

    ],


    # ========================================================
    # DEVOPS
    # ========================================================

    "DevOps": [

        "Git",

        "GitHub",

        "GitLab",

        "Jenkins",

        "Docker",

        "Kubernetes",

        "CI/CD",

        "Continuous Integration",

        "Continuous Deployment"

    ],


    # ========================================================
    # OPERATING SYSTEMS
    # ========================================================

    "Operating Systems": [

        "Windows",

        "Linux",

        "Ubuntu",

        "Unix",

        "macOS"

    ],


    # ========================================================
    # NETWORKING
    # ========================================================

    "Networking": [

        "Computer Networks",

        "TCP/IP",

        "TCP",

        "UDP",

        "HTTP",

        "HTTPS",

        "DNS",

        "OSI",

        "Networking"

    ],


    # ========================================================
    # TOOLS
    # ========================================================

    "Tools": [

        "Git",

        "GitHub",

        "GitLab",

        "VS Code",

        "Visual Studio Code",

        "Figma",

        "Postman",

        "Jira",

        "Android Studio"

    ],


    # ========================================================
    # MOBILE DEVELOPMENT
    # ========================================================

    "Mobile Development": [

        "Android",

        "Android Development",

        "Flutter",

        "React Native",

        "Kotlin",

        "Swift"

    ],


    # ========================================================
    # GPU COMPUTING
    # ========================================================

    "GPU Computing": [

        "CUDA",

        "CUDA C",

        "CUDA Python",

        "GPU Computing",

        "GPU Programming",

        "OpenCL",

        "CuPy"

    ]

}


# ============================================================
# OCR NORMALIZATION
# ============================================================

def normalize_text(
    text
):

    """
    Normalize OCR/document text.
    """

    if not text:

        return ""


    text = str(
        text
    )


    # ========================================================
    # NORMALIZE LINE BREAKS
    # ========================================================

    text = text.replace(
        "\n",
        " "
    )

    text = text.replace(
        "\r",
        " "
    )

    text = text.replace(
        "\t",
        " "
    )


    # ========================================================
    # NORMALIZE DASHES
    # ========================================================

    text = text.replace(
        "‐",
        "-"
    )

    text = text.replace(
        "–",
        "-"
    )

    text = text.replace(
        "—",
        "-"
    )


    # ========================================================
    # REMOVE EXTRA SPACES
    # ========================================================

    text = re.sub(

        r"\s+",

        " ",

        text

    )


    return text.strip()


# ============================================================
# NORMALIZE SKILL NAME
# ============================================================

def normalize_skill_name(
    skill
):

    """
    Normalize skill name.
    """

    if not skill:

        return ""


    skill = str(
        skill
    ).strip()


    skill = re.sub(

        r"\s+",

        " ",

        skill

    )


    return skill


# ============================================================
# SKILL MATCHING
# ============================================================

def skill_exists(
    text,
    skill
):

    """
    Check whether a skill exists
    using safe word boundaries.
    """

    if not text or not skill:

        return False


    normalized_text = normalize_text(
        text
    ).lower()


    normalized_skill = normalize_skill_name(
        skill
    ).lower()


    escaped_skill = re.escape(
        normalized_skill
    )


    # ========================================================
    # SAFE WORD BOUNDARIES
    #
    # Prevent:
    #
    # R -> matching random letters
    # C -> matching every C
    # Go -> matching Goal
    # ========================================================

    pattern = (

        rf"(?<!\w)"

        rf"{escaped_skill}"

        rf"(?!\w)"

    )


    return (

        re.search(

            pattern,

            normalized_text,

            flags=re.IGNORECASE

        )

        is not None

    )


# ============================================================
# OCR SAFE SKILL MATCHING
# ============================================================

def skill_exists_ocr_safe(
    text,
    skill
):

    """
    Safely check whether a skill
    exists in OCR/document text.
    """

    if not text or not skill:

        return False


    normalized_text = normalize_text(
        text
    )


    normalized_skill = normalize_skill_name(
        skill
    )


    return skill_exists(

        normalized_text,

        normalized_skill

    )


# ============================================================
# EXTRACT SKILLS BY CATEGORY
# ============================================================

def extract_skills_by_category(
    text
):

    """
    Extract skills organized by category.
    """

    text = normalize_text(
        text
    )


    result = {}


    if not text:

        return result


    for category, skills in (
        SKILL_DATABASE.items()
    ):

        detected = []


        for skill in skills:

            if skill_exists_ocr_safe(

                text,

                skill

            ):

                if skill not in detected:

                    detected.append(
                        skill
                    )


        if detected:

            result[
                category
            ] = detected


    return result


# ============================================================
# EXTRACT ALL SKILLS
# ============================================================

def extract_skills(
    text
):

    """
    Extract all unique skills.
    """

    categorized = (
        extract_skills_by_category(
            text
        )
    )


    skills = []


    for category_skills in (
        categorized.values()
    ):

        for skill in category_skills:

            if skill not in skills:

                skills.append(
                    skill
                )


    return skills


# ============================================================
# EXTRACT SKILL DETAILS
# ============================================================

def extract_skill_details(
    text,
    source="document"
):

    """
    Extract detailed skill information.
    """

    categorized = (
        extract_skills_by_category(
            text
        )
    )


    results = []


    for category, skills in (
        categorized.items()
    ):

        for skill in skills:

            results.append({

                "name":
                    skill,

                "category":
                    category,

                "proficiency":
                    "Detected",

                "source":
                    source

            })


    return results


# ============================================================
# MERGE SKILLS
# ============================================================

def merge_skills(

    manual_skills=None,

    extracted_skills=None

):

    """
    Merge manually entered skills
    with automatically extracted skills.
    """


    manual_skills = (

        manual_skills

        if isinstance(
            manual_skills,
            list
        )

        else []

    )


    extracted_skills = (

        extracted_skills

        if isinstance(
            extracted_skills,
            list
        )

        else []

    )


    merged = []

    existing_names = set()


    # ========================================================
    # MANUAL SKILLS
    # ========================================================

    for skill in manual_skills:

        if isinstance(
            skill,
            str
        ):

            skill_data = {

                "name":
                    skill,

                "category":
                    "Other",

                "proficiency":
                    "Not specified",

                "source":
                    "manual"

            }


        elif isinstance(
            skill,
            dict
        ):

            skill_data = {

                "name":
                    skill.get(
                        "name",
                        ""
                    ),

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

            }


        else:

            continue


        skill_name = normalize_skill_name(

            skill_data.get(
                "name"
            )

        )


        if not skill_name:

            continue


        skill_key = skill_name.lower()


        if skill_key in existing_names:

            continue


        skill_data[
            "name"
        ] = skill_name


        merged.append(
            skill_data
        )


        existing_names.add(
            skill_key
        )


    # ========================================================
    # EXTRACTED SKILLS
    # ========================================================

    for skill in extracted_skills:

        if isinstance(
            skill,
            str
        ):

            skill_data = {

                "name":
                    skill,

                "category":
                    "Other",

                "proficiency":
                    "Detected",

                "source":
                    "document"

            }


        elif isinstance(
            skill,
            dict
        ):

            skill_data = {

                "name":
                    skill.get(
                        "name",
                        ""
                    ),

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

            }


        else:

            continue


        skill_name = normalize_skill_name(

            skill_data.get(
                "name"
            )

        )


        if not skill_name:

            continue


        skill_key = skill_name.lower()


        if skill_key in existing_names:

            continue


        skill_data[
            "name"
        ] = skill_name


        merged.append(
            skill_data
        )


        existing_names.add(
            skill_key
        )


    return merged


# ============================================================
# MERGE CATEGORIES
# ============================================================

def merge_categories(
    category_sources
):

    """
    Merge categorized skill dictionaries.
    """

    merged = {}


    for categories in category_sources:

        if not isinstance(
            categories,
            dict
        ):

            continue


        for category, skills in (
            categories.items()
        ):

            if category not in merged:

                merged[
                    category
                ] = []


            if not isinstance(
                skills,
                list
            ):

                continue


            for skill in skills:

                if skill not in merged[
                    category
                ]:

                    merged[
                        category
                    ].append(
                        skill
                    )


    return merged


# ============================================================
# EXTRACT SKILLS FROM MULTIPLE DOCUMENTS
# ============================================================

def extract_skills_from_documents(

    resume_text="",

    certificate_texts=None

):

    """
    Extract skills separately from:

    - Resume
    - Certificates

    Then combine all skills.

    Returns:

    {
        "skills": [],
        "resume_skills": [],
        "certificate_skills": [],
        "categorized_skills": {},
        "skill_details": [],
        "document_count": 0
    }
    """


    # ========================================================
    # VALIDATE CERTIFICATE TEXTS
    # ========================================================

    certificate_texts = (

        certificate_texts

        if isinstance(
            certificate_texts,
            list
        )

        else []

    )


    # ========================================================
    # RESUME
    # ========================================================

    normalized_resume = normalize_text(
        resume_text
    )


    resume_skills = []

    resume_categories = {}

    resume_details = []


    if normalized_resume:

        resume_skills = extract_skills(
            normalized_resume
        )


        resume_categories = (
            extract_skills_by_category(
                normalized_resume
            )
        )


        resume_details = (
            extract_skill_details(

                normalized_resume,

                source="resume"

            )
        )


    # ========================================================
    # CERTIFICATES
    # ========================================================

    normalized_certificates = []


    for certificate_text in certificate_texts:

        normalized_certificate = normalize_text(
            certificate_text
        )


        if normalized_certificate:

            normalized_certificates.append(
                normalized_certificate
            )


    combined_certificate_text = " ".join(
        normalized_certificates
    )


    certificate_skills = []

    certificate_categories = {}

    certificate_details = []


    if combined_certificate_text:

        certificate_skills = extract_skills(
            combined_certificate_text
        )


        certificate_categories = (
            extract_skills_by_category(
                combined_certificate_text
            )
        )


        certificate_details = (
            extract_skill_details(

                combined_certificate_text,

                source="certificate"

            )
        )


    # ========================================================
    # COMBINE ALL SKILLS
    # ========================================================

    all_skills = []


    for skill in (

        resume_skills

        +

        certificate_skills

    ):

        if skill not in all_skills:

            all_skills.append(
                skill
            )


    # ========================================================
    # COMBINE CATEGORIES
    # ========================================================

    categorized_skills = merge_categories(

        [

            resume_categories,

            certificate_categories

        ]

    )


    # ========================================================
    # COMBINE SKILL DETAILS
    # ========================================================

    skill_details = []

    existing_skills = set()


    for detail in (

        resume_details

        +

        certificate_details

    ):

        if not isinstance(
            detail,
            dict
        ):

            continue


        skill_name = normalize_skill_name(

            detail.get(
                "name",
                ""
            )

        )


        if not skill_name:

            continue


        skill_key = skill_name.lower()


        if skill_key in existing_skills:

            continue


        detail[
            "name"
        ] = skill_name


        skill_details.append(
            detail
        )


        existing_skills.add(
            skill_key
        )


    # ========================================================
    # DOCUMENT COUNT
    # ========================================================

    document_count = 0


    if normalized_resume:

        document_count += 1


    document_count += len(
        normalized_certificates
    )


    # ========================================================
    # FINAL RESULT
    # ========================================================

    return {

        "skills":
            all_skills,

        "resume_skills":
            resume_skills,

        "certificate_skills":
            certificate_skills,

        "categorized_skills":
            categorized_skills,

        "skill_details":
            skill_details,

        "document_count":
            document_count

    }


# ============================================================
# CREATE SKILL SUMMARY
# ============================================================

def create_skill_summary(
    skills
):

    """
    Create skill summary grouped by category.
    """

    if not isinstance(
        skills,
        list
    ):

        return {

            "total_skills":
                0,

            "categories":
                {}

        }


    categories = {}

    unique_skills = set()


    for skill in skills:

        if not isinstance(
            skill,
            dict
        ):

            continue


        category = skill.get(
            "category",
            "Other"
        )


        name = normalize_skill_name(

            skill.get(
                "name",
                ""
            )

        )


        if not name:

            continue


        skill_key = name.lower()


        if skill_key in unique_skills:

            continue


        unique_skills.add(
            skill_key
        )


        categories.setdefault(

            category,

            []

        )


        if name not in categories[
            category
        ]:

            categories[
                category
            ].append(
                name
            )


    return {

        "total_skills":
            len(
                unique_skills
            ),

        "categories":
            categories

    }


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    resume_sample = """

    RISHI

    Computer Science Engineering Student

    Skills:

    Python
    Java
    C++
    SQL
    MongoDB
    Flask
    React
    Git
    GitHub
    Docker
    AWS

    Projects:

    Developed a web application using
    Python, Flask, React and MongoDB.

    Machine learning project using
    Python, NumPy, Pandas and Scikit-learn.

    """


    certificate_samples = [

        """

        Python Programming Certificate

        Successfully completed training in:

        Python
        NumPy
        Pandas
        Machine Learning

        """

    ]


    print(
        "\n================================"
    )

    print(
        "RESUME SKILLS"
    )

    print(
        "================================"
    )


    print(

        extract_skills(
            resume_sample
        )

    )


    print(
        "\n================================"
    )

    print(
        "COMPLETE DOCUMENT EXTRACTION"
    )

    print(
        "================================"
    )


    result = extract_skills_from_documents(

        resume_text=
            resume_sample,

        certificate_texts=
            certificate_samples

    )


    print(

        result

    )


    print(
        "\n================================"
    )

    print(
        "RESUME SKILLS"
    )

    print(
        "================================"
    )


    print(

        result.get(
            "resume_skills"
        )

    )


    print(
        "\n================================"
    )

    print(
        "CERTIFICATE SKILLS"
    )

    print(
        "================================"
    )


    print(

        result.get(
            "certificate_skills"
        )

    )


    print(
        "\n================================"
    )

    print(
        "ALL SKILLS"
    )

    print(
        "================================"
    )


    print(

        result.get(
            "skills"
        )

    )


    print(
        "\n================================"
    )

    print(
        "CATEGORIZED SKILLS"
    )

    print(
        "================================"
    )


    print(

        result.get(
            "categorized_skills"
        )

    )


    print(
        "\n================================"
    )

    print(
        "DOCUMENT COUNT"
    )

    print(
        "================================"
    )


    print(

        result.get(
            "document_count"
        )

    )