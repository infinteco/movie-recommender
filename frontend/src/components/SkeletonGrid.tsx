/** Placeholder grid shown while recommendations load. */
export function SkeletonGrid({ count = 12 }: { count?: number }) {
  return (
    <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6">
      {Array.from({ length: count }).map((_, i) => (
        <div key={i} className="overflow-hidden rounded-xl bg-[#1b1b1f] ring-1 ring-white/5">
          <div className="shimmer aspect-[2/3] w-full bg-white/5" />
          <div className="space-y-2 p-3">
            <div className="shimmer h-3 w-3/4 rounded bg-white/5" />
            <div className="shimmer h-3 w-1/2 rounded bg-white/5" />
          </div>
        </div>
      ))}
    </div>
  );
}
