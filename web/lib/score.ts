export function rankingScore(row: (string | number)[]): number {
  return (
    Number(row[2]) +
    8 * Number(row[3]) +
    4 * Number(row[4]) +
    2 * Number(row[5])
  );
}
