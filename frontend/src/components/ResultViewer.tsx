import React, { useState } from 'react';
import { Download, Layers, Sliders, Eye, FileCheck, Maximize2, RotateCcw, Sparkles } from 'lucide-react';
import { Button } from './ui/Button';
import { Badge } from './ui/Badge';
import { GlassCard } from './ui/GlassCard';

export interface ResultViewerProps {
  mediaType: 'image' | 'video';
  originalUrl: string;
  resultUrl: string;
  title?: string;
  metrics?: {
    fps: number;
    avgInferenceMs: number;
    classDistribution: Record<string, number>;
  };
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

export const ResultViewer: React.FC<ResultViewerProps> = ({
  mediaType,
  originalUrl,
  resultUrl,
  title = 'Perception Segmentation Result',
  metrics,
}) => {
  const [viewMode, setViewMode] = useState<'overlay' | 'side-by-side' | 'raw' | 'mask'>('overlay');
  const [opacity, setOpacity] = useState<number>(75);
  const [isFullscreen, setIsFullscreen] = useState<boolean>(false);

  const handleDownload = () => {
    const link = document.createElement('a');
    link.href = resultUrl;
    link.download = `segmented_output.${mediaType === 'image' ? 'jpg' : 'mp4'}`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const detectedClassCount = metrics?.classDistribution
    ? Object.keys(metrics.classDistribution).length
    : 0;

  return (
    <GlassCard hoverEffect glowColor="cyan" className={`p-6 space-y-6 ${isFullscreen ? 'fixed inset-4 z-50 overflow-y-auto bg-slate-950/95 border-cyan-500/40 shadow-2xl' : ''}`}>
      {/* Header Bar */}
      <div className="flex flex-wrap items-center justify-between gap-4 border-b border-slate-800 pb-4">
        <div className="flex items-center space-x-3">
          <div className="p-2 rounded-xl bg-cyan-500/10 border border-cyan-500/20 text-cyan-400">
            <Layers className="w-5 h-5" />
          </div>
          <div>
            <h3 className="font-bold text-lg text-slate-100 font-heading">{title}</h3>
            <p className="text-xs text-slate-400">DeepLabV3+ ASPP Multi-Class Inference Output</p>
          </div>
        </div>

        <div className="flex flex-wrap items-center gap-2">
          {mediaType === 'image' && (
            <div className="flex items-center bg-slate-900/80 p-1 rounded-xl border border-slate-800">
              <button
                onClick={() => setViewMode('overlay')}
                className={`px-3 py-1 rounded-lg text-xs font-semibold transition ${
                  viewMode === 'overlay' ? 'bg-cyan-500 text-white shadow-md' : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                Overlay
              </button>
              <button
                onClick={() => setViewMode('side-by-side')}
                className={`px-3 py-1 rounded-lg text-xs font-semibold transition ${
                  viewMode === 'side-by-side' ? 'bg-cyan-500 text-white shadow-md' : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                Side-by-Side
              </button>
              <button
                onClick={() => setViewMode('raw')}
                className={`px-3 py-1 rounded-lg text-xs font-semibold transition ${
                  viewMode === 'raw' ? 'bg-cyan-500 text-white shadow-md' : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                Raw Scene
              </button>
            </div>
          )}

          <Button
            variant="outline"
            size="sm"
            onClick={() => setIsFullscreen(!isFullscreen)}
            leftIcon={<Maximize2 className="w-3.5 h-3.5" />}
          >
            {isFullscreen ? 'Exit Fullscreen' : 'Fullscreen'}
          </Button>

          <Button
            variant="primary"
            size="sm"
            onClick={handleDownload}
            leftIcon={<Download className="w-3.5 h-3.5" />}
          >
            Download Result
          </Button>
        </div>
      </div>

      {/* Opacity Control Slider */}
      {mediaType === 'image' && viewMode === 'overlay' && (
        <div className="flex items-center space-x-4 bg-slate-900/70 p-3.5 rounded-xl border border-slate-800 text-xs">
          <Sliders className="w-4 h-4 text-cyan-400 shrink-0" />
          <span className="text-slate-300 font-semibold shrink-0">Segmentation Mask Opacity: {opacity}%</span>
          <input
            type="range"
            min="0"
            max="100"
            value={opacity}
            onChange={(e) => setOpacity(Number(e.target.value))}
            className="flex-1 accent-cyan-400 cursor-pointer h-1.5 bg-slate-800 rounded-lg"
          />
        </div>
      )}

      {/* Media Canvas Display Container */}
      <div className="relative overflow-hidden rounded-2xl bg-black border border-slate-800 min-h-[320px] max-h-[540px] flex items-center justify-center hud-scanline">
        {mediaType === 'video' ? (
          <video controls autoPlay loop className="w-full h-auto max-h-[520px] object-contain">
            <source src={resultUrl} type="video/mp4" />
            Your browser does not support HTML5 video playback.
          </video>
        ) : viewMode === 'side-by-side' ? (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3 w-full p-3">
            <div className="space-y-1.5">
              <span className="text-xs font-semibold text-slate-400 px-1 flex items-center gap-1">
                <span className="w-2 h-2 rounded-full bg-slate-500" /> Original Road Scene
              </span>
              <img src={originalUrl} alt="Original scene" className="w-full h-auto rounded-xl object-contain max-h-[440px] border border-slate-800" />
            </div>
            <div className="space-y-1.5">
              <span className="text-xs font-semibold text-cyan-400 px-1 flex items-center gap-1">
                <span className="w-2 h-2 rounded-full bg-cyan-400" /> DeepLabV3+ Segmented Classes
              </span>
              <img src={resultUrl} alt="Segmented mask" className="w-full h-auto rounded-xl object-contain max-h-[440px] border border-slate-800" />
            </div>
          </div>
        ) : (
          <div className="relative w-full flex justify-center">
            <img src={originalUrl} alt="Raw scene" className="w-full h-auto max-h-[520px] object-contain rounded-xl" />
            <img
              src={resultUrl}
              alt="Segmented mask"
              style={{ opacity: viewMode === 'raw' ? 0 : opacity / 100 }}
              className="absolute top-0 left-0 w-full h-full max-h-[520px] object-contain rounded-xl transition-opacity duration-150 pointer-events-none"
            />
          </div>
        )}
      </div>

      {/* Summary Stat Pills */}
      <div className="flex flex-wrap items-center justify-between gap-3 text-xs bg-slate-900/60 p-3 rounded-xl border border-slate-800">
        <div className="flex items-center space-x-2">
          <Badge variant="emerald" dot>Scene Successfully Segmented</Badge>
          <span className="text-slate-400">|</span>
          <span className="text-slate-300 font-semibold">{detectedClassCount} Semantic Classes Detected</span>
        </div>

        {metrics?.avgInferenceMs && (
          <span className="text-cyan-400 font-bold font-mono">
            Processing Latency: {metrics.avgInferenceMs.toFixed(1)} ms
          </span>
        )}
      </div>

      {/* Class Legend Breakdown */}
      {metrics?.classDistribution && Object.keys(metrics.classDistribution).length > 0 && (
        <div className="space-y-3 pt-2">
          <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Per-Class Pixel Distribution Breakdown</h4>
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-3">
            {Object.entries(metrics.classDistribution).map(([className, percentage]) => {
              const color = CLASS_COLORS[className.toLowerCase()] || '#94a3b8';
              const pctVal = Number(percentage);
              return (
                <div key={className} className="bg-slate-900/80 border border-slate-800 p-3 rounded-xl space-y-1.5">
                  <div className="flex items-center justify-between text-xs">
                    <span className="capitalize text-slate-200 font-semibold flex items-center gap-1.5">
                      <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: color }} />
                      {className}
                    </span>
                    <span className="text-cyan-400 font-bold font-mono">{pctVal.toFixed(1)}%</span>
                  </div>
                  <div className="w-full bg-slate-950 rounded-full h-1.5 overflow-hidden border border-slate-800/80">
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
  );
};
