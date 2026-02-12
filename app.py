from __future__ import annotations

import hashlib
import html
import json
import os
import secrets
import sqlite3
from http import cookies
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from statistics import mean
from urllib.parse import parse_qs, urlparse

DB_PATH = os.path.join(os.path.dirname(__file__), "freight_saas.db")
SESSIONS: dict[str, int] = {}


def db_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def init_db() -> None:
    with db_conn() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS tenants (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tenant_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                hs_code TEXT NOT NULL,
                unit_cost REAL NOT NULL,
                weight_kg REAL NOT NULL,
                volume_m3 REAL NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (tenant_id) REFERENCES tenants(id)
            );

            CREATE TABLE IF NOT EXISTS quotes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tenant_id INTEGER NOT NULL,
                reference TEXT NOT NULL,
                origin_port TEXT NOT NULL,
                destination_port TEXT NOT NULL,
                incoterm TEXT NOT NULL,
                currency TEXT NOT NULL,
                container_type TEXT NOT NULL,
                lead_time_days INTEGER NOT NULL,
                base_freight REAL NOT NULL,
                surcharges REAL NOT NULL,
                insurance_rate REAL NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (tenant_id) REFERENCES tenants(id)
            );

            CREATE TABLE IF NOT EXISTS quote_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                quote_id INTEGER NOT NULL,
                product_id INTEGER NOT NULL,
                quantity INTEGER NOT NULL,
                FOREIGN KEY (quote_id) REFERENCES quotes(id),
                FOREIGN KEY (product_id) REFERENCES products(id)
            );
            """
        )


def layout(title: str, body: str, tenant_id: int | None = None, message: str = "") -> str:
    nav = "<a href='/'>Início</a>"
    if tenant_id:
        nav += " | <a href='/dashboard'>Dashboard</a> | <a href='/products'>Produtos</a> | <a href='/quotes'>Cotações</a> | <a href='/logout'>Sair</a>"
    else:
        nav += " | <a href='/login'>Entrar</a> | <a href='/register'>Criar conta</a>"

    alert = f"<div class='alert'>{html.escape(message)}</div>" if message else ""

    return f"""<!doctype html>
<html lang='pt-BR'>
<head>
  <meta charset='utf-8'/>
  <meta name='viewport' content='width=device-width, initial-scale=1'/>
  <title>{html.escape(title)}</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 0; background: #f5f8fb; color:#0f2942; }}
    .nav {{ background:#0f2942; color:#fff; padding:12px 18px; }}
    .nav a {{ color:#fff; text-decoration:none; margin-right: 8px; }}
    .container {{ max-width: 1100px; margin: 20px auto; padding: 0 16px; }}
    .card {{ background:#fff; border-radius:8px; padding:14px; box-shadow:0 4px 16px rgba(0,0,0,.08); margin-bottom:16px; }}
    .alert {{ background:#ecfeff; border:1px solid #99f6e4; border-radius:8px; padding:10px; margin-bottom:10px; }}
    input, select {{ width:100%; padding:8px; margin: 5px 0; border:1px solid #d1d5db; border-radius:6px; }}
    button {{ background:#2563eb; color:white; border:0; padding:10px 14px; border-radius:6px; cursor:pointer; }}
    table {{ width:100%; border-collapse: collapse; background:#fff; }}
    th, td {{ border:1px solid #e5e7eb; padding:8px; text-align:left; }}
    .grid {{ display:grid; grid-template-columns: repeat(auto-fit,minmax(220px,1fr)); gap:12px; }}
    .muted {{ color:#475569; font-size: 14px; }}
  </style>
</head>
<body>
  <div class='nav'>{nav}</div>
  <div class='container'>{alert}{body}</div>
</body></html>"""


def get_tenant_id(handler: BaseHTTPRequestHandler) -> int | None:
    raw = handler.headers.get("Cookie", "")
    c = cookies.SimpleCookie()
    c.load(raw)
    token = c.get("session")
    if not token:
        return None
    return SESSIONS.get(token.value)


def create_session(tenant_id: int) -> str:
    token = secrets.token_hex(24)
    SESSIONS[token] = tenant_id
    return f"session={token}; HttpOnly; Path=/"


def clear_session(handler: BaseHTTPRequestHandler) -> str:
    raw = handler.headers.get("Cookie", "")
    c = cookies.SimpleCookie()
    c.load(raw)
    t = c.get("session")
    if t and t.value in SESSIONS:
        del SESSIONS[t.value]
    return "session=deleted; Path=/; Max-Age=0"


def parse_form(handler: BaseHTTPRequestHandler) -> dict[str, str]:
    length = int(handler.headers.get("Content-Length", "0"))
    body = handler.rfile.read(length).decode("utf-8")
    data = parse_qs(body)
    return {k: v[0] if v else "" for k, v in data.items()}


def analysis(conn: sqlite3.Connection, quote_id: int) -> dict[str, float | str]:
    quote = conn.execute("SELECT * FROM quotes WHERE id=?", (quote_id,)).fetchone()
    items = conn.execute(
        """
        SELECT qi.quantity, p.* FROM quote_items qi
        JOIN products p ON p.id = qi.product_id
        WHERE qi.quote_id=?
        """,
        (quote_id,),
    ).fetchall()

    total_weight = sum(i["quantity"] * i["weight_kg"] for i in items)
    total_volume = sum(i["quantity"] * i["volume_m3"] for i in items)
    total_cargo_value = sum(i["quantity"] * i["unit_cost"] for i in items)
    insurance_cost = total_cargo_value * (quote["insurance_rate"] / 100)
    total_logistics_cost = quote["base_freight"] + quote["surcharges"] + insurance_cost
    total_landed_cost = total_cargo_value + total_logistics_cost
    cost_per_kg = total_logistics_cost / total_weight if total_weight else 0
    cost_per_m3 = total_logistics_cost / total_volume if total_volume else 0

    risk_score = 35
    if quote["lead_time_days"] > 35:
        risk_score += 20
    if quote["destination_port"].lower() in {"lagos", "durban", "mumbai", "santos"}:
        risk_score += 10
    if total_volume > 50:
        risk_score += 15
    risk_score = min(risk_score, 100)

    recommendation = "Competitivo"
    if cost_per_kg > 2.8 or risk_score > 70:
        recommendation = "Revisar parceiro logístico"
    elif cost_per_kg > 1.6:
        recommendation = "Negociar bunker e THC"

    return {
        "total_weight": round(total_weight, 2),
        "total_volume": round(total_volume, 2),
        "total_cargo_value": round(total_cargo_value, 2),
        "insurance_cost": round(insurance_cost, 2),
        "total_logistics_cost": round(total_logistics_cost, 2),
        "total_landed_cost": round(total_landed_cost, 2),
        "cost_per_kg": round(cost_per_kg, 2),
        "cost_per_m3": round(cost_per_m3, 2),
        "risk_score": risk_score,
        "recommendation": recommendation,
    }


class App(BaseHTTPRequestHandler):
    def render(self, title: str, body: str, status: int = 200, message: str = "") -> None:
        tenant_id = get_tenant_id(self)
        out = layout(title, body, tenant_id, message).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(out)))
        self.end_headers()
        self.wfile.write(out)

    def send_redirect(self, to: str, cookie: str | None = None) -> None:
        self.send_response(302)
        self.send_header("Location", to)
        if cookie:
            self.send_header("Set-Cookie", cookie)
        self.end_headers()

    def send_json(self, payload: dict, status: int = 200) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        tenant_id = get_tenant_id(self)
        path = urlparse(self.path).path

        if path == "/health":
            return self.send_json({"status": "ok"})

        if path == "/":
            return self.render(
                "OceanQuote",
                """
                <div class='card'>
                  <h1>OceanQuote SaaS</h1>
                  <p>Sistema para receber e analisar preços de vários produtos em cotações marítimas internacionais.</p>
                  <p class='muted'>Passos rápidos: 1) Crie conta 2) Cadastre produtos 3) Gere uma cotação com várias quantidades.</p>
                  <a href='/register'><button>Começar agora</button></a>
                </div>
                """,
            )

        if path == "/register":
            return self.render(
                "Cadastro",
                """
                <div class='card'><h2>Criar conta</h2>
                <form method='post'>
                  <input name='company_name' placeholder='Empresa' required>
                  <input name='email' placeholder='Email' required>
                  <input type='password' name='password' placeholder='Senha' required>
                  <button>Cadastrar</button>
                </form></div>
                """,
            )

        if path == "/login":
            return self.render(
                "Login",
                """
                <div class='card'><h2>Entrar</h2>
                <form method='post'>
                  <input name='email' placeholder='Email' required>
                  <input type='password' name='password' placeholder='Senha' required>
                  <button>Entrar</button>
                </form></div>
                """,
            )

        if path == "/logout":
            return self.send_redirect("/", clear_session(self))

        if not tenant_id:
            return self.send_redirect("/login")

        with db_conn() as conn:
            if path == "/dashboard":
                quotes = conn.execute("SELECT id FROM quotes WHERE tenant_id=?", (tenant_id,)).fetchall()
                products = conn.execute("SELECT id FROM products WHERE tenant_id=?", (tenant_id,)).fetchall()
                avg_cost = mean([analysis(conn, q["id"])["total_landed_cost"] for q in quotes]) if quotes else 0
                return self.render(
                    "Dashboard",
                    f"""
                    <h2>Dashboard</h2>
                    <div class='grid'>
                      <div class='card'><h3>Produtos</h3><p>{len(products)}</p></div>
                      <div class='card'><h3>Cotações</h3><p>{len(quotes)}</p></div>
                      <div class='card'><h3>Custo médio landed</h3><p>US$ {avg_cost:.2f}</p></div>
                    </div>
                    """,
                )

            if path == "/products":
                items = conn.execute("SELECT * FROM products WHERE tenant_id=? ORDER BY id DESC", (tenant_id,)).fetchall()
                rows = "".join(
                    [
                        f"<tr><td>{html.escape(r['name'])}</td><td>{html.escape(r['category'])}</td><td>{html.escape(r['hs_code'])}</td><td>{r['unit_cost']:.2f}</td><td>{r['weight_kg']:.2f}</td><td>{r['volume_m3']:.3f}</td></tr>"
                        for r in items
                    ]
                )
                return self.render(
                    "Produtos",
                    f"""
                    <div class='card'><h2>Produtos</h2>
                      <form method='post'>
                        <div class='grid'>
                          <input name='name' placeholder='Produto' required>
                          <input name='category' placeholder='Categoria' required>
                          <input name='hs_code' placeholder='HS Code' required>
                          <input type='number' step='0.01' name='unit_cost' placeholder='Preço unitário' required>
                          <input type='number' step='0.01' name='weight_kg' placeholder='Peso kg' required>
                          <input type='number' step='0.001' name='volume_m3' placeholder='Volume m³' required>
                        </div>
                        <button>Adicionar produto</button>
                      </form>
                    </div>
                    <table><tr><th>Produto</th><th>Categoria</th><th>HS</th><th>Preço</th><th>Peso</th><th>Volume</th></tr>{rows}</table>
                    """,
                )

            if path == "/quotes":
                products = conn.execute("SELECT * FROM products WHERE tenant_id=? ORDER BY id DESC", (tenant_id,)).fetchall()
                quotes = conn.execute("SELECT * FROM quotes WHERE tenant_id=? ORDER BY id DESC", (tenant_id,)).fetchall()
                qty_fields = "".join(
                    [
                        f"<label>{html.escape(p['name'])} ({html.escape(p['category'])})</label><input type='number' name='qty_{p['id']}' min='0' value='0'>"
                        for p in products
                    ]
                )
                rows = "".join(
                    [
                        f"<tr><td>{html.escape(q['reference'])}</td><td>{html.escape(q['origin_port'])} → {html.escape(q['destination_port'])}</td><td>{q['lead_time_days']} dias</td><td><a href='/quotes/{q['id']}'>Detalhes</a></td></tr>"
                        for q in quotes
                    ]
                )
                return self.render(
                    "Cotações",
                    f"""
                    <div class='card'><h2>Cotações marítimas</h2>
                    <form method='post'>
                      <div class='grid'>
                        <input name='reference' placeholder='Ref' required>
                        <input name='origin_port' placeholder='Origem' required>
                        <input name='destination_port' placeholder='Destino' required>
                        <input name='incoterm' value='FOB' required>
                        <input name='currency' value='USD' required>
                        <select name='container_type'><option>20GP</option><option>40GP</option><option>40HC</option><option>LCL</option></select>
                        <input type='number' name='lead_time_days' placeholder='Lead time dias' required>
                        <input type='number' step='0.01' name='base_freight' placeholder='Frete base' required>
                        <input type='number' step='0.01' name='surcharges' placeholder='Taxas adicionais' required>
                        <input type='number' step='0.01' name='insurance_rate' placeholder='Seguro %' required>
                      </div>
                      <h3>Quantidade por produto</h3>
                      <div class='grid'>{qty_fields}</div>
                      <button>Gerar cotação</button>
                    </form></div>
                    <table><tr><th>Ref</th><th>Rota</th><th>Lead time</th><th>Ação</th></tr>{rows}</table>
                    """,
                )

            if path.startswith("/quotes/"):
                quote_id_raw = path.split("/")[-1]
                if quote_id_raw.isdigit():
                    quote_id = int(quote_id_raw)
                    quote = conn.execute("SELECT * FROM quotes WHERE id=? AND tenant_id=?", (quote_id, tenant_id)).fetchone()
                    if not quote:
                        return self.render("Não encontrado", "<div class='card'>Cotação não encontrada</div>", 404)

                    a = analysis(conn, quote_id)
                    items = conn.execute(
                        """
                        SELECT qi.quantity, p.name, p.unit_cost FROM quote_items qi
                        JOIN products p ON p.id = qi.product_id
                        WHERE qi.quote_id=?
                        """,
                        (quote_id,),
                    ).fetchall()
                    rows = "".join(
                        [
                            f"<tr><td>{html.escape(i['name'])}</td><td>{i['quantity']}</td><td>{quote['currency']} {i['unit_cost']:.2f}</td><td>{quote['currency']} {i['quantity'] * i['unit_cost']:.2f}</td></tr>"
                            for i in items
                        ]
                    )
                    return self.render(
                        "Análise",
                        f"""
                        <div class='card'><h2>Análise da cotação {html.escape(quote['reference'])}</h2>
                        <p>Rota: {html.escape(quote['origin_port'])} → {html.escape(quote['destination_port'])}</p>
                        <div class='grid'>
                          <div class='card'><strong>Valor da carga</strong><br>{quote['currency']} {a['total_cargo_value']}</div>
                          <div class='card'><strong>Custo logístico</strong><br>{quote['currency']} {a['total_logistics_cost']}</div>
                          <div class='card'><strong>Custo total</strong><br>{quote['currency']} {a['total_landed_cost']}</div>
                          <div class='card'><strong>Risco</strong><br>{a['risk_score']}/100</div>
                        </div>
                        <ul>
                          <li>Peso total: {a['total_weight']} kg</li>
                          <li>Volume total: {a['total_volume']} m³</li>
                          <li>Custo por kg: {quote['currency']} {a['cost_per_kg']}</li>
                          <li>Custo por m³: {quote['currency']} {a['cost_per_m3']}</li>
                          <li>Seguro: {quote['currency']} {a['insurance_cost']}</li>
                          <li><strong>Recomendação:</strong> {a['recommendation']}</li>
                        </ul></div>
                        <table><tr><th>Produto</th><th>Qtd</th><th>Preço unit.</th><th>Total</th></tr>{rows}</table>
                        """,
                    )

            if path.startswith("/api/quotes/") and path.endswith("/analysis"):
                parts = path.strip("/").split("/")
                if len(parts) == 4 and parts[0] == "api" and parts[1] == "quotes" and parts[2].isdigit():
                    quote_id = int(parts[2])
                    quote = conn.execute("SELECT id FROM quotes WHERE id=? AND tenant_id=?", (quote_id, tenant_id)).fetchone()
                    if not quote:
                        return self.send_json({"error": "Cotação não encontrada"}, 404)
                    return self.send_json(analysis(conn, quote_id))

        return self.render("404", "<div class='card'>Página não encontrada.</div>", 404)

    def do_POST(self) -> None:
        path = urlparse(self.path).path
        tenant_id = get_tenant_id(self)
        data = parse_form(self)

        with db_conn() as conn:
            if path == "/register":
                company_name = data.get("company_name", "").strip()
                email = data.get("email", "").strip().lower()
                password = data.get("password", "").strip()
                if not company_name or not email or not password:
                    return self.render("Cadastro", "", 400, "Preencha todos os campos para cadastrar.")
                try:
                    conn.execute(
                        "INSERT INTO tenants (company_name, email, password_hash) VALUES (?, ?, ?)",
                        (company_name, email, hash_password(password)),
                    )
                    conn.commit()
                except sqlite3.IntegrityError:
                    return self.render("Cadastro", "", 400, "E-mail já cadastrado.")
                return self.send_redirect("/login")

            if path == "/login":
                email = data.get("email", "").strip().lower()
                password = data.get("password", "").strip()
                tenant = conn.execute(
                    "SELECT id FROM tenants WHERE email=? AND password_hash=?",
                    (email, hash_password(password)),
                ).fetchone()
                if not tenant:
                    return self.render("Login", "", 401, "Credenciais inválidas.")
                return self.send_redirect("/dashboard", create_session(int(tenant["id"])))

            if not tenant_id:
                return self.send_redirect("/login")

            if path == "/products":
                conn.execute(
                    """
                    INSERT INTO products (tenant_id, name, category, hs_code, unit_cost, weight_kg, volume_m3)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        tenant_id,
                        data["name"],
                        data["category"],
                        data["hs_code"],
                        float(data["unit_cost"]),
                        float(data["weight_kg"]),
                        float(data["volume_m3"]),
                    ),
                )
                conn.commit()
                return self.send_redirect("/products")

            if path == "/quotes":
                cur = conn.execute(
                    """
                    INSERT INTO quotes (tenant_id, reference, origin_port, destination_port, incoterm, currency,
                    container_type, lead_time_days, base_freight, surcharges, insurance_rate)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        tenant_id,
                        data["reference"],
                        data["origin_port"],
                        data["destination_port"],
                        data["incoterm"].upper(),
                        data["currency"].upper(),
                        data["container_type"],
                        int(data["lead_time_days"]),
                        float(data["base_freight"]),
                        float(data["surcharges"]),
                        float(data["insurance_rate"]),
                    ),
                )
                quote_id = cur.lastrowid
                products = conn.execute("SELECT id FROM products WHERE tenant_id=?", (tenant_id,)).fetchall()
                for p in products:
                    qty = int(data.get(f"qty_{p['id']}", "0") or "0")
                    if qty > 0:
                        conn.execute(
                            "INSERT INTO quote_items (quote_id, product_id, quantity) VALUES (?, ?, ?)",
                            (quote_id, p["id"], qty),
                        )
                conn.commit()
                return self.send_redirect(f"/quotes/{quote_id}")

        return self.render("404", "<div class='card'>Operação inválida.</div>", 404)


if __name__ == "__main__":
    init_db()
    server = ThreadingHTTPServer(("0.0.0.0", 5000), App)
    print("Servidor em http://localhost:5000")
    server.serve_forever()
