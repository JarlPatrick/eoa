"use client";

import Link from "next/link";
import type { Statistics } from "@/lib/api";
import { PageSizeSelect, useListPageSize } from "@/components/ListPageSize";
import { Pagination, pageNumber } from "@/components/Pagination";
import { SortHeading } from "@/components/SortHeading";

const columns = [
  ["name", "Nimi"],
  ["score", "Punktid"],
  ["participations", "Osalemisi"],
  ["first", "1. kohti · kaalutud"],
  ["second", "2. kohti · kaalutud"],
  ["third", "3. kohti · kaalutud"],
] as const;

export function HonorRollTable({
  data,
  sort,
  order,
  page,
  rows,
  view,
}: {
  data: Statistics["rows"];
  sort?: string;
  order?: string;
  page?: string;
  rows?: string;
  view: "students" | "mentors";
}) {
  const { pageSize, selected } = useListPageSize(rows);
  const currentPage = Math.min(
    pageNumber(page),
    Math.max(1, Math.ceil(data.length / pageSize)),
  );
  const visible = data.slice(
    (currentPage - 1) * pageSize,
    currentPage * pageSize,
  );

  return (
    <>
      <div className="table-controls">
        <PageSizeSelect
          path="/people"
          selected={selected}
          sort={sort}
          order={order}
          params={{ view }}
        />
        <Pagination
          page={currentPage}
          total={data.length}
          pageSize={pageSize}
          path="/people"
          params={{ sort, order, rows, view }}
        />
      </div>
      <div className="table-scroll">
        <table>
          <thead>
            <tr>
              {columns.map(([key, label]) => (
                <SortHeading
                  key={key}
                  label={
                    key === "participations" && view === "mentors"
                      ? "Juhendamisi"
                      : label
                  }
                  column={key}
                  current={sort}
                  order={order}
                  base="/people"
                  params={{ rows, view }}
                />
              ))}
            </tr>
          </thead>
          <tbody>
            {visible.map((row) => (
              <tr key={String(row[0])}>
                <td>
                  <Link prefetch={false} href={`/people/${row[0]}`}>
                    {row[1]}
                  </Link>
                </td>
                <td>{row[6]}</td>
                <td>{row[2]}</td>
                <td>{row[3]}</td>
                <td>{row[4]}</td>
                <td>{row[5]}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div className="table-controls">
        <PageSizeSelect
          path="/people"
          selected={selected}
          sort={sort}
          order={order}
          params={{ view }}
        />
        <Pagination
          page={currentPage}
          total={data.length}
          pageSize={pageSize}
          path="/people"
          params={{ sort, order, rows, view }}
        />
      </div>
      {data.length === 0 && <p>Andmeid ei leitud.</p>}
    </>
  );
}
