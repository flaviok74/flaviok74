import { NextResponse } from "next/server";
import { prisma } from "@/lib/db";

function resolveOrganizationId(request: Request) {
  return request.headers.get("x-organization-id") ?? "";
}

export async function GET(request: Request) {
  const organizationId = resolveOrganizationId(request);

  if (!organizationId) {
    return NextResponse.json({ error: "Missing organization" }, { status: 400 });
  }

  const quotes = await prisma.freightQuote.findMany({
    where: { organizationId },
    include: { supplier: true, originPort: true, destinationPort: true, costLines: true }
  });

  return NextResponse.json({ data: quotes });
}

export async function POST(request: Request) {
  const organizationId = resolveOrganizationId(request);

  if (!organizationId) {
    return NextResponse.json({ error: "Missing organization" }, { status: 400 });
  }

  const payload = await request.json();

  const quote = await prisma.freightQuote.create({
    data: {
      organizationId,
      supplierId: payload.supplierId,
      originPortId: payload.originPortId,
      destinationPortId: payload.destinationPortId,
      currency: payload.currency,
      validityEnd: new Date(payload.validityEnd),
      sourceType: payload.sourceType,
      status: payload.status,
      createdByUserId: payload.createdByUserId,
      carrier: payload.carrier,
      service: payload.service,
      incoterm: payload.incoterm,
      sourceUrl: payload.sourceUrl,
      sourceReference: payload.sourceReference,
      costLines: {
        create: payload.costLines ?? []
      }
    }
  });

  return NextResponse.json({ data: quote }, { status: 201 });
}
