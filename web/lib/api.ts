import "server-only";
import { notFound } from "next/navigation";
import { cache } from "react";

const baseUrl = process.env.API_INTERNAL_URL ?? "http://localhost:8000";
const internalHeaders = {
  "X-EOA-Internal-Token": process.env.EOA_INTERNAL_API_TOKEN ?? "",
};

const getJson = cache(async (path: string): Promise<unknown> => {
  const response = await fetch(`${baseUrl}${path}`, {
    cache: "no-store",
    headers: internalHeaders,
  });
  if (response.status === 404) notFound();
  if (!response.ok) throw new Error(`API ${path} returned ${response.status}`);
  return response.json();
});

export async function getApi<T>(path: string): Promise<T> {
  return (await getJson(path)) as T;
}

export async function getApiPage<T>(
  path: string,
): Promise<{ items: T; nextOffset: number | null; total: number }> {
  const response = await fetch(`${baseUrl}${path}`, {
    cache: "no-store",
    headers: internalHeaders,
  });
  if (!response.ok) throw new Error(`API ${path} returned ${response.status}`);
  const next = response.headers.get("X-Result-Next-Offset");
  return {
    items: (await response.json()) as T,
    nextOffset: next === null ? null : Number(next),
    total: Number(response.headers.get("X-Result-Total") ?? 0),
  };
}

export type ContestItem = {
  id: number;
  subcontest_name: string;
  contest_name: string | null;
  year: number | null;
  subject: string;
  subject_abbrev: string;
  contest_type: string;
  age_group: string;
  tasks_link?: string | null;
  solutions_link?: string | null;
  result_count?: number;
};

export type SubjectItem = { subject_abbrev: string; subject: string };
export const getSubjects = cache(() => getApi<SubjectItem[]>("/contest"));
export const getSubjectContests = cache((subject: string) =>
  getApi<ContestItem[]>(
    `/site/contests?subject=${encodeURIComponent(subject)}`,
  ),
);

export type Home = {
  subjects: number;
  contests: number;
  seasons: number;
  people: number;
  schools: number;
  latest_year: number | null;
  recent: (Omit<ContestItem, "year"> & {
    start_date: string | null;
    end_date: string | null;
  })[];
  recent_added: ContestItem[];
};

export type PersonLink = { person_id: number; person_name: string };

export type Results = {
  title: string;
  contest_name: string;
  subject: string | null;
  subject_abbrev: string | null;
  subcontest: string | null;
  age_group: string | null;
  type: string | null;
  year: number | null;
  start_date: string | null;
  end_date: string | null;
  columns: string[];
  rows: {
    placement: number | null;
    person_id: number | null;
    person_name: string | null;
    age_group: string | null;
    school_id: number | null;
    school: string | null;
    mentors: string[];
    mentor_links: PersonLink[];
    fields: string[];
  }[];
  tasks_link: string | null;
  solutions_link: string | null;
  description: string | null;
};

export type PersonEntry = {
  person_name: string;
  subject: string | null;
  type: string | null;
  season: string | null;
  age_group: string | null;
  placement: number | null;
  subcontest_id: number;
  subject_name: string | null;
  school_id: number | null;
  school_name: string | null;
  mentors: PersonLink[];
};

export type MentorEntry = {
  mentor_name: string;
  student_name: string;
  subject: string | null;
  type: string | null;
  season: string | null;
  age_group: string | null;
  placement: number | null;
  subcontest_id: number;
  subject_name: string | null;
  student_id: number | null;
  school_id: number | null;
  school_name: string | null;
};

export type SchoolRanking = {
  school_id: number | string;
  school_name: string;
  participations: number;
  students: number;
  first_places: number;
  second_places: number;
  third_places: number;
};

export type SchoolPeople = {
  school_id: number;
  school_name: string;
  total_students: number | null;
  total_participations: number | null;
  students: (PersonLink & { participations: number })[] | null;
  mentors: (PersonLink & { participations: number })[] | null;
};

export type Statistics = { fields: string[]; rows: (string | number)[][] };
