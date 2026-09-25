function Profile() {
  return (
    <div className="page-container">

      <div className="page-header">
        <span>ACCOUNT</span>
        <h1>My Profile</h1>
        <p>Manage your academic and personal information.</p>
      </div>

      <div className="profile-layout">

        <div className="profile-card profile-summary">
          <div className="profile-avatar">
            V
          </div>

          <h2>Student Name</h2>
          <p>student@example.com</p>

          <div className="profile-badge">
            🎓 Student
          </div>
        </div>

        <div className="profile-card">

          <h2>Personal Information</h2>

          <div className="profile-form">

            <div>
              <label>First Name</label>
              <input type="text" value="Student" readOnly />
            </div>

            <div>
              <label>Last Name</label>
              <input type="text" value="Name" readOnly />
            </div>

            <div>
              <label>Email</label>
              <input
                type="email"
                value="student@example.com"
                readOnly
              />
            </div>

            <div>
              <label>Date of Birth</label>
              <input type="text" value="01/01/2005" readOnly />
            </div>

          </div>

          <h2 className="profile-section-title">
            Academic Information
          </h2>

          <div className="profile-form">

            <div>
              <label>Education Level</label>
              <input
                type="text"
                value="B.Tech Information Technology"
                readOnly
              />
            </div>

            <div>
              <label>College</label>
              <input
                type="text"
                value="College of Engineering Guindy"
                readOnly
              />
            </div>

          </div>

          <button className="primary-btn">
            Edit Profile
          </button>

        </div>

      </div>

    </div>
  );
}

export default Profile;