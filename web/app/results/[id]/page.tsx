import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { getApi, type Results } from "@/lib/api";
import { SortHeading } from "@/components/SortHeading";
import { Breadcrumbs } from "@/components/Breadcrumbs";
import { compareValues } from "@/lib/sort";
import { internalId, publicId } from "@/lib/public-id";
import { resultMetadata } from "@/lib/result-metadata";

type Props = {
  params: Promise<{ id: string }>;
  searchParams: Promise<{ sort?: string; order?: string }>;
};
const safeLink = (url: string | null) =>
  url && /^https?:\/\//i.test(url) ? url : null;
const formatDate = (date: string) => {
  const [year, month, day] = date.split("-");
  return `${Number(day)}.${Number(month)}.${year}`;
};

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { id } = await params;
  const numericId = internalId("result", id);
  if (!numericId) return { title: "Tulemust ei leitud" };
  const data = await getApi<Results>(`/subcontests/${numericId}`);
  return { title: data.title || data.contest_name };
}

export default async function ResultsPage({ params, searchParams }: Props) {
  const { id } = await params;
  const { sort, order } = await searchParams;
  const numericId = internalId("result", id);
  if (!numericId) notFound();
  const data = await getApi<Results>(`/subcontests/${numericId}`);
  const documents = resultMetadata(numericId);
  const fieldIndex = sort?.startsWith("field-") ? Number(sort.slice(6)) : -1;
  const validField =
    Number.isInteger(fieldIndex) &&
    fieldIndex >= 0 &&
    fieldIndex < data.columns.length;
  const sortedRows =
    sort &&
    (["placement", "name", "school", "mentor"].includes(sort) || validField)
      ? [...data.rows].sort((a, b) => {
          const value = (row: Results["rows"][number]) =>
            sort === "placement"
              ? row.placement
              : sort === "name"
                ? row.person_name
                : sort === "school"
                  ? row.school
                  : sort === "mentor"
                    ? row.mentors.join(" / ")
                    : row.fields[fieldIndex];
          const comparison = compareValues(value(a), value(b));
          return order === "desc" ? -comparison : comparison;
        })
      : data.rows;
  const hasGroup = data.rows.some((r) => r.age_group);
  const hasSchool = data.rows.some((r) => r.school);
  const hasMentor = data.rows.some((r) => r.mentors.length > 0);
  const contestLabel =
    data.type && data.year !== null
      ? `${data.type.charAt(0).toLocaleUpperCase("et-EE")}${data.type.slice(1).toLocaleLowerCase("et-EE")} ${data.year}/${data.year + 1}`
      : data.contest_name;
  const date = data.start_date
    ? data.end_date && data.end_date !== data.start_date
      ? `${formatDate(data.start_date)}–${formatDate(data.end_date)}`
      : formatDate(data.start_date)
    : data.end_date
      ? formatDate(data.end_date)
      : null;
  return (
    <>
      <section className="page-intro">
        <Breadcrumbs
          items={[
            { label: "Olümpiaadid", href: "/contests" },
            ...(data.subject
              ? [
                  {
                    label: data.subject,
                    href: data.subject_abbrev
                      ? `/contests/${data.subject_abbrev}`
                      : "/contests",
                  },
                ]
              : []),
            { label: contestLabel, href: `/results/${id}` },
          ]}
        />
        {(data.subcontest || data.age_group) && (
          <p>{data.subcontest || data.age_group}</p>
        )}
        {date && (
          <p className="results-date">
            Toimumisaeg:{" "}
            <time dateTime={data.start_date || data.end_date || undefined}>
              {date}
            </time>
          </p>
        )}
        {documents.status === "partial" && (
          <p>Ainult osa tulemustest on andmebaasis.</p>
        )}
        <div className="actions">
          <a href={`/api/subcontests/${numericId}?format=csv`}>
            Laadi alla CSV
          </a>
          {(documents.questions?.localUrl || safeLink(data.tasks_link)) && (
            <a
              href={documents.questions?.localUrl || safeLink(data.tasks_link)!}
            >
              Ülesanded ↗
            </a>
          )}
          {documents.questions?.localUrl && safeLink(data.tasks_link) && (
            <a href={safeLink(data.tasks_link)!}>Ülesannete algallikas ↗</a>
          )}
          {safeLink(data.solutions_link) && (
            <a href={safeLink(data.solutions_link)!}>Lahendused ↗</a>
          )}
          {(documents.regulations?.localUrl ||
            documents.regulations?.sourceUrl) && (
            <a
              href={
                documents.regulations?.localUrl ||
                documents.regulations?.sourceUrl
              }
            >
              Juhend või ajakava ↗
            </a>
          )}
          {(documents.source?.localUrl || documents.source?.sourceUrl) && (
            <a href={documents.source?.localUrl || documents.source?.sourceUrl}>
              Tulemuste algallikas ↗
            </a>
          )}
        </div>
      </section>
      <div className="table-scroll">
        <table>
          <caption className="sr-only">
            {data.title || data.contest_name}
          </caption>
          <thead>
            <tr>
              <SortHeading
                label="Koht"
                column="placement"
                current={sort}
                order={order}
                base={`/results/${id}`}
              />
              <SortHeading
                label="Nimi"
                column="name"
                current={sort}
                order={order}
                base={`/results/${id}`}
              />
              {hasGroup && <th scope="col">Klass</th>}
              {hasSchool && (
                <SortHeading
                  label="Kool"
                  column="school"
                  current={sort}
                  order={order}
                  base={`/results/${id}`}
                />
              )}
              {hasMentor && (
                <SortHeading
                  label="Juhendaja"
                  column="mentor"
                  current={sort}
                  order={order}
                  base={`/results/${id}`}
                />
              )}
              {data.columns.map((c, i) => (
                <SortHeading
                  label={c}
                  column={`field-${i}`}
                  current={sort}
                  order={order}
                  base={`/results/${id}`}
                  key={`${i}-${c}`}
                />
              ))}
            </tr>
          </thead>
          <tbody>
            {sortedRows.map((r, i) => (
              <tr key={`${r.person_id ?? "anon"}-${i}`}>
                <td>{r.placement ?? ""}</td>
                <td>
                  {r.person_id ? (
                    <Link
                      prefetch={false}
                      href={`/people/${publicId("person", r.person_id)}`}
                    >
                      {r.person_name}
                    </Link>
                  ) : (
                    (r.person_name ?? "Nimi peidetud")
                  )}
                </td>
                {hasGroup && <td>{r.age_group}</td>}
                {hasSchool && (
                  <td>
                    {r.school_id ? (
                      <Link
                        prefetch={false}
                        href={`/schools/${publicId("school", r.school_id)}`}
                      >
                        {r.school}
                      </Link>
                    ) : (
                      r.school
                    )}
                  </td>
                )}
                {hasMentor && (
                  <td>
                    {r.mentor_links.length
                      ? r.mentor_links.map((m, n) => (
                          <span key={m.person_id}>
                            {n > 0 ? " / " : ""}
                            <Link
                              prefetch={false}
                              href={`/people/${publicId("person", m.person_id)}`}
                            >
                              {m.person_name}
                            </Link>
                          </span>
                        ))
                      : r.mentors.join(" / ")}
                  </td>
                )}
                {data.columns.map((_, n) => (
                  <td key={n}>{r.fields[n] ?? ""}</td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {data.rows.length === 0 && <p>Tulemusi ei ole veel lisatud.</p>}
      {data.description && <p className="description">{data.description}</p>}
    </>
  );
}
