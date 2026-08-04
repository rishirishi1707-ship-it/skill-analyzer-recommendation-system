import "./App.css";
import { useState } from "react";
import Register from "./Register";

function App() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);
  const [showRegister, setShowRegister] = useState(false);

  // Show Registration Page
  if (showRegister) {
    return (
      <Register />
    );
  }

  // Student Login
  const handleLogin = async (event) => {
    event.preventDefault();

    setMessage("");
    setLoading(true);

    try {
      const response = await fetch(
        "http://127.0.0.1:5000/api/students/login",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            email: email,
            password: password,
          }),
        }
      );

      const data = await response.json();

      if (response.ok && data.success) {
        // Save JWT token
        if (data.token) {
          localStorage.setItem("token", data.token);
        }

        // Save student information
        if (data.student) {
          localStorage.setItem(
            "student",
            JSON.stringify(data.student)
          );
        }

        setMessage("Login successful!");

        console.log("Login response:", data);
      } else {
        setMessage(
          data.message || "Invalid email or password"
        );
      }
    } catch (error) {
      console.error("Login error:", error);

      setMessage(
        "Unable to connect to the backend server."
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-container">

      <div className="login-card">

        <h1>Skill Analyzer</h1>

        <p className="subtitle">
          Student Skill Analyzer & Recommendation System
        </p>

        <h2>Student Login</h2>

        <form onSubmit={handleLogin}>

          <label htmlFor="email">
            Email Address
          </label>

          <input
            id="email"
            type="email"
            placeholder="Enter your email"
            value={email}
            onChange={(event) =>
              setEmail(event.target.value)
            }
            required
          />

          <label htmlFor="password">
            Password
          </label>

          <input
            id="password"
            type="password"
            placeholder="Enter your password"
            value={password}
            onChange={(event) =>
              setPassword(event.target.value)
            }
            required
          />

          <button
            type="submit"
            disabled={loading}
          >
            {loading ? "Logging in..." : "Login"}
          </button>

        </form>

        {message && (
          <p className="message">
            {message}
          </p>
        )}

        <div className="register-text">

          <p>Don't have an account?</p>

          <button
            type="button"
            onClick={() => {
              setMessage("");
              setShowRegister(true);
            }}
          >
            Create Student Account
          </button>

        </div>

      </div>

    </div>
  );
}

export default App;