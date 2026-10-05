import type { Metadata } from "next";
import type { CSSProperties } from "react";
import Link from "next/link";
import { notFound } from "next/navigation";
import { getSubjectContests, type ContestItem } from "@/lib/api";
import { publicId } from "@/lib/public-id";
import { occurrenceMetadata, resultMetadata } from "@/lib/result-metadata";
import { Breadcrumbs } from "@/components/Breadcrumbs";

type Props = { params: Promise<{ subject: string }> };
type ContestGroup = { type: string; ages: string[] };
type YearRow = number | { from: number; to: number };

async function subjectResults(code: string) {
  const results = await getSubjectContests(code);
  if (results.length === 0) notFound();
  return results;
}

function fullYear(year: number | null) {
  return year === null ? "Aasta teadmata" : `${year}/${year + 1}`;
}

function yearRows(known: number[], current: number): YearRow[] {
  if (!known.length) return [];
  const first = Math.min(...known);
  const knownSet = new Set(known);
  const rows: YearRow[] = [];
  let year = Math.max(current, ...known);
  while (year >= first) {
    if (knownSet.has(year) || year >= current - 4) {
      rows.push(year--);
      continue;
    }
    const to = year;
    while (year >= first && !knownSet.has(year) && year < current - 4) year--;
    const from = year + 1;
    if (to - from >= 3) rows.push({ from, to });
    else for (let value = to; value >= from; value--) rows.push(value);
  }
  return rows;
}

function ResultCell({
  entries,
  subject,
  type,
  age,
  year,
}: {
  entries: ContestItem[];
  subject: string;
  type: string;
  age: string;
  year: number | null;
}) {
  if (!entries.length) {
    const occurrence = occurrenceMetadata(subject, type, age, year);
    if (occurrence?.status === "source-only") {
      const href = occurrence.source?.localUrl || occurrence.source?.sourceUrl;
      return href ? (
        <div className="matrix-results">
          <a
            className="matrix-result"
            href={href}
            aria-label={`${type}, ${age}, ${fullYear(year)}: algallikas olemas, tulemused puuduvad`}
            title="Algallikas on olemas; tulemusi ei ole andmebaasis"
          >
            <span className="matrix-symbol">◇</span>
            <span className="matrix-file-marks" aria-hidden="true">
              <b>A</b>
            </span>
          </a>
        </div>
      ) : (
        <span
          className="matrix-unknown"
          title="Algallikas on teada, kuid link puudub"
        >
          ◇
        </span>
      );
    }
    const absent = occurrence?.status === "not-held";
    return (
      <span
        className="matrix-unknown"
        title={absent ? "Võistlust ei toimunud" : "Võistluse kohta pole teavet"}
      >
        {absent ? "—" : "?"}
      </span>
    );
  }
  return (
    <div className="matrix-results">
      {entries.map((item) => {
        const metadata = resultMetadata(item.id);
        const hasQuestions = Boolean(
          metadata.questions?.sourceUrl ||
          metadata.questions?.localUrl ||
          item.tasks_link,
        );
        const hasRules = Boolean(
          metadata.regulations?.sourceUrl || metadata.regulations?.localUrl,
        );
        const hasSource = Boolean(
          metadata.source?.sourceUrl || metadata.source?.localUrl,
        );
        const partial = metadata.status === "partial";
        const sourceOnly =
          metadata.status === "source-only" ||
          (item.result_count === 0 && hasSource);
        const label = sourceOnly
          ? "Allikas"
          : item.result_count === 0
            ? "Kirje"
            : partial
              ? "Osalised"
              : metadata.status === "complete"
                ? "Täielikud"
                : "Tulemused";
        const symbol = sourceOnly
          ? "◇"
          : item.result_count === 0
            ? "○"
            : partial
              ? "◐"
              : metadata.status === "complete"
                ? "✓"
                : "↗";
        return (
          <Link
            prefetch={false}
            className={`matrix-result ${partial ? "matrix-result-partial" : ""}`}
            href={`/results/${publicId("result", item.id)}`}
            key={item.id}
            aria-label={`${type}, ${age || "üldarvestus"}, ${fullYear(year)}: ${label.toLocaleLowerCase("et-EE")}`}
            title={item.subcontest_name || "Tulemused"}
          >
            <span className="matrix-symbol" aria-hidden="true">
              {symbol}
            </span>
            <span className="matrix-file-marks" aria-hidden="true">
              {hasQuestions && <b>Ü</b>}
              {hasRules && <b>J</b>}
              {hasSource && <b>A</b>}
            </span>
          </Link>
        );
      })}
    </div>
  );
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { subject } = await params;
  const results = await subjectResults(subject);
  return { title: results[0].subject };
}

