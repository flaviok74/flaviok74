from datetime import datetime
from decimal import Decimal

from price_manager.analysis import PriceAnalyzer
from price_manager.parsing import PriceRecord


def test_price_analyzer_summary():
    records = [
        PriceRecord(
            product="Item",
            price=Decimal("10"),
            currency="BRL",
            vendor="Fornecedor A",
            source_uid="1",
            received_at=datetime(2024, 1, 1, 8, 0, 0),
        ),
        PriceRecord(
            product="Item",
            price=Decimal("12"),
            currency="BRL",
            vendor="Fornecedor B",
            source_uid="2",
            received_at=datetime(2024, 1, 2, 8, 0, 0),
        ),
    ]

    analyzer = PriceAnalyzer(records)
    summaries = analyzer.summarize()
    assert len(summaries) == 1
    summary = summaries[0]
    assert summary.average_price == Decimal("11.00")
    assert summary.lowest_price == Decimal("10")
    assert summary.highest_price == Decimal("12")
    assert summary.last_vendor == "Fornecedor B"
    assert summary.price_change == Decimal("2")
