import './App.css'

function App() {
  const folders = [
    { name: 'backend', open: true, children: ['app', 'scripts', 'requirements.txt'] },
    { name: 'frontend', open: true, children: ['public', 'src', 'package.json'] },
    { name: 'scripts', open: false, children: ['db.py', 'setup_db.sh'] },
  ]

  return (
    <main className="app-shell">
      <aside className="sidebar" aria-label="EduNova project folders">
        <div className="sidebar-heading">
          <span className="brand-mark">E</span>
          <span>EduNova</span>
        </div>
        <div className="explorer-label">EXPLORER</div>
        <nav className="folder-tree" aria-label="Project folders">
          <button type="button" className="tree-item project-item">
            <span className="chevron">⌄</span>
            <span className="folder-icon" aria-hidden="true" />
            <span>EDUNOVA-AI</span>
          </button>
          {folders.map((folder) => (
            <div className="folder-group" key={folder.name}>
              <button type="button" className="tree-item">
                <span className="chevron">{folder.open ? '⌄' : '›'}</span>
                <span className="folder-icon" aria-hidden="true" />
                <span>{folder.name}</span>
              </button>
              {folder.open && (
                <div className="folder-children">
                  {folder.children.map((child) => (
                    <button type="button" className="tree-item child-item" key={child}>
                      <span className="file-icon" aria-hidden="true" />
                      <span>{child}</span>
                    </button>
                  ))}
                </div>
              )}
            </div>
          ))}
          <button type="button" className="tree-item">
            <span className="file-icon" aria-hidden="true" />
            <span>README.md</span>
          </button>
          <button type="button" className="tree-item">
            <span className="file-icon" aria-hidden="true" />
            <span>schema.sql</span>
          </button>
        </nav>
      </aside>

      <section className="content-panel">
        <header className="topbar">
          <span className="breadcrumb">EduNova / Overview</span>
          <span className="status-dot">System ready</span>
        </header>
        <div className="content-inner">
          <p className="eyebrow">CAREER GUIDANCE PLATFORM</p>
          <h1>Build a clearer path forward.</h1>
          <p className="intro">
            Explore your project folders and keep the matching engine, student profiles,
            and exam catalog in one place.
          </p>
          <div className="overview-grid">
            <article>
              <span className="card-kicker">01 / MATCH</span>
              <h2>Find your next opportunity</h2>
              <p>Ranked entrance exam recommendations based on your goals and eligibility.</p>
            </article>
            <article>
              <span className="card-kicker">02 / PROFILE</span>
              <h2>Your profile, understood</h2>
              <p>Keep marks, preferences, and financial context ready for every match.</p>
            </article>
          </div>
        </div>
      </section>
    </main>
  )
}

export default App
