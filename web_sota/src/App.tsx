import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { AnimatePresence, motion } from "framer-motion";
import {
	Activity,
	BookOpen,
	Box,
	ChevronLeft,
	ChevronRight,
	Cpu,
	ExternalLink,
	Globe,
	HelpCircle,
	LayoutDashboard,
	Moon,
	ScrollText,
	Search,
	Server,
	Settings as SettingsIcon,
	Sun,
	Terminal,
	Wrench,
	Zap,
} from "lucide-react";
import { useEffect, useState } from "react";
import {
	Link,
	Route,
	BrowserRouter as Router,
	Routes,
	useLocation,
} from "react-router-dom";
import { cn } from "./common/utils";
import { API_BASE } from "./lib/api";
import { useAppStore } from "./lib/store";
import AppsHub from "./pages/apps";
import Chat from "./pages/chat";
import Dashboard from "./pages/dashboard";
import EventLogs from "./pages/eventlogs";
import Help from "./pages/help";
import Logging from "./pages/Logging";
import Processes from "./pages/processes";
import Services from "./pages/services";
import Settings from "./pages/settings";
import SkillsPage from "./pages/skills";
import Tools from "./pages/tools";
import Workflows from "./pages/workflows";

const queryClient = new QueryClient();

function Sidebar() {
	const location = useLocation();
	const { sidebarCollapsed, toggleSidebar } = useAppStore();

	const navItems = [
		{ name: "Dashboard", path: "/", icon: LayoutDashboard },
		{ name: "Services", path: "/services", icon: Server },
		{ name: "Processes", path: "/processes", icon: Cpu },
		{ name: "Event Logs", path: "/eventlogs", icon: ScrollText },
		{ name: "Workflows", path: "/workflows", icon: Zap },
		{ name: "Tools", path: "/tools", icon: Wrench },
		{ name: "Skills", path: "/skills", icon: BookOpen },
		{ name: "Apps", path: "/apps", icon: Search },
		{ name: "Chat", path: "/chat", icon: Terminal },
		{ name: "Logs", path: "/logs", icon: Terminal },
		{ name: "Help", path: "/help", icon: HelpCircle },
		{ name: "Settings", path: "/settings", icon: SettingsIcon },
	];

	const fleetApps = [
		{ name: "Robotics Hub", url: "http://localhost:10892", icon: Box },
		{ name: "Plex Manager", url: "http://localhost:10740", icon: Activity },
		{ name: "Central Docs", url: "http://localhost:10794", icon: Globe },
	];

	return (
		<aside
			className={cn(
				"glass h-screen flex flex-col p-4 z-50 sticky top-0 transition-all duration-300",
				sidebarCollapsed ? "w-16" : "w-64",
			)}
		>
			<div
				className={cn(
					"flex items-center mb-6",
					sidebarCollapsed ? "justify-center px-0 py-6" : "space-x-3 px-2 py-6",
				)}
			>
				{sidebarCollapsed ? (
					<button
						onClick={toggleSidebar}
						className="w-10 h-10 vibrant-gradient rounded-xl flex items-center justify-center shadow-lg shadow-primary/20 hover:scale-105 transition-transform"
					>
						<ChevronRight className="w-5 h-5 text-white" />
					</button>
				) : (
					<>
						<div className="w-10 h-10 vibrant-gradient rounded-xl flex items-center justify-center shadow-lg shadow-primary/20 shrink-0">
							<Activity className="w-6 h-6 text-white" />
						</div>
						<div className="flex-1">
							<h1 className="font-extrabold text-lg tracking-tight leading-none vibrant-text">
								Windows
							</h1>
							<p className="text-xs text-muted-foreground uppercase tracking-widest font-bold mt-1">
								Operations
							</p>
						</div>
						<button
							onClick={toggleSidebar}
							className="text-muted-foreground hover:text-foreground transition-colors p-1 -mr-1"
						>
							<ChevronLeft className="w-4 h-4" />
						</button>
					</>
				)}
			</div>

			<div className="flex-1 space-y-1">
				{!sidebarCollapsed && (
					<p className="text-xs font-bold text-muted-foreground px-3 mb-2 uppercase tracking-widest">
						Main Menu
					</p>
				)}
				{navItems.map((item) => {
					const isActive = location.pathname === item.path;
					return (
						<Link
							key={item.path}
							to={item.path}
							className={cn(
								"relative flex items-center rounded-xl transition-all duration-300 group",
								sidebarCollapsed
									? "justify-center p-2.5"
									: "space-x-3 px-3 py-2.5",
								isActive
									? "text-primary bg-primary/10 shadow-sm"
									: "text-muted-foreground hover:text-foreground hover:bg-white/5",
							)}
							title={sidebarCollapsed ? item.name : undefined}
						>
							{isActive && !sidebarCollapsed && (
								<motion.div
									layoutId="active-pill"
									className="absolute left-0 w-1 h-6 bg-primary rounded-r-full"
									transition={{ type: "spring", stiffness: 300, damping: 30 }}
								/>
							)}
							<item.icon
								className={cn(
									"w-5 h-5 shrink-0 transition-transform group-hover:scale-110",
									isActive && "text-primary",
								)}
							/>
							{!sidebarCollapsed && (
								<span className="text-sm font-semibold">{item.name}</span>
							)}
						</Link>
					);
				})}
			</div>

			<div className="mt-auto space-y-4">
				{!sidebarCollapsed && (
					<div className="p-3 bg-white/5 rounded-2xl border border-white/5">
						<p className="text-xs font-bold text-muted-foreground mb-3 uppercase tracking-widest flex items-center gap-1.5">
							<Globe className="w-3 h-3" /> Fleet Discovery
						</p>
						<div className="space-y-1">
							{fleetApps.map((app) => (
								<a
									key={app.name}
									href={app.url}
									target="_blank"
									rel="noreferrer"
									className="flex items-center justify-between px-2 py-1.5 text-[11px] font-medium text-muted-foreground hover:text-primary transition-colors hover:bg-primary/5 rounded-lg group"
								>
									<span className="flex items-center gap-2">
										<app.icon className="w-3.5 h-3.5" />
										{app.name}
									</span>
									<ExternalLink className="w-3 h-3 opacity-0 group-hover:opacity-100 transition-opacity" />
								</a>
							))}
						</div>
					</div>
				)}

				{!sidebarCollapsed && (
					<div className="flex items-center gap-3 px-3 py-4 border-t border-white/5">
						<div className="w-8 h-8 rounded-full bg-primary/20 border border-primary/50 flex items-center justify-center text-xs font-bold text-primary">
							SS
						</div>
						<div className="flex flex-col">
							<span className="text-xs font-bold leading-none">Sandra S.</span>
							<span className="text-xs text-muted-foreground mt-0.5">
								Administrator
							</span>
						</div>
					</div>
				)}
			</div>
		</aside>
	);
}

