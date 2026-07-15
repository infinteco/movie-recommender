export interface Recommendation {
  id: number;
  title: string;
  score: number;
  similarity: number;
  vote_average: number;
  genres: string[];
  release_date: string | null;
  poster_url: string | null;
}

export interface RecommendResponse {
  query: string;
  resolved_title: string;
  count: number;
  results: Recommendation[];
}

export interface ApiError {
  detail: string;
  suggestions?: string[];
}
