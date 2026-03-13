import type React from "react";

import type { Job } from "./types";

type JobsTabProps = {
  jobs: Job[];
  jobsError: string | null;
  url: string;
  notes: string;
  status: string | null;
  onSubmit: (event: React.FormEvent) => void;
  setUrl: (value: string) => void;
  setNotes: (value: string) => void;
  theme: {
    card: React.CSSProperties;
    sectionTitle: React.CSSProperties;
  };
};

export function JobsTab({
  jobs,
  jobsError,
  url,
  notes,
  status,
  onSubmit,
  setUrl,
  setNotes,
  theme
}: JobsTabProps) {
  return (
    <section style={theme.card}>
      <h2 style={theme.sectionTitle}>Manual Job Intake</h2>
      <p style={{ color: "#556" }}>Capture an opportunity directly.</p>

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

      <h2 style={theme.sectionTitle}>Job List</h2>
      {jobsError && <p>{jobsError}</p>}
      {!jobsError && jobs.length === 0 && <p>No jobs yet.</p>}
      <ul>
        {jobs.map((job) => (
          <li key={job.id}>
            <strong>{job.title || "Untitled Role"}</strong> — {job.company_name || "Unknown Company"} (
            {job.status || "new"})
          </li>
        ))}
      </ul>
    </section>
  );
}
