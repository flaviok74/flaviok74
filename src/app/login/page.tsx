export default function LoginPage() {
  return (
    <section className="mx-auto max-w-md">
      <div className="card">
        <h2 className="text-lg font-semibold">Acesso</h2>
        <p className="text-sm text-slate-600">Entre com suas credenciais corporativas.</p>
        <div className="mt-6 space-y-4">
          {["Email", "Senha"].map((label) => (
            <div key={label} className="space-y-2">
              <label className="text-xs font-semibold uppercase text-slate-500">{label}</label>
              <div className="h-10 rounded-lg border border-dashed border-slate-300 bg-slate-50" />
            </div>
          ))}
          <button className="w-full rounded-lg bg-brand-500 px-4 py-2 text-sm font-semibold text-white">Entrar</button>
        </div>
      </div>
    </section>
  );
}
