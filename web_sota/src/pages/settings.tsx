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
import { cn } from "@/common/utils";
import { Badge } from "@/components/ui/badge";
import {
	Card,
	CardContent,
	CardDescription,
	CardHeader,
	CardTitle,
} from "@/components/ui/card";

export default function Settings() {
	const { data: status } = useQuery({
		queryKey: ["status"],
		queryFn: () => fetch("/api/status").then((res) => res.json()),
	});

	const configItems = [
		{ label: "Frontend Node", value: "10749", status: "online", icon: Globe },
		{ label: "Backend Hub", value: "10748", status: "online", icon: Server },
		{
			label: "Standard",
			value: "January 2026 SOTA",
			status: "compliant",
			icon: ShieldCheck,
		},
		{ label: "Latency", value: "4ms", status: "optimized", icon: Activity },
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
					<span className="text-[10px] font-bold uppercase tracking-widest text-primary">
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
							<p className="text-[10px] font-black text-muted-foreground uppercase tracking-[0.2em]">
								{item.label}
							</p>
							<p className="text-xl font-bold mt-1 text-foreground leading-none">
								{item.value}
							</p>
						</div>
						<Badge
							variant="outline"
							className="bg-primary/5 text-primary border-primary/20 text-[9px] uppercase tracking-widest py-0"
						>
							{item.status}
						</Badge>
					</motion.div>
				))}
			</div>

			<div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
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
										Goliath-v2
									</span>
								</div>
								<div className="flex items-center justify-between py-2 border-b border-white/5">
									<span className="text-sm font-semibold text-muted-foreground uppercase tracking-widest">
										Node Version
									</span>
									<span className="text-sm font-mono text-foreground font-bold">
										22.1.0-STABLE
									</span>
								</div>
								<div className="flex items-center justify-between py-2 border-b border-white/5">
									<span className="text-sm font-semibold text-muted-foreground uppercase tracking-widest">
										FastMCP Core
									</span>
									<span className="text-sm font-mono text-primary font-bold">
										3.1.1
									</span>
								</div>
							</div>
							<div className="space-y-4">
								<div className="flex items-center justify-between py-2 border-b border-white/5">
									<span className="text-sm font-semibold text-muted-foreground uppercase tracking-widest">
										Build Target
									</span>
									<span className="text-sm font-mono text-foreground font-bold">
										ESNEXT-OPTIMIZED
									</span>
								</div>
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
									This instance is operating in **Composite Mode**, merging
									physical OS hooks with a virtual MCP container. All telemetry
									is aggregated via the FastAPI Unified Bridge.
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
									<p className="text-[10px] text-muted-foreground font-medium uppercase tracking-widest mt-1">
										{status
											? `Synced as ${status.user}`
											: "Service Disconnected"}
									</p>
								</div>
								{status && (
									<Badge className="vibrant-gradient border-none text-[10px] py-0">
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
										Metadata DB
									</span>
								</div>
								<div className="w-2 h-2 rounded-full bg-success" />
							</div>
							<div className="flex items-center justify-between p-3 rounded-xl bg-white/5 border border-white/5">
								<div className="flex items-center gap-3">
									<Info className="w-4 h-4 text-muted-foreground" />
									<span className="text-xs font-bold uppercase tracking-widest">
										Audit Logs
									</span>
								</div>
								<div className="w-2 h-2 rounded-full bg-success" />
							</div>
							<p className="text-[9px] text-muted-foreground italic leading-tight text-center px-4">
								Auto-compaction active. Retention period: 7 days.
							</p>
						</CardContent>
					</Card>
				</div>
			</div>
		</div>
	);
}

import { Activity } from "lucide-react";
