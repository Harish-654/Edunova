import { Link, useNavigate } from "react-router-dom";

function Login() {
  const navigate = useNavigate();

  const handleLogin = (e) => {
    e.preventDefault();

    // Frontend demo only
    navigate("/dashboard");
  };

  return (
    <div className="auth-page">
      <div className="auth-box">

        <div className="auth-header">
          <div className="auth-logo">🎓</div>
          <h1>Welcome Back</h1>
          <p>Login to continue your EduNova journey.</p>
        </div>

        <form onSubmit={handleLogin}>

          <label>Email Address</label>
          <input
            type="email"
            placeholder="Enter your email"
            required
          />

          <label>Password</label>
          <input
            type="password"
            placeholder="Enter your password"
            required
          />

          <div className="form-options">
            <label className="checkbox-label">
              <input type="checkbox" />
              Remember me
            </label>

            <span>Forgot password?</span>
          </div>

          <button type="submit" className="primary-btn full-btn">
            Login
          </button>

        </form>

        <p className="auth-bottom">
          Don't have an account?{" "}
          <Link to="/register">Create Account</Link>
        </p>

      </div>
    </div>
  );
}

export default Login;