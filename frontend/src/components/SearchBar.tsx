import { useEffect, useRef, useState } from "react";
import { searchTitles } from "../api";

/** Search box with debounced search-as-you-type suggestions. */
export function SearchBar({ onSubmit }: { onSubmit: (title: string) => void }) {
  const [value, setValue] = useState("");
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const [open, setOpen] = useState(false);
  const boxRef = useRef<HTMLDivElement>(null);

  // Debounced suggestion fetch, cancelling in-flight requests.
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
      } catch {
        /* aborted or failed — ignore */
      }
    }, 200);
    return () => {
      clearTimeout(timer);
      controller.abort();
    };
  }, [value]);

  // Close the dropdown on outside click.
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

  return (
    <div ref={boxRef} className="relative w-full max-w-xl">
      <form
        onSubmit={(e) => {
          e.preventDefault();
          if (value.trim()) submit(value.trim());
        }}
      >
        <input
          type="text"
          value={value}
          onChange={(e) => setValue(e.target.value)}
          onFocus={() => suggestions.length > 0 && setOpen(true)}
          placeholder="Search a movie…"
          aria-label="Search a movie"
          className="w-full rounded-xl border border-slate-700 bg-slate-900 px-4 py-3 text-slate-100 placeholder-slate-500 outline-none focus:border-indigo-500"
        />
      </form>

      {open && suggestions.length > 0 && (
        <ul className="absolute z-10 mt-1 max-h-72 w-full overflow-auto rounded-xl border border-slate-700 bg-slate-900 py-1 shadow-xl">
          {suggestions.map((s) => (
            <li key={s}>
              <button
                onClick={() => submit(s)}
                className="block w-full px-4 py-2 text-left text-sm text-slate-200 hover:bg-indigo-600"
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
