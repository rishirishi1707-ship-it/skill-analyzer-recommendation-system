"""
===========================================================
LLM ANALYZER
===========================================================

Uses a local Ollama LLM to analyze real student data.

The analyzer is responsible for:

1. Student profile analysis
2. Skill summary
3. Strength identification
4. Skill-gap identification
5. Career-role analysis
6. Learning recommendations
7. Overall assessment

IMPORTANT:
- No OpenAI API is required.
- Ollama runs locally.
- Only actual student information is provided to the LLM.
- Passwords and internal MongoDB information are removed.
- Automatically detected skills are read from:
      student["detected_skills"]
- Job matching is NOT performed here.

Job matching will be handled separately by:
    services/job_matcher.py
===========================================================
"""

import json
import requests


# ============================================================
# OLLAMA CONFIGURATION
# ============================================================

OLLAMA_URL = "http://localhost:11434/api/generate"

OLLAMA_MODEL = "llama3.1:8b"

OLLAMA_TIMEOUT = 300


# ============================================================
# CALL OLLAMA
# ============================================================

def call_ollama(prompt):
    """
    Send a prompt to the local Ollama model.

    Parameters
    ----------
    prompt : str
        Prompt sent to Ollama.

    Returns
    -------
    str
        Raw LLM response.
    """

    try:

        response = requests.post(

            OLLAMA_URL,

            json={

                "model":
                    OLLAMA_MODEL,

                "prompt":
                    prompt,

                "stream":
                    False,

                "format":
                    "json"

            },

            timeout=OLLAMA_TIMEOUT

        )

        response.raise_for_status()

        result = response.json()

        raw_response = result.get(
            "response",
            ""
        )

        if not raw_response:

            raise RuntimeError(
                "Ollama returned an empty response."
            )

        return raw_response.strip()

    # ========================================================
    # OLLAMA CONNECTION ERROR
    # ========================================================

    except requests.exceptions.ConnectionError as error:

        raise RuntimeError(
            "Could not connect to Ollama. "
            "Make sure Ollama is installed, running, "
            "and the required model is available."
        ) from error

    # ========================================================
    # OLLAMA TIMEOUT
    # ========================================================

    except requests.exceptions.Timeout as error:

        raise RuntimeError(
            "Ollama request timed out. "
            "The local model may need more time."
        ) from error

    # ========================================================
    # OTHER REQUEST ERROR
    # ========================================================

    except requests.exceptions.RequestException as error:

        raise RuntimeError(
            f"Ollama request failed: {error}"
        ) from error

    # ========================================================
    # UNEXPECTED ERROR
    # ========================================================

    except Exception as error:

        raise RuntimeError(
            f"Unexpected Ollama error: {error}"
        ) from error


# ============================================================
# CLEAN RESUME DATA
# ============================================================

def clean_resume_data(resume):
    """
    Remove internal/server-specific resume information
    before sending the data to Ollama.
    """

    if not isinstance(
        resume,
        dict
    ):

        return {}

    cleaned_resume = dict(
        resume
    )

    # --------------------------------------------------------
    # Remove physical/internal file information
    # --------------------------------------------------------

    cleaned_resume.pop(
        "file_path",
        None
    )

    cleaned_resume.pop(
        "stored_filename",
        None
    )

    cleaned_resume.pop(
        "file",
        None
    )

    return cleaned_resume


# ============================================================
# CLEAN CERTIFICATIONS
# ============================================================

def clean_certifications(certifications):
    """
    Remove internal file information from certifications
    while preserving useful certification information.
    """

    if not isinstance(
        certifications,
        list
    ):

        return []

    cleaned_certifications = []

    for certification in certifications:

        if not isinstance(
            certification,
            dict
        ):

            continue

        certification_copy = dict(
            certification
        )

        # ----------------------------------------------------
        # Clean uploaded file information
        # ----------------------------------------------------

        file_data = certification_copy.get(
            "file"
        )

        if isinstance(
            file_data,
            dict
        ):

            cleaned_file = dict(
                file_data
            )

            cleaned_file.pop(
                "file_path",
                None
            )

            cleaned_file.pop(
                "stored_filename",
                None
            )

            certification_copy[
                "file"
            ] = cleaned_file

        cleaned_certifications.append(
            certification_copy
        )

    return cleaned_certifications


# ============================================================
# CLEAN PROJECT DATA
# ============================================================

def clean_projects(projects):
    """
    Keep only meaningful project information.
    """

    if not isinstance(
        projects,
        list
    ):

        return []

    cleaned_projects = []

    for project in projects:

        if not isinstance(
            project,
            dict
        ):

            continue

        project_copy = dict(
            project
        )

        # Remove unnecessary internal information
        project_copy.pop(
            "_id",
            None
        )

        project_copy.pop(
            "file_path",
            None
        )

        cleaned_projects.append(
            project_copy
        )

    return cleaned_projects


