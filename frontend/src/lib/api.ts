import type { PracticeRequest, PracticeResponse, PracticeHistoryItem, LibraryText } from "./types";

const API_BASE = "/api/v1";

async function fetchJSON<T>(url: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${url}`, {
    headers: { "Content-Type": "application/json", ...options?.headers },
    ...options,
  });
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: "Request failed" }));
    throw new Error(error.detail || `HTTP ${response.status}`);
  }
  return response.json();
}

export async function generatePractice(request: PracticeRequest): Promise<PracticeResponse> {
  return fetchJSON<PracticeResponse>("/practice/generate", {
    method: "POST",
    body: JSON.stringify(request),
  });
}

export async function generatePracticeStream(
  request: PracticeRequest,
  onToken: (token: string) => void,
  onDone: () => void,
): Promise<void> {
  const response = await fetch(`${API_BASE}/practice/generate/stream`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    throw new Error(`HTTP ${response.status}`);
  }

  const reader = response.body?.getReader();
  if (!reader) throw new Error("No response body");

  const decoder = new TextDecoder();
  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    const chunk = decoder.decode(value);
    const lines = chunk.split("\n");

    for (const line of lines) {
      if (line.startsWith("data: ")) {
        const data = JSON.parse(line.slice(6));
        if (data.token === "\n[DONE]") {
          onDone();
        } else {
          onToken(data.token);
        }
      }
    }
  }
}

export async function getPractice(id: string): Promise<PracticeResponse> {
  return fetchJSON<PracticeResponse>(`/practice/${id}`);
}

export async function ratePractice(id: string, rating: number, notes?: string): Promise<void> {
  await fetchJSON(`/practice/${id}/rate?rating=${rating}${notes ? `&notes=${encodeURIComponent(notes)}` : ""}`, {
    method: "PATCH",
  });
}

export async function getHistory(limit = 20, offset = 0): Promise<{ practices: PracticeHistoryItem[] }> {
  return fetchJSON(`/history?limit=${limit}&offset=${offset}`);
}

export async function getLibrary(): Promise<{ texts: LibraryText[]; stats: { chunks_count: number; techniques_count: number } }> {
  return fetchJSON("/ingest/library");
}

export async function uploadText(file: File, title: string, author?: string, tradition?: string): Promise<{ id: string }> {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("title", title);
  if (author) formData.append("author", author);
  if (tradition) formData.append("tradition", tradition);

  const response = await fetch(`${API_BASE}/ingest/upload`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    throw new Error(`Upload failed: HTTP ${response.status}`);
  }
  return response.json();
}

export async function processText(textId: string): Promise<void> {
  await fetchJSON(`/ingest/process/${textId}`, { method: "POST" });
}

export async function getHealth(): Promise<{ status: string; ollama: string }> {
  return fetchJSON("/health");
}
