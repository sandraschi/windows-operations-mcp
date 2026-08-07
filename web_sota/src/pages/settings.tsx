import { useQuery } from "@tanstack/react-query";
import { motion } from "framer-motion";
import {
	Cpu,
	CpuIcon,
	Database,
	Globe,
	HardDrive,
	Info,
	Layers,
	Network,
	Server,
	ShieldCheck,
} from "lucide-react";
import { useEffect, useState } from "react";
import { cn } from "@/common/utils";
import { Badge } from "@/components/ui/badge";
import {
	Card,
	CardContent,
	CardDescription,
	CardHeader,
	CardTitle,
} from "@/components/ui/card";
import { API_BASE } from "@/lib/api";

function LLMProviderSelect() {
	const [providers, setProviders] = useState<
		Record<string, { name: string }[]>
	>({});
	const [selectedProvider, setSelectedProvider] = useState("ollama");
	const [selectedModel, setSelectedModel] = useState("");

	useEffect(() => {
		fetch(API_BASE + "/api/llm/providers")
			.then((r) => r.json())
			.then((d) => {
				setProviders(d);
				const savedP = localStorage.getItem("llm_provider") || "ollama";
				const savedM = localStorage.getItem("llm_model") || "";
				setSelectedProvider(savedP);
				const models = d[savedP === "ollama" ? "ollama" : "lm_studio"];
				if (models?.length)
					setSelectedModel(
						savedM && models.some((m: { name: string }) => m.name === savedM)
							? savedM
							: models[0].name,
					);
			})
			.catch(() => setProviders({ ollama: [{ name: "llama3.2:3b" }] }));
	}, []);

	const save = (p: string, m: string) => {
		localStorage.setItem("llm_provider", p);
		localStorage.setItem("llm_model", m);
	};

	const models =
		providers[selectedProvider === "ollama" ? "ollama" : "lm_studio"] || [];
	const dot = models.length > 0 ? "bg-success" : "bg-muted-foreground";

	return (
		<div className="space-y-3">
			<div className="flex items-center gap-2 mb-3">
				<div className={`w-2 h-2 rounded-full ${dot}`} />
				<span className="text-xs font-bold uppercase tracking-widest text-muted-foreground">
					{models.length > 0 ? `${selectedProvider} connected` : "no provider"}
				</span>
			</div>
			<select
				className="h-10 w-full rounded-xl bg-zinc-800 text-zinc-100 border border-zinc-600 px-3 text-sm"
				value={selectedProvider}
				onChange={(e) => {
					setSelectedProvider(e.target.value);
					save(e.target.value, "");
				}}
			>
				<option value="ollama">Ollama</option>
				<option value="lm_studio">LM Studio</option>
			</select>
			<select
				className="h-10 w-full rounded-xl bg-zinc-800 text-zinc-100 border border-zinc-600 px-3 text-sm"
				value={selectedModel}
				onChange={(e) => {
					setSelectedModel(e.target.value);
					save(selectedProvider, e.target.value);
				}}
			>
				{models.map((m) => (
					<option key={m.name} value={m.name}>
						{m.name}
					</option>
				))}
			</select>
			<p className="text-[11px] text-muted-foreground italic">
				Saved to browser storage. Used by AI tools and LLM chat.
			</p>
		</div>
	);
}

