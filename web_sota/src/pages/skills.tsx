import { useQuery } from "@tanstack/react-query";
import { motion } from "framer-motion";
import { BookOpen, ChevronRight, FileText, Lightbulb } from "lucide-react";
import { useState } from "react";
import { API_BASE } from "@/lib/api";

interface Skill {
  name: string;
  description: string;
  content?: string;
}

const builtinSkills: Skill[] = [
  { name: "windows-expert", description: "Windows system administration, registry, services, accounts, event logs, networking, permissions, automation, and performance monitoring." },
];

export default function SkillsPage() {
  const [selected, setSelected] = useState<string | null>(null);

  const { data: remoteSkills, isLoading } = useQuery({
    queryKey: ["skills"],
    queryFn: () =>
      fetch(API_BASE + "/api/skills")
        .then((r) => (r.ok ? r.json() : []))
        .catch(() => []),
    retry: false,
  });

  const allSkills = remoteSkills?.length ? remoteSkills : builtinSkills;
  const currentSkill = allSkills.find((s: Skill) => s.name === selected);

  return (
    <div className="max-w-5xl mx-auto space-y-8">
      <motion.div
        initial={{ opacity: 0, x: -20 }}
        animate={{ opacity: 1, x: 0 }}
        className="space-y-2"
      >
        <div className="flex items-center gap-2 mb-1">
          <Lightbulb className="w-5 h-5 text-primary" />
          <span className="text-[10px] font-black uppercase tracking-[0.2em] text-muted-foreground">
            Server Capabilities
          </span>
        </div>
        <h1 className="text-5xl font-black tracking-tighter italic">
          Skills <span className="vibrant-text not-italic">Directory</span>
        </h1>
        <p className="text-sm text-muted-foreground mt-2">
          Registered skill modules available on this MCP server.
        </p>
      </motion.div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-1 space-y-2">
          {allSkills.map((skill: Skill, idx: number) => (
            <motion.button
              key={skill.name}
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: idx * 0.05 }}
              onClick={() => setSelected(skill.name)}
              className={`w-full text-left p-4 rounded-2xl transition-all border ${
                selected === skill.name
                  ? "bg-primary/10 border-primary/30 text-primary"
                  : "bg-white/5 border-white/5 hover:border-white/10 hover:bg-white/[0.07]"
              }`}
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <FileText className="w-4 h-4 shrink-0" />
                  <span className="text-sm font-bold">{skill.name}</span>
                </div>
                <ChevronRight className="w-4 h-4 text-muted-foreground" />
              </div>
              <p className="text-xs text-muted-foreground mt-1 line-clamp-1">
                {skill.description}
              </p>
            </motion.button>
          ))}
        </div>

        <div className="lg:col-span-2">
          {currentSkill ? (
            <motion.div
              key={currentSkill.name}
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="glass-card rounded-[2.5rem] p-8"
            >
              <div className="flex items-center gap-3 mb-6">
                <BookOpen className="w-6 h-6 text-primary" />
                <h2 className="text-2xl font-bold">{currentSkill.name}</h2>
              </div>
              <div className="prose prose-invert prose-sm max-w-none text-muted-foreground leading-relaxed whitespace-pre-wrap">
                {currentSkill.content || currentSkill.description}
              </div>
            </motion.div>
          ) : (
            <div className="glass-card rounded-[2.5rem] p-8 flex items-center justify-center h-48">
              <p className="text-muted-foreground text-sm">
                Select a skill to view its contents.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
