const baseUrl = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

const tokenStorageKey = "jobculler_jwt";

function getAuthToken() {
  if (typeof window === "undefined") {
    return undefined;
  }
  return window.localStorage.getItem(tokenStorageKey) ?? undefined;
}

function buildHeaders(extra?: Record<string, string>) {
  const headers: Record<string, string> = { ...extra };
  const token = getAuthToken();
  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }
  return headers;
}

export async function submitManualUrl(url: string, notes?: string) {
  const res = await fetch(`${baseUrl}/jobs/manual`, {
    method: "POST",
    headers: buildHeaders({ "Content-Type": "application/json" }),
    body: JSON.stringify({ url, notes })
  });

  if (!res.ok) {
    throw new Error(`Request failed: ${res.status}`);
  }

  return res.json();
}

export async function listJobs() {
  const res = await fetch(`${baseUrl}/jobs`, {
    headers: buildHeaders()
  });

  if (!res.ok) {
    throw new Error(`Request failed: ${res.status}`);
  }

  return res.json() as Promise<{ items: Array<{ id: string; title?: string; company_name?: string; status?: string }>; count: number }>;
}

export async function listQueue(failedOnly = false) {
  const path = failedOnly ? "queue/failed" : "queue";
  const res = await fetch(`${baseUrl}/${path}`, {
    headers: buildHeaders()
  });

  if (!res.ok) {
    throw new Error(`Request failed: ${res.status}`);
  }

  return res.json() as Promise<{ items: Array<{ id: string; task_type: string; status: string; attempts: number; last_error?: string | null }>; count: number }>;
}

export async function getSourceConfig() {
  const res = await fetch(`${baseUrl}/source-config`, {
    headers: buildHeaders()
  });

  if (!res.ok) {
    throw new Error(`Request failed: ${res.status}`);
  }

  return res.json() as Promise<{ yaml: string; source: string }>;
}

export async function updateSourceConfig(yaml: string) {
  const res = await fetch(`${baseUrl}/source-config`, {
    method: "PUT",
    headers: buildHeaders({ "Content-Type": "application/json" }),
    body: JSON.stringify({ yaml })
  });

  if (!res.ok) {
    throw new Error(`Request failed: ${res.status}`);
  }

  return res.json();
}
