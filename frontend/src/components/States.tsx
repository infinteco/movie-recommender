const POPULAR = ["The Dark Knight", "Inception", "Interstellar", "Avatar", "Toy Story", "The Matrix"];

/** Empty state shown before any search, with quick-pick chips. */
export function EmptyState({ onPick }: { onPick: (title: string) => void }) {
  return (
    <div className="mx-auto mt-8 max-w-xl text-center">
      <p className="text-slate-400">Not sure where to start? Try one of these:</p>
      <div className="mt-4 flex flex-wrap justify-center gap-2">
        {POPULAR.map((t) => (
          <button
            key={t}
            onClick={() => onPick(t)}
            className="rounded-full border border-white/10 bg-white/5 px-4 py-1.5 text-sm text-slate-200 transition hover:border-[color:var(--gold)] hover:text-white"
          >
            {t}
          </button>
        ))}
      </div>
    </div>
  );
}

/** Error state, optionally offering close-title suggestions. */
export function ErrorState({
  message,
  suggestions = [],
  onPick,
}: {
  message: string;
  suggestions?: string[];
  onPick: (title: string) => void;
}) {
  return (
    <div className="mx-auto mt-12 max-w-xl text-center">
      <div className="mb-3 text-4xl">🎬</div>
      <p className="text-lg text-rose-400">{message}</p>
      {suggestions.length > 0 && (
        <div className="mt-4">
          <p className="text-sm text-slate-400">Did you mean:</p>
          <div className="mt-2 flex flex-wrap justify-center gap-2">
            {suggestions.map((s) => (
              <button
                key={s}
                onClick={() => onPick(s)}
                className="rounded-full bg-white/5 px-3 py-1.5 text-sm text-slate-200 ring-1 ring-white/10 transition hover:bg-[color:var(--gold)] hover:text-black"
              >
                {s}
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
