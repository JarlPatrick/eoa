import "server-only";
import { createHmac, timingSafeEqual } from "node:crypto";

type Kind = "result" | "school" | "person";

function secret() {
  const value = process.env.PUBLIC_ID_SECRET;
  if (!value || value.length < 32)
    throw new Error("PUBLIC_ID_SECRET must contain at least 32 characters");
  return value;
}

export function publicId(kind: Kind, id: number): string {
  if (!Number.isSafeInteger(id) || id < 1 || id > 0xffffffff)
    throw new Error("Invalid public ID source");
  const bytes = Buffer.alloc(16);
  bytes.writeUInt32BE(id, 0);
  createHmac("sha256", secret())
    .update(`${kind}:${id}`)
    .digest()
    .copy(bytes, 4, 0, 12);
  bytes[6] = (bytes[6] & 0x0f) | 0x40;
  bytes[8] = (bytes[8] & 0x3f) | 0x80;
  const hex = bytes.toString("hex");
  return `${hex.slice(0, 8)}-${hex.slice(8, 12)}-${hex.slice(12, 16)}-${hex.slice(16, 20)}-${hex.slice(20)}`;
}

export function internalId(kind: Kind, value: string): number | null {
  if (
    !/^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i.test(
      value,
    )
  )
    return null;
  const id = Number.parseInt(value.slice(0, 8), 16);
  if (id < 1) return null;
  const expected = Buffer.from(publicId(kind, id).replaceAll("-", ""), "hex");
  const actual = Buffer.from(value.replaceAll("-", ""), "hex");
  return timingSafeEqual(actual, expected) ? id : null;
}
