"""Price analysis utilities."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from statistics import mean
from typing import Dict, Iterable, List, Optional

from .parsing import PriceRecord


@dataclass
class PriceSummary:
    product: str
    average_price: Decimal
    lowest_price: Decimal
    highest_price: Decimal
    last_price: Decimal
    last_vendor: str
    last_seen: datetime
    price_change: Optional[Decimal]
    price_change_percent: Optional[Decimal]
    observations: int


class PriceAnalyzer:
    """Generate aggregated statistics from stored price records."""

    def __init__(self, records: Iterable[PriceRecord]):
        self.records = list(records)

    def summarize(self) -> List[PriceSummary]:
        grouped: Dict[str, List[PriceRecord]] = defaultdict(list)
        for record in sorted(self.records, key=lambda r: r.received_at):
            grouped[record.product].append(record)

        summaries: List[PriceSummary] = []
        for product, records in grouped.items():
            prices = [record.price for record in records]
            average_price = Decimal(str(mean(float(price) for price in prices))).quantize(Decimal("0.01"))
            lowest_price = min(prices)
            highest_price = max(prices)
            last_record = records[-1]
            previous_price = records[-2].price if len(records) > 1 else None
            change = None
            change_percent = None
            if previous_price is not None:
                change = last_record.price - previous_price
                if previous_price != 0:
                    change_percent = (change / previous_price * Decimal("100")).quantize(Decimal("0.01"))
            summaries.append(
                PriceSummary(
                    product=product,
                    average_price=average_price,
                    lowest_price=lowest_price,
                    highest_price=highest_price,
                    last_price=last_record.price,
                    last_vendor=last_record.vendor,
                    last_seen=last_record.received_at,
                    price_change=change,
                    price_change_percent=change_percent,
                    observations=len(records),
                )
            )
        return summaries


__all__ = ["PriceAnalyzer", "PriceSummary"]
