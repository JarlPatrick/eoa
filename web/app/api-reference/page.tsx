import type { Metadata } from "next";
import { ApiDocs } from "@/components/ApiDocs";

export const metadata: Metadata = { title: "API" };

export default function ApiReferencePage() {
  return (
    <>
      <section className="page-intro">
        <h1>API</h1>
        <p>Otsi andmeid ja proovi päringuid otse dokumentatsioonis.</p>
      </section>
      <ApiDocs />
    </>
  );
}
