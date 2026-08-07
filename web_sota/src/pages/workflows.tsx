import { useQuery } from "@tanstack/react-query";
import { motion } from "framer-motion";
import {
	Activity,
	CheckCircle2,
	ChevronRight,
	Clock,
	Play,
	Plus,
	Zap,
} from "lucide-react";
import { API_BASE } from "@/lib/api";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";

export default function Workflows() {
	const { data: workflows, isLoading } = useQuery({
		queryKey: ["workflows"],
		queryFn: () => fetch(API_BASE + "/api/workflows").then((res) => res.json()),
	});

	return (
		<div className="max-w-6xl mx-auto space-y-10">
			<header className="flex flex-col md:flex-row md:items-end justify-between gap-6">
				<div className="space-y-2">
					<div className="flex items-center gap-2 mb-1">
						<Zap className="w-3.5 h-3.5 text-primary" />
						<span className="text-xs font-black uppercase tracking-[0.2em] text-muted-foreground">
							Automation Engineering
						</span>
					</div>
					<h1 className="text-5xl font-black tracking-tighter leading-none italic">
						Mission <span className="vibrant-text not-italic">Logistics</span>
					</h1>
				</div>

				<Button className="h-14 px-8 rounded-2xl vibrant-gradient text-white font-bold text-xs uppercase tracking-widest shadow-lg shadow-primary/20 hover:scale-[1.02] active:scale-95 transition-all flex items-center gap-2 border-none">
					<Plus className="w-4 h-4" />
					Initialize Protocol
				</Button>
			</header>

			<div className="grid gap-6 md:grid-cols-2">
				{workflows?.workflows?.map((workflow: any, idx: number) => (
					<motion.div
						key={workflow.id}
						initial={{ opacity: 0, scale: 0.95 }}
						animate={{ opacity: 1, scale: 1 }}
						transition={{ delay: idx * 0.1, duration: 0.4 }}
						className="glass-card group p-8 rounded-[2.5rem] flex flex-col justify-between min-h-[300px]"
					>
						<div>
							<div className="flex justify-between items-start mb-6">
								<div className="p-4 rounded-2xl bg-white/5 border border-white/10 group-hover:bg-primary/10 group-hover:border-primary/20 transition-all duration-500">
									<Zap className="w-6 h-6 text-muted-foreground group-hover:text-primary transition-colors" />
								</div>
								<Badge
									variant="outline"
									className="bg-green-500/10 text-green-400 border-green-500/20 text-xs font-black tracking-widest px-3 py-1"
								>
									READY_TO_DEPLOY
								</Badge>
							</div>

							<h3 className="text-2xl font-black italic tracking-tighter mb-2 group-hover:vibrant-text transition-all duration-300">
								{workflow.name}
							</h3>
							<p className="text-xs text-muted-foreground/80 leading-relaxed max-w-sm">
								{workflow.description ||
									"Standardized system orchestration protocol for continuous Windows environment stability."}
							</p>
						</div>

						<div className="mt-8 space-y-6">
							<div className="flex items-center gap-6 text-xs font-bold text-muted-foreground uppercase tracking-widest">
								<div className="flex items-center gap-2">
									<Clock className="w-3.5 h-3.5 text-primary/60" />
									Weekly Sched.
								</div>
								<div className="flex items-center gap-2">
									<CheckCircle2 className="w-3.5 h-3.5 text-green-500/60" />
									Last Run: 2h ago
								</div>
							</div>

							<button className="w-full flex items-center justify-between p-4 rounded-2xl bg-white/5 border border-white/5 hover:bg-white/10 hover:border-white/20 transition-all group/btn group-hover:shadow-lg ">
								<span className="flex items-center gap-3">
									<Play className="w-4 h-4 text-primary" />
									<span className="text-xs font-black uppercase tracking-[0.2em] text-foreground">
										Execute Protocol
									</span>
								</span>
								<ChevronRight className="w-4 h-4 text-muted-foreground group-hover/btn:translate-x-1 transition-transform" />
							</button>
						</div>
					</motion.div>
				))}

				{(!workflows?.workflows || workflows.workflows.length === 0) &&
					!isLoading && (
						<div className="md:col-span-2 py-32 glass-card rounded-[3rem] border-dashed border-2 flex flex-col items-center justify-center text-center">
							<Activity className="w-12 h-12 text-muted-foreground/20 mb-6" />
							<h3 className="text-2xl font-black italic tracking-tighter opacity-50 uppercase">
								No Protocols Compiled
							</h3>
							<p className="text-xs text-muted-foreground mt-2 max-w-xs leading-relaxed font-medium">
								Create a new mission protocol to begin automated Windows
								orchestration.
							</p>
							<Button
								variant="outline"
								className="mt-8 rounded-xl border-white/10 text-xs font-black uppercase tracking-widest px-8"
							>
								Browse Templates
							</Button>
						</div>
					)}
			</div>
		</div>
	);
}

// Ensure Activity is imported in the code
