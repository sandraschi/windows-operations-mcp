import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { AnimatePresence, motion } from "framer-motion";
import {
	Activity,
	Box,
	ExternalLink,
	Globe,
	LayoutDashboard,
	Settings as SettingsIcon,
	Terminal,
	Wrench,
	Zap,
} from "lucide-react";
import {
	Link,
	Route,
	BrowserRouter as Router,
	Routes,
	useLocation,
} from "react-router-dom";
import { cn } from "./common/utils";
import Chat from "./pages/chat";
import Dashboard from "./pages/dashboard";
import Settings from "./pages/settings";
import Tools from "./pages/tools";
import Workflows from "./pages/workflows";

const queryClient = new QueryClient();

function Sidebar() {
	const location = useLocation();

	const navItems = [
		{ name: "Dashboard", path: "/", icon: LayoutDashboard },
		{ name: "Workflows", path: "/workflows", icon: Zap },
		{ name: "Tools", path: "/tools", icon: Wrench },
		{ name: "Chat", path: "/chat", icon: Terminal },
		{ name: "Settings", path: "/settings", icon: SettingsIcon },
	];

	const fleetApps = [
		{ name: "Robotics Hub", url: "http://localhost:10892", icon: Box },
		{ name: "Plex Manager", url: "http://localhost:10714", icon: Activity },
		{ name: "Central Docs", url: "http://localhost:10794", icon: Globe },
	];

	return (
		<aside className="w-64 glass h-screen flex flex-col p-4 z-50 sticky top-0">
			<div className="flex items-center space-x-3 px-2 py-6 mb-6">
				<div className="w-10 h-10 vibrant-gradient rounded-xl flex items-center justify-center shadow-lg shadow-primary/20">
					<Activity className="w-6 h-6 text-white" />
				</div>
				<div>
					<h1 className="font-extrabold text-lg tracking-tight leading-none vibrant-text">
						Windows
					</h1>
					<p className="text-[10px] text-muted-foreground uppercase tracking-widest font-bold mt-1">
						Operations SOTA
					</p>
				</div>
			</div>

			<div className="flex-1 space-y-1">
				<p className="text-[10px] font-bold text-muted-foreground px-3 mb-2 uppercase tracking-widest">
					Main Menu
				</p>
				{navItems.map((item) => {
					const isActive = location.pathname === item.path;
					return (
						<Link
							key={item.path}
							to={item.path}
							className={cn(
								"relative flex items-center space-x-3 px-3 py-2.5 rounded-xl transition-all duration-300 group",
								isActive
									? "text-primary bg-primary/10 shadow-sm"
									: "text-muted-foreground hover:text-foreground hover:bg-white/5",
							)}
						>
							{isActive && (
								<motion.div
									layoutId="active-pill"
									className="absolute left-0 w-1 h-6 bg-primary rounded-r-full"
									transition={{ type: "spring", stiffness: 300, damping: 30 }}
								/>
							)}
							<item.icon
								className={cn(
									"w-5 h-5 transition-transform group-hover:scale-110",
									isActive && "text-primary",
								)}
							/>
							<span className="text-sm font-semibold">{item.name}</span>
						</Link>
					);
				})}
			</div>

			<div className="mt-auto space-y-4">
				<div className="p-3 bg-white/5 rounded-2xl border border-white/5">
					<p className="text-[10px] font-bold text-muted-foreground mb-3 uppercase tracking-widest flex items-center gap-1.5">
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

				<div className="flex items-center gap-3 px-3 py-4 border-t border-white/5">
					<div className="w-8 h-8 rounded-full bg-primary/20 border border-primary/50 flex items-center justify-center text-[10px] font-bold text-primary">
						SS
					</div>
					<div className="flex flex-col">
						<span className="text-xs font-bold leading-none">Sandra S.</span>
						<span className="text-[10px] text-muted-foreground mt-0.5">
							Administrator
						</span>
					</div>
				</div>
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
				<div className="flex items-center space-x-2 px-3 py-1.5 rounded-full bg-success/10 border border-success/20">
					<div className="w-2 h-2 rounded-full bg-success animate-pulse" />
					<span className="text-[10px] font-bold text-success uppercase tracking-wider">
						System Live
					</span>
				</div>

				<div className="flex items-center space-x-3 text-muted-foreground hover:text-foreground transition-colors cursor-pointer group">
					<div className="text-right">
						<p className="text-[10px] font-bold leading-none">Goliath-v2</p>
						<p className="text-[9px] mt-0.5 opacity-60">127.0.0.1:10748</p>
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
					<Route path="/workflows" element={<Workflows />} />
					<Route path="/tools" element={<Tools />} />
					<Route path="/chat" element={<Chat />} />
					<Route path="/settings" element={<Settings />} />
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

						<footer className="px-8 py-4 border-t border-white/5 text-[10px] text-muted-foreground flex justify-between items-center bg-[#020205]/40">
							<div className="flex items-center gap-4">
								<span>v0.3.0 PREVIEW</span>
								<span className="w-1 h-1 rounded-full bg-white/10" />
								<span>SOTA January 2026</span>
							</div>
							<div className="flex items-center gap-2">
								<Activity className="w-3 h-3 text-primary" />
								<span className="font-mono">LOCAL_LATENCY: 4ms</span>
							</div>
						</footer>
					</div>
				</div>
			</Router>
		</QueryClientProvider>
	);
}
