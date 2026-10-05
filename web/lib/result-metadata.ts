import records from "@/data/result-metadata.json";
import occurrences from "@/data/competition-occurrences.json";

export type DocumentLink = { sourceUrl?: string; localUrl?: string };
export type ResultMetadata = {
  status?: "complete" | "partial" | "source-only";
  questions?: DocumentLink;
  regulations?: DocumentLink;
  source?: DocumentLink;
};

export function resultMetadata(id: number): ResultMetadata {
  return (records as Record<string, ResultMetadata>)[String(id)] ?? {};
}

export type OccurrenceMetadata = {
  status: "not-held" | "source-only";
  source?: DocumentLink;
  questions?: DocumentLink;
  regulations?: DocumentLink;
};

export function occurrenceMetadata(
  subject: string,
  type: string,
  age: string,
  year: number | null,
): OccurrenceMetadata | null {
  const key = JSON.stringify([subject, type, age, year]);
  return (occurrences as Record<string, OccurrenceMetadata>)[key] ?? null;
}
