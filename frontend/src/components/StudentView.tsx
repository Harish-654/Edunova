import { useEffect, useState } from "react";
import { api } from "../api";
import QuestionnairePage from "./QuestionnairePage";
import type { Exam, ExamDetail, Recommendation, Scholarship } from "../types";

interface Props {
  tab: string;
}

function formatMoney(value: number | null | undefined): string {
  if (value === null || value === undefined) {
    return "—";
  }
  return "₹ " + value.toLocaleString("en-IN");
}

function formatDate(value: string | null | undefined): string {
  if (!value) {
    return "—";
  }
  return new Date(value).toLocaleDateString("en-IN", {
    day: "2-digit",
    month: "short",
    year: "numeric",
  });
}

function MatchesSection() {
  const [items, setItems] = useState<Recommendation[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api<Recommendation[]>("/match/my")
      .then(setItems)
      .catch((err) =>
        setError(err instanceof Error ? err.message : "Could not load matches"),
      )
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return <div className="empty">Finding the best exams for you...</div>;
  }
  if (error) {
    return <div className="error-box">{error}</div>;
  }
  if (items.length === 0) {
    return (
      <div className="empty">
        No answers yet. Open the <strong>Questionnaire</strong> tab and save your
        answers first.
      </div>
    );
  }

  return (
    <div>
      {items.map((item) => (
        <div className="list-item" key={item.exam_id}>
          <div className="head">
            <div>
              <div className="title">{item.exam_name}</div>
              <div className="muted">
                {item.exam_code}
                {item.conducting_body ? ` · ${item.conducting_body}` : ""}
              </div>
            </div>
            <div className="row">
              <span className={`badge ${item.eligible ? "ok" : "no"}`}>
                {item.eligible ? "Eligible" : "Not eligible"}
              </span>
              <span className="badge neutral">{item.composite_score}% match</span>
            </div>
          </div>

          <div className="row" style={{ marginTop: 10 }}>
            <span className="muted">
              Semantic similarity {(item.semantic_score * 100).toFixed(1)}%
            </span>
            {item.matched_fields.length > 0 && (
              <span className="tags">
                {item.matched_fields.map((field) => (
                  <span className="tag" key={field}>
                    {field}
                  </span>
                ))}
              </span>
            )}
          </div>

          {!item.eligible && item.reasons.length > 0 && (
            <div className="muted" style={{ marginTop: 8 }}>
              {item.reasons.join(" ")}
            </div>
          )}
        </div>
      ))}
    </div>
  );
}

function ExamsSection() {
  const [items, setItems] = useState<Exam[]>([]);
  const [detail, setDetail] = useState<ExamDetail | null>(null);
  const [openId, setOpenId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api<Exam[]>("/exams")
      .then(setItems)
      .catch((err) => setError(err instanceof Error ? err.message : "Failed to load"));
  }, []);

  async function toggle(exam: Exam) {
    if (openId === exam.exam_id) {
      setOpenId(null);
      setDetail(null);
      return;
    }
    try {
      const data = await api<ExamDetail>(`/exams/${exam.exam_id}`);
      setDetail(data);
      setOpenId(exam.exam_id);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load exam");
    }
  }

  if (error) {
    return <div className="error-box">{error}</div>;
  }

  return (
    <div>
      {items.map((exam) => (
        <div className="list-item" key={exam.exam_id}>
          <div className="head">
            <div>
              <div className="title">{exam.exam_name}</div>
              <div className="muted">
                {exam.exam_level ? `${exam.exam_level} · ` : ""}
                {exam.conducting_body || ""}
              </div>
            </div>
            <button className="link-btn" onClick={() => toggle(exam)}>
              {openId === exam.exam_id ? "Hide dates" : "View dates"}
            </button>
          </div>

          {openId === exam.exam_id && detail && (
            <div style={{ marginTop: 14 }}>
              <h3>Important dates</h3>
              <table>
                <thead>
                  <tr>
                    <th>Year</th>
                    <th>Applications open</th>
                    <th>Applications close</th>
                    <th>Exam date</th>
                  </tr>
                </thead>
                <tbody>
                  {detail.schedules.map((schedule) => (
                    <tr key={schedule.schedule_id}>
                      <td>{schedule.academic_year}</td>
                      <td>{formatDate(schedule.application_start_date)}</td>
                      <td>{formatDate(schedule.application_end_date)}</td>
                      <td>{formatDate(schedule.exam_date)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>

              <h3>Eligibility</h3>
              <div className="muted">
                {detail.eligibility?.required_degree
                  ? `Requires ${detail.eligibility.required_degree}`
                  : "No degree requirement"}
                {detail.eligibility?.min_qualifying_percentage
                  ? ` · at least ${detail.eligibility.min_qualifying_percentage}% marks`
                  : ""}
                {detail.eligibility?.max_age ? ` · max age ${detail.eligibility.max_age}` : ""}
              </div>

              <h3>Application fee</h3>
              <div className="muted">{detail.application_fee || "Not specified"}</div>

              {detail.official_url && (
                <p>
                  <a href={detail.official_url} target="_blank" rel="noreferrer">
                    Official website
                  </a>
                </p>
              )}
            </div>
          )}
        </div>
      ))}
    </div>
  );
}

function ScholarshipsSection() {
  const [items, setItems] = useState<Scholarship[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api<Scholarship[]>("/scholarships")
      .then(setItems)
      .catch((err) => setError(err instanceof Error ? err.message : "Failed to load"));
  }, []);

  if (error) {
    return <div className="error-box">{error}</div>;
  }

  return (
    <div className="card">
      <h2>Available scholarships</h2>
      <p className="muted">Aid you can apply for alongside these exams.</p>
      <table>
        <thead>
          <tr>
            <th>Scholarship</th>
            <th>Provider</th>
            <th>Max amount</th>
            <th>Family income limit</th>
          </tr>
        </thead>
        <tbody>
          {items.map((item) => (
            <tr key={item.scholarship_id}>
              <td>{item.title}</td>
              <td>{item.provider_name || "—"}</td>
              <td>{formatMoney(item.max_amount)}</td>
              <td>{formatMoney(item.max_income_limit)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default function StudentView({ tab }: Props) {
  if (tab === "questionnaire") {
    return <QuestionnairePage />;
  }
  if (tab === "exams") {
    return <ExamsSection />;
  }
  if (tab === "scholarships") {
    return <ScholarshipsSection />;
  }
  return <MatchesSection />;
}
