# =========================================================
# services/skill_extractor.py
# =========================================================

import re


# =========================================================
# SKILL DATABASE
# =========================================================

SKILL_DATABASE = {

    "Programming": [
        "C",
        "C++",
        "Java",
        "Python",
        "JavaScript",
        "TypeScript",
        "SQL",
        "CUDA",
        "R",
        "Go",
        "Rust",
        "PHP"
    ],

    "Frameworks": [
        "React",
        "Angular",
        "Node.js",
        "Django",
        "Flask",
        "Spring",
        "Spring Boot",
        "Express.js",
        "Next.js",
        "FastAPI"
    ],

    "Databases": [
        "MySQL",
        "PostgreSQL",
        "MongoDB",
        "Oracle",
        "SQLite",
        "Redis"
    ],

    "Cloud": [
        "AWS",
        "Azure",
        "Google Cloud",
        "GCP"
    ],

    "DevOps": [
        "Git",
        "GitHub",
        "Docker",
        "Kubernetes",
        "Jenkins",
        "CI/CD"
    ],

    "Operating Systems": [
        "Windows",
        "Linux",
        "macOS",
        "Ubuntu"
    ],

    "AI / ML": [
        "Machine Learning",
        "Deep Learning",
        "Artificial Intelligence",
        "TensorFlow",
        "PyTorch",
        "Scikit-learn",
        "Pandas",
        "NumPy",
        "OpenCV"
    ],

    "Tools": [
        "VS Code",
        "Visual Studio",
        "Android Studio",
        "Figma",
        "Postman"
    ],

    "Web": [
        "HTML",
        "CSS",
        "REST API",
        "REST APIs",
        "API"
    ]
}


# =========================================================
# NORMALIZE TEXT
# =========================================================

def normalize_text(text):

    if not text:
        return ""

    text = str(text)

    text = text.replace(
        "\n",
        " "
    )

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


# =========================================================
# FIND SKILLS IN TEXT
# =========================================================

def extract_skills_from_text(text):

    text = normalize_text(text)

    if not text:
        return []


    detected_skills = []


    for category, skills in SKILL_DATABASE.items():

        for skill in skills:

            # -------------------------------------------------
            # Escape special regex characters
            # -------------------------------------------------

            escaped_skill = re.escape(
                skill
            )

            # -------------------------------------------------
            # Word-boundary matching
            # -------------------------------------------------

            pattern = (
                r"(?<!\w)"
                + escaped_skill
                + r"(?!\w)"
            )

            if re.search(
                pattern,
                text,
                flags=re.IGNORECASE
            ):

                detected_skills.append({

                    "skill":
                        skill,

                    "category":
                        category

                })


    # =====================================================
    # REMOVE DUPLICATES
    # =====================================================

    unique_skills = {}

    for item in detected_skills:

        key = item["skill"].lower()

        if key not in unique_skills:

            unique_skills[key] = item


    return list(
        unique_skills.values()
    )


# =========================================================
# EXTRACT SKILLS FROM MULTIPLE DOCUMENTS
# =========================================================

def extract_skills_from_documents(
    resume_text="",
    certificate_texts=None
):

    if certificate_texts is None:

        certificate_texts = []


    # =====================================================
    # RESUME SKILLS
    # =====================================================

    resume_skills = (
        extract_skills_from_text(
            resume_text
        )
    )


    # =====================================================
    # CERTIFICATE SKILLS
    # =====================================================

    certificate_skills = []


    for certificate_text in certificate_texts:

        certificate_skills.extend(

            extract_skills_from_text(
                certificate_text
            )

        )


    # =====================================================
    # COMBINE
    # =====================================================

    all_skills = (
        resume_skills
        +
        certificate_skills
    )


    # =====================================================
    # REMOVE DUPLICATES
    # =====================================================

    unique_skills = {}

    for item in all_skills:

        key = item["skill"].lower()

        if key not in unique_skills:

            unique_skills[key] = item


    return list(
        unique_skills.values()
    )