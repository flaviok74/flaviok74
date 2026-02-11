# OceanQuote SaaS (sem dependências externas)

Sistema SaaS para cotação de fretes marítimos internacionais que recebe e analisa preços de vários produtos por embarque.

## O que o sistema faz

- Cadastro e login de empresas (multi-tenant).
- Cadastro de produtos com categoria, HS code, peso, volume e preço unitário.
- Criação de cotações marítimas com rota, incoterm, tipo de container e custos.
- Associação de múltiplos produtos por cotação com quantidades.
- Análise automática por cotação:
  - valor da carga,
  - custo logístico,
  - landed cost,
  - custo por kg e por m³,
  - score de risco,
  - recomendação.

## Como executar

```bash
python app.py
```

Abra no navegador: `http://localhost:5000`

## Stack

- Python padrão (`http.server`, `sqlite3`)
- HTML/CSS
