import Link from "next/link";

type Crumb = { label: string; href: string };

export function Breadcrumbs({ items }: { items: Crumb[] }) {
  return (
    <nav className="breadcrumbs" aria-label="Asukoht">
      <ol>
        {items.map((item, index) => (
          <li key={`${item.href}-${index}`}>
            {index === items.length - 1 ? (
              <h1>
                <Link prefetch={false} href={item.href} aria-current="page">
                  {item.label}
                </Link>
              </h1>
            ) : (
              <Link prefetch={false} href={item.href}>
                {item.label}
              </Link>
            )}
          </li>
        ))}
      </ol>
    </nav>
  );
}
