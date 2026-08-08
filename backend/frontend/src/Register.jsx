import { useState } from "react";

function Register() {
  const [step, setStep] = useState(1);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");

  // =========================================================
  // FORM DATA
  // =========================================================

  const [formData, setFormData] = useState({
    // PERSONAL
    full_name: "",
    register_number: "",
    roll_number: "",
    email: "",
    mobile: "",
    gender: "",
    date_of_birth: "",
    department: "",
    degree: "",
    year_of_study: "",
    section: "",
    semester: "",
    password: "",
    confirm_password: "",

    // ACADEMIC
    college_name: "",
    university: "",
    branch: "",
    current_cgpa: "",
    tenth_percentage: "",
    twelfth_percentage: "",
    number_of_arrears: "",
    backlog_history: "",
    academic_year: "",
    graduation_year: "",

    // SKILLS
    skills: [],

    // CERTIFICATIONS
    has_certifications: "",
    certifications: [],

    // RESUME
    has_resume: "",
    resume_name: "",
    resume_file: null,

    // PROJECTS
    projects: [],

    // CAREER
    interested_domain: "",
    preferred_job_role: "",
    preferred_location: "",
    internship_preferences: "",
    career_goal: "",
    learning_goal: "",
  });

  // =========================================================
  // CURRENT SKILL
  // =========================================================

  const [currentSkill, setCurrentSkill] = useState({
    category: "",
    name: "",
    proficiency: "",
  });

  // =========================================================
  // CURRENT CERTIFICATION
  // =========================================================

  const [currentCertification, setCurrentCertification] =
    useState({
      name: "",
      issuing_authority: "",
      date: "",
      certificate_id: "",
      file: null,
      file_name: "",
    });

  // =========================================================
  // CURRENT PROJECT
  // =========================================================

  const [currentProject, setCurrentProject] = useState({
    title: "",
    role: "",
    technologies: "",
    duration: "",
    description: "",
  });

  // =========================================================
  // UPDATE FIELD
  // =========================================================

  const updateField = (field, value) => {
    setFormData((previous) => ({
      ...previous,
      [field]: value,
    }));
  };

  // =========================================================
  // NEXT STEP
  // =========================================================

  const nextStep = () => {
    setMessage("");

    if (step === 1) {
      if (
        !formData.full_name.trim() ||
        !formData.register_number.trim() ||
        !formData.email.trim() ||
        !formData.password ||
        !formData.confirm_password
      ) {
        setMessage(
          "Please fill all required personal information."
        );
        return;
      }

      if (
        formData.password !==
        formData.confirm_password
      ) {
        setMessage("Passwords do not match.");
        return;
      }
    }

    if (step === 4) {
      if (
        formData.has_certifications === "yes" &&
        formData.certifications.length === 0
      ) {
        setMessage(
          "Please add at least one certification or select No."
        );
        return;
      }
    }

    if (step === 5) {
      if (
        formData.has_resume === "yes" &&
        !formData.resume_file
      ) {
        setMessage("Please upload your resume.");
        return;
      }
    }

    if (step === 6) {
      if (formData.projects.length === 0) {
        setMessage(
          "Please add at least one project."
        );
        return;
      }
    }

    if (step < 8) {
      setStep(step + 1);
    }
  };

  // =========================================================
  // PREVIOUS STEP
  // =========================================================

  const previousStep = () => {
    setMessage("");

    if (step > 1) {
      setStep(step - 1);
    }
  };

  // =========================================================
  // SKILLS
  // =========================================================

  const addSkill = () => {
    if (
      !currentSkill.category ||
      !currentSkill.name.trim() ||
      !currentSkill.proficiency
    ) {
      setMessage(
        "Please select skill category, skill and proficiency."
      );
      return;
    }

    setFormData((previous) => ({
      ...previous,
      skills: [
        ...previous.skills,
        {
          ...currentSkill,
          name: currentSkill.name.trim(),
        },
      ],
    }));

    setCurrentSkill({
      category: "",
      name: "",
      proficiency: "",
    });

    setMessage("");
  };

  const removeSkill = (index) => {
    setFormData((previous) => ({
      ...previous,
      skills: previous.skills.filter(
        (_, skillIndex) =>
          skillIndex !== index
      ),
    }));
  };

  // =========================================================
  // CERTIFICATIONS
  // =========================================================

  const addCertification = () => {
    if (
      !currentCertification.name.trim() ||
      !currentCertification.issuing_authority.trim()
    ) {
      setMessage(
        "Please enter certification name and issuing authority."
      );
      return;
    }

    setFormData((previous) => ({
      ...previous,
      certifications: [
        ...previous.certifications,
        {
          name:
            currentCertification.name.trim(),

          issuing_authority:
            currentCertification.issuing_authority.trim(),

          date:
            currentCertification.date,

          certificate_id:
            currentCertification.certificate_id,

          file:
            currentCertification.file,

          file_name:
            currentCertification.file_name,
        },
      ],
    }));

    setCurrentCertification({
      name: "",
      issuing_authority: "",
      date: "",
      certificate_id: "",
      file: null,
      file_name: "",
    });

    setMessage("");
  };

  const removeCertification = (index) => {
    setFormData((previous) => ({
      ...previous,
      certifications:
        previous.certifications.filter(
          (_, certificationIndex) =>
            certificationIndex !== index
        ),
    }));
  };

  // =========================================================
  // PROJECTS
  // =========================================================

  const addProject = () => {
    if (
      !currentProject.title.trim() ||
      !currentProject.description.trim()
    ) {
      setMessage(
        "Please enter project title and description."
      );
      return;
    }

    setFormData((previous) => ({
      ...previous,
      projects: [
        ...previous.projects,
        {
          ...currentProject,
          title:
            currentProject.title.trim(),
          description:
            currentProject.description.trim(),
        },
      ],
    }));

    setCurrentProject({
      title: "",
      role: "",
      technologies: "",
      duration: "",
      description: "",
    });

    setMessage("");
  };

  const removeProject = (index) => {
    setFormData((previous) => ({
      ...previous,
      projects: previous.projects.filter(
        (_, projectIndex) =>
          projectIndex !== index
      ),
    }));
  };

  // =========================================================
  // RESUME FILE
  // =========================================================

  const handleResumeChange = (event) => {
    const file =
      event.target.files?.[0];

    if (!file) {
      updateField("resume_file", null);
      updateField("resume_name", "");
      return;
    }

    const allowedTypes = [
      "application/pdf",
      "application/msword",
      "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ];

    const extension = file.name
      .split(".")
      .pop()
      ?.toLowerCase();

    if (
      !allowedTypes.includes(file.type) &&
      !["pdf", "doc", "docx"].includes(
        extension
      )
    ) {
      setMessage(
        "Please upload a PDF, DOC or DOCX resume."
      );
      event.target.value = "";
      return;
    }

    if (file.size > 10 * 1024 * 1024) {
      setMessage(
        "Resume size must be less than 10 MB."
      );
      event.target.value = "";
      return;
    }

    updateField(
      "resume_file",
      file
    );

    updateField(
      "resume_name",
      file.name
    );

    setMessage("");
  };

  // =========================================================
  // CERTIFICATE FILE
  // =========================================================

  const handleCertificateChange = (
    event
  ) => {
    const file =
      event.target.files?.[0];

    if (!file) {
      setCurrentCertification(
        (previous) => ({
          ...previous,
          file: null,
          file_name: "",
        })
      );

      return;
    }

    const allowedTypes = [
      "application/pdf",
      "application/msword",
      "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ];

    const extension = file.name
      .split(".")
      .pop()
      ?.toLowerCase();

    if (
      !allowedTypes.includes(file.type) &&
      !["pdf", "doc", "docx"].includes(
        extension
      )
    ) {
      setMessage(
        "Please upload a PDF, DOC or DOCX certificate."
      );

      event.target.value = "";
      return;
    }

    if (file.size > 10 * 1024 * 1024) {
      setMessage(
        "Certificate size must be less than 10 MB."
      );

      event.target.value = "";
      return;
    }

    setCurrentCertification(
      (previous) => ({
        ...previous,
        file,
        file_name: file.name,
      })
    );

    setMessage("");
  };

  // =========================================================
  // SUBMIT REGISTRATION
  // =========================================================

  const handleSubmit = async () => {
    setMessage("");
    setLoading(true);

    try {
      // =====================================================
      // JSON PAYLOAD
      // =====================================================

      const payload = {
        // PERSONAL
        full_name:
          formData.full_name.trim(),

        register_number:
          formData.register_number.trim(),

        roll_number:
          formData.roll_number,

        email:
          formData.email.trim(),

        mobile:
          formData.mobile,

        gender:
          formData.gender,

        date_of_birth:
          formData.date_of_birth,

        department:
          formData.department,

        degree:
          formData.degree,

        year_of_study:
          formData.year_of_study,

        section:
          formData.section,

        semester:
          formData.semester,

        password:
          formData.password,

        // ACADEMIC
        academic: {
          college_name:
            formData.college_name,

          university:
            formData.university,

          branch:
            formData.branch,

          current_cgpa:
            formData.current_cgpa,

          tenth_percentage:
            formData.tenth_percentage,

          twelfth_percentage:
            formData.twelfth_percentage,

          number_of_arrears:
            formData.number_of_arrears,

          backlog_history:
            formData.backlog_history,

          academic_year:
            formData.academic_year,

          graduation_year:
            formData.graduation_year,
        },

        // SKILLS
        skills:
          formData.skills,

        // CERTIFICATIONS
        //
        // IMPORTANT:
        // File objects are NOT placed inside JSON.
        // Only certification information is sent here.
        certifications:
          formData.certifications.map(
            (certification) => ({
              name:
                certification.name,

              issuing_authority:
                certification.issuing_authority,

              date:
                certification.date,

              certificate_id:
                certification.certificate_id,

              file_name:
                certification.file_name,
            })
          ),

        // RESUME
        resume: {
          has_resume:
            formData.has_resume,

          resume_name:
            formData.resume_name,
        },

        // PROJECTS
        projects:
          formData.projects,

        // CAREER
        career_preferences: {
          interested_domain:
            formData.interested_domain,

          preferred_job_role:
            formData.preferred_job_role,

          preferred_location:
            formData.preferred_location,

          internship_preferences:
            formData.internship_preferences,

          career_goal:
            formData.career_goal,

          learning_goal:
            formData.learning_goal,
        },
      };

      // =====================================================
      // FORM DATA
      // =====================================================

      const uploadData =
        new FormData();

      // -----------------------------------------------------
      // Student JSON
      // -----------------------------------------------------

      uploadData.append(
        "student_data",
        JSON.stringify(payload)
      );

      // -----------------------------------------------------
      // Resume
      // -----------------------------------------------------

      if (formData.resume_file) {
        uploadData.append(
          "resume",
          formData.resume_file
        );
      }

      // -----------------------------------------------------
      // Certificates
      //
      // The backend uses:
      // request.files.getlist("certificates")
      // -----------------------------------------------------

      formData.certifications.forEach(
        (certification) => {
          if (certification.file) {
            uploadData.append(
              "certificates",
              certification.file
            );
          }
        }
      );

      // =====================================================
      // DEBUG
      // =====================================================

      console.log(
        "================================="
      );

      console.log(
        "STUDENT DATA:"
      );

      console.log(
        payload
      );

      console.log(
        "RESUME:",
        formData.resume_file
      );

      console.log(
        "CERTIFICATES:"
      );

      formData.certifications.forEach(
        (certification, index) => {
          console.log(
            index + 1,
            certification.file
          );
        }
      );

      console.log(
        "================================="
      );

      // =====================================================
      // SEND REQUEST
      // =====================================================

      const response =
        await fetch(
          "http://127.0.0.1:5000/api/students/register",
          {
            method: "POST",

            // IMPORTANT:
            // DO NOT set Content-Type manually.
            // Browser creates multipart/form-data boundary.
            body: uploadData,
          }
        );

      // =====================================================
      // READ RESPONSE
      // =====================================================

      const responseText =
        await response.text();

      let data;

      try {
        data =
          JSON.parse(responseText);
      } catch {
        console.error(
          "Backend returned non-JSON response:",
          responseText
        );

        throw new Error(
          "Backend returned an invalid response."
        );
      }

      console.log(
        "BACKEND RESPONSE:",
        data
      );

      // =====================================================
      // SUCCESS
      // =====================================================

      if (
        response.ok &&
        data.success
      ) {
        setMessage(
          "Student registered successfully!"
        );

        console.log(
          "Student ID:",
          data.student_id
        );

        console.log(
          "Resume uploaded:",
          data.resume_uploaded
        );

        console.log(
          "Certificates uploaded:",
          data.certificates_uploaded
        );

        console.log(
          "Resume text extracted:",
          data.resume_text_extracted
        );

        console.log(
          "Certificate texts extracted:",
          data.certificate_texts_extracted
        );

        // Optional:
        // Move to login page later.
      } else {
        setMessage(
          data.message ||
          "Registration failed."
        );
      }
    } catch (error) {
      console.error(
        "Registration error:",
        error
      );

      setMessage(
        error.message ||
        "Unable to connect to the backend server."
      );
    } finally {
      setLoading(false);
    }
  };

  // =========================================================
  // STYLES
  // =========================================================

  const inputStyle = {
    width: "100%",
    padding: "12px 14px",
    marginTop: "6px",
    marginBottom: "15px",
    border: "1px solid #e5e7eb",
    borderRadius: "10px",
    fontSize: "14px",
    outline: "none",
    boxSizing: "border-box",
  };

  const labelStyle = {
    display: "block",
    fontWeight: "600",
    fontSize: "13px",
    color: "#374151",
  };

  const sectionStyle = {
    background: "#ffffff",
    padding: "30px",
    borderRadius: "18px",
    boxShadow:
      "0 10px 30px rgba(31, 41, 55, 0.08)",
    width: "100%",
    maxWidth: "850px",
    boxSizing: "border-box",
  };

  const buttonStyle = {
    padding: "12px 22px",
    border: "none",
    borderRadius: "10px",
    background:
      "linear-gradient(135deg,#4f46e5,#7c3aed)",
    color: "white",
    fontWeight: "700",
    cursor: "pointer",
  };

  // =========================================================
  // RENDER
  // =========================================================

  return (
    <div
      style={{
        minHeight: "100vh",
        padding: "30px 15px",
        background: "#f5f7ff",
        boxSizing: "border-box",
      }}
    >
      <div style={sectionStyle}>

        {/* =================================================
            TITLE
        ================================================= */}

        <h1
          style={{
            textAlign: "center",
            color: "#4f46e5",
            marginBottom: "8px",
          }}
        >
          Student Registration
        </h1>

        <p
          style={{
            textAlign: "center",
            color: "#6b7280",
            marginBottom: "25px",
          }}
        >
          Skill Analyzer & Recommendation
          System
        </p>

        {/* =================================================
            PROGRESS
        ================================================= */}

        <div
          style={{
            display: "grid",
            gridTemplateColumns:
              "repeat(8, 1fr)",
            gap: "5px",
            marginBottom: "30px",
          }}
        >
          {[
            "Personal",
            "Academic",
            "Skills",
            "Certificates",
            "Resume",
            "Projects",
            "Career",
            "Review",
          ].map(
            (title, index) => (
              <div
                key={title}
                style={{
                  textAlign: "center",
                  fontSize: "10px",
                  fontWeight:
                    step === index + 1
                      ? "800"
                      : "500",
                  color:
                    step === index + 1
                      ? "#4f46e5"
                      : "#9ca3af",
                }}
              >
                <div
                  style={{
                    width: "28px",
                    height: "28px",
                    margin:
                      "0 auto 4px",
                    borderRadius: "50%",
                    display: "flex",
                    alignItems:
                      "center",
                    justifyContent:
                      "center",
                    background:
                      step >= index + 1
                        ? "#4f46e5"
                        : "#e5e7eb",
                    color:
                      step >= index + 1
                        ? "white"
                        : "#6b7280",
                    fontWeight: "700",
                  }}
                >
                  {index + 1}
                </div>

                {title}
              </div>
            )
          )}
        </div>

        {/* =================================================
            STEP 1
        ================================================= */}

        {step === 1 && (
          <div>
            <h2>
              👤 Personal Information
            </h2>

            <p
              style={{
                color: "#6b7280",
                margin:
                  "6px 0 20px",
              }}
            >
              Enter your basic student
              information.
            </p>

            <label style={labelStyle}>
              Full Name *
              <input
                style={inputStyle}
                value={
                  formData.full_name
                }
                onChange={(e) =>
                  updateField(
                    "full_name",
                    e.target.value
                  )
                }
                placeholder="Enter full name"
              />
            </label>

            <label style={labelStyle}>
              Register Number *
              <input
                style={inputStyle}
                value={
                  formData.register_number
                }
                onChange={(e) =>
                  updateField(
                    "register_number",
                    e.target.value
                  )
                }
                placeholder="Enter register number"
              />
            </label>

            <label style={labelStyle}>
              Roll Number
              <input
                style={inputStyle}
                value={
                  formData.roll_number
                }
                onChange={(e) =>
                  updateField(
                    "roll_number",
                    e.target.value
                  )
                }
                placeholder="Enter roll number"
              />
            </label>

            <label style={labelStyle}>
              Email Address *
              <input
                type="email"
                style={inputStyle}
                value={
                  formData.email
                }
                onChange={(e) =>
                  updateField(
                    "email",
                    e.target.value
                  )
                }
                placeholder="Enter email"
              />
            </label>

            <label style={labelStyle}>
              Mobile Number
              <input
                style={inputStyle}
                value={
                  formData.mobile
                }
                onChange={(e) =>
                  updateField(
                    "mobile",
                    e.target.value
                  )
                }
                placeholder="Enter mobile number"
              />
            </label>

            <label style={labelStyle}>
              Gender
              <select
                style={inputStyle}
                value={
                  formData.gender
                }
                onChange={(e) =>
                  updateField(
                    "gender",
                    e.target.value
                  )
                }
              >
                <option value="">
                  Select gender
                </option>
                <option>
                  Male
                </option>
                <option>
                  Female
                </option>
                <option>
                  Other
                </option>
              </select>
            </label>

            <label style={labelStyle}>
              Date of Birth
              <input
                type="date"
                style={inputStyle}
                value={
                  formData.date_of_birth
                }
                onChange={(e) =>
                  updateField(
                    "date_of_birth",
                    e.target.value
                  )
                }
              />
            </label>

            <label style={labelStyle}>
              Department
              <input
                style={inputStyle}
                value={
                  formData.department
                }
                onChange={(e) =>
                  updateField(
                    "department",
                    e.target.value
                  )
                }
                placeholder="Computer Science & Engineering"
              />
            </label>

            <label style={labelStyle}>
              Degree
              <input
                style={inputStyle}
                value={
                  formData.degree
                }
                onChange={(e) =>
                  updateField(
                    "degree",
                    e.target.value
                  )
                }
                placeholder="B.E / B.Tech"
              />
            </label>

            <label style={labelStyle}>
              Year of Study
              <select
                style={inputStyle}
                value={
                  formData.year_of_study
                }
                onChange={(e) =>
                  updateField(
                    "year_of_study",
                    e.target.value
                  )
                }
              >
                <option value="">
                  Select year
                </option>
                <option>
                  1st Year
                </option>
                <option>
                  2nd Year
                </option>
                <option>
                  3rd Year
                </option>
                <option>
                  4th Year
                </option>
              </select>
            </label>

            <label style={labelStyle}>
              Section
              <input
                style={inputStyle}
                value={
                  formData.section
                }
                onChange={(e) =>
                  updateField(
                    "section",
                    e.target.value
                  )
                }
                placeholder="A"
              />
            </label>

            <label style={labelStyle}>
              Semester
              <input
                style={inputStyle}
                value={
                  formData.semester
                }
                onChange={(e) =>
                  updateField(
                    "semester",
                    e.target.value
                  )
                }
                placeholder="6"
              />
            </label>

            <label style={labelStyle}>
              Password *
              <input
                type="password"
                style={inputStyle}
                value={
                  formData.password
                }
                onChange={(e) =>
                  updateField(
                    "password",
                    e.target.value
                  )
                }
                placeholder="Create password"
              />
            </label>

            <label style={labelStyle}>
              Confirm Password *
              <input
                type="password"
                style={inputStyle}
                value={
                  formData.confirm_password
                }
                onChange={(e) =>
                  updateField(
                    "confirm_password",
                    e.target.value
                  )
                }
                placeholder="Confirm password"
              />
            </label>
          </div>
        )}

        {/* =================================================
            STEP 2
        ================================================= */}

        {step === 2 && (
          <div>
            <h2>
              📚 Academic Details
            </h2>

            <label style={labelStyle}>
              College Name
              <input
                style={inputStyle}
                value={
                  formData.college_name
                }
                onChange={(e) =>
                  updateField(
                    "college_name",
                    e.target.value
                  )
                }
              />
            </label>

            <label style={labelStyle}>
              University
              <input
                style={inputStyle}
                value={
                  formData.university
                }
                onChange={(e) =>
                  updateField(
                    "university",
                    e.target.value
                  )
                }
              />
            </label>

            <label style={labelStyle}>
              Branch
              <input
                style={inputStyle}
                value={
                  formData.branch
                }
                onChange={(e) =>
                  updateField(
                    "branch",
                    e.target.value
                  )
                }
              />
            </label>

            <label style={labelStyle}>
              Current CGPA
              <input
                type="number"
                min="0"
                max="10"
                step="0.01"
                style={inputStyle}
                value={
                  formData.current_cgpa
                }
                onChange={(e) =>
                  updateField(
                    "current_cgpa",
                    e.target.value
                  )
                }
                placeholder="Example: 8.25"
              />
            </label>

            <label style={labelStyle}>
              10th Percentage
              <input
                type="number"
                min="0"
                max="100"
                style={inputStyle}
                value={
                  formData.tenth_percentage
                }
                onChange={(e) =>
                  updateField(
                    "tenth_percentage",
                    e.target.value
                  )
                }
              />
            </label>

            <label style={labelStyle}>
              12th Percentage
              <input
                type="number"
                min="0"
                max="100"
                style={inputStyle}
                value={
                  formData.twelfth_percentage
                }
                onChange={(e) =>
                  updateField(
                    "twelfth_percentage",
                    e.target.value
                  )
                }
              />
            </label>

            <label style={labelStyle}>
              Number of Arrears
              <input
                type="number"
                min="0"
                style={inputStyle}
                value={
                  formData.number_of_arrears
                }
                onChange={(e) =>
                  updateField(
                    "number_of_arrears",
                    e.target.value
                  )
                }
              />
            </label>

            <label style={labelStyle}>
              Backlog History
              <textarea
                style={inputStyle}
                value={
                  formData.backlog_history
                }
                onChange={(e) =>
                  updateField(
                    "backlog_history",
                    e.target.value
                  )
                }
                placeholder="Describe backlog history if any"
              />
            </label>

            <label style={labelStyle}>
              Academic Year
              <input
                style={inputStyle}
                value={
                  formData.academic_year
                }
                onChange={(e) =>
                  updateField(
                    "academic_year",
                    e.target.value
                  )
                }
                placeholder="2026-2027"
              />
            </label>

            <label style={labelStyle}>
              Graduation Year
              <input
                type="number"
                style={inputStyle}
                value={
                  formData.graduation_year
                }
                onChange={(e) =>
                  updateField(
                    "graduation_year",
                    e.target.value
                  )
                }
              />
            </label>
          </div>
        )}

        {/* =================================================
            STEP 3
        ================================================= */}

        {step === 3 && (
          <div>
            <h2>
              💻 Skills & Proficiency
            </h2>

            <select
              style={inputStyle}
              value={
                currentSkill.category
              }
              onChange={(e) =>
                setCurrentSkill({
                  ...currentSkill,
                  category:
                    e.target.value,
                })
              }
            >
              <option value="">
                Select category
              </option>
              <option>
                Programming
              </option>
              <option>
                Framework
              </option>
              <option>
                Database
              </option>
              <option>
                Cloud
              </option>
              <option>
                Operating System
              </option>
              <option>
                Tool
              </option>
            </select>

            <input
              style={inputStyle}
              placeholder="Skill name - Python, React, MongoDB..."
              value={
                currentSkill.name
              }
              onChange={(e) =>
                setCurrentSkill({
                  ...currentSkill,
                  name:
                    e.target.value,
                })
              }
            />

            <select
              style={inputStyle}
              value={
                currentSkill.proficiency
              }
              onChange={(e) =>
                setCurrentSkill({
                  ...currentSkill,
                  proficiency:
                    e.target.value,
                })
              }
            >
              <option value="">
                Select proficiency
              </option>
              <option>
                Beginner
              </option>
              <option>
                Intermediate
              </option>
              <option>
                Advanced
              </option>
              <option>
                Expert
              </option>
            </select>

            <button
              type="button"
              style={buttonStyle}
              onClick={addSkill}
            >
              + Add Skill
            </button>

            {formData.skills.map(
              (skill, index) => (
                <div
                  key={index}
                  style={{
                    marginTop: "12px",
                    padding: "14px",
                    background:
                      "#f8fafc",
                    borderRadius:
                      "10px",
                    display: "flex",
                    justifyContent:
                      "space-between",
                    alignItems:
                      "center",
                  }}
                >
                  <span>
                    <strong>
                      {skill.name}
                    </strong>{" "}
                    —{" "}
                    {skill.category}{" "}
                    —{" "}
                    {
                      skill.proficiency
                    }
                  </span>

                  <button
                    type="button"
                    onClick={() =>
                      removeSkill(
                        index
                      )
                    }
                  >
                    Remove
                  </button>
                </div>
              )
            )}
          </div>
        )}

        {/* =================================================
            STEP 4 - CERTIFICATIONS
        ================================================= */}

        {step === 4 && (
          <div>
            <h2>
              🏆 Certifications
            </h2>

            <label style={labelStyle}>
              Do you have certifications?
            </label>

            <select
              style={inputStyle}
              value={
                formData.has_certifications
              }
              onChange={(e) =>
                updateField(
                  "has_certifications",
                  e.target.value
                )
              }
            >
              <option value="">
                Select
              </option>

              <option value="yes">
                Yes
              </option>

              <option value="no">
                No
              </option>
            </select>

            {formData.has_certifications ===
              "yes" && (
                <>
                  <input
                    style={inputStyle}
                    placeholder="Certification name"
                    value={
                      currentCertification.name
                    }
                    onChange={(e) =>
                      setCurrentCertification(
                        {
                          ...currentCertification,
                          name:
                            e.target.value,
                        }
                      )
                    }
                  />

                  <input
                    style={inputStyle}
                    placeholder="Issuing authority"
                    value={
                      currentCertification.issuing_authority
                    }
                    onChange={(e) =>
                      setCurrentCertification(
                        {
                          ...currentCertification,
                          issuing_authority:
                            e.target.value,
                        }
                      )
                    }
                  />

                  <input
                    type="date"
                    style={inputStyle}
                    value={
                      currentCertification.date
                    }
                    onChange={(e) =>
                      setCurrentCertification(
                        {
                          ...currentCertification,
                          date:
                            e.target.value,
                        }
                      )
                    }
                  />

                  <input
                    style={inputStyle}
                    placeholder="Certificate ID"
                    value={
                      currentCertification.certificate_id
                    }
                    onChange={(e) =>
                      setCurrentCertification(
                        {
                          ...currentCertification,
                          certificate_id:
                            e.target.value,
                        }
                      )
                    }
                  />

                  {/* CERTIFICATE FILE */}

                  <label style={labelStyle}>
                    Upload Certificate

                    <input
                      type="file"
                      accept=".pdf,.doc,.docx"
                      style={inputStyle}
                      onChange={
                        handleCertificateChange
                      }
                    />
                  </label>

                  {currentCertification.file_name && (
                    <p
                      style={{
                        color:
                          "#16a34a",
                        fontSize:
                          "13px",
                      }}
                    >
                      Selected:{" "}
                      {
                        currentCertification.file_name
                      }
                    </p>
                  )}

                  <button
                    type="button"
                    style={buttonStyle}
                    onClick={
                      addCertification
                    }
                  >
                    + Add Certification
                  </button>

                  {formData.certifications.map(
                    (
                      certification,
                      index
                    ) => (
                      <div
                        key={index}
                        style={{
                          marginTop:
                            "12px",
                          padding:
                            "14px",
                          background:
                            "#f8fafc",
                          borderRadius:
                            "10px",
                        }}
                      >
                        <strong>
                          {
                            certification.name
                          }
                        </strong>

                        <p>
                          {
                            certification.issuing_authority
                          }
                        </p>

                        {certification.file_name && (
                          <p
                            style={{
                              color:
                                "#16a34a",
                              fontSize:
                                "13px",
                            }}
                          >
                            📎{" "}
                            {
                              certification.file_name
                            }
                          </p>
                        )}

                        <button
                          type="button"
                          onClick={() =>
                            removeCertification(
                              index
                            )
                          }
                        >
                          Remove
                        </button>
                      </div>
                    )
                  )}
                </>
              )}
          </div>
        )}

        {/* =================================================
            STEP 5 - RESUME
        ================================================= */}

        {step === 5 && (
          <div>
            <h2>
              📄 Resume
            </h2>

            <label style={labelStyle}>
              Do you have a resume?
            </label>

            <select
              style={inputStyle}
              value={
                formData.has_resume
              }
              onChange={(e) =>
                updateField(
                  "has_resume",
                  e.target.value
                )
              }
            >
              <option value="">
                Select
              </option>

              <option value="yes">
                Yes
              </option>

              <option value="no">
                No
              </option>
            </select>

            {formData.has_resume ===
              "yes" && (
                <>
                  <label
                    style={labelStyle}
                  >
                    Upload Resume

                    <input
                      type="file"
                      accept=".pdf,.doc,.docx"
                      style={inputStyle}
                      onChange={
                        handleResumeChange
                      }
                    />
                  </label>

                  {formData.resume_name && (
                    <p
                      style={{
                        color:
                          "#16a34a",
                        marginBottom:
                          "15px",
                      }}
                    >
                      Selected:{" "}
                      {
                        formData.resume_name
                      }
                    </p>
                  )}
                </>
              )}

            <p
              style={{
                color: "#6b7280",
                fontSize: "13px",
                marginTop: "15px",
              }}
            >
              PDF, DOC and DOCX files up to
              10 MB are supported.
            </p>
          </div>
        )}

        {/* =================================================
            STEP 6 - PROJECTS
        ================================================= */}

        {step === 6 && (
          <div>
            <h2>
              🚀 Projects & Experience
            </h2>

            <input
              style={inputStyle}
              placeholder="Project title"
              value={
                currentProject.title
              }
              onChange={(e) =>
                setCurrentProject({
                  ...currentProject,
                  title:
                    e.target.value,
                })
              }
            />

            <input
              style={inputStyle}
              placeholder="Your role"
              value={
                currentProject.role
              }
              onChange={(e) =>
                setCurrentProject({
                  ...currentProject,
                  role:
                    e.target.value,
                })
              }
            />

            <input
              style={inputStyle}
              placeholder="Technologies used"
              value={
                currentProject.technologies
              }
              onChange={(e) =>
                setCurrentProject({
                  ...currentProject,
                  technologies:
                    e.target.value,
                })
              }
            />

            <input
              style={inputStyle}
              placeholder="Duration"
              value={
                currentProject.duration
              }
              onChange={(e) =>
                setCurrentProject({
                  ...currentProject,
                  duration:
                    e.target.value,
                })
              }
            />

            <textarea
              style={inputStyle}
              placeholder="Project description"
              value={
                currentProject.description
              }
              onChange={(e) =>
                setCurrentProject({
                  ...currentProject,
                  description:
                    e.target.value,
                })
              }
            />

            <button
              type="button"
              style={buttonStyle}
              onClick={addProject}
            >
              + Add Project
            </button>

            {formData.projects.map(
              (project, index) => (
                <div
                  key={index}
                  style={{
                    marginTop: "15px",
                    padding: "16px",
                    background:
                      "#f8fafc",
                    borderRadius:
                      "12px",
                  }}
                >
                  <strong>
                    {project.title}
                  </strong>

                  <p>
                    {
                      project.description
                    }
                  </p>

                  <button
                    type="button"
                    onClick={() =>
                      removeProject(
                        index
                      )
                    }
                  >
                    Remove
                  </button>
                </div>
              )
            )}
          </div>
        )}

        {/* =================================================
            STEP 7 - CAREER
        ================================================= */}

        {step === 7 && (
          <div>
            <h2>
              🎯 Career Preferences
            </h2>

            <label style={labelStyle}>
              Interested Domain

              <select
                style={inputStyle}
                value={
                  formData.interested_domain
                }
                onChange={(e) =>
                  updateField(
                    "interested_domain",
                    e.target.value
                  )
                }
              >
                <option value="">
                  Select domain
                </option>

                <option>
                  Artificial Intelligence
                </option>

                <option>
                  Machine Learning
                </option>

                <option>
                  Data Science
                </option>

                <option>
                  Web Development
                </option>

                <option>
                  App Development
                </option>

                <option>
                  Cybersecurity
                </option>

                <option>
                  Cloud Computing
                </option>

                <option>
                  DevOps
                </option>

                <option>
                  Networking
                </option>

                <option>
                  Embedded Systems / IoT
                </option>

                <option>
                  GPU Computing / CUDA
                </option>

                <option>
                  Software Development
                </option>

                <option>
                  Other
                </option>
              </select>
            </label>

            <label style={labelStyle}>
              Preferred Job Role

              <input
                style={inputStyle}
                value={
                  formData.preferred_job_role
                }
                onChange={(e) =>
                  updateField(
                    "preferred_job_role",
                    e.target.value
                  )
                }
                placeholder="Example: Software Developer"
              />
            </label>

            <label style={labelStyle}>
              Preferred Location

              <input
                style={inputStyle}
                value={
                  formData.preferred_location
                }
                onChange={(e) =>
                  updateField(
                    "preferred_location",
                    e.target.value
                  )
                }
                placeholder="Example: Bangalore / Remote"
              />
            </label>

            <label style={labelStyle}>
              Internship Preference

              <select
                style={inputStyle}
                value={
                  formData.internship_preferences
                }
                onChange={(e) =>
                  updateField(
                    "internship_preferences",
                    e.target.value
                  )
                }
              >
                <option value="">
                  Select
                </option>

                <option>
                  Looking for internship
                </option>

                <option>
                  Not currently looking
                </option>
              </select>
            </label>

            <label style={labelStyle}>
              Career Goal

              <textarea
                style={inputStyle}
                value={
                  formData.career_goal
                }
                onChange={(e) =>
                  updateField(
                    "career_goal",
                    e.target.value
                  )
                }
                placeholder="What career do you want to pursue?"
              />
            </label>

            <label style={labelStyle}>
              Learning Goal

              <textarea
                style={inputStyle}
                value={
                  formData.learning_goal
                }
                onChange={(e) =>
                  updateField(
                    "learning_goal",
                    e.target.value
                  )
                }
                placeholder="What skills do you want to learn?"
              />
            </label>
          </div>
        )}

        {/* =================================================
            STEP 8 - REVIEW
        ================================================= */}

        {step === 8 && (
          <div>
            <h2>
              ✅ Review & Submit
            </h2>

            <p
              style={{
                color: "#6b7280",
                marginBottom:
                  "20px",
              }}
            >
              Please review your
              information before
              submitting.
            </p>

            <ReviewSection
              title="Personal Information"
              data={{
                "Full Name":
                  formData.full_name,

                "Register Number":
                  formData.register_number,

                "Roll Number":
                  formData.roll_number,

                Email:
                  formData.email,

                Mobile:
                  formData.mobile,

                Gender:
                  formData.gender,

                "Date of Birth":
                  formData.date_of_birth,

                Department:
                  formData.department,

                Degree:
                  formData.degree,

                "Year of Study":
                  formData.year_of_study,

                Section:
                  formData.section,

                Semester:
                  formData.semester,
              }}
            />

            <ReviewSection
              title="Academic Details"
              data={{
                College:
                  formData.college_name,

                University:
                  formData.university,

                Branch:
                  formData.branch,

                CGPA:
                  formData.current_cgpa,

                "10th Percentage":
                  formData.tenth_percentage,

                "12th Percentage":
                  formData.twelfth_percentage,

                Arrears:
                  formData.number_of_arrears,

                "Backlog History":
                  formData.backlog_history,

                "Academic Year":
                  formData.academic_year,

                "Graduation Year":
                  formData.graduation_year,
              }}
            />

            {/* SKILLS */}

            <div
              style={{
                marginTop: "20px",
                padding: "18px",
                background:
                  "#f8fafc",
                borderRadius:
                  "12px",
              }}
            >
              <h3>
                💻 Skills
              </h3>

              {formData.skills.length ===
                0 ? (
                <p>
                  No skills added.
                </p>
              ) : (
                formData.skills.map(
                  (
                    skill,
                    index
                  ) => (
                    <p key={index}>
                      <strong>
                        {
                          skill.name
                        }
                      </strong>{" "}
                      —{" "}
                      {
                        skill.category
                      }{" "}
                      —{" "}
                      {
                        skill.proficiency
                      }
                    </p>
                  )
                )
              )}
            </div>

            {/* CERTIFICATIONS */}

            <div
              style={{
                marginTop: "20px",
                padding: "18px",
                background:
                  "#f8fafc",
                borderRadius:
                  "12px",
              }}
            >
              <h3>
                🏆 Certifications
              </h3>

              {formData.has_certifications !==
                "yes" ? (
                <p>
                  No certifications
                </p>
              ) : (
                formData.certifications.map(
                  (
                    certification,
                    index
                  ) => (
                    <div
                      key={index}
                      style={{
                        marginBottom:
                          "12px",
                      }}
                    >
                      <strong>
                        {
                          certification.name
                        }
                      </strong>

                      <p>
                        {
                          certification.issuing_authority
                        }
                      </p>

                      {certification.file_name && (
                        <p
                          style={{
                            color:
                              "#16a34a",
                          }}
                        >
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
            </div>

            {/* RESUME */}

            <div
              style={{
                marginTop: "20px",
                padding: "18px",
                background:
                  "#f8fafc",
                borderRadius:
                  "12px",
              }}
            >
              <h3>
                📄 Resume
              </h3>

              <p>
                {formData.has_resume ===
                  "yes"
                  ? formData.resume_name ||
                  "Resume selected"
                  : "No resume"}
              </p>
            </div>

            {/* PROJECTS */}

            <div
              style={{
                marginTop: "20px",
                padding: "18px",
                background:
                  "#f8fafc",
                borderRadius:
                  "12px",
              }}
            >
              <h3>
                🚀 Projects
              </h3>

              <p>
                {
                  formData.projects.length
                }{" "}
                project(s)
              </p>

              {formData.projects.map(
                (
                  project,
                  index
                ) => (
                  <p key={index}>
                    <strong>
                      {
                        project.title
                      }
                    </strong>{" "}
                    —{" "}
                    {
                      project.role
                    }
                  </p>
                )
              )}
            </div>

            {/* CAREER */}

            <ReviewSection
              title="Career Preferences"
              data={{
                "Interested Domain":
                  formData.interested_domain,

                "Preferred Job Role":
                  formData.preferred_job_role,

                "Preferred Location":
                  formData.preferred_location,

                Internship:
                  formData.internship_preferences,

                "Career Goal":
                  formData.career_goal,

                "Learning Goal":
                  formData.learning_goal,
              }}
            />
          </div>
        )}

        {/* =================================================
            MESSAGE
        ================================================= */}

        {message && (
          <div
            style={{
              marginTop: "20px",
              padding: "13px",
              borderRadius: "10px",

              background:
                message.includes(
                  "successfully"
                )
                  ? "#dcfce7"
                  : "#fee2e2",

              color:
                message.includes(
                  "successfully"
                )
                  ? "#166534"
                  : "#b91c1c",

              fontWeight: "600",
              fontSize: "14px",
            }}
          >
            {message}
          </div>
        )}

        {/* =================================================
            NAVIGATION
        ================================================= */}

        <div
          style={{
            display: "flex",
            justifyContent:
              "space-between",
            marginTop: "30px",
            gap: "10px",
          }}
        >
          {step > 1 ? (
            <button
              type="button"
              onClick={
                previousStep
              }
              style={{
                ...buttonStyle,
                background:
                  "#64748b",
              }}
            >
              ← Previous
            </button>
          ) : (
            <div />
          )}

          {step < 8 ? (
            <button
              type="button"
              onClick={nextStep}
              style={
                buttonStyle
              }
            >
              Next →
            </button>
          ) : (
            <button
              type="button"
              onClick={
                handleSubmit
              }
              disabled={loading}
              style={{
                ...buttonStyle,
                opacity:
                  loading
                    ? 0.6
                    : 1,
                cursor:
                  loading
                    ? "not-allowed"
                    : "pointer",
              }}
            >
              {loading
                ? "Submitting..."
                : "Submit Registration"}
            </button>
          )}
        </div>
      </div>
    </div>
  );
}

// =========================================================
// REVIEW COMPONENT
// =========================================================

function ReviewSection({
  title,
  data,
}) {
  return (
    <div
      style={{
        marginTop: "20px",
        padding: "18px",
        background:
          "#f8fafc",
        borderRadius:
          "12px",
      }}
    >
      <h3>{title}</h3>

      {Object.entries(
        data
      ).map(
        ([label, value]) => (
          <p
            key={label}
            style={{
              marginTop:
                "8px",
            }}
          >
            <strong>
              {label}:
            </strong>{" "}
            {value ||
              "Not provided"}
          </p>
        )
      )}
    </div>
  );
}

export default Register;