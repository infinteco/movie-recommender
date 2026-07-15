import type { ApiError, RecommendResponse } from "./types";

const BASE_URL = (import.meta.env.VITE_API_URL ?? "http://localhost:8000").replace(/\/$/, "");

export class RecommendError extends Error {
  suggestions: string[];
  constructor(message: string, suggestions: string[] = []) {
    super(message);
    this.suggestions = suggestions;
  }
}

/** Search-as-you-type: returns matching catalog titles. */
export async function searchTitles(q: string, signal?: AbortSignal): Promise<string[]> {
  if (!q.trim()) return [];
  const res = await fetch(`${BASE_URL}/movies/search?q=${encodeURIComponent(q)}`, { signal });
  if (!res.ok) return [];
  const data = (await res.json()) as { results: string[] };
  return data.results;
}

/** Fetch recommendations for a title. Throws RecommendError on 404/failure. */
export async function getRecommendations(title: string, k = 10): Promise<RecommendResponse> {
  const res = await fetch(
    `${BASE_URL}/recommend?title=${encodeURIComponent(title)}&k=${k}`,
  );
  if (res.ok) {
    return (await res.json()) as RecommendResponse;
  }
  let payload: ApiError | null = null;
  try {
    payload = (await res.json()) as ApiError;
  } catch {
    payload = null;
  }
  if (res.status === 404 && payload) {
    throw new RecommendError(payload.detail, payload.suggestions ?? []);
  }
  throw new RecommendError(payload?.detail ?? `Request failed (${res.status}).`);
}
