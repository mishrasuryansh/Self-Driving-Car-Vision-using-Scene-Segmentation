import React from 'react';
import { Settings } from 'lucide-react';

export const SettingsPage: React.FC = () => (
  <div className="space-y-6">
    <div className="flex items-center space-x-3 text-cyan-400">
      <Settings className="w-8 h-8" />
      <h1 className="text-2xl font-bold text-slate-100">System Settings</h1>
    </div>
    <div className="glass-card p-6">
      <p className="text-slate-400">Configure model threshold settings, GPU device selection, and storage retention parameters.</p>
    </div>
  </div>
);
