"""Utilities for retrieving pricing e-mails from an Outlook inbox."""

from __future__ import annotations

import email
import imaplib
import logging
from dataclasses import dataclass
from email.message import Message
from typing import Iterable, List, Optional

from .config import EmailConfig

_LOGGER = logging.getLogger(__name__)


@dataclass
class RawEmail:
    """Simple structure representing the parts of an email we care about."""

    uid: str
    subject: str
    sender: str
    body: str
    received_at: str


class OutlookEmailClient:
    """Minimal IMAP client tailored for Outlook inboxes."""

    def __init__(self, config: EmailConfig) -> None:
        self._config = config
        self._connection: Optional[imaplib.IMAP4_SSL] = None

    def connect(self) -> None:
        """Establish a secure IMAP connection to Outlook."""

        if self._connection is not None:
            return

        _LOGGER.info("Connecting to Outlook mailbox %s", self._config.address)
        self._connection = imaplib.IMAP4_SSL(self._config.host)
        self._connection.login(self._config.address, self._config.password)
        self._connection.select(self._config.mailbox)

    def disconnect(self) -> None:
        """Close the IMAP connection if it is open."""

        if self._connection is None:
            return

        try:
            self._connection.close()
        finally:
            self._connection.logout()
            self._connection = None

    def fetch_emails(self, search_criteria: str = "ALL", limit: Optional[int] = None) -> List[RawEmail]:
        """Retrieve e-mails that match the provided IMAP search criteria."""

        self.connect()
        assert self._connection is not None  # For type-checkers

        _LOGGER.debug("Searching Outlook mailbox using criteria: %s", search_criteria)
        status, data = self._connection.uid("search", None, search_criteria)
        if status != "OK":
            raise RuntimeError(f"Failed to search mailbox: {status}")

        uids = data[0].split()
        if limit is not None:
            uids = uids[-limit:]

        emails: List[RawEmail] = []
        for uid in uids:
            status, msg_data = self._connection.uid("fetch", uid, b"(RFC822)")
            if status != "OK":
                _LOGGER.warning("Failed to fetch message %s: %s", uid.decode(), status)
                continue

            raw_message = email.message_from_bytes(msg_data[0][1])
            emails.append(self._convert(uid.decode(), raw_message))
        return emails

    def _convert(self, uid: str, message: Message) -> RawEmail:
        """Convert an :class:`email.message.Message` into :class:`RawEmail`."""

        subject = message.get("Subject", "(sem assunto)")
        sender = message.get("From", "")
        received_at = message.get("Date", "")

        body_parts: Iterable[str] = []
        if message.is_multipart():
            parts: List[str] = []
            for part in message.walk():
                content_type = part.get_content_type()
                if content_type == "text/plain":
                    charset = part.get_content_charset() or "utf-8"
                    try:
                        parts.append(part.get_payload(decode=True).decode(charset, errors="replace"))
                    except Exception:  # pragma: no cover - defensive
                        _LOGGER.exception("Failed to decode email part for UID %s", uid)
                        continue
            body_parts = parts
        else:
            charset = message.get_content_charset() or "utf-8"
            payload = message.get_payload(decode=True) or b""
            body_parts = [payload.decode(charset, errors="replace")]

        body = "\n".join(body_parts).strip()
        return RawEmail(uid=uid, subject=subject, sender=sender, body=body, received_at=received_at)


__all__ = ["OutlookEmailClient", "RawEmail"]
