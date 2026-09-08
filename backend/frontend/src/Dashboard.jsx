import { useEffect, useState } from "react";

function Dashboard({ onLogout }) {
    // =========================================================
    // STATE
    // =========================================================

    const [student, setStudent] = useState(null);

    const [activeSection, setActiveSection] =
        useState("overview");

    const [loading, setLoading] =
        useState(true);

    // Job recommendation state
    const [recommendations, setRecommendations] =
        useState([]);

    const [recommendationLoading, setRecommendationLoading] =
        useState(false);

    const [recommendationError, setRecommendationError] =
        useState("");

    // =========================================================
    // LOAD STUDENT DATA
    // =========================================================

    useEffect(() => {
        const loadStudentProfile = async () => {
            try {
                // Get the JWT token
                const token =
                    localStorage.getItem("token");

                if (!token) {
                    console.error(
                        "JWT token not found."
                    );

                    setLoading(false);
                    return;
                }

                // Get the basic student information
                const storedStudent =
                    localStorage.getItem("student");

                let basicStudent = null;

                if (storedStudent) {
                    try {
                        basicStudent =
                            JSON.parse(
                                storedStudent
                            );
                    } catch (error) {
                        console.error(
                            "Invalid student data in localStorage:",
                            error
                        );
                    }
                }

                // -------------------------------------------------
                // FETCH COMPLETE PROFILE FROM BACKEND
                // -------------------------------------------------

                const response = await fetch(
                    "http://127.0.0.1:5000/api/students/profile",
                    {
                        method: "GET",

                        headers: {
                            Authorization:
                                `Bearer ${token}`,

                            "Content-Type":
                                "application/json",
                        },
                    }
                );

                const data =
                    await response.json();

                console.log(
                    "COMPLETE STUDENT PROFILE:",
                    data
                );

                // -------------------------------------------------
                // HANDLE AUTH ERROR
                // -------------------------------------------------

                if (response.status === 401) {
                    console.error(
                        "JWT authentication failed:",
                        data
                    );

                    setStudent(
                        basicStudent
                    );

                    setLoading(false);
                    return;
                }

                // -------------------------------------------------
                // HANDLE OTHER ERRORS
                // -------------------------------------------------

                if (!response.ok) {
                    console.error(
                        "Profile API error:",
                        data
                    );

                    setStudent(
                        basicStudent
                    );

                    setLoading(false);
                    return;
                }

                // -------------------------------------------------
                // GET PROFILE FROM RESPONSE
                // -------------------------------------------------

                const completeStudent =
                    data?.student ||
                    data?.profile ||
                    data?.data ||
                    data;

                if (
                    completeStudent &&
                    typeof completeStudent ===
                    "object"
                ) {
                    // Save complete profile in React state
                    setStudent(
                        completeStudent
                    );

                    // Update localStorage too
                    localStorage.setItem(
                        "student",
                        JSON.stringify(
                            completeStudent
                        )
                    );

                    console.log(
                        "Updated student profile:",
                        completeStudent
                    );

                    console.log(
                        "Detected skills:",
                        completeStudent
                            ?.detected_skills
                    );
                } else {
                    setStudent(
                        basicStudent
                    );
                }

            } catch (error) {
                console.error(
                    "Unable to load complete student profile:",
                    error
                );

                // Fallback to existing localStorage data
                try {
                    const storedStudent =
                        localStorage.getItem(
                            "student"
                        );

                    if (storedStudent) {
                        setStudent(
                            JSON.parse(
                                storedStudent
                            )
                        );
                    }
                } catch (storageError) {
                    console.error(
                        "Unable to read stored student:",
                        storageError
                    );
                }
            } finally {
                setLoading(false);
            }
        };

        loadStudentProfile();
    }, []);

    // =========================================================
    // LOAD JOB RECOMMENDATIONS
    // =========================================================

    useEffect(() => {
        if (activeSection !== "recommendations") {
            return;
        }

        fetchRecommendations();
    }, [activeSection]);

    // =========================================================
    // FETCH JOB RECOMMENDATIONS
    // =========================================================

    const fetchRecommendations = async () => {
        setRecommendationLoading(true);
        setRecommendationError("");

        try {
            // -------------------------------------------------
            // GET JWT TOKEN
            // -------------------------------------------------

            const token =
                localStorage.getItem("token");

            if (!token) {
                setRecommendationError(
                    "Login token not found. Please login again."
                );

                setRecommendations([]);

                return;
            }

            // -------------------------------------------------
            // CALL BACKEND
            // -------------------------------------------------

            const response = await fetch(
                "http://127.0.0.1:5000/api/students/job-recommendations",
                {
                    method: "GET",

                    headers: {
                        Authorization:
                            `Bearer ${token}`,

                        "Content-Type":
                            "application/json",
                    },
                }
            );

            // -------------------------------------------------
            // READ RESPONSE
            // -------------------------------------------------

            let data = {};

            try {
                data = await response.json();
            } catch (jsonError) {
                console.error(
                    "Unable to parse API response:",
                    jsonError
                );
            }

            console.log(
                "JOB RECOMMENDATIONS RESPONSE:",
                data
            );

            // -------------------------------------------------
            // AUTHORIZATION ERROR
            // -------------------------------------------------

            if (response.status === 401) {
                setRecommendations([]);

                setRecommendationError(
                    data?.message ||
                    "Your login session has expired. Please login again."
                );

                return;
            }

            // -------------------------------------------------
            // OTHER API ERROR
            // -------------------------------------------------

            if (!response.ok) {
                setRecommendations([]);

                setRecommendationError(
                    data?.message ||
                    "Unable to load job recommendations."
                );

                return;
            }

            // -------------------------------------------------
            // SUCCESS
            // -------------------------------------------------

            if (
                data?.success &&
                Array.isArray(
                    data?.recommendations
                )
            ) {
                setRecommendations(
                    data.recommendations
                );

                setRecommendationError("");
            } else {
                setRecommendations([]);

                setRecommendationError(
                    data?.message ||
                    "No job recommendations were returned."
                );
            }

        } catch (error) {
            console.error(
                "Recommendation API error:",
                error
            );

            setRecommendations([]);

            setRecommendationError(
                "Unable to connect to the backend. Make sure Flask is running."
            );

        } finally {
            setRecommendationLoading(false);
        }
    };

    // =========================================================
    // LOGOUT
    // =========================================================

    const handleLogout = () => {
        if (onLogout) {
            onLogout();
        } else {
            localStorage.removeItem("token");
            localStorage.removeItem("student");

            window.location.reload();
        }
    };

    // =========================================================
    // LOADING
    // =========================================================

    if (loading) {
        return (
            <div
                style={{
                    minHeight: "100vh",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    background: "#f5f7ff",
                    fontFamily:
                        "Arial, sans-serif",
                }}
            >
                <h2>
                    Loading dashboard...
                </h2>
            </div>
        );
    }

    // =========================================================
    // STUDENT NAME
    // =========================================================

    const studentName =
        student?.full_name ||
        student?.personal?.full_name ||
        student?.name ||
        "Student";

    const firstName =
        studentName.split(" ")[0];

    // =========================================================
    // ACADEMIC DATA
    // =========================================================

    const academic =
        student?.academic || {};

    // =========================================================
    // SKILLS
    // =========================================================

    const skills =
        Array.isArray(student?.skills)
            ? student.skills
            : [];

    const detectedSkills =
        Array.isArray(
            student?.detected_skills?.all
        )
            ? student.detected_skills.all
            : [];

    // =========================================================
    // CERTIFICATIONS
    // =========================================================

    const certifications =
        Array.isArray(
            student?.certifications
        )
            ? student.certifications
            : [];

    // =========================================================
    // PROJECTS
    // =========================================================

    const projects =
        Array.isArray(student?.projects)
            ? student.projects
            : [];

    // =========================================================
    // CAREER
    // =========================================================

    const career =
        student?.career_preferences ||
        {};

    // =========================================================
    // PERSONAL DATA
    // =========================================================

    const personal =
        student?.personal || {};

    // =========================================================
    // DASHBOARD DATA
    // =========================================================

    const skillCount =
        skills.length > 0
            ? skills.length
            : detectedSkills.length;

    const projectCount =
        projects.length;

    const certificationCount =
        certifications.length;

    // =========================================================
    // NAVIGATION
    // =========================================================

    const navigation = [
        {
            id: "overview",
            label: "Overview",
            icon: "🏠",
        },
        {
            id: "profile",
            label: "My Profile",
            icon: "👤",
        },
        {
            id: "skills",
            label: "My Skills",
            icon: "💻",
        },
        {
            id: "projects",
            label: "Projects",
            icon: "🚀",
        },
        {
            id: "certifications",
            label: "Certifications",
            icon: "🏆",
        },
        {
            id: "career",
            label: "Career Goals",
            icon: "🎯",
        },
        {
            id: "recommendations",
            label: "Recommendations",
            icon: "✨",
        },
    ];

    // =========================================================
    // STYLES
    // =========================================================

    const pageStyle = {
        minHeight: "100vh",
        background:
            "linear-gradient(135deg,#f5f7ff,#eef2ff)",
        fontFamily:
            "Arial, Helvetica, sans-serif",
        color: "#1f2937",
    };

    const sidebarStyle = {
        position: "fixed",
        left: 0,
        top: 0,
        bottom: 0,
        width: "250px",
        background:
            "linear-gradient(180deg,#312e81,#4f46e5)",
        color: "white",
        padding: "25px 15px",
        boxSizing: "border-box",
        display: "flex",
        flexDirection: "column",
        zIndex: 10,
    };

    const mainStyle = {
        marginLeft: "250px",
        minHeight: "100vh",
        padding: "30px",
        boxSizing: "border-box",
    };

    const cardStyle = {
        background: "white",
        borderRadius: "18px",
        padding: "22px",
        boxShadow:
            "0 8px 25px rgba(31,41,55,0.08)",
    };

    const navButtonStyle = {
        width: "100%",
        border: "none",
        padding: "13px 15px",
        marginBottom: "7px",
        borderRadius: "10px",
        textAlign: "left",
        cursor: "pointer",
        fontSize: "14px",
        fontWeight: "600",
    };

    // =========================================================
    // RENDER
    // =========================================================

    return (
        <div style={pageStyle}>

            {/* =====================================================
                SIDEBAR
            ===================================================== */}

            <aside style={sidebarStyle}>

                {/* PROJECT TITLE */}

                <div
                    style={{
                        padding:
                            "5px 10px 25px",
                        borderBottom:
                            "1px solid rgba(255,255,255,0.2)",
                        marginBottom: "20px",
                    }}
                >
                    <h2
                        style={{
                            margin: 0,
                            fontSize: "20px",
                        }}
                    >
                        Skill Analyzer
                    </h2>

                    <p
                        style={{
                            margin:
                                "7px 0 0",
                            fontSize: "12px",
                            opacity: 0.8,
                            lineHeight: 1.5,
                        }}
                    >
                        Student Dashboard
                    </p>
                </div>

                {/* NAVIGATION */}

                <nav>
                    {navigation.map(
                        (item) => (
                            <button
                                key={item.id}
                                type="button"
                                onClick={() =>
                                    setActiveSection(
                                        item.id
                                    )
                                }
                                style={{
                                    ...navButtonStyle,
                                    background:
                                        activeSection ===
                                            item.id
                                            ? "rgba(255,255,255,0.2)"
                                            : "transparent",
                                    color: "white",
                                }}
                            >
                                <span
                                    style={{
                                        marginRight:
                                            "10px",
                                    }}
                                >
                                    {item.icon}
                                </span>

                                {item.label}
                            </button>
                        )
                    )}
                </nav>

                {/* SIDEBAR BOTTOM */}

                <div
                    style={{
                        marginTop: "auto",
                    }}
                >
                    <button
                        type="button"
                        onClick={handleLogout}
                        style={{
                            ...navButtonStyle,
                            background:
                                "rgba(239,68,68,0.9)",
                            color: "white",
                        }}
                    >
                        🚪 Logout
                    </button>
                </div>

            </aside>

            {/* =====================================================
                MAIN CONTENT
            ===================================================== */}

            <main style={mainStyle}>

                {/* ===================================================
                    TOP BAR
                =================================================== */}

                <div
                    style={{
                        display: "flex",
                        justifyContent:
                            "space-between",
                        alignItems:
                            "center",
                        marginBottom:
                            "30px",
                        gap: "20px",
                    }}
                >

                    <div>
                        <p
                            style={{
                                margin: 0,
                                color: "#6b7280",
                                fontSize: "14px",
                            }}
                        >
                            Welcome back 👋
                        </p>

                        <h1
                            style={{
                                margin:
                                    "5px 0 0",
                                fontSize: "30px",
                                color: "#111827",
                            }}
                        >
                            {firstName}
                        </h1>
                    </div>

                    <div
                        style={{
                            background:
                                "white",
                            padding:
                                "10px 16px",
                            borderRadius:
                                "12px",
                            boxShadow:
                                "0 5px 15px rgba(0,0,0,0.06)",
                            fontSize: "14px",
                            fontWeight:
                                "600",
                        }}
                    >
                        🎓{" "}
                        {student?.degree ||
                            personal?.degree ||
                            "Student"}
                    </div>

                </div>

                {/* ===================================================
                    OVERVIEW
                =================================================== */}

                {activeSection ===
                    "overview" && (
                        <>
                            {/* WELCOME CARD */}

                            <div
                                style={{
                                    ...cardStyle,
                                    background:
                                        "linear-gradient(135deg,#4f46e5,#7c3aed)",
                                    color: "white",
                                    marginBottom:
                                        "25px",
                                }}
                            >
                                <h2
                                    style={{
                                        marginTop: 0,
                                    }}
                                >
                                    Welcome to your
                                    Skill Dashboard
                                </h2>

                                <p
                                    style={{
                                        opacity: 0.9,
                                        lineHeight: 1.6,
                                        marginBottom: 0,
                                    }}
                                >
                                    Track your skills,
                                    academic progress,
                                    projects and
                                    career goals in
                                    one place.
                                </p>
                            </div>

                            {/* STAT CARDS */}

                            <div
                                style={{
                                    display:
                                        "grid",
                                    gridTemplateColumns:
                                        "repeat(auto-fit,minmax(180px,1fr))",
                                    gap: "18px",
                                    marginBottom:
                                        "25px",
                                }}
                            >

                                <StatCard
                                    icon="💻"
                                    title="Skills"
                                    value={skillCount}
                                />

                                <StatCard
                                    icon="🚀"
                                    title="Projects"
                                    value={projectCount}
                                />

                                <StatCard
                                    icon="🏆"
                                    title="Certifications"
                                    value={
                                        certificationCount
                                    }
                                />

                                <StatCard
                                    icon="🎯"
                                    title="Career Goal"
                                    value={
                                        career?.preferred_job_role ||
                                        "Not set"
                                    }
                                    small
                                />

                            </div>

                            {/* PROFILE + ACADEMIC */}

                            <div
                                style={{
                                    display:
                                        "grid",
                                    gridTemplateColumns:
                                        "repeat(auto-fit,minmax(300px,1fr))",
                                    gap: "20px",
                                }}
                            >

                                <div
                                    style={cardStyle}
                                >
                                    <h3>
                                        👤 Profile
                                    </h3>

                                    <InfoRow
                                        label="Name"
                                        value={
                                            studentName
                                        }
                                    />

                                    <InfoRow
                                        label="Email"
                                        value={
                                            student?.email ||
                                            personal?.email
                                        }
                                    />

                                    <InfoRow
                                        label="Register Number"
                                        value={
                                            student?.register_number ||
                                            personal?.register_number
                                        }
                                    />

                                    <InfoRow
                                        label="Department"
                                        value={
                                            student?.department ||
                                            personal?.department
                                        }
                                    />

                                    <InfoRow
                                        label="Year"
                                        value={
                                            student?.year_of_study ||
                                            personal?.year_of_study
                                        }
                                    />
                                </div>

                                <div
                                    style={cardStyle}
                                >
                                    <h3>
                                        📚 Academic
                                    </h3>

                                    <InfoRow
                                        label="College"
                                        value={
                                            academic?.college_name
                                        }
                                    />

                                    <InfoRow
                                        label="University"
                                        value={
                                            academic?.university
                                        }
                                    />

                                    <InfoRow
                                        label="CGPA"
                                        value={
                                            academic?.current_cgpa
                                        }
                                    />

                                    <InfoRow
                                        label="10th"
                                        value={
                                            academic?.tenth_percentage
                                        }
                                    />

                                    <InfoRow
                                        label="12th"
                                        value={
                                            academic?.twelfth_percentage
                                        }
                                    />
                                </div>

                            </div>
                        </>
                    )}

                {/* ===================================================
                    PROFILE
                =================================================== */}

                {activeSection ===
                    "profile" && (
                        <SectionCard
                            title="👤 My Profile"
                        >
                            <InfoRow
                                label="Full Name"
                                value={
                                    student?.full_name ||
                                    personal?.full_name
                                }
                            />

                            <InfoRow
                                label="Register Number"
                                value={
                                    student?.register_number ||
                                    personal?.register_number
                                }
                            />

                            <InfoRow
                                label="Roll Number"
                                value={
                                    student?.roll_number ||
                                    personal?.roll_number
                                }
                            />

                            <InfoRow
                                label="Email"
                                value={
                                    student?.email ||
                                    personal?.email
                                }
                            />

                            <InfoRow
                                label="Mobile"
                                value={
                                    student?.mobile ||
                                    personal?.mobile
                                }
                            />

                            <InfoRow
                                label="Gender"
                                value={
                                    student?.gender ||
                                    personal?.gender
                                }
                            />

                            <InfoRow
                                label="Date of Birth"
                                value={
                                    student?.date_of_birth ||
                                    personal?.date_of_birth
                                }
                            />

                            <InfoRow
                                label="Department"
                                value={
                                    student?.department ||
                                    personal?.department
                                }
                            />

                            <InfoRow
                                label="Degree"
                                value={
                                    student?.degree ||
                                    personal?.degree
                                }
                            />

                            <InfoRow
                                label="Year of Study"
                                value={
                                    student?.year_of_study ||
                                    personal?.year_of_study
                                }
                            />

                            <InfoRow
                                label="Section"
                                value={
                                    student?.section ||
                                    personal?.section
                                }
                            />

                            <InfoRow
                                label="Semester"
                                value={
                                    student?.semester ||
                                    personal?.semester
                                }
                            />

                            <h3
                                style={{
                                    marginTop:
                                        "30px",
                                }}
                            >
                                📚 Academic
                                Information
                            </h3>

                            <InfoRow
                                label="College"
                                value={
                                    academic?.college_name
                                }
                            />

                            <InfoRow
                                label="University"
                                value={
                                    academic?.university
                                }
                            />

                            <InfoRow
                                label="Branch"
                                value={
                                    academic?.branch
                                }
                            />

                            <InfoRow
                                label="Current CGPA"
                                value={
                                    academic?.current_cgpa
                                }
                            />

                            <InfoRow
                                label="10th Percentage"
                                value={
                                    academic?.tenth_percentage
                                }
                            />

                            <InfoRow
                                label="12th Percentage"
                                value={
                                    academic?.twelfth_percentage
                                }
                            />

                            <InfoRow
                                label="Number of Arrears"
                                value={
                                    academic?.number_of_arrears
                                }
                            />

                            <InfoRow
                                label="Academic Year"
                                value={
                                    academic?.academic_year
                                }
                            />

                            <InfoRow
                                label="Graduation Year"
                                value={
                                    academic?.graduation_year
                                }
                            />
                        </SectionCard>
                    )}

                {/* ===================================================
                    SKILLS
                =================================================== */}

                {activeSection ===
                    "skills" && (
                        <SectionCard
                            title="💻 My Skills"
                        >

                            {/* MANUAL SKILLS */}

                            <h3>
                                ✨ Added Skills
                            </h3>

                            {skills.length ===
                                0 ? (
                                <EmptyState
                                    text="No skills have been added yet."
                                />
                            ) : (
                                <div
                                    style={{
                                        display:
                                            "grid",
                                        gridTemplateColumns:
                                            "repeat(auto-fit,minmax(220px,1fr))",
                                        gap: "15px",
                                        marginBottom:
                                            "30px",
                                    }}
                                >
                                    {skills.map(
                                        (
                                            skill,
                                            index
                                        ) => (
                                            <div
                                                key={
                                                    index
                                                }
                                                style={{
                                                    padding:
                                                        "18px",
                                                    borderRadius:
                                                        "14px",
                                                    background:
                                                        "#f5f3ff",
                                                    border:
                                                        "1px solid #ddd6fe",
                                                }}
                                            >
                                                <h3
                                                    style={{
                                                        margin:
                                                            "0 0 8px",
                                                        color:
                                                            "#4f46e5",
                                                    }}
                                                >
                                                    {typeof skill ===
                                                        "string"
                                                        ? skill
                                                        : skill.name ||
                                                        "Skill"}
                                                </h3>

                                                {typeof skill !==
                                                    "string" && (
                                                        <>
                                                            <p
                                                                style={{
                                                                    margin:
                                                                        "4px 0",
                                                                    color:
                                                                        "#6b7280",
                                                                }}
                                                            >
                                                                Category:{" "}
                                                                {skill.category ||
                                                                    "N/A"}
                                                            </p>

                                                            <p
                                                                style={{
                                                                    margin:
                                                                        "4px 0",
                                                                    fontWeight:
                                                                        "700",
                                                                }}
                                                            >
                                                                Level:{" "}
                                                                {skill.proficiency ||
                                                                    "N/A"}
                                                            </p>
                                                        </>
                                                    )}
                                            </div>
                                        )
                                    )}
                                </div>
                            )}

                            {/* DETECTED SKILLS */}

                            <h3>
                                🤖 Skills Detected From Documents
                            </h3>

                            {detectedSkills.length ===
                                0 ? (
                                <EmptyState
                                    text="No skills have been detected from your uploaded documents."
                                />
                            ) : (
                                <SkillList
                                    title="Automatically Detected Skills"
                                    skills={
                                        detectedSkills
                                    }
                                    emptyText="No detected skills."
                                    background="#eff6ff"
                                    border="#bfdbfe"
                                    textColor="#1d4ed8"
                                />
                            )}
                        </SectionCard>
                    )}

                {/* ===================================================
                    PROJECTS
                =================================================== */}

                {activeSection ===
                    "projects" && (
                        <SectionCard
                            title="🚀 Projects & Experience"
                        >
                            {projects.length ===
                                0 ? (
                                <EmptyState
                                    text="No projects have been added yet."
                                />
                            ) : (
                                projects.map(
                                    (
                                        project,
                                        index
                                    ) => (
                                        <div
                                            key={
                                                index
                                            }
                                            style={{
                                                padding:
                                                    "20px",
                                                marginBottom:
                                                    "15px",
                                                background:
                                                    "#f8fafc",
                                                borderRadius:
                                                    "14px",
                                                border:
                                                    "1px solid #e5e7eb",
                                            }}
                                        >
                                            <h3>
                                                {project.title ||
                                                    "Project"}
                                            </h3>

                                            <InfoRow
                                                label="Role"
                                                value={
                                                    project.role
                                                }
                                            />

                                            <InfoRow
                                                label="Technologies"
                                                value={
                                                    Array.isArray(
                                                        project.technologies
                                                    )
                                                        ? project.technologies.join(
                                                            ", "
                                                        )
                                                        : project.technologies
                                                }
                                            />

                                            <InfoRow
                                                label="Duration"
                                                value={
                                                    project.duration
                                                }
                                            />

                                            <p
                                                style={{
                                                    lineHeight:
                                                        1.6,
                                                }}
                                            >
                                                <strong>
                                                    Description:
                                                </strong>{" "}
                                                {project.description ||
                                                    "Not provided"}
                                            </p>
                                        </div>
                                    )
                                )
                            )}
                        </SectionCard>
                    )}

                {/* ===================================================
                    CERTIFICATIONS
                =================================================== */}

                {activeSection ===
                    "certifications" && (
                        <SectionCard
                            title="🏆 Certifications"
                        >
                            {certifications.length ===
                                0 ? (
                                <EmptyState
                                    text="No certifications have been added yet."
                                />
                            ) : (
                                certifications.map(
                                    (
                                        certification,
                                        index
                                    ) => (
                                        <div
                                            key={
                                                index
                                            }
                                            style={{
                                                padding:
                                                    "20px",
                                                marginBottom:
                                                    "15px",
                                                background:
                                                    "#fffbeb",
                                                borderRadius:
                                                    "14px",
                                                border:
                                                    "1px solid #fde68a",
                                            }}
                                        >
                                            <h3>
                                                {
                                                    certification.name
                                                }
                                            </h3>

                                            <InfoRow
                                                label="Issuing Authority"
                                                value={
                                                    certification.issuing_authority
                                                }
                                            />

                                            <InfoRow
                                                label="Date"
                                                value={
                                                    certification.date
                                                }
                                            />

                                            <InfoRow
                                                label="Certificate ID"
                                                value={
                                                    certification.certificate_id
                                                }
                                            />

                                            {certification.file_name && (
                                                <p>
                                                    📎{" "}
                                                    {
                                                        certification.file_name
                                                    }
                                                </p>
                                            )}
                                        </div>
                                    )
                                )
                            )}
                        </SectionCard>
                    )}

                {/* ===================================================
                    CAREER
                =================================================== */}

                {activeSection ===
                    "career" && (
                        <SectionCard
                            title="🎯 Career Goals"
                        >
                            <InfoRow
                                label="Interested Domain"
                                value={
                                    career?.interested_domain
                                }
                            />

                            <InfoRow
                                label="Preferred Job Role"
                                value={
                                    career?.preferred_job_role
                                }
                            />

                            <InfoRow
                                label="Preferred Location"
                                value={
                                    career?.preferred_location
                                }
                            />

                            <InfoRow
                                label="Internship Preference"
                                value={
                                    career?.internship_preferences
                                }
                            />

                            <div
                                style={{
                                    marginTop:
                                        "25px",
                                }}
                            >
                                <h3>
                                    Career Goal
                                </h3>

                                <p
                                    style={{
                                        lineHeight:
                                            1.7,
                                        color:
                                            "#4b5563",
                                    }}
                                >
                                    {career?.career_goal ||
                                        "No career goal provided."}
                                </p>
                            </div>

                            <div
                                style={{
                                    marginTop:
                                        "25px",
                                }}
                            >
                                <h3>
                                    Learning Goal
                                </h3>

                                <p
                                    style={{
                                        lineHeight:
                                            1.7,
                                        color:
                                            "#4b5563",
                                    }}
                                >
                                    {career?.learning_goal ||
                                        "No learning goal provided."}
                                </p>
                            </div>
                        </SectionCard>
                    )}

                {/* ===================================================
                    RECOMMENDATIONS
                =================================================== */}

                {activeSection ===
                    "recommendations" && (
                        <SectionCard
                            title="✨ Personalized Recommendations"
                        >

                            {/* -------------------------------------------------
                                HEADER
                            ------------------------------------------------- */}

                            <div
                                style={{
                                    padding:
                                        "22px",
                                    background:
                                        "linear-gradient(135deg,#eef2ff,#f5f3ff)",
                                    borderRadius:
                                        "14px",
                                    marginBottom:
                                        "25px",
                                }}
                            >
                                <h3
                                    style={{
                                        marginTop: 0,
                                        color: "#312e81",
                                    }}
                                >
                                    🎯 Career Recommendation
                                </h3>

                                <p
                                    style={{
                                        lineHeight:
                                            1.6,
                                        marginBottom: 0,
                                    }}
                                >
                                    Your recommendations
                                    are calculated using
                                    your skills, academic
                                    eligibility, career
                                    preferences and job
                                    requirements.
                                </p>

                                {recommendations.length >
                                    0 && (
                                        <div
                                            style={{
                                                marginTop:
                                                    "15px",
                                                display:
                                                    "inline-block",
                                                padding:
                                                    "8px 13px",
                                                background:
                                                    "white",
                                                borderRadius:
                                                    "20px",
                                                color:
                                                    "#4338ca",
                                                fontWeight:
                                                    "700",
                                                fontSize:
                                                    "13px",
                                            }}
                                        >
                                            🎯{" "}
                                            {
                                                recommendations.length
                                            } suitable job
                                            {recommendations.length !==
                                                1
                                                ? "s"
                                                : ""}{" "}
                                            found
                                        </div>
                                    )}
                            </div>

                            {/* -------------------------------------------------
                                LEARNING RECOMMENDATION
                            ------------------------------------------------- */}

                            <div
                                style={{
                                    padding:
                                        "22px",
                                    background:
                                        "#f0fdf4",
                                    borderRadius:
                                        "14px",
                                    marginBottom:
                                        "25px",
                                }}
                            >
                                <h3
                                    style={{
                                        marginTop: 0,
                                        color: "#166534",
                                    }}
                                >
                                    📚 Learning Recommendation
                                </h3>

                                {recommendationLoading ? (
                                    <p>
                                        Analyzing your
                                        skills and job
                                        requirements...
                                    </p>
                                ) : recommendations.length ===
                                    0 ? (
                                    <p
                                        style={{
                                            lineHeight: 1.6,
                                        }}
                                    >
                                        Missing-skill
                                        recommendations
                                        will appear when
                                        suitable jobs are
                                        found.
                                    </p>
                                ) : (
                                    <LearningSummary
                                        recommendations={
                                            recommendations
                                        }
                                    />
                                )}
                            </div>

                            {/* -------------------------------------------------
                                JOB ROLE RECOMMENDATION
                            ------------------------------------------------- */}

                            <div
                                style={{
                                    padding:
                                        "22px",
                                    background:
                                        "#fff7ed",
                                    borderRadius:
                                        "14px",
                                }}
                            >
                                <div
                                    style={{
                                        display: "flex",
                                        justifyContent:
                                            "space-between",
                                        alignItems:
                                            "center",
                                        gap: "15px",
                                        flexWrap:
                                            "wrap",
                                        marginBottom:
                                            "20px",
                                    }}
                                >
                                    <h3
                                        style={{
                                            margin: 0,
                                            color:
                                                "#9a3412",
                                        }}
                                    >
                                        💼 Job Role
                                        Recommendation
                                    </h3>

                                    <button
                                        type="button"
                                        onClick={
                                            fetchRecommendations
                                        }
                                        disabled={
                                            recommendationLoading
                                        }
                                        style={{
                                            border:
                                                "none",
                                            background:
                                                recommendationLoading
                                                    ? "#fdba74"
                                                    : "#f97316",
                                            color:
                                                "white",
                                            padding:
                                                "10px 16px",
                                            borderRadius:
                                                "9px",
                                            cursor:
                                                recommendationLoading
                                                    ? "not-allowed"
                                                    : "pointer",
                                            fontWeight:
                                                "700",
                                        }}
                                    >
                                        {recommendationLoading
                                            ? "Loading..."
                                            : "🔄 Refresh"}
                                    </button>
                                </div>

                                {/* -------------------------------------------------
                                    LOADING
                                ------------------------------------------------- */}

                                {recommendationLoading && (
                                    <div
                                        style={{
                                            padding:
                                                "30px",
                                            textAlign:
                                                "center",
                                            background:
                                                "white",
                                            borderRadius:
                                                "12px",
                                        }}
                                    >
                                        <div
                                            style={{
                                                fontSize:
                                                    "35px",
                                                marginBottom:
                                                    "10px",
                                            }}
                                        >
                                            🔎
                                        </div>

                                        <h3>
                                            Finding the
                                            best jobs for
                                            you...
                                        </h3>

                                        <p
                                            style={{
                                                color:
                                                    "#6b7280",
                                            }}
                                        >
                                            Checking your
                                            eligibility,
                                            skills and
                                            career
                                            preferences.
                                        </p>
                                    </div>
                                )}

                                {/* -------------------------------------------------
                                    ERROR
                                ------------------------------------------------- */}

                                {!recommendationLoading &&
                                    recommendationError && (
                                        <div
                                            style={{
                                                padding:
                                                    "20px",
                                                background:
                                                    "#fef2f2",
                                                border:
                                                    "1px solid #fecaca",
                                                borderRadius:
                                                    "12px",
                                                color:
                                                    "#991b1b",
                                            }}
                                        >
                                            <h3
                                                style={{
                                                    marginTop: 0,
                                                }}
                                            >
                                                ⚠️ Unable to
                                                load
                                                recommendations
                                            </h3>

                                            <p
                                                style={{
                                                    lineHeight:
                                                        1.6,
                                                }}
                                            >
                                                {
                                                    recommendationError
                                                }
                                            </p>

                                            <button
                                                type="button"
                                                onClick={
                                                    fetchRecommendations
                                                }
                                                style={{
                                                    border:
                                                        "none",
                                                    background:
                                                        "#991b1b",
                                                    color:
                                                        "white",
                                                    padding:
                                                        "10px 15px",
                                                    borderRadius:
                                                        "8px",
                                                    cursor:
                                                        "pointer",
                                                    fontWeight:
                                                        "700",
                                                }}
                                            >
                                                🔄 Try Again
                                            </button>
                                        </div>
                                    )}

                                {/* -------------------------------------------------
                                    NO RESULTS
                                ------------------------------------------------- */}

                                {!recommendationLoading &&
                                    !recommendationError &&
                                    recommendations.length ===
                                    0 && (
                                        <div
                                            style={{
                                                padding:
                                                    "35px 20px",
                                                textAlign:
                                                    "center",
                                                background:
                                                    "white",
                                                borderRadius:
                                                    "12px",
                                            }}
                                        >
                                            <div
                                                style={{
                                                    fontSize:
                                                        "40px",
                                                    marginBottom:
                                                        "10px",
                                                }}
                                            >
                                                📭
                                            </div>

                                            <h3>
                                                No eligible
                                                jobs found
                                            </h3>

                                            <p
                                                style={{
                                                    color:
                                                        "#6b7280",
                                                    lineHeight:
                                                        1.6,
                                                }}
                                            >
                                                We could not
                                                find a job
                                                matching your
                                                current
                                                eligibility
                                                requirements.
                                            </p>

                                            <p
                                                style={{
                                                    color:
                                                        "#6b7280",
                                                }}
                                            >
                                                Try updating
                                                your skills,
                                                CGPA, career
                                                preferences
                                                or academic
                                                information.
                                            </p>
                                        </div>
                                    )}

                                {/* -------------------------------------------------
                                    RECOMMENDED JOBS
                                ------------------------------------------------- */}

                                {!recommendationLoading &&
                                    recommendations.length >
                                    0 && (
                                        <div
                                            style={{
                                                display:
                                                    "grid",
                                                gap:
                                                    "18px",
                                            }}
                                        >
                                            {recommendations.map(
                                                (
                                                    job,
                                                    index
                                                ) => (
                                                    <JobRecommendationCard
                                                        key={
                                                            job.job_id ||
                                                            index
                                                        }
                                                        job={
                                                            job
                                                        }
                                                        index={
                                                            index
                                                        }
                                                    />
                                                )
                                            )}
                                        </div>
                                    )}
                            </div>

                        </SectionCard>
                    )}

            </main>

        </div>
    );
}

