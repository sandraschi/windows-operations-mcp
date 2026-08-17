import { Play, RefreshCw, RotateCw, Server, Square } from "lucide-react";
import { useCallback, useEffect, useState } from "react";
import { API_BASE } from "@/lib/api";

type Service = {
	name: string;
	display_name: string;
	status: string;
};

const STATUS_STYLE: Record<string, string> = {
	running: "bg-emerald-500/10 text-emerald-400 border-emerald-500/20",
	stopped: "bg-zinc-500/10 text-zinc-400 border-zinc-500/20",
	starting: "bg-amber-500/10 text-amber-400 border-amber-500/20",
	stopping: "bg-amber-500/10 text-amber-400 border-amber-500/20",
	other: "bg-rose-500/10 text-rose-400 border-rose-500/20",
};

export default function Services() {
	const [services, setServices] = useState<Service[]>([]);
	const [filter, setFilter] = useState("");
	const [busy, setBusy] = useState<Record<string, boolean>>({});
	const [error, setError] = useState("");

	const load = useCallback(async () => {
		const q = new URLSearchParams();
		if (filter) q.set("filter_status", filter);
		try {
			const r = await fetch(API_BASE + `/api/services?${q}`);
			const d = await r.json();
			setServices(d.services ?? []);
		} catch {
			setServices([]);
		}
	}, [filter]);

	useEffect(() => {
		load();
	}, [load]);

	const act = async (name: string, action: string) => {
		setBusy((b) => ({ ...b, [name]: true }));
		setError("");
		try {
			const r = await fetch(
				API_BASE + `/api/services/${encodeURIComponent(name)}/action`,
				{
					method: "POST",
					headers: { "Content-Type": "application/json" },
					body: JSON.stringify({ action }),
				},
			);
			if (!r.ok) {
				const d = await r.json().catch(() => ({}));
				setError(d.detail || `HTTP ${r.status}`);
			}
			await load();
		} catch (e) {
			setError(String(e));
		} finally {
			setBusy((b) => ({ ...b, [name]: false }));
		}
	};

	return (
		<div data-testid="services-page" className="max-w-6xl mx-auto space-y-6">
			<header className="flex items-center justify-between">
				<div className="space-y-2">
					<div className="flex items-center gap-2 mb-1">
						<Server className="w-3.5 h-3.5 text-primary" />
						<span className="text-xs font-black uppercase tracking-[0.2em] text-muted-foreground">
							winops_svc
						</span>
					</div>
					<h1 className="text-4xl font-black tracking-tighter leading-none italic">
						Services
					</h1>
				</div>
				<div className="flex items-center gap-3">
					<select
						className="h-10 rounded-xl bg-zinc-800 text-zinc-100 border border-zinc-600 px-3 text-sm"
						value={filter}
						onChange={(e) => setFilter(e.target.value)}
					>
						<option value="">All services</option>
						<option value="running">Running</option>
						<option value="stopped">Stopped</option>
					</select>
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
				<div className="divide-y divide-white/5">
					{services.map((s) => (
						<div
							key={s.name}
							className="flex items-center justify-between gap-4 px-6 py-4 hover:bg-white/[0.03] transition-colors"
						>
							<div className="min-w-0">
								<p className="font-bold text-sm truncate">
									{s.display_name || s.name}
								</p>
								<p className="text-xs text-muted-foreground font-mono truncate">
									{s.name}
								</p>
							</div>
							<div className="flex items-center gap-3 shrink-0">
								<span
									className={`px-2.5 py-1 rounded-full border text-[11px] font-bold uppercase tracking-wider ${
										STATUS_STYLE[s.status] || STATUS_STYLE.other
									}`}
								>
									{s.status}
								</span>
								{s.status !== "running" && (
									<button
										onClick={() => act(s.name, "start")}
										disabled={busy[s.name]}
										title="Start"
										className="p-2 rounded-lg border border-white/10 text-muted-foreground hover:text-emerald-400 hover:border-emerald-500/30 disabled:opacity-40 transition-all"
									>
										<Play className="w-4 h-4" />
									</button>
								)}
								{s.status === "running" && (
									<button
										onClick={() => act(s.name, "stop")}
										disabled={busy[s.name]}
										title="Stop"
										className="p-2 rounded-lg border border-white/10 text-muted-foreground hover:text-rose-400 hover:border-rose-500/30 disabled:opacity-40 transition-all"
									>
										<Square className="w-4 h-4" />
									</button>
								)}
								<button
									onClick={() => act(s.name, "restart")}
									disabled={busy[s.name]}
									title="Restart"
									className="p-2 rounded-lg border border-white/10 text-muted-foreground hover:text-amber-400 hover:border-amber-500/30 disabled:opacity-40 transition-all"
								>
									<RotateCw className="w-4 h-4" />
								</button>
							</div>
						</div>
					))}
					{services.length === 0 && (
						<div className="py-16 text-center text-xs text-muted-foreground">
							No services found
						</div>
					)}
				</div>
			</div>
		</div>
	);
}
