import { useMutation } from "@tanstack/react-query";
import { AnimatePresence, motion } from "framer-motion";
import {
	Bot,
	Command,
	Download,
	Eraser,
	Loader2,
	Send,
	Sparkles,
	Terminal,
	User,
	Wifi,
	WifiOff,
} from "lucide-react";
import { useCallback, useEffect, useRef, useState } from "react";
import { cn } from "@/common/utils";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { ScrollArea } from "@/components/ui/scroll-area";
import { API_BASE } from "@/lib/api";

const LS_HISTORY = "winops-chat-history";
const LS_PERSONALITY = "winops-chat-personality";
const MAX_HISTORY = 100;

interface Message {
	id: string;
	role: "user" | "assistant";
	content: string;
}

const PERSONALITIES = [
	{
		id: "operator",
		label: "SysOp",
		prompt:
			"You are a Windows system operator. Be precise, authoritative, and security-conscious.",
	},
	{
		id: "debugger",
		label: "Debugger",
		prompt:
			"You are a debugging specialist. Focus on process analysis, error logs, and root cause detection.",
	},
	{
		id: "automator",
		label: "Automator",
		prompt:
			"You are an automation engineer. Design scripts, scheduled tasks, and repeatable operations.",
	},
	{ id: "custom", label: "Custom", prompt: "" },
];

const EXAMPLE_PROMPTS = [
	"List all high-CPU processes",
	"Check disk space on C:",
	"Show recent system errors",
	"Design a deployment workflow",
	"Kill a hung process by PID",
	"Check Windows Update status",
	"List running services",
	"Create a scheduled task",
	"Show network connections",
];

function loadHistory(): Message[] {
	try {
		const s = localStorage.getItem(LS_HISTORY);
		if (s) return JSON.parse(s);
	} catch {
		return [];
	}
	return [];
}

