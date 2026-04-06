import { useState } from "react";

import type { Job } from "./types";

type JobsTabProps = {
  jobs: Job[];
  jobsError: string | null;
  url: string;
  notes: string;
  status: string | null;
  onSubmit: (event: React.FormEvent) => void;
  onRefreshJobs?: () => void;
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
  onRefreshJobs,
  setUrl,
  setNotes,
  theme
}: JobsTabProps) {
  const [expanded, setExpanded] = useState<Record<string, boolean>>({});

  function toggleExpanded(jobId: string) {
    setExpanded((prev) => ({ ...prev, [jobId]: !prev[jobId] }));
  }

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

      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", gap: 12 }}>
        <h2 style={theme.sectionTitle}>Job List</h2>
        {onRefreshJobs && (
          <button type="button" onClick={onRefreshJobs}>
            Refresh Jobs
          </button>
        )}
      </div>
      {jobsError && <p>{jobsError}</p>}
      {!jobsError && jobs.length === 0 && <p>No jobs yet.</p>}
      <ul>
        {jobs.map((job) => (
          <li key={job.id}>
            <div style={{ marginBottom: 6 }}>
              <h3 style={{ margin: "0 0 4px" }}>{job.title || "Untitled Role"}</h3>
              <h4 style={{ margin: 0, color: "#0f172a" }}>{job.company_name || "Unknown Company"}</h4>
            </div>
            <div style={{ color: "#475569", fontSize: 14, marginBottom: 8 }}>
              {job.location ? job.location : "Location unknown"}
              {" · "}
              {job.remote_flag ? "Remote" : "On-site/Hybrid"}
              {job.status ? ` · ${job.status}` : ""}
            </div>
            {job.canonical_url && (
              <div style={{ marginBottom: 8 }}>
                <a href={job.canonical_url} target="_blank" rel="noreferrer">
                  View Listing
                </a>
              </div>
            )}
            {job.description ? (
              <div style={{ marginBottom: 12 }}>
                <div
                  className={expanded[job.id] ? "job-desc-expanded" : "job-desc-collapsed"}
                  style={{
                    color: "#334155",
                    lineHeight: "20px",
                    borderLeft: "3px solid #e2e8f0",
                    paddingLeft: 10
                  }}
                >
                  {job.description}
                </div>
                <button type="button" onClick={() => toggleExpanded(job.id)} style={{ marginTop: 6 }}>
                  {expanded[job.id] ? "Collapse" : "Expand"}
                </button>
              </div>
            ) : (
              <p style={{ color: "#64748b" }}>No description available.</p>
            )}
          </li>
        ))}
      </ul>
      <style>
        {`
          .job-desc-collapsed {
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
            overflow: hidden;
          }
          .job-desc-expanded {
            white-space: pre-wrap;
          }
        `}
      </style>
    </section>
  );
}
