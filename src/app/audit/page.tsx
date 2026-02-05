const auditRows = [
  {
    id: "1",
    entity: "freight_quote",
    action: "UPDATE",
    user: "Operador",
    date: "2024-02-05"
  },
  {
    id: "2",
    entity: "supplier",
    action: "CREATE",
    user: "Admin",
    date: "2024-02-03"
  }
];

export default function AuditPage() {
  return (
    <section className="space-y-6">
      <div className="card">
        <h2 className="text-lg font-semibold">Auditoria</h2>
        <p className="text-sm text-slate-600">Filtre por período, entidade, usuário e ação.</p>
        <div className="mt-4 grid gap-4 md:grid-cols-4">
          {["Período", "Usuário", "Fornecedor", "Entidade"].map((label) => (
            <div key={label} className="space-y-2">
              <label className="text-xs font-semibold uppercase text-slate-500">{label}</label>
              <div className="h-10 rounded-lg border border-dashed border-slate-300 bg-slate-50" />
            </div>
          ))}
        </div>
        <div className="mt-6 space-y-3">
          {auditRows.map((row) => (
            <div key={row.id} className="flex items-center justify-between rounded-lg border border-slate-200 p-4">
              <div>
                <p className="text-sm text-slate-500">{row.entity}</p>
                <p className="font-semibold">{row.action}</p>
              </div>
              <div className="text-sm text-slate-600">{row.user}</div>
              <div className="text-sm text-slate-600">{row.date}</div>
              <button className="rounded-lg border border-slate-200 px-3 py-1 text-xs font-semibold">Detalhes</button>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