export default function Chat() {
	const [input, setInput] = useState("");
	const [messages, setMessages] = useState<Message[]>(() => {
		const saved = loadHistory();
		if (saved.length > 0) return saved;
		return [
			{
				id: "1",
				role: "assistant",
				content:
					"Windows Operations AI active. How can I assist with your system administration task?",
			},
		];
	});
	const [personality, setPersonality] = useState(
		() => localStorage.getItem(LS_PERSONALITY) || "operator",
	);
	const [backendOk, setBackendOk] = useState<boolean | null>(null);
	const scrollRef = useRef<HTMLDivElement>(null);

	useEffect(() => {
		try {
			localStorage.setItem(
				LS_HISTORY,
				JSON.stringify(messages.slice(-MAX_HISTORY)),
			);
		} catch {
			/* ignore */
		}
	}, [messages]);

	useEffect(() => {
		localStorage.setItem(LS_PERSONALITY, personality);
	}, [personality]);

	useEffect(() => {
		fetch(API_BASE + "/health")
			.then((r) => setBackendOk(r.ok))
			.catch(() => setBackendOk(false));
	}, []);

	const mutation = useMutation({
		mutationFn: (query: string) =>
			fetch(API_BASE + "/api/chat", {
				method: "POST",
				headers: { "Content-Type": "application/json" },
				body: JSON.stringify({ query }),
			}).then((res) => res.json()),
		onSuccess: (data) => {
			const botMsg: Message = {
				id: Date.now().toString(),
				role: "assistant",
				content: data.response || "Task acknowledged.",
			};
			setMessages((prev) => [...prev, botMsg]);
		},
	});

	const handleSubmit = useCallback(
		(e: React.FormEvent) => {
			e.preventDefault();
			if (!input.trim() || mutation.isPending) return;
			const userMsg: Message = {
				id: Date.now().toString(),
				role: "user",
				content: input.trim(),
			};
			setMessages((prev) => [...prev, userMsg]);
			setInput("");
			mutation.mutate(userMsg.content);
		},
		[input, mutation],
	);

	useEffect(() => {
		scrollRef.current?.scrollIntoView({ behavior: "smooth" });
	}, [messages]);

	const handleClear = useCallback(() => {
		setMessages([]);
		try {
			localStorage.removeItem(LS_HISTORY);
		} catch {
			/* ignore */
		}
	}, []);

	const handleExport = useCallback(() => {
		const text = messages
			.map((m) => `[${m.role.toUpperCase()}] ${m.content}`)
			.join("\n\n");
		const blob = new Blob([text], { type: "text/plain" });
		const url = URL.createObjectURL(blob);
		const a = document.createElement("a");
		a.href = url;
		a.download = `winops-chat-${new Date().toISOString().slice(0, 10)}.txt`;
		a.click();
		URL.revokeObjectURL(url);
	}, [messages]);

	return (
		<div
			data-testid="chat-page"
			className="flex flex-col h-[calc(100vh-12rem)] max-w-5xl mx-auto"
		>
			<div className="mb-8 flex items-end justify-between">
				<div>
					<div className="flex items-center gap-2 mb-2">
						<div className="p-1.5 rounded-lg bg-primary/20 text-primary">
							<Sparkles className="w-4 h-4" />
						</div>
						<span className="text-xs font-bold uppercase tracking-[0.2em] text-primary">
							Intelligence Layer
						</span>
					</div>
					<h1 className="text-4xl font-black tracking-tighter">
						AI Command Center
					</h1>
					<p className="text-muted-foreground mt-1 text-sm">
						Natural language orchestration for advanced system operations.
					</p>
				</div>
				<div className="flex items-center gap-2">
					<span className="text-xs uppercase tracking-wider text-muted-foreground font-mono bg-white/5 border border-white/10 px-2 py-0.5 rounded">
						skill:sysop
					</span>
					<select
						data-testid="personality-select"
						value={personality}
						onChange={(e) => setPersonality(e.target.value)}
						className="bg-zinc-800 text-xs text-zinc-100 border border-zinc-600 rounded px-2 py-1"
					>
						{PERSONALITIES.map((p) => (
							<option key={p.id} value={p.id}>
								{p.label}
							</option>
						))}
					</select>
					{backendOk === true && (
						<span className="flex items-center gap-1 text-xs text-emerald-400">
							<Wifi className="w-3 h-3" />
							Online
						</span>
					)}
					{backendOk === false && (
						<span className="flex items-center gap-1 text-xs text-red-400">
							<WifiOff className="w-3 h-3" />
							Offline
						</span>
					)}
					<div className="hidden md:flex items-center gap-2 px-3 py-1.5 rounded-lg bg-white/5 border border-white/10 text-xs font-mono text-muted-foreground">
						<Command className="w-3 h-3" />
						<span>CMD + K TO SEARCH</span>
					</div>
				</div>
			</div>

			<div
				data-testid="example-prompts"
				className="flex flex-wrap gap-1.5 mb-4"
			>
				{EXAMPLE_PROMPTS.map((p) => (
					<button
						key={p}
						onClick={() => setInput(p)}
						className="flex items-center gap-1 px-2.5 py-1 rounded-full text-xs border border-white/10 text-muted-foreground hover:text-foreground hover:border-primary/40 transition-colors bg-white/[0.02]"
					>
						<Sparkles className="w-2.5 h-2.5" />
						{p}
					</button>
				))}
			</div>

			<Card
				data-testid="chat-messages"
				className="flex-1 flex flex-col overflow-hidden glass border-white/5 shadow-2xl relative"
			>
				<div className="absolute inset-0 bg-gradient-to-b from-primary/5 to-transparent pointer-events-none" />

				<ScrollArea className="flex-1 p-6 lg:p-8">
					<div className="space-y-8">
						<AnimatePresence initial={false}>
							{messages.map((m) => (
								<motion.div
									key={m.id}
									initial={{ opacity: 0, y: 20, scale: 0.95 }}
									animate={{ opacity: 1, y: 0, scale: 1 }}
									className={cn(
										"flex gap-4 max-w-[85%]",
										m.role === "assistant"
											? "mr-auto"
											: "ml-auto flex-row-reverse",
									)}
								>
									<div
										className={cn(
											"w-8 h-8 rounded-lg flex items-center justify-center shrink-0 mt-1",
											m.role === "assistant"
												? "bg-primary text-white shadow-lg shadow-primary/20"
												: "bg-white/10 border border-white/10",
										)}
									>
										{m.role === "assistant" ? (
											<Bot size={18} />
										) : (
											<User size={18} />
										)}
									</div>
									<div
										className={cn(
											"relative group",
											m.role === "assistant" ? "text-left" : "text-right",
										)}
									>
										<div
											className={cn(
												"px-5 py-3 rounded-2xl text-sm leading-relaxed shadow-sm",
												m.role === "assistant"
													? "bg-white/5 border border-white/10 text-foreground rounded-tl-none"
													: "vibrant-gradient text-white rounded-tr-none",
											)}
										>
											{m.content}
										</div>
										<span className="text-[11px] text-muted-foreground mt-1.5 block uppercase tracking-widest font-bold opacity-0 group-hover:opacity-100 transition-opacity">
											{m.role === "assistant" ? "AI Response" : "User Authored"}
										</span>
									</div>
								</motion.div>
							))}
						</AnimatePresence>

						{mutation.isPending && (
							<motion.div
								initial={{ opacity: 0, y: 10 }}
								animate={{ opacity: 1, y: 0 }}
								className="flex gap-4 mr-auto animate-pulse"
							>
								<div className="w-8 h-8 rounded-lg bg-primary/20 text-primary flex items-center justify-center">
									<Bot size={18} />
								</div>
								<div className="px-5 py-3 rounded-2xl bg-white/5 border border-white/10 text-muted-foreground italic text-sm rounded-tl-none">
									Synchronizing with system bus...
								</div>
							</motion.div>
						)}
						<div ref={scrollRef} className="h-4" />
					</div>
				</ScrollArea>

				<div className="p-6 bg-white/[0.02] border-t border-white/5 backdrop-blur-md">
					<div className="flex gap-1 mb-2 max-w-4xl mx-auto">
						<Button
							data-testid="chat-export"
							size="icon"
							variant="ghost"
							onClick={handleExport}
							disabled={messages.length === 0}
							className="h-7 w-7 text-muted-foreground"
							title="Export"
						>
							<Download className="h-3.5 w-3.5" />
						</Button>
						<Button
							data-testid="chat-clear"
							size="icon"
							variant="ghost"
							onClick={handleClear}
							disabled={messages.length === 0}
							className="h-7 w-7 text-muted-foreground"
							title="Clear"
						>
							<Eraser className="h-3.5 w-3.5" />
						</Button>
					</div>
					<form
						onSubmit={handleSubmit}
						className="flex gap-3 relative max-w-4xl mx-auto"
					>
						<div className="absolute left-4 top-1/2 -translate-y-1/2 text-muted-foreground">
							<Terminal size={18} />
						</div>
						<Input
							data-testid="chat-input"
							value={input}
							onChange={(e) => setInput(e.target.value)}
							placeholder="E.g., list all high-CPU processes, or design a deployment workflow..."
							className="flex-1 bg-white/5 border-white/10 h-14 pl-12 pr-4 rounded-xl focus:ring-primary/50 transition-all text-base"
						/>
						<Button
							data-testid="chat-send"
							type="submit"
							disabled={mutation.isPending}
							className="h-14 px-8 rounded-xl vibrant-gradient border-none shadow-lg shadow-primary/20 hover:scale-[1.02] active:scale-95 transition-transform"
						>
							{mutation.isPending ? (
								<Loader2 className="w-5 h-5 animate-spin" />
							) : (
								<Send className="w-5 h-5" />
							)}
						</Button>
					</form>
					<p className="text-[11px] text-center text-muted-foreground mt-4 uppercase tracking-[0.2em] font-bold opacity-50">
						Operational logs are persisted to metadata.json
					</p>
				</div>
			</Card>
		</div>
	);
}
