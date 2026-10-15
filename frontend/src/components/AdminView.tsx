import { useEffect, useState } from "react";
import type { FormEvent } from "react";
import { api } from "../api";
import type {
  Anomaly,
  CrawlResult,
  Overview,
  Payload,
  Scholarship,
  Source,
} from "../types";

interface Props {
  tab: string;
}

function formatMoney(value: number | null | undefined): string {
  if (value === null || value === undefined) {
    return "—";
  }
  return "₹ " + value.toLocaleString("en-IN");
}

function OverviewSection() {
  const [data, setData] = useState<Overview | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api<Overview>("/admin/overview")
      .then(setData)
      .catch((err) => setError(err instanceof Error ? err.message : "Failed to load"));
  }, []);

  if (error) {
    return <div className="error-box">{error}</div>;
  }
  if (!data) {
    return <div className="empty">Loading overview...</div>;
  }

  const stats = [
    { label: "Students", value: data.students },
    { label: "Exams", value: data.exams },
    { label: "Scholarships", value: data.scholarships },
    { label: "Crawl sources", value: data.sources },
    { label: "Fetched payloads", value: data.payloads },
    { label: "Anomalies", value: data.anomalies },
  ];

  return (
    <div>
      <div className="card">
        <h2>System overview</h2>
        <p className="muted">Live counts from the database.</p>
      </div>
      <div className="grid">
        {stats.map((stat) => (
          <div className="stat" key={stat.label}>
            <div className="value">{stat.value}</div>
            <div className="label">{stat.label}</div>
          </div>
        ))}
      </div>
    </div>
  );
}

