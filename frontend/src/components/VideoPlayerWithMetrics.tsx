import React from 'react';
import { Video, Activity, Clock, BarChart2, CheckCircle2 } from 'lucide-react';
import { JobDetails } from './JobStatusStepper';
import { GlassCard } from './ui/GlassCard';
import { Badge } from './ui/Badge';
import { StatCard } from './ui/StatCard';

interface VideoPlayerWithMetricsProps {
  job: JobDetails;
}

const CLASS_COLORS: Record<string, string> = {
  road: '#06b6d4',
  vehicle: '#3b82f6',
  sky: '#8b5cf6',
  vegetation: '#10b981',
  pedestrian: '#ef4444',
  building: '#f59e0b',
  sidewalk: '#ec4899',
  other: '#64748b',
};

export const VideoPlayerWithMetrics: React.FC<VideoPlayerWithMetricsProps> = ({ job }) => {
  const videoUrl = job.output_path || '';
  const metrics = job.metrics;

  return (
    <div className="space-y-6">
      {/* Video Player Card */}
      <GlassCard glowColor="purple" className="p-6 space-y-4">
        <div className="flex items-center justify-between border-b border-slate-800 pb-3">
          <div className="flex items-center space-x-2">
            <div className="p-2 rounded-xl bg-purple-500/10 border border-purple-500/20 text-purple-400">
              <Video className="w-5 h-5" />
            </div>
            <div>
              <h3 className="font-bold text-lg text-slate-100 font-heading">Segmented Output Video Stream</h3>
              <p className="text-xs text-slate-400">DeepLabV3+ Frame-by-Frame Inference Output</p>
            </div>
          </div>
          <Badge variant="emerald" dot>Live Perception Stream</Badge>
        </div>

        <div className="bg-black rounded-2xl overflow-hidden border border-slate-800 flex justify-center max-h-[500px] hud-scanline">
          {videoUrl ? (
            <video controls autoPlay loop className="w-full h-auto max-h-[500px] object-contain">
              <source src={videoUrl} type="video/mp4" />
              Your browser does not support HTML5 video playback.
            </video>
          ) : (
            <div className="p-12 text-slate-500 text-xs">Video output stream unavailable.</div>
          )}
        </div>
      </GlassCard>

      {/* Aggregate Metrics Panel */}
      {metrics && (
        <GlassCard glowColor="cyan" className="p-6 space-y-6">
          <div className="flex items-center space-x-2 border-b border-slate-800 pb-3">
            <div className="p-2 rounded-xl bg-cyan-500/10 border border-cyan-500/20 text-cyan-400">
              <BarChart2 className="w-5 h-5" />
            </div>
            <div>
              <h3 className="font-bold text-lg text-slate-100 font-heading">Aggregate Perception Metrics</h3>
              <p className="text-xs text-slate-400">Section 8.2 Throughput & Class Percentage Breakdown</p>
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <StatCard
              icon={<Activity className="w-6 h-6" />}
              label="Processing Throughput"
              value={`${metrics.fps.toFixed(1)} FPS`}
              subValue="Real-Time Target Achieved"
              accentColor="cyan"
            />
            <StatCard
              icon={<Clock className="w-6 h-6" />}
              label="Average Frame Latency"
              value={`${metrics.avgInferenceMs.toFixed(2)} ms`}
              subValue="Sub-50ms Frame SLA"
              accentColor="purple"
            />
          </div>

          {/* Class Breakdown Horizontal Bar Charts */}
          {metrics.classDistribution && Object.keys(metrics.classDistribution).length > 0 && (
            <div className="space-y-3 pt-2">
              <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Per-Class Pixel Distribution Breakdown</h4>
              <div className="space-y-3">
                {Object.entries(metrics.classDistribution).map(([className, pct]) => {
                  const color = CLASS_COLORS[className.toLowerCase()] || '#94a3b8';
                  const pctVal = Number(pct);
                  return (
                    <div key={className} className="space-y-1.5 bg-slate-900/60 p-3 rounded-xl border border-slate-800">
                      <div className="flex justify-between text-xs font-semibold">
                        <span className="capitalize text-slate-200 flex items-center gap-1.5">
                          <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: color }} />
                          {className}
                        </span>
                        <span className="text-cyan-400 font-bold font-mono">{pctVal.toFixed(1)}%</span>
                      </div>
                      <div className="w-full bg-slate-950 rounded-full h-2 overflow-hidden border border-slate-800">
                        <div
                          className="h-full rounded-full transition-all duration-300"
                          style={{ width: `${pctVal}%`, backgroundColor: color }}
                        />
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}
        </GlassCard>
      )}
    </div>
  );
};
