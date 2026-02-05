import { PriceQuoteLine } from "@prisma/client";

type Totals = {
  total: number;
  average: number;
  min: number;
  max: number;
};

export function calculatePriceStats(lines: PriceQuoteLine[]): Totals {
  if (!lines.length) {
    return { total: 0, average: 0, min: 0, max: 0 };
  }

  const prices = lines.map((line) => Number(line.unitPrice));
  const total = prices.reduce((acc, value) => acc + value, 0);
  const average = total / prices.length;
  const min = Math.min(...prices);
  const max = Math.max(...prices);

  return { total, average, min, max };
}
