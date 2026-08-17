import { Cpu, RefreshCw, Search, Skull } from "lucide-react";
import { useCallback, useEffect, useState } from "react";
import { API_BASE } from "@/lib/api";

type Proc = {
	pid: number;
	name: string;
	cpu_percent: number;
	memory_percent: number;
};

export default function Processes() {
	const [procs, setProcs] = useState<Proc[]>([]);
	const [total, setTotal] = useState(0);
	const [search, setSearch] = useState("");
	const [error, setError] = useState("");
	const [busy, setBusy] = useState<number | null>(null);

	const load = useCallback(async () => {
		const q = new URLSearchParams();
		q.set("limit", "200");
		if (search) q.set("search", search);
		try {
			const r = await fetch(API_BASE + `/api/processes?${q}`);
			const d = await r.json();
			setProcs(d.processes ?? []);
			setTotal(d.total ?? d.count ?? 0);
		} catch {
			setProcs([]);
		}
	}, [search]);

	useEffect(() => {
		const iv = setInterval(load, 5000);
		load();
		return () => clearInterval(iv);
	}, [load]);

	const kill = async (pid: number, name: string) => {
		if (!window.confirm(`Terminate process ${name} (PID ${pid})?`)) return;
		setBusy(pid);
		setError("");
		try {
			const r = await fetch(API_BASE + `/api/processes/${pid}`, {
				method: "DELETE",
			});
			if (!r.ok) {
				const d = await r.json().catch(() => ({}));
				setError(d.detail || `HTTP ${r.status}`);
			}
			await load();
		} catch (e) {
			setError(String(e));
		} finally {
			setBusy(null);
		}
	};

	return (
		<div data-testid="processes-page" className="max-w-6xl mx-auto space-y-6">
			<header className="flex items-center justify-between">
				<div className="space-y-2">
					<div className="flex items-center gap-2 mb-1">
						<Cpu className="w-3.5 h-3.5 text-primary" />
						<span className="text-xs font-black uppercase tracking-[0.2em] text-muted-foreground">
							winops_process
						</span>
					</div>
					<h1 className="text-4xl font-black tracking-tighter leading-none italic">
						Processes
					</h1>
					<p className="text-xs text-muted-foreground">
						{total} processes · top {procs.length} by CPU · auto-refresh 5s
					</p>
				</div>
				<div className="flex items-center gap-3">
					<div className="relative">
						<Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
						<input
							value={search}
							onChange={(e) => setSearch(e.target.value)}
							placeholder="Filter by name..."
							className="h-10 pl-10 pr-4 rounded-xl bg-zinc-800 border border-zinc-600 text-sm text-zinc-100 placeholder:text-zinc-500 focus:outline-none focus:ring-2 focus:ring-primary/20"
						/>
					</div>
					<button
						onClick={() => load()}
						className="h-10 px-4 rounded-xl border border-white/10 text-xs font-bold uppercase tracking-widest text-muted-foreground hover:text-foreground hover:bg-white/5 transition-all flex items-center gap-2"
					>
						<RefreshCw className="w-3.5 h-3.5" /> Refresh
					</button>
				</div>
			</header>

			{error && (
				<div className="p-3 rounded-xl bg-rose-500/10 border border-rose-500/20 text-xs text-rose-400">
					{error}
				</div>
			)}

			<div className="glass-card rounded-3xl overflow-hidden">
				<div className="grid grid-cols-12 gap-4 px-6 py-3 text-[11px] font-bold uppercase tracking-widest text-muted-foreground border-b border-white/5">
					<span className="col-span-5">Process</span>
					<span className="col-span-2 text-right">PID</span>
					<span className="col-span-2 text-right">CPU</span>
					<span className="col-span-2 text-right">Memory</span>
					<span className="col-span-1" />
				</div>
				<div className="divide-y divide-white/5 max-h-[60vh] overflow-auto">
					{procs.map((p) => (
						<div
							key={p.pid}
							className="grid grid-cols-12 gap-4 items-center px-6 py-2.5 hover:bg-white/[0.03] transition-colors"
						>
							<span className="col-span-5 text-sm font-bold truncate">
								{p.name}
							</span>
							<span className="col-span-2 text-right text-xs font-mono text-muted-foreground">
								{p.pid}
							</span>
							<span className="col-span-2 text-right text-xs font-mono text-foreground">
								{p.cpu_percent.toFixed(1)}%
							</span>
							<span className="col-span-2 text-right text-xs font-mono text-foreground">
								{p.memory_percent.toFixed(1)}%
							</span>
							<span className="col-span-1 flex justify-end">
								<button
									onClick={() => kill(p.pid, p.name)}
									disabled={busy === p.pid}
									title={`Terminate ${p.name}`}
									className="p-1.5 rounded-lg border border-white/10 text-muted-foreground hover:text-rose-400 hover:border-rose-500/30 disabled:opacity-40 transition-all"
								>
									<Skull className="w-3.5 h-3.5" />
								</button>
							</span>
						</div>
					))}
					{procs.length === 0 && (
						<div className="py-16 text-center text-xs text-muted-foreground">
							No processes match
						</div>
					)}
				</div>
			</div>
		</div>
	);
}
