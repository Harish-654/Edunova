import { useEffect, useState } from "react";
import type { FormEvent } from "react";
import { api } from "../api";
import type { Question, QuestionnaireResult } from "../types";

type AnswerValue = string | number | string[];

interface StoredResponse {
  answers: Record<string, AnswerValue>;
  derived_statement: string | null;
  derived_fields: string[] | null;
}

interface Props {
  onSubmitted?: () => void;
}

export default function QuestionnairePage({ onSubmitted }: Props) {
  const [questions, setQuestions] = useState<Question[]>([]);
  const [answers, setAnswers] = useState<Record<string, AnswerValue>>({});
  const [result, setResult] = useState<QuestionnaireResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    api<Question[]>("/questionnaire/questions")
      .then(setQuestions)
      .catch((err) =>
        setError(err instanceof Error ? err.message : "Failed to load questions"),
      );
  }, []);

  // the server keeps the last submission, so reopening this tab shows it instead of a blank form
  useEffect(() => {
    api<StoredResponse | null>("/questionnaire/me")
      .then((saved) => {
        if (!saved) return;
        setAnswers(saved.answers);
        setResult({
          derived_statement: saved.derived_statement ?? "",
          derived_fields: saved.derived_fields ?? [],
          career_interest_statement: saved.derived_statement ?? "",
          profile_updated: true,
        });
      })
      .catch(() => {});
  }, []);

  function setValue(id: string, value: AnswerValue) {
    setAnswers((previous) => ({ ...previous, [id]: value }));
  }

  function toggleMulti(id: string, value: string) {
    const current = Array.isArray(answers[id]) ? (answers[id] as string[]) : [];
    const next = current.includes(value)
      ? current.filter((item) => item !== value)
      : [...current, value];
    setValue(id, next);
  }

  async function submit(event: FormEvent) {
    event.preventDefault();
    setBusy(true);
    setError(null);
    try {
      const data = await api<QuestionnaireResult>("/questionnaire/submit", {
        method: "POST",
        body: { answers },
      });
      setResult(data);
      onSubmitted?.();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Submission failed");
    } finally {
      setBusy(false);
    }
  }

  if (result) {
    return (
      <div className="card">
        <h2>Your answers are saved</h2>
        <p className="muted">This is how the filter engine will search for you.</p>
        <h3>Your career statement</h3>
        <p>{result.career_interest_statement || "Not provided"}</p>
        <h3>Fields the engine will look for</h3>
        <div className="tags">
          {result.derived_fields.length > 0 ? (
            result.derived_fields.map((field) => (
              <span className="tag" key={field}>
                {field}
              </span>
            ))
          ) : (
            <span className="muted">No fields selected yet.</span>
          )}
        </div>
        <div style={{ marginTop: 16 }}>
          <button className="primary-btn" type="button" onClick={() => setResult(null)}>
            Edit answers
          </button>
        </div>
      </div>
    );
  }

  return (
    <form className="card" onSubmit={submit}>
      <h2>Career questionnaire</h2>
      <p className="muted">
        Answer these questions so we can find the exams and careers that fit you.
      </p>

      {questions.map((question) => (
        <div key={question.id}>
          {question.type === "multi" ? (
            <div className="prompt">{question.prompt}</div>
          ) : (
            <label htmlFor={`q-${question.id}`}>{question.prompt}</label>
          )}

          {question.type === "text" && (
            <input
              id={`q-${question.id}`}
              value={typeof answers[question.id] === "string" ? (answers[question.id] as string) : ""}
              onChange={(event) => setValue(question.id, event.target.value)}
            />
          )}

          {question.type === "number" && (
            <input
              id={`q-${question.id}`}
              type="number"
              value={typeof answers[question.id] === "number" ? String(answers[question.id]) : ""}
              onChange={(event) =>
                setValue(question.id, event.target.value === "" ? "" : Number(event.target.value))
              }
            />
          )}

          {question.type === "select" && (
            <select
              id={`q-${question.id}`}
              value={typeof answers[question.id] === "string" ? (answers[question.id] as string) : ""}
              onChange={(event) => setValue(question.id, event.target.value)}
            >
              <option value="">Choose an option</option>
              {(question.options ?? []).map((option) => (
                <option value={option.value} key={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          )}

          {question.type === "multi" &&
            (question.options ?? []).map((option) => (
              <label className="interest-option" key={option.value}>
                <input
                  type="checkbox"
                  checked={Array.isArray(answers[question.id]) &&
                    (answers[question.id] as string[]).includes(option.value)}
                  onChange={() => toggleMulti(question.id, option.value)}
                />
                <span>{option.label}</span>
              </label>
            ))}
        </div>
      ))}

      <div style={{ marginTop: 20 }}>
        <button className="primary-btn" type="submit" disabled={busy}>
          {busy ? "Saving..." : "Save answers"}
        </button>
      </div>

      {error && <div className="error-box">{error}</div>}
    </form>
  );
}
