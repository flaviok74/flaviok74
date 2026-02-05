const quotes = [
  {
    id: "Q-1024",
    route: "Santos → Rotterdam",
    supplier: "Atlantic Shipping",
    validity: "Válida até 12/10/2024",
    status: "APPROVED"
  },
  {
    id: "Q-1025",
    route: "Shanghai → Santos",
    supplier: "BlueWave Logistics",
    validity: "Expira em 4 dias",
    status: "IMPORTED_PENDING_REVIEW"
  }
];

export default function QuotesPage() {
  return (
    <section className="space-y-6">
      <div className="card">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div>
            <h2 className="text-lg font-semibold">Cotações</h2>
            <p className="text-sm text-slate-600">Busca rápida, filtros e status de validade.</p>
          </div>
          <div className="flex gap-3">
            <button className="rounded-lg border border-slate-200 px-4 py-2 text-sm font-semibold">Duplicar</button>
            <button className="rounded-lg bg-brand-500 px-4 py-2 text-sm font-semibold text-white">Nova cotação</button>
          </div>
        </div>
        <div className="mt-6 grid gap-4">
          {quotes.map((quote) => (
            <div key={quote.id} className="flex flex-wrap items-center justify-between gap-3 rounded-lg border border-slate-200 p-4">
              <div>
                <p className="text-sm text-slate-500">{quote.id}</p>
                <p className="text-base font-semibold">{quote.route}</p>
                <p className="text-sm text-slate-600">{quote.supplier}</p>
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
