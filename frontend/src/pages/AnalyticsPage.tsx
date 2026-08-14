import React from 'react';
import { BarChart2 } from 'lucide-react';

export const AnalyticsPage: React.FC = () => (
  <div className="space-y-6">
    <div className="flex items-center space-x-3 text-cyan-400">
      <BarChart2 className="w-8 h-8" />
      <h1 className="text-2xl font-bold text-slate-100">Perception Analytics</h1>
    </div>
    <div className="glass-card p-6">
      <p className="text-slate-400">Class distribution breakdown, mean IoU metrics, and inference latency statistics.</p>
    </div>
  </div>
);
