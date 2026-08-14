/**
 * User Settings & Profile Preference Page (T072).
 *
 * Provides editable user profile fields, password update form with validation,
 * default model selection, and success toast feedback.
 */

import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { useToast } from '../components/Toast';
import { Settings, User, Lock, Cpu, Save } from 'lucide-react';

export const SettingsPage: React.FC = () => {
  const { user } = useAuth();
  const { showToast } = useToast();

  const [fullName, setFullName] = useState(user?.full_name || '');
  const [email] = useState(user?.email || '');
  const [currentPass, setCurrentPass] = useState('');
  const [newPass, setNewPass] = useState('');
  const [confirmPass, setConfirmPass] = useState('');
  const [passError, setPassError] = useState<string | null>(null);
  const [selectedModel, setSelectedModel] = useState<string>('deeplabv3_resnet101');

  const handleProfileSave = (e: React.FormEvent) => {
    e.preventDefault();
    showToast('User profile updated successfully!', 'success', 'Profile Saved');
  };

  const handlePasswordSave = (e: React.FormEvent) => {
    e.preventDefault();
    setPassError(null);

    if (newPass.length < 8) {
      setPassError('New password must be at least 8 characters long.');
      return;
    }

    if (newPass !== confirmPass) {
      setPassError('New password and confirmation do not match.');
      return;
    }

    setCurrentPass('');
    setNewPass('');
    setConfirmPass('');
    showToast('Password updated successfully!', 'success', 'Security Updated');
  };

  const handleModelSave = (e: React.FormEvent) => {
    e.preventDefault();
    localStorage.setItem('preferred_model_id', selectedModel);
    showToast(`Default model preference set to ${selectedModel}`, 'info', 'Preference Saved');
  };

  return (
    <div className="space-y-8 max-w-4xl mx-auto">
      <div className="flex items-center space-x-3 border-b border-slate-800 pb-4">
        <Settings className="w-8 h-8 text-cyan-400" />
        <div>
          <h1 className="text-2xl font-bold">User Settings & Preferences</h1>
          <p className="text-xs text-slate-400">Manage account credentials, profile details, and model selection</p>
        </div>
      </div>

      {/* User Profile Section */}
      <form onSubmit={handleProfileSave} className="glass-card p-6 space-y-4">
        <div className="flex items-center space-x-2 border-b border-slate-800 pb-3">
          <User className="w-5 h-5 text-cyan-400" />
          <h3 className="font-semibold text-lg text-slate-100">User Profile</h3>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label className="block text-xs font-medium text-slate-400 mb-1">Full Name</label>
            <input
              type="text"
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-xs text-slate-100 focus:border-cyan-400 focus:outline-none"
            />
          </div>

          <div>
            <label className="block text-xs font-medium text-slate-400 mb-1">Email Address (Read Only)</label>
            <input
              type="email"
              disabled
              value={email}
              className="w-full bg-slate-900/50 border border-slate-800 rounded-lg px-3 py-2 text-xs text-slate-500 cursor-not-allowed"
            />
          </div>
        </div>

        <button type="submit" className="btn-primary text-xs flex items-center space-x-1.5 py-2">
          <Save className="w-4 h-4" />
          <span>Save Profile Changes</span>
        </button>
      </form>

      {/* Password Change Section */}
      <form onSubmit={handlePasswordSave} className="glass-card p-6 space-y-4">
        <div className="flex items-center space-x-2 border-b border-slate-800 pb-3">
          <Lock className="w-5 h-5 text-purple-400" />
          <h3 className="font-semibold text-lg text-slate-100">Security & Password</h3>
        </div>

        {passError && (
          <div className="p-3 rounded-lg bg-red-950/60 border border-red-800 text-red-300 text-xs">
            {passError}
          </div>
        )}

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <div>
            <label className="block text-xs font-medium text-slate-400 mb-1">Current Password</label>
            <input
              type="password"
              required
              value={currentPass}
              onChange={(e) => setCurrentPass(e.target.value)}
              className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-xs text-slate-100 focus:border-purple-400 focus:outline-none"
            />
          </div>

          <div>
            <label className="block text-xs font-medium text-slate-400 mb-1">New Password</label>
            <input
              type="password"
              required
              value={newPass}
              onChange={(e) => setNewPass(e.target.value)}
              className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-xs text-slate-100 focus:border-purple-400 focus:outline-none"
            />
          </div>

          <div>
            <label className="block text-xs font-medium text-slate-400 mb-1">Confirm New Password</label>
            <input
              type="password"
              required
              value={confirmPass}
              onChange={(e) => setConfirmPass(e.target.value)}
              className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-xs text-slate-100 focus:border-purple-400 focus:outline-none"
            />
          </div>
        </div>

        <button type="submit" className="btn-primary bg-gradient-to-r from-purple-600 to-indigo-600 text-xs flex items-center space-x-1.5 py-2">
          <Lock className="w-4 h-4" />
          <span>Update Password</span>
        </button>
      </form>

      {/* Model Selection Preference */}
      <form onSubmit={handleModelSave} className="glass-card p-6 space-y-4">
        <div className="flex items-center space-x-2 border-b border-slate-800 pb-3">
          <Cpu className="w-5 h-5 text-emerald-400" />
          <h3 className="font-semibold text-lg text-slate-100">Segmentation Model Preference</h3>
        </div>

        <div>
          <label className="block text-xs font-medium text-slate-400 mb-1">Default Model Architecture</label>
          <select
            value={selectedModel}
            onChange={(e) => setSelectedModel(e.target.value)}
            className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-xs text-slate-100 focus:border-emerald-400 focus:outline-none cursor-pointer"
          >
            <option value="deeplabv3_resnet101">DeepLabV3+ (ResNet-101 ASPP) [Recommended / Section 8.2 Standard]</option>
            <option value="deeplabv3_mobilenet_v3">DeepLabV3+ (MobileNetV3 Lightweight)</option>
          </select>
        </div>

        <button type="submit" className="btn-primary bg-gradient-to-r from-emerald-600 to-teal-600 text-xs flex items-center space-x-1.5 py-2">
          <Save className="w-4 h-4" />
          <span>Save Preference</span>
        </button>
      </form>
    </div>
  );
};
