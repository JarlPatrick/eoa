"use client";

import { useRouter } from "next/navigation";

const fixedSizes = [10, 20, 50, 100] as const;

export function useListPageSize(rows: string | undefined) {
  const fixed = fixedSizes.find((size) => String(size) === rows);
  return {
    pageSize: rows === "all" ? Infinity : (fixed ?? 20),
    selected: rows === "all" ? "all" : String(fixed ?? 20),
  };
}

export function PageSizeSelect({
  path,
  selected,
  sort,
  order,
  params = {},
}: {
  path: string;
  selected: string;
  sort?: string;
  order?: string;
  params?: Record<string, string | undefined>;
}) {
  const router = useRouter();
  return (
    <label className="page-size-control">
      <span className="page-size-label-long">Ridu lehel</span>
      <span className="page-size-label-short">Ridu</span>
      <select
        value={selected}
        onChange={(event) => {
          const query = new URLSearchParams();
          if (sort) query.set("sort", sort);
          if (order) query.set("order", order);
          for (const [key, value] of Object.entries(params))
            if (value) query.set(key, value);
          query.set("rows", event.target.value);
          router.push(`${path}${query.size ? `?${query}` : ""}`);
        }}
      >
        {fixedSizes.map((size) => (
          <option value={size} key={size}>
            {size}
          </option>
        ))}
        <option value="all">Kõik</option>
      </select>
    </label>
  );
}
