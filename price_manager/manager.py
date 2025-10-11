"""High level orchestration utilities for the price management workflow."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import List

from .analysis import PriceAnalyzer, PriceSummary
from .config import EmailConfig
from .email_client import OutlookEmailClient
from .parsing import PriceRecord, parse_email
from .storage import fetch_all, initialize, store_records

_LOGGER = logging.getLogger(__name__)


class PriceManager:
    """Coordinate the ingestion and analysis pipeline."""

    def __init__(self, db_path: str | Path) -> None:
        self.db_path = Path(db_path)
        initialize(self.db_path)

    def ingest_from_email(
        self,
        email_config: EmailConfig,
        search_criteria: str = "ALL",
        limit: int | None = None,
    ) -> int:
        client = OutlookEmailClient(email_config)
        ingested = 0
        try:
            emails = client.fetch_emails(search_criteria=search_criteria, limit=limit)
            for raw_email in emails:
                records = parse_email(raw_email)
                if not records:
                    _LOGGER.info("Nenhum preço identificado no e-mail %s", raw_email.uid)
                    continue
                ingested += store_records(self.db_path, records)
        finally:
            client.disconnect()
        return ingested

    def list_records(self) -> List[PriceRecord]:
        return fetch_all(self.db_path)

    def analyze(self) -> List[PriceSummary]:
        records = self.list_records()
        analyzer = PriceAnalyzer(records)
        return analyzer.summarize()


__all__ = ["PriceManager"]
