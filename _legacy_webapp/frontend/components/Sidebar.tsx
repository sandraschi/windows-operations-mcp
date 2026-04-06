'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Home, MessageSquare, Wrench, Grid, Settings, LayoutDashboard, Database, HardDrive, Monitor } from 'lucide-react';

export function Sidebar() {
  const pathname = usePathname();
  
  const isActive = (path: string) => pathname === path 
    ? 'bg-zinc-800/80 text-white shadow-sm border-zinc-700/50' 
    : 'text-zinc-400 hover:bg-zinc-800/50 hover:text-zinc-200 border-transparent';

  const linkClass = (path: string) => `flex items-center gap-3 p-3 rounded-lg border transition-all duration-200 ${isActive(path)}`;

  return (
    <aside className="w-64 border-r border-zinc-800 bg-zinc-950/50 backdrop-blur-xl flex flex-col h-full">
      <div className="p-6 border-b border-zinc-800/50">
        <div className="font-bold text-xl bg-gradient-to-r from-emerald-400 to-cyan-400 bg-clip-text text-transparent flex items-center gap-2">
            <Database className="w-6 h-6 text-emerald-500" />
            <span>MCP Server</span>
        </div>
        <div className="text-xs text-zinc-500 mt-1 font-mono">V2 Standardized</div>
      </div>
      
      <nav className="flex-1 p-4 flex flex-col gap-1 overflow-y-auto">
        <div className="text-xs font-semibold text-zinc-600 uppercase tracking-wider mb-2 px-3 mt-2">Platform</div>
        
        <Link href="/" className={linkClass('/')}>
            <LayoutDashboard className="w-5 h-5" />
            <span>Dashboard</span>
        </Link>
        <Link href="/chat" className={linkClass('/chat')}>
            <MessageSquare className="w-5 h-5" />
            <span>AI Chat</span>
        </Link>
        <Link href="/tools" className={linkClass('/tools')}>
            <Wrench className="w-5 h-5" />
            <span>Tools</span>
        </Link>

        <div className="text-xs font-semibold text-zinc-600 uppercase tracking-wider mb-2 px-3 mt-6">System</div>

        <Link href="/apps" className={linkClass('/apps')}>
            <Grid className="w-5 h-5" />
            <span>Our Apps</span>
        </Link>
        <Link href="/settings" className={linkClass('/settings')}>
            <Settings className="w-5 h-5" />
            <span>Settings</span>
        </Link>
      </nav>
      
      <div className="p-4 border-t border-zinc-800/50">
        <div className="text-[10px] text-zinc-600 text-center">
            Powered by Antigravity
        </div>
      </div>
    </aside>
  );
}
