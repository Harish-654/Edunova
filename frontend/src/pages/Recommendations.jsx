import RecommendationCard from "../components/RecommendationCard";

function Recommendations() {
  return (
    <div className="page-container">

      <div className="page-header">
        <span>EXPLORE</span>
        <h1>Recommendations</h1>
        <p>
          Discover opportunities selected for your academic and career goals.
        </p>
      </div>

      <div className="search-box">
        🔍
        <input
          type="text"
          placeholder="Search recommendations..."
        />
      </div>

      <div className="filter-row">
        <button className="filter-active">All</button>
        <button>Career</button>
        <button>Exams</button>
        <button>Scholarships</button>
        <button>Courses</button>
      </div>

      <div className="recommendation-grid large-grid">

        <RecommendationCard
          title="Software Developer"
          category="Career"
          description="Build applications and solve real-world technical problems."
          tag="Recommended"
        />

        <RecommendationCard
          title="Data Scientist"
          category="Career"
          description="Work with data, machine learning and analytical models."
          tag="Popular"
        />

        <RecommendationCard
          title="GATE 2027"
          category="Exam"
          description="National-level examination for higher technical education."
          tag="Upcoming"
        />

        <RecommendationCard
          title="AI & Machine Learning Course"
          category="Course"
          description="Develop skills in artificial intelligence and machine learning."
          tag="Trending"
        />

        <RecommendationCard
          title="Cloud Computing"
          category="Career"
          description="Explore cloud technologies and modern infrastructure."
          tag="Recommended"
        />

        <RecommendationCard
          title="Government Scholarship"
          category="Scholarship"
          description="Explore available financial assistance opportunities."
          tag="New"
        />

      </div>

    </div>
  );
}

export default Recommendations;