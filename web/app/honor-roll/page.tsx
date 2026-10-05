import { permanentRedirect } from "next/navigation";

export default async function OldHonorRoll({
  searchParams,
}: {
  searchParams: Promise<Record<string, string>>;
}) {
  const params = new URLSearchParams(await searchParams);
  permanentRedirect(`/people${params.size ? `?${params}` : ""}`);
}