function IngestionSection() {
  const [sources, setSources] = useState<Source[]>([]);
  const [anomalies, setAnomalies] = useState<Anomaly[]>([]);
  const [payloads, setPayloads] = useState<Payload[]>([]);
  const [results, setResults] = useState<CrawlResult[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [name, setName] = useState("");
  const [url, setUrl] = useState("");

  async function loadAll() {
    try {
      const [sourceList, anomalyList, payloadList] = await Promise.all([
        api<Source[]>("/ingestion/sources"),
        api<Anomaly[]>("/ingestion/anomalies?limit=10"),
        api<Payload[]>("/ingestion/payloads?limit=10"),
      ]);
      setSources(sourceList);
      setAnomalies(anomalyList);
      setPayloads(payloadList);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load ingestion data");
    }
  }

  useEffect(() => {
    loadAll();
  }, []);

  async function runCrawl(sourceId?: string) {
    setBusy(true);
    setError(null);
    try {
      const path = sourceId ? `/ingestion/run?source_id=${sourceId}` : "/ingestion/run";
      const data = await api<CrawlResult[]>(path, { method: "POST" });
      setResults(data);
      await loadAll();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Crawl failed");
    } finally {
      setBusy(false);
    }
  }

  async function addSource(event: FormEvent) {
    event.preventDefault();
    setBusy(true);
    setError(null);
    try {
      await api("/ingestion/sources", {
        method: "POST",
        body: { target_name: name, target_url: url, is_active: true },
      });
      setName("");
      setUrl("");
      await loadAll();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to add source");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div>
      <div className="card">
        <h2>Crawling sources</h2>
        <p className="muted">
          Fetch pages into raw storage, then check what parsing found.
        </p>

        <div className="row" style={{ marginTop: 12 }}>
          <button
            className="primary-btn"
            onClick={() => runCrawl()}
            disabled={busy}
            type="button"
          >
            {busy ? "Running..." : "Run all crawlers"}
          </button>
        </div>

        <table style={{ marginTop: 14 }}>
          <thead>
            <tr>
              <th>Source</th>
              <th>URL</th>
              <th>Schedule</th>
              <th>Status</th>
              <th />
            </tr>
          </thead>
          <tbody>
            {sources.map((source) => (
              <tr key={source.source_id}>
                <td>{source.target_name}</td>
                <td>{source.target_url}</td>
                <td>{source.cron_expression}</td>
                <td>
                  <span className={`badge ${source.is_active ? "ok" : "neutral"}`}>
                    {source.is_active ? "Active" : "Paused"}
                  </span>
                </td>
                <td>
                  <button
                    className="link-btn"
                    onClick={() => runCrawl(source.source_id)}
                    disabled={busy}
                    type="button"
                  >
                    Crawl
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>

        <form onSubmit={addSource} className="row" style={{ marginTop: 16 }}>
          <input
            placeholder="Source name"
            value={name}
            onChange={(event) => setName(event.target.value)}
            required
          />
          <input
            placeholder="https://..."
            value={url}
            onChange={(event) => setUrl(event.target.value)}
            required
          />
          <button className="primary-btn" type="submit" disabled={busy}>
            Add source
          </button>
        </form>
      </div>

      {results.length > 0 && (
        <div className="card">
          <h2>Last crawl results</h2>
          <table>
            <thead>
              <tr>
                <th>Source</th>
                <th>Fetched</th>
                <th>Missing fields</th>
                <th>Error</th>
              </tr>
            </thead>
            <tbody>
              {results.map((result) => (
                <tr key={result.source_id}>
                  <td>{result.target_name}</td>
                  <td>{result.fetched ? "Yes" : "No"}</td>
                  <td>{result.missing_fields.join(", ") || "none"}</td>
                  <td className="muted">{result.error || "—"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <div className="card">
        <h2>Recent anomalies</h2>
        <p className="muted">Fields the parser could not find in fetched pages.</p>
        <table>
          <thead>
            <tr>
              <th>When</th>
              <th>Error</th>
              <th>Missing</th>
            </tr>
          </thead>
          <tbody>
            {anomalies.map((anomaly) => (
              <tr key={anomaly.log_id}>
                <td>{new Date(anomaly.logged_at).toLocaleString("en-IN")}</td>
                <td>
                  <span className="badge no">{anomaly.error_code}</span>
                </td>
                <td>{(anomaly.missing_fields ?? []).join(", ") || "—"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="card">
        <h2>Recent raw payloads</h2>
        <table>
          <thead>
            <tr>
              <th>Fetched at</th>
              <th>Processed</th>
            </tr>
          </thead>
          <tbody>
            {payloads.map((payload) => (
              <tr key={payload.payload_id}>
                <td>{new Date(payload.fetched_at).toLocaleString("en-IN")}</td>
                <td>
                  <span className={`badge ${payload.is_processed ? "ok" : "no"}`}>
                    {payload.is_processed ? "Processed" : "Pending"}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {error && <div className="error-box">{error}</div>}
    </div>
  );
}

function ScholarshipsSection() {
  const [items, setItems] = useState<Scholarship[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  const [title, setTitle] = useState("");
  const [provider, setProvider] = useState("");
  const [amount, setAmount] = useState("");
  const [income, setIncome] = useState("");

  async function load() {
    try {
      setItems(await api<Scholarship[]>("/scholarships"));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load scholarships");
    }
  }

  useEffect(() => {
    load();
  }, []);

  async function createScholarship(event: FormEvent) {
    event.preventDefault();
    setBusy(true);
    setError(null);
    setNotice(null);
    try {
      const body: Record<string, unknown> = { title };
      if (provider) {
        body.provider_name = provider;
      }
      if (amount) {
        body.max_amount = Number(amount);
      }
      if (income) {
        body.max_income_limit = Number(income);
      }
      await api("/admin/scholarships", { method: "POST", body });
      setTitle("");
      setProvider("");
      setAmount("");
      setIncome("");
      setNotice("Scholarship created.");
      await load();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to create");
    } finally {
      setBusy(false);
    }
  }

  async function updateAmount(item: Scholarship, value: string) {
    setBusy(true);
    setError(null);
    setNotice(null);
    try {
      await api(`/admin/scholarships/${item.scholarship_id}`, {
        method: "PUT",
        body: { max_amount: value === "" ? null : Number(value) },
      });
      setNotice(`Updated "${item.title}".`);
      await load();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to update");
    } finally {
      setBusy(false);
    }
  }

  async function removeScholarship(item: Scholarship) {
    if (!window.confirm(`Delete "${item.title}"?`)) {
      return;
    }
    setBusy(true);
    setError(null);
    try {
      await api(`/admin/scholarships/${item.scholarship_id}`, { method: "DELETE" });
      setNotice("Scholarship deleted.");
      await load();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to delete");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div>
      <div className="card">
        <h2>Add scholarship</h2>
        <form onSubmit={createScholarship}>
          <label htmlFor="s-title">Title</label>
          <input
            id="s-title"
            value={title}
            onChange={(event) => setTitle(event.target.value)}
            required
          />

          <label htmlFor="s-provider">Provider</label>
          <input
            id="s-provider"
            value={provider}
            onChange={(event) => setProvider(event.target.value)}
          />

          <div className="row">
            <div style={{ flex: 1 }}>
              <label htmlFor="s-amount">Max amount (₹)</label>
              <input
                id="s-amount"
                type="number"
                value={amount}
                onChange={(event) => setAmount(event.target.value)}
              />
            </div>
            <div style={{ flex: 1 }}>
              <label htmlFor="s-income">Family income limit (₹)</label>
              <input
                id="s-income"
                type="number"
                value={income}
                onChange={(event) => setIncome(event.target.value)}
              />
            </div>
          </div>

          <div style={{ marginTop: 16 }}>
            <button className="primary-btn" type="submit" disabled={busy}>
              {busy ? "Saving..." : "Add scholarship"}
            </button>
          </div>

          {notice && <div className="success-box">{notice}</div>}
          {error && <div className="error-box">{error}</div>}
        </form>
      </div>

      <div className="card">
        <h2>Scholarships</h2>
        <table>
          <thead>
            <tr>
              <th>Title</th>
              <th>Provider</th>
              <th>Max amount</th>
              <th>Income limit</th>
              <th />
            </tr>
          </thead>
          <tbody>
            {items.map((item) => (
              <tr key={item.scholarship_id}>
                <td>{item.title}</td>
                <td>{item.provider_name || "—"}</td>
                <td>
                  <div className="row">
                    <input
                      key={`${item.scholarship_id}-${item.max_amount}`}
                      type="number"
                      defaultValue={
                        item.max_amount === null || item.max_amount === undefined
                          ? ""
                          : String(item.max_amount)
                      }
                      id={`amount-${item.scholarship_id}`}
                    />
                    <button
                      className="link-btn"
                      type="button"
                      disabled={busy}
                      onClick={() => {
                        const input = document.getElementById(
                          `amount-${item.scholarship_id}`,
                        ) as HTMLInputElement | null;
                        if (input) {
                          void updateAmount(item, input.value);
                        }
                      }}
                    >
                      Save
                    </button>
                  </div>
                </td>
                <td>{formatMoney(item.max_income_limit)}</td>
                <td>
                  <button
                    className="danger-btn"
                    type="button"
                    disabled={busy}
                    onClick={() => removeScholarship(item)}
                  >
                    Delete
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default function AdminView({ tab }: Props) {
  if (tab === "ingestion") {
    return <IngestionSection />;
  }
  if (tab === "scholarships") {
    return <ScholarshipsSection />;
  }
  return <OverviewSection />;
}
