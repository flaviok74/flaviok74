import { describe, expect, it } from "vitest";
import { calculatePriceStats } from "./totals";

const sampleLines = [
  { unitPrice: 10 },
  { unitPrice: 25 },
  { unitPrice: 40 }
] as const;

describe("calculatePriceStats", () => {
  it("returns aggregated price stats", () => {
    const stats = calculatePriceStats(sampleLines as any);

    expect(stats.total).toBe(75);
    expect(stats.average).toBe(25);
    expect(stats.min).toBe(10);
    expect(stats.max).toBe(40);
  });

  it("returns zeros for empty list", () => {
    const stats = calculatePriceStats([] as any);

    expect(stats.total).toBe(0);
    expect(stats.average).toBe(0);
    expect(stats.min).toBe(0);
    expect(stats.max).toBe(0);
  });
});
