import { useState } from "react";
import { setToken } from "./api";
import AdminView from "./components/AdminView";
import AuthPage from "./components/AuthPage";
import StudentView from "./components/StudentView";
import type { Student } from "./types";

const STUDENT_TABS = [
  { id: "matches", label: "My matches" },
  { id: "exams", label: "Exams" },
  { id: "scholarships", label: "Scholarships" },
  { id: "questionnaire", label: "Questionnaire" },
];

const ADMIN_TABS = [
  { id: "overview", label: "Overview" },
  { id: "ingestion", label: "Crawling" },
  { id: "scholarships", label: "Scholarships" },
];

function loadUser(): Student | null {
  const raw = localStorage.getItem("edunova_user");
  if (!raw) {
    return null;
  }
  try {
    return JSON.parse(raw) as Student;
  } catch {
    return null;
  }
}

export default function App() {
  const [student, setStudent] = useState<Student | null>(loadUser);
  const [tab, setTab] = useState<string>("matches");

  function handleAuth(token: string, user: Student) {
    setToken(token);
    localStorage.setItem("edunova_user", JSON.stringify(user));
    setStudent(user);
    setTab(user.role === "admin" ? "overview" : "matches");
  }

  function handleLogout() {
    setToken(null);
    localStorage.removeItem("edunova_user");
    setStudent(null);
  }

  if (!student) {
    return <AuthPage onAuth={handleAuth} />;
  }

  const tabs = student.role === "admin" ? ADMIN_TABS : STUDENT_TABS;

  return (
    <div>
      <header className="topbar">
        <span className="brand">EduNova</span>
        <nav className="nav">
          {tabs.map((item) => (
            <button
              key={item.id}
              className={tab === item.id ? "active" : ""}
              onClick={() => setTab(item.id)}
            >
              {item.label}
            </button>
          ))}
        </nav>
        <span className="topbar-spacer" />
        <span className="user-chip">
          {student.full_name} &middot; {student.role}
        </span>
        <button className="link-btn" onClick={handleLogout}>
          Log out
        </button>
      </header>
      <main className="page">
        {student.role === "admin" ? <AdminView tab={tab} /> : <StudentView tab={tab} />}
      </main>
    </div>
  );
}
