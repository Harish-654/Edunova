function NotificationCard({ title, message, date, type }) {
  return (
    <div className="notification-card">
      <div className="notification-icon">
        {type === "deadline" ? "⏰" : "🔔"}
      </div>

      <div>
        <h3>{title}</h3>
        <p>{message}</p>
        <small>{date}</small>
      </div>
    </div>
  );
}

export default NotificationCard;