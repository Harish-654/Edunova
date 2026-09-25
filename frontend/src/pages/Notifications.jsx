import NotificationCard from "../components/NotificationCard";

function Notifications() {
  return (
    <div className="page-container">

      <div className="page-header">
        <span>UPDATES</span>
        <h1>Notifications</h1>
        <p>
          Stay updated with deadlines, exams and important opportunities.
        </p>
      </div>

      <div className="notification-list">

        <NotificationCard
          title="Exam Application Deadline"
          message="The application deadline for the upcoming examination is approaching."
          date="Today"
          type="deadline"
        />

        <NotificationCard
          title="New Career Recommendation"
          message="A new career opportunity has been added to your recommendations."
          date="Yesterday"
          type="recommendation"
        />

        <NotificationCard
          title="Scholarship Opportunity"
          message="A scholarship opportunity matching your profile is available."
          date="2 days ago"
          type="recommendation"
        />

        <NotificationCard
          title="Profile Update"
          message="Keep your academic profile updated to receive better recommendations."
          date="3 days ago"
          type="profile"
        />

      </div>

    </div>
  );
}

export default Notifications;