import { useEffect, useState } from "react";
import { listJobs, listQueue, submitManualUrl } from "./api";

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

  useEffect(() => {
    listJobs()
      .then((res) => setJobs(res.items))
      .catch(() => setJobsError("Unable to load jobs"));
  }, []);

  useEffect(() => {
    listQueue(true)
      .then((res) => setQueue(res.items))
      .catch(() => setQueueError("Unable to load queue"));
  }, []);

  return (
    <div style={{ maxWidth: 900, margin: "40px auto", fontFamily: "Georgia, serif" }}>
      <h1>Job Intelligence Agent</h1>
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

      <h2>Failed Queue Items</h2>
      {queueError && <p>{queueError}</p>}
      {!queueError && queue.length === 0 && <p>No failed queue items.</p>}
      <ul>
        {queue.map((item) => (
          <li key={item.id}>
            <strong>{item.task_type}</strong> — {item.status} (attempts: {item.attempts})
            {item.last_error ? ` — ${item.last_error}` : ""}
          </li>
        ))
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
        ))
      </ul>
    </div>
  );
}