// =============================================================
// JOB RECOMMENDATION CARD
// =============================================================

function JobRecommendationCard({
    job,
    index,
}) {
    const finalScore =
        Number(
            job?.final_score
        ) || 0;

    const skillMatch =
        Number(
            job?.skill_match_percentage
        ) || 0;

    const preferredSkillMatch =
        Number(
            job?.preferred_skill_match_percentage
        ) || 0;

    const preferenceMatch =
        Number(
            job?.preference_match_percentage
        ) || 0;

    const studentScore =
        job?.student_score !== null &&
            job?.student_score !== undefined
            ? Number(job.student_score)
            : null;

    const matchedSkills =
        Array.isArray(
            job?.matched_skills
        )
            ? job.matched_skills
            : [];

    const missingSkills =
        Array.isArray(
            job?.missing_skills
        )
            ? job.missing_skills
            : [];

    const preferredMissingSkills =
        Array.isArray(
            job?.preferred_missing_skills
        )
            ? job.preferred_missing_skills
            : [];

    const locations =
        Array.isArray(job?.location)
            ? job.location.join(", ")
            : job?.location ||
            "Location not specified";

    return (
        <div
            style={{
                background: "white",
                borderRadius: "16px",
                padding: "22px",
                border:
                    "1px solid #e5e7eb",
                boxShadow:
                    "0 5px 18px rgba(31,41,55,0.06)",
            }}
        >

            {/* JOB HEADER */}

            <div
                style={{
                    display: "flex",
                    justifyContent:
                        "space-between",
                    alignItems:
                        "flex-start",
                    gap: "20px",
                    flexWrap:
                        "wrap",
                }}
            >
                <div>
                    <div
                        style={{
                            display:
                                "inline-block",
                            padding:
                                "5px 10px",
                            borderRadius:
                                "20px",
                            background:
                                "#eef2ff",
                            color:
                                "#4338ca",
                            fontSize:
                                "12px",
                            fontWeight:
                                "700",
                            marginBottom:
                                "8px",
                        }}
                    >
                        #{index + 1} Recommended
                    </div>

                    <h2
                        style={{
                            margin:
                                "5px 0",
                            color:
                                "#111827",
                            fontSize:
                                "21px",
                        }}
                    >
                        {job?.job_role ||
                            "Job Role"}
                    </h2>

                    <h3
                        style={{
                            margin:
                                "5px 0 10px",
                            color:
                                "#4f46e5",
                            fontSize:
                                "16px",
                        }}
                    >
                        {job?.company_name ||
                            "Company"}
                    </h3>

                    <p
                        style={{
                            margin:
                                "5px 0",
                            color:
                                "#6b7280",
                        }}
                    >
                        📍 {locations}
                    </p>

                    {job?.employment_type && (
                        <p
                            style={{
                                margin:
                                    "5px 0",
                                color:
                                    "#6b7280",
                            }}
                        >
                            💼{" "}
                            {job.employment_type}
                        </p>
                    )}

                    {job?.experience_required && (
                        <p
                            style={{
                                margin:
                                    "5px 0",
                                color:
                                    "#6b7280",
                            }}
                        >
                            🧑‍💻 Experience:{" "}
                            {
                                job.experience_required
                            }
                        </p>
                    )}
                </div>

                {/* FINAL SCORE */}

                <div
                    style={{
                        minWidth:
                            "120px",
                        padding:
                            "15px",
                        borderRadius:
                            "14px",
                        background:
                            "#eef2ff",
                        textAlign:
                            "center",
                    }}
                >
                    <p
                        style={{
                            margin:
                                "0 0 5px",
                            fontSize:
                                "12px",
                            color:
                                "#6b7280",
                            fontWeight:
                                "700",
                        }}
                    >
                        MATCH SCORE
                    </p>

                    <div
                        style={{
                            fontSize:
                                "30px",
                            fontWeight:
                                "800",
                            color:
                                "#4f46e5",
                        }}
                    >
                        {finalScore}%
                    </div>
                </div>
            </div>

            {/* JOB DESCRIPTION */}

            {job?.job_description && (
                <p
                    style={{
                        marginTop:
                            "18px",
                        lineHeight:
                            "1.6",
                        color:
                            "#4b5563",
                    }}
                >
                    {job.job_description}
                </p>
            )}

            {/* MATCH BREAKDOWN */}

            <div
                style={{
                    display:
                        "grid",
                    gridTemplateColumns:
                        "repeat(auto-fit,minmax(150px,1fr))",
                    gap:
                        "12px",
                    marginTop:
                        "20px",
                }}
            >
                <ScoreBox
                    title="Required Skills"
                    value={
                        skillMatch
                    }
                />

                <ScoreBox
                    title="Preferred Skills"
                    value={
                        preferredSkillMatch
                    }
                />

                <ScoreBox
                    title="Career Preference"
                    value={
                        preferenceMatch
                    }
                />

                {studentScore !== null && (
                    <ScoreBox
                        title="Student Score"
                        value={
                            studentScore
                        }
                        suffix="/10"
                    />
                )}
            </div>

            {/* MATCHED SKILLS */}

            <SkillList
                title="✅ Matched Skills"
                skills={
                    matchedSkills
                }
                emptyText="No required skills matched yet."
                background="#f0fdf4"
                border="#bbf7d0"
                textColor="#166534"
            />

            {/* MISSING SKILLS */}

            <SkillList
                title="📚 Missing Required Skills"
                skills={
                    missingSkills
                }
                emptyText="You have all required skills."
                background="#fef2f2"
                border="#fecaca"
                textColor="#991b1b"
            />

            {/* PREFERRED MISSING SKILLS */}

            {preferredMissingSkills.length >
                0 && (
                    <SkillList
                        title="⭐ Missing Preferred Skills"
                        skills={
                            preferredMissingSkills
                        }
                        emptyText=""
                        background="#fffbeb"
                        border="#fde68a"
                        textColor="#92400e"
                    />
                )}

            {/* ELIGIBILITY */}

            <div
                style={{
                    marginTop:
                        "18px",
                    padding:
                        "14px",
                    borderRadius:
                        "10px",
                    background:
                        "#f0fdf4",
                    border:
                        "1px solid #bbf7d0",
                }}
            >
                <strong
                    style={{
                        color:
                            "#166534",
                    }}
                >
                    ✅ Eligibility:
                </strong>

                <span
                    style={{
                        marginLeft:
                            "8px",
                        color:
                            "#166534",
                    }}
                >
                    You meet the eligibility
                    requirements for this job.
                </span>
            </div>

            {/* SCORE REQUIREMENT */}

            {job?.minimum_score !== null &&
                job?.minimum_score !==
                undefined && (
                    <div
                        style={{
                            marginTop:
                                "12px",
                            padding:
                                "12px 14px",
                            borderRadius:
                                "10px",
                            background:
                                "#f8fafc",
                            border:
                                "1px solid #e5e7eb",
                            fontSize:
                                "13px",
                            color:
                                "#4b5563",
                        }}
                    >
                        🎯 Minimum required
                        student score:{" "}
                        <strong>
                            {
                                job.minimum_score
                            }
                        </strong>
                        /10
                    </div>
                )}

            {/* LEARNING RECOMMENDATIONS */}

            {Array.isArray(
                job?.learning_recommendations
            ) &&
                job.learning_recommendations
                    .length > 0 && (
                    <div
                        style={{
                            marginTop:
                                "18px",
                            padding:
                                "18px",
                            borderRadius:
                                "12px",
                            background:
                                "#f5f3ff",
                            border:
                                "1px solid #ddd6fe",
                        }}
                    >
                        <h4
                            style={{
                                marginTop: 0,
                                color:
                                    "#4338ca",
                            }}
                        >
                            🎓 Recommended Learning
                        </h4>

                        {job.learning_recommendations.map(
                            (
                                item,
                                itemIndex
                            ) => (
                                <div
                                    key={
                                        itemIndex
                                    }
                                    style={{
                                        padding:
                                            "9px 0",
                                        borderBottom:
                                            itemIndex <
                                                job
                                                    .learning_recommendations
                                                    .length -
                                                1
                                                ? "1px solid #e5e7eb"
                                                : "none",
                                    }}
                                >
                                    <strong>
                                        {item.skill}
                                    </strong>

                                    <span
                                        style={{
                                            marginLeft:
                                                "8px",
                                            fontSize:
                                                "12px",
                                            padding:
                                                "4px 8px",
                                            borderRadius:
                                                "12px",
                                            background:
                                                item.priority ===
                                                    "high"
                                                    ? "#fee2e2"
                                                    : "#fef3c7",
                                            color:
                                                item.priority ===
                                                    "high"
                                                    ? "#991b1b"
                                                    : "#92400e",
                                        }}
                                    >
                                        {
                                            item.priority
                                        }
                                    </span>

                                    <p
                                        style={{
                                            margin:
                                                "5px 0 0",
                                            fontSize:
                                                "13px",
                                            color:
                                                "#6b7280",
                                        }}
                                    >
                                        {
                                            item.reason
                                        }
                                    </p>
                                </div>
                            )
                        )}
                    </div>
                )}

            {/* APPLY BUTTON */}

            {job?.application_url && (
                <div
                    style={{
                        marginTop:
                            "20px",
                    }}
                >
                    <a
                        href={
                            job.application_url
                        }
                        target="_blank"
                        rel="noopener noreferrer"
                        style={{
                            display:
                                "inline-block",
                            textDecoration:
                                "none",
                            background:
                                "#4f46e5",
                            color:
                                "white",
                            padding:
                                "11px 20px",
                            borderRadius:
                                "9px",
                            fontWeight:
                                "700",
                        }}
                    >
                        🚀 View / Apply
                    </a>
                </div>
            )}
        </div>
    );
}

