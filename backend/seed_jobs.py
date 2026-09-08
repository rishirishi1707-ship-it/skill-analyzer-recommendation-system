# =========================================================
# seed_jobs.py
# =========================================================

from config import db


jobs_collection = db["job_requirements"]


jobs = [

    # =====================================================
    # TCS - JOB 1
    # =====================================================

    {
        "company_name": "TCS",

        "job_role": "Graduate Software Engineer",

        "job_description":
            "Entry-level software engineering role involving "
            "application development, programming, testing and "
            "problem solving.",

        "required_skills": [
            "Java",
            "SQL",
            "Git",
            "Data Structures"
        ],

        "preferred_skills": [
            "Spring Boot",
            "REST API",
            "MongoDB"
        ],

        "minimum_score": 6.0,

        "eligibility": {
            "degrees": [
                "B.E",
                "B.Tech"
            ],

            "branches": [
                "CSE",
                "IT",
                "ECE"
            ],

            "minimum_cgpa": 6.0,

            "graduation_years": [
                2026,
                2027
            ],

            "maximum_backlogs": 0
        },

        "location": [
            "Chennai",
            "Bangalore",
            "Hyderabad"
        ],

        "employment_type": "Full-time",

        "experience_required": "0-1 years",

        "application_url":
            "https://www.tcs.com/careers/india"
    },


    # =====================================================
    # TCS - JOB 2
    # =====================================================

    {
        "company_name": "TCS",

        "job_role": "Data Analyst",

        "job_description":
            "Entry-level data role involving data analysis, "
            "SQL queries, reporting and basic programming.",

        "required_skills": [
            "Python",
            "SQL",
            "Excel",
            "Data Analysis"
        ],

        "preferred_skills": [
            "Power BI",
            "Pandas",
            "Statistics"
        ],

        "minimum_score": 6.0,

        "eligibility": {
            "degrees": [
                "B.E",
                "B.Tech"
            ],

            "branches": [
                "CSE",
                "IT",
                "ECE",
                "EEE"
            ],

            "minimum_cgpa": 6.0,

            "graduation_years": [
                2026,
                2027
            ],

            "maximum_backlogs": 0
        },

        "location": [
            "Chennai",
            "Bangalore"
        ],

        "employment_type": "Full-time",

        "experience_required": "0-1 years",

        "application_url":
            "https://www.tcs.com/careers/india"
    },


    # =====================================================
    # INFOSYS - JOB 3
    # =====================================================

    {
        "company_name": "Infosys",

        "job_role": "Associate Software Engineer",

        "job_description":
            "Graduate technology role involving software "
            "development, testing, debugging and client solutions.",

        "required_skills": [
            "Java",
            "Python",
            "SQL",
            "Problem Solving"
        ],

        "preferred_skills": [
            "Git",
            "REST API",
            "Spring Boot"
        ],

        "minimum_score": 6.0,

        "eligibility": {
            "degrees": [
                "B.E",
                "B.Tech"
            ],

            "branches": [
                "CSE",
                "IT",
                "ECE"
            ],

            "minimum_cgpa": 6.0,

            "graduation_years": [
                2026,
                2027
            ],

            "maximum_backlogs": 0
        },

        "location": [
            "Chennai",
            "Bangalore",
            "Hyderabad",
            "Pune"
        ],

        "employment_type": "Full-time",

        "experience_required": "0-1 years",

        "application_url":
            "https://www.infosys.com/careers/apply.html"
    },


    # =====================================================
    # INFOSYS - JOB 4
    # =====================================================

    {
        "company_name": "Infosys",

        "job_role": "Specialist Programmer",

        "job_description":
            "Programming-focused entry-level role involving "
            "software development and technical problem solving.",

        "required_skills": [
            "Java",
            "Data Structures",
            "Algorithms",
            "SQL"
        ],

        "preferred_skills": [
            "Python",
            "Spring Boot",
            "Cloud"
        ],

        "minimum_score": 7.0,

        "eligibility": {
            "degrees": [
                "B.E",
                "B.Tech"
            ],

            "branches": [
                "CSE",
                "IT"
            ],

            "minimum_cgpa": 7.0,

            "graduation_years": [
                2026,
                2027
            ],

            "maximum_backlogs": 0
        },

        "location": [
            "Bangalore",
            "Hyderabad",
            "Pune"
        ],

        "employment_type": "Full-time",

        "experience_required": "0-1 years",

        "application_url":
            "https://www.infosys.com/careers/graduates.html"
    },


    # =====================================================
    # ACCENTURE - JOB 5
    # =====================================================

    {
        "company_name": "Accenture",

        "job_role": "Application Development Associate",

        "job_description":
            "Entry-level application development role involving "
            "designing, building, testing and configuring software.",

        "required_skills": [
            "Java",
            "SQL",
            "Data Structures",
            "Problem Solving"
        ],

        "preferred_skills": [
            "Python",
            "REST API",
            "Cloud"
        ],

        "minimum_score": 6.0,

        "eligibility": {
            "degrees": [
                "B.E",
                "B.Tech"
            ],

            "branches": [
                "CSE",
                "IT",
                "ECE",
                "EEE"
            ],

            "minimum_cgpa": 6.0,

            "graduation_years": [
                2026,
                2027
            ],

            "maximum_backlogs": 0
        },

        "location": [
            "Chennai",
            "Bangalore",
            "Hyderabad",
            "Pune"
        ],

        "employment_type": "Full-time",

        "experience_required": "0-1 years",

        "application_url":
            "https://www.accenture.com/in-en/careers"
    },


    # =====================================================
    # ACCENTURE - JOB 6
    # =====================================================

    {
        "company_name": "Accenture",

        "job_role": "Cloud Technology Associate",

        "job_description":
            "Entry-level technology role involving cloud "
            "platforms, application support and modern software systems.",

        "required_skills": [
            "Python",
            "SQL",
            "Linux",
            "Cloud Computing"
        ],

        "preferred_skills": [
            "AWS",
            "Azure",
            "Docker",
            "Git"
        ],

        "minimum_score": 6.0,

        "eligibility": {
            "degrees": [
                "B.E",
                "B.Tech"
            ],

            "branches": [
                "CSE",
                "IT",
                "ECE"
            ],

            "minimum_cgpa": 6.0,

            "graduation_years": [
                2026,
                2027
            ],

            "maximum_backlogs": 0
        },

        "location": [
            "Bangalore",
            "Hyderabad",
            "Pune"
        ],

        "employment_type": "Full-time",

        "experience_required": "0-1 years",

        "application_url":
            "https://www.accenture.com/in-en/careers"
    },


    # =====================================================
    # COGNIZANT - JOB 7
    # =====================================================

    {
        "company_name": "Cognizant",

        "job_role": "Programmer Analyst Trainee",

        "job_description":
            "Graduate technology role involving programming, "
            "application development, testing and technical support.",

        "required_skills": [
            "Java",
            "SQL",
            "Python",
            "Problem Solving"
        ],

        "preferred_skills": [
            "Git",
            "REST API",
            "Cloud"
        ],

        "minimum_score": 6.0,

        "eligibility": {
            "degrees": [
                "B.E",
                "B.Tech"
            ],

            "branches": [
                "CSE",
                "IT",
                "ECE"
            ],

            "minimum_cgpa": 6.0,

            "graduation_years": [
                2026,
                2027
            ],

            "maximum_backlogs": 0
        },

        "location": [
            "Chennai",
            "Bangalore",
            "Hyderabad",
            "Pune"
        ],

        "employment_type": "Full-time",

        "experience_required": "0-1 years",

        "application_url":
            "https://careers.cognizant.com/india-en/"
    },


    # =====================================================
    # COGNIZANT - JOB 8
    # =====================================================

    {
        "company_name": "Cognizant",

        "job_role": "Junior Data Analyst",

        "job_description":
            "Entry-level data role involving data processing, "
            "SQL analysis, reporting and business insights.",

        "required_skills": [
            "Python",
            "SQL",
            "Excel",
            "Statistics"
        ],

        "preferred_skills": [
            "Power BI",
            "Pandas",
            "Data Visualization"
        ],

        "minimum_score": 6.0,

        "eligibility": {
            "degrees": [
                "B.E",
                "B.Tech"
            ],

            "branches": [
                "CSE",
                "IT",
                "ECE",
                "EEE"
            ],

            "minimum_cgpa": 6.0,

            "graduation_years": [
                2026,
                2027
            ],

            "maximum_backlogs": 0
        },

        "location": [
            "Chennai",
            "Bangalore"
        ],

        "employment_type": "Full-time",

        "experience_required": "0-1 years",

        "application_url":
            "https://careers.cognizant.com/india-en/"
    },


    # =====================================================
    # CAPGEMINI - JOB 9
    # =====================================================

    {
        "company_name": "Capgemini",

        "job_role": "Software Engineer - Graduate",

        "job_description":
            "Graduate software engineering role involving "
            "application development, testing and modern technology.",

        "required_skills": [
            "Java",
            "SQL",
            "Git",
            "Problem Solving"
        ],

        "preferred_skills": [
            "Spring Boot",
            "REST API",
            "Docker"
        ],

        "minimum_score": 6.0,

        "eligibility": {
            "degrees": [
                "B.E",
                "B.Tech"
            ],

            "branches": [
                "CSE",
                "IT",
                "ECE"
            ],

            "minimum_cgpa": 6.0,

            "graduation_years": [
                2026,
                2027
            ],

            "maximum_backlogs": 0
        },

        "location": [
            "Chennai",
            "Bangalore",
            "Mumbai",
            "Pune"
        ],

        "employment_type": "Full-time",

        "experience_required": "0-1 years",

        "application_url":
            "https://www.capgemini.com/in-en/careers/"
    },


    # =====================================================
    # CAPGEMINI - JOB 10
    # =====================================================

    {
        "company_name": "Capgemini",

        "job_role": "Cloud & Data Graduate Engineer",

        "job_description":
            "Graduate technology role involving cloud, data "
            "processing and software engineering concepts.",

        "required_skills": [
            "Python",
            "SQL",
            "Cloud Computing",
            "Data Analysis"
        ],

        "preferred_skills": [
            "AWS",
            "Azure",
            "Pandas",
            "Power BI"
        ],

        "minimum_score": 6.0,

        "eligibility": {
            "degrees": [
                "B.E",
                "B.Tech"
            ],

            "branches": [
                "CSE",
                "IT",
                "ECE"
            ],

            "minimum_cgpa": 6.0,

            "graduation_years": [
                2026,
                2027
            ],

            "maximum_backlogs": 0
        },

        "location": [
            "Bangalore",
            "Hyderabad",
            "Pune"
        ],

        "employment_type": "Full-time",

        "experience_required": "0-1 years",

        "application_url":
            "https://www.capgemini.com/in-en/careers/"
    }

]


# =========================================================
# INSERT JOBS
# =========================================================

if __name__ == "__main__":

    print(
        "\n========================================"
    )

    print(
        "JOB DATASET SEED"
    )

    print(
        "========================================"
    )


    # -----------------------------------------------------
    # OPTIONAL: CLEAR EXISTING PROTOTYPE JOBS
    # -----------------------------------------------------

    existing_count = jobs_collection.count_documents({})

    print(
        f"Existing jobs: {existing_count}"
    )


    # -----------------------------------------------------
    # INSERT
    # -----------------------------------------------------

    result = jobs_collection.insert_many(
        jobs
    )


    print(
        f"Inserted jobs: {len(result.inserted_ids)}"
    )


    # -----------------------------------------------------
    # FINAL COUNT
    # -----------------------------------------------------

    final_count = jobs_collection.count_documents({})

    print(
        f"Total jobs in database: {final_count}"
    )


    print(
        "\nJob dataset inserted successfully."
    )