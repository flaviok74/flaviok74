from __future__ import annotations

from datetime import datetime
from functools import wraps
from statistics import mean

from flask import (
    Flask,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
app.config["SECRET_KEY"] = "dev-secret-change-me"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///freight_saas.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


class Tenant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    products = db.relationship("Product", backref="tenant", lazy=True)
    quotes = db.relationship("FreightQuote", backref="tenant", lazy=True)


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey("tenant.id"), nullable=False)
    name = db.Column(db.String(120), nullable=False)
    category = db.Column(db.String(60), nullable=False)
    hs_code = db.Column(db.String(20), nullable=False)
    unit_cost = db.Column(db.Float, nullable=False)
    weight_kg = db.Column(db.Float, nullable=False)
    volume_m3 = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class FreightQuote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey("tenant.id"), nullable=False)
    reference = db.Column(db.String(40), nullable=False)
    origin_port = db.Column(db.String(80), nullable=False)
    destination_port = db.Column(db.String(80), nullable=False)
    incoterm = db.Column(db.String(10), nullable=False)
    currency = db.Column(db.String(10), nullable=False)
    container_type = db.Column(db.String(20), nullable=False)
    lead_time_days = db.Column(db.Integer, nullable=False)
    base_freight = db.Column(db.Float, nullable=False)
    surcharges = db.Column(db.Float, nullable=False)
    insurance_rate = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    items = db.relationship(
        "QuoteItem", backref="quote", lazy=True, cascade="all, delete-orphan"
    )


class QuoteItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quote_id = db.Column(db.Integer, db.ForeignKey("freight_quote.id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("product.id"), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)

    product = db.relationship("Product")


def login_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if "tenant_id" not in session:
            flash("Faça login para continuar.", "warning")
            return redirect(url_for("login"))
        return fn(*args, **kwargs)

    return wrapper


def current_tenant() -> Tenant | None:
    tenant_id = session.get("tenant_id")
    if not tenant_id:
        return None
    return Tenant.query.get(tenant_id)


def generate_analysis(quote: FreightQuote):
    total_weight = 0.0
    total_volume = 0.0
    total_cargo_value = 0.0

    for item in quote.items:
        total_weight += item.quantity * item.product.weight_kg
        total_volume += item.quantity * item.product.volume_m3
        total_cargo_value += item.quantity * item.product.unit_cost

    insurance_cost = total_cargo_value * (quote.insurance_rate / 100)
    total_logistics_cost = quote.base_freight + quote.surcharges + insurance_cost
    total_landed_cost = total_cargo_value + total_logistics_cost

    cost_per_kg = total_logistics_cost / total_weight if total_weight else 0
    cost_per_m3 = total_logistics_cost / total_volume if total_volume else 0

    risk_score = 35
    if quote.lead_time_days > 35:
        risk_score += 20
    if quote.destination_port.lower() in {"lagos", "durban", "mumbai", "santos"}:
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


@app.route("/")
def index():
    if "tenant_id" in session:
        return redirect(url_for("dashboard"))
    return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        company_name = request.form["company_name"].strip()
        email = request.form["email"].strip().lower()
        password = request.form["password"]

        if Tenant.query.filter_by(email=email).first():
            flash("E-mail já cadastrado.", "danger")
            return redirect(url_for("register"))

        tenant = Tenant(
            company_name=company_name,
            email=email,
            password_hash=generate_password_hash(password),
        )
        db.session.add(tenant)
        db.session.commit()

        flash("Conta criada com sucesso! Faça login.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"].strip().lower()
        password = request.form["password"]

        tenant = Tenant.query.filter_by(email=email).first()
        if not tenant or not check_password_hash(tenant.password_hash, password):
            flash("Credenciais inválidas.", "danger")
            return redirect(url_for("login"))

        session["tenant_id"] = tenant.id
        flash("Login realizado com sucesso.", "success")
        return redirect(url_for("dashboard"))

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("Sessão encerrada.", "info")
    return redirect(url_for("index"))


@app.route("/dashboard")
@login_required
def dashboard():
    tenant = current_tenant()
    quotes = (
        FreightQuote.query.filter_by(tenant_id=tenant.id)
        .order_by(FreightQuote.created_at.desc())
        .all()
    )
    products = Product.query.filter_by(tenant_id=tenant.id).all()

    analyses = [generate_analysis(q) for q in quotes] if quotes else []
    avg_landed_cost = mean([a["total_landed_cost"] for a in analyses]) if analyses else 0

    return render_template(
        "dashboard.html",
        tenant=tenant,
        quote_count=len(quotes),
        product_count=len(products),
        avg_landed_cost=round(avg_landed_cost, 2),
        latest_quotes=quotes[:5],
    )


@app.route("/products", methods=["GET", "POST"])
@login_required
def products():
    tenant = current_tenant()

    if request.method == "POST":
        product = Product(
            tenant_id=tenant.id,
            name=request.form["name"].strip(),
            category=request.form["category"].strip(),
            hs_code=request.form["hs_code"].strip(),
            unit_cost=float(request.form["unit_cost"]),
            weight_kg=float(request.form["weight_kg"]),
            volume_m3=float(request.form["volume_m3"]),
        )
        db.session.add(product)
        db.session.commit()
        flash("Produto adicionado com sucesso.", "success")
        return redirect(url_for("products"))

    items = (
        Product.query.filter_by(tenant_id=tenant.id)
        .order_by(Product.created_at.desc())
        .all()
    )
    return render_template("products.html", products=items)


@app.route("/quotes", methods=["GET", "POST"])
@login_required
def quotes():
    tenant = current_tenant()
    products = Product.query.filter_by(tenant_id=tenant.id).all()

    if request.method == "POST":
        quote = FreightQuote(
            tenant_id=tenant.id,
            reference=request.form["reference"].strip(),
            origin_port=request.form["origin_port"].strip(),
            destination_port=request.form["destination_port"].strip(),
            incoterm=request.form["incoterm"].strip().upper(),
            currency=request.form["currency"].strip().upper(),
            container_type=request.form["container_type"],
            lead_time_days=int(request.form["lead_time_days"]),
            base_freight=float(request.form["base_freight"]),
            surcharges=float(request.form["surcharges"]),
            insurance_rate=float(request.form["insurance_rate"]),
        )
        db.session.add(quote)
        db.session.flush()

        for product in products:
            qty = request.form.get(f"qty_{product.id}", "0")
            quantity = int(qty) if qty else 0
            if quantity > 0:
                db.session.add(QuoteItem(quote_id=quote.id, product_id=product.id, quantity=quantity))

        db.session.commit()
        flash("Cotação criada com sucesso.", "success")
        return redirect(url_for("quote_detail", quote_id=quote.id))

    list_quotes = (
        FreightQuote.query.filter_by(tenant_id=tenant.id)
        .order_by(FreightQuote.created_at.desc())
        .all()
    )
    return render_template("quotes.html", products=products, quotes=list_quotes)


@app.route("/quotes/<int:quote_id>")
@login_required
def quote_detail(quote_id: int):
    tenant = current_tenant()
    quote = FreightQuote.query.filter_by(id=quote_id, tenant_id=tenant.id).first_or_404()
    analysis = generate_analysis(quote)
    return render_template("quote_detail.html", quote=quote, analysis=analysis)


@app.route("/api/quotes/<int:quote_id>/analysis")
@login_required
def quote_analysis_api(quote_id: int):
    tenant = current_tenant()
    quote = FreightQuote.query.filter_by(id=quote_id, tenant_id=tenant.id).first_or_404()
    return jsonify(generate_analysis(quote))


@app.cli.command("init-db")
def init_db_command():
    db.create_all()
    print("Database initialized.")


with app.app_context():
    db.create_all()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
