import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { Breadcrumbs } from "@/components/Breadcrumbs";
import { SortHeading } from "@/components/SortHeading";
import {
  getApi,
  type MentorEntry,
  type PersonEntry,
  type PersonLink,
} from "@/lib/api";
import { internalId, publicId } from "@/lib/public-id";
import { compareValues } from "@/lib/sort";

type Search = {
  sort?: string;
  order?: string;
  mentorSort?: string;
  mentorOrder?: string;
};
type Props = { params: Promise<{ id: string }>; searchParams: Promise<Search> };

function sortedRows<T>(
  rows: T[],
  key: string | undefined,
  order: string | undefined,
  values: Record<string, (row: T) => string | number | null | undefined>,
): T[] {
  if (!key || !Object.hasOwn(values, key)) return rows;
  return [...rows].sort((a, b) => {
    const comparison = compareValues(values[key](a), values[key](b));
    return order === "desc" ? -comparison : comparison;
  });
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { id } = await params;
  const numericId = internalId("person", id);
  if (!numericId) return { title: "Inimest ei leitud" };
  const person = await getApi<PersonLink>(`/people/${numericId}`);
  return { title: person.person_name };
}

export default async function PersonPage({ params, searchParams }: Props) {
  const { id } = await params;
  const { sort, order, mentorSort, mentorOrder } = await searchParams;
  const numericId = internalId("person", id);
  if (!numericId) notFound();
  const [person, results, mentees] = await Promise.all([
    getApi<PersonLink>(`/people/${numericId}`),
    getApi<PersonEntry[]>(`/contestant/${numericId}`),
    getApi<MentorEntry[]>(`/mentor/${numericId}`),
  ]);
  const path = `/people/${id}`;
  const sortedResults = sortedRows(results, sort, order, {
    season: (row) => row.season,
    subject: (row) => row.subject_name,
    contest: (row) => row.type,
    age: (row) => row.age_group,
    school: (row) => row.school_name,
    mentor: (row) =>
      row.mentors.map((mentor) => mentor.person_name).join(" / "),
    placement: (row) => row.placement,
  });
  const sortedMentees = sortedRows(mentees, mentorSort, mentorOrder, {
    season: (row) => row.season,
    student: (row) => row.student_name,
    subject: (row) => row.subject_name,
    contest: (row) => row.type,
    age: (row) => row.age_group,
    school: (row) => row.school_name,
    placement: (row) => row.placement,
  });
  const resultHead = (label: string, column: string) => (
    <SortHeading
      label={label}
      column={column}
      current={sort}
      order={order}
      base={path}
      params={{ mentorSort, mentorOrder }}
    />
  );
  const mentorHead = (label: string, column: string) => (
    <SortHeading
      label={label}
      column={column}
      current={mentorSort}
      order={mentorOrder}
      base={path}
      sortKey="mentorSort"
      orderKey="mentorOrder"
      params={{ sort, order }}
    />
  );
  const schoolLink = (schoolId: number | null, schoolName: string | null) =>
    schoolId && schoolName ? (
      <Link prefetch={false} href={`/schools/${publicId("school", schoolId)}`}>
        {schoolName}
      </Link>
    ) : (
      schoolName || "—"
    );

  return (
    <>
      <section className="page-intro">
        <Breadcrumbs
          items={[
            { label: "Inimesed", href: "/people" },
            { label: person.person_name, href: path },
          ]}
        />
      </section>
      <section className="section-block">
        <h2>Osalemised · {results.length}</h2>
        {results.length ? (
          <div className="table-scroll">
            <table>
              <thead>
                <tr>
                  {resultHead("Õppeaasta", "season")}
                  {resultHead("Õppeaine", "subject")}
                  {resultHead("Võistlus", "contest")}
                  {resultHead("Klass", "age")}
                  {resultHead("Kool", "school")}
                  {resultHead("Juhendaja", "mentor")}
                  {resultHead("Koht", "placement")}
                </tr>
              </thead>
              <tbody>
                {sortedResults.map((r, i) => (
                  <tr key={`${r.subcontest_id}-${i}`}>
                    <td>{r.season}</td>
                    <td>{r.subject_name}</td>
                    <td>
                      <Link
                        prefetch={false}
                        href={`/results/${publicId("result", r.subcontest_id)}`}
                      >
                        {r.type ?? "Tulemused"}
                      </Link>
                    </td>
                    <td>{r.age_group}</td>
                    <td>{schoolLink(r.school_id, r.school_name)}</td>
                    <td>
                      {r.mentors.map((mentor, index) => (
                        <span key={mentor.person_id}>
                          {index > 0 ? " / " : ""}
                          <Link
                            prefetch={false}
                            href={`/people/${publicId("person", mentor.person_id)}`}
                          >
                            {mentor.person_name}
                          </Link>
                        </span>
                      ))}
                    </td>
                    <td>{r.placement ?? ""}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <p>Osalemisi ei leitud.</p>
        )}
      </section>
      {mentees.length > 0 && (
        <section className="section-block">
          <h2>Juhendamised · {mentees.length}</h2>
          <div className="table-scroll">
            <table>
              <thead>
                <tr>
                  {mentorHead("Õppeaasta", "season")}
                  {mentorHead("Õpilane", "student")}
                  {mentorHead("Õppeaine", "subject")}
                  {mentorHead("Võistlus", "contest")}
                  {mentorHead("Klass", "age")}
                  {mentorHead("Kool", "school")}
                  {mentorHead("Koht", "placement")}
                </tr>
              </thead>
              <tbody>
                {sortedMentees.map((m, i) => (
                  <tr key={`${m.subcontest_id}-${i}`}>
                    <td>{m.season}</td>
                    <td>
                      {m.student_id ? (
                        <Link
                          prefetch={false}
                          href={`/people/${publicId("person", m.student_id)}`}
                        >
                          {m.student_name}
                        </Link>
                      ) : (
                        m.student_name
                      )}
                    </td>
                    <td>{m.subject_name}</td>
                    <td>
                      <Link
                        prefetch={false}
                        href={`/results/${publicId("result", m.subcontest_id)}`}
                      >
                        {m.type ?? "Tulemused"}
                      </Link>
                    </td>
                    <td>{m.age_group}</td>
                    <td>{schoolLink(m.school_id, m.school_name)}</td>
                    <td>{m.placement ?? ""}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      )}
    </>
  );
}
