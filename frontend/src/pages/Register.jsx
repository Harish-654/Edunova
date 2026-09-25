import { Link, useNavigate } from "react-router-dom";

function Register() {
  const navigate = useNavigate();

  const handleRegister = (e) => {
    e.preventDefault();

    // Frontend demo only
    navigate("/login");
  };

  return (
    <div className="auth-page">
      <div className="auth-box register-box">

        <div className="auth-header">
          <div className="auth-logo">✨</div>
          <h1>Create Your Account</h1>
          <p>Start your personalized EduNova journey.</p>
        </div>

        <form onSubmit={handleRegister}>

          <div className="two-inputs">
            <div>
              <label>First Name</label>
              <input
                type="text"
                placeholder="First name"
                required
              />
            </div>

            <div>
              <label>Last Name</label>
              <input
                type="text"
                placeholder="Last name"
                required
              />
            </div>
          </div>

          <label>Email Address</label>
          <input
            type="email"
            placeholder="Enter your email"
            required
          />

          <label>Date of Birth</label>
          <input
            type="date"
            required
          />

          <label>Password</label>
          <input
            type="password"
            placeholder="Create password"
            required
          />

          <label>Confirm Password</label>
          <input
            type="password"
            placeholder="Confirm password"
            required
          />

          <button type="submit" className="primary-btn full-btn">
            Create Account
          </button>

        </form>

        <p className="auth-bottom">
          Already have an account?{" "}
          <Link to="/login">Login</Link>
        </p>

      </div>
    </div>
  );
}

export default Register;