/**
 * Reusable Error Banner Alert Component (T075).
 */

import React from 'react';
import { AlertCircle, X } from 'lucide-react';

interface ErrorBannerProps {
  message: string;
  onDismiss?: () => void;
}

export const ErrorBanner: React.FC<ErrorBannerProps> = ({ message, onDismiss }) => {
  return (
    <div className="p-4 rounded-lg bg-red-950/60 border border-red-800 text-red-300 text-sm flex items-center justify-between space-x-3">
      <div className="flex items-center space-x-3">
        <AlertCircle className="w-5 h-5 text-red-400 flex-shrink-0" />
        <span>{message}</span>
      </div>
      {onDismiss && (
        <button onClick={onDismiss} className="text-red-400 hover:text-white p-1">
          <X className="w-4 h-4" />
        </button>
      )}
    </div>
  );
};
