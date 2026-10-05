import type { Metadata } from "next";
import Link from "next/link";
import { getApiPage, type ContestItem, type PersonLink } from "@/lib/api";
import { publicId } from "@/lib/public-id";
import { Pagination, pageNumber } from "@/components/Pagination";

export const metadata: Metadata = { title: "Üldotsing" };

const pageSize = 20;
type Search = {
  q?: string;
  studentsPage?: string;
  mentorsPage?: string;
  schoolsPage?: string;
  contestsPage?: string;
};

export default async function SearchPage({
  searchParams,
}: {
  searchParams: Promise<Search>;
}) {
  const params = await searchParams;
  const query = (params.q ?? "").trim();
  const intro = (
    <section className="page-intro">
      <h1>Üldotsing</h1>
      <p>Otsi õpilasi, juhendajaid, koole ja võistlusi.</p>
    </section>
  );
  if (!query) return intro;

  const studentPage = pageNumber(params.studentsPage);
  const mentorPage = pageNumber(params.mentorsPage);
  const schoolPage = pageNumber(params.schoolsPage);
  const contestPage = pageNumber(params.contestsPage);
  const encoded = encodeURIComponent(query);
  const [students, mentors, schools, contests] = await Promise.all([
    getApiPage<PersonLink[]>(
      `/people/search?q=${encoded}&role=student&offset=${(studentPage - 1) * pageSize}&limit=${pageSize}`,
    ),
    getApiPage<PersonLink[]>(
      `/people/search?q=${encoded}&role=mentor&offset=${(mentorPage - 1) * pageSize}&limit=${pageSize}`,
    ),
    getApiPage<{ school_id: number; school_name: string }[]>(
      `/schools/search?q=${encoded}&offset=${(schoolPage - 1) * pageSize}&limit=${pageSize}`,
    ),
    getApiPage<ContestItem[]>(
      `/site/contests?q=${encoded}&offset=${(contestPage - 1) * pageSize}&limit=${pageSize}`,
    ),
  ]);
  const paginationParams = {
    q: query,
    studentsPage: params.studentsPage,
    mentorsPage: params.mentorsPage,
    schoolsPage: params.schoolsPage,
    contestsPage: params.contestsPage,
  };

  return (
    <>
      {intro}
      <section className="section-block">
        <h2>Õpilased · {students.total}</h2>
        {students.items.length ? (
          <ul className="link-list">
            {students.items.map((person) => (
              <li key={person.person_id}>
                <Link
                  prefetch={false}
                  href={`/people/${publicId("person", person.person_id)}`}
                >
                  {person.person_name}
                </Link>
              </li>
            ))}
          </ul>
        ) : (
          <p>Õpilasi ei leitud.</p>
        )}
        <Pagination
          page={studentPage}
          total={students.total}
          pageSize={pageSize}
          path="/search"
          pageKey="studentsPage"
          params={paginationParams}
        />
      </section>
      <section className="section-block">
        <h2>Juhendajad · {mentors.total}</h2>
        {mentors.items.length ? (
          <ul className="link-list">
            {mentors.items.map((person) => (
              <li key={person.person_id}>
                <Link
                  prefetch={false}
                  href={`/people/${publicId("person", person.person_id)}`}
                >
                  {person.person_name}
                </Link>
              </li>
            ))}
          </ul>
        ) : (
          <p>Juhendajaid ei leitud.</p>
        )}
        <Pagination
          page={mentorPage}
          total={mentors.total}
          pageSize={pageSize}
          path="/search"
          pageKey="mentorsPage"
          params={paginationParams}
        />
      </section>
      <section className="section-block">
        <h2>Koolid · {schools.total}</h2>
        {schools.items.length ? (
          <ul className="link-list">
            {schools.items.map((school) => (
              <li key={school.school_id}>
                <Link
                  prefetch={false}
                  href={`/schools/${publicId("school", school.school_id)}`}
                >
                  {school.school_name}
                </Link>
              </li>
            ))}
          </ul>
        ) : (
          <p>Koole ei leitud.</p>
        )}
        <Pagination
          page={schoolPage}
          total={schools.total}
          pageSize={pageSize}
          path="/search"
          pageKey="schoolsPage"
          params={paginationParams}
        />
      </section>
      <section className="section-block">
        <h2>Võistlused · {contests.total}</h2>
        {contests.items.length ? (
          <ul className="link-list">
            {contests.items.map((item) => (
              <li key={item.id}>
                <Link
                  prefetch={false}
                  href={`/results/${publicId("result", item.id)}`}
                >
                  {item.subject} · {item.contest_type} ·{" "}
                  {item.year === null
                    ? "Aasta teadmata"
                    : `${item.year}/${item.year + 1}`}{" "}
                  · {item.age_group}
                </Link>
              </li>
            ))}
          </ul>
        ) : (
          <p>Võistlusi ei leitud.</p>
        )}
        <Pagination
          page={contestPage}
          total={contests.total}
          pageSize={pageSize}
          path="/search"
          pageKey="contestsPage"
          params={paginationParams}
        />
      </section>
    </>
  );
}
