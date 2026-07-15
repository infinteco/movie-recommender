import type { Recommendation } from "../types";

// Deterministic gradient for the poster placeholder so each film looks distinct.
const GRADIENTS = [
  "from-indigo-600/40 to-slate-900",
  "from-rose-600/40 to-slate-900",
  "from-emerald-600/40 to-slate-900",
  "from-amber-600/40 to-slate-900",
  "from-sky-600/40 to-slate-900",
  "from-fuchsia-600/40 to-slate-900",
];

function gradientFor(title: string): string {
  let h = 0;
  for (let i = 0; i < title.length; i++) h = (h * 31 + title.charCodeAt(i)) & 0xffff;
  return GRADIENTS[h % GRADIENTS.length];
}

/** IMDb-inspired film card. Click it to explore recommendations for that title. */
export function MovieCard({
  movie,
  onExplore,
}: {
  movie: Recommendation;
  onExplore: (title: string) => void;
}) {
  const year = movie.release_date ? movie.release_date.slice(0, 4) : null;
  const matchPct = Math.round(movie.similarity * 100);

  return (
    <button
      type="button"
      onClick={() => onExplore(movie.title)}
      title={`Explore movies similar to ${movie.title}`}
      className="group relative flex flex-col overflow-hidden rounded-xl bg-[#1b1b1f] text-left shadow-lg ring-1 ring-white/5 transition-all duration-200 hover:-translate-y-1 hover:shadow-2xl hover:ring-[color:var(--gold)]/40 focus:outline-none focus:ring-2 focus:ring-[color:var(--gold)]"
    >
      <div className="relative aspect-[2/3] w-full">
        {movie.poster_url ? (
          <img
            src={movie.poster_url}
            alt={`${movie.title} poster`}
            loading="lazy"
            className="h-full w-full object-cover"
          />
        ) : (
          <div
            className={`flex h-full w-full flex-col items-center justify-center gap-2 bg-gradient-to-b ${gradientFor(
              movie.title,
            )} p-3 text-center`}
          >
            <span className="text-3xl opacity-70">🎬</span>
            <span className="line-clamp-3 text-sm font-semibold text-slate-200">{movie.title}</span>
          </div>
        )}

        {/* Rating pill (IMDb-style gold star) */}
        <div className="absolute left-2 top-2 flex items-center gap-1 rounded-md bg-black/75 px-1.5 py-0.5 backdrop-blur">
          <span className="text-[color:var(--gold)]">★</span>
          <span className="text-xs font-bold text-white">{movie.vote_average.toFixed(1)}</span>
        </div>

        {/* Match badge */}
        <div className="absolute right-2 top-2 rounded-md bg-[color:var(--gold)] px-1.5 py-0.5 text-xs font-bold text-black">
          {matchPct}%
        </div>

        {/* Hover overlay */}
        <div className="pointer-events-none absolute inset-0 flex items-end justify-center bg-gradient-to-t from-black/85 via-black/20 to-transparent opacity-0 transition-opacity group-hover:opacity-100">
          <span className="mb-3 rounded-full bg-[color:var(--gold)] px-3 py-1 text-xs font-bold text-black">
            ▸ Explore similar
          </span>
        </div>
      </div>

      <div className="flex flex-1 flex-col gap-1 p-3">
        <h3 className="line-clamp-1 text-sm font-semibold text-white">{movie.title}</h3>
        <div className="flex items-center justify-between text-xs text-slate-400">
          <span>{year ?? "—"}</span>
          <span className="truncate pl-2 text-right">{movie.genres.slice(0, 2).join(" · ")}</span>
        </div>
      </div>
    </button>
  );
}
