"""
Skill Extractor
---------------
Extracts technical and professional skills from:

- Resume text
- Certificate text
- Project descriptions
- Student-entered information

Uses a rule-based approach that can later be connected
to an LLM for deeper skill-gap analysis and recommendations.
"""

import re


# ============================================================
# SKILL DATABASE
# ============================================================

SKILL_DATABASE = {

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
        "C",
    ],

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
        "REST APIs",
    ],

    "Databases": [
        "MySQL",
        "PostgreSQL",
        "MongoDB",
        "Oracle",
        "SQLite",
        "Redis",
        "Firebase",
    ],

    "Cloud": [
        "AWS",
        "Amazon Web Services",
        "Azure",
        "Microsoft Azure",
        "Google Cloud",
        "GCP",
    ],

    "Data Science": [
        "Pandas",
        "NumPy",
        "Matplotlib",
        "Seaborn",
        "Scikit-learn",
        "scikit-learn",
        "Jupyter",
        "Jupyter Notebook",
    ],

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
        "Transformers",
    ],

    "Machine Learning": [
        "TensorFlow",
        "PyTorch",
        "Keras",
        "XGBoost",
        "LightGBM",
        "Machine Learning",
        "Deep Learning",
    ],

    "Cybersecurity": [
        "Cybersecurity",
        "Cyber Security",
        "Network Security",
        "Ethical Hacking",
        "Penetration Testing",
        "Cryptography",
        "OWASP",
    ],

    "DevOps": [
        "Git",
        "GitHub",
        "GitLab",
        "Jenkins",
        "Docker",
        "Kubernetes",
        "CI/CD",
        "Continuous Integration",
        "Continuous Deployment",
    ],

    "Operating Systems": [
        "Windows",
        "Linux",
        "Ubuntu",
        "Unix",
        "macOS",
    ],

    "Networking": [
        "Computer Networks",
        "TCP/IP",
        "TCP",
        "UDP",
        "HTTP",
        "HTTPS",
        "DNS",
        "OSI",
        "Networking",
    ],

    "Tools": [
        "Git",
        "GitHub",
        "GitLab",
        "VS Code",
        "Visual Studio Code",
        "Figma",
        "Postman",
        "Jira",
        "Android Studio",
    ],

    "Mobile Development": [
        "Android",
        "Android Development",
        "Flutter",
        "React Native",
        "Kotlin",
        "Swift",
    ],

    "GPU Computing": [
        "CUDA",
        "CUDA C",
        "CUDA Python",
        "GPU Computing",
        "GPU Programming",
        "OpenCL",
        "CuPy",
    ],

}


# ============================================================
# OCR NORMALIZATION
# ============================================================

def normalize_text(text):
    """
    Normalize OCR/document text.

    Handles:
    - New lines
    - Tabs
    - Multiple spaces
    - Common OCR formatting issues
    """

    if not text:
        return ""

    text = str(text)

    # Normalize line breaks
    text = text.replace("\n", " ")
    text = text.replace("\r", " ")
    text = text.replace("\t", " ")

    # Common OCR substitutions
    text = text.replace("‐", "-")
    text = text.replace("-", "-")
    text = text.replace("–", "-")
    text = text.replace("—", "-")

    # Multiple spaces
    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


# ============================================================
# NORMALIZE SKILL NAME
# ============================================================

def normalize_skill_name(skill):
    """
    Normalize skill name for comparison.
    """

    if not skill:
        return ""

    skill = str(skill).strip()

    skill = re.sub(
        r"\s+",
        " ",
        skill
    )

    return skill


# ============================================================
# SKILL MATCHING
# ============================================================

