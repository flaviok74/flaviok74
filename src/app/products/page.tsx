const products = [
  { name: "Ácido Cítrico", category: "Químicos", unit: "kg" },
  { name: "Container 1000L", category: "Embalagens", unit: "un" }
];

export default function ProductsPage() {
  return (
    <section className="space-y-6">
      <div className="card">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-lg font-semibold">Produtos</h2>
            <p className="text-sm text-slate-600">Catálogo de itens monitorados por preço.</p>
          </div>
          <button className="rounded-lg bg-brand-500 px-4 py-2 text-sm font-semibold text-white">Novo produto</button>
        </div>
        <div className="mt-6 space-y-3">
          {products.map((product) => (
            <div key={product.name} className="flex items-center justify-between rounded-lg border border-slate-200 p-4">
              <div>
                <p className="font-semibold">{product.name}</p>
                <p className="text-sm text-slate-600">{product.category}</p>
              </div>
              <span className="badge bg-slate-100 text-slate-600">{product.unit}</span>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
