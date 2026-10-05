import type { Metadata } from "next";
import Link from "next/link";
import { getApi, type Statistics } from "@/lib/api";
import { publicId } from "@/lib/public-id";
import { HonorRollTable } from "@/components/HonorRollTable";
import { compareValues } from "@/lib/sort";
import { rankingScore } from "@/lib/score";

export const metadata: Metadata = { title: "Inimesed" };

export default async function PeoplePage({
  searchParams,
}: {
  searchParams: Promise<{
    view?: string;
    sort?: string;
    order?: string;
    page?: string;
    rows?: string;
  }>;
}) {
  const { view, sort, order, page, rows } = await searchParams;
  const selected = view === "mentors" ? "mentors" : "students";
  const data = await getApi<Statistics>(
    `/statistics/${selected}?weighted=true`,
  );
  const scored = data.rows.map((row) => [...row, rankingScore(row)]);
  const indexes: Record<string, number> = {
    name: 1,
    participations: 2,
    first: 3,
    second: 4,
    third: 5,
    score: 6,
  };
  const sorted =
    sort && Object.hasOwn(indexes, sort)
      ? [...scored].sort((a, b) => {
          const comparison = compareValues(a[indexes[sort]], b[indexes[sort]]);
          return order === "desc" ? -comparison : comparison;
        })
      : scored.sort(
          (a, b) =>
            Number(b[6]) - Number(a[6]) ||
            Number(b[3]) - Number(a[3]) ||
            String(a[1]).localeCompare(String(b[1]), "et"),
        );
  const publicRows = sorted.map((row) => [
    publicId("person", Number(row[0])),
    ...row.slice(1),
  ]);
  return (
    <>
      <section className="page-intro">
        <h1>Inimesed</h1>
        <p>
          Edetabelis on vähemalt kümne osalemise või juhendamisega inimesed ning
          õpilased, kes on jõudnud esikolmikusse. Punktid: iga osalemine või
          juhendamine 1, esimene koht 8, teine 4 ja kolmas 2 lisapunkti.
          Esikolmiku kohad on kaalutud vanuserühma klasside arvu järgi, kõige
          rohkem kolme klassiga.
        </p>
      </section>
      <nav className="school-tabs" aria-label="Inimeste vaade">
        <Link
          prefetch={false}
          href="/people"
          aria-current={selected === "students" ? "page" : undefined}
        >
          Õpilased
        </Link>
        <Link
          prefetch={false}
          href="/people?view=mentors"
          aria-current={selected === "mentors" ? "page" : undefined}
        >
          Juhendajad
        </Link>
      </nav>
      <HonorRollTable
        data={publicRows}
        sort={sort}
        order={order}
        page={page}
        rows={rows}
        view={selected}
      />
    </>
  );
}
