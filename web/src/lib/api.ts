const API_BASE = process.env.NEXT_PUBLIC_API_URL || "";

export interface LinkPayload {
  url: string;
  notes?: string;
  tags?: string[];
}

export interface LinkResponse {
  id: string;
  url: string;
  title?: string;
  summary: string;
  smart_tags: string[];
  confidence_score: number;
}

export interface DashboardResponse {
  top_reads: LinkResponse[];
  trending_topics: string[];
}

export async function createLink(payload: LinkPayload): Promise<LinkResponse> {
  const res = await fetch(`${API_BASE}/api/links`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });

  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.message || "Failed to create link");
  }
  return res.json();
}

export async function fetchDashboard(): Promise<DashboardResponse> {
  const res = await fetch(`${API_BASE}/api/dashboard`);
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.message || "Failed to fetch dashboard");
  }
  return res.json();
}

export async function fetchLinkHealth(id: string): Promise<any> {
  const res = await fetch(`${API_BASE}/api/links/${id}/health`);
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.message || "Failed to fetch link health");
  }
  return res.json();
}