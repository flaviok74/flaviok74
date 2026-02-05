import "@/styles/globals.css";
import type { ReactNode } from "react";

export const metadata = {
  title: "Ekoquim Product Pricing",
  description: "Plataforma de monitoramento de preços de produtos"
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="pt-BR">
      <body>
        <div className="min-h-screen bg-slate-50">
          <header className="border-b border-slate-200 bg-white">
            <div className="mx-auto flex max-w-6xl flex-wrap items-center justify-between gap-4 px-6 py-4">
              <div>
                <p className="text-sm text-slate-500">Ekoquim Product Pricing</p>
                <h1 className="text-xl font-semibold text-slate-900">Gestão e análise de preços</h1>
              </div>
              <nav className="flex flex-wrap gap-4 text-sm font-medium text-slate-600">
                <a className="hover:text-slate-900" href="/dashboard">Dashboard</a>
                <a className="hover:text-slate-900" href="/prices">Preços</a>
                <a className="hover:text-slate-900" href="/imports">Importar link</a>
                <a className="hover:text-slate-900" href="/products">Produtos</a>
                <a className="hover:text-slate-900" href="/vendors">Fornecedores</a>
                <a className="hover:text-slate-900" href="/audit">Auditoria</a>
                <a className="hover:text-slate-900" href="/admin/users">Administração</a>
              </nav>
            </div>
          </header>
          <main className="mx-auto max-w-6xl px-6 py-8">{children}</main>
        </div>
      </body>
    </html>
  );
}