// =============================================================
// SCORE BOX
// =============================================================

function ScoreBox({
    title,
    value,
    suffix = "%",
}) {
    const numericValue =
        Number(value);

    return (
        <div
            style={{
                padding:
                    "14px",
                background:
                    "#f8fafc",
                borderRadius:
                    "10px",
                border:
                    "1px solid #e5e7eb",
            }}
        >
            <p
                style={{
                    margin:
                        "0 0 5px",
                    color:
                        "#6b7280",
                    fontSize:
                        "12px",
                }}
            >
                {title}
            </p>

            <strong
                style={{
                    color:
                        "#111827",
                    fontSize:
                        "20px",
                }}
            >
                {Number.isFinite(numericValue)
                    ? numericValue.toFixed(1)
                    : "0.0"}
                {suffix}
            </strong>
        </div>
    );
}

// =============================================================
// SKILL LIST
// =============================================================

function SkillList({
    title,
    skills,
    emptyText,
    background,
    border,
    textColor,
}) {
    return (
        <div
            style={{
                marginTop:
                    "18px",
                padding:
                    "18px",
                borderRadius:
                    "12px",
                background,
                border:
                    `1px solid ${border}`,
            }}
        >
            <h4
                style={{
                    marginTop: 0,
                    color: textColor,
                }}
            >
                {title}
            </h4>

            {skills.length === 0 ? (
                <p
                    style={{
                        marginBottom: 0,
                        color: "#6b7280",
                    }}
                >
                    {emptyText}
                </p>
            ) : (
                <div
                    style={{
                        display:
                            "flex",
                        flexWrap:
                            "wrap",
                        gap:
                            "8px",
                    }}
                >
                    {skills.map(
                        (
                            skill,
                            index
                        ) => (
                            <span
                                key={
                                    index
                                }
                                style={{
                                    padding:
                                        "7px 11px",
                                    borderRadius:
                                        "20px",
                                    background:
                                        "white",
                                    color:
                                        textColor,
                                    border:
                                        `1px solid ${border}`,
                                    fontSize:
                                        "13px",
                                    fontWeight:
                                        "600",
                                }}
                            >
                                {typeof skill ===
                                    "string"
                                    ? skill
                                    : skill?.name ||
                                    "Skill"}
                            </span>
                        )
                    )}
                </div>
            )}
        </div>
    );
}