export default function Settings() {
	const { data: status } = useQuery({
		queryKey: ["status"],
		queryFn: () => fetch(API_BASE + "/api/status").then((res) => res.json()),
	});

	const configItems = [
		{
			label: "Frontend Node",
			value: "10749",
			status: "dev server",
			icon: Globe,
		},
		{
			label: "Backend Hub",
			value: "10748",
			status: status ? "online" : "offline",
			icon: Server,
		},
		{
			label: "Platform",
			value: status?.platform ?? "...",
			status: status ? "detected" : "unknown",
			icon: ShieldCheck,
		},
		{
			label: "Python",
			value: status?.python_version ?? "...",
			status: "runtime",
			icon: Activity,
		},
	];

	return (
		<div className="max-w-6xl mx-auto space-y-12 pb-20">
			<div className="flex items-center justify-between">
				<div>
					<h1 className="text-4xl font-black tracking-tight vibrant-text">
						System Manifest
					</h1>
					<p className="text-muted-foreground mt-2 text-sm max-w-md">
						Metadata orchestration and environmental synchronization for the
						Windows Operations ecosystem.
					</p>
				</div>
				<div className="flex items-center gap-2 px-4 py-2 rounded-full glass border-primary/20 backdrop-blur-xl">
					<div className="w-2 h-2 rounded-full bg-primary animate-ping" />
					<span className="text-xs font-bold uppercase tracking-widest text-primary">
						REAL-TIME SYNC
					</span>
				</div>
			</div>

			<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
				{configItems.map((item, i) => (
					<motion.div
						key={item.label}
						initial={{ opacity: 0, y: 20 }}
						animate={{ opacity: 1, y: 0 }}
						transition={{ delay: i * 0.1 }}
						className="glass-card p-6 flex flex-col items-center text-center space-y-4"
					>
						<div className="p-3 rounded-2xl bg-primary/10 text-primary border border-primary/20 group-hover:scale-110 transition-transform">
							<item.icon className="w-6 h-6" />
						</div>
						<div>
							<p className="text-xs font-black text-muted-foreground uppercase tracking-[0.2em]">
								{item.label}
							</p>
							<p className="text-xl font-bold mt-1 text-foreground leading-none">
								{item.value}
							</p>
						</div>
						<Badge
							variant="outline"
							className="bg-primary/5 text-primary border-primary/20 text-[11px] uppercase tracking-widest py-0"
						>
							{item.status}
						</Badge>
					</motion.div>
				))}
			</div>

			<div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
				<Card className="glass border-white/5 overflow-hidden">
					<CardHeader className="bg-white/5 border-b border-white/5">
						<div className="flex items-center gap-3">
							<Cpu className="w-5 h-5 text-primary" />
							<CardTitle className="text-lg">Local LLM</CardTitle>
						</div>
					</CardHeader>
					<CardContent className="p-6 space-y-4">
						<LLMProviderSelect />
					</CardContent>
				</Card>

				<Card className="lg:col-span-2 glass border-white/5 overflow-hidden group">
					<CardHeader className="border-b border-white/5 bg-white/[0.02] p-8">
						<div className="flex items-center gap-4">
							<div className="p-3 rounded-2xl vibrant-gradient text-white shadow-xl shadow-primary/20">
								<CpuIcon className="w-6 h-6" />
							</div>
							<div>
								<CardTitle className="text-2xl font-bold">
									Environment Registry
								</CardTitle>
								<CardDescription>
									Authoritative system metadata and build configurations.
								</CardDescription>
							</div>
						</div>
					</CardHeader>
					<CardContent className="p-8 space-y-8">
						<div className="grid grid-cols-1 md:grid-cols-2 gap-x-12 gap-y-8">
							<div className="space-y-4">
								<div className="flex items-center justify-between py-2 border-b border-white/5">
									<span className="text-sm font-semibold text-muted-foreground uppercase tracking-widest">
										Runtime Host
									</span>
									<span className="text-sm font-mono text-foreground font-bold">
										{status?.host ?? "..."}
									</span>
								</div>
								<div className="flex items-center justify-between py-2 border-b border-white/5">
									<span className="text-sm font-semibold text-muted-foreground uppercase tracking-widest">
										Python Runtime
									</span>
									<span className="text-sm font-mono text-foreground font-bold">
										{status?.python_version ?? "..."}
									</span>
								</div>
								<div className="flex items-center justify-between py-2 border-b border-white/5">
									<span className="text-sm font-semibold text-muted-foreground uppercase tracking-widest">
										FastMCP Core
									</span>
									<span className="text-sm font-mono text-primary font-bold">
										3.4.5
									</span>
								</div>
							</div>
							<div className="space-y-4">
								<div className="flex items-center justify-between py-2 border-b border-white/5">
									<span className="text-sm font-semibold text-muted-foreground uppercase tracking-widest">
										CSS Engine
									</span>
									<span className="text-sm font-mono text-foreground font-bold">
										TAILWIND_V3.4
									</span>
								</div>
								<div className="flex items-center justify-between py-2 border-b border-white/5">
									<span className="text-sm font-semibold text-muted-foreground uppercase tracking-widest">
										Vite Core
									</span>
									<span className="text-sm font-mono text-foreground font-bold">
										7.3.1
									</span>
								</div>
							</div>
						</div>

						<div className="p-6 rounded-2xl bg-white/5 border border-white/10 flex items-start gap-4">
							<div className="p-2 rounded-lg bg-primary/20 text-primary mt-1">
								<Layers className="w-4 h-4" />
							</div>
							<div>
								<h4 className="text-sm font-bold">Architecture Note</h4>
								<p className="text-xs text-muted-foreground mt-1 leading-relaxed">
									FastAPI bridge in front of a FastMCP 3.4 ASGI app. stdio
									transport for Claude Desktop / IDE clients; HTTP on
									127.0.0.1:10748 for the webapp (REST /api/*, MCP streamable at
									/mcp).
								</p>
							</div>
						</div>
					</CardContent>
				</Card>

				<div className="space-y-8">
					<Card className="glass border-white/5 overflow-hidden">
						<CardHeader className="bg-white/5 border-b border-white/5">
							<div className="flex items-center gap-3">
								<Network className="w-5 h-5 text-primary" />
								<CardTitle className="text-lg">Unified Bridge</CardTitle>
							</div>
						</CardHeader>
						<CardContent className="p-6">
							<div className="flex items-center gap-6 p-5 rounded-2xl bg-primary/5 border border-primary/10 relative overflow-hidden group">
								<div className="absolute top-0 right-0 w-24 h-24 vibrant-gradient opacity-10 blur-2xl group-hover:opacity-20 transition-opacity" />
								<div
									className={cn(
										"w-12 h-12 rounded-2xl flex items-center justify-center text-white shadow-lg",
										status
											? "vibrant-gradient shadow-primary/20"
											: "bg-destructive shadow-destructive/20",
									)}
								>
									<Cpu className={cn("w-6 h-6", status && "animate-pulse")} />
								</div>
								<div className="flex-1">
									<p className="text-sm font-black tracking-tight">
										FASTAPI U-BRIDGE
									</p>
									<p className="text-xs text-muted-foreground font-medium uppercase tracking-widest mt-1">
										{status
											? `Synced as ${status.user}`
											: "Service Disconnected"}
									</p>
								</div>
								{status && (
									<Badge className="vibrant-gradient border-none text-xs py-0">
										{status.mcp}
									</Badge>
								)}
							</div>
						</CardContent>
					</Card>

					<Card className="glass border-white/5 overflow-hidden">
						<CardHeader className="bg-white/5 border-b border-white/5">
							<div className="flex items-center gap-3">
								<Database className="w-5 h-5 text-muted-foreground" />
								<CardTitle className="text-lg">Data Integrity</CardTitle>
							</div>
						</CardHeader>
						<CardContent className="p-6 space-y-4">
							<div className="flex items-center justify-between p-3 rounded-xl bg-white/5 border border-white/5">
								<div className="flex items-center gap-3">
									<HardDrive className="w-4 h-4 text-muted-foreground" />
									<span className="text-xs font-bold uppercase tracking-widest">
										Log Ring Buffer
									</span>
								</div>
								<div className="w-2 h-2 rounded-full bg-success" />
							</div>
							<div className="flex items-center justify-between p-3 rounded-xl bg-white/5 border border-white/5">
								<div className="flex items-center gap-3">
									<Info className="w-4 h-4 text-muted-foreground" />
									<span className="text-xs font-bold uppercase tracking-widest">
										Structured Logging
									</span>
								</div>
								<div className="w-2 h-2 rounded-full bg-success" />
							</div>
							<p className="text-[11px] text-muted-foreground italic leading-tight text-center px-4">
								In-memory ring buffer, 5000 entries, backed by structlog. See
								the Logs page.
							</p>
						</CardContent>
					</Card>
				</div>
			</div>
		</div>
	);
}

import { Activity } from "lucide-react";
