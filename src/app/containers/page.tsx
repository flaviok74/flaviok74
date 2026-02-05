const containers = [
  { code: "20GP", description: "Standard 20-foot" },
  { code: "40HC", description: "High Cube 40-foot" },
  { code: "40NOR", description: "Non-operating reefer" }
];

export default function ContainersPage() {
  return (
    <section className="space-y-6">
      <div className="card">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-lg font-semibold">Tipos de container</h2>
            <p className="text-sm text-slate-600">Cadastros de 20GP, 40HC, 40NOR e outros.</p>
          </div>
          <button className="rounded-lg bg-brand-500 px-4 py-2 text-sm font-semibold text-white">Novo tipo</button>
        </div>
        <div className="mt-6 space-y-3">
          {containers.map((container) => (
            <div key={container.code} className="flex items-center justify-between rounded-lg border border-slate-200 p-4">
              <div>
                <p className="font-semibold">{container.code}</p>
                <p className="text-sm text-slate-600">{container.description}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