// =============================================================
// LEARNING SUMMARY
// =============================================================

function LearningSummary({
    recommendations,
}) {
    const skillMap =
        new Map();

    recommendations.forEach(
        (job) => {
            const required =
                Array.isArray(
                    job?.missing_skills
                )
                    ? job.missing_skills
                    : [];

            const preferred =
                Array.isArray(
                    job?.preferred_missing_skills
                )
                    ? job.preferred_missing_skills
                    : [];

            required.forEach(
                (skill) => {
                    if (
                        !skillMap.has(
                            skill
                        )
                    ) {
                        skillMap.set(
                            skill,
                            "high"
                        );
                    }
                }
            );

            preferred.forEach(
                (skill) => {
                    if (
                        !skillMap.has(
                            skill
                        )
                    ) {
                        skillMap.set(
                            skill,
                            "medium"
                        );
                    }
                }
            );
        }
    );

    const missingSkills =
        Array.from(
            skillMap.entries()
        );

    if (
        missingSkills.length ===
        0
    ) {
        return (
            <p
                style={{
                    lineHeight: 1.6,
                    color:
                        "#166534",
                }}
            >
                🎉 Great! You currently
                have all the important
                skills required by your
                recommended jobs.
            </p>
        );
    }

    return (
        <div>
            <p
                style={{
                    lineHeight: 1.6,
                }}
            >
                Based on your recommended
                jobs, these are the skills
                you should consider learning:
            </p>

            <div
                style={{
                    display:
                        "flex",
                    flexWrap:
                        "wrap",
                    gap:
                        "10px",
                }}
            >
                {missingSkills.map(
                    (
                        [skill, priority],
                        index
                    ) => (
                        <span
                            key={
                                index
                            }
                            style={{
                                padding:
                                    "8px 13px",
                                borderRadius:
                                    "20px",
                                background:
                                    priority ===
                                        "high"
                                        ? "#fee2e2"
                                        : "#fef3c7",
                                color:
                                    priority ===
                                        "high"
                                        ? "#991b1b"
                                        : "#92400e",
                                fontWeight:
                                    "700",
                                fontSize:
                                    "13px",
                            }}
                        >
                            {skill}
                            {" · "}
                            {priority}
                        </span>
                    )
                )}
            </div>
        </div>
    );
}

