import { PrismaClient, QuoteSourceType, QuoteStatus } from "@prisma/client";

const prisma = new PrismaClient();

async function main() {
  const organization = await prisma.organization.create({
    data: {
      name: "Ekoquim Pricing Lab",
      users: {
        create: [
          {
            name: "Admin User",
            email: "admin@ekoquim.test",
            passwordHash: "changeme",
            role: "ADMIN"
          },
          {
            name: "Analista",
            email: "analista@ekoquim.test",
            passwordHash: "changeme",
            role: "ANALYST"
          },
          {
            name: "Leitura",
            email: "viewer@ekoquim.test",
            passwordHash: "changeme",
            role: "VIEWER"
          }
        ]
      }
    }
  });

  await prisma.vendor.createMany({
    data: [
      {
        organizationId: organization.id,
        name: "Atlas Distribuidora",
        country: "BR",
        email: "precos@atlas.test",
        status: "active"
      },
      {
        organizationId: organization.id,
        name: "Norte Supply",
        country: "US",
        email: "sales@norte.test",
        status: "active"
      },
      {
        organizationId: organization.id,
        name: "Mercury Global",
        country: "CN",
        email: "pricing@mercury.test",
        status: "inactive"
      }
    ]
  });

  const categories = await prisma.productCategory.createMany({
    data: [
      { organizationId: organization.id, name: "Químicos" },
      { organizationId: organization.id, name: "Embalagens" },
      { organizationId: organization.id, name: "Serviços" }
    ]
  });

  const categoryList = await prisma.productCategory.findMany({
    where: { organizationId: organization.id }
  });

  await prisma.product.createMany({
    data: [
      {
        organizationId: organization.id,
        categoryId: categoryList[0]?.id,
        name: "Ácido Cítrico",
        sku: "ACID-01",
        unit: "kg"
      },
      {
        organizationId: organization.id,
        categoryId: categoryList[0]?.id,
        name: "Peróxido de Hidrogênio",
        sku: "PER-02",
        unit: "kg"
      },
      {
        organizationId: organization.id,
        categoryId: categoryList[1]?.id,
        name: "Container 1000L",
        sku: "CONT-1000",
        unit: "un"
      },
      {
        organizationId: organization.id,
        categoryId: categoryList[2]?.id,
        name: "Frete Rodoviário",
        sku: "SERV-FRT",
        unit: "viagem"
      }
    ]
  });

  const admin = await prisma.user.findFirstOrThrow({
    where: { email: "admin@ekoquim.test" }
  });

  const vendors = await prisma.vendor.findMany({
    where: { organizationId: organization.id }
  });

  const products = await prisma.product.findMany({
    where: { organizationId: organization.id }
  });

  for (let index = 0; index < 10; index += 1) {
    const vendor = vendors[index % vendors.length];
    await prisma.priceQuote.create({
      data: {
        organizationId: organization.id,
        vendorId: vendor.id,
        currency: "USD",
        validTo: new Date(Date.now() + 1000 * 60 * 60 * 24 * 30),
        sourceType: QuoteSourceType.MANUAL,
        status: QuoteStatus.APPROVED,
        createdByUserId: admin.id,
        priceLines: {
          create: products.map((product, productIndex) => ({
            productId: product.id,
            unitPrice: 10 + productIndex * 2 + index,
            minOrderQty: 100,
            leadTimeDays: 7 + productIndex
          }))
        }
      }
    });
  }

  void categories;
}

main()
  .catch(async (error) => {
    console.error(error);
    process.exit(1);
  })
  .finally(async () => {
    await prisma.$disconnect();
  });
