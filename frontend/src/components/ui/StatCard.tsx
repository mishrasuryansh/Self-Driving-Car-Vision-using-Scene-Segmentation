import React from 'react';
import { GlassCard } from './GlassCard';

export interface StatCardProps {
  icon: React.ReactNode;
  label: string;
  value: string | number;
  subValue?: string;
  trend?: string;
  accentColor?: 'cyan' | 'blue' | 'purple' | 'emerald';
}

export const StatCard: React.FC<StatCardProps> = ({
  icon,
  label,
  value,
  subValue,
  trend,
  accentColor = 'cyan',
}) => {
  const iconBgStyles = {
    cyan: 'bg-cyan-500/10 text-cyan-400 border-cyan-500/20',
    blue: 'bg-blue-500/10 text-blue-400 border-blue-500/20',
    purple: 'bg-purple-500/10 text-purple-400 border-purple-500/20',
    emerald: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20',
  };

  return (
    <GlassCard hoverEffect className="p-5">
      <div className="flex items-start justify-between">
        <div className="space-y-1">
          <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
            {label}
          </span>
          <div className="text-2xl lg:text-3xl font-extrabold text-slate-100 font-heading">
            {value}
          </div>
          {subValue && (
            <p className="text-xs text-slate-400 font-medium">{subValue}</p>
          )}
        </div>

        <div className={`p-3 rounded-xl border ${iconBgStyles[accentColor]}`}>
          {icon}
        </div>
      </div>

      {trend && (
        <div className="mt-3 pt-3 border-t border-white/5 flex items-center text-xs text-emerald-400">
          <span>{trend}</span>
        </div>
      )}
    </GlassCard>
  );
};
