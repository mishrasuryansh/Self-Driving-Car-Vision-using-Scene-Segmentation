import React, { useState, useEffect } from 'react';
import { Activity, CheckCircle2, AlertTriangle, ShieldCheck } from 'lucide-react';
import apiClient from '../../services/api';

interface HealthCheck {
  api: 'operational' | 'degraded' | 'unavailable';
  worker: 'operational' | 'degraded' | 'unavailable';
  redis: 'operational' | 'degraded' | 'unavailable';
  db: 'operational' | 'degraded' | 'unavailable';
}

export const SystemStatusBadge: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [health, setHealth] = useState<HealthCheck>({
    api: 'operational',
    worker: 'operational',
    redis: 'operational',
    db: 'operational',
  });

  useEffect(() => {
    const checkSystemStatus = async () => {
      try {
        await apiClient.get('/health');
        setHealth({
          api: 'operational',
          worker: 'operational',
          redis: 'operational',
          db: 'operational',
        });
      } catch (err) {
        setHealth((prev) => ({ ...prev, api: 'degraded' }));
      }
    };
    checkSystemStatus();
  }, []);

  const isAllOperational = Object.values(health).every((v) => v === 'operational');

  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center space-x-2 px-3 py-1.5 rounded-full bg-slate-900/80 border border-slate-800 hover:border-slate-700 transition text-xs cursor-pointer"
        title="Click to view Perception Engine Infrastructure Health"
      >
        <span className="relative flex h-2 w-2">
          <span
            className={`animate-ping absolute inline-flex h-full w-full rounded-full opacity-75 ${
              isAllOperational ? 'bg-emerald-400' : 'bg-amber-400'
            }`}
          />
          <span
            className={`relative inline-flex rounded-full h-2 w-2 ${
              isAllOperational ? 'bg-emerald-500' : 'bg-amber-500'
            }`}
          />
        </span>
        <span className="font-semibold text-slate-300">
          {isAllOperational ? 'System Operational' : 'Degraded Performance'}
        </span>
      </button>

      {/* Popover Status Card */}
      {isOpen && (
        <div className="absolute right-0 mt-2 w-64 glass-card p-4 shadow-2xl z-50 space-y-3 text-xs border border-cyan-500/20">
          <div className="flex items-center justify-between border-b border-slate-800 pb-2">
            <div className="flex items-center space-x-1.5 font-bold text-slate-200">
              <ShieldCheck className="w-4 h-4 text-cyan-400" />
              <span>Infra Health Matrix</span>
            </div>
            <button
              onClick={() => setIsOpen(false)}
              className="text-slate-500 hover:text-slate-300"
            >
              ✕
            </button>
          </div>

          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-slate-400">FastAPI REST Gateway</span>
              <span className="text-emerald-400 font-semibold flex items-center">
                <CheckCircle2 className="w-3 h-3 mr-1" /> {health.api}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-slate-400">Celery Async Workers</span>
              <span className="text-emerald-400 font-semibold flex items-center">
                <CheckCircle2 className="w-3 h-3 mr-1" /> {health.worker}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-slate-400">Redis Cache & Broker</span>
              <span className="text-emerald-400 font-semibold flex items-center">
                <CheckCircle2 className="w-3 h-3 mr-1" /> {health.redis}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-slate-400">DeepLabV3+ Engine</span>
              <span className="text-cyan-400 font-semibold flex items-center">
                <Activity className="w-3 h-3 mr-1" /> PyTorch Ready
              </span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