export default async function SubjectPage({ params }: Props) {
  const { subject } = await params;
  const results = await subjectResults(subject);
  const years = [
    ...new Set(
      results
        .map((item) => item.year)
        .filter((year): year is number => year !== null),
    ),
  ];
  const now = new Date();
  const currentYear =
    now.getUTCMonth() >= 7 ? now.getUTCFullYear() : now.getUTCFullYear() - 1;
  const rows = yearRows(years, currentYear);
  if (results.some((item) => item.year === null)) rows.push(Number.NaN);
  const types = [...new Set(results.map((item) => item.contest_type))].sort(
    (a, b) => a.localeCompare(b, "et"),
  );
  const groups: ContestGroup[] = types.map((type) => ({
    type,
    ages: [
      ...new Set(
        results
          .filter((item) => item.contest_type === type)
          .map((item) => item.age_group),
      ),
    ].sort((a, b) => a.localeCompare(b, "et", { numeric: true })),
  }));
  const columnCount = groups.reduce(
    (count, group) => count + group.ages.length,
    0,
  );
  const columnWidth = Math.max(
    94,
    ...groups.flatMap((group) =>
      group.ages.map((age) =>
        Math.min(136, (age || "Üldarvestus").length * 9 + 18),
      ),
    ),
  );
  const tableWidth = 104 + columnCount * columnWidth;
  const cells = new Map<string, ContestItem[]>();
  for (const item of results) {
    const key = JSON.stringify([item.contest_type, item.age_group, item.year]);
    cells.set(key, [...(cells.get(key) ?? []), item]);
  }
  const entriesFor = (type: string, age: string, year: number | null) =>
    cells.get(JSON.stringify([type, age, year])) ?? [];
  const earliest = years.length ? Math.min(...years) : null;

  return (
    <>
      <section className="page-intro">
        <Breadcrumbs
          items={[
            { label: "Olümpiaadid", href: "/contests" },
            { label: results[0].subject, href: `/contests/${subject}` },
          ]}
        />
        <p>
          Õppeaastad, võistlused ja vanuserühmad. Vali lahter tulemuste
          avamiseks.
        </p>
      </section>
      <div
        className="contest-table-scroll"
        style={{ "--contest-width": `${tableWidth}px` } as CSSProperties}
      >
        <table className="contest-matrix" style={{ width: `${tableWidth}px` }}>
          <colgroup>
            <col style={{ width: "104px" }} />
            <col span={columnCount} style={{ width: `${columnWidth}px` }} />
          </colgroup>
          <caption className="sr-only">
            {results[0].subject}: tulemused õppeaastate, võistluste ja
            vanuserühmade kaupa
          </caption>
          <thead>
            <tr>
              <th scope="col" rowSpan={2}>
                Õppeaasta
              </th>
              {groups.map(({ type, ages }) => (
                <th
                  className="contest-column-start"
                  scope="colgroup"
                  colSpan={ages.length}
                  key={type}
                >
                  {type}
                </th>
              ))}
            </tr>
            <tr>
              {groups.flatMap(({ type, ages }) =>
                ages.map((age, index) => (
                  <th
                    className={index === 0 ? "contest-column-start" : undefined}
                    scope="col"
                    key={`${type}-${age}`}
                  >
                    {age || "Üldarvestus"}
                  </th>
                )),
              )}
            </tr>
          </thead>
          <tbody>
            {rows.map((row) =>
              typeof row === "number" ? (
                <tr key={Number.isNaN(row) ? "unknown" : row}>
                  <th scope="row">
                    {fullYear(Number.isNaN(row) ? null : row)}
                  </th>
                  {groups.flatMap(({ type, ages }) =>
                    ages.map((age, index) => (
                      <td
                        className={
                          index === 0 ? "contest-column-start" : undefined
                        }
                        key={`${type}-${age}`}
                      >
                        <ResultCell
                          entries={entriesFor(
                            type,
                            age,
                            Number.isNaN(row) ? null : row,
                          )}
                          subject={subject}
                          type={type}
                          age={age}
                          year={Number.isNaN(row) ? null : row}
                        />
                      </td>
                    )),
                  )}
                </tr>
              ) : (
                <tr className="matrix-gap" key={`${row.from}-${row.to}`}>
                  <th
                    scope="row"
                    title={`${fullYear(row.to)}–${fullYear(row.from)}`}
                  >
                    {row.to}–{row.from}
                  </th>
                  <td colSpan={columnCount}>
                    <span className="matrix-gap-label">
                      {row.to - row.from + 1} õppeaasta kohta ei ole selle
                      õppeaine andmeid
                    </span>
                  </td>
                </tr>
              ),
            )}
          </tbody>
        </table>
      </div>
      {earliest !== null && earliest > 1953 && (
        <p className="matrix-history">
          Varasemate õppeaastate 1953/1954–{fullYear(earliest - 1)} kohta ei ole
          selle õppeaine andmeid; neid aastaid tabelis eraldi ei näidata.
        </p>
      )}
      <section className="matrix-legend-section" aria-label="Tabeli tähised">
        <h2>Tähised</h2>
        <div className="matrix-legend">
          <span>
            <strong className="legend-result">↗</strong> Tulemused andmebaasis,
            täielikkus teadmata
          </span>
          <span>
            <strong>✓</strong> Täielikkus kinnitatud
          </span>
          <span>
            <strong>◐</strong> Osalised tulemused
          </span>
          <span>
            <strong>○</strong> Kirje ilma tulemusteta
          </span>
          <span>
            <strong>◇</strong> Algallikas olemas, tulemused puudu
          </span>
          <span>
            <strong>?</strong> Teave puudub
          </span>
          <span>
            <strong>—</strong> Võistlust ei toimunud (kui kinnitatud)
          </span>
          <span>
            <strong>Ü</strong> Ülesanded lingitud
          </span>
          <span>
            <strong>J</strong> Juhend või ajakava lingitud
          </span>
          <span>
            <strong>A</strong> Algallikas lingitud
          </span>
        </div>
        <p className="matrix-legend-note">
          Ü, J ja A puudumine tähendab, et vastavat linki pole lisatud.
          Failikirjel võib olla algne URL ja kohalik koopia.
        </p>
      </section>
    </>
  );
}
