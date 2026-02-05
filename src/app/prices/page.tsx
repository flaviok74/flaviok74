const priceQuotes = [
  {
    id: "PQ-2041",
    product: "Ácido Cítrico",
    vendor: "Atlas Distribuidora",
    validity: "Válido até 12/10/2024",
    status: "APPROVED"
  },
  {
    id: "PQ-2042",
    product: "Peróxido de Hidrogênio",
    vendor: "Norte Supply",
    validity: "Expira em 4 dias",
    status: "IMPORTED_PENDING_REVIEW"
  }
];

export default function PricesPage() {
  return (
    <section className="space-y-6">
      <div className="card">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div>
            <h2 className="text-lg font-semibold">Cotações de preço</h2>
            <p className="text-sm text-slate-600">Busca rápida, filtros e alertas de variação.</p>
          </div>
          <div className="flex gap-3">
            <button className="rounded-lg border border-slate-200 px-4 py-2 text-sm font-semibold">Duplicar</button>
            <button className="rounded-lg bg-brand-500 px-4 py-2 text-sm font-semibold text-white">Nova cotação</button>
          </div>
        </div>
        <div className="mt-6 grid gap-4">
          {priceQuotes.map((quote) => (
            <div key={quote.id} className="flex flex-wrap items-center justify-between gap-3 rounded-lg border border-slate-200 p-4">
              <div>
                <p className="text-sm text-slate-500">{quote.id}</p>
                <p className="text-base font-semibold">{quote.product}</p>
                <p className="text-sm text-slate-600">{quote.vendor}</p>
              </div>
              <div className="text-sm text-slate-600">{quote.validity}</div>
              <span className="badge bg-slate-100 text-slate-600">{quote.status}</span>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
