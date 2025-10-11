from datetime import datetime

from price_manager.email_client import RawEmail
from price_manager.parsing import parse_email


def build_email(body: str) -> RawEmail:
    return RawEmail(
        uid="1",
        subject="cotacao",
        sender="fornecedor@example.com",
        body=body,
        received_at=datetime.utcnow().isoformat(),
    )


def test_parse_csv_email():
    email = build_email("produto,preco,moeda\nProduto A,12,BRL\nProduto B,15,USD")
    records = parse_email(email)
    assert len(records) == 2
    assert records[0].product == "Produto A"
    assert str(records[0].price) == "12"
    assert records[1].currency == "USD"


def test_parse_product_lines():
    email = build_email("Produto A; 12,50; R$; Fornecedor 1\nOutro Produto: 20 : USD : Vendor")
    records = parse_email(email)
    assert len(records) == 2
    assert records[0].currency == "BRL"
    assert records[1].vendor == "Vendor"


def test_parse_key_blocks():
    email = build_email(
        "Produto: Item X\nPreço: 10,00\nMoeda: BRL\nFornecedor: Teste\n\nProduto: Item Y\nPreço: 5"
    )
    records = parse_email(email)
    assert len(records) == 2
    assert records[1].product == "Item Y"
