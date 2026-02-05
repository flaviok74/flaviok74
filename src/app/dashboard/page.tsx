const stats = [
  { label: "Cotações ativas", value: "128" },
  { label: "Rotas monitoradas", value: "42" },
  { label: "Fornecedores ativos", value: "18" },
  { label: "Risco de rollover alto", value: "12%" }
];

const insights = [
  {
    title: "Tendência de preço (90 dias)",
    description: "Queda média de 6% nas rotas Santos → Rotterdam para 40HC."
  },
  {
    title: "Transit time médio",
    description: "22 dias na rota Shanghai → Santos com variação de ±3 dias."
  },
  {
    title: "Top fornecedores",
    description: "Atlantic Shipping lidera em volume de cotações aprovadas."
  }
];

export default function DashboardPage() {
  return (
    <section className="space-y-8">
      <div className="grid gap-4 md:grid-cols-4">
        {stats.map((stat) => (
          <div key={stat.label} className="card">
            <p className="text-sm text-slate-500">{stat.label}</p>
            <p className="mt-2 text-2xl font-semibold text-slate-900">{stat.value}</p>
          </div>
        ))}
      </div>

      <div className="grid gap-6 md:grid-cols-3">
        {insights.map((insight) => (
          <div key={insight.title} className="card">
            <h3 className="text-base font-semibold">{insight.title}</h3>
            <p className="mt-2 text-sm text-slate-600">{insight.description}</p>
          </div>
        ))}
      </div>

      <div className="card">
        <h3 className="text-base font-semibold">Filtros globais</h3>
        <div className="mt-4 grid gap-4 md:grid-cols-4">
          {["Período", "Fornecedor", "Origem", "Destino"].map((label) => (
            <div key={label} className="space-y-2">
              <label className="text-xs font-semibold uppercase text-slate-500">{label}</label>
              <div className="h-10 rounded-lg border border-dashed border-slate-300 bg-slate-50" />
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
