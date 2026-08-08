import "./App.css";
import { useState } from "react";

import Register from "./Register";
import Dashboard from "./Dashboard";

function App() {
  // =========================================================
  // LOGIN STATE
  // =========================================================

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);

  // =========================================================
  // PAGE STATE
  // =========================================================

  const [showRegister, setShowRegister] = useState(false);

  const [showDashboard, setShowDashboard] =
    useState(
      !!localStorage.getItem("token")
    );

  // =========================================================
  // OPEN REGISTRATION
  // =========================================================

  const openRegister = () => {
    setMessage("");
    setEmail("");
    setPassword("");
    setShowRegister(true);
  };

  // =========================================================
  // BACK TO LOGIN
  // =========================================================

  const backToLogin = () => {
    setMessage("");
    setShowRegister(false);
  };

  // =========================================================
  // LOGOUT
  // =========================================================

  const handleLogout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("student");

    setEmail("");
    setPassword("");
    setMessage("");

    setShowDashboard(false);
    setShowRegister(false);
  };

  // =========================================================
  // STUDENT LOGIN
  // =========================================================

  const handleLogin = async (event) => {
    event.preventDefault();

    setMessage("");

    // Basic validation
    if (!email.trim() || !password) {
      setMessage(
        "Please enter your email and password."
      );
      return;
    }

    setLoading(true);

    try {
      // =====================================================
      // SEND LOGIN REQUEST
      // =====================================================

      const response = await fetch(
        "http://127.0.0.1:5000/api/students/login",
        {
          method: "POST",

          headers: {
            "Content-Type": "application/json",
          },

          body: JSON.stringify({
            email: email.trim(),
            password: password,
          }),
        }
      );

      // =====================================================
      // READ RESPONSE SAFELY
      // =====================================================

      const responseText =
        await response.text();

      let data;

      try {
        data = JSON.parse(responseText);
      } catch (jsonError) {
        console.error(
          "Backend returned non-JSON response:",
          responseText
        );

        throw new Error(
          "Backend returned an invalid response. Check that the Flask server is running correctly."
        );
      }

      console.log(
        "Login response:",
        data
      );

      // =====================================================
      // LOGIN SUCCESS
      // =====================================================

      if (
        response.ok &&
        data.success
      ) {
        // ---------------------------------------------------
        // SAVE JWT TOKEN
        // ---------------------------------------------------

        if (data.token) {
          localStorage.setItem(
            "token",
            data.token
          );
        }

        // ---------------------------------------------------
        // SAVE STUDENT INFORMATION
        // ---------------------------------------------------

        if (data.student) {
          localStorage.setItem(
            "student",
            JSON.stringify(
              data.student
            )
          );
        }

        // ---------------------------------------------------
        // SHOW SUCCESS MESSAGE
        // ---------------------------------------------------

        setMessage(
          "Login successful!"
        );

        // ---------------------------------------------------
        // OPEN DASHBOARD
        // ---------------------------------------------------

        setShowDashboard(true);
      }

      // =====================================================
      // LOGIN FAILED
      // =====================================================

      else {
        setMessage(
          data.message ||
          "Invalid email or password."
        );
      }
    }

    // =======================================================
    // CONNECTION ERROR
    // =======================================================

    catch (error) {
      console.error(
        "Login error:",
        error
      );

      setMessage(
        error.message ||
        "Unable to connect to the backend server. Make sure Flask is running on port 5000."
      );
    }

    // =======================================================
    // STOP LOADING
    // =======================================================

    finally {
      setLoading(false);
    }
  };

  // =========================================================
  // DASHBOARD
  // =========================================================

  if (showDashboard) {
    return (
      <Dashboard
        onLogout={handleLogout}
      />
    );
  }

  // =========================================================
  // REGISTRATION PAGE
  // =========================================================

  if (showRegister) {
    return (
      <div>
        <Register />

        {/* -----------------------------------------------
            BACK TO LOGIN BUTTON
        ----------------------------------------------- */}

        <div
          style={{
            position: "fixed",
            top: "20px",
            left: "20px",
            zIndex: 1000,
          }}
        >
          <button
            type="button"
            onClick={backToLogin}
            style={{
              padding: "10px 16px",
              border: "none",
              borderRadius: "8px",
              background: "#64748b",
              color: "white",
              fontWeight: "600",
              cursor: "pointer",
              boxShadow:
                "0 4px 12px rgba(0,0,0,0.15)",
            }}
          >
            ← Back to Login
          </button>
        </div>
      </div>
    );
  }

  // =========================================================
  // LOGIN PAGE
  // =========================================================

  return (
    <div className="login-container">

      <div className="login-card">

        {/* =================================================
            PROJECT TITLE
        ================================================= */}

        <h1>
          Skill Analyzer
        </h1>

        <p className="subtitle">
          Student Skill Analyzer &
          Recommendation System
        </p>

        <h2>
          Student Login
        </h2>

        {/* =================================================
            LOGIN FORM
        ================================================= */}

        <form
          onSubmit={handleLogin}
        >

          {/* =================================================
              EMAIL
          ================================================= */}

          <label htmlFor="email">
            Email Address
          </label>

          <input
            id="email"
            type="email"
            placeholder="Enter your email"
            value={email}
            onChange={(event) =>
              setEmail(
                event.target.value
              )
            }
            required
          />

          {/* =================================================
              PASSWORD
          ================================================= */}

          <label htmlFor="password">
            Password
          </label>

          <input
            id="password"
            type="password"
            placeholder="Enter your password"
            value={password}
            onChange={(event) =>
              setPassword(
                event.target.value
              )
            }
            required
          />

          {/* =================================================
              LOGIN BUTTON
          ================================================= */}

          <button
            type="submit"
            disabled={loading}
          >
            {loading
              ? "Logging in..."
              : "Login"}
          </button>

        </form>

        {/* =================================================
            LOGIN MESSAGE
        ================================================= */}

        {message && (
          <p
            className="message"
            style={{
              color:
                message
                  .toLowerCase()
                  .includes("successful")
                  ? "#16a34a"
                  : "#dc2626",
            }}
          >
            {message}
          </p>
        )}

        {/* =================================================
            REGISTRATION
        ================================================= */}

        <div className="register-text">

          <p>
            Don't have an account?
          </p>

          <button
            type="button"
            onClick={openRegister}
          >
            Create Student Account
          </button>

        </div>

      </div>

    </div>
  );
}

export default App;