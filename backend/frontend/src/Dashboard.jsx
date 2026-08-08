import { useEffect, useState } from "react";

function Dashboard({ onLogout }) {
    // =========================================================
    // STATE
    // =========================================================

    const [student, setStudent] = useState(null);
    const [activeSection, setActiveSection] =
        useState("overview");

    const [loading, setLoading] = useState(true);

    // =========================================================
    // LOAD STUDENT DATA
    // =========================================================

    useEffect(() => {
        try {
            const storedStudent =
                localStorage.getItem("student");

            if (storedStudent) {
                setStudent(
                    JSON.parse(storedStudent)
                );
            }
        } catch (error) {
            console.error(
                "Unable to load student data:",
                error
            );
        } finally {
            setLoading(false);
        }
    }, []);

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
        student?.name ||
        "Student";

    const firstName =
        studentName.split(" ")[0];

    // =========================================================
    // ACADEMIC DATA
    // =========================================================

    const academic =
        student?.academic || {};

    const skills =
        student?.skills || [];

    const certifications =
        student?.certifications || [];

    const projects =
        student?.projects || [];

    const career =
        student?.career_preferences ||
        {};

    // =========================================================
    // DASHBOARD DATA
    // =========================================================

    const skillCount =
        Array.isArray(skills)
            ? skills.length
            : 0;

    const projectCount =
        Array.isArray(projects)
            ? projects.length
            : 0;

    const certificationCount =
        Array.isArray(certifications)
            ? certifications.length
            : 0;

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
                                            student?.email
                                        }
                                    />

                                    <InfoRow
                                        label="Register Number"
                                        value={
                                            student?.register_number
                                        }
                                    />

                                    <InfoRow
                                        label="Department"
                                        value={
                                            student?.department
                                        }
                                    />

                                    <InfoRow
                                        label="Year"
                                        value={
                                            student?.year_of_study
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
                                    student?.full_name
                                }
                            />

                            <InfoRow
                                label="Register Number"
                                value={
                                    student?.register_number
                                }
                            />

                            <InfoRow
                                label="Roll Number"
                                value={
                                    student?.roll_number
                                }
                            />

                            <InfoRow
                                label="Email"
                                value={
                                    student?.email
                                }
                            />

                            <InfoRow
                                label="Mobile"
                                value={
                                    student?.mobile
                                }
                            />

                            <InfoRow
                                label="Gender"
                                value={
                                    student?.gender
                                }
                            />

                            <InfoRow
                                label="Date of Birth"
                                value={
                                    student?.date_of_birth
                                }
                            />

                            <InfoRow
                                label="Department"
                                value={
                                    student?.department
                                }
                            />

                            <InfoRow
                                label="Degree"
                                value={
                                    student?.degree
                                }
                            />

                            <InfoRow
                                label="Year of Study"
                                value={
                                    student?.year_of_study
                                }
                            />

                            <InfoRow
                                label="Section"
                                value={
                                    student?.section
                                }
                            />

                            <InfoRow
                                label="Semester"
                                value={
                                    student?.semester
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
                                                    {skill.name ||
                                                        "Skill"}
                                                </h3>

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
                                            </div>
                                        )
                                    )}
                                </div>
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
                                                    project.technologies
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
                            <div
                                style={{
                                    padding:
                                        "20px",
                                    background:
                                        "#eef2ff",
                                    borderRadius:
                                        "14px",
                                    marginBottom:
                                        "20px",
                                }}
                            >
                                <h3>
                                    🎯 Career Recommendation
                                </h3>

                                <p
                                    style={{
                                        lineHeight:
                                            1.6,
                                    }}
                                >
                                    Based on your skills,
                                    academic background
                                    and career preferences,
                                    personalized career
                                    recommendations will
                                    appear here.
                                </p>
                            </div>

                            <div
                                style={{
                                    padding:
                                        "20px",
                                    background:
                                        "#f0fdf4",
                                    borderRadius:
                                        "14px",
                                    marginBottom:
                                        "20px",
                                }}
                            >
                                <h3>
                                    📚 Learning Recommendation
                                </h3>

                                <p
                                    style={{
                                        lineHeight:
                                            1.6,
                                    }}
                                >
                                    Your learning roadmap
                                    will be generated based
                                    on your current skills
                                    and learning goals.
                                </p>
                            </div>

                            <div
                                style={{
                                    padding:
                                        "20px",
                                    background:
                                        "#fff7ed",
                                    borderRadius:
                                        "14px",
                                }}
                            >
                                <h3>
                                    💼 Job Role Recommendation
                                </h3>

                                <p
                                    style={{
                                        lineHeight:
                                            1.6,
                                    }}
                                >
                                    Job-role recommendations
                                    will be displayed here
                                    after the recommendation
                                    engine is connected.
                                </p>
                            </div>
                        </SectionCard>
                    )}

            </main>

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
                {value ||
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