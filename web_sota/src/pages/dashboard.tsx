import { useQuery } from "@tanstack/react-query";
import { motion } from "framer-motion";
import {
	ArrowUpRight,
	ChevronRight,
	Cpu,
	Database,
	HardDrive,
	Monitor,
	Wrench,
} from "lucide-react";
import { Link } from "react-router-dom";
import { cn } from "@/common/utils";
import { Progress } from "@/components/ui/progress";
import { API_BASE } from "@/lib/api";

interface StatCardProps {
	title: string;
	value: string | number;
	subValue: string;
	icon: any;
	progress?: number;
	color: string;
	delay: number;
}

function StatCard({
	title,
	value,
	subValue,
	icon: Icon,
	progress,
	color,
	delay,
}: StatCardProps) {
	return (
		<motion.div
			initial={{ opacity: 0, y: 20 }}
			animate={{ opacity: 1, y: 0 }}
			transition={{ delay, duration: 0.5 }}
			data-testid={`kpi-${title.toLowerCase().replace(/\s+/g, "-")}`}
			className="glass-card p-6 rounded-3xl relative overflow-hidden group"
		>
			<div
				className={cn(
					"absolute top-0 right-0 w-32 h-32 blur-3xl opacity-10 transition-opacity group-hover:opacity-20",
					color,
				)}
			/>

			<div className="flex justify-between items-start mb-4">
				<div
					className={cn(
						"p-3 rounded-2xl bg-white/5 border border-white/10 group-hover:scale-110 transition-transform duration-500",
					)}
				>
					<Icon className="w-6 h-6 text-foreground/80" />
				</div>
				<ArrowUpRight className="w-4 h-4 text-muted-foreground opacity-0 group-hover:opacity-100 transition-all transform translate-y-1 group-hover:translate-y-0" />
			</div>

			<div className="space-y-1 mt-6">
				<p className="text-sm font-bold text-muted-foreground uppercase tracking-wider">
					{title}
				</p>
				<div className="flex items-baseline gap-2">
					<h3 className="text-3xl font-black tracking-tight">{value}</h3>
					{typeof progress === "number" && (
						<span className="text-xs font-bold px-1.5 py-0.5 rounded-md bg-white/5 border border-white/5">
							LIVE
						</span>
					)}
				</div>
				<p className="text-xs text-muted-foreground/60 font-medium">
					{subValue}
				</p>
			</div>

			{typeof progress === "number" && (
				<div className="mt-6 space-y-2">
					<div className="flex justify-between text-xs font-bold uppercase tracking-tighter">
						<span>Utilization</span>
						<span>{progress}%</span>
					</div>
					<Progress
						value={progress}
						className="h-1.5 bg-white/5"
						indicatorClassName={cn(
							"vibrant-gradient shadow-[0_0_10px_rgba(139,92,246,0.5)]",
						)}
					/>
				</div>
			)}
		</motion.div>
	);
}

