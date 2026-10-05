"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const items = [
  {
    href: "/contests",
    label: "Olümpiaadid",
    active: (path: string) =>
      path.startsWith("/contests") ||
      path.startsWith("/results") ||
      path.startsWith("/olympiads"),
  },
  {
    href: "/schools",
    label: "Koolid",
    active: (path: string) => path.startsWith("/schools"),
  },
  {
    href: "/people",
    label: "Inimesed",
    active: (path: string) =>
      path.startsWith("/honor-roll") || path.startsWith("/people"),
  },
  {
    href: "/about",
    label: "Meist",
    active: (path: string) => path.startsWith("/about"),
  },
  {
    href: "/api-reference",
    label: "API",
    active: (path: string) => path.startsWith("/api-reference"),
  },
];

export function HeaderNavigation() {
  const pathname = usePathname();
  return (
    <nav aria-label="Peamenüü" className="top-nav">
      {items.map((item) => (
        <Link
          prefetch={false}
          key={item.href}
          href={item.href}
          aria-current={item.active(pathname) ? "page" : undefined}
        >
          {item.label}
        </Link>
      ))}
    </nav>
  );
}
