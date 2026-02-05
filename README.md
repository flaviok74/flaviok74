# Ekoquim Product Pricing

Aplicativo web para receber, comparar e analisar preços de vários produtos, com multi-tenant, auditoria completa e dashboards.

## Stack
- Next.js (App Router) + TypeScript
- PostgreSQL + Prisma
- NextAuth (Credentials + RBAC)
- Tailwind CSS

## Setup local
```bash
npm install
```

1. Crie o banco PostgreSQL e configure o `.env`:
```
DATABASE_URL="postgresql://user:password@localhost:5432/ekoquim"
NEXTAUTH_SECRET="dev-secret"
```

2. Rode migrações e seed:
```bash
npm run prisma:generate
npm run prisma:migrate
npm run prisma:seed
```

3. Suba o app:
```bash
npm run dev
```

## Seed inicial
- 1 organização
- 3 usuários (admin, analista, leitura)
- 3 fornecedores
- 3 categorias
- 4 produtos
- 10 cotações com linhas de preço

## API (exemplos)
### Criar cotação de preço
`POST /api/prices`
```json
{
  "vendorId": "uuid",
  "currency": "USD",
  "validTo": "2024-12-31",
  "sourceType": "MANUAL",
  "status": "APPROVED",
  "createdByUserId": "uuid",
  "notes": "Negociação mensal",
  "priceLines": [
    { "productId": "uuid", "unitPrice": 12.5, "minOrderQty": 100 }
  ]
}
```

### Adicionar linha de preço
`POST /api/prices`
```json
{
  "vendorId": "uuid",
  "currency": "USD",
  "validTo": "2024-12-31",
  "sourceType": "MANUAL",
  "status": "APPROVED",
  "createdByUserId": "uuid",
  "priceLines": [
    { "productId": "uuid", "unitPrice": 18.9, "leadTimeDays": 10 }
  ]
}
```

### Aprovar importação
`POST /api/prices`
```json
{
  "vendorId": "uuid",
  "currency": "USD",
  "validTo": "2024-12-31",
  "sourceType": "WEB_LINK",
  "status": "APPROVED",
  "createdByUserId": "uuid",
  "sourceUrl": "https://example.com/precos.pdf"
}
```

## Auditoria
Toda criação/edição/exclusão deve gerar registros em `AuditLog` com o JSON antes/depois. Isso pode ser integrado usando middlewares do Prisma ou uma camada de serviços.

## Observações
- Todas as tabelas carregam `organizationId` para isolamento multi-tenant.
- O parsing automático de links está preparado via `sourceType`, `sourceUrl` e `status`.
- Exporte logs em CSV via endpoint de auditoria ou camada de serviço.
