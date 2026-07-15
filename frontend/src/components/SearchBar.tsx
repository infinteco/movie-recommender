import { useEffect, useRef, useState } from "react";
import { searchTitles } from "../api";

/** Search box with debounced search-as-you-type suggestions. */
export function SearchBar({
  onSubmit,
  autoFocus = false,
}: {
  onSubmit: (title: string) => void;
  autoFocus?: boolean;
}) {
  const [value, setValue] = useState("");
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const [open, setOpen] = useState(false);
  const [active, setActive] = useState(-1);
  const boxRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!value.trim()) {
      setSuggestions([]);
      return;
    }
    const controller = new AbortController();
    const timer = setTimeout(async () => {
      try {
        const results = await searchTitles(value, controller.signal);
        setSuggestions(results);
        setOpen(true);
        setActive(-1);
      } catch {
        /* aborted */
      }
    }, 180);
    return () => {
      clearTimeout(timer);
      controller.abort();
    };
  }, [value]);

  useEffect(() => {
    const onClick = (e: MouseEvent) => {
      if (boxRef.current && !boxRef.current.contains(e.target as Node)) setOpen(false);
    };
    document.addEventListener("mousedown", onClick);
    return () => document.removeEventListener("mousedown", onClick);
  }, []);

  const submit = (title: string) => {
    setValue(title);
    setOpen(false);
    onSubmit(title);
  };

  const onKeyDown = (e: React.KeyboardEvent) => {
    if (!open || suggestions.length === 0) return;
    if (e.key === "ArrowDown") {
      e.preventDefault();
      setActive((a) => Math.min(a + 1, suggestions.length - 1));
    } else if (e.key === "ArrowUp") {
      e.preventDefault();
      setActive((a) => Math.max(a - 1, 0));
    } else if (e.key === "Enter" && active >= 0) {
      e.preventDefault();
      submit(suggestions[active]);
    }
  };

  return (
    <div ref={boxRef} className="relative w-full max-w-2xl">
      <form
        onSubmit={(e) => {
          e.preventDefault();
          if (value.trim()) submit(value.trim());
        }}
      >
        <div className="flex items-center gap-2 rounded-full border border-white/10 bg-white/5 px-4 py-3 shadow-xl backdrop-blur transition focus-within:border-[color:var(--gold)] focus-within:bg-white/10">
          <svg className="h-5 w-5 shrink-0 text-slate-400" viewBox="0 0 24 24" fill="none">
            <path
              d="M21 21l-4.3-4.3M11 19a8 8 0 100-16 8 8 0 000 16z"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
            />
          </svg>
          <input
            type="text"
            value={value}
            autoFocus={autoFocus}
            onChange={(e) => setValue(e.target.value)}
            onFocus={() => suggestions.length > 0 && setOpen(true)}
            onKeyDown={onKeyDown}
            placeholder="Search a movie you love…"
            aria-label="Search a movie"
            className="w-full bg-transparent text-base text-white placeholder-slate-500 outline-none"
          />
          <button
            type="submit"
            className="hidden shrink-0 rounded-full bg-[color:var(--gold)] px-4 py-1.5 text-sm font-bold text-black transition hover:brightness-95 sm:block"
          >
            Search
          </button>
        </div>
      </form>

      {open && suggestions.length > 0 && (
        <ul className="absolute z-20 mt-2 max-h-80 w-full overflow-auto rounded-2xl border border-white/10 bg-[#161619] py-1 shadow-2xl">
          {suggestions.map((s, i) => (
            <li key={s}>
              <button
                onMouseEnter={() => setActive(i)}
                onClick={() => submit(s)}
                className={`block w-full px-4 py-2.5 text-left text-sm transition ${
                  i === active ? "bg-[color:var(--gold)] text-black" : "text-slate-200 hover:bg-white/5"
                }`}
              >
                {s}
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
