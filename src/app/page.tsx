import Link from "next/link";

export default function HomePage() {
  return (
    <section className="space-y-6">
      <div className="card">
        <h2 className="text-lg font-semibold">Bem-vindo ao Ekoquim Product Pricing</h2>
        <p className="mt-2 text-sm text-slate-600">
          Centralize preços de fornecedores, compare históricos e acompanhe tendências por produto.
        </p>
        <div className="mt-4 flex flex-wrap gap-3">
          <Link className="rounded-lg bg-brand-500 px-4 py-2 text-sm font-semibold text-white" href="/dashboard">
            Abrir dashboard
          </Link>
          <Link className="rounded-lg border border-slate-200 px-4 py-2 text-sm font-semibold" href="/prices">
            Ver preços
          </Link>
        </div>
      </div>
    </section>
  );
}
