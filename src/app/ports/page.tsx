const ports = [
  { name: "Santos", country: "BR", code: "BRSSZ" },
  { name: "Rotterdam", country: "NL", code: "NLRTM" }
];

export default function PortsPage() {
  return (
    <section className="space-y-6">
      <div className="card">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-lg font-semibold">Portos</h2>
            <p className="text-sm text-slate-600">Origem e destino com códigos UN/LOCODE.</p>
          </div>
          <button className="rounded-lg bg-brand-500 px-4 py-2 text-sm font-semibold text-white">Novo porto</button>
        </div>
        <div className="mt-6 space-y-3">
          {ports.map((port) => (
            <div key={port.code} className="flex items-center justify-between rounded-lg border border-slate-200 p-4">
              <div>
                <p className="font-semibold">{port.name}</p>
                <p className="text-sm text-slate-600">{port.country}</p>
              </div>
              <span className="badge bg-slate-100 text-slate-600">{port.code}</span>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
