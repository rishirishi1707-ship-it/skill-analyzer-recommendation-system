import { useState } from "react";

function Register() {
  const [formData, setFormData] = useState({
    name: "",
    studentId: "",
    email: "",
    mobile: "",
    password: "",
    confirmPassword: "",
    gender: "",
    dob: "",
    department: "",
    degree: "",
    year: "",
    section: "",
    semester: "",
  });

  const [message, setMessage] = useState("");

  const handleChange = (event) => {
    const { name, value } = event.target;

    setFormData((previous) => ({
      ...previous,
      [name]: value,
    }));
  };

  const handleSubmit = async (event) => {
    event.preventDefault();

    if (formData.password !== formData.confirmPassword) {
      setMessage("Passwords do not match.");
      return;
    }

    try {
      const response = await fetch(
        "http://127.0.0.1:5000/api/students/register",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(formData),
        }
      );

      const data = await response.json();

      if (response.ok && data.success) {
        setMessage("Registration successful!");
      } else {
        setMessage(data.message || "Registration failed.");
      }
    } catch (error) {
      console.error(error);
      setMessage("Unable to connect to the backend.");
    }
  };

  return (
    <div className="login-container">
      <div className="login-card">

        <h1>Skill Analyzer</h1>

        <p className="subtitle">
          Student Skill Analyzer & Recommendation System
        </p>

        <h2>Student Registration</h2>

        <form onSubmit={handleSubmit}>

          <label>Full Name</label>
          <input
            name="name"
            type="text"
            placeholder="Enter your full name"
            value={formData.name}
            onChange={handleChange}
            required
          />

          <label>Student ID</label>
          <input
            name="studentId"
            type="text"
            placeholder="Enter your student ID"
            value={formData.studentId}
            onChange={handleChange}
            required
          />

          <label>Email Address</label>
          <input
            name="email"
            type="email"
            placeholder="Enter your email"
            value={formData.email}
            onChange={handleChange}
            required
          />

          <label>Mobile Number</label>
          <input
            name="mobile"
            type="tel"
            placeholder="Enter your mobile number"
            value={formData.mobile}
            onChange={handleChange}
            required
          />

          <label>Password</label>
          <input
            name="password"
            type="password"
            placeholder="Create a password"
            value={formData.password}
            onChange={handleChange}
            required
          />

          <label>Confirm Password</label>
          <input
            name="confirmPassword"
            type="password"
            placeholder="Confirm your password"
            value={formData.confirmPassword}
            onChange={handleChange}
            required
          />

          <label>Gender</label>
          <select
            name="gender"
            value={formData.gender}
            onChange={handleChange}
            required
          >
            <option value="">Select Gender</option>
            <option value="Male">Male</option>
            <option value="Female">Female</option>
            <option value="Other">Other</option>
          </select>

          <label>Date of Birth</label>
          <input
            name="dob"
            type="date"
            value={formData.dob}
            onChange={handleChange}
            required
          />

          <label>Department</label>
          <input
            name="department"
            type="text"
            placeholder="Example: Computer Science"
            value={formData.department}
            onChange={handleChange}
            required
          />

          <label>Degree</label>
          <input
            name="degree"
            type="text"
            placeholder="Example: B.E."
            value={formData.degree}
            onChange={handleChange}
            required
          />

          <label>Year of Study</label>
          <select
            name="year"
            value={formData.year}
            onChange={handleChange}
            required
          >
            <option value="">Select Year</option>
            <option value="1">1st Year</option>
            <option value="2">2nd Year</option>
            <option value="3">3rd Year</option>
            <option value="4">4th Year</option>
          </select>

          <label>Section</label>
          <input
            name="section"
            type="text"
            placeholder="Example: A"
            value={formData.section}
            onChange={handleChange}
            required
          />

          <label>Semester</label>
          <input
            name="semester"
            type="number"
            min="1"
            max="8"
            placeholder="Enter semester"
            value={formData.semester}
            onChange={handleChange}
            required
          />

          <button type="submit">
            Register
          </button>

        </form>

        {message && (
          <p className="message">
            {message}
          </p>
        )}

      </div>
    </div>
  );
}

export default Register;