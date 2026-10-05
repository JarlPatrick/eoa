"use client";

import { useEffect, useRef } from "react";

export function HeaderSearch() {
  const input = useRef<HTMLInputElement>(null);

  useEffect(() => {
    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape" && document.activeElement === input.current) {
        input.current?.blur();
        return;
      }
      const commandSearch =
        (event.ctrlKey || event.metaKey) && event.key.toLowerCase() === "k";
      const slashSearch =
        event.key === "/" && !event.ctrlKey && !event.metaKey && !event.altKey;
      const target = event.target;
      const editing =
        target instanceof HTMLElement &&
        (target.isContentEditable ||
          ["INPUT", "TEXTAREA", "SELECT"].includes(target.tagName));
      if (commandSearch || (slashSearch && !editing)) {
        event.preventDefault();
        input.current?.focus();
      }
    };
    document.addEventListener("keydown", onKeyDown);
    return () => document.removeEventListener("keydown", onKeyDown);
  }, []);

  return (
    <form className="header-search" action="/search" role="search">
      <label className="sr-only" htmlFor="header-name-search">
        Otsi inimesi, koole ja võistlusi
      </label>
      <input
        ref={input}
        id="header-name-search"
        name="q"
        placeholder="Otsi inimesi, koole, võistlusi · /"
        aria-keyshortcuts="/ Control+K Meta+K"
        required
      />
      <button type="submit">Otsi</button>
    </form>
  );
}
