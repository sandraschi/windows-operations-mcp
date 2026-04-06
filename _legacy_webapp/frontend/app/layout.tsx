import type { Metadata } from 'next';
import './globals.css';
import { Sidebar } from '@/components/Sidebar';

export const metadata: Metadata = {
  title: 'MCP Webapp',
  description: 'Standardized MCP Webapp V2',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark h-full">
      <body className="bg-zinc-950 text-zinc-100 h-full flex overflow-hidden">
        <Sidebar />
        <main className="flex-1 flex flex-col h-full overflow-hidden relative">
            <div className="flex-1 overflow-y-auto overflow-x-hidden">
                {children}
            </div>
        </main>
      </body>
    </html>
  );
}
