import { useCallback, useEffect, useMemo, useState } from "react";
import { API_BASE } from "../lib/api";

type InboxItem = {
	key: string;
	section: "eventlog" | "backend" | "service";
	title: string;
	detail: string;
	level: string;
	timestamp: string;
};

type AckMap = Record<string, number>;

const ACK_KEY = "winops-inbox-ack-v1";

function loadAck(): AckMap {
	try {
		return JSON.parse(localStorage.getItem(ACK_KEY) || "{}");
	} catch {
		return {};
	}
}

const LEVEL_BADGE: Record<string, string> = {
	Error: "text-red-300 bg-red-950/50 border-red-800/60",
	Warning: "text-yellow-300 bg-yellow-950/40 border-yellow-800/60",
	ERROR: "text-red-300 bg-red-950/50 border-red-800/60",
	WARNING: "text-yellow-300 bg-yellow-950/40 border-yellow-800/60",
	stopped: "text-orange-300 bg-orange-950/40 border-orange-800/60",
};

export default function Inbox() {
	const [items, setItems] = useState<InboxItem[]>([]);
	const [loading, setLoading] = useState(true);
	const [error, setError] = useState("");
	const [search, setSearch] = useState("");
	const [section, setSection] = useState("");
	const [showAcked, setShowAcked] = useState(false);
	const [ack, setAck] = useState<AckMap>(loadAck);

	const fetchInbox = useCallback(async () => {
		setLoading(true);
		setError("");
		try {
			const [evRes, errRes, warnRes, svcRes] = await Promise.all([
				fetch(`${API_BASE}/api/eventlogs?channel=System&limit=100&hours=24`),
				fetch(`${API_BASE}/api/logs?level=ERROR&limit=100&sort=desc`),
				fetch(`${API_BASE}/api/logs?level=WARNING&limit=100&sort=desc`),
				fetch(
					`${API_BASE}/api/services?filter_status=stopped&include_system=false`,
				),
			]);
			if (!evRes.ok || !errRes.ok || !warnRes.ok || !svcRes.ok) {
				throw new Error(
					"backend returned " +
						[evRes.status, errRes.status, warnRes.status, svcRes.status].join(
							"/",
						),
				);
			}
			const [ev, errLogs, warnLogs, svc] = await Promise.all([
				evRes.json(),
				errRes.json(),
				warnRes.json(),
				svcRes.json(),
			]);
			const next: InboxItem[] = [];
			for (const e of (ev.events || []).filter(
				(x: any) => x.level === "Error" || x.level === "Warning",
			)) {
				next.push({
					key: `ev:${e.source}:${e.id}:${e.timestamp}`,
					section: "eventlog",
					title: `${e.source} — Event ${e.id} (${e.level})`,
					detail: e.message || "(no message text)",
					level: e.level,
					timestamp: e.timestamp,
				});
			}
			for (const e of [
				...(errLogs.entries || []),
				...(warnLogs.entries || []),
			]) {
				next.push({
					key: `log:${e.id}`,
					section: "backend",
					title: `[${e.kind || "server"}] ${e.level}`,
					detail: e.detail,
					level: e.level,
					timestamp: e.timestamp,
				});
			}
			for (const s of svc.services || []) {
				next.push({
					key: `svc:${s.name}`,
					section: "service",
					title: `${s.display_name || s.name} is stopped`,
					detail: `Service '${s.name}' is not running. Start it from the Services page if it should be up.`,
					level: "stopped",
					timestamp: "",
				});
			}
			next.sort((a, b) => (b.timestamp || "").localeCompare(a.timestamp || ""));
			setItems(next);
		} catch (e: any) {
			setError(e?.message || "Inbox fetch failed");
		} finally {
			setLoading(false);
		}
	}, []);

	useEffect(() => {
		fetchInbox();
	}, [fetchInbox]);

	const acknowledge = (key: string) => {
		setAck((prev) => {
			const map = { ...prev, [key]: Date.now() };
			try {
				localStorage.setItem(ACK_KEY, JSON.stringify(map));
			} catch {
				// storage full/blocked: ack lasts for this session only
			}
			return map;
		});
	};

	const visible = useMemo(() => {
		const q = search.toLowerCase();
		return items.filter((i) => {
			if (!showAcked && ack[i.key]) return false;
			if (section && i.section !== section) return false;
			if (q && !`${i.title} ${i.detail}`.toLowerCase().includes(q))
				return false;
			return true;
		});
	}, [items, search, section, showAcked, ack]);

	const openCount = items.filter((i) => !ack[i.key]).length;

	return (
		<div className="space-y-4" data-testid="inbox-page">
			<div className="flex flex-wrap items-center gap-3">
				<h2 className="text-lg font-bold text-slate-200 mr-2">Inbox</h2>
				<span className="text-sm text-slate-400" data-testid="inbox-count">
					{loading ? "Loading..." : `${openCount} open / ${items.length} total`}
				</span>

				<select
					data-testid="inbox-filter-section"
					className="h-8 rounded border border-slate-700 bg-slate-800 px-2 text-sm text-slate-300"
					value={section}
					onChange={(e) => setSection(e.target.value)}
				>
					<option value="">All sections</option>
					<option value="eventlog">Event log</option>
					<option value="backend">Backend logs</option>
					<option value="service">Stopped services</option>
				</select>

				<input
					data-testid="inbox-search"
					className="h-8 w-56 rounded border border-slate-700 bg-slate-800 px-2 text-sm text-slate-300 placeholder:text-slate-500"
					placeholder="Search the queue..."
					value={search}
					onChange={(e) => setSearch(e.target.value)}
				/>

				<label className="flex items-center gap-2 text-sm text-slate-400">
					<input
						type="checkbox"
						checked={showAcked}
						onChange={(e) => setShowAcked(e.target.checked)}
					/>
					Show acknowledged
				</label>

				<button
					data-testid="inbox-refresh"
					className="h-8 rounded border border-slate-700 px-3 text-sm text-slate-300 hover:bg-slate-800"
					onClick={fetchInbox}
				>
					Refresh
				</button>
			</div>

			{loading && (
				<div className="text-sm text-slate-400 py-12 text-center">
					Loading attention queue...
				</div>
			)}

			{!loading && error && (
				<div
					className="rounded-lg border border-red-800 bg-red-950/30 p-4"
					data-testid="inbox-error"
				>
					<p className="text-sm font-bold text-red-300">
						Inbox unavailable: {error}
					</p>
					<p className="text-sm text-slate-400 mt-1">
						Is the backend running on {API_BASE}? Start it with{" "}
						<span className="font-mono">just web</span> and retry.
					</p>
					<button
						className="mt-3 h-8 rounded border border-red-700 px-3 text-sm text-red-300 hover:bg-red-950/50"
						onClick={fetchInbox}
					>
						Retry
					</button>
				</div>
			)}

			{!loading && !error && visible.length === 0 && (
				<div
					className="rounded-lg border border-slate-800 bg-slate-950 p-12 text-center"
					data-testid="inbox-empty"
				>
					<p className="text-sm font-bold text-slate-300">
						Queue clear — nothing needs attention.
					</p>
					<p className="text-sm text-slate-500 mt-1">
						System event errors, backend warnings, and stopped services will
						appear here.
					</p>
				</div>
			)}

			<div className="space-y-2">
				{visible.map((i) => (
					<div
						key={i.key}
						className={`rounded-lg border border-slate-800 bg-slate-950 p-3 ${ack[i.key] ? "opacity-50" : ""}`}
					>
						<div className="flex items-center gap-2 flex-wrap">
							<span
								className={`rounded border px-2 py-0.5 text-sm font-bold ${LEVEL_BADGE[i.level] || "text-slate-300 bg-slate-900"}`}
							>
								{i.level}
							</span>
							<span className="text-sm font-bold text-slate-200">
								{i.title}
							</span>
							{i.timestamp && (
								<span className="text-sm text-slate-500 ml-auto">
									{i.timestamp.replace("T", " ").split(".")[0]}
								</span>
							)}
						</div>
						<p className="text-sm text-slate-400 mt-1 break-words">
							{i.detail}
						</p>
						{!ack[i.key] && (
							<button
								className="mt-2 h-7 rounded border border-slate-700 px-2 text-sm text-slate-400 hover:bg-slate-800"
								onClick={() => acknowledge(i.key)}
							>
								Acknowledge
							</button>
						)}
					</div>
				))}
			</div>
		</div>
	);
}
