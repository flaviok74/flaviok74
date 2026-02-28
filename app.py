import os
import re
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from threading import Lock
from typing import Dict, List, Optional

import requests
from flask import Flask, jsonify, render_template, request
from msal import ConfidentialClientApplication


@dataclass
class QuoteRow:
    produto: str
    fornecedor: str
    preco: float
    moeda: str
    quantidade: Optional[float]
    unidade: Optional[str]
    data_email: str
    assunto: str


class OutlookRFQService:
    def __init__(self) -> None:
        self.tenant_id = os.getenv("TENANT_ID", "")
        self.client_id = os.getenv("CLIENT_ID", "")
        self.client_secret = os.getenv("CLIENT_SECRET", "")
        self.user_email = os.getenv("OUTLOOK_USER_EMAIL", "")
        self.folder_name = os.getenv("OUTLOOK_RFQ_FOLDER", "RFQ")
        self.graph_base_url = "https://graph.microsoft.com/v1.0"

    @property
    def is_configured(self) -> bool:
        return all([self.tenant_id, self.client_id, self.client_secret, self.user_email])

    def _get_access_token(self) -> str:
        authority = f"https://login.microsoftonline.com/{self.tenant_id}"
        app = ConfidentialClientApplication(
            client_id=self.client_id,
            authority=authority,
            client_credential=self.client_secret,
        )
        result = app.acquire_token_for_client(scopes=["https://graph.microsoft.com/.default"])
        token = result.get("access_token")
        if not token:
            raise RuntimeError(result.get("error_description", "Falha ao obter token do Graph"))
        return token

    def _headers(self) -> Dict[str, str]:
        return {"Authorization": f"Bearer {self._get_access_token()}", "Accept": "application/json"}

    def _get_folder_id(self, headers: Dict[str, str]) -> Optional[str]:
        url = f"{self.graph_base_url}/users/{self.user_email}/mailFolders"
        response = requests.get(
            url,
            headers=headers,
            params={"$top": "200", "$select": "id,displayName"},
            timeout=20,
        )
        response.raise_for_status()
        for folder in response.json().get("value", []):
            if folder.get("displayName", "").lower() == self.folder_name.lower():
                return folder.get("id")
        return None

    def _extract_quote_rows(self, message: Dict) -> List[QuoteRow]:
        subject = message.get("subject", "Sem assunto")
        from_email = message.get("from", {}).get("emailAddress", {}).get("address", "fornecedor@desconhecido.com")
        sent_date_raw = message.get("receivedDateTime")
        sent_date = datetime.now(timezone.utc)
        if sent_date_raw:
            sent_date = datetime.fromisoformat(sent_date_raw.replace("Z", "+00:00"))

        body = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", message.get("body", {}).get("content", "")))

        pattern = re.compile(
            r"Produto\s*:\s*(?P<produto>[^;]+?)\s*;\s*"
            r"Preço\s*:\s*(?P<preco>[0-9]+(?:[\.,][0-9]+)?)\s*(?P<moeda>[A-Z]{3})\s*;\s*"
            r"Quantidade\s*:\s*(?P<quantidade>[0-9]+(?:[\.,][0-9]+)?)\s*(?P<unidade>[A-Za-z]+)",
            flags=re.IGNORECASE,
        )

        rows: List[QuoteRow] = []
        for match in pattern.finditer(body):
            rows.append(
                QuoteRow(
                    produto=match.group("produto").strip(),
                    fornecedor=from_email,
                    preco=float(match.group("preco").replace(".", "").replace(",", ".")),
                    moeda=match.group("moeda").upper(),
                    quantidade=float(match.group("quantidade").replace(".", "").replace(",", ".")),
                    unidade=match.group("unidade"),
                    data_email=sent_date.strftime("%Y-%m-%d %H:%M"),
                    assunto=subject,
                )
            )

        if rows:
            return rows

        fallback = re.search(r"([0-9]+(?:[\.,][0-9]+)?)\s*(BRL|USD|EUR)", body, re.IGNORECASE)
        if fallback:
            product = re.sub(r"^(RFQ|Cotação)\s*[-:]\s*", "", subject, flags=re.IGNORECASE)
            return [
                QuoteRow(
                    produto=product or "Produto não identificado",
                    fornecedor=from_email,
                    preco=float(fallback.group(1).replace(".", "").replace(",", ".")),
                    moeda=fallback.group(2).upper(),
                    quantidade=None,
                    unidade=None,
                    data_email=sent_date.strftime("%Y-%m-%d %H:%M"),
                    assunto=subject,
                )
            ]
        return []

    def get_outlook_quotes(self) -> Dict:
        if not self.is_configured:
            return {
                "status": "demo",
                "quotes": self._demo_data(),
                "message": "Sem credenciais do Graph. Outlook em modo demo.",
            }

        headers = self._headers()
        folder_id = self._get_folder_id(headers)
        if not folder_id:
            raise RuntimeError(f"Pasta '{self.folder_name}' não encontrada para {self.user_email}")

        response = requests.get(
            f"{self.graph_base_url}/users/{self.user_email}/mailFolders/{folder_id}/messages",
            headers=headers,
            params={
                "$top": "100",
                "$select": "subject,from,receivedDateTime,body",
                "$orderby": "receivedDateTime desc",
            },
            timeout=30,
        )
        response.raise_for_status()

        rows: List[QuoteRow] = []
        for msg in response.json().get("value", []):
            rows.extend(self._extract_quote_rows(msg))

        return {
            "status": "ok",
            "quotes": [asdict(row) for row in rows],
            "message": f"{len(rows)} cotações lidas do Outlook.",
        }

    def _demo_data(self) -> List[Dict]:
        return [
            asdict(
                QuoteRow(
                    produto="Aço Carbono 1020",
                    fornecedor="fornecedorA@exemplo.com",
                    preco=4250.0,
                    moeda="BRL",
                    quantidade=10.0,
                    unidade="ton",
                    data_email="2026-01-21 09:10",
                    assunto="RFQ - Aço Carbono 1020",
                )
            ),
            asdict(
                QuoteRow(
                    produto="Resina PP H503",
                    fornecedor="fornecedorC@exemplo.com",
                    preco=1300.5,
                    moeda="USD",
                    quantidade=5.0,
                    unidade="ton",
                    data_email="2026-01-21 10:05",
                    assunto="RFQ - Resina PP H503",
                )
            ),
        ]


