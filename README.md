# RFQ Price Analyzer (Outlook + Entrada Manual)

Webapp em HTML/CSS dinâmico para receber e analisar preços de vários produtos.

## O que o sistema faz

- Lê e-mails da pasta **RFQ** do Outlook via Microsoft Graph.
- Permite **adicionar cotações manualmente** (para testar sem depender do Outlook).
- Exibe tabela dinâmica com filtros por produto, fornecedor, moeda e preço máximo.
- Mostra resumo de total, fornecedores únicos, menor preço e preço médio.
- Atualiza os dados automaticamente a cada **2 horas**.

## Como testar agora (sem Outlook)

1. Instale dependências:

```bash
pip install -r requirements.txt
```

2. Rode o app (sem `.env` mesmo):

```bash
python app.py
```

3. Acesse:

`http://localhost:8000`

4. Use a área **"Teste rápido: adicionar cotação manual"** para cadastrar preços e validar filtros/tabela.

## Configuração Outlook (opcional)

Copie e preencha:

```bash
cp .env.example .env
```

Variáveis:

- `TENANT_ID`
- `CLIENT_ID`
- `CLIENT_SECRET`
- `OUTLOOK_USER_EMAIL`
- `OUTLOOK_RFQ_FOLDER` (default: `RFQ`)

Com as credenciais, o sistema busca cotações reais da pasta RFQ e combina com as cotações manuais.

## APIs úteis

- `GET /health` → healthcheck
- `GET /api/quotes` → lista cotações (Outlook + manuais)
- `POST /api/manual-quotes` → adiciona cotação manual
- `DELETE /api/manual-quotes` → limpa cotações manuais

### Exemplo `POST /api/manual-quotes`

```json
{
  "produto": "Parafuso M10",
  "fornecedor": "fornecedor@empresa.com",
  "preco": 1.75,
  "moeda": "BRL",
  "quantidade": 1000,
  "unidade": "un",
  "assunto": "Cotação manual"
}
```
