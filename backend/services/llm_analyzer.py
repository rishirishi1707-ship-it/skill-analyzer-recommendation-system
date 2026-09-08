"""
===========================================================
LLM ANALYZER
===========================================================

Uses a local Ollama LLM to analyze real student data.

Responsibilities:

1. Student profile analysis
2. Skill summary
3. Strength identification
4. Skill-gap identification
5. Career-role analysis
6. Learning recommendations
7. Overall assessment

IMPORTANT:

- Ollama runs locally.
- No OpenAI API required.
- Only actual student information is provided.
- Passwords and internal file paths are removed.
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


    except requests.exceptions.ConnectionError as error:

        raise RuntimeError(

            "Could not connect to Ollama. "
            "Make sure Ollama is running and "
            "the required model is available."

        ) from error


    except requests.exceptions.Timeout as error:

        raise RuntimeError(

            "Ollama request timed out."

        ) from error


    except requests.exceptions.RequestException as error:

        raise RuntimeError(

            f"Ollama request failed: {error}"

        ) from error


    except Exception as error:

        raise RuntimeError(

            f"Unexpected Ollama error: {error}"

        ) from error


# ============================================================
# CLEAN RESUME DATA
# ============================================================

def clean_resume_data(resume):

    """
    Remove internal file information and
    extracted document text.
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
    # Resume file is nested inside:
    #
    # resume["file"]
    # --------------------------------------------------------

    file_data = cleaned_resume.get(
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

        cleaned_file.pop(
            "extracted_text",
            None
        )


        cleaned_resume[
            "file"
        ] = cleaned_file


    # --------------------------------------------------------
    # Remove possible direct internal fields
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
        "extracted_text",
        None
    )


    return cleaned_resume


# ============================================================
# CLEAN CERTIFICATIONS
# ============================================================

def clean_certifications(certifications):

    """
    Remove internal certificate file information.
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
        # Nested certificate file
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

            cleaned_file.pop(
                "extracted_text",
                None
            )


            certification_copy[
                "file"
            ] = cleaned_file


        # ----------------------------------------------------
        # Direct fields
        # ----------------------------------------------------

        certification_copy.pop(
            "file_path",
            None
        )

        certification_copy.pop(
            "stored_filename",
            None
        )

        certification_copy.pop(
            "extracted_text",
            None
        )


        cleaned_certifications.append(
            certification_copy
        )


    return cleaned_certifications


# ============================================================
# CLEAN PROJECT DATA
# ============================================================

def clean_projects(projects):

    """
    Keep meaningful project information.
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
# CLEAN MANUAL SKILLS
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

    Compatible with current student_routes.py:

        student["detected_skills"] = {

            "resume": [],
            "certificates": [],
            "all": [],
            "categorized_skills": {},
            "details": [],
            "document_count": 0

        }
    """

    if not isinstance(
        detected_skills,
        dict
    ):

        return {

            "resume": [],

            "certificates": [],

            "all": [],

            "categorized_skills": {},

            "details": [],

            "document_count": 0

        }


    resume_skills = detected_skills.get(
        "resume",
        []
    )


    certificate_skills = detected_skills.get(
        "certificates",
        []
    )


    all_skills = detected_skills.get(
        "all",
        []
    )


    categorized_skills = detected_skills.get(
        "categorized_skills",
        {}
    )


    skill_details = detected_skills.get(
        "details",
        []
    )


    document_count = detected_skills.get(
        "document_count",
        0
    )


    # --------------------------------------------------------
    # VALIDATE TYPES
    # --------------------------------------------------------

    if not isinstance(
        resume_skills,
        list
    ):

        resume_skills = []


    if not isinstance(
        certificate_skills,
        list
    ):

        certificate_skills = []


    if not isinstance(
        all_skills,
        list
    ):

        all_skills = []


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

        "resume":
            resume_skills,

        "certificates":
            certificate_skills,

        "all":
            all_skills,

        "categorized_skills":
            categorized_skills,

        "details":
            skill_details,

        "document_count":
            document_count

    }


# ============================================================
# GET DETECTED SKILLS
# ============================================================

def get_detected_skills(student):

    """
    Retrieve automatically detected skills.

    CURRENT LOCATION:

        student["detected_skills"]
    """

    if not isinstance(
        student,
        dict
    ):

        return clean_detected_skills(
            {}
        )


    detected_skills = student.get(
        "detected_skills",
        {}
    )


    return clean_detected_skills(
        detected_skills
    )


# ============================================================
# PREPARE STUDENT DATA
# ============================================================

def prepare_student_data(student):

    """
    Prepare a clean student profile before
    sending data to the LLM.
    """

    if not isinstance(
        student,
        dict
    ):

        raise ValueError(
            "Student data must be a dictionary."
        )


    # ========================================================
    # BASIC DATA
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
    # DETECTED SKILLS
    # ========================================================

    detected_skills = get_detected_skills(
        student
    )


    # ========================================================
    # CLEAN PERSONAL DATA
    # ========================================================

    if isinstance(
        personal,
        dict
    ):

        cleaned_personal = dict(
            personal
        )

    else:

        cleaned_personal = {}


    # --------------------------------------------------------
    # Remove private information
    # --------------------------------------------------------

    cleaned_personal.pop(
        "email",
        None
    )

    cleaned_personal.pop(
        "mobile",
        None
    )

    cleaned_personal.pop(
        "password",
        None
    )

    cleaned_personal.pop(
        "_id",
        None
    )


    # ========================================================
    # CREATE CLEAN PROFILE
    # ========================================================

    student_data = {

        "personal":
            cleaned_personal,


        "academic":

            academic

            if isinstance(
                academic,
                dict
            )

            else {},


        # ----------------------------------------------------
        # MANUAL SKILLS
        # ----------------------------------------------------

        "manual_skills":

            clean_skills(
                skills
            ),


        # ----------------------------------------------------
        # AUTOMATICALLY DETECTED SKILLS
        # ----------------------------------------------------

        "detected_skills":

            detected_skills,


        # ----------------------------------------------------
        # CERTIFICATIONS
        # ----------------------------------------------------

        "certifications":

            clean_certifications(
                certifications
            ),


        # ----------------------------------------------------
        # RESUME
        # ----------------------------------------------------

        "resume":

            clean_resume_data(
                resume
            ),


        # ----------------------------------------------------
        # PROJECTS
        # ----------------------------------------------------

        "projects":

            clean_projects(
                projects
            ),


        # ----------------------------------------------------
        # CAREER PREFERENCES
        # ----------------------------------------------------

        "career_preferences":

            career_preferences

            if isinstance(
                career_preferences,
                dict
            )

            else {}

    }


    return student_data


# ============================================================
# BUILD LLM PROMPT
# ============================================================

def build_analysis_prompt(student_data):

    """
    Build prompt for Ollama.
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

