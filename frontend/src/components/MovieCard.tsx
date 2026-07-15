import type { Recommendation } from "../types";

/** A single recommendation card. Click it to explore recommendations for that film. */
export function MovieCard({
  movie,
  onExplore,
}: {
  movie: Recommendation;
  onExplore: (title: string) => void;
}) {
  const year = movie.release_date ? movie.release_date.slice(0, 4) : null;
  const similarityPct = Math.round(movie.similarity * 100);

  return (
    <button
      type="button"
      onClick={() => onExplore(movie.title)}
      title={`Find movies similar to ${movie.title}`}
      className="group flex flex-col overflow-hidden rounded-xl bg-slate-900 text-left ring-1 ring-slate-800 transition hover:ring-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-400"
    >
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
        {/* Hover affordance: this card is clickable to explore further. */}
        <div className="pointer-events-none absolute inset-0 flex items-end justify-center bg-gradient-to-t from-black/70 to-transparent opacity-0 transition group-hover:opacity-100">
          <span className="mb-3 rounded-full bg-indigo-600 px-3 py-1 text-xs font-medium text-white">
            ▸ Find similar
          </span>
        </div>
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
    </button>
  );
}
