const users = [
  { name: "Admin User", role: "ADMIN", email: "admin@ekoquim.test" },
  { name: "Analista", role: "ANALYST", email: "analista@ekoquim.test" },
  { name: "Leitura", role: "VIEWER", email: "viewer@ekoquim.test" }
];

export default function UsersPage() {
  return (
    <section className="space-y-6">
      <div className="card">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-lg font-semibold">Usuários e perfis</h2>
            <p className="text-sm text-slate-600">Gerencie acessos e permissões por organização.</p>
          </div>
          <button className="rounded-lg bg-brand-500 px-4 py-2 text-sm font-semibold text-white">Novo usuário</button>
        </div>
        <div className="mt-6 space-y-3">
          {users.map((user) => (
            <div key={user.email} className="flex items-center justify-between rounded-lg border border-slate-200 p-4">
              <div>
                <p className="font-semibold">{user.name}</p>
                <p className="text-sm text-slate-600">{user.email}</p>
              </div>
              <span className="badge bg-slate-100 text-slate-600">{user.role}</span>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
