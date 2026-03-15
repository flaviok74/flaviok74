const REFRESH_INTERVAL_MS = 2 * 60 * 60 * 1000;

let allQuotes = [];

const statusEl = document.getElementById("status-msg");
const quotesBody = document.getElementById("quotes-body");
const lastUpdate = document.getElementById("last-update");
const summaryCards = document.getElementById("summary-cards");
const manualMsg = document.getElementById("manual-msg");

const filters = {
  product: document.getElementById("filter-product"),
  supplier: document.getElementById("filter-supplier"),
  currency: document.getElementById("filter-currency"),
  maxPrice: document.getElementById("filter-max-price"),
};

document.getElementById("btn-clear").addEventListener("click", () => {
  filters.product.value = "";
  filters.supplier.value = "";
  filters.currency.value = "";
  filters.maxPrice.value = "";
  renderTable(allQuotes);
  renderSummary(allQuotes);
});

Object.values(filters).forEach((el) => el.addEventListener("input", applyFilters));

document.getElementById("manual-form").addEventListener("submit", submitManualQuote);
document.getElementById("btn-clear-manual").addEventListener("click", clearManualQuotes);

async function submitManualQuote(event) {
  event.preventDefault();
  manualMsg.textContent = "Salvando cotação manual...";

  const payload = {
    produto: document.getElementById("manual-produto").value,
    fornecedor: document.getElementById("manual-fornecedor").value,
    preco: document.getElementById("manual-preco").value,
    moeda: document.getElementById("manual-moeda").value,
    quantidade: document.getElementById("manual-quantidade").value,
    unidade: document.getElementById("manual-unidade").value,
    assunto: document.getElementById("manual-assunto").value,
  };

  try {
    const response = await fetch("/api/manual-quotes", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const data = await response.json();

    if (!response.ok) throw new Error(data.message || "Erro ao salvar cotação manual");

    manualMsg.textContent = data.message;
    event.target.reset();
    await loadQuotes();
  } catch (error) {
    manualMsg.textContent = `Erro: ${error.message}`;
  }
}

async function clearManualQuotes() {
  try {
    const response = await fetch("/api/manual-quotes", { method: "DELETE" });
    const data = await response.json();
    if (!response.ok) throw new Error(data.message || "Erro ao limpar cotações");

    manualMsg.textContent = data.message;
    await loadQuotes();
  } catch (error) {
    manualMsg.textContent = `Erro: ${error.message}`;
  }
}

async function loadQuotes() {
  statusEl.textContent = "Atualizando dados...";
  try {
    const response = await fetch("/api/quotes");
    const data = await response.json();

    if (!response.ok) throw new Error(data.message || "Falha ao carregar cotações");

    allQuotes = data.quotes || [];
    statusEl.textContent = data.message;
    lastUpdate.textContent = `Última atualização: ${data.last_update}`;

    populateCurrencyFilter(allQuotes);
    renderTable(allQuotes);
    renderSummary(allQuotes);
  } catch (error) {
    statusEl.textContent = `Erro: ${error.message}`;
    quotesBody.innerHTML = "";
    summaryCards.innerHTML = "";
  }
}

function populateCurrencyFilter(quotes) {
  const current = filters.currency.value;
  const currencies = [...new Set(quotes.map((q) => q.moeda))].sort();
  filters.currency.innerHTML = '<option value="">Todas</option>';
  currencies.forEach((currency) => {
    const option = document.createElement("option");
    option.value = currency;
    option.textContent = currency;
    filters.currency.appendChild(option);
  });
  filters.currency.value = current;
}

function applyFilters() {
  const productFilter = filters.product.value.trim().toLowerCase();
  const supplierFilter = filters.supplier.value.trim().toLowerCase();
  const currencyFilter = filters.currency.value;
  const maxPriceFilter = Number(filters.maxPrice.value || 0);

  const filtered = allQuotes.filter((quote) => {
    const productOk = quote.produto.toLowerCase().includes(productFilter);
    const supplierOk = quote.fornecedor.toLowerCase().includes(supplierFilter);
    const currencyOk = currencyFilter ? quote.moeda === currencyFilter : true;
    const priceOk = maxPriceFilter > 0 ? quote.preco <= maxPriceFilter : true;
    return productOk && supplierOk && currencyOk && priceOk;
  });

  renderTable(filtered);
  renderSummary(filtered);
}

function renderTable(quotes) {
  if (!quotes.length) {
    quotesBody.innerHTML = '<tr><td colspan="6">Nenhuma cotação para os filtros selecionados.</td></tr>';
    return;
  }

  quotesBody.innerHTML = quotes.map((quote) => `
      <tr>
        <td>${quote.produto}</td>
        <td>${quote.fornecedor}</td>
        <td>${formatCurrency(quote.preco, quote.moeda)}</td>
        <td>${formatQuantity(quote.quantidade, quote.unidade)}</td>
        <td>${quote.data_email}</td>
        <td>${quote.assunto}</td>
      </tr>
    `).join("");
}

function renderSummary(quotes) {
  if (!quotes.length) {
    summaryCards.innerHTML = "";
    return;
  }

  const cheapest = quotes.reduce((acc, quote) => (quote.preco < acc.preco ? quote : acc), quotes[0]);
  const avgPrice = quotes.reduce((sum, quote) => sum + quote.preco, 0) / quotes.length;
  const supplierCount = new Set(quotes.map((q) => q.fornecedor)).size;

  summaryCards.innerHTML = `
    <div class="card"><strong>Total de cotações</strong><span>${quotes.length}</span></div>
    <div class="card"><strong>Fornecedores únicos</strong><span>${supplierCount}</span></div>
    <div class="card"><strong>Menor preço</strong><span>${formatCurrency(cheapest.preco, cheapest.moeda)} (${cheapest.produto})</span></div>
    <div class="card"><strong>Preço médio</strong><span>${avgPrice.toFixed(2)}</span></div>
  `;
}

function formatCurrency(value, currency) {
  return new Intl.NumberFormat("pt-BR", { style: "currency", currency, minimumFractionDigits: 2 }).format(value);
}

function formatQuantity(quantity, unit) {
  if (quantity == null) return "-";
  return `${quantity} ${unit || ""}`.trim();
}

loadQuotes();
setInterval(loadQuotes, REFRESH_INTERVAL_MS);