def skill_exists(text, skill):
    """
    Check whether a skill exists in the text.

    Uses case-insensitive matching and word boundaries.
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

    pattern = (
        rf"(?<!\w)"
        rf"{escaped_skill}"
        rf"(?!\w)"
    )

    return re.search(
        pattern,
        normalized_text,
        flags=re.IGNORECASE
    ) is not None


# ============================================================
# SPECIAL OCR SKILL MATCHING
# ============================================================

def skill_exists_ocr_safe(text, skill):
    """
    OCR-safe skill matching.

    This is especially useful for:
        C++
        C
        C++
        Node.js
        Express.js
        CI/CD
        C#
    """

    if not text or not skill:
        return False

    normalized_text = normalize_text(
        text
    ).lower()

    normalized_skill = normalize_skill_name(
        skill
    ).lower()

    # Direct search first
    if normalized_skill in normalized_text:
        return True

    # Regex search
    return skill_exists(
        normalized_text,
        normalized_skill
    )


# ============================================================
# EXTRACT SKILLS BY CATEGORY
# ============================================================

def extract_skills_by_category(text):
    """
    Extract skills and organize them by category.

    Example:

    {
        "Programming": [
            "Python",
            "Java"
        ],
        "Databases": [
            "MongoDB"
        ]
    }
    """

    text = normalize_text(
        text
    )

    result = {}

    if not text:
        return result

    for category, skills in SKILL_DATABASE.items():

        detected = []

        for skill in skills:

            if skill_exists_ocr_safe(
                text,
                skill
            ):

                # Prevent duplicate skill names
                if skill not in detected:

                    detected.append(
                        skill
                    )

        if detected:

            result[category] = detected

    return result


# ============================================================
# EXTRACT ALL SKILLS
# ============================================================

def extract_skills(text):
    """
    Return all detected skills as a list.
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
# EXTRACT SKILLS WITH DETAILS
# ============================================================

def extract_skill_details(text):
    """
    Return detailed skill information.
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
                    "document"

            })

    return results


# ============================================================
# MERGE MANUAL + EXTRACTED SKILLS
# ============================================================

def merge_skills(
    manual_skills=None,
    extracted_skills=None
):
    """
    Merge manually entered skills with
    automatically extracted skills.
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

    # --------------------------------------------------------
    # MANUAL SKILLS
    # --------------------------------------------------------

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

        if not skill_data["name"]:

            continue

        merged.append(
            skill_data
        )

    # --------------------------------------------------------
    # EXTRACTED SKILLS
    # --------------------------------------------------------

    existing_names = {

        item["name"].lower()

        for item in merged

        if item.get("name")
    }

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

        if not skill_data["name"]:

            continue

        skill_key = (
            skill_data["name"]
            .lower()
        )

        if skill_key not in existing_names:

            merged.append(
                skill_data
            )

            existing_names.add(
                skill_key
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
    Extract skills from resume and certificates.

    Returns:

    {
        "skills": [],
        "categorized_skills": {},
        "skill_details": [],
        "document_count": 0
    }
    """

    certificate_texts = (
        certificate_texts
        if isinstance(
            certificate_texts,
            list
        )
        else []
    )

    documents = []

    # --------------------------------------------------------
    # RESUME
    # --------------------------------------------------------

    if resume_text:

        normalized_resume = (
            normalize_text(
                resume_text
            )
        )

        if normalized_resume:

            documents.append(
                normalized_resume
            )

    # --------------------------------------------------------
    # CERTIFICATES
    # --------------------------------------------------------

    for certificate_text in (
        certificate_texts
    ):

        if not certificate_text:

            continue

        normalized_certificate = (
            normalize_text(
                certificate_text
            )
        )

        if normalized_certificate:

            documents.append(
                normalized_certificate
            )

    # --------------------------------------------------------
    # COMBINE DOCUMENTS
    # --------------------------------------------------------

    combined_text = " ".join(
        documents
    )

    # --------------------------------------------------------
    # EXTRACT
    # --------------------------------------------------------

    skills = extract_skills(
        combined_text
    )

    categorized_skills = (
        extract_skills_by_category(
            combined_text
        )
    )

    skill_details = (
        extract_skill_details(
            combined_text
        )
    )

    # --------------------------------------------------------
    # RESULT
    # --------------------------------------------------------

    result = {

        "skills":
            skills,

        "categorized_skills":
            categorized_skills,

        "skill_details":
            skill_details,

        "document_count":
            len(documents)
    }

    return result


# ============================================================
# SKILL SUMMARY
# ============================================================

def create_skill_summary(
    skills
):
    """
    Create a summary from skill details.
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

        name = skill.get(
            "name",
            ""
        )

        if not name:
            continue

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
            len(skills),

        "categories":
            categories
    }


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    sample_text = """

    RISHI

    Computer Science Engineering

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

    print("\n================================")
    print("DETECTED SKILLS")
    print("================================")

    print(
        extract_skills(
            sample_text
        )
    )

    print("\n================================")
    print("CATEGORIZED SKILLS")
    print("================================")

    print(
        extract_skills_by_category(
            sample_text
        )
    )

    print("\n================================")
    print("SKILL DETAILS")
    print("================================")

    print(
        extract_skill_details(
            sample_text
        )
    )

    print("\n================================")
    print("DOCUMENT EXTRACTION")
    print("================================")

    print(
        extract_skills_from_documents(
            resume_text=sample_text,
            certificate_texts=[]
        )
    )