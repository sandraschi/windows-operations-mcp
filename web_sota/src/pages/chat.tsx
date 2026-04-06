import { useState, useRef, useEffect } from 'react';
import { useMutation } from '@tanstack/react-query';
import { motion, AnimatePresence } from 'framer-motion';
import { Send, Terminal, User, Bot, Loader2, Sparkles, Command } from 'lucide-react';
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { ScrollArea } from "@/components/ui/scroll-area";
import { cn } from "@/common/utils";

interface Message {
    id: string;
    role: 'user' | 'assistant';
    content: string;
}

export default function Chat() {
    const [input, setInput] = useState('');
    const [messages, setMessages] = useState<Message[]>([
        { id: '1', role: 'assistant', content: 'Windows Operations AI active. How can I assist with your system administration task?' }
    ]);
    const scrollRef = useRef<HTMLDivElement>(null);

    const mutation = useMutation({
        mutationFn: (query: string) =>
            fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ query })
            }).then(res => res.json()),
        onSuccess: (data) => {
            const botMsg: Message = { 
                id: Date.now().toString(), 
                role: 'assistant', 
                content: data.response || 'Task acknowledged.' 
            };
            setMessages(prev => [...prev, botMsg]);
        }
    });

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        if (!input.trim() || mutation.isPending) return;

        const userMsg: Message = { 
            id: Date.now().toString(), 
            role: 'user', 
            content: input.trim() 
        };
        setMessages(prev => [...prev, userMsg]);
        setInput('');
        mutation.mutate(userMsg.content);
    };

    useEffect(() => {
        if (scrollRef.current) {
            scrollRef.current.scrollIntoView({ behavior: 'smooth' });
        }
    }, [messages]);

    return (
        <div className="flex flex-col h-[calc(100vh-12rem)] max-w-5xl mx-auto">
            <div className="mb-8 flex items-end justify-between">
                <div>
                    <div className="flex items-center gap-2 mb-2">
                        <div className="p-1.5 rounded-lg bg-primary/20 text-primary">
                            <Sparkles className="w-4 h-4" />
                        </div>
                        <span className="text-[10px] font-bold uppercase tracking-[0.2em] text-primary">Intelligence Layer</span>
                    </div>
                    <h1 className="text-4xl font-black tracking-tighter">AI Command Center</h1>
                    <p className="text-muted-foreground mt-1 text-sm">Natural language orchestration for advanced system operations.</p>
                </div>
                <div className="hidden md:flex items-center gap-2 px-3 py-1.5 rounded-lg bg-white/5 border border-white/10 text-[10px] font-mono text-muted-foreground">
                    <Command className="w-3 h-3" />
                    <span>CMD + K TO SEARCH</span>
                </div>
            </div>

            <Card className="flex-1 flex flex-col overflow-hidden glass border-white/5 shadow-2xl relative">
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
                                        m.role === 'assistant' ? "mr-auto" : "ml-auto flex-row-reverse"
                                    )}
                                >
                                    <div className={cn(
                                        "w-8 h-8 rounded-lg flex items-center justify-center shrink-0 mt-1",
                                        m.role === 'assistant' ? "bg-primary text-white shadow-lg shadow-primary/20" : "bg-white/10 border border-white/10"
                                    )}>
                                        {m.role === 'assistant' ? <Bot size={18} /> : <User size={18} />}
                                    </div>
                                    <div className={cn(
                                        "relative group",
                                        m.role === 'assistant' ? "text-left" : "text-right"
                                    )}>
                                        <div className={cn(
                                            "px-5 py-3 rounded-2xl text-sm leading-relaxed shadow-sm",
                                            m.role === 'assistant' 
                                                ? "bg-white/5 border border-white/10 text-foreground rounded-tl-none" 
                                                : "vibrant-gradient text-white rounded-tr-none"
                                        )}>
                                            {m.content}
                                        </div>
                                        <span className="text-[9px] text-muted-foreground mt-1.5 block uppercase tracking-widest font-bold opacity-0 group-hover:opacity-100 transition-opacity">
                                            {m.role === 'assistant' ? 'AI Response' : 'User Authored'}
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
                    <form onSubmit={handleSubmit} className="flex gap-3 relative max-w-4xl mx-auto">
                        <div className="absolute left-4 top-1/2 -translate-y-1/2 text-muted-foreground">
                            <Terminal size={18} />
                        </div>
                        <Input
                            value={input}
                            onChange={(e) => setInput(e.target.value)}
                            placeholder="E.g., list all high-CPU processes, or design a deployment workflow..."
                            className="flex-1 bg-white/5 border-white/10 h-14 pl-12 pr-4 rounded-xl focus:ring-primary/50 transition-all text-base"
                        />
                        <Button 
                            type="submit" 
                            disabled={mutation.isPending}
                            className="h-14 px-8 rounded-xl vibrant-gradient border-none shadow-lg shadow-primary/20 hover:scale-[1.02] active:scale-95 transition-transform"
                        >
                            {mutation.isPending ? <Loader2 className="w-5 h-5 animate-spin" /> : <Send className="w-5 h-5" />}
                        </Button>
                    </form>
                    <p className="text-[9px] text-center text-muted-foreground mt-4 uppercase tracking-[0.2em] font-bold opacity-50">
                        Operational logs are persisted to metadata.json
                    </p>
                </div>
            </Card>
        </div>
    );
}