function TopBar() {
	const location = useLocation();
	const pathParts = location.pathname.split("/").filter(Boolean);
	const pageTitle =
		pathParts.length > 0
			? pathParts[0].charAt(0).toUpperCase() + pathParts[0].slice(1)
			: "Dashboard";

	const [backendOk, setBackendOk] = useState<boolean | null>(null);

	useEffect(() => {
		let cancelled = false;
		const check = async () => {
			try {
				const r = await fetch(API_BASE + "/health", {
					signal: AbortSignal.timeout(3000),
				});
				if (!cancelled) setBackendOk(r.ok);
			} catch {
				if (!cancelled) setBackendOk(false);
			}
		};
		check();
		const iv = setInterval(check, 10_000);
		return () => {
			cancelled = true;
			clearInterval(iv);
		};
	}, []);

	const dotColor =
		backendOk === null
			? "bg-muted-foreground"
			: backendOk
				? "bg-success"
				: "bg-destructive";
	const dotLabel =
		backendOk === null
			? "Connecting..."
			: backendOk
				? "System Live"
				: "Backend Offline";

	// EXPERIMENTAL light mode (invert hack). Not fleet standard — see index.css.
	// Toggling `.dark` off the root flips the invert filter; persisted so the
	// choice survives reloads. Delete this + the CSS block to revert.
	const [light, setLight] = useState(() => {
		try {
			return localStorage.getItem("windows-ops-light-mode") === "1";
		} catch {
			return false;
		}
	});

	useEffect(() => {
		document.documentElement.classList.toggle("dark", !light);
		try {
			localStorage.setItem("windows-ops-light-mode", light ? "1" : "0");
		} catch {
			// ignore storage errors
		}
	}, [light]);

	return (
		<header className="h-16 border-b border-white/5 flex items-center justify-between px-8 sticky top-0 bg-[#020205]/80 backdrop-blur-md z-40">
			<div className="flex items-center space-x-4">
				<div className="flex items-center space-x-2 text-xs font-medium text-muted-foreground">
					<Globe className="w-3.5 h-3.5" />
					<span>Fleet</span>
					<span>/</span>
					<span className="text-foreground font-bold">{pageTitle}</span>
				</div>
			</div>

			<div className="flex items-center space-x-6">
				<button
					type="button"
					onClick={() => setLight((v) => !v)}
					className="p-2 rounded-lg text-muted-foreground hover:text-foreground hover:bg-white/5 transition-colors"
					title={
						light
							? "Switch to dark (experimental light mode)"
							: "Switch to light (experimental, ugly)"
					}
					aria-label="Toggle light mode (experimental)"
				>
					{light ? <Moon className="w-4 h-4" /> : <Sun className="w-4 h-4" />}
				</button>

				<div
					data-testid="backend-dot"
					className={`flex items-center space-x-2 px-3 py-1.5 rounded-full border ${
						backendOk === false
							? "bg-destructive/10 border-destructive/20"
							: "bg-success/10 border-success/20"
					}`}
				>
					<div
						className={`w-2 h-2 rounded-full ${dotColor} ${backendOk === null ? "animate-pulse" : ""}`}
					/>
					<span
						className={`text-xs font-bold uppercase tracking-wider ${
							backendOk === false ? "text-destructive" : "text-success"
						}`}
					>
						{dotLabel}
					</span>
				</div>

				<div className="flex items-center space-x-3 text-muted-foreground hover:text-foreground transition-colors cursor-pointer group">
					<div className="text-right">
						<p className="text-xs font-bold leading-none">Goliath-v2</p>
						<p className="text-[11px] mt-0.5 opacity-60">127.0.0.1:10748</p>
					</div>
				</div>
			</div>
		</header>
	);
}

