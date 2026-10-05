import { notFound, permanentRedirect } from "next/navigation";
import { getSubjects } from "@/lib/api";

export default async function LegacyOlympiadPage({
  params,
}: {
  params: Promise<{ subject: string; type: string }>;
}) {
  const { subject, type } = await params;
  const entry = (await getSubjects()).find((item) => item.subject === subject);
  if (!entry || !type) notFound();
  permanentRedirect(`/contests/${entry.subject_abbrev}`);
}
