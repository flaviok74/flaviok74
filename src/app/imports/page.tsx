export default function ImportsPage() {
  return (
    <section className="space-y-6">
      <div className="card">
        <h2 className="text-lg font-semibold">Nova cotação por link</h2>
        <p className="text-sm text-slate-600">
          Cole o link da cotação, selecione fornecedor, origem/destino e moeda. O parser automático
          será integrado em versões futuras.
        </p>
        <div className="mt-6 grid gap-4 md:grid-cols-2">
          {["URL da cotação", "Fornecedor", "Origem", "Destino", "Moeda", "Validade"].map((label) => (
            <div key={label} className="space-y-2">
              <label className="text-xs font-semibold uppercase text-slate-500">{label}</label>
              <div className="h-10 rounded-lg border border-dashed border-slate-300 bg-slate-50" />
            </div>
          ))}
        </div>
        <div className="mt-6 flex gap-3">
          <button className="rounded-lg border border-slate-200 px-4 py-2 text-sm font-semibold">Salvar rascunho</button>
          <button className="rounded-lg bg-brand-500 px-4 py-2 text-sm font-semibold text-white">Enviar para revisão</button>
        </div>
      </div>
    </section>
  );
}
