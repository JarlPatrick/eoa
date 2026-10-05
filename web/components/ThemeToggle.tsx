"use client";

/* The mount effect syncs the theme set by the early layout script. The event handler writes that theme to the DOM. */
/* eslint-disable react-hooks/set-state-in-effect, react-hooks/immutability */

import { useEffect, useRef, useState } from "react";

type Theme = "system" | "light" | "dark";

const options: { theme: Theme; label: string }[] = [
  { theme: "system", label: "Süsteemi järgi" },
  { theme: "light", label: "Hele" },
  { theme: "dark", label: "Tume" },
];

function ThemeIcon({ theme }: { theme: Theme }) {
  if (theme === "system")
    return (
      <svg
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        strokeWidth="1.8"
        strokeLinecap="round"
        strokeLinejoin="round"
        aria-hidden="true"
      >
        <rect x="3" y="4" width="18" height="13" rx="1.5" />
        <path d="M8 21h8m-4-4v4" />
      </svg>
    );
  if (theme === "light")
    return (
      <svg
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        strokeWidth="1.8"
        strokeLinecap="round"
        aria-hidden="true"
      >
        <circle cx="12" cy="12" r="4" />
        <path d="M12 2v2m0 16v2M4.93 4.93l1.42 1.42m11.3 11.3 1.42 1.42M2 12h2m16 0h2M4.93 19.07l1.42-1.42m11.3-11.3 1.42-1.42" />
      </svg>
    );
  return (
    <svg
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.8"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      <path d="M20.5 14.1A8.5 8.5 0 0 1 9.9 3.5 8.5 8.5 0 1 0 20.5 14.1Z" />
    </svg>
  );
}

export function ThemeToggle() {
  const [theme, setTheme] = useState<Theme>("system");
  const [open, setOpen] = useState(false);
  const root = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const stored = document.documentElement.dataset.theme;
    if (stored === "light" || stored === "dark") setTheme(stored);
  }, []);

  useEffect(() => {
    if (!open) return;
    const dismiss = (event: MouseEvent) => {
      if (!root.current?.contains(event.target as Node)) setOpen(false);
    };
    const escape = (event: KeyboardEvent) => {
      if (event.key === "Escape") setOpen(false);
    };
    document.addEventListener("mousedown", dismiss);
    document.addEventListener("keydown", escape);
    return () => {
      document.removeEventListener("mousedown", dismiss);
      document.removeEventListener("keydown", escape);
    };
  }, [open]);

  const selectTheme = (next: Theme) => {
    if (next === "system") {
      delete document.documentElement.dataset.theme;
      try {
        localStorage.removeItem("eoa-theme");
      } catch {
        /* Selection remains active for this visit. */
      }
    } else {
      document.documentElement.dataset.theme = next;
      try {
        localStorage.setItem("eoa-theme", next);
      } catch {
        /* Selection remains active for this visit. */
      }
    }
    setTheme(next);
    setOpen(false);
  };

  return (
    <div className="theme-controls" ref={root}>
      <button
        type="button"
        className="theme-toggle"
        aria-label="Vali värviteema"
        aria-expanded={open}
        title={`Värviteema: ${options.find((option) => option.theme === theme)?.label}`}
        onClick={() => setOpen((value) => !value)}
      >
        <ThemeIcon theme={theme} />
      </button>
      {open && (
        <div className="theme-menu" role="group" aria-label="Värviteema">
          {options.map((option) => (
            <button
              key={option.theme}
              type="button"
              aria-pressed={theme === option.theme}
              onClick={() => selectTheme(option.theme)}
            >
              <ThemeIcon theme={option.theme} />
              <span>{option.label}</span>
              <span aria-hidden="true" className="theme-selected">
                {theme === option.theme ? "✓" : ""}
              </span>
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
