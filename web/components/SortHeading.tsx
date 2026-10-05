import Link from "next/link";

export function SortHeading({
  label,
  column,
  current,
  order,
  base,
  params = {},
  sortKey = "sort",
  orderKey = "order",
}: {
  label: string;
  column: string;
  current?: string;
  order?: string;
  base: string;
  params?: Record<string, string | undefined>;
  sortKey?: string;
  orderKey?: string;
}) {
  const active = current === column;
  const nextOrder = active && order === "asc" ? "desc" : "asc";
  const query = new URLSearchParams({
    [sortKey]: column,
    [orderKey]: nextOrder,
  });
  for (const [key, value] of Object.entries(params))
    if (value) query.set(key, value);
  return (
    <th
      scope="col"
      aria-sort={
        active ? (order === "desc" ? "descending" : "ascending") : "none"
      }
    >
      <Link prefetch={false} href={`${base}?${query}`}>
        {label}
        {active ? (order === "desc" ? " ↓" : " ↑") : ""}
      </Link>
    </th>
  );
}
