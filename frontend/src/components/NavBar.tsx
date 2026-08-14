import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Car, ChevronDown, Menu, X, Upload, History, BarChart2, Settings, Info, User, LogOut, Video, Image } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { SystemStatusBadge } from './ui/SystemStatusBadge';
import { Button } from './ui/Button';

export const NavBar: React.FC = () => {
  const { user, isAuthenticated, logout } = useAuth();
  const [isMobileOpen, setIsMobileOpen] = useState(false);
  const [isUploadDropdownOpen, setIsUploadDropdownOpen] = useState(false);
  const location = useLocation();

  const isActive = (path: string) => location.pathname === path;

  return (
    <header className="glass-nav sticky top-0 z-50 w-full transition-all">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo & Title */}
          <Link to="/" className="flex items-center space-x-3 group">
            <div className="p-2 rounded-xl bg-cyan-500/10 border border-cyan-500/30 group-hover:border-cyan-400 group-hover:shadow-[0_0_15px_rgba(6,182,212,0.3)] transition-all">
              <Car className="w-5 h-5 text-cyan-400" />
            </div>
            <span className="font-heading font-extrabold text-lg tracking-tight bg-gradient-to-r from-white via-slate-100 to-cyan-400 bg-clip-text text-transparent">
              Self-Driving<span className="text-cyan-400 font-light ml-1">Vision</span>
            </span>
          </Link>

          {/* Desktop Navigation Links */}
          <nav className="hidden lg:flex items-center space-x-1">
            <Link
              to="/"
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition ${
                isActive('/')
                  ? 'bg-cyan-500/10 text-cyan-400 border border-cyan-500/20'
                  : 'text-slate-300 hover:text-white hover:bg-slate-800/50'
              }`}
            >
              Dashboard
            </Link>

            {/* Upload Dropdown Menu */}
            <div className="relative" onMouseLeave={() => setIsUploadDropdownOpen(false)}>
              <button
                onClick={() => setIsUploadDropdownOpen(!isUploadDropdownOpen)}
                onMouseEnter={() => setIsUploadDropdownOpen(true)}
                className={`flex items-center space-x-1 px-3 py-1.5 rounded-lg text-xs font-semibold transition cursor-pointer ${
                  isActive('/upload/image') || isActive('/upload/video')
                    ? 'bg-cyan-500/10 text-cyan-400 border border-cyan-500/20'
                    : 'text-slate-300 hover:text-white hover:bg-slate-800/50'
                }`}
              >
                <span>Analyze</span>
                <ChevronDown className="w-3.5 h-3.5" />
              </button>

              {isUploadDropdownOpen && (
                <div className="absolute left-0 mt-1 w-52 rounded-xl glass-card p-1.5 shadow-2xl border border-cyan-500/20 z-50 animate-in fade-in zoom-in-95 duration-150">
                  <Link
                    to="/upload/image"
                    onClick={() => setIsUploadDropdownOpen(false)}
                    className="flex items-center space-x-2.5 px-3 py-2 rounded-lg text-xs text-slate-300 hover:bg-cyan-500/10 hover:text-cyan-300 transition"
                  >
                    <Image className="w-4 h-4 text-cyan-400" />
                    <div>
                      <div className="font-semibold">Image Segmentation</div>
                      <div className="text-[10px] text-slate-500">Real-Time Single Frame</div>
                    </div>
                  </Link>

                  <Link
                    to="/upload/video"
                    onClick={() => setIsUploadDropdownOpen(false)}
                    className="flex items-center space-x-2.5 px-3 py-2 rounded-lg text-xs text-slate-300 hover:bg-purple-500/10 hover:text-purple-300 transition"
                  >
                    <Video className="w-4 h-4 text-purple-400" />
                    <div>
                      <div className="font-semibold">Video Stream (Async)</div>
                      <div className="text-[10px] text-slate-500">Celery Distributed Queue</div>
                    </div>
                  </Link>
                </div>
              )}
            </div>

            <Link
              to="/history"
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition ${
                isActive('/history')
                  ? 'bg-cyan-500/10 text-cyan-400 border border-cyan-500/20'
                  : 'text-slate-300 hover:text-white hover:bg-slate-800/50'
              }`}
            >
              History
            </Link>

            <Link
              to="/analytics"
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition ${
                isActive('/analytics')
                  ? 'bg-cyan-500/10 text-cyan-400 border border-cyan-500/20'
                  : 'text-slate-300 hover:text-white hover:bg-slate-800/50'
              }`}
            >
              Analytics
            </Link>

            <Link
              to="/settings"
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition ${
                isActive('/settings')
                  ? 'bg-cyan-500/10 text-cyan-400 border border-cyan-500/20'
                  : 'text-slate-300 hover:text-white hover:bg-slate-800/50'
              }`}
            >
              Settings
            </Link>

            <Link
              to="/about"
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition ${
                isActive('/about')
                  ? 'bg-cyan-500/10 text-cyan-400 border border-cyan-500/20'
                  : 'text-slate-300 hover:text-white hover:bg-slate-800/50'
              }`}
            >
              About
            </Link>
          </nav>

          {/* Right Action Bar: System Health & Auth Slot */}
          <div className="hidden lg:flex items-center space-x-3">
            <SystemStatusBadge />

            {isAuthenticated ? (
              <div className="flex items-center space-x-2 border-l border-slate-800 pl-3">
                <span className="text-xs text-slate-300 font-semibold bg-slate-900 border border-slate-800 px-3 py-1.5 rounded-xl flex items-center gap-1.5">
                  <User className="w-3.5 h-3.5 text-cyan-400" />
                  {user?.full_name || user?.email}
                </span>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={logout}
                  title="Logout session"
                  leftIcon={<LogOut className="w-3.5 h-3.5 text-rose-400" />}
                >
                  Logout
                </Button>
              </div>
            ) : (
              <div className="flex items-center space-x-2 border-l border-slate-800 pl-3">
                <Link to="/login">
                  <Button variant="ghost" size="sm">
                    Sign In
                  </Button>
                </Link>
                <Link to="/register">
                  <Button variant="primary" size="sm">
                    Register
                  </Button>
                </Link>
              </div>
            )}
          </div>

          {/* Mobile Hamburger Menu Button */}
          <div className="lg:hidden flex items-center space-x-2">
            <SystemStatusBadge />
            <button
              onClick={() => setIsMobileOpen(!isMobileOpen)}
              className="p-2 rounded-xl bg-slate-900 border border-slate-800 text-slate-300 hover:text-white"
              aria-label="Toggle Menu"
            >
              {isMobileOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Drawer */}
      {isMobileOpen && (
        <div className="lg:hidden glass-card border-t border-slate-800 px-4 py-4 space-y-2 animate-in slide-in-from-top-2">
          <Link
            to="/"
            onClick={() => setIsMobileOpen(false)}
            className="block px-3 py-2 rounded-lg text-sm font-semibold text-slate-200 hover:bg-cyan-500/10 hover:text-cyan-400"
          >
            Dashboard
          </Link>
          <Link
            to="/upload/image"
            onClick={() => setIsMobileOpen(false)}
            className="block px-3 py-2 rounded-lg text-sm font-semibold text-slate-200 hover:bg-cyan-500/10 hover:text-cyan-400"
          >
            Analyze Image
          </Link>
          <Link
            to="/upload/video"
            onClick={() => setIsMobileOpen(false)}
            className="block px-3 py-2 rounded-lg text-sm font-semibold text-slate-200 hover:bg-purple-500/10 hover:text-purple-400"
          >
            Analyze Video (Async)
          </Link>
          <Link
            to="/history"
            onClick={() => setIsMobileOpen(false)}
            className="block px-3 py-2 rounded-lg text-sm font-semibold text-slate-200 hover:bg-cyan-500/10 hover:text-cyan-400"
          >
            History
          </Link>
          <Link
            to="/analytics"
            onClick={() => setIsMobileOpen(false)}
            className="block px-3 py-2 rounded-lg text-sm font-semibold text-slate-200 hover:bg-cyan-500/10 hover:text-cyan-400"
          >
            Analytics
          </Link>
          <Link
            to="/settings"
            onClick={() => setIsMobileOpen(false)}
            className="block px-3 py-2 rounded-lg text-sm font-semibold text-slate-200 hover:bg-cyan-500/10 hover:text-cyan-400"
          >
            Settings
          </Link>
          <Link
            to="/about"
            onClick={() => setIsMobileOpen(false)}
            className="block px-3 py-2 rounded-lg text-sm font-semibold text-slate-200 hover:bg-cyan-500/10 hover:text-cyan-400"
          >
            About
          </Link>

          <div className="pt-3 border-t border-slate-800 flex flex-col space-y-2">
            {isAuthenticated ? (
              <Button variant="danger" size="sm" onClick={() => { logout(); setIsMobileOpen(false); }}>
                Logout
              </Button>
            ) : (
              <>
                <Link to="/login" onClick={() => setIsMobileOpen(false)}>
                  <Button variant="secondary" size="sm" className="w-full">
                    Sign In
                  </Button>
                </Link>
                <Link to="/register" onClick={() => setIsMobileOpen(false)}>
                  <Button variant="primary" size="sm" className="w-full">
                    Register
                  </Button>
                </Link>
              </>
            )}
          </div>
        </div>
      )}
    </header>
  );
};