2. Do NOT assume the student knows a technology
that does not appear in the supplied information.

3. Do NOT create fake certifications.

4. Do NOT create fake projects.

5. Do NOT assume work experience.

6. Clearly distinguish manually entered skills
from automatically detected document skills.

7. Use academic information only when it exists.

8. Use projects and certifications as supporting evidence.

9. Use career preferences and learning goals when available.

10. Identify realistic skill gaps.

11. Learning recommendations must directly address
identified skill gaps.

12. If information is insufficient,
explicitly mention that.

13. Do NOT recommend roles simply because they are popular.

14. Do NOT invent job requirements.

15. Do NOT perform company matching.

16. Do NOT perform job matching.

17. Job matching is handled separately by the
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

Return exactly one JSON object:

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

        "career_reasoning":
            "Overall explanation of career suitability."
    }},

    "learning_recommendations": [
        {{
            "topic": "Skill or topic",
            "reason": "Why the student should learn this"
        }}
    ],

    "overall_assessment":
        "Overall assessment of the student's current profile."
}}

============================================================
OVERALL SCORE RULE
============================================================

Give an overall score from 0 to 10.

Consider only information actually provided:

- Academic profile
- Manually entered skills
- Automatically detected skills
- Certifications
- Projects
- Career preferences
- Learning goals

Do not award points for missing information.

============================================================
FINAL REMINDER
============================================================

Analyze only the supplied student data.

Do not invent missing information.

Do not hard-code career roles.

Do not perform company matching.

Do not perform job matching.

Return valid JSON only.
"""


    return prompt


# ============================================================
# PARSE LLM RESPONSE
# ============================================================

def parse_llm_response(raw_response):

    """
    Convert LLM response into a Python dictionary.
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
    # SKILL SUMMARY
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

        score = max(
            0,
            min(
                10,
                score
            )
        )


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
    Analyze a real student profile using Ollama.
    """

    # --------------------------------------------------------
    # PREPARE DATA
    # --------------------------------------------------------

    student_data = prepare_student_data(
        student
    )


    # --------------------------------------------------------
    # BUILD PROMPT
    # --------------------------------------------------------

    prompt = build_analysis_prompt(
        student_data
    )


    # --------------------------------------------------------
    # CALL OLLAMA
    # --------------------------------------------------------

    raw_response = call_ollama(
        prompt
    )


    # --------------------------------------------------------
    # PARSE RESPONSE
    # --------------------------------------------------------

    analysis = parse_llm_response(
        raw_response
    )


    # --------------------------------------------------------
    # RETURN ERROR
    # --------------------------------------------------------

    if "error" in analysis:

        return analysis


    # --------------------------------------------------------
    # VALIDATE RESPONSE
    # --------------------------------------------------------

    analysis = validate_analysis(
        analysis
    )


    return analysis


# ============================================================
# LOCAL TEST
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


        "skills": [

            {

                "name":
                    "Python",

                "category":
                    "Programming",

                "proficiency":
                    "Advanced"

            },

            {

                "name":
                    "MongoDB",

                "category":
                    "Database",

                "proficiency":
                    "Intermediate"

            }

        ],


        "detected_skills": {

            "resume": [

                "Python",

                "Flask"

            ],

            "certificates": [

                "MongoDB"

            ],

            "all": [

                "Python",

                "Flask",

                "MongoDB"

            ],

            "categorized_skills": {

                "Programming": [

                    "Python"

                ],

                "Web Development": [

                    "Flask"

                ],

                "Databases": [

                    "MongoDB"

                ]

            },

            "details": [

                {

                    "name":
                        "Python",

                    "category":
                        "Programming",

                    "source":
                        "document"

                }

            ],

            "document_count":
                2

        },


        "resume": {

            "has_resume":
                True,

            "resume_name":
                "resume.pdf"

        },


        "certifications": [],


        "projects": [

            {

                "title":
                    "Student Management System",

                "description":
                    "Web application using Python, Flask and MongoDB."

            }

        ],


        "career_preferences": {

            "interested_domain":
                "Software Development",

            "preferred_job_role":
                "Backend Developer",

            "career_goal":
                "Become a software developer",

            "learning_goal":
                "Improve backend development skills"

        }

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