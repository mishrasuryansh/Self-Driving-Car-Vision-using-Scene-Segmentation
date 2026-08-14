/**
 * Reusable Loading Spinner Component (T075).
 */

import React from 'react';
import { Loader2 } from 'lucide-react';

interface SpinnerProps {
  size?: 'sm' | 'md' | 'lg';
  label?: string;
  className?: string;
}

export const Spinner: React.FC<SpinnerProps> = ({
  size = 'md',
  label = 'Loading...',
  className = '',
}) => {
  const sizeMap = {
    sm: 'w-4 h-4',
    md: 'w-6 h-6',
    lg: 'w-8 h-8',
  };

  return (
    <div className={`flex items-center justify-center space-x-2 text-slate-400 ${className}`}>
      <Loader2 className={`${sizeMap[size]} text-cyan-400 animate-spin`} />
      {label && <span className="text-xs font-medium text-slate-300">{label}</span>}
    </div>
  );
};
