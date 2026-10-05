import type { NextRequest } from "next/server";

const baseUrl = process.env.API_INTERNAL_URL ?? "http://localhost:8000";

function publicPath(path: string): boolean {
  return (
    path === "openapi.json" ||
    /^contest(?:\/[^/]+){0,4}$/.test(path) ||
    /^subcontests\/[1-9]\d*$/.test(path) ||
    /^people\/(?:search|[1-9]\d*)$/.test(path) ||
    /^(?:contestant|mentor)\/[1-9]\d*$/.test(path) ||
    /^schools(?:\/search|\/[1-9]\d*\/(?:students|mentors))?$/.test(path)
  );
}

export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ path: string[] }> },
) {
  const { path: segments } = await params;
  if (
    segments.some(
      (segment) =>
        segment === "." ||
        segment === ".." ||
        segment.includes("/") ||
        segment.includes("\\"),
    )
  ) {
    return new Response("Not found", { status: 404 });
  }
  const path = segments.join("/");
  if (!publicPath(path)) return new Response("Not found", { status: 404 });

  const upstream = new URL(
    `${baseUrl}/${segments.map(encodeURIComponent).join("/")}`,
  );
  upstream.search = request.nextUrl.search;
  const response = await fetch(upstream, { cache: "no-store" });
  const headers = new Headers({});
  for (const [name, value] of response.headers) {
    if (
      ["content-type", "content-disposition"].includes(name) ||
      name.startsWith("x-result-")
    )
      headers.set(name, value);
  }
  return new Response(response.body, { status: response.status, headers });
}
