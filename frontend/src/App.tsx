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
    window.scrollTo({ top: 0, behavior: "smooth" });
    try {
      const res = await getRecommendations(title, 12);
      setData(res);
      setStatus("success");
    } catch (e) {
      const err = e as RecommendError;
      setError({ message: err.message, suggestions: err.suggestions ?? [] });
      setStatus("error");
    }
  };

  const idle = status === "idle";

  return (
    <div className="min-h-screen">
      {/* Nav */}
      <header className="sticky top-0 z-30 border-b border-white/5 bg-[#0d0d0f]/80 backdrop-blur">
        <div className="mx-auto flex max-w-7xl items-center gap-4 px-4 py-3">
          <button
            onClick={() => {
              setStatus("idle");
              setData(null);
            }}
            className="flex shrink-0 items-center gap-2"
          >
            <span className="text-xl">🎬</span>
            <span className="text-lg font-extrabold tracking-tight">
              Cine<span className="text-[color:var(--gold)]">Match</span>
            </span>
          </button>
          {!idle && (
            <div className="flex-1">
              <SearchBar onSubmit={run} />
            </div>
          )}
          <a
            href="https://github.com/infinteco/movie-recommender"
            target="_blank"
            rel="noreferrer"
            className="ml-auto hidden shrink-0 text-sm text-slate-400 transition hover:text-white sm:block"
          >
            GitHub ↗
          </a>
        </div>
      </header>

      {/* Hero (idle only) */}
      {idle && (
        <section className="relative px-4 pb-10 pt-16 text-center sm:pt-24">
          <h1 className="mx-auto max-w-3xl text-4xl font-extrabold leading-tight tracking-tight sm:text-6xl">
            Find your next <span className="text-[color:var(--gold)]">favorite film</span>
          </h1>
          <p className="mx-auto mt-4 max-w-xl text-base text-slate-400 sm:text-lg">
            Content-based recommendations over ~4,800 films — search one you love and discover more
            like it.
          </p>
          <div className="mt-8 flex justify-center">
            <SearchBar onSubmit={run} autoFocus />
          </div>
          <EmptyState onPick={run} />
        </section>
      )}

      {/* Results */}
      <main className="mx-auto max-w-7xl px-4 pb-20">
        {status === "loading" && (
          <div className="pt-8">
            <SkeletonGrid count={12} />
          </div>
        )}

        {status === "error" && (
          <ErrorState message={error.message} suggestions={error.suggestions} onPick={run} />
        )}

        {status === "success" && data && (
          <div className="pt-8">
            <div className="mb-6 flex flex-wrap items-baseline justify-between gap-2">
              <h2 className="text-xl font-bold sm:text-2xl">
                More like <span className="text-[color:var(--gold)]">{data.resolved_title}</span>
              </h2>
              <p className="text-sm text-slate-500">
                {data.count} picks · tap any poster to keep exploring
              </p>
            </div>
            <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6">
              {data.results.map((m) => (
                <MovieCard key={m.id} movie={m} onExplore={run} />
              ))}
            </div>
          </div>
        )}
      </main>

      <footer className="border-t border-white/5 px-4 py-8 text-center text-xs text-slate-600">
        Data: TMDB 5000 dataset. This product uses the TMDB API but is not endorsed or certified by
        TMDB. Built by Harsh Gupta.
      </footer>
    </div>
  );
}
