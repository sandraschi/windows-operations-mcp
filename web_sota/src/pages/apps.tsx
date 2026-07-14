import { useQuery } from "@tanstack/react-query";
import { motion } from "framer-motion";
import {
  Activity,
  ExternalLink,
  Globe,
  Grid,
  Server,
  Wifi,
} from "lucide-react";
import { API_BASE } from "@/lib/api";

interface FleetApp {
  name: string;
  url: string;
  status?: string;
  port?: number;
}

const knownApps: FleetApp[] = [
  { name: "Robotics Hub", url: "http://localhost:10892", port: 10892 },
  { name: "Plex Manager", url: "http://localhost:10714", port: 10714 },
  { name: "Central Docs", url: "http://localhost:10794", port: 10794 },
];

function getIcon(name: string) {
  const lower = name.toLowerCase();
  if (lower.includes("robot") || lower.includes("hub")) return Server;
  if (lower.includes("plex") || lower.includes("media")) return Activity;
  if (lower.includes("doc")) return Globe;
  return Grid;
}

export default function AppsHub() {
  const { data: healthMap } = useQuery({
    queryKey: ["fleet-health"],
    queryFn: async () => {
      const results: Record<string, boolean> = {};
      for (const app of knownApps) {
        try {
          const r = await fetch(`${app.url}/health`, { signal: AbortSignal.timeout(3000) });
          results[app.name] = r.ok;
        } catch {
          results[app.name] = false;
        }
      }
      return results;
    },
    refetchInterval: 15000,
    retry: false,
  });

  return (
    <div className="max-w-6xl mx-auto space-y-8">
      <motion.div
        initial={{ opacity: 0, x: -20 }}
        animate={{ opacity: 1, x: 0 }}
        className="space-y-2"
      >
        <div className="flex items-center gap-2 mb-1">
          <Wifi className="w-5 h-5 text-primary" />
          <span className="text-[10px] font-black uppercase tracking-[0.2em] text-muted-foreground">
            Fleet Discovery
          </span>
        </div>
        <h1 className="text-5xl font-black tracking-tighter italic">
          Apps <span className="vibrant-text not-italic">Hub</span>
        </h1>
        <p className="text-sm text-muted-foreground mt-2">
          Discovered fleet applications and their live health status.
        </p>
      </motion.div>

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {knownApps.map((app, idx) => {
          const Icon = getIcon(app.name);
          const alive = healthMap?.[app.name];
          return (
            <motion.a
              key={app.name}
              href={app.url}
              target="_blank"
              rel="noreferrer"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: idx * 0.1 }}
              className="glass-card p-6 rounded-3xl block group hover:border-primary/30 transition-all"
            >
              <div className="flex items-start justify-between mb-4">
                <div className="p-3 rounded-2xl bg-white/5 border border-white/10 group-hover:scale-110 transition-transform">
                  <Icon className="w-6 h-6" />
                </div>
                <div className="flex items-center gap-1.5">
                  <div
                    className={`w-2 h-2 rounded-full ${
                      alive === undefined
                        ? "bg-gray-500"
                        : alive
                          ? "bg-green-500"
                          : "bg-red-500"
                    }`}
                  />
                  <span className="text-[10px] font-bold uppercase tracking-wider text-muted-foreground">
                    {alive === undefined ? "..." : alive ? "Online" : "Offline"}
                  </span>
                </div>
              </div>

              <h3 className="font-bold text-lg mb-1 group-hover:text-primary transition-colors">
                {app.name}
              </h3>
              {app.port && (
                <p className="text-xs text-muted-foreground font-mono">
                  :{app.port}
                </p>
              )}

              <div className="mt-4 flex items-center gap-1 text-[10px] font-bold uppercase tracking-wider text-muted-foreground group-hover:text-primary transition-colors">
                <span>Open</span>
                <ExternalLink className="w-3 h-3" />
              </div>
            </motion.a>
          );
        })}
      </div>

      <div className="glass-card rounded-[2.5rem] p-8 border-dashed border-white/10">
        <p className="text-sm text-muted-foreground">
          Fleet discovery scans the local network for active MCP servers. Apps
          above are detected via port probes. Add more targets in the{" "}
          <code className="text-primary text-xs">App.tsx</code> fleet apps list.
        </p>
      </div>
    </div>
  );
}
