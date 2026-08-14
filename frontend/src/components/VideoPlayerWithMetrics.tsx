/**
 * Video Player with Real-Time Metrics & Class Breakdown Component (T067).
 *
 * Renders segmented video playback with Section 8.2 performance metrics
 * and class percentage bar charts.
 */

import React from 'react';
import { Video, Activity, Clock, BarChart2 } from 'lucide-react';
import { JobDetails } from './JobStatusStepper';

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
      {/* Video Player */}
      <div className="glass-card p-6 space-y-4">
        <div className="flex items-center space-x-2 border-b border-slate-800 pb-3">
          <Video className="w-5 h-5 text-purple-400" />
          <h3 className="font-semibold text-lg text-slate-100">Segmented Output Video Stream</h3>
        </div>

        <div className="bg-black rounded-lg overflow-hidden border border-slate-800 flex justify-center max-h-[500px]">
          {videoUrl ? (
            <video controls autoPlay loop className="w-full h-auto max-h-[500px] object-contain">
              <source src={videoUrl} type="video/mp4" />
              Your browser does not support HTML5 video playback.
            </video>
          ) : (
            <div className="p-12 text-slate-500 text-sm">Video output stream unavailable.</div>
          )}
        </div>
      </div>

      {/* Aggregate Metrics Panel (T067) */}
      {metrics && (
        <div className="glass-card p-6 space-y-6">
          <div className="flex items-center space-x-2 border-b border-slate-800 pb-3">
            <BarChart2 className="w-5 h-5 text-cyan-400" />
            <h3 className="font-semibold text-lg text-slate-100">Aggregate Perception Metrics</h3>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div className="bg-slate-900/60 p-4 rounded-lg border border-slate-800 flex items-center space-x-4">
              <Activity className="w-8 h-8 text-cyan-400" />
              <div>
                <div className="text-xs text-slate-400">Processing Throughput</div>
                <div className="text-2xl font-extrabold text-slate-100">{metrics.fps.toFixed(1)} FPS</div>
              </div>
            </div>

            <div className="bg-slate-900/60 p-4 rounded-lg border border-slate-800 flex items-center space-x-4">
              <Clock className="w-8 h-8 text-purple-400" />
              <div>
                <div className="text-xs text-slate-400">Average Frame Latency</div>
                <div className="text-2xl font-extrabold text-slate-100">{metrics.avgInferenceMs.toFixed(2)} ms</div>
              </div>
            </div>
          </div>

          {/* Class Breakdown Horizontal Bar Charts */}
          {metrics.classDistribution && Object.keys(metrics.classDistribution).length > 0 && (
            <div className="space-y-3 pt-2">
              <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Per-Class Pixel Distribution Breakdown</h4>
              <div className="space-y-2">
                {Object.entries(metrics.classDistribution).map(([className, pct]) => {
                  const color = CLASS_COLORS[className.toLowerCase()] || '#94a3b8';
                  return (
                    <div key={className} className="space-y-1">
                      <div className="flex justify-between text-xs font-medium">
                        <span className="capitalize text-slate-300">{className}</span>
                        <span className="text-cyan-400 font-bold">{pct.toFixed(1)}%</span>
                      </div>
                      <div className="w-full bg-slate-900 rounded-full h-2 overflow-hidden border border-slate-800">
                        <div
                          className="h-full rounded-full transition-all duration-300"
                          style={{ width: `${pct}%`, backgroundColor: color }}
                        />
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
