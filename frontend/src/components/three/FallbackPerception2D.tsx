import React from 'react';
import { Cpu, ShieldCheck, Activity, Layers } from 'lucide-react';

export const FallbackPerception2D: React.FC = () => {
  return (
    <div className="relative w-full h-[400px] lg:h-[480px] rounded-2xl glass-card overflow-hidden border border-cyan-500/20 flex flex-col items-center justify-center p-6 bg-gradient-to-b from-cyan-950/20 via-slate-900/60 to-purple-950/20">
      {/* Background Animated Radar Grid */}
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,_var(--tw-gradient-stops))] from-cyan-900/20 via-transparent to-transparent animate-pulse-subtle pointer-events-none" />

      {/* Futuristic Vehicle Perception Grid Diagram */}
      <div className="relative z-10 space-y-6 text-center max-w-sm">
        <div className="relative mx-auto w-28 h-28 flex items-center justify-center rounded-2xl bg-cyan-500/10 border border-cyan-400/30 shadow-[0_0_30px_rgba(6,182,212,0.2)]">
          <Cpu className="w-14 h-14 text-cyan-400 animate-pulse" />
          <div className="absolute -top-2 -right-2 bg-purple-500 text-white text-[10px] font-bold px-2 py-0.5 rounded-full border border-purple-400">
            FSD AI
          </div>
        </div>

        <div className="space-y-2">
          <h4 className="text-lg font-bold text-slate-100 font-heading">
            Autonomous Vision Perception
          </h4>
          <p className="text-xs text-slate-400">
            Real-time semantic scene understanding powered by DeepLabV3+ ASPP multi-scale features.
          </p>
        </div>

        {/* Floating Semantic Tags */}
        <div className="flex flex-wrap justify-center gap-2 text-[11px] font-semibold">
          <span className="px-2.5 py-1 rounded-md bg-cyan-950/80 text-cyan-300 border border-cyan-800/80 flex items-center gap-1">
            <span className="w-2 h-2 rounded-full bg-cyan-400" /> [Road: 48.2%]
          </span>
          <span className="px-2.5 py-1 rounded-md bg-blue-950/80 text-blue-300 border border-blue-800/80 flex items-center gap-1">
            <span className="w-2 h-2 rounded-full bg-blue-400" /> [Vehicle: 21.5%]
          </span>
          <span className="px-2.5 py-1 rounded-md bg-rose-950/80 text-rose-300 border border-rose-800/80 flex items-center gap-1">
            <span className="w-2 h-2 rounded-full bg-rose-400" /> [Pedestrian: 4.8%]
          </span>
          <span className="px-2.5 py-1 rounded-md bg-emerald-950/80 text-emerald-300 border border-emerald-800/80 flex items-center gap-1">
            <span className="w-2 h-2 rounded-full bg-emerald-400" /> [Vegetation: 14.1%]
          </span>
        </div>
      </div>
    </div>
  );
};