// =============================================================
// STAT CARD
// =============================================================

function StatCard({
    icon,
    title,
    value,
    small = false,
}) {
    return (
        <div
            style={{
                background:
                    "white",
                borderRadius:
                    "16px",
                padding:
                    "20px",
                boxShadow:
                    "0 8px 25px rgba(31,41,55,0.07)",
            }}
        >
            <div
                style={{
                    fontSize:
                        "26px",
                    marginBottom:
                        "10px",
                }}
            >
                {icon}
            </div>

            <p
                style={{
                    margin:
                        "0 0 5px",
                    color:
                        "#6b7280",
                    fontSize:
                        "13px",
                }}
            >
                {title}
            </p>

            <h3
                style={{
                    margin: 0,
                    color:
                        "#111827",
                    fontSize:
                        small
                            ? "15px"
                            : "26px",
                }}
            >
                {value || "Not set"}
            </h3>
        </div>
    );
}

// =============================================================
// SECTION CARD
// =============================================================

function SectionCard({
    title,
    children,
}) {
    return (
        <div
            style={{
                background:
                    "white",
                borderRadius:
                    "18px",
                padding:
                    "28px",
                boxShadow:
                    "0 8px 25px rgba(31,41,55,0.08)",
            }}
        >
            <h2
                style={{
                    marginTop: 0,
                    marginBottom:
                        "25px",
                    color:
                        "#111827",
                }}
            >
                {title}
            </h2>

            {children}
        </div>
    );
}