export default function Dashboard() {
	const { data: stats } = useQuery({
		queryKey: ["system-stats"],
		queryFn: () =>
			fetch(API_BASE + "/api/system-stats").then((res) => res.json()),
		refetchInterval: 2000,
	});

	const { data: processes } = useQuery({
		queryKey: ["processes"],
		queryFn: () => fetch(API_BASE + "/api/processes").then((res) => res.json()),
		refetchInterval: 5000,
	});

	const { data: status } = useQuery({
		queryKey: ["status"],
		queryFn: () => fetch(API_BASE + "/api/status").then((res) => res.json()),
	});

	return (
		<div data-testid="dashboard" className="max-w-7xl mx-auto space-y-10">
			<header className="space-y-6">
				<motion.div
					initial={{ opacity: 0, x: -20 }}
					animate={{ opacity: 1, x: 0 }}
					transition={{ duration: 0.6 }}
					className="space-y-3"
				>
					<div className="flex items-center gap-2 mb-1">
						<div className="w-2 h-2 rounded-full bg-green-500 animate-pulse shadow-[0_0_8px_rgba(34,197,94,0.6)]" />
						<span className="text-xs font-black uppercase tracking-[0.2em] text-muted-foreground">
							Live system telemetry
						</span>
					</div>
					<h1 className="text-5xl font-black tracking-tighter leading-none italic">
						Windows <span className="vibrant-text not-italic">Operations</span>
					</h1>
					<p className="text-sm text-muted-foreground max-w-xl leading-relaxed">
						Monitor and manage this Windows machine: processes, services, event
						logs, registry, accounts, firewall, scheduled tasks, files,
						archives, environment variables, and more — exposed as MCP tools for
						Claude, Cursor, and other AI clients.
					</p>
					<div className="flex items-center gap-3 pt-2">
						<Link
							to="/tools"
							className="vibrant-gradient text-white font-bold py-3 px-6 rounded-2xl text-xs uppercase tracking-widest shadow-lg shadow-primary/20 hover:scale-[1.02] active:scale-95 transition-all"
						>
							Explore Tools
						</Link>
						<Link
							to="/chat"
							className="text-foreground font-bold py-3 px-6 rounded-2xl text-xs uppercase tracking-widest border border-white/10 hover:bg-white/5 transition-all"
						>
							Open Chat
						</Link>
					</div>
				</motion.div>
			</header>

			<section className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
				<StatCard
					title="CPU Load"
					value={`${stats?.cpu_percent ?? 0}%`}
					subValue="Processor utilization"
					icon={Cpu}
					progress={stats?.cpu_percent ?? 0}
					color="bg-violet-500"
					delay={0.1}
				/>
				<StatCard
					title="Memory"
					value={`${stats?.memory ? Math.round(stats.memory.percent) : 0}%`}
					subValue={`${stats?.memory ? (stats.memory.available / 1024 / 1024 / 1024).toFixed(1) : 0} GB free`}
					icon={Database}
					progress={stats?.memory ? Math.round(stats.memory.percent) : 0}
					color="bg-blue-500"
					delay={0.2}
				/>
				<StatCard
					title="Disk (C:)"
					value={`${stats?.disk ? Math.round(stats.disk.percent) : 0}%`}
					subValue="Main system drive"
					icon={HardDrive}
					progress={stats?.disk ? Math.round(stats.disk.percent) : 0}
					color="bg-emerald-500"
					delay={0.3}
				/>
				<StatCard
					title="Platform"
					value={status?.platform ?? "..."}
					subValue={`${status?.release ?? ""} · ${status?.host ?? ""}`}
					icon={Monitor}
					color="bg-rose-500"
					delay={0.4}
				/>
			</section>

			<motion.section
				initial={{ opacity: 0, y: 20 }}
				animate={{ opacity: 1, y: 0 }}
				transition={{ delay: 0.5, duration: 0.6 }}
				className="grid grid-cols-1 lg:grid-cols-3 gap-8"
			>
				<div className="lg:col-span-2 glass-card rounded-[2.5rem] p-8">
					<div className="flex justify-between items-center mb-8">
						<div>
							<h2 className="text-2xl font-black italic tracking-tight">
								Active <span className="not-italic opacity-50">Processes</span>
							</h2>
							<p className="text-xs text-muted-foreground font-medium mt-1">
								Top 10 by CPU, refreshed every 5 seconds
							</p>
						</div>
					</div>

					<div className="space-y-3">
						{processes?.processes?.map((proc: any, idx: number) => (
							<motion.div
								key={proc.pid}
								initial={{ opacity: 0, x: -10 }}
								animate={{ opacity: 1, x: 0 }}
								transition={{ delay: 0.6 + idx * 0.05 }}
								className="flex items-center justify-between p-4 rounded-2xl bg-white/5 border border-white/5 hover:border-white/10 hover:bg-white/[0.07] transition-all group cursor-pointer"
							>
								<div className="flex items-center gap-4">
									<div className="w-10 h-10 rounded-xl bg-white/5 flex items-center justify-center font-bold text-xs text-muted-foreground group-hover:text-primary transition-colors">
										{proc.name.charAt(0).toUpperCase()}
									</div>
									<div className="flex flex-col">
										<span className="font-bold text-sm">{proc.name}</span>
										<span className="text-xs text-muted-foreground font-mono">
											PID: {proc.pid}
										</span>
									</div>
								</div>
								<div className="flex items-center gap-8">
									<div className="flex flex-col items-end">
										<span className="text-xs font-black text-foreground group-hover:text-primary transition-colors">
											{Math.round(proc.cpu_percent)}%
										</span>
										<span className="text-xs text-muted-foreground font-bold uppercase tracking-tighter">
											CPU Load
										</span>
									</div>
									<div className="flex flex-col items-end w-20">
										<span className="text-xs font-bold text-foreground">
											{Math.round(proc.memory_percent)}%
										</span>
										<span className="text-xs text-muted-foreground font-bold uppercase tracking-tighter">
											Memory
										</span>
									</div>
									<ChevronRight className="w-4 h-4 text-muted-foreground opacity-0 group-hover:opacity-100 transition-all translate-x-2 group-hover:translate-x-0" />
								</div>
							</motion.div>
						))}
					</div>
				</div>

				<div className="space-y-6">
					<div className="glass-card rounded-[2.5rem] p-8">
						<Wrench className="w-8 h-8 text-primary mb-4" />
						<h3 className="text-xl font-bold tracking-tight mb-3">
							What this can do
						</h3>
						<ul className="space-y-2 mb-6">
							{[
								"Processes & performance monitoring",
								"Services, scheduled tasks, event logs",
								"Registry, environment variables, accounts",
								"Files, archives, firewall, network",
								"Command & PowerShell execution",
								"Docker container management",
							].map((item) => (
								<li
									key={item}
									className="flex items-center gap-2 text-xs text-muted-foreground"
								>
									<span className="w-1.5 h-1.5 rounded-full bg-primary shrink-0" />
									{item}
								</li>
							))}
						</ul>
						<Link
							to="/tools"
							className="w-full block text-center vibrant-gradient text-white font-bold py-3 px-6 rounded-2xl text-xs uppercase tracking-widest shadow-lg shadow-primary/20 hover:scale-[1.02] active:scale-95 transition-all"
						>
							Browse all tools
						</Link>
					</div>
				</div>
			</motion.section>
		</div>
	);
}
