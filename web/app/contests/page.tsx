import type { Metadata } from "next";
import Link from "next/link";
import { getSubjects } from "@/lib/api";

export const metadata: Metadata = { title: "Olümpiaadid" };

export default async function ContestsPage() {
  const entries = await getSubjects();
  const subjects = entries
    .map((item) => [item.subject_abbrev, item.subject] as const)
    .sort(([, a], [, b]) => a.localeCompare(b, "et"));

  return (
    <>
      <section className="page-intro">
        <h1>Olümpiaadid</h1>
        <p>Vali õppeaine, et sirvida võistluste tulemusi õppeaastate kaupa.</p>
      </section>
      {subjects.length === 0 ? (
        <p>Õppeaineid ei leitud.</p>
      ) : (
        <ul className="link-list subject-list">
          {subjects.map(([code, name]) => (
            <li key={code}>
              <Link prefetch={false} href={`/contests/${code}`}>
                {name}
              </Link>
            </li>
          ))}
        </ul>
      )}
    </>
  );
}
