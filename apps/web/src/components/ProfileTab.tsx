import type React from "react";

import type { Preferences } from "./types";

type ProfileTabProps = {
  idealUrl: string;
  idealWhy: string;
  idealStatus: string | null;
  onSubmitIdeal: (event: React.FormEvent) => void;
  setIdealUrl: (value: string) => void;
  setIdealWhy: (value: string) => void;
  preferences: Preferences;
  setPreferences: (value: Preferences) => void;
  preferencesStatus: string | null;
  savePreferences: () => void;
  loadPreferences: () => void;
  coreValues: string;
  dreamJob: string;
  valuesStatus: string | null;
  setCoreValues: (value: string) => void;
  setDreamJob: (value: string) => void;
  saveValues: () => void;
  loadValues: () => void;
  resumeText: string;
  resumeStatus: string | null;
  setResumeText: (value: string) => void;
  saveResume: () => void;
  loadResume: () => void;
  theme: {
    card: React.CSSProperties;
    sectionTitle: React.CSSProperties;
  };
};

export function ProfileTab({
  idealUrl,
  idealWhy,
  idealStatus,
  onSubmitIdeal,
  setIdealUrl,
  setIdealWhy,
  preferences,
  setPreferences,
  preferencesStatus,
  savePreferences,
  loadPreferences,
  coreValues,
  dreamJob,
  valuesStatus,
  setCoreValues,
  setDreamJob,
  saveValues,
  loadValues,
  resumeText,
  resumeStatus,
  setResumeText,
  saveResume,
  loadResume,
  theme
}: ProfileTabProps) {
  return (
    <section style={theme.card}>
      <h2>Core Preferences</h2>
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
        <label>
          Location
          <input
            type="text"
            value={preferences.location}
            onChange={(e) => setPreferences({ ...preferences, location: e.target.value })}
            style={{ width: "100%", padding: 8, marginTop: 6 }}
          />
        </label>
        <label>
          Work Mode (remote/hybrid/onsite)
          <input
            type="text"
            value={preferences.work_mode}
            onChange={(e) => setPreferences({ ...preferences, work_mode: e.target.value })}
            style={{ width: "100%", padding: 8, marginTop: 6 }}
          />
        </label>
        <label>
          Salary (free text)
          <input
            type="text"
            value={preferences.salary}
            onChange={(e) => setPreferences({ ...preferences, salary: e.target.value })}
            style={{ width: "100%", padding: 8, marginTop: 6 }}
            placeholder="$140k+"
          />
        </label>
        <label>
          Salary Period
          <select
            value={preferences.salary_period}
            onChange={(e) => setPreferences({ ...preferences, salary_period: e.target.value })}
            style={{ width: "100%", padding: 8, marginTop: 6 }}
          >
            <option value="">Select period</option>
            <option value="year">Year</option>
            <option value="month">Month</option>
            <option value="week">Week</option>
            <option value="day">Day</option>
            <option value="hour">Hour</option>
          </select>
        </label>
        <label>
          Sector
          <input
            type="text"
            value={preferences.sector}
            onChange={(e) => setPreferences({ ...preferences, sector: e.target.value })}
            style={{ width: "100%", padding: 8, marginTop: 6 }}
          />
        </label>
        <label>
          Target Role
          <input
            type="text"
            value={preferences.target_role}
            onChange={(e) => setPreferences({ ...preferences, target_role: e.target.value })}
            style={{ width: "100%", padding: 8, marginTop: 6 }}
          />
        </label>
        <label>
          Company Size
          <input
            type="text"
            value={preferences.company_size}
            onChange={(e) => setPreferences({ ...preferences, company_size: e.target.value })}
            style={{ width: "100%", padding: 8, marginTop: 6 }}
            placeholder="50-200"
          />
        </label>
      </div>
      <div style={{ display: "flex", gap: 8, marginTop: 10, alignItems: "center" }}>
        <button type="button" onClick={savePreferences}>
          Save Preferences
        </button>
        <button type="button" onClick={loadPreferences}>
          Reload
        </button>
        {preferencesStatus && <span>{preferencesStatus}</span>}
      </div>

      <hr style={{ margin: "32px 0" }} />

      <h2>Core Values</h2>
      <label>
        Values (one per line)
        <textarea
          value={coreValues}
          onChange={(e) => setCoreValues(e.target.value)}
          style={{ width: "100%", minHeight: 120, padding: 10, fontFamily: "monospace", marginTop: 6 }}
        />
      </label>
      <label style={{ display: "block", marginTop: 12 }}>
        Dream Job Description
        <textarea
          value={dreamJob}
          onChange={(e) => setDreamJob(e.target.value)}
          style={{ width: "100%", minHeight: 120, padding: 10, fontFamily: "monospace", marginTop: 6 }}
        />
      </label>
      <div style={{ display: "flex", gap: 8, marginTop: 10, alignItems: "center" }}>
        <button type="button" onClick={saveValues}>
          Save Values
        </button>
        <button type="button" onClick={loadValues}>
          Reload
        </button>
        {valuesStatus && <span>{valuesStatus}</span>}
      </div>

      <hr style={{ margin: "32px 0" }} />

      <h2>Resume</h2>
      <p style={{ color: "#555" }}>Paste a text version of your resume for query generation.</p>
      <textarea
        value={resumeText}
        onChange={(e) => setResumeText(e.target.value)}
        style={{ width: "100%", minHeight: 220, padding: 10, fontFamily: "monospace" }}
        placeholder="Paste resume text here"
      />
      <div style={{ display: "flex", gap: 8, marginTop: 10, alignItems: "center" }}>
        <button type="button" onClick={saveResume}>
          Save Resume
        </button>
        <button type="button" onClick={loadResume}>
          Reload
        </button>
        {resumeStatus && <span>{resumeStatus}</span>}
      </div>

      <hr style={{ margin: "32px 0" }} />

      <h2>Ideal Job Intake</h2>
      <p style={{ color: "#555" }}>Provide a job URL and why it is ideal for you.</p>
      <form onSubmit={onSubmitIdeal}>
        <div style={{ marginBottom: 12 }}>
          <label>
            Job URL
            <input
              type="url"
              required
              value={idealUrl}
              onChange={(e) => setIdealUrl(e.target.value)}
              style={{ width: "100%", padding: 8, marginTop: 6 }}
              placeholder="https://company.com/careers/ideal-role"
            />
          </label>
        </div>
        <div style={{ marginBottom: 12 }}>
          <label>
            Why This Is Ideal
            <textarea
              value={idealWhy}
              onChange={(e) => setIdealWhy(e.target.value)}
              style={{ width: "100%", padding: 8, marginTop: 6, minHeight: 120 }}
              placeholder="Describe why this role is a great fit for you."
            />
          </label>
        </div>
        <button type="submit" style={{ padding: "8px 14px" }}>
          Save Ideal Job
        </button>
      </form>
      {idealStatus && <p style={{ marginTop: 16 }}>{idealStatus}</p>}
    </section>
  );
}
