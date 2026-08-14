import React from 'react';
import { History } from 'lucide-react';

export const HistoryPage: React.FC = () => (
  <div className="space-y-6">
    <div className="flex items-center space-x-3 text-cyan-400">
      <History className="w-8 h-8" />
      <h1 className="text-2xl font-bold text-slate-100">Segmentation History</h1>
    </div>
    <div className="glass-card p-6">
      <p className="text-slate-400">View previous segmentation jobs, outputs, and performance metrics.</p>
    </div>
  </div>
);
