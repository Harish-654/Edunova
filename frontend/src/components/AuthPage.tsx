import { useState } from "react";
import type { FormEvent } from "react";
import { api } from "../api";
import type { AuthResponse, Student } from "../types";

interface Props {
  onAuth: (token: string, student: Student) => void;
}

export default function AuthPage({ onAuth }: Props) {
  const [mode, setMode] = useState<"login" | "register">("login");
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  async function submit(event: FormEvent) {
    event.preventDefault();
    setBusy(true);
    setError(null);
    try {
      const path = mode === "login" ? "/auth/login" : "/auth/register";
      const body =
        mode === "login"
          ? { email, password }
          : { full_name: fullName, email, password };
      const data = await api<AuthResponse>(path, { method: "POST", body });
      onAuth(data.access_token, data.student);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="auth-wrap">
      <div className="card">
        <div className="brand" style={{ marginBottom: 12 }}>
          EduNova
        </div>
        <div className="auth-tabs">
          <button
            className={mode === "login" ? "active" : ""}
            onClick={() => setMode("login")}
            type="button"
          >
            Log in
          </button>
          <button
            className={mode === "register" ? "active" : ""}
            onClick={() => setMode("register")}
            type="button"
          >
            Create account
          </button>
        </div>

        <form onSubmit={submit}>
          {mode === "register" && (
            <>
              <label htmlFor="fullName">Full name</label>
              <input
                id="fullName"
                value={fullName}
                onChange={(event) => setFullName(event.target.value)}
                required
                minLength={2}
              />
            </>
          )}

          <label htmlFor="email">Email</label>
          <input
            id="email"
            type="email"
            value={email}
            onChange={(event) => setEmail(event.target.value)}
            required
          />

          <label htmlFor="password">Password</label>
          <input
            id="password"
            type="password"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            required
            minLength={6}
          />

          <div style={{ marginTop: 18 }}>
            <button className="primary-btn" type="submit" disabled={busy}>
              {busy ? "Please wait..." : mode === "login" ? "Log in" : "Create account"}
            </button>
          </div>

          {error && <div className="error-box">{error}</div>}
        </form>
      </div>
      <p className="muted" style={{ textAlign: "center" }}>
        Students register here. Admin accounts are created with{" "}
        <code>create_admin.py</code>.
      </p>
    </div>
  );
}
