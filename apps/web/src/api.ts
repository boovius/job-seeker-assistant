const baseUrl = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

function authHeader() {
  // TODO: wire Supabase auth token retrieval
  return "Bearer REPLACE_WITH_TOKEN";
}

export async function submitManualUrl(url: string, notes?: string) {
  const res = await fetch(`${baseUrl}/jobs/manual`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: authHeader()
    },
    body: JSON.stringify({ url, notes })
  });

  if (!res.ok) {
    throw new Error(`Request failed: ${res.status}`);
  }

  return res.json();
}

export async function listJobs() {
  const res = await fetch(`${baseUrl}/jobs`, {
    headers: {
      Authorization: authHeader()
    }
  });

  if (!res.ok) {
    throw new Error(`Request failed: ${res.status}`);
  }

  return res.json() as Promise<{ items: Array<{ id: string; title?: string; company_name?: string; status?: string }>; count: number }>;
}
