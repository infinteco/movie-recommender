import type { Recommendation } from "../types";

/** A single recommendation card: poster (or placeholder), title, score, genres. */
export function MovieCard({ movie }: { movie: Recommendation }) {
  const year = movie.release_date ? movie.release_date.slice(0, 4) : null;
  const similarityPct = Math.round(movie.similarity * 100);

  return (
    <div className="group flex flex-col overflow-hidden rounded-xl bg-slate-900 ring-1 ring-slate-800 transition hover:ring-indigo-500">
      <div className="relative aspect-[2/3] w-full bg-slate-800">
        {movie.poster_url ? (
          <img
            src={movie.poster_url}
            alt={`${movie.title} poster`}
            loading="lazy"
            className="h-full w-full object-cover"
          />
        ) : (
          <div className="flex h-full w-full items-center justify-center p-3 text-center text-sm text-slate-500">
            {movie.title}
          </div>
        )}
        <span
          className="absolute right-2 top-2 rounded-full bg-black/70 px-2 py-1 text-xs font-medium text-indigo-300"
          title="Content similarity to your query"
        >
          {similarityPct}% match
        </span>
      </div>

      <div className="flex flex-1 flex-col gap-1 p-3">
        <h3 className="line-clamp-2 text-sm font-semibold text-slate-100">
          {movie.title}
          {year && <span className="ml-1 font-normal text-slate-500">({year})</span>}
        </h3>
        <div className="mt-auto flex items-center justify-between pt-2 text-xs text-slate-400">
          <span className="truncate">{movie.genres.slice(0, 2).join(", ")}</span>
          <span className="shrink-0 text-amber-400">★ {movie.vote_average.toFixed(1)}</span>
        </div>
      </div>
    </div>
  );
}
