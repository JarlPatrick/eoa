import Link from "next/link";

export default function NotFound() {
  return (
    <section className="page-intro">
      <h1>Lehte ei leitud</h1>
      <p>Soovitud tulemust või profiili ei leitud.</p>
      <Link prefetch={false} href="/">
        Tagasi avalehele
      </Link>
    </section>
  );
}
