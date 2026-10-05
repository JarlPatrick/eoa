import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { Breadcrumbs } from "@/components/Breadcrumbs";
import { Pagination, pageNumber } from "@/components/Pagination";
import { getApi, type SchoolPeople } from "@/lib/api";
import { internalId, publicId } from "@/lib/public-id";

type Props = {
  params: Promise<{ id: string }>;
  searchParams: Promise<{ view?: string; page?: string }>;
};

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { id } = await params;
  const numericId = internalId("school", id);
  if (!numericId) return { title: "Kooli ei leitud" };
  const school = await getApi<SchoolPeople>(`/schools/${numericId}/students`);
  return { title: school.school_name };
}

export default async function SchoolPage({ params, searchParams }: Props) {
  const { id } = await params;
  const { view, page } = await searchParams;
  const numericId = internalId("school", id);
  if (!numericId) notFound();
  const selected = view === "mentors" ? "mentors" : "students";
  const [studentData, mentorData] = await Promise.all([
    getApi<SchoolPeople>(`/schools/${numericId}/students`),
    selected === "mentors"
      ? getApi<SchoolPeople>(`/schools/${numericId}/mentors`)
      : Promise.resolve(null),
  ]);
  const data = mentorData ?? studentData;
  const people = (
    selected === "students" ? (data.students ?? []) : (data.mentors ?? [])
  ).map((person) => ({
    ...person,
    person_id: publicId("person", person.person_id),
  }));
  const currentPage = Math.min(
    pageNumber(page),
    Math.max(1, Math.ceil(people.length / 50)),
  );

  return (
    <>
      <section className="page-intro">
        <Breadcrumbs
          items={[
            { label: "Koolid", href: "/schools" },
            { label: data.school_name, href: `/schools/${id}` },
          ]}
        />
        <p>
          Osalemisi kokku:{" "}
          <strong>{studentData.total_participations ?? "—"}</strong> (ka need,
          mille õpilase nime siin ei kuvata).
        </p>
      </section>
      <nav className="school-tabs" aria-label="Kooli inimesed">
        <Link
          prefetch={false}
          href={`/schools/${id}`}
          aria-current={selected === "students" ? "page" : undefined}
        >
          Õpilased
        </Link>
        <Link
          prefetch={false}
          href={`/schools/${id}?view=mentors`}
          aria-current={selected === "mentors" ? "page" : undefined}
        >
          Juhendajad
        </Link>
      </nav>
      <PeopleTable
        people={people.slice((currentPage - 1) * 50, currentPage * 50)}
        countLabel={
          selected === "students" ? "Osalemisi" : "Õpilasi juhendatud"
        }
      />
      <Pagination
        page={currentPage}
        total={people.length}
        pageSize={50}
        path={`/schools/${id}`}
        params={selected === "mentors" ? { view: "mentors" } : {}}
      />
    </>
  );
}

function PeopleTable({
  people,
  countLabel,
}: {
  people: { person_id: string; person_name: string; participations: number }[];
  countLabel: string;
}) {
  if (!people.length) return <p>Andmeid ei leitud.</p>;
  return (
    <div className="table-scroll">
      <table>
        <thead>
          <tr>
            <th scope="col">Nimi</th>
            <th scope="col">{countLabel}</th>
          </tr>
        </thead>
        <tbody>
          {people.map((person) => (
            <tr key={person.person_id}>
              <td>
                <Link prefetch={false} href={`/people/${person.person_id}`}>
                  {person.person_name}
                </Link>
              </td>
              <td>{person.participations}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
