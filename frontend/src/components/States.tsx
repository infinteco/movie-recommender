/** Empty state shown before any search. */
export function EmptyState() {
  return (
    <div className="mt-16 text-center text-slate-500">
      <p className="text-lg">Search for a movie to see recommendations.</p>
      <p className="mt-1 text-sm">Try “The Dark Knight”, “Inception”, or “Toy Story”.</p>
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
    <div className="mt-16 text-center">
      <p className="text-lg text-rose-400">{message}</p>
      {suggestions.length > 0 && (
        <div className="mt-4">
          <p className="text-sm text-slate-400">Did you mean:</p>
          <div className="mt-2 flex flex-wrap justify-center gap-2">
            {suggestions.map((s) => (
              <button
                key={s}
                onClick={() => onPick(s)}
                className="rounded-full bg-slate-800 px-3 py-1 text-sm text-slate-200 hover:bg-indigo-600"
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
