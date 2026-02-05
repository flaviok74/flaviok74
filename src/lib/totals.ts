import { FreightQuoteCost } from "@prisma/client";

type Totals = {
  groupTotals: Record<string, { total20gp: number; total40hc: number; total40nor: number }>;
  grandTotal: { total20gp: number; total40hc: number; total40nor: number };
};

export function calculateTotals(costs: FreightQuoteCost[]): Totals {
  const groupTotals: Totals["groupTotals"] = {};
  const grandTotal = { total20gp: 0, total40hc: 0, total40nor: 0 };

  for (const cost of costs) {
    if (!groupTotals[cost.group]) {
      groupTotals[cost.group] = { total20gp: 0, total40hc: 0, total40nor: 0 };
    }
    const amount20gp = Number(cost.amount20gp ?? 0);
    const amount40hc = Number(cost.amount40hc ?? 0);
    const amount40nor = Number(cost.amount40nor ?? 0);

    groupTotals[cost.group].total20gp += amount20gp;
    groupTotals[cost.group].total40hc += amount40hc;
    groupTotals[cost.group].total40nor += amount40nor;

    grandTotal.total20gp += amount20gp;
    grandTotal.total40hc += amount40hc;
    grandTotal.total40nor += amount40nor;
  }

  return { groupTotals, grandTotal };
}
