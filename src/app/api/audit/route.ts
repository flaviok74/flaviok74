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

  const logs = await prisma.auditLog.findMany({
    where: { organizationId },
    orderBy: { createdAt: "desc" }
  });

  return NextResponse.json({ data: logs });
}