function AnimatedRoutes() {
	const location = useLocation();
	return (
		<AnimatePresence mode="wait">
			<motion.div
				key={location.pathname}
				initial={{ opacity: 0, y: 10 }}
				animate={{ opacity: 1, y: 0 }}
				exit={{ opacity: 0, y: -10 }}
				transition={{ duration: 0.2 }}
				className="flex-1"
			>
				<Routes location={location}>
					<Route path="/" element={<Dashboard />} />
					<Route path="/services" element={<Services />} />
					<Route path="/processes" element={<Processes />} />
					<Route path="/eventlogs" element={<EventLogs />} />
					<Route path="/workflows" element={<Workflows />} />
					<Route path="/tools" element={<Tools />} />
					<Route path="/skills" element={<SkillsPage />} />
					<Route path="/apps" element={<AppsHub />} />
					<Route path="/chat" element={<Chat />} />
					<Route path="/help" element={<Help />} />
					<Route path="/settings" element={<Settings />} />
					<Route path="/logs" element={<Logging />} />
				</Routes>
			</motion.div>
		</AnimatePresence>
	);
}

export default function App() {
	return (
		<QueryClientProvider client={queryClient}>
			<Router>
				<div className="flex min-h-screen bg-[#020205] text-foreground font-sans selection:bg-primary/30">
					<Sidebar />
					<div className="flex-1 flex flex-col min-w-0">
						<TopBar />
						<main className="flex-1 overflow-x-hidden px-8 py-8">
							<AnimatedRoutes />
						</main>

						<footer className="px-8 py-4 border-t border-white/5 text-xs text-muted-foreground flex justify-between items-center bg-[#020205]/40">
							<div className="flex items-center gap-4">
								<span>v14.2.0</span>
								<span className="w-1 h-1 rounded-full bg-white/10" />
								<span>Windows Operations MCP</span>
							</div>
							<div className="flex items-center gap-2">
								<Activity className="w-3 h-3 text-primary" />
								<span className="font-mono">FastMCP 3.4</span>
							</div>
						</footer>
					</div>
				</div>
			</Router>
		</QueryClientProvider>
	);
}
