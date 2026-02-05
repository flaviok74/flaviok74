const stats = [
  { label: "Produtos monitorados", value: "86" },
  { label: "Fornecedores ativos", value: "24" },
  { label: "Cotações recentes", value: "112" },
  { label: "Alertas de aumento", value: "7" }
];

const insights = [
  {
    title: "Tendência de preço (90 dias)",
    description: "Ácido Cítrico com alta de 4% e maior volatilidade nas últimas 8 semanas."
  },
  {
    title: "Lead time médio",
    description: "9 dias úteis nos itens de embalagens, com pico na região Sudeste."
  },
  {
    title: "Top fornecedores",
    description: "Atlas Distribuidora lidera em consistência e menor variação de preço."
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
          {["Período", "Fornecedor", "Produto", "Categoria"].map((label) => (
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
