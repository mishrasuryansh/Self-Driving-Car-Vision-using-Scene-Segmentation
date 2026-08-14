/**
 * Persistent Navigation Bar with Responsive Mobile Hamburger Menu (T060).
 *
 * Implements exact Section 10.2 navigation elements (Logo, Dashboard,
 * Upload Dropdown for Image/Video, History, Analytics, Settings, About, Auth Slot).
 */

import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Car, ChevronDown, Menu, X, Upload, History, BarChart2, Settings, Info, User } from 'lucide-react';
import { useAuth } from '../context/AuthContext';


export const NavBar: React.FC = () => {
  const { user, isAuthenticated, logout } = useAuth();
  const [isMobileOpen, setIsMobileOpen] = useState(false);
  const [isUploadDropdownOpen, setIsUploadDropdownOpen] = useState(false);
  const location = useLocation();

  const isActive = (path: string) => location.pathname === path;

  return (
    <header className="glass-nav sticky top-0 z-50 w-full">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo & Title */}
          <Link to="/" className="flex items-center space-x-3 text-cyan-400 font-bold text-lg hover:opacity-90 transition">
            <Car className="w-7 h-7 text-cyan-400" />
            <span className="bg-gradient-to-r from-cyan-400 to-blue-500 bg-clip-text text-transparent">
              Self-Driving Vision
            </span>
          </Link>

          {/* Desktop Navigation Links */}
          <nav className="hidden md:flex items-center space-x-6">
            <Link
              to="/"
              className={`text-sm font-medium transition ${isActive('/') ? 'text-cyan-400 font-semibold' : 'text-slate-300 hover:text-white'}`}
            >
              Dashboard
            </Link>

            {/* Upload Dropdown */}
            <div className="relative">
              <button
                onClick={() => setIsUploadDropdownOpen(!isUploadDropdownOpen)}
                className={`flex items-center space-x-1 text-sm font-medium transition ${
                  isActive('/upload/image') || isActive('/upload/video') ? 'text-cyan-400 font-semibold' : 'text-slate-300 hover:text-white'
                }`}
              >
                <span>Upload</span>
                <ChevronDown className="w-4 h-4" />
              </button>

              {isUploadDropdownOpen && (
                <div
                  className="absolute left-0 mt-2 w-48 rounded-lg bg-slate-900 border border-slate-800 shadow-xl py-2 z-50"
                  onMouseLeave={() => setIsUploadDropdownOpen(false)}
                >
                  <Link
                    to="/upload/image"
                    onClick={() => setIsUploadDropdownOpen(false)}
                    className="flex items-center px-4 py-2 text-sm text-slate-300 hover:bg-slate-800 hover:text-cyan-400"
                  >
                    <Upload className="w-4 h-4 mr-2" /> Image Segmentation
                  </Link>
                  <Link
                    to="/upload/video"
                    onClick={() => setIsUploadDropdownOpen(false)}
                    className="flex items-center px-4 py-2 text-sm text-slate-300 hover:bg-slate-800 hover:text-cyan-400"
                  >
                    <Upload className="w-4 h-4 mr-2" /> Video Stream (Async)
                  </Link>
                </div>
              )}
            </div>

            <Link
              to="/history"
              className={`text-sm font-medium transition ${isActive('/history') ? 'text-cyan-400 font-semibold' : 'text-slate-300 hover:text-white'}`}
            >
              History
            </Link>

            <Link
              to="/analytics"
              className={`text-sm font-medium transition ${isActive('/analytics') ? 'text-cyan-400 font-semibold' : 'text-slate-300 hover:text-white'}`}
            >
              Analytics
            </Link>

            <Link
              to="/settings"
              className={`text-sm font-medium transition ${isActive('/settings') ? 'text-cyan-400 font-semibold' : 'text-slate-300 hover:text-white'}`}
            >
              Settings
            </Link>

            <Link
              to="/about"
              className={`text-sm font-medium transition ${isActive('/about') ? 'text-cyan-400 font-semibold' : 'text-slate-300 hover:text-white'}`}
            >
              About
            </Link>
          </nav>

          {/* Auth Slot / Controls (T062) */}
          <div className="hidden md:flex items-center space-x-3">
            {isAuthenticated ? (
              <div className="flex items-center space-x-3">
                <span className="text-xs text-cyan-400 font-medium bg-slate-900 border border-slate-800 px-3 py-1.5 rounded-lg flex items-center">
                  <User className="w-3.5 h-3.5 mr-1.5" />
                  {user?.full_name || user?.email}
                </span>
                <button
                  onClick={logout}
                  className="text-sm font-medium text-slate-400 hover:text-red-400 px-3 py-1.5 rounded-lg border border-slate-800 hover:border-red-900/50 transition"
                >
                  Logout
                </button>
              </div>
            ) : (
              <>
                <Link to="/login" className="text-sm font-medium text-slate-300 hover:text-white px-3 py-1.5 rounded-lg border border-slate-700">
                  Sign In
                </Link>
                <Link to="/register" className="btn-primary text-sm">
                  Register
                </Link>
              </>
            )}
          </div>

          {/* Mobile Hamburger Button */}
          <div className="md:hidden flex items-center">
            <button
              onClick={() => setIsMobileOpen(!isMobileOpen)}
              className="text-slate-300 hover:text-white p-2 focus:outline-none"
              aria-label="Toggle Navigation Menu"
            >
              {isMobileOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Collapse Navigation Menu */}
      {isMobileOpen && (
        <div className="md:hidden bg-slate-900 border-b border-slate-800 px-4 pt-2 pb-4 space-y-2">
          <Link
            to="/"
            onClick={() => setIsMobileOpen(false)}
            className="block px-3 py-2 rounded-md text-base font-medium text-slate-300 hover:bg-slate-800 hover:text-cyan-400"
          >
            Dashboard
          </Link>
          <div className="pl-3 space-y-1">
            <div className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Upload</div>
            <Link
              to="/upload/image"
              onClick={() => setIsMobileOpen(false)}
              className="block px-3 py-1.5 text-sm text-slate-300 hover:text-cyan-400"
            >
              Image Segmentation
            </Link>
            <Link
              to="/upload/video"
              onClick={() => setIsMobileOpen(false)}
              className="block px-3 py-1.5 text-sm text-slate-300 hover:text-cyan-400"
            >
              Video Stream (Async)
            </Link>
          </div>
          <Link
            to="/history"
            onClick={() => setIsMobileOpen(false)}
            className="block px-3 py-2 rounded-md text-base font-medium text-slate-300 hover:bg-slate-800 hover:text-cyan-400"
          >
            History
          </Link>
          <Link
            to="/analytics"
            onClick={() => setIsMobileOpen(false)}
            className="block px-3 py-2 rounded-md text-base font-medium text-slate-300 hover:bg-slate-800 hover:text-cyan-400"
          >
            Analytics
          </Link>
          <Link
            to="/settings"
            onClick={() => setIsMobileOpen(false)}
            className="block px-3 py-2 rounded-md text-base font-medium text-slate-300 hover:bg-slate-800 hover:text-cyan-400"
          >
            Settings
          </Link>
          <Link
            to="/about"
            onClick={() => setIsMobileOpen(false)}
            className="block px-3 py-2 rounded-md text-base font-medium text-slate-300 hover:bg-slate-800 hover:text-cyan-400"
          >
            About
          </Link>
          <div className="pt-2 border-t border-slate-800 flex flex-col space-y-2">
            <Link
              to="/login"
              onClick={() => setIsMobileOpen(false)}
              className="w-full text-center px-4 py-2 border border-slate-700 text-sm font-medium rounded-lg text-slate-300"
            >
              Sign In
            </Link>
            <Link
              to="/register"
              onClick={() => setIsMobileOpen(false)}
              className="w-full text-center btn-primary text-sm"
            >
              Register
            </Link>
          </div>
        </div>
      )}
    </header>
  );
};
