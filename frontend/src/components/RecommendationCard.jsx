function RecommendationCard({ title, category, description, tag }) {
  return (
    <div className="recommendation-card">
      <div className="card-top">
        <span className="tag">{tag}</span>
        <span className="category">{category}</span>
      </div>

      <h3>{title}</h3>

      <p>{description}</p>

      <button className="outline-btn">View Details</button>
    </div>
  );
}

export default RecommendationCard;