import { describe, expect, it } from "vitest";
import { calculateTotals } from "./totals";

const sampleCosts = [
  { group: "ORIGIN", amount20gp: 100, amount40hc: 150, amount40nor: null },
  { group: "OCEAN", amount20gp: 400, amount40hc: 600, amount40nor: 650 },
  { group: "DESTINATION", amount20gp: 80, amount40hc: 80, amount40nor: 80 }
] as const;

describe("calculateTotals", () => {
  it("sums totals by group and overall", () => {
    const totals = calculateTotals(sampleCosts as any);

    expect(totals.groupTotals.ORIGIN.total20gp).toBe(100);
    expect(totals.groupTotals.OCEAN.total40hc).toBe(600);
    expect(totals.groupTotals.DESTINATION.total40nor).toBe(80);
    expect(totals.grandTotal.total20gp).toBe(580);
    expect(totals.grandTotal.total40hc).toBe(830);
    expect(totals.grandTotal.total40nor).toBe(730);
  });
});
