"""Parsing helpers that transform e-mail bodies into structured price records."""

from __future__ import annotations

import csv
import email.utils
import io
import re
import unicodedata
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal, InvalidOperation
from typing import List

from .email_client import RawEmail

PRODUCT_LINE_RE = re.compile(
    r"^(?P<product>[^;:,]+)\s*[;:,]\s*(?P<price>[-+]?[0-9]+(?:[\.,][0-9]+)?)"  # price
    r"(?:\s*[;:,]\s*(?P<currency>[A-Z]{3}|R\$|US\$|€|£))?"  # currency (optional)
    r"(?:\s*[;:,]\s*(?P<vendor>.+))?$",  # vendor (optional)
    re.IGNORECASE,
)

FIELD_VALUE_RE = re.compile(r"^(?P<field>\w+)[\s:=]+(?P<value>.+)$")


@dataclass
class PriceRecord:
    """Structured representation of a price quotation."""

    product: str
    price: Decimal
    currency: str
    vendor: str
    source_uid: str
    received_at: datetime


def parse_email(raw_email: RawEmail) -> List[PriceRecord]:
    """Parse a raw e-mail into price records.

    The parser accepts the following layouts:

    * CSV content with headers containing at least ``product`` and ``price``.
    * Text lines using separators (comma, semicolon or colon) in the pattern
      ``produto; preço; moeda; fornecedor``.
    * ``Chave: valor`` style blocks, repeated per product.
    """

    parsers = (parse_as_csv, parse_as_product_lines, parse_as_key_blocks)
    for parser in parsers:
        records = parser(raw_email)
        if records:
            return records
    return []


def parse_as_csv(raw_email: RawEmail) -> List[PriceRecord]:
    """Attempt to parse the body of the e-mail as CSV."""

    body = raw_email.body.strip()
    if not body:
        return []

    try:
        sample = body.splitlines()[0]
    except IndexError:
        return []

    if "," not in sample and ";" not in sample:
        return []

    delimiter = ";" if sample.count(";") >= sample.count(",") else ","
    reader = csv.DictReader(io.StringIO(body), delimiter=delimiter)
    normalized = [_normalize_field_names(field) for field in reader.fieldnames or []]

    def lookup(row: dict[str, str], name: str) -> str:
        for key, normalized_key in zip(reader.fieldnames or [], normalized):
            if normalized_key == name:
                return row.get(key, "")
        return ""

    records: List[PriceRecord] = []
    for row in reader:
        product = lookup(row, "product") or lookup(row, "produto")
        price = lookup(row, "price") or lookup(row, "preco")
        if not product or not price:
            continue
        currency = lookup(row, "currency") or lookup(row, "moeda") or "BRL"
        vendor = lookup(row, "vendor") or lookup(row, "fornecedor") or raw_email.sender
        parsed_price = _to_decimal(price)
        if parsed_price is None:
            continue
        records.append(
            PriceRecord(
                product=product.strip(),
                price=parsed_price,
                currency=_normalize_currency(currency),
                vendor=vendor.strip(),
                source_uid=raw_email.uid,
                received_at=_parse_date(raw_email.received_at),
            )
        )
    return records


def parse_as_product_lines(raw_email: RawEmail) -> List[PriceRecord]:
    """Parse free-form text where each line contains price information."""

    records: List[PriceRecord] = []
    for line in raw_email.body.splitlines():
        line = line.strip()
        if not line:
            continue
        match = PRODUCT_LINE_RE.match(line)
        if not match:
            continue
        normalized_name = _normalize_field_names(match.group("product"))
        if normalized_name in {"produto", "preco", "price", "moeda", "currency", "fornecedor", "vendor"}:
            continue
        price = _to_decimal(match.group("price") or "")
        if price is None:
            continue
        currency = match.group("currency") or "BRL"
        vendor = match.group("vendor") or raw_email.sender
        records.append(
            PriceRecord(
                product=match.group("product").strip(),
                price=price,
                currency=_normalize_currency(currency),
                vendor=vendor.strip(),
                source_uid=raw_email.uid,
                received_at=_parse_date(raw_email.received_at),
            )
        )
    return records


def parse_as_key_blocks(raw_email: RawEmail) -> List[PriceRecord]:
    """Parse bodies containing ``chave: valor`` pairs for each product."""

    product = ""
    price_text = ""
    currency = "BRL"
    vendor = raw_email.sender
    records: List[PriceRecord] = []

    for line in raw_email.body.splitlines():
        line = line.strip()
        if not line:
            continue
        match = FIELD_VALUE_RE.match(line)
        if not match:
            continue
        field = _normalize_field_names(match.group("field"))
        value = match.group("value").strip()

        if field in {"product", "produto"}:
            if product and price_text:
                record = _record_from_parts(product, price_text, currency, vendor, raw_email)
                if record:
                    records.append(record)
            product = value
            price_text = ""
            currency = "BRL"
            vendor = raw_email.sender
        elif field in {"price", "preco"}:
            price_text = value
        elif field in {"currency", "moeda"}:
            currency = value
        elif field in {"vendor", "fornecedor"}:
            vendor = value

    if product and price_text:
        record = _record_from_parts(product, price_text, currency, vendor, raw_email)
        if record:
            records.append(record)

    return records


def _record_from_parts(
    product: str,
    price_text: str,
    currency: str,
    vendor: str,
    raw_email: RawEmail,
) -> PriceRecord | None:
    price = _to_decimal(price_text)
    if price is None:
        return None
    return PriceRecord(
        product=product.strip(),
        price=price,
        currency=_normalize_currency(currency or "BRL"),
        vendor=vendor.strip() or raw_email.sender,
        source_uid=raw_email.uid,
        received_at=_parse_date(raw_email.received_at),
    )


def _normalize_field_names(field: str) -> str:
    normalized = unicodedata.normalize("NFD", field.strip().lower())
    without_accents = "".join(char for char in normalized if unicodedata.category(char) != "Mn")
    return without_accents


def _normalize_currency(currency: str) -> str:
    currency = currency.strip().upper()
    return {
        "R$": "BRL",
        "US$": "USD",
        "€": "EUR",
        "£": "GBP",
    }.get(currency, currency)


def _to_decimal(value: str) -> Decimal | None:
    cleaned = value.replace("R$", "").replace("US$", "").replace(" ", "").strip()
    cleaned = cleaned.replace(".", "").replace(",", ".") if cleaned.count(",") == 1 else cleaned
    try:
        return Decimal(cleaned)
    except (InvalidOperation, ValueError):
        return None


def _parse_date(value: str) -> datetime:
    try:
        return email.utils.parsedate_to_datetime(value)  # type: ignore[attr-defined]
    except Exception:
        return datetime.utcnow()


__all__ = ["PriceRecord", "parse_email"]
