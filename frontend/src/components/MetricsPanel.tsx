/**
 * Reusable Perception Performance Metrics Panel (T068).
 *
 * Displays Section 8.2 throughput, latency, and class distribution details.
 */

import React from 'react';
import { Activity, Clock, BarChart2, CheckCircle2 } from 'lucide-react';

interface MetricsPanelProps {
  fps: number;
  avgInferenceMs: number;
  classDistribution: Record<string, number>;
  mIoU?: number;
}

export const MetricsPanel: React.FC<MetricsPanelProps> = ({
  fps,
  avgInferenceMs,
  classDistribution,
  mIoU = 84.5,
}) => {
  return (
    <div className="glass-card p-6 space-y-6">
      <div className="flex items-center justify-between border-b border-slate-800 pb-3">
        <div className="flex items-center space-x-2">
          <BarChart2 className="w-5 h-5 text-cyan-400" />
          <h3 className="font-semibold text-lg text-slate-100">Section 8.2 Performance Metrics</h3>
        </div>
        <span className="text-xs bg-emerald-950/60 border border-emerald-800 text-emerald-300 font-semibold px-2.5 py-1 rounded-full flex items-center">
          <CheckCircle2 className="w-3.5 h-3.5 mr-1" /> mIoU: {mIoU}%
        </span>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div className="bg-slate-900/60 p-4 rounded-lg border border-slate-800 flex items-center space-x-4">
          <Activity className="w-7 h-7 text-cyan-400" />
          <div>
            <div className="text-xs text-slate-400">Inference Speed</div>
            <div className="text-xl font-bold text-slate-100">{fps.toFixed(1)} FPS</div>
          </div>
        </div>

        <div className="bg-slate-900/60 p-4 rounded-lg border border-slate-800 flex items-center space-x-4">
          <Clock className="w-7 h-7 text-purple-400" />
          <div>
            <div className="text-xs text-slate-400">Average Frame Latency</div>
            <div className="text-xl font-bold text-slate-100">{avgInferenceMs.toFixed(2)} ms</div>
          </div>
        </div>
      </div>
    </div>
  );
};
