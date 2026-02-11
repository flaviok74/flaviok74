# OceanQuote SaaS (pronto para testar)

Sistema SaaS para cotação de fretes marítimos internacionais que recebe e analisa preços de vários produtos por embarque.

## Funcionalidades

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
- Endpoint JSON de análise: `/api/quotes/<id>/analysis`.

## Como testar agora

```bash
python app.py
```

Acesse no navegador:

- `http://localhost:5000`
- healthcheck: `http://localhost:5000/health`

### Fluxo sugerido de teste

1. Crie conta em **Criar conta**.
2. Faça login.
3. Cadastre 2 ou 3 produtos em **Produtos**.
4. Em **Cotações**, preencha os dados e informe quantidades para cada produto.
5. Abra **Detalhes** para ver a análise final.

## Stack

- Python padrão (`http.server`, `sqlite3`)
- HTML/CSS
