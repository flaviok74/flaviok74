"""Command line interface for the price management toolkit."""

from __future__ import annotations

import argparse
import json
import logging
from datetime import datetime
from decimal import Decimal
from typing import Any

from .config import EmailConfig
from .manager import PriceManager

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Sistema de gestão de coleta e análise de preços")
    parser.add_argument("database", help="Caminho para o arquivo SQLite que armazenará os preços")

    subparsers = parser.add_subparsers(dest="command", required=True)

    ingest_parser = subparsers.add_parser("ingest", help="Coleta automaticamente novos preços do Outlook")
    ingest_parser.add_argument(
        "--search",
        default="ALL",
        help="Critério IMAP para busca (ex: 'SUBJECT \"cotação\"')",
    )
    ingest_parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Limita a quantidade de e-mails processados",
    )

    analyze_parser = subparsers.add_parser("analyze", help="Gera relatório agregado de preços")
    analyze_parser.add_argument(
        "--format",
        choices=["json", "table"],
        default="table",
        help="Formato da saída de análise",
    )

    list_parser = subparsers.add_parser("list", help="Lista todos os registros armazenados")
    list_parser.add_argument("--limit", type=int, default=20, help="Quantidade máxima de registros exibidos")

    return parser


def command_ingest(args: argparse.Namespace) -> None:
    config = EmailConfig.from_env()
    manager = PriceManager(args.database)
    ingested = manager.ingest_from_email(
        config,
        search_criteria=args.search,
        limit=args.limit,
    )
    logging.info("%s novos preços armazenados", ingested)


def command_analyze(args: argparse.Namespace) -> None:
    manager = PriceManager(args.database)
    summaries = manager.analyze()
    if args.format == "json":
        data = [summary.__dict__ for summary in summaries]
        print(json.dumps(data, default=_json_serializer, indent=2, ensure_ascii=False))
        return

    _print_table(summaries)


def command_list(args: argparse.Namespace) -> None:
    manager = PriceManager(args.database)
    records = manager.list_records()[: args.limit]
    for record in records:
        logging.info(
            "%s | %s | %s %s | %s",
            record.received_at.isoformat(timespec="seconds"),
            record.product,
            record.currency,
            record.price,
            record.vendor,
        )


def _print_table(summaries) -> None:
    if not summaries:
        print("Nenhum registro disponível.")
        return

    headers = [
        "Produto",
        "Média",
        "Mínimo",
        "Máximo",
        "Último",
        "Fornecedor",
        "Variação",
        "%",
        "Observações",
        "Atualizado em",
    ]
    rows = []
    for summary in summaries:
        rows.append(
            [
                summary.product,
                f"{summary.average_price:.2f}",
                f"{summary.lowest_price:.2f}",
                f"{summary.highest_price:.2f}",
                f"{summary.last_price:.2f}",
                summary.last_vendor,
                f"{summary.price_change:+.2f}" if summary.price_change is not None else "-",
                f"{summary.price_change_percent:+.2f}" if summary.price_change_percent is not None else "-",
                summary.observations,
                summary.last_seen.isoformat(timespec="seconds"),
            ]
        )

    widths = [max(len(str(value)) for value in column) for column in zip(headers, *rows)]
    _print_row(headers, widths)
    print("-+-".join("-" * width for width in widths))
    for row in rows:
        _print_row(row, widths)


def _print_row(values, widths):
    print(" | ".join(str(value).ljust(width) for value, width in zip(values, widths)))


def _json_serializer(value: Any):
    if isinstance(value, (datetime, Decimal)):
        return value.isoformat() if isinstance(value, datetime) else float(value)
    return value


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    command = args.command.replace("-", "_")
    handler = globals().get(f"command_{command}")
    if handler is None:
        raise SystemExit(f"Comando desconhecido: {args.command}")
    handler(args)


if __name__ == "__main__":
    main()
