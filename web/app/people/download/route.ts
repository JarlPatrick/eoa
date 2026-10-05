import { rankingScore } from "@/lib/score";

const baseUrl = process.env.API_INTERNAL_URL ?? "http://localhost:8000";

export async function GET(request: Request) {
  const view = new URL(request.url).searchParams.get("view");
  if (view !== "mentors") return new Response("Not found", { status: 404 });
  const response = await fetch(`${baseUrl}/statistics/${view}?weighted=true`, {
    cache: "no-store",
    headers: {
      "X-EOA-Internal-Token": process.env.EOA_INTERNAL_API_TOKEN ?? "",
    },
  });
  if (!response.ok)
    return new Response("Andmeid ei õnnestunud laadida", { status: 502 });
  const data = (await response.json()) as {
    fields: string[];
    rows: (string | number)[][];
  };
  const csvCell = (value: string | number) =>
    `"${String(value).replaceAll('"', '""')}"`;
  const lines = [
    [...data.fields, "score"].map(csvCell).join(","),
    ...data.rows.map((row) =>
      [...row, rankingScore(row)].map(csvCell).join(","),
    ),
  ];
  return new Response(`\uFEFF${lines.join("\r\n")}\r\n`, {
    headers: {
      "Content-Type": "text/csv; charset=utf-8",
      "Content-Disposition": `attachment; filename="${view}.csv"`,
    },
  });
}
