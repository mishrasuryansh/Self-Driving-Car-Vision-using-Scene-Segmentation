import React from 'react';
import { Activity, Clock, BarChart2, CheckCircle2 } from 'lucide-react';
import { GlassCard } from './ui/GlassCard';
import { Badge } from './ui/Badge';
import { StatCard } from './ui/StatCard';

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
    <GlassCard glowColor="cyan" className="p-6 space-y-6">
      <div className="flex items-center justify-between border-b border-slate-800 pb-3">
        <div className="flex items-center space-x-2">
          <div className="p-2 rounded-xl bg-cyan-500/10 border border-cyan-500/20 text-cyan-400">
            <BarChart2 className="w-5 h-5" />
          </div>
          <div>
            <h3 className="font-bold text-lg text-slate-100 font-heading">Section 8.2 Performance Metrics</h3>
            <p className="text-xs text-slate-400">Inference Throughput & Benchmark Accuracy</p>
          </div>
        </div>
        <Badge variant="emerald" dot>mIoU: {mIoU}%</Badge>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <StatCard
          icon={<Activity className="w-6 h-6" />}
          label="Inference Speed"
          value={`${fps.toFixed(1)} FPS`}
          subValue="Real-Time Target"
          accentColor="cyan"
        />

        <StatCard
          icon={<Clock className="w-6 h-6" />}
          label="Average Frame Latency"
          value={`${avgInferenceMs.toFixed(2)} ms`}
          subValue="Sub-50ms SLA"
          accentColor="purple"
        />
      </div>
    </GlassCard>
  );
};
