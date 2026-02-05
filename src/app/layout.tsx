import "@/styles/globals.css";
import type { ReactNode } from "react";

export const metadata = {
  title: "Ekoquim Freight Quotes",
  description: "Plataforma de cotações de frete marítimo"
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="pt-BR">
      <body>
        <div className="min-h-screen bg-slate-50">
          <header className="border-b border-slate-200 bg-white">
            <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
              <div>
                <p className="text-sm text-slate-500">Ekoquim Freight Quotes</p>
                <h1 className="text-xl font-semibold text-slate-900">Gestão de cotações marítimas</h1>
              </div>
              <nav className="flex gap-4 text-sm font-medium text-slate-600">
                <a className="hover:text-slate-900" href="/dashboard">Dashboard</a>
                <a className="hover:text-slate-900" href="/quotes">Cotações</a>
                <a className="hover:text-slate-900" href="/imports">Importar link</a>
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
