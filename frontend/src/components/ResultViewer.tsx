/**
 * Shared Result Viewer Component (T071).
 *
 * Provides a unified before/after slider, side-by-side comparison,
 * image/video media playback, class distribution legend, and artifact download button.
 */

import React, { useState } from 'react';
import { Download, Layers, Sliders, Eye, FileCheck } from 'lucide-react';

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
  title = 'Segmentation Result',
  metrics,
}) => {
  const [viewMode, setViewMode] = useState<'overlay' | 'side-by-side' | 'raw' | 'mask'>('overlay');
  const [opacity, setOpacity] = useState<number>(75);

  const handleDownload = () => {
    const link = document.createElement('a');
    link.href = resultUrl;
    link.download = `segmented_output.${mediaType === 'image' ? 'jpg' : 'mp4'}`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="glass-card p-6 space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-4 border-b border-slate-800 pb-4">
        <div className="flex items-center space-x-2">
          <Layers className="w-5 h-5 text-cyan-400" />
          <h3 className="font-semibold text-lg text-slate-100">{title}</h3>
        </div>

        <div className="flex flex-wrap items-center gap-2">
          {mediaType === 'image' && (
            <>
              <button
                onClick={() => setViewMode('overlay')}
                className={`px-3 py-1.5 rounded-lg text-xs font-medium transition ${
                  viewMode === 'overlay' ? 'bg-cyan-500 text-white font-bold' : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
                }`}
              >
                Overlay
              </button>
              <button
                onClick={() => setViewMode('side-by-side')}
                className={`px-3 py-1.5 rounded-lg text-xs font-medium transition ${
                  viewMode === 'side-by-side' ? 'bg-cyan-500 text-white font-bold' : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
                }`}
              >
                Side-by-Side
              </button>
            </>
          )}

          <button
            onClick={handleDownload}
            className="btn-primary text-xs flex items-center space-x-1.5 py-1.5 px-3"
          >
            <Download className="w-4 h-4" />
            <span>Download Result</span>
          </button>
        </div>
      </div>

      {/* Opacity Control Slider (for image overlay mode) */}
      {mediaType === 'image' && viewMode === 'overlay' && (
        <div className="flex items-center space-x-4 bg-slate-900/60 p-3 rounded-lg border border-slate-800 text-xs">
          <Sliders className="w-4 h-4 text-cyan-400" />
          <span className="text-slate-300 font-medium">Mask Opacity: {opacity}%</span>
          <input
            type="range"
            min="0"
            max="100"
            value={opacity}
            onChange={(e) => setOpacity(Number(e.target.value))}
            className="flex-1 accent-cyan-400 cursor-pointer"
          />
        </div>
      )}

      {/* Media Canvas Display Container */}
      <div className="relative overflow-hidden rounded-lg bg-black border border-slate-800 min-h-[300px] flex items-center justify-center">
        {mediaType === 'video' ? (
          <video controls autoPlay loop className="w-full h-auto max-h-[500px] object-contain">
            <source src={resultUrl} type="video/mp4" />
            Your browser does not support HTML5 video playback.
          </video>
        ) : viewMode === 'side-by-side' ? (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-2 w-full p-2">
            <div className="space-y-1">
              <span className="text-xs font-medium text-slate-400 px-1">Original Scene</span>
              <img src={originalUrl} alt="Original scene" className="w-full h-auto rounded-lg object-contain max-h-[450px]" />
            </div>
            <div className="space-y-1">
              <span className="text-xs font-medium text-cyan-400 px-1">Segmented Mask</span>
              <img src={resultUrl} alt="Segmented mask" className="w-full h-auto rounded-lg object-contain max-h-[450px]" />
            </div>
          </div>
        ) : (
          <div className="relative w-full flex justify-center">
            <img src={originalUrl} alt="Raw scene" className="w-full h-auto max-h-[500px] object-contain rounded-lg" />
            <img
              src={resultUrl}
              alt="Segmented mask"
              style={{ opacity: opacity / 100 }}
              className="absolute top-0 left-0 w-full h-full max-h-[500px] object-contain rounded-lg transition-opacity duration-150 pointer-events-none"
            />
          </div>
        )}
      </div>

      {/* Class Legend Breakdown */}
      {metrics?.classDistribution && Object.keys(metrics.classDistribution).length > 0 && (
        <div className="pt-2">
          <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">Class Distribution Legend</h4>
          <div className="flex flex-wrap gap-2">
            {Object.entries(metrics.classDistribution).map(([className, percentage]) => {
              const color = CLASS_COLORS[className.toLowerCase()] || '#94a3b8';
              return (
                <div key={className} className="flex items-center space-x-2 bg-slate-900 border border-slate-800 px-3 py-1.5 rounded-lg text-xs">
                  <span className="w-3 h-3 rounded-full" style={{ backgroundColor: color }} />
                  <span className="capitalize text-slate-200 font-medium">{className}:</span>
                  <span className="text-cyan-400 font-bold">{percentage.toFixed(1)}%</span>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
};