// =============================================================
// INFO ROW
// =============================================================

function InfoRow({
    label,
    value,
}) {
    let displayValue =
        value;

    if (
        Array.isArray(value)
    ) {
        displayValue =
            value.join(", ");
    }

    if (
        typeof value ===
        "object" &&
        value !== null &&
        !Array.isArray(value)
    ) {
        displayValue =
            JSON.stringify(value);
    }

    return (
        <div
            style={{
                display:
                    "flex",
                justifyContent:
                    "space-between",
                gap: "20px",
                padding:
                    "10px 0",
                borderBottom:
                    "1px solid #f1f5f9",
            }}
        >
            <strong
                style={{
                    color:
                        "#4b5563",
                    fontSize:
                        "14px",
                }}
            >
                {label}
            </strong>

            <span
                style={{
                    color:
                        "#111827",
                    fontSize:
                        "14px",
                    textAlign:
                        "right",
                    maxWidth:
                        "60%",
                    wordBreak:
                        "break-word",
                }}
            >
                {displayValue ||
                    "Not provided"}
            </span>
        </div>
    );
}

// =============================================================
// EMPTY STATE
// =============================================================

function EmptyState({
    text,
}) {
    return (
        <div
            style={{
                padding:
                    "40px 20px",
                textAlign:
                    "center",
                color:
                    "#6b7280",
                background:
                    "#f8fafc",
                borderRadius:
                    "14px",
            }}
        >
            <div
                style={{
                    fontSize:
                        "35px",
                    marginBottom:
                        "10px",
                }}
            >
                📭
            </div>

            <p>{text}</p>
        </div>
    );
}

export default Dashboard;