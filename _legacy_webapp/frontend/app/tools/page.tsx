'use client';

import { useState, useEffect } from 'react';
import { Terminal, Wrench, AlertTriangle } from 'lucide-react';

interface Tool {
  name: string;
  description: string;
  inputSchema: any;
}

export default function ToolsPage() {
  const [tools, setTools] = useState<Tool[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Attempt to fetch from backend API
    fetch('/api/tools') 
      .then(res => res.json())
      .then(data => {
        if (data.tools) setTools(data.tools);
        else if (data.error) setError(data.error);
        else setError('Unknown response format');
      })
      .catch(err => {
        console.error(err);
        setError('Failed to load tools. Is the backend running?');
      })
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="container mx-auto p-6 max-w-5xl">
      <header className="flex items-center gap-3 mb-8 pb-4 border-b border-zinc-800">
        <div className="bg-amber-900/30 p-2 rounded-lg border border-amber-900/50">
            <Wrench className="w-8 h-8 text-amber-500" />
        </div>
        <div>
            <h1 className="text-3xl font-bold bg-gradient-to-r from-amber-400 to-orange-400 bg-clip-text text-transparent">
            Available Tools
            </h1>
            <p className="text-zinc-400">Capabilities exposed by this MCP Server</p>
        </div>
      </header>

      {loading && (
        <div className="grid gap-4">
            {[1,2,3].map(i => (
                <div key={i} className="h-32 bg-zinc-900/50 animate-pulse rounded-xl border border-zinc-800" />
            ))}
        </div>
      )}
      
      {error && (
        <div className="p-4 bg-red-950/30 text-red-200 rounded-xl border border-red-900/50 flex items-center gap-3">
            <AlertTriangle className="w-5 h-5" />
            {error}
        </div>
      )}

      {!loading && !error && tools.length === 0 && (
         <div className="text-center py-20 text-zinc-500">
            No tools found.
         </div>
      )}

      <div className="grid gap-4">
        {tools.map((tool) => (
          <div key={tool.name} className="bg-zinc-900 border border-zinc-800 rounded-xl p-6 hover:border-zinc-700 transition-all hover:shadow-lg hover:shadow-black/50 group">
            <div className="flex items-start justify-between mb-3">
                <h3 className="text-lg font-mono font-bold text-zinc-100 flex items-center gap-2 group-hover:text-amber-400 transition-colors">
                    <Terminal className="w-4 h-4 text-zinc-500 group-hover:text-amber-500/50" />
                    {tool.name}
                </h3>
            </div>
            <p className="text-zinc-400 mb-6 text-sm leading-relaxed whitespace-pre-wrap">{tool.description}</p>
            {tool.inputSchema && (
                <div className="bg-zinc-950 rounded-lg border border-zinc-900 overflow-hidden">
                    <div className="px-3 py-1.5 bg-zinc-900/50 border-b border-zinc-900 text-[10px] font-mono text-zinc-500 uppercase tracking-wider">
                        Input Schema
                    </div>
                    <div className="p-3 overflow-x-auto">
                        <pre className="text-xs font-mono text-emerald-400/80">
                            {JSON.stringify(tool.inputSchema, null, 2)}
                        </pre>
                    </div>
                </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
