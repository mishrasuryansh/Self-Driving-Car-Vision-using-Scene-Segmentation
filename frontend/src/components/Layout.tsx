import React from 'react';
import { NavBar } from './NavBar';
import { ShieldCheck, Cpu } from 'lucide-react';

interface LayoutProps {
  children: React.ReactNode;
}

export const Layout: React.FC<LayoutProps> = ({ children }) => {
  return (
    <div className="min-h-screen flex flex-col bg-[#070a12] text-slate-100 relative overflow-hidden font-sans">
      {/* Background Ambient Glow Lights */}
      <div className="fixed top-0 left-1/4 w-[500px] h-[500px] bg-cyan-500/10 rounded-full blur-[140px] pointer-events-none z-0" />
      <div className="fixed top-1/3 right-1/4 w-[600px] h-[600px] bg-purple-500/10 rounded-full blur-[160px] pointer-events-none z-0" />
      <div className="fixed bottom-0 left-1/3 w-[500px] h-[500px] bg-blue-500/10 rounded-full blur-[140px] pointer-events-none z-0" />

      {/* Subtle Background HUD Grid Overlay */}
      <div className="fixed inset-0 bg-[linear-gradient(to_right,#1e293b0f_1px,transparent_1px),linear-gradient(to_bottom,#1e293b0f_1px,transparent_1px)] bg-[size:4rem_4rem] pointer-events-none z-0" />

      <NavBar />

      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8 relative z-10">
        {children}
      </main>

      <footer className="border-t border-slate-800/80 bg-[#070a12]/90 backdrop-blur-md py-6 relative z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col md:flex-row items-center justify-between gap-4 text-xs text-slate-400">
          <div className="flex items-center space-x-2">
            <Cpu className="w-4 h-4 text-cyan-400" />
            <span className="font-semibold text-slate-300">
              Self-Driving Car Vision Platform
            </span>
            <span className="text-slate-600">|</span>
            <span>DeepLabV3+ ASPP Architecture</span>
          </div>

          <div className="flex items-center space-x-4">
            <span className="bg-slate-900 border border-slate-800 px-2.5 py-1 rounded-md text-[11px] text-slate-300">
              PSIT Kanpur B.Tech CSE Project
            </span>
            <span>&copy; 2026 Vision AI Lab. All rights reserved.</span>
          </div>
        </div>
      </footer>
    </div>
  );
};