# ============================================================
# CLEAN SKILLS
# ============================================================

def clean_skills(skills):
    """
    Clean manually entered skills.
    """

    if not isinstance(
        skills,
        list
    ):

        return []

    cleaned_skills = []

    for skill in skills:

        # ----------------------------------------------------
        # Skill stored as dictionary
        # ----------------------------------------------------

        if isinstance(
            skill,
            dict
        ):

            skill_copy = dict(
                skill
            )

            skill_copy.pop(
                "_id",
                None
            )

            cleaned_skills.append(
                skill_copy
            )

        # ----------------------------------------------------
        # Skill stored as string
        # ----------------------------------------------------

        elif isinstance(
            skill,
            str
        ):

            cleaned_skills.append(
                skill
            )

    return cleaned_skills


# ============================================================
# CLEAN DETECTED SKILLS
# ============================================================

def clean_detected_skills(detected_skills):
    """
    Clean automatically detected skills.

    These skills come from:
        Resume
        Certificates
        Skill extractor
    """

    if not isinstance(
        detected_skills,
        dict
    ):

        return {

            "resume": [],

            "certificates": [],

            "all": [],

            "details": []

        }

    return {

        "resume":
            detected_skills.get(
                "resume",
                detected_skills.get(
                    "resume_skills",
                    []
                )
            ),

        "certificates":
            detected_skills.get(
                "certificates",
                detected_skills.get(
                    "certificate_skills",
                    []
                )
            ),

        "all":
            detected_skills.get(
                "all",
                detected_skills.get(
                    "skills",
                    []
                )
            ),

        "details":
            detected_skills.get(
                "details",
                detected_skills.get(
                    "skill_details",
                    []
                )
            )

    }


# ============================================================
# PREPARE STUDENT DATA
# ============================================================

def prepare_student_data(student):
    """
    Prepare a clean student profile before sending it
    to the LLM.

    Internal information such as:
        - password
        - MongoDB _id
        - physical file paths
        - stored filenames

    is removed.

    IMPORTANT:
    Automatically detected skills are taken directly from:

        student["detected_skills"]

    and NOT from llm_analysis.
    """

    if not isinstance(
        student,
        dict
    ):

        raise ValueError(
            "Student data must be a dictionary."
        )

    # ========================================================
    # BASIC STUDENT DATA
    # ========================================================

    personal = student.get(
        "personal",
        {}
    )

    academic = student.get(
        "academic",
        {}
    )

    skills = student.get(
        "skills",
        []
    )

    detected_skills = student.get(
        "detected_skills",
        {}
    )

    certifications = student.get(
        "certifications",
        []
    )

    resume = student.get(
        "resume",
        {}
    )

    projects = student.get(
        "projects",
        []
    )

    career_preferences = student.get(
        "career_preferences",
        {}
    )

    # ========================================================
    # CREATE CLEAN PROFILE
    # ========================================================

    student_data = {

        "personal": (
            personal
            if isinstance(
                personal,
                dict
            )
            else {}
        ),

        "academic": (
            academic
            if isinstance(
                academic,
                dict
            )
            else {}
        ),

        "skills":
            clean_skills(
                skills
            ),

        "detected_skills":
            clean_detected_skills(
                detected_skills
            ),

        "certifications":
            clean_certifications(
                certifications
            ),

        "resume":
            clean_resume_data(
                resume
            ),

        "projects":
            clean_projects(
                projects
            ),

        "career_preferences": (
            career_preferences
            if isinstance(
                career_preferences,
                dict
            )
            else {}
        )

    }

    # ========================================================
    # REMOVE SENSITIVE PERSONAL INFORMATION
    # ========================================================

    # We don't need these fields for skill analysis.

    student_data["personal"].pop(
        "password",
        None
    )

    student_data["personal"].pop(
        "_id",
        None
    )

    # Email and mobile are also unnecessary for LLM analysis.

    student_data["personal"].pop(
        "email",
        None
    )

    student_data["personal"].pop(
        "mobile",
        None
    )

    # ========================================================
    # REMOVE INTERNAL INFORMATION
    # ========================================================

    student_data.pop(
        "_id",
        None
    )

    student_data.pop(
        "password",
        None
    )

    return student_data


# ============================================================
# BUILD LLM PROMPT
# ============================================================

