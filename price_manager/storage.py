"""Persistence utilities backed by SQLite."""

from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from typing import Iterable, Iterator, List

from .parsing import PriceRecord

SCHEMA = """
CREATE TABLE IF NOT EXISTS price_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product TEXT NOT NULL,
    price NUMERIC NOT NULL,
    currency TEXT NOT NULL,
    vendor TEXT NOT NULL,
    source_uid TEXT NOT NULL,
    received_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_price_records_product ON price_records(product);
CREATE INDEX IF NOT EXISTS idx_price_records_vendor ON price_records(vendor);
"""


@contextmanager
def connect(db_path: str | Path) -> Iterator[sqlite3.Connection]:
    connection = sqlite3.connect(str(db_path))
    try:
        yield connection
    finally:
        connection.commit()
        connection.close()


def initialize(db_path: str | Path) -> None:
    with connect(db_path) as connection:
        connection.executescript(SCHEMA)


def store_records(db_path: str | Path, records: Iterable[PriceRecord]) -> int:
    rows = [
        (
            record.product,
            float(record.price),
            record.currency,
            record.vendor,
            record.source_uid,
            record.received_at.isoformat(),
        )
        for record in records
    ]
    if not rows:
        return 0

    with connect(db_path) as connection:
        connection.executemany(
            """
            INSERT INTO price_records
                (product, price, currency, vendor, source_uid, received_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            rows,
        )
    return len(rows)


def fetch_all(db_path: str | Path) -> List[PriceRecord]:
    with connect(db_path) as connection:
        cursor = connection.execute(
            """
            SELECT product, price, currency, vendor, source_uid, received_at
            FROM price_records
            ORDER BY received_at DESC
            """
        )
        return [
            PriceRecord(
                product=row[0],
                price=Decimal(str(row[1])),
                currency=row[2],
                vendor=row[3],
                source_uid=row[4],
                received_at=datetime.fromisoformat(row[5]),
            )
            for row in cursor.fetchall()
        ]


__all__ = ["initialize", "store_records", "fetch_all", "connect"]
