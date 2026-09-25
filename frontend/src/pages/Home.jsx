import { Link } from "react-router-dom";

function Home() {
  return (
    <div className="home">

      <section className="hero">
        <div className="hero-content">
          <span className="hero-badge">
            🎓 Smart Education Platform
          </span>

          <h1>
            Your Future Starts
            <span> With EduNova</span>
          </h1>

          <p>
            Discover career opportunities, exams, recommendations and
            important educational updates in one place.
          </p>

          <div className="hero-buttons">
            <Link to="/register" className="primary-btn">
              Get Started
            </Link>

            <Link to="/login" className="secondary-btn">
              Login
            </Link>
          </div>
        </div>

        <div className="hero-card">
          <div className="floating-card">
            <span>📚</span>
            <div>
              <strong>Learning</strong>
              <p>Keep growing every day</p>
            </div>
          </div>

          <div className="floating-card">
            <span>🎯</span>
            <div>
              <strong>Career Goals</strong>
              <p>Find opportunities for you</p>
            </div>
          </div>

          <div className="floating-card">
            <span>🔔</span>
            <div>
              <strong>Notifications</strong>
              <p>Never miss a deadline</p>
            </div>
          </div>
        </div>
      </section>

      <section className="features-section">
        <div className="section-heading">
          <span>FEATURES</span>
          <h2>Everything You Need in One Place</h2>
          <p>
            EduNova helps students discover and manage their educational
            journey.
          </p>
        </div>

        <div className="feature-grid">
          <div className="feature-card">
            <div className="feature-icon">🎯</div>
            <h3>Personalized Recommendations</h3>
            <p>
              Explore opportunities based on your interests and academic
              profile.
            </p>
          </div>

          <div className="feature-card">
            <div className="feature-icon">📅</div>
            <h3>Exam Updates</h3>
            <p>
              Keep track of important examinations and application deadlines.
            </p>
          </div>

          <div className="feature-card">
            <div className="feature-icon">🔔</div>
            <h3>Smart Notifications</h3>
            <p>
              Get timely reminders about deadlines and important updates.
            </p>
          </div>

          <div className="feature-card">
            <div className="feature-icon">👤</div>
            <h3>Student Profile</h3>
            <p>
              Maintain your academic details and career preferences.
            </p>
          </div>
        </div>
      </section>

      <section className="cta-section">
        <h2>Ready to Explore Your Future?</h2>
        <p>
          Create your EduNova profile and start exploring opportunities.
        </p>

        <Link to="/register" className="primary-btn">
          Create Account
        </Link>
      </section>

    </div>
  );
}

export default Home;