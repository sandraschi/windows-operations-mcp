import {
	BookOpen,
	Box,
	Bug,
	Cpu,
	Globe,
	Server,
	Terminal,
	Wrench,
	Zap,
} from "lucide-react";
import { API_BASE } from "@/lib/api";

const sections = [
	{
		icon: Server,
		title: "Architecture",
		body: [
			"FastAPI bridge + FastMCP 3.4 server, dual transport.",
			"stdio: Claude Desktop / IDE clients (default).",
			"HTTP: uvicorn on 127.0.0.1:10748 — REST under /api/*, MCP streamable HTTP at /mcp.",
			"The webapp is a React + Vite SPA that talks to the backend REST API directly.",
		],
	},
	{
		icon: Cpu,
		title: "Ports",
		body: [
			"10748 — backend (FastAPI + MCP /mcp, /health, /api/*)",
			"10749 — frontend (Vite dev server only; proxies /api → 10748)",
			"11434 — Ollama (optional, LLM chat provider)",
			"1234 — LM Studio (optional, LLM chat provider)",
		],
	},
	{
		icon: Wrench,
		title: "Pages",
		body: [
			"Dashboard — live CPU/RAM/disk + top processes (2s/5s polling)",
			"Tools — dynamic tool registry via GET /api/tools",
			"Skills — skill list from GET /api/skills",
			"Apps — fleet app discovery, probes each app's /health",
			"Chat — LLM chat via POST /api/chat (uses selected provider/model)",
			"Logs — backend log ring buffer (5000 entries, filter/export/clear)",
			"Settings — backend status + local LLM provider/model selection",
		],
	},
	{
		icon: Zap,
		title: "Environment",
		body: [
			"LOG_LEVEL — DEBUG|INFO|WARNING|ERROR (default INFO)",
			"LOG_JSON — true for JSON log output",
			"ENVIRONMENT — development|production",
			"WINOPS_PREFAB_APPS — 0 disables Prefab UI tool registration",
			"MCP_TRANSPORT / MCP_PORT / MCP_HOST — HTTP mode settings",
		],
	},
	{
		icon: Bug,
		title: "Troubleshooting",
		body: [
			"Backend offline (red dot): start the backend, then the topbar recovers on the next poll.",
			"Health check: GET /health and GET /api/health both return 200 when up.",
			"No LLM models: start Ollama (11434) or LM Studio (1234); Settings re-probes on load.",
			"Empty Logs page: logs are captured from process start — entries appear as the backend runs.",
			"Dev proxy: /api is proxied by Vite; direct calls use API_BASE = backend port 10748.",
		],
	},
	{
		icon: Box,
		title: "Tool Surface",
		body: [
			"16 portmanteau namespaces: winops_cmd, winops_container, winops_archive, winops_json,",
			"winops_process, winops_svc, winops_sys, winops_evtlog, winops_perf, winops_acl,",
			"winops_accounts, winops_auto, winops_net, winops_env, winops_apps, winops_file.",
			"Agentic tools: agentic_system_hardening, autonomous_troubleshooter.",
			"Prefab cards: system_health_card, process_list_card.",
		],
	},
];

export default function Help() {
	return (
		<div className="max-w-4xl mx-auto space-y-10">
			<header className="space-y-2">
				<div className="flex items-center gap-2 mb-1">
					<BookOpen className="w-3.5 h-3.5 text-primary" />
					<span className="text-xs font-black uppercase tracking-[0.2em] text-muted-foreground">
						Reference
					</span>
				</div>
				<h1 className="text-5xl font-black tracking-tighter leading-none italic">
					Help <span className="vibrant-text not-italic">& Docs</span>
				</h1>
				<p className="text-sm text-muted-foreground mt-3 max-w-xl leading-relaxed">
					Windows Operations MCP v14.2.0 — FastMCP 3.4 server. Backend at{" "}
					<code className="text-primary font-mono text-xs">{API_BASE}</code>.
				</p>
			</header>

			<div className="grid gap-6">
				{sections.map((section) => (
					<div
						key={section.title}
						className="glass-card rounded-3xl p-6 flex gap-5 items-start"
					>
						<div className="w-11 h-11 shrink-0 rounded-2xl bg-primary/10 border border-primary/20 flex items-center justify-center">
							<section.icon className="w-5 h-5 text-primary" />
						</div>
						<div className="min-w-0">
							<h2 className="text-lg font-black tracking-tight mb-2">
								{section.title}
							</h2>
							<ul className="space-y-1.5">
								{section.body.map((line) => (
									<li
										key={line}
										className="text-xs text-muted-foreground leading-relaxed flex gap-2"
									>
										<span className="text-primary mt-1 shrink-0">
											<Terminal className="w-2.5 h-2.5" />
										</span>
										<span>{line}</span>
									</li>
								))}
							</ul>
						</div>
					</div>
				))}
			</div>

			<p className="text-xs text-muted-foreground/60 text-center pb-8">
				<Globe className="w-3 h-3 inline mr-1" />
				Fleet docs: mcp-central-docs/standards (SOTA webapp + tool design
				standards)
			</p>
		</div>
	);
}
