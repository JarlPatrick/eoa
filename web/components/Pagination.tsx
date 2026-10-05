import Link from "next/link";

export function pageNumber(value: string | undefined): number {
  const number = Number(value);
  return Number.isSafeInteger(number) && number > 0 ? number : 1;
}

export function Pagination({
  page,
  total,
  pageSize,
  path,
  params = {},
  pageKey = "page",
}: {
  page: number;
  total: number;
  pageSize: number;
  path: string;
  params?: Record<string, string | undefined>;
  pageKey?: string;
}) {
  const pages = Math.max(1, Math.ceil(total / pageSize));
  if (pages <= 1) return null;

  const href = (next: number) => {
    const query = new URLSearchParams();
    for (const [key, value] of Object.entries(params))
      if (value) query.set(key, value);
    query.set(pageKey, String(next));
    return `${path}?${query}`;
  };

  const visible = new Set([1, pages]);
  for (
    let next = Math.max(1, page - 2);
    next <= Math.min(pages, page + 2);
    next++
  )
    visible.add(next);
  for (let next = 2; next < pages; next++) {
    if (visible.has(next - 1) && visible.has(next + 1)) visible.add(next);
  }
  const numbers = [...visible].sort((a, b) => a - b);

  return (
    <nav aria-label="Leheküljed" className="pagination">
      <div className="pagination-links">
        {page > 1 ? (
          <Link
            prefetch={false}
            href={href(page - 1)}
            rel="prev"
            aria-label="Eelmine lehekülg"
          >
            ← Eelmine
          </Link>
        ) : (
          <span className="pagination-disabled" aria-hidden="true">
            ← Eelmine
          </span>
        )}
        {numbers.map((number, index) => (
          <span className="pagination-item" key={number}>
            {index > 0 && number - numbers[index - 1] > 1 && (
              <span className="pagination-ellipsis" aria-hidden="true">
                …
              </span>
            )}
            {number === page ? (
              <span
                className="pagination-current"
                aria-current="page"
                aria-label={`Lehekülg ${number}`}
              >
                {number}
              </span>
            ) : (
              <Link
                prefetch={false}
                href={href(number)}
                aria-label={`Lehekülg ${number}`}
              >
                {number}
              </Link>
            )}
          </span>
        ))}
        {page < pages ? (
          <Link
            prefetch={false}
            href={href(page + 1)}
            rel="next"
            aria-label="Järgmine lehekülg"
          >
            Järgmine →
          </Link>
        ) : (
          <span className="pagination-disabled" aria-hidden="true">
            Järgmine →
          </span>
        )}
      </div>
      <form action={path} className="page-jump">
        {Object.entries(params)
          .filter(([key, value]) => key !== pageKey && value)
          .map(([key, value]) => (
            <input key={key} type="hidden" name={key} value={value} />
          ))}
        <label>
          <span className="page-jump-label">Lehekülg </span>
          <input
            type="number"
            name={pageKey}
            min={1}
            max={pages}
            defaultValue={page}
            aria-label={`Mine lehele, kokku ${pages} lehekülge`}
          />
        </label>
        <span>/ {pages}</span>
        <button type="submit">Mine</button>
      </form>
    </nav>
  );
}
