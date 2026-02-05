const suppliers = [
  { name: "Atlantic Shipping", country: "BR", status: "ativo" },
  { name: "BlueWave Logistics", country: "US", status: "ativo" }
];

export default function SuppliersPage() {
  return (
    <section className="space-y-6">
      <div className="card">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-lg font-semibold">Fornecedores</h2>
            <p className="text-sm text-slate-600">Cadastre empresas que enviam cotações.</p>
          </div>
          <button className="rounded-lg bg-brand-500 px-4 py-2 text-sm font-semibold text-white">Novo fornecedor</button>
        </div>
        <div className="mt-6 space-y-3">
          {suppliers.map((supplier) => (
            <div key={supplier.name} className="flex items-center justify-between rounded-lg border border-slate-200 p-4">
              <div>
                <p className="font-semibold">{supplier.name}</p>
                <p className="text-sm text-slate-600">{supplier.country}</p>
              </div>
              <span className="badge bg-emerald-100 text-emerald-700">{supplier.status}</span>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
