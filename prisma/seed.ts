import { PrismaClient, QuoteSourceType, QuoteStatus, ChargeGroup } from "@prisma/client";

const prisma = new PrismaClient();

async function main() {
  const organization = await prisma.organization.create({
    data: {
      name: "Ekoquim Logistics",
      users: {
        create: [
          {
            name: "Admin User",
            email: "admin@ekoquim.test",
            passwordHash: "changeme",
            role: "ADMIN"
          },
          {
            name: "Operador",
            email: "operador@ekoquim.test",
            passwordHash: "changeme",
            role: "OPERATOR"
          },
          {
            name: "Auditor",
            email: "auditor@ekoquim.test",
            passwordHash: "changeme",
            role: "AUDITOR"
          }
        ]
      }
    }
  });

  const suppliers = await prisma.supplier.createMany({
    data: [
      {
        organizationId: organization.id,
        name: "Atlantic Shipping",
        country: "BR",
        email: "quotes@atlantic.test",
        status: "active"
      },
      {
        organizationId: organization.id,
        name: "BlueWave Logistics",
        country: "US",
        email: "pricing@bluewave.test",
        status: "active"
      },
      {
        organizationId: organization.id,
        name: "Pacific Global",
        country: "CN",
        email: "sales@pacific.test",
        status: "inactive"
      }
    ]
  });

  const portData = [
    { name: "Santos", country: "BR", code: "BRSSZ" },
    { name: "Itajai", country: "BR", code: "BRITJ" },
    { name: "Rio de Janeiro", country: "BR", code: "BRRIO" },
    { name: "Hamburg", country: "DE", code: "DEHAM" },
    { name: "Rotterdam", country: "NL", code: "NLRTM" },
    { name: "Antwerp", country: "BE", code: "BEANR" },
    { name: "Shanghai", country: "CN", code: "CNSHA" },
    { name: "Ningbo", country: "CN", code: "CNNGB" },
    { name: "Los Angeles", country: "US", code: "USLAX" },
    { name: "New York", country: "US", code: "USNYC" }
  ];

  const ports = await prisma.port.createMany({
    data: portData.map((port) => ({
      organizationId: organization.id,
      name: port.name,
      country: port.country,
      code: port.code
    }))
  });

  await prisma.containerType.createMany({
    data: [
      { name: "20GP", code: "20GP", description: "Standard 20-foot" },
      { name: "40HC", code: "40HC", description: "High Cube 40-foot" },
      { name: "40NOR", code: "40NOR", description: "Non-operating reefer" }
    ]
  });

  const admin = await prisma.user.findFirstOrThrow({
    where: { email: "admin@ekoquim.test" }
  });

  const supplierList = await prisma.supplier.findMany({
    where: { organizationId: organization.id }
  });
  const portList = await prisma.port.findMany({
    where: { organizationId: organization.id }
  });

  for (let index = 0; index < 10; index += 1) {
    const supplier = supplierList[index % supplierList.length];
    const origin = portList[index % portList.length];
    const destination = portList[(index + 3) % portList.length];
    await prisma.freightQuote.create({
      data: {
        organizationId: organization.id,
        supplierId: supplier.id,
        originPortId: origin.id,
        destinationPortId: destination.id,
        carrier: "Sample Carrier",
        service: "Direct",
        currency: "USD",
        validityEnd: new Date(Date.now() + 1000 * 60 * 60 * 24 * 30),
        transitTimeDays: 25,
        rolloverRisk: "MEDIUM",
        sourceType: QuoteSourceType.MANUAL,
        status: QuoteStatus.APPROVED,
        createdByUserId: admin.id,
        costLines: {
          create: [
            {
              group: ChargeGroup.ORIGIN,
              chargeName: "THC",
              amount20gp: 120,
              amount40hc: 180,
              amount40nor: 180
            },
            {
              group: ChargeGroup.OCEAN,
              chargeName: "Ocean Freight",
              amount20gp: 800,
              amount40hc: 1200,
              amount40nor: 1250
            },
            {
              group: ChargeGroup.DESTINATION,
              chargeName: "Documentation",
              amount20gp: 90,
              amount40hc: 90,
              amount40nor: 90
            }
          ]
        }
      }
    });
  }

  void suppliers;
  void ports;
}

main()
  .catch(async (error) => {
    console.error(error);
    process.exit(1);
  })
  .finally(async () => {
    await prisma.$disconnect();
  });
