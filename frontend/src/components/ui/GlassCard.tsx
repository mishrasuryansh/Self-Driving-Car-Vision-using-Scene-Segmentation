import React from 'react';

export interface GlassCardProps extends React.HTMLAttributes<HTMLDivElement> {
  hoverEffect?: boolean;
  glowColor?: 'cyan' | 'blue' | 'purple' | 'emerald' | 'none';
  headerAccent?: boolean;
}

export const GlassCard: React.FC<GlassCardProps> = ({
  children,
  hoverEffect = false,
  glowColor = 'none',
  headerAccent = false,
  className = '',
  ...props
}) => {
  const glowStyles = {
    cyan: 'border-cyan-500/30 shadow-[0_0_25px_-5px_rgba(6,182,212,0.15)]',
    blue: 'border-blue-500/30 shadow-[0_0_25px_-5px_rgba(59,130,246,0.15)]',
    purple: 'border-purple-500/30 shadow-[0_0_25px_-5px_rgba(139,92,246,0.15)]',
    emerald: 'border-emerald-500/30 shadow-[0_0_25px_-5px_rgba(16,185,129,0.15)]',
    none: 'border-white/10',
  };

  return (
    <div
      className={`glass-card relative overflow-hidden ${glowStyles[glowColor]} ${
        hoverEffect ? 'glass-card-hover' : ''
      } ${className}`}
      {...props}
    >
      {headerAccent && (
        <div className="absolute top-0 left-0 right-0 h-[2px] bg-gradient-to-r from-cyan-500 via-blue-500 to-purple-500" />
      )}
      {children}
    </div>
  );
};
