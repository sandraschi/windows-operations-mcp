import { RefreshCw, ScrollText } from "lucide-react";
import { useCallback, useEffect, useState } from "react";
import { API_BASE } from "@/lib/api";

type LogEvent = {
	timestamp: string;
	id: number;
	source: string;
	level: string;
	message: string;
};

const LEVEL_STYLE: Record<string, string> = {
	Error: "bg-rose-500/10 text-rose-400 border-rose-500/20",
	Warning: "bg-amber-500/10 text-amber-400 border-amber-500/20",
	Info: "bg-blue-500/10 text-blue-400 border-blue-500/20",
	AuditSuccess: "bg-emerald-500/10 text-emerald-400 border-emerald-500/20",
	AuditFailure: "bg-rose-500/10 text-rose-400 border-rose-500/20",
};

export default function EventLogs() {
	const [channels, setChannels] = useState<string[]>([]);
	const [channel, setChannel] = useState("System");
	const [hours, setHours] = useState(24);
	const [events, setEvents] = useState<LogEvent[]>([]);
	const [error, setError] = useState("");

	const loadChannels = useCallback(async () => {
		try {
			const r = await fetch(API_BASE + "/api/eventlogs/channels");
			const d = await r.json();
			if (d.channels?.length) {
				setChannels(d.channels);
				if (!d.channels.includes(channel)) setChannel(d.channels[0]);
			}
		} catch {
			// backend may still be warming up — Refresh retries
		}
	}, [channel]);

	useEffect(() => {
		loadChannels();
	}, [loadChannels]);

	const load = useCallback(async () => {
		setError("");
		try {
			const r = await fetch(
				API_BASE +
					`/api/eventlogs?channel=${encodeURIComponent(channel)}&limit=100&hours=${hours}`,
			);
			const d = await r.json();
			if (!r.ok) {
				setError(d.detail || `HTTP ${r.status}`);
				return;
			}
			setEvents(d.events ?? []);
		} catch (e) {
			setError(String(e));
		}
	}, [channel, hours]);

	useEffect(() => {
		load();
	}, [load]);

	return (
		<div data-testid="eventlogs-page" className="max-w-6xl mx-auto space-y-6">
			<header className="flex items-center justify-between">
				<div className="space-y-2">
					<div className="flex items-center gap-2 mb-1">
						<ScrollText className="w-3.5 h-3.5 text-primary" />
						<span className="text-xs font-black uppercase tracking-[0.2em] text-muted-foreground">
							winops_evtlog
						</span>
					</div>
					<h1 className="text-4xl font-black tracking-tighter leading-none italic">
						Event Logs
					</h1>
				</div>
				<div className="flex items-center gap-3">
					<select
						className="h-10 rounded-xl bg-zinc-800 text-zinc-100 border border-zinc-600 px-3 text-sm max-w-64"
						value={channel}
						onChange={(e) => setChannel(e.target.value)}
					>
						{channels.map((c) => (
							<option key={c} value={c}>
								{c}
							</option>
						))}
					</select>
					<select
						className="h-10 rounded-xl bg-zinc-800 text-zinc-100 border border-zinc-600 px-3 text-sm"
						value={hours}
						onChange={(e) => setHours(Number(e.target.value))}
					>
						<option value="1">Last hour</option>
						<option value="6">Last 6 hours</option>
						<option value="24">Last 24 hours</option>
						<option value="72">Last 3 days</option>
						<option value="168">Last 7 days</option>
					</select>
					<button
						onClick={() => {
							load();
							loadChannels();
						}}
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
					{events.map((ev, i) => (
						<div
							key={`${ev.id}-${i}`}
							className="px-6 py-3 hover:bg-white/[0.03] transition-colors"
						>
							<div className="flex items-center gap-3">
								<span
									className={`px-2 py-0.5 rounded border text-[10px] font-bold uppercase tracking-wider shrink-0 ${
										LEVEL_STYLE[ev.level] ||
										"bg-zinc-500/10 text-zinc-400 border-zinc-500/20"
									}`}
								>
									{ev.level}
								</span>
								<span className="text-xs font-mono text-muted-foreground shrink-0">
									{ev.id}
								</span>
								<span className="text-xs text-muted-foreground font-mono truncate">
									{ev.source}
								</span>
								<span className="ml-auto text-[11px] text-muted-foreground/60 font-mono shrink-0">
									{ev.timestamp.replace("T", " ").slice(0, 19)}
								</span>
							</div>
							<p className="text-sm text-foreground/90 mt-1.5 leading-relaxed">
								{ev.message || (
									<span className="text-muted-foreground italic">
										(no message)
									</span>
								)}
							</p>
						</div>
					))}
					{events.length === 0 && !error && (
						<div className="py-16 text-center text-xs text-muted-foreground">
							No events in the selected window
						</div>
					)}
				</div>
			</div>
		</div>
	);
}
