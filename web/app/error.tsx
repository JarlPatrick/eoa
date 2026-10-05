"use client";

export default function ErrorPage({ reset }: { reset: () => void }) {
  return (
    <section className="page-intro">
      <h1>Andmete laadimine ebaõnnestus</h1>
      <p>Palun proovige mõne aja pärast uuesti.</p>
      <button onClick={reset}>Proovi uuesti</button>
    </section>
  );
}
