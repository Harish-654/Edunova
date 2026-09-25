import { Link } from "react-router-dom";
import RecommendationCard from "../components/RecommendationCard";

function Dashboard() {
  return (
    <div className="dashboard-page">

      <section className="dashboard-header">
        <div>
          <p className="welcome-text">Welcome back 👋</p>
          <h1>Student Dashboard</h1>
          <p>
            Here's what's happening with your educational journey.
          </p>
        </div>

        <Link to="/profile" className="profile-mini">
          👤
          <span>My Profile</span>
        </Link>
      </section>

      <section className="stats-grid">

        <div className="stat-card">
          <div className="stat-icon">🎯</div>
          <div>
            <h2>08</h2>
            <p>Recommendations</p>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon">📅</div>
          <div>
            <h2>05</h2>
            <p>Upcoming Exams</p>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon">🔔</div>
          <div>
            <h2>03</h2>
            <p>Notifications</p>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon">⭐</div>
          <div>
            <h2>06</h2>
            <p>Bookmarked</p>
          </div>
        </div>

      </section>

      <section className="dashboard-grid">

        <div className="dashboard-main">
          <div className="section-title-row">
            <div>
              <span>FOR YOU</span>
              <h2>Recommended Opportunities</h2>
            </div>

            <Link to="/recommendations">
              View All →
            </Link>
          </div>

          <div className="recommendation-grid">

            <RecommendationCard
              title="Software Developer"
              category="Career"
              description="Explore software development roles and required skills."
              tag="Recommended"
            />

            <RecommendationCard
              title="GATE 2027"
              category="Exam"
              description="Prepare for higher studies and technical opportunities."
              tag="Upcoming"
            />

          </div>
        </div>

        <div className="dashboard-side">
          <div className="side-card">
            <div className="section-title-row">
              <div>
                <span>UPDATES</span>
                <h2>Recent Notifications</h2>
              </div>
            </div>

            <div className="mini-notification">
              <span>⏰</span>
              <div>
                <strong>Exam Application</strong>
                <p>Application deadline is approaching.</p>
              </div>
            </div>

            <div className="mini-notification">
              <span>🔔</span>
              <div>
                <strong>New Recommendation</strong>
                <p>A new career opportunity is available.</p>
              </div>
            </div>

            <Link to="/notifications" className="view-link">
              View all notifications →
            </Link>
          </div>
        </div>

      </section>

    </div>
  );
}

export default Dashboard;