# OceanQuote SaaS

Sistema SaaS para cotação de fretes marítimos internacionais com análise de preços de múltiplos produtos por embarque.

## Funcionalidades

- Cadastro e autenticação de empresa (tenant).
- Cadastro de produtos com HS Code, peso, volume e preço unitário.
- Criação de cotações de frete marítimo com rota, incoterm, container, frete base, taxas e seguro.
- Associação de quantidades de vários produtos em cada cotação.
- Motor de análise com:
  - custo logístico total,
  - custo landed total,
  - custo por kg e por m³,
  - score de risco operacional,
  - recomendação comercial.
- API JSON para consulta da análise (`/api/quotes/<id>/analysis`).

## Como executar

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Acesse em `http://localhost:5000`.

## Stack

- Flask
- SQLite
- Bootstrap 5
