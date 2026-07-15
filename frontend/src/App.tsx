import { useState } from "react";
import { getRecommendations, RecommendError } from "./api";
import { MovieCard } from "./components/MovieCard";
import { SearchBar } from "./components/SearchBar";
import { SkeletonGrid } from "./components/SkeletonGrid";
import { EmptyState, ErrorState } from "./components/States";
import type { RecommendResponse } from "./types";

type Status = "idle" | "loading" | "error" | "success";

export default function App() {
  const [status, setStatus] = useState<Status>("idle");
  const [data, setData] = useState<RecommendResponse | null>(null);
  const [error, setError] = useState<{ message: string; suggestions: string[] }>({
    message: "",
    suggestions: [],
  });

  const run = async (title: string) => {
    setStatus("loading");
    setData(null);
    try {
      const res = await getRecommendations(title, 10);
      setData(res);
      setStatus("success");
    } catch (e) {
      const err = e as RecommendError;
      setError({ message: err.message, suggestions: err.suggestions ?? [] });
      setStatus("error");
    }
  };

  return (
    <div className="mx-auto min-h-screen max-w-6xl px-4 py-10">
      <header className="mb-8 text-center">
        <h1 className="text-3xl font-bold tracking-tight sm:text-4xl">🎬 Movie Recommender</h1>
        <p className="mt-2 text-slate-400">
          Content-based recommendations from the TMDB 5000 dataset, blended with popularity.
        </p>
      </header>

      <div className="flex justify-center">
        <SearchBar onSubmit={run} />
      </div>

      <main className="mt-10">
        {status === "idle" && <EmptyState />}

        {status === "loading" && <SkeletonGrid count={10} />}

        {status === "error" && (
          <ErrorState message={error.message} suggestions={error.suggestions} onPick={run} />
        )}

        {status === "success" && data && (
          <>
            <p className="mb-4 text-sm text-slate-400">
              Because you searched{" "}
              <span className="font-medium text-slate-200">{data.resolved_title}</span> — showing{" "}
              {data.count} recommendations.{" "}
              <span className="text-slate-500">Click any movie to explore further.</span>
            </p>
            <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5">
              {data.results.map((m) => (
                <MovieCard
                  key={m.id}
                  movie={m}
                  onExplore={(title) => {
                    window.scrollTo({ top: 0, behavior: "smooth" });
                    void run(title);
                  }}
                />
              ))}
            </div>
          </>
        )}
      </main>

      <footer className="mt-16 text-center text-xs text-slate-600">
        Data: TMDB 5000 dataset. This product uses the TMDB API but is not endorsed or certified by
        TMDB.
      </footer>
    </div>
  );
}
