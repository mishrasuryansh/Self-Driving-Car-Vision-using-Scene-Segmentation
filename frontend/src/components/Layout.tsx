/**
 * Shared Page Layout Wrapper Component (T060).
 *
 * Wraps all application routes with persistent navigation bar and footer.
 */

import React from 'react';
import { NavBar } from './NavBar';

interface LayoutProps {
  children: React.ReactNode;
}

export const Layout: React.FC<LayoutProps> = ({ children }) => {
  return (
    <div className="min-h-screen flex flex-col bg-slate-950 text-slate-100">
      <NavBar />
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {children}
      </main>
      <footer className="border-t border-slate-800 bg-slate-900/50 py-4 text-center text-xs text-slate-500">
        Self-Driving Car Vision Platform &copy; 2026. Powered by DeepLabV3+ & PyTorch.
      </footer>
    </div>
  );
};
