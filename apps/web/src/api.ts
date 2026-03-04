import { getAccessToken } from "./supabase";

const baseUrl = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

async function buildHeaders(extra?: Record<string, string>) {
  const headers: Record<string, string> = { ...extra };
  const token = await getAccessToken();
  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }
  return headers;
}

export async function submitManualUrl(url: string, notes?: string) {
  const res = await fetch(`${baseUrl}/jobs/manual`, {
    method: "POST",
    headers: await buildHeaders({ "Content-Type": "application/json" }),
    body: JSON.stringify({ url, notes })
  });

  if (!res.ok) {
    throw new Error(`Request failed: ${res.status}`);
  }

  return res.json();
}

export async function submitIdealJob(url: string, whyText: string) {
  const res = await fetch(`${baseUrl}/jobs/ideal`, {
    method: "POST",
    headers: await buildHeaders({ "Content-Type": "application/json" }),
    body: JSON.stringify({ url, why_text: whyText })
  });

  if (!res.ok) {
    throw new Error(`Request failed: ${res.status}`);
  }

  return res.json();
}

export async function listJobs() {
  const res = await fetch(`${baseUrl}/jobs`, {
    headers: await buildHeaders()
  });

  if (!res.ok) {
    throw new Error(`Request failed: ${res.status}`);
  }

  return res.json() as Promise<{ items: Array<{ id: string; title?: string; company_name?: string; status?: string }>; count: number }>;
}

export async function listQueue(failedOnly = false) {
  const path = failedOnly ? "queue/failed" : "queue";
  const res = await fetch(`${baseUrl}/${path}`, {
    headers: await buildHeaders()
  });

  if (!res.ok) {
    throw new Error(`Request failed: ${res.status}`);
  }

  return res.json() as Promise<{ items: Array<{ id: string; task_type: string; status: string; attempts: number; last_error?: string | null }>; count: number }>;
}

export async function getSourceConfig() {
  const res = await fetch(`${baseUrl}/source-config`, {
    headers: await buildHeaders()
  });

  if (!res.ok) {
    throw new Error(`Request failed: ${res.status}`);
  }

  return res.json() as Promise<{ yaml: string; source: string }>;
}

export async function updateSourceConfig(yaml: string) {
  const res = await fetch(`${baseUrl}/source-config`, {
    method: "PUT",
    headers: await buildHeaders({ "Content-Type": "application/json" }),
    body: JSON.stringify({ yaml })
  });

  if (!res.ok) {
    throw new Error(`Request failed: ${res.status}`);
  }

  return res.json();
}

export async function runPipeline(maxCycles = 3) {
  const res = await fetch(`${baseUrl}/workflows/run-pipeline`, {
    method: "POST",
    headers: await buildHeaders({ "Content-Type": "application/json" }),
    body: JSON.stringify({ run_worker: true, max_cycles: maxCycles })
  });

  if (!res.ok) {
    throw new Error(`Request failed: ${res.status}`);
  }

  return res.json() as Promise<{
    status: string;
    tasks: number;
    run_worker?: boolean;
    max_cycles?: number;
    source_ids?: string[];
    message?: string;
  }>;
}

export async function getPreferences() {
  const res = await fetch(`${baseUrl}/user/preferences`, {
    headers: await buildHeaders()
  });

  if (!res.ok) {
    throw new Error(`Request failed: ${res.status}`);
  }

  return res.json() as Promise<{
    location?: string | null;
    work_mode?: string | null;
    salary_min?: number | null;
    salary_max?: number | null;
    salary_currency?: string | null;
    salary_period?: string | null;
    sector?: string | null;
    target_role?: string | null;
    company_size?: string | null;
  }>;
}

export async function updatePreferences(payload: {
  location?: string;
  work_mode?: string;
  salary?: string;
  salary_min?: number;
  salary_max?: number;
  salary_currency?: string;
  salary_period?: string;
  sector?: string;
  target_role?: string;
  company_size?: string;
}) {
  const res = await fetch(`${baseUrl}/user/preferences`, {
    method: "PUT",
    headers: await buildHeaders({ "Content-Type": "application/json" }),
    body: JSON.stringify(payload)
  });

  if (!res.ok) {
    throw new Error(`Request failed: ${res.status}`);
  }

  return res.json();
}

export async function getValues() {
  const res = await fetch(`${baseUrl}/user/values`, {
    headers: await buildHeaders()
  });

  if (!res.ok) {
    throw new Error(`Request failed: ${res.status}`);
  }

  return res.json() as Promise<{ values?: string[] | null; dream_job_description?: string | null }>;
}

export async function updateValues(payload: { values?: string[]; dream_job_description?: string }) {
  const res = await fetch(`${baseUrl}/user/values`, {
    method: "PUT",
    headers: await buildHeaders({ "Content-Type": "application/json" }),
    body: JSON.stringify(payload)
  });

  if (!res.ok) {
    throw new Error(`Request failed: ${res.status}`);
  }

  return res.json();
}