app = Flask(__name__)
service = OutlookRFQService()
manual_quotes: List[Dict] = []
manual_lock = Lock()


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/health")
def health():
    return jsonify({"status": "ok", "time": datetime.now().isoformat()})


@app.route("/api/quotes")
def get_quotes():
    try:
        outlook_payload = service.get_outlook_quotes()
        with manual_lock:
            merged_quotes = outlook_payload["quotes"] + list(manual_quotes)

        return jsonify(
            {
                "status": outlook_payload["status"],
                "last_update": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "quotes": merged_quotes,
                "message": f"{len(merged_quotes)} cotações totais (Outlook + manuais).",
            }
        )
    except Exception as exc:
        return jsonify({"status": "error", "last_update": datetime.now().strftime("%Y-%m-%d %H:%M"), "quotes": [], "message": str(exc)}), 500


@app.route("/api/manual-quotes", methods=["POST"])
def add_manual_quote():
    payload = request.get_json(silent=True) or {}

    try:
        produto = str(payload.get("produto", "")).strip()
        fornecedor = str(payload.get("fornecedor", "manual@local")).strip() or "manual@local"
        moeda = str(payload.get("moeda", "BRL")).upper().strip()
        assunto = str(payload.get("assunto", "Entrada manual")).strip() or "Entrada manual"
        preco = float(payload.get("preco"))

        quantidade_raw = payload.get("quantidade")
        quantidade = float(quantidade_raw) if quantidade_raw not in (None, "") else None
        unidade = str(payload.get("unidade", "")).strip() or None

        if not produto:
            raise ValueError("produto é obrigatório")
        if moeda not in {"BRL", "USD", "EUR"}:
            raise ValueError("moeda deve ser BRL, USD ou EUR")
        if preco < 0:
            raise ValueError("preco deve ser maior ou igual a zero")

    except (TypeError, ValueError) as exc:
        return jsonify({"status": "error", "message": f"Payload inválido: {exc}"}), 400

    quote = asdict(
        QuoteRow(
            produto=produto,
            fornecedor=fornecedor,
            preco=preco,
            moeda=moeda,
            quantidade=quantidade,
            unidade=unidade,
            data_email=datetime.now().strftime("%Y-%m-%d %H:%M"),
            assunto=assunto,
        )
    )

    with manual_lock:
        manual_quotes.append(quote)

    return jsonify({"status": "ok", "message": "Cotação manual adicionada.", "quote": quote}), 201


@app.route("/api/manual-quotes", methods=["DELETE"])
def clear_manual_quotes():
    with manual_lock:
        manual_quotes.clear()
    return jsonify({"status": "ok", "message": "Cotações manuais limpas."})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
