import { useEffect, useState } from "react";
import { getSourceConfig, listJobs, listQueue, submitManualUrl, updateSourceConfig } from "./api";
import { supabase } from "./supabase";

type Job = {
  id: string;
  title?: string;
  company_name?: string;
  status?: string;
};

type QueueItem = {
  id: string;
  task_type: string;
  status: string;
  attempts: number;
  last_error?: string | null;
};

export function App() {
  const [url, setUrl] = useState("");
  const [notes, setNotes] = useState("");
  const [status, setStatus] = useState<string | null>(null);
  const [jobs, setJobs] = useState<Job[]>([]);
  const [jobsError, setJobsError] = useState<string | null>(null);
  const [queue, setQueue] = useState<QueueItem[]>([]);
  const [queueError, setQueueError] = useState<string | null>(null);
  const [loadingQueue, setLoadingQueue] = useState(false);
  const [configText, setConfigText] = useState("");
  const [configStatus, setConfigStatus] = useState<string | null>(null);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [authStatus, setAuthStatus] = useState<string | null>(null);
  const [authUser, setAuthUser] = useState<string | null>(null);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setStatus("Submitting...");

    try {
      await submitManualUrl(url, notes || undefined);
      setStatus("Queued");
      setUrl("");
      setNotes("");
    } catch (err) {
      setStatus("Failed to submit");
    }
  }

  async function loadQueue(failedOnly = false) {
    setLoadingQueue(true);
    try {
      const res = await listQueue(failedOnly);
      setQueue(res.items);
      setQueueError(null);
    } catch (err) {
      setQueueError("Unable to load queue");
    } finally {
      setLoadingQueue(false);
    }
  }

  async function loadConfig() {
    try {
      const res = await getSourceConfig();
      setConfigText(res.yaml);
      setConfigStatus(`Loaded config from ${res.source}`);
    } catch (err) {
      setConfigStatus("Failed to load config");
    }
  }

  async function saveConfig() {
    setConfigStatus("Saving...");
    try {
      await updateSourceConfig(configText);
      setConfigStatus("Saved");
    } catch (err) {
      setConfigStatus("Save failed");
    }
  }

  useEffect(() => {
    listJobs()
      .then((res) => setJobs(res.items))
      .catch(() => setJobsError("Unable to load jobs"));
  }, []);

  useEffect(() => {
    loadQueue(true);
  }, []);

  useEffect(() => {
    loadConfig();
  }, []);

  useEffect(() => {
    supabase.auth.getSession().then(({ data }) => {
      setAuthUser(data.session?.user?.email ?? null);
    });
  }, []);

  async function signIn(e: React.FormEvent) {
    e.preventDefault();
    setAuthStatus("Signing in...");
    const { data, error } = await supabase.auth.signInWithPassword({ email, password });
    if (error) {
      setAuthStatus(`Sign-in failed: ${error.message}`);
      return;
    }
    setAuthStatus("Signed in.");
    setAuthUser(data.user?.email ?? null);
  }

  async function signOut() {
    await supabase.auth.signOut();
    setAuthUser(null);
    setAuthStatus("Signed out.");
  }

  return (
    <div style={{ maxWidth: 980, margin: "40px auto", fontFamily: "Georgia, serif" }}>
      <h1>Job Intelligence Agent</h1>
      <div style={{ marginBottom: 24, padding: 12, border: "1px solid #ddd", borderRadius: 8 }}>
        <h2>Sign In</h2>
        {authUser ? (
          <div style={{ display: "flex", gap: 12, alignItems: "center" }}>
            <span>Signed in as {authUser}</span>
            <button type="button" onClick={signOut}>
              Sign Out
            </button>
          </div>
        ) : (
          <form onSubmit={signIn} style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="Email"
              required
              style={{ flex: "1 1 200px", padding: 8 }}
            />
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Password"
              required
              style={{ flex: "1 1 200px", padding: 8 }}
            />
            <button type="submit">Sign In</button>
          </form>
        )}
        {authStatus && <p style={{ marginTop: 8 }}>{authStatus}</p>}
      </div>
      <p>Manual URL intake (Phase 1)</p>

      <form onSubmit={onSubmit}>
        <div style={{ marginBottom: 12 }}>
          <label>
            Job URL
            <input
              type="url"
              required
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              style={{ width: "100%", padding: 8, marginTop: 6 }}
              placeholder="https://company.com/careers/role"
            />
          </label>
        </div>

        <div style={{ marginBottom: 12 }}>
          <label>
            Notes
            <textarea
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              style={{ width: "100%", padding: 8, marginTop: 6, minHeight: 100 }}
              placeholder="Anything to remember about this role?"
            />
          </label>
        </div>

        <button type="submit" style={{ padding: "8px 14px" }}>
          Submit
        </button>
      </form>

      {status && <p style={{ marginTop: 16 }}>{status}</p>}

      <hr style={{ margin: "32px 0" }} />

      <h2>Source Config</h2>
      <p style={{ color: "#555" }}>Edit YAML to change keyword profiles and enabled sources.</p>
      <textarea
        value={configText}
        onChange={(e) => setConfigText(e.target.value)}
        style={{ width: "100%", minHeight: 240, padding: 10, fontFamily: "monospace" }}
      />
      <div style={{ display: "flex", gap: 8, marginTop: 8 }}>
        <button type="button" onClick={saveConfig}>
          Save Config
        </button>
        <button type="button" onClick={loadConfig}>
          Reload Config
        </button>
        {configStatus && <span>{configStatus}</span>}
      </div>

      <hr style={{ margin: "32px 0" }} />

      <h2>Queue Status</h2>
      <div style={{ display: "flex", gap: 8, marginBottom: 12 }}>
        <button type="button" onClick={() => loadQueue(false)} disabled={loadingQueue}>
          {loadingQueue ? "Loading..." : "Refresh All"}
        </button>
        <button type="button" onClick={() => loadQueue(true)} disabled={loadingQueue}>
          {loadingQueue ? "Loading..." : "Refresh Failed"}
        </button>
      </div>

      {queueError && <p>{queueError}</p>}
      {!queueError && queue.length === 0 && <p>No queue items.</p>}
      <ul>
        {queue.map((item) => (
          <li key={item.id}>
            <strong>{item.task_type}</strong> — {item.status} (attempts: {item.attempts})
            {item.last_error ? ` — ${item.last_error}` : ""}
          </li>
        ))}
      </ul>

      <hr style={{ margin: "32px 0" }} />

      <h2>Job List</h2>
      {jobsError && <p>{jobsError}</p>}
      {!jobsError && jobs.length === 0 && <p>No jobs yet.</p>}
      <ul>
        {jobs.map((job) => (
          <li key={job.id}>
            <strong>{job.title || "Untitled Role"}</strong> — {job.company_name || "Unknown Company"} ({job.status || "new"})
          </li>
        ))}
      </ul>
    </div>
  );
}
