import { useQuery } from "@tanstack/react-query";
import { motion } from "framer-motion";
import {
	Archive,
	Box,
	ChevronRight,
	Cpu,
	Database,
	Search,
	Shield,
	Terminal,
	Wrench,
	Zap,
} from "lucide-react";
import { API_BASE } from "@/lib/api";
import { cn } from "@/common/utils";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";

const toolIcons: Record<string, any> = {
	process_management: Activity,
	system_management: Cpu,
	file_operations: Database,
	command_execution: Terminal,
	windows_services: Shield,
	archive_management: Archive,
	git_operations: Zap,
};

function ToolCard({ tool, idx }: { tool: string; idx: number }) {
	// Basic heuristic to pick an icon if not directly matched
	const Icon =
		toolIcons[Object.keys(toolIcons).find((k) => tool.includes(k)) || ""] ||
		Box;

	return (
		<motion.div
			initial={{ opacity: 0, x: -20 }}
			animate={{ opacity: 1, x: 0 }}
			transition={{ delay: 0.1 + idx * 0.05, duration: 0.4 }}
			className="glass-card group flex items-center gap-6 p-6 rounded-[2rem] cursor-pointer hover:border-primary/40"
		>
			<div className="w-14 h-14 rounded-2xl bg-white/5 border border-white/10 flex items-center justify-center transition-transform group-hover:scale-110 group-hover:rotate-6 duration-500">
				<Icon
					className={cn(
						"w-7 h-7 text-muted-foreground transition-colors group-hover:text-primary",
					)}
				/>
			</div>

			<div className="flex-1">
				<div className="flex items-center gap-3 mb-1">
					<h3 className="text-xl font-black tracking-tighter italic">{tool}</h3>
					<Badge
						variant="secondary"
						className="bg-white/5 border-white/5 text-xs font-bold tracking-widest uppercase"
					>
						MCP TOOL
					</Badge>
				</div>
				<div className="flex items-center gap-4">
					<p className="text-xs text-muted-foreground/60 font-medium tracking-tight">
						Authoritative Bridge Integration
					</p>
					<div className="w-1 h-1 rounded-full bg-muted/30" />
					<p className="text-xs font-mono text-primary/40 uppercase tracking-widest">
						windows_operations_mcp.core
					</p>
				</div>
			</div>

			<div className="flex items-center gap-4">
				<div className="flex -space-x-2">
					{[1, 2, 3].map((i) => (
						<div
							key={i}
							className="w-6 h-6 rounded-full border-2 border-background bg-muted-foreground/10 flex items-center justify-center text-[8px] font-bold text-muted-foreground"
						>
							IO
						</div>
					))}
				</div>
				<div className="w-10 h-10 rounded-full border border-white/10 flex items-center justify-center text-muted-foreground group-hover:text-primary group-hover:bg-primary/10 group-hover:border-primary/20 transition-all">
					<ChevronRight className="w-5 h-5 group-hover:translate-x-0.5 transition-transform" />
				</div>
			</div>
		</motion.div>
	);
}

export default function Tools() {
	const { data: tools, isLoading } = useQuery({
		queryKey: ["tools"],
		queryFn: () => fetch(API_BASE + "/api/tools").then((res) => res.json()),
	});

	return (
		<div className="max-w-5xl mx-auto space-y-10">
			<header className="flex flex-col md:flex-row md:items-end justify-between gap-6">
				<div className="space-y-2">
					<div className="flex items-center gap-2 mb-1">
						<Wrench className="w-3.5 h-3.5 text-primary" />
						<span className="text-xs font-black uppercase tracking-[0.2em] text-muted-foreground">
							Capabilities Inventory
						</span>
					</div>
					<h1 className="text-5xl font-black tracking-tighter leading-none italic">
						Tool <span className="vibrant-text not-italic">Registry</span>
					</h1>
				</div>

				<div className="relative group w-full md:w-80">
					<Search className="absolute left-4 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground group-focus-within:text-primary transition-colors" />
					<Input
						placeholder="Search system tools..."
						className="pl-12 h-14 bg-white/5 border-white/10 rounded-2xl focus-visible:ring-primary/20 transition-all font-medium text-sm"
					/>
				</div>
			</header>

			<div className="grid gap-4">
				{tools?.tools?.map((tool: string, idx: number) => (
					<ToolCard key={tool} tool={tool} idx={idx} />
				))}

				{(!tools?.tools || tools.tools.length === 0) && !isLoading && (
					<motion.div
						initial={{ opacity: 0, scale: 0.95 }}
						animate={{ opacity: 1, scale: 1 }}
						className="flex flex-col items-center justify-center py-32 glass-card rounded-[3rem] border-dashed"
					>
						<div className="w-20 h-20 rounded-3xl bg-white/5 border border-white/5 flex items-center justify-center mb-6">
							<Box className="w-10 h-10 text-muted-foreground/20" />
						</div>
						<h3 className="text-2xl font-black tracking-tighter mb-2 italic">
							Zero{" "}
							<span className="not-italic text-muted-foreground">Signals</span>
						</h3>
						<p className="text-sm text-muted-foreground max-w-xs text-center leading-relaxed">
							No authoritative tools were discovered on the current bridge.
							Check connection status.
						</p>
						<button className="mt-8 px-8 py-3 rounded-2xl bg-white/5 border border-white/10 text-xs font-black uppercase tracking-widest text-muted-foreground hover:text-primary hover:border-primary/40 transition-all">
							Force Discovery
						</button>
					</motion.div>
				)}

				{isLoading && (
					<div className="space-y-4">
						{[1, 2, 3, 4].map((i) => (
							<div
								key={i}
								className="h-28 glass-card rounded-[2rem] animate-pulse"
							/>
						))}
					</div>
				)}
			</div>
		</div>
	);
}

// Missing imports fix (Activity was used but not imported in my thought)
import { Activity } from "lucide-react";
