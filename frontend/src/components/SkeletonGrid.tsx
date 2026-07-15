/** Placeholder grid shown while recommendations load. */
export function SkeletonGrid({ count = 10 }: { count?: number }) {
  return (
    <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5">
      {Array.from({ length: count }).map((_, i) => (
        <div key={i} className="overflow-hidden rounded-xl bg-slate-900 ring-1 ring-slate-800">
          <div className="aspect-[2/3] w-full animate-pulse bg-slate-800" />
          <div className="space-y-2 p-3">
            <div className="h-3 w-3/4 animate-pulse rounded bg-slate-800" />
            <div className="h-3 w-1/2 animate-pulse rounded bg-slate-800" />
          </div>
        </div>
      ))}
    </div>
  );
}
