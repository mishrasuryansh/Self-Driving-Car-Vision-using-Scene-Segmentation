/**
 * Interactive Segment Mask Overlay & Canvas Toggle Component (T065).
 *
 * Renders original image with colorized semantic segmentation mask overlay,
 * interactive opacity blending slider, side-by-side mode, and class color legend.
 */

import React, { useState } from 'react';
import { Eye, EyeOff, Layers, Sliders } from 'lucide-react';

interface SegmentMaskOverlayProps {
  originalUrl: string;
  maskUrl: string;
  classDistribution?: Record<string, number>;
}

const CLASS_COLORS: Record<string, string> = {
  road: '#06b6d4',       // Cyan
  vehicle: '#3b82f6',    // Blue
  sky: '#8b5cf6',        // Purple
  vegetation: '#10b981', // Green
  pedestrian: '#ef4444', // Red
  building: '#f59e0b',   // Amber
  sidewalk: '#ec4899',   // Pink
  other: '#64748b',      // Slate
};

export const SegmentMaskOverlay: React.FC<SegmentMaskOverlayProps> = ({
  originalUrl,
  maskUrl,
  classDistribution = {},
}) => {
  const [opacity, setOpacity] = useState<number>(75);
  const [viewMode, setViewMode] = useState<'overlay' | 'side-by-side' | 'raw' | 'mask'>('overlay');

  return (
    <div className="space-y-4 glass-card p-6">
      <div className="flex flex-wrap items-center justify-between gap-4 border-b border-slate-800 pb-4">
        <div className="flex items-center space-x-2">
          <Layers className="w-5 h-5 text-cyan-400" />
          <h3 className="font-semibold text-lg text-slate-100">Segmentation Visualization</h3>
        </div>

        {/* View Controls */}
        <div className="flex flex-wrap items-center gap-2">
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

          <button
            onClick={() => setViewMode('raw')}
            className={`px-3 py-1.5 rounded-lg text-xs font-medium transition ${
              viewMode === 'raw' ? 'bg-cyan-500 text-white font-bold' : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
            }`}
          >
            Raw Image
          </button>

          <button
            onClick={() => setViewMode('mask')}
            className={`px-3 py-1.5 rounded-lg text-xs font-medium transition ${
              viewMode === 'mask' ? 'bg-cyan-500 text-white font-bold' : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
            }`}
          >
            Mask Only
          </button>
        </div>
      </div>

      {/* Opacity Control Slider (for overlay mode) */}
      {viewMode === 'overlay' && (
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

      {/* Display Canvas Container */}
      <div className="relative overflow-hidden rounded-lg bg-black border border-slate-800 min-h-[300px] flex items-center justify-center">
        {viewMode === 'side-by-side' ? (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-2 w-full p-2">
            <div className="space-y-1">
              <span className="text-xs font-medium text-slate-400 px-1">Original Scene</span>
              <img src={originalUrl} alt="Original road scene" className="w-full h-auto rounded-lg object-contain max-h-[450px]" />
            </div>
            <div className="space-y-1">
              <span className="text-xs font-medium text-cyan-400 px-1">Segmented Classes</span>
              <img src={maskUrl} alt="Segmentation mask" className="w-full h-auto rounded-lg object-contain max-h-[450px]" />
            </div>
          </div>
        ) : (
          <div className="relative w-full flex justify-center">
            {/* Raw Image Layer */}
            <img
              src={originalUrl}
              alt="Raw road scene"
              className={`w-full h-auto max-h-[500px] object-contain rounded-lg ${viewMode === 'mask' ? 'hidden' : 'block'}`}
            />

            {/* Segmentation Mask Overlay Layer */}
            <img
              src={maskUrl}
              alt="Segmentation mask"
              style={{ opacity: viewMode === 'raw' ? 0 : viewMode === 'mask' ? 1 : opacity / 100 }}
              className={`absolute top-0 left-0 w-full h-full max-h-[500px] object-contain rounded-lg transition-opacity duration-150 pointer-events-none ${
                viewMode === 'raw' ? 'hidden' : 'block'
              }`}
            />
          </div>
        )}
      </div>

      {/* Class Legend Breakdown */}
      {Object.keys(classDistribution).length > 0 && (
        <div className="pt-2">
          <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">Class Distribution Legend</h4>
          <div className="flex flex-wrap gap-2">
            {Object.entries(classDistribution).map(([className, percentage]) => {
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
