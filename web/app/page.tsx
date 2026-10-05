import Link from "next/link";
import { permanentRedirect } from "next/navigation";
import { getApi, type Home } from "@/lib/api";
import { publicId } from "@/lib/public-id";

type Search = Record<string, string | string[] | undefined>;
const first = (value: string | string[] | undefined) =>
  Array.isArray(value) ? value[0] : value;

export default async function HomePage({
  searchParams,
}: {
  searchParams: Promise<Search>;
}) {
  const query = await searchParams;
  const id = first(query.id);
  const name = first(query.name);
  const personId = first(query.name_id);
  const schoolId = first(query.school_id);
  if (id && /^\d+$/.test(id))
    permanentRedirect(`/results/${publicId("result", Number(id))}`);
  if (name) permanentRedirect(`/search?q=${encodeURIComponent(name)}`);
  if (personId && /^\d+$/.test(personId))
    permanentRedirect(`/people/${publicId("person", Number(personId))}`);
  if (first(query.kool)) permanentRedirect("/schools");
  if (first(query.hof)) permanentRedirect("/people");
  if (schoolId && /^\d+$/.test(schoolId))
    permanentRedirect(`/schools/${publicId("school", Number(schoolId))}`);

  const home = await getApi<Home>("/site/home");
  const recent = new Map<
    string,
    {
      subject: string;
      type: string;
      subjectCode: string;
      date: string | null;
      items: Home["recent"];
    }
  >();
  for (const item of home.recent) {
    const key = JSON.stringify([
      item.subject,
      item.contest_type,
      item.contest_name,
    ]);
    const group = recent.get(key) ?? {
      subject: item.subject,
      type: item.contest_type,
      subjectCode: item.subject_abbrev,
      date: item.start_date || item.end_date,
      items: [],
    };
    group.items.push(item);
    recent.set(key, group);
  }
  // This server-rendered page uses the current time to label recent results.
  // eslint-disable-next-line react-hooks/purity
  const monthAgo = Date.now() - 30 * 24 * 60 * 60 * 1000;
  const isLastMonth = (date: string | null) =>
    date !== null && new Date(`${date}T00:00:00Z`).getTime() >= monthAgo;

  return (
    <>
      <section className="page-intro home-intro">
        <div className="home-intro-copy">
          <h1>Eesti olümpiaadide tulemused</h1>
          <p>
            Mitteametlik andmebaas, mis koondab Eesti olümpiaadide tulemusi,
            osalejaid ja koole.
          </p>
          <Link prefetch={false} className="primary-link" href="/contests">
            Sirvi olümpiaadide tulemusi →
          </Link>
        </div>
        <dl className="home-stats">
          <div>
            <dt>Õppeaineid</dt>
            <dd>{home.subjects}</dd>
          </div>
          <div>
            <dt>Võistlusi</dt>
            <dd>{home.contests}</dd>
          </div>
          <div>
            <dt>Õppeaastaid</dt>
            <dd>{home.seasons}</dd>
          </div>
          <div>
            <dt>Inimesi</dt>
            <dd>{home.people}</dd>
          </div>
          <div>
            <dt>Koole</dt>
            <dd>{home.schools}</dd>
          </div>
        </dl>
      </section>
      <section className="section-block">
        <div className="section-heading">
          <h2>
            {home.latest_year === null
              ? "Viimased tulemused"
              : `Viimased tulemused · ${home.latest_year}/${home.latest_year + 1}`}
          </h2>
        </div>
        {recent.size === 0 ? (
          <p>Tulemusi ei ole veel lisatud.</p>
        ) : (
          <div className="table-scroll">
            <table>
              <thead>
                <tr>
                  <th scope="col">Õppeaine</th>
                  <th scope="col">Võistlus</th>
                  <th scope="col">Tulemused</th>
                </tr>
              </thead>
              <tbody>
                {[...recent].map(([key, group]) => (
                  <tr
                    key={key}
                    className={
                      isLastMonth(group.date) ? "recent-month-row" : undefined
                    }
                  >
                    <td>
                      <Link
                        prefetch={false}
                        href={`/contests/${group.subjectCode}`}
                      >
                        {group.subject}
                      </Link>
                    </td>
                    <td>
                      {group.type}
                      {isLastMonth(group.date) && (
                        <span className="recent-badge">
                          Viimase 30 päeva jooksul
                        </span>
                      )}
                    </td>
                    <td>
                      <div className="home-result-links">
                        {group.items.map((item) => (
                          <Link
                            prefetch={false}
                            href={`/results/${publicId("result", item.id)}`}
                            key={item.id}
                          >
                            {item.subcontest_name || item.age_group}
                          </Link>
                        ))}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
      <section className="section-block">
        <h2>Viimati lisatud tulemused</h2>
        {home.recent_added.length === 0 ? (
          <p>Tulemusi ei ole veel lisatud.</p>
        ) : (
          <div className="table-scroll">
            <table>
              <thead>
                <tr>
                  <th scope="col">Õppeaine</th>
                  <th scope="col">Võistlus</th>
                  <th scope="col">Õppeaasta</th>
                  <th scope="col">Tulemused</th>
                </tr>
              </thead>
              <tbody>
                {home.recent_added.map((item) => (
                  <tr key={item.id}>
                    <td>
                      <Link
                        prefetch={false}
                        href={`/contests/${item.subject_abbrev}`}
                      >
                        {item.subject}
                      </Link>
                    </td>
                    <td>{item.contest_type}</td>
                    <td>
                      {item.year === null
                        ? "—"
                        : `${item.year}/${item.year + 1}`}
                    </td>
                    <td>
                      <Link
                        prefetch={false}
                        href={`/results/${publicId("result", item.id)}`}
                      >
                        {item.subcontest_name || item.age_group}
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </>
  );
}
