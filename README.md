# Ekoquim Freight Quotes

Aplicativo web para coleta e gestão de cotações de frete marítimo, com multi-tenant, auditoria completa e dashboards.

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
- 3 usuários (admin, operador, auditor)
- 3 fornecedores
- 10 portos
- 3 tipos de container
- 10 cotações com linhas de custo

## API (exemplos)
### Criar cotação
`POST /api/quotes`
```json
{
  "supplierId": "uuid",
  "originPortId": "uuid",
  "destinationPortId": "uuid",
  "currency": "USD",
  "validityEnd": "2024-12-31",
  "sourceType": "MANUAL",
  "status": "APPROVED",
  "createdByUserId": "uuid",
  "carrier": "Maersk",
  "service": "Direct",
  "incoterm": "FOB",
  "costLines": [
    { "group": "ORIGIN", "chargeName": "THC", "amount20gp": 120 },
    { "group": "OCEAN", "chargeName": "Freight", "amount20gp": 800 }
  ]
}
```

### Adicionar linha de custo
`POST /api/quotes`
```json
{
  "supplierId": "uuid",
  "originPortId": "uuid",
  "destinationPortId": "uuid",
  "currency": "USD",
  "validityEnd": "2024-12-31",
  "sourceType": "MANUAL",
  "status": "APPROVED",
  "createdByUserId": "uuid",
  "costLines": [
    { "group": "DESTINATION", "chargeName": "Documentation", "amount40hc": 90 }
  ]
}
```

### Aprovar importação
`POST /api/quotes`
```json
{
  "supplierId": "uuid",
  "originPortId": "uuid",
  "destinationPortId": "uuid",
  "currency": "USD",
  "validityEnd": "2024-12-31",
  "sourceType": "WEB_LINK",
  "status": "APPROVED",
  "createdByUserId": "uuid",
  "sourceUrl": "https://example.com/quote.pdf"
}
```

## Auditoria
Toda criação/edição/exclusão deve gerar registros em `AuditLog` com o JSON antes/depois. Isso pode ser integrado usando middlewares do Prisma ou uma camada de serviços.

## Observações
- Todas as tabelas carregam `organizationId` para isolamento multi-tenant.
- O parsing automático de links está preparado via `sourceType`, `sourceUrl` e `status`.
- Exporte logs em CSV via endpoint de auditoria ou camada de serviço.