def build_analysis_prompt(student_data):
    """
    Build the prompt used by Ollama.

    The LLM is instructed to analyze only the student's
    actual information.
    """

    student_json = json.dumps(

        student_data,

        indent=2,

        ensure_ascii=False,

        default=str

    )

    prompt = f"""
You are an AI-powered Student Skill Analyzer.

Your task is to analyze ONE student's actual profile.

You must use ONLY the information provided below.

============================================================
STRICT ANALYSIS RULES
============================================================

1. Do NOT invent skills.

2. Do NOT assume the student knows a technology that
   does not appear in the supplied information.

3. Do NOT create fake certifications.

4. Do NOT create fake projects.

5. Do NOT assume experience that is not provided.

6. Clearly distinguish manually entered skills from
   automatically detected document skills.

7. Use academic information when evaluating the student's
   current profile.

8. Use projects and certifications as supporting evidence.

9. Use career preferences and learning goals when analyzing
   suitable career directions.

10. Identify realistic skill gaps.

11. Learning recommendations should directly address
    identified skill gaps.

12. If there is insufficient information, explicitly say
    that there is insufficient information.

13. Do NOT use predefined career recommendations.

14. Do NOT recommend a role merely because it is popular.

15. Do NOT invent job requirements.

16. Do NOT perform company/job matching in this analysis.

17. Job matching will be handled separately by the
    application's job matching service.

18. Return ONLY valid JSON.

19. Do NOT use Markdown.

============================================================
STUDENT PROFILE
============================================================

{student_json}

============================================================
OUTPUT FORMAT
============================================================

Return exactly one JSON object with this structure:

{{
    "skill_summary": "Concise summary of the student's current profile and skills.",

    "overall_score": 0,

    "strengths": [
        "Strength supported by the student's actual data"
    ],

    "skill_gaps": [
        {{
            "skill": "Skill name",
            "reason": "Why this is a relevant skill gap"
        }}
    ],

    "career_analysis": {{
        "suitable_roles": [
            {{
                "role": "Career role",
                "reason": "Why this role matches the student's actual profile"
            }}
        ],
        "career_reasoning": "Overall explanation of career suitability."
    }},

    "learning_recommendations": [
        {{
            "topic": "Skill or topic",
            "reason": "Why the student should learn this"
        }}
    ],

    "overall_assessment": "Overall assessment of the student's current profile."
}}

============================================================
OVERALL SCORE RULE
============================================================

Give an overall score from 0 to 10.

The score should consider:

- Academic profile
- Manually entered skills
- Automatically detected skills
- Certifications
- Projects
- Career preferences
- Learning goals

Do not award points for information that is not present.

============================================================
FINAL REMINDER
============================================================

Analyze only the supplied student data.

Do not invent missing information.

Do not hard-code career roles.

Do not perform company/job matching.

Return valid JSON only.
"""

    return prompt


# ============================================================
# PARSE LLM RESPONSE
# ============================================================

def parse_llm_response(raw_response):
    """
    Convert the LLM response into a Python dictionary.

    Handles:
    - Valid JSON
    - JSON surrounded by whitespace
    - Invalid JSON
    - Empty responses
    """

    if not raw_response:

        return {

            "error":
                "LLM returned an empty response."

        }

    try:

        parsed_response = json.loads(
            raw_response
        )

        if isinstance(
            parsed_response,
            dict
        ):

            return parsed_response

        return {

            "error":
                "LLM response is not a JSON object.",

            "raw_response":
                raw_response

        }

    except json.JSONDecodeError as error:

        print(
            "LLM JSON parsing error:",
            error
        )

        return {

            "error":
                "LLM returned invalid JSON.",

            "raw_response":
                raw_response

        }


# ============================================================
# VALIDATE ANALYSIS
# ============================================================

def validate_analysis(analysis):
    """
    Ensure the LLM result has the expected structure.

    Missing fields are filled with safe defaults.
    """

    if not isinstance(
        analysis,
        dict
    ):

        return {

            "error":
                "Invalid analysis format."

        }

    # ========================================================
    # BASIC FIELDS
    # ========================================================

    if not isinstance(
        analysis.get(
            "skill_summary"
        ),
        str
    ):

        analysis[
            "skill_summary"
        ] = ""

    # ========================================================
    # OVERALL SCORE
    # ========================================================

    score = analysis.get(
        "overall_score"
    )

    try:

        score = float(
            score
        )

        if score < 0:

            score = 0

        if score > 10:

            score = 10

        analysis[
            "overall_score"
        ] = score

    except (
        TypeError,
        ValueError
    ):

        analysis[
            "overall_score"
        ] = None

    # ========================================================
    # STRENGTHS
    # ========================================================

    if not isinstance(
        analysis.get(
            "strengths"
        ),
        list
    ):

        analysis[
            "strengths"
        ] = []

    # ========================================================
    # SKILL GAPS
    # ========================================================

    if not isinstance(
        analysis.get(
            "skill_gaps"
        ),
        list
    ):

        analysis[
            "skill_gaps"
        ] = []

    # ========================================================
    # CAREER ANALYSIS
    # ========================================================

    career_analysis = analysis.get(
        "career_analysis"
    )

    if not isinstance(
        career_analysis,
        dict
    ):

        career_analysis = {}

    if not isinstance(
        career_analysis.get(
            "suitable_roles"
        ),
        list
    ):

        career_analysis[
            "suitable_roles"
        ] = []

    if not isinstance(
        career_analysis.get(
            "career_reasoning"
        ),
        str
    ):

        career_analysis[
            "career_reasoning"
        ] = ""

    analysis[
        "career_analysis"
    ] = career_analysis

    # ========================================================
    # LEARNING RECOMMENDATIONS
    # ========================================================

    if not isinstance(
        analysis.get(
            "learning_recommendations"
        ),
        list
    ):

        analysis[
            "learning_recommendations"
        ] = []

    # ========================================================
    # OVERALL ASSESSMENT
    # ========================================================

    if not isinstance(
        analysis.get(
            "overall_assessment"
        ),
        str
    ):

        analysis[
            "overall_assessment"
        ] = ""

    return analysis


