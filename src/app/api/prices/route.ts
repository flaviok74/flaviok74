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

  const quotes = await prisma.priceQuote.findMany({
    where: { organizationId },
    include: { vendor: true, priceLines: { include: { product: true } } }
  });

  return NextResponse.json({ data: quotes });
}

export async function POST(request: Request) {
  const organizationId = resolveOrganizationId(request);

  if (!organizationId) {
    return NextResponse.json({ error: "Missing organization" }, { status: 400 });
  }

  const payload = await request.json();

  const quote = await prisma.priceQuote.create({
    data: {
      organizationId,
      vendorId: payload.vendorId,
      currency: payload.currency,
      validTo: new Date(payload.validTo),
      validFrom: payload.validFrom ? new Date(payload.validFrom) : undefined,
      sourceType: payload.sourceType,
      status: payload.status,
      createdByUserId: payload.createdByUserId,
      notes: payload.notes,
      sourceUrl: payload.sourceUrl,
      sourceReference: payload.sourceReference,
      priceLines: {
        create: payload.priceLines ?? []
      }
    }
  });

  return NextResponse.json({ data: quote }, { status: 201 });
}
