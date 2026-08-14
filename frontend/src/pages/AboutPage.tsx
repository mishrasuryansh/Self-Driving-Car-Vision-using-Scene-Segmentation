import React from 'react';
import { Info } from 'lucide-react';

export const AboutPage: React.FC = () => (
  <div className="space-y-6">
    <div className="flex items-center space-x-3 text-cyan-400">
      <Info className="w-8 h-8" />
      <h1 className="text-2xl font-bold text-slate-100">About Self-Driving Car Vision Platform</h1>
    </div>
    <div className="glass-card p-6 space-y-3">
      <p className="text-slate-300">
        An end-to-end deep learning platform for real-time scene segmentation in self-driving vehicle systems. Built using PyTorch, DeepLabV3+, FastAPI, Celery, Redis, MongoDB, and React.
      </p>
    </div>
  </div>
);