# ============================================================
# ANALYZE STUDENT
# ============================================================

def analyze_student(student):
    """
    Analyze an actual student profile using Ollama.

    Parameters
    ----------
    student : dict
        Student document retrieved from MongoDB.

    Returns
    -------
    dict
        Structured LLM analysis.
    """

    # ========================================================
    # PREPARE STUDENT DATA
    # ========================================================

    student_data = prepare_student_data(
        student
    )

    # ========================================================
    # BUILD PROMPT
    # ========================================================

    prompt = build_analysis_prompt(
        student_data
    )

    # ========================================================
    # CALL OLLAMA
    # ========================================================

    raw_response = call_ollama(
        prompt
    )

    # ========================================================
    # PARSE RESPONSE
    # ========================================================

    analysis = parse_llm_response(
        raw_response
    )

    # ========================================================
    # CHECK ERROR
    # ========================================================

    if "error" in analysis:

        return analysis

    # ========================================================
    # VALIDATE STRUCTURE
    # ========================================================

    analysis = validate_analysis(
        analysis
    )

    return analysis


# ============================================================
# SIMPLE LOCAL TEST
# ============================================================

if __name__ == "__main__":

    test_student = {

        "personal": {

            "full_name":
                "Test Student",

            "department":
                "Computer Science",

            "degree":
                "B.E",

            "year_of_study":
                "3rd Year"

        },

        "academic": {

            "current_cgpa":
                8.5,

            "graduation_year":
                2027

        },

        # ----------------------------------------------------
        # MANUALLY ENTERED SKILLS
        # ----------------------------------------------------

        "skills": [

            {

                "name":
                    "Python",

                "category":
                    "Programming",

                "proficiency":
                    "Advanced",

                "source":
                    "manual"

            },

            {

                "name":
                    "MongoDB",

                "category":
                    "Databases",

                "proficiency":
                    "Intermediate",

                "source":
                    "manual"

            }

        ],

        # ----------------------------------------------------
        # AUTOMATICALLY DETECTED SKILLS
        #
        # IMPORTANT:
        # This is now read from student["detected_skills"]
        # ----------------------------------------------------

        "detected_skills": {

            "resume": [

                "Python",

                "Flask",

                "REST API"

            ],

            "certificates": [

                "Java",

                "SQL"

            ],

            "all": [

                "Python",

                "Flask",

                "REST API",

                "Java",

                "SQL"

            ],

            "details": []

        },

        # ----------------------------------------------------
        # CERTIFICATIONS
        # ----------------------------------------------------

        "certifications": [],

        # ----------------------------------------------------
        # RESUME
        # ----------------------------------------------------

        "resume": {

            "has_resume":
                True,

            "resume_name":
                "resume.pdf"

        },

        # ----------------------------------------------------
        # PROJECTS
        # ----------------------------------------------------

        "projects": [

            {

                "title":
                    "Student Management System",

                "description":
                    "A web application built using Python and MongoDB."

            }

        ],

        # ----------------------------------------------------
        # CAREER PREFERENCES
        # ----------------------------------------------------

        "career_preferences": {

            "interested_domain":
                "Software Development",

            "preferred_job_role":
                "",

            "preferred_location":
                "",

            "career_goal":
                "Become a software developer",

            "learning_goal":
                "Improve programming and backend development skills"

        },

        # ----------------------------------------------------
        # INTERNAL DATA
        # ----------------------------------------------------

        "_id":
            "internal-id",

        "password":
            "should-never-be-sent-to-llm"

    }

    print(
        "\n========================================"
    )

    print(
        "TESTING LOCAL LLM ANALYZER"
    )

    print(
        "========================================"
    )

    try:

        result = analyze_student(
            test_student
        )

        print(
            json.dumps(
                result,
                indent=4,
                ensure_ascii=False
            )
        )

    except Exception as error:

        print(
            "\nLLM ANALYSIS ERROR:"
        )

        print(
            error
        )

    print(
        "\n========================================"
    )