"""
LLM Analyzer
------------
Uses a local Ollama LLM to analyze real student data.

The analysis is based on:
- Academic information
- Manually entered skills
- Resume-extracted skills
- Certificate-extracted skills
- Certifications
- Projects
- Career preferences
- Learning goals

No OpenAI API is required.
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
        Prompt sent to the LLM.

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

        return (
            result.get(
                "response",
                ""
            )
            or ""
        ).strip()

    except requests.exceptions.ConnectionError as error:

        raise RuntimeError(
            "Could not connect to Ollama. "
            "Make sure Ollama is running."
        ) from error

    except requests.exceptions.Timeout as error:

        raise RuntimeError(
            "Ollama request timed out. "
            "The local model may need more time."
        ) from error

    except requests.exceptions.RequestException as error:

        raise RuntimeError(
            f"Ollama request failed: {error}"
        ) from error


# ============================================================
# CLEAN STUDENT DATA
# ============================================================

def prepare_student_data(student):
    """
    Prepare student data before sending it to the LLM.

    Sensitive/internal information such as:
    - password
    - MongoDB _id
    - uploaded file paths

    is removed.
    """

    if not isinstance(
        student,
        dict
    ):

        raise ValueError(
            "Student data must be a dictionary"
        )

    # --------------------------------------------------------
    # Create a clean copy
    # --------------------------------------------------------

    student_data = {

        "personal":
            student.get(
                "personal",
                {}
            ),

        "academic":
            student.get(
                "academic",
                {}
            ),

        "skills":
            student.get(
                "skills",
                []
            ),

        "certifications":
            student.get(
                "certifications",
                []
            ),

        "resume":
            student.get(
                "resume",
                {}
            ),

        "projects":
            student.get(
                "projects",
                []
            ),

        "career_preferences":
            student.get(
                "career_preferences",
                {}
            )
    }

    # --------------------------------------------------------
    # Add previously detected document skills
    # --------------------------------------------------------

    existing_llm_analysis = student.get(
        "llm_analysis",
        {}
    )

    if not isinstance(
        existing_llm_analysis,
        dict
    ):

        existing_llm_analysis = {}

    student_data[
        "detected_skills"
    ] = existing_llm_analysis.get(
        "detected_skills",
        {}
    )

    # --------------------------------------------------------
    # Remove password
    # --------------------------------------------------------

    student_data.pop(
        "password",
        None
    )

    # --------------------------------------------------------
    # Remove MongoDB ID
    # --------------------------------------------------------

    student_data.pop(
        "_id",
        None
    )

    # --------------------------------------------------------
    # Remove resume file information
    # --------------------------------------------------------

    resume = student_data.get(
        "resume"
    )

    if isinstance(
        resume,
        dict
    ):

        resume.pop(
            "file",
            None
        )

        # Remove physical server path
        resume.pop(
            "file_path",
            None
        )

        resume.pop(
            "stored_filename",
            None
        )

    # --------------------------------------------------------
    # Remove certificate file paths
    # --------------------------------------------------------

    certifications = student_data.get(
        "certifications"
    )

    if isinstance(
        certifications,
        list
    ):

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

            file_data = certification_copy.get(
                "file"
            )

            if isinstance(
                file_data,
                dict
            ):

                file_data = dict(
                    file_data
                )

                file_data.pop(
                    "file_path",
                    None
                )

                file_data.pop(
                    "stored_filename",
                    None
                )

                certification_copy[
                    "file"
                ] = file_data

            cleaned_certifications.append(
                certification_copy
            )

        student_data[
            "certifications"
        ] = cleaned_certifications

    return student_data


# ============================================================
# BUILD LLM PROMPT
# ============================================================

def build_analysis_prompt(student_data):
    """
    Build the prompt used by the LLM.

    The LLM is explicitly instructed to analyze
    only the student's real data.
    """

    student_json = json.dumps(

        student_data,

        indent=2,

        ensure_ascii=False,

        default=str

    )

    prompt = f"""
You are an AI-powered Student Skill Analyzer.

Your job is to analyze ONE student's actual information.

IMPORTANT RULES:

1. Analyze ONLY the information provided below.

2. Do NOT invent skills.

3. Do NOT assume that the student knows a skill
   that is not present in the data.

4. Do NOT use predefined career recommendations.

5. Do NOT recommend a career simply because it is
   popular or because you were instructed to mention it.

6. Career recommendations must be based on the student's
   actual skills, academic information, projects,
   certifications, resume/certificate detected skills,
   career preferences, and learning goals.

7. Clearly distinguish between:
   - manually entered skills
   - skills detected from documents

8. Identify realistic skill gaps based on the student's
   current profile and stated goals.

9. Learning recommendations should address the identified
   skill gaps.

10. If there is insufficient information for a conclusion,
    say so instead of inventing information.

STUDENT INFORMATION:

{student_json}

Return ONLY valid JSON.

Use exactly this structure:

{{
    "skill_summary": "Concise summary of the student's current skills and profile.",

    "strengths": [
        "Strength supported by the student's data"
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
        "career_reasoning": "Overall explanation of the career suitability."
    }},

    "learning_recommendations": [
        {{
            "topic": "Skill or topic",
            "reason": "Why the student should learn this"
        }}
    ],

    "overall_assessment": "Overall assessment of the student's current profile."
}}

Remember:

- Base every conclusion on the supplied student data.
- Do not hard-code career roles.
- Do not assume missing information.
- Do not include Markdown.
- Return JSON only.
"""

    return prompt


# ============================================================
# PARSE LLM RESPONSE
# ============================================================

def parse_llm_response(raw_response):
    """
    Convert the LLM response into a Python dictionary.
    """

    if not raw_response:

        return {

            "error":
                "LLM returned an empty response"

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
                "LLM response is not a JSON object",

            "raw_response":
                raw_response

        }

    except json.JSONDecodeError:

        return {

            "error":
                "LLM returned invalid JSON",

            "raw_response":
                raw_response

        }


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

    # --------------------------------------------------------
    # Prepare data
    # --------------------------------------------------------

    student_data = prepare_student_data(
        student
    )

    # --------------------------------------------------------
    # Build prompt
    # --------------------------------------------------------

    prompt = build_analysis_prompt(
        student_data
    )

    # --------------------------------------------------------
    # Call Ollama
    # --------------------------------------------------------

    raw_response = call_ollama(
        prompt
    )

    # --------------------------------------------------------
    # Parse response
    # --------------------------------------------------------

    analysis = parse_llm_response(
        raw_response
    )

    return analysis


# ============================================================
# SIMPLE TEST
# ============================================================

if __name__ == "__main__":

    test_student = {

        "personal": {

            "full_name":
                "Test Student",

            "department":
                "Computer Science"

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

        "certifications": [],

        "resume": {

            "has_resume":
                True,

            "resume_name":
                "resume.pdf"

        },

        "projects": [

            {

                "title":
                    "Student Management System",

                "description":
                    "A web application built using Python and MongoDB."

            }

        ],

        "career_preferences": {

            "interested_domain":
                "Software Development",

            "preferred_job_role":
                "",

            "learning_goal":
                "Improve programming skills"

        },

        "llm_analysis": {

            "detected_skills": {

                "skills": [
                    "Python",
                    "MongoDB",
                    "Flask"
                ],

                "categorized_skills": {

                    "Programming": [
                        "Python"
                    ],

                    "Databases": [
                        "MongoDB"
                    ],

                    "Web Development": [
                        "Flask"
                    ]

                }

            }

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