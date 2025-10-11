"""Application configuration utilities for the price management system."""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass
class EmailConfig:
    """Configuration required to connect to an Outlook inbox."""

    address: str
    password: str
    host: str = "outlook.office365.com"
    mailbox: str = "INBOX"

    @classmethod
    def from_env(
        cls,
        address_var: str = "PRICE_MANAGER_EMAIL",
        password_var: str = "PRICE_MANAGER_PASSWORD",
        host_var: str | None = None,
        mailbox_var: str | None = None,
    ) -> "EmailConfig":
        """Build a configuration instance using environment variables.

        Parameters
        ----------
        address_var:
            Name of the environment variable that stores the Outlook address.
        password_var:
            Name of the environment variable that stores the account password
            or app-specific token.
        host_var:
            Optional environment variable name for a custom IMAP host.
        mailbox_var:
            Optional environment variable name for a custom mailbox folder.

        Returns
        -------
        EmailConfig
            A populated configuration object.

        Raises
        ------
        EnvironmentError
            If one of the required values is missing.
        """

        address = os.getenv(address_var)
        password = os.getenv(password_var)
        if not address or not password:
            missing = [
                name
                for name, value in ((address_var, address), (password_var, password))
                if not value
            ]
            raise EnvironmentError(
                "Missing required email credentials in environment: "
                + ", ".join(missing)
            )

        host = os.getenv(host_var) if host_var else None
        mailbox = os.getenv(mailbox_var) if mailbox_var else None
        return cls(
            address=address,
            password=password,
            host=host or "outlook.office365.com",
            mailbox=mailbox or "INBOX",
        )


__all__ = ["EmailConfig"]
