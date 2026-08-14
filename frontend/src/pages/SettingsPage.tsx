import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { Settings, User, Lock, Cpu, Save, Sliders, Moon, Eye } from 'lucide-react';
import { GlassCard } from '../components/ui/GlassCard';
import { Button } from '../components/ui/Button';
import { Badge } from '../components/ui/Badge';

export const SettingsPage: React.FC = () => {
  const { user } = useAuth();

  const [fullName, setFullName] = useState(user?.full_name || '');
  const [email] = useState(user?.email || '');
  const [currentPass, setCurrentPass] = useState('');
  const [newPass, setNewPass] = useState('');
  const [confirmPass, setConfirmPass] = useState('');
  const [passError, setPassError] = useState<string | null>(null);
  const [selectedModel, setSelectedModel] = useState<string>('deeplabv3plus_resnet101');
  const [savedFeedback, setSavedFeedback] = useState<string | null>(null);

  const showNotification = (msg: string) => {
    setSavedFeedback(msg);
    setTimeout(() => setSavedFeedback(null), 3000);
  };

  const handleProfileSave = (e: React.FormEvent) => {
    e.preventDefault();
    showNotification('User profile details saved successfully!');
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
    showNotification('Security credentials updated successfully!');
  };

  const handleModelSave = (e: React.FormEvent) => {
    e.preventDefault();
    localStorage.setItem('preferred_model_id', selectedModel);
    showNotification(`Default model set to ${selectedModel}`);
  };

  return (
    <div className="space-y-8 max-w-4xl mx-auto py-2">
      {/* Header Bar */}
      <div className="flex flex-wrap items-center justify-between gap-4 border-b border-slate-800 pb-4">
        <div className="flex items-center space-x-3">
          <div className="p-2.5 rounded-2xl bg-cyan-500/10 border border-cyan-500/20 text-cyan-400">
            <Settings className="w-6 h-6" />
          </div>
          <div>
            <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-100 font-heading">
              Platform Settings & Preferences
            </h1>
            <p className="text-xs text-slate-400">
              Manage account credentials, profile details, and model architecture defaults
            </p>
          </div>
        </div>

        {savedFeedback && (
          <Badge variant="emerald" dot>{savedFeedback}</Badge>
        )}
      </div>

      {/* Profile Settings Card */}
      <GlassCard hoverEffect glowColor="cyan" className="p-6 space-y-4">
        <div className="flex items-center space-x-2 border-b border-slate-800 pb-3">
          <User className="w-5 h-5 text-cyan-400" />
          <h3 className="font-bold text-lg text-slate-100 font-heading">User Profile Information</h3>
        </div>

        <form onSubmit={handleProfileSave} className="space-y-4">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1.5">Full Name</label>
              <input
                type="text"
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                className="w-full glass-input px-3 py-2 text-xs"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1.5">Email Address (Managed)</label>
              <input
                type="email"
                disabled
                value={email || 'pilot@selfdriving.com'}
                className="w-full glass-input px-3 py-2 text-xs opacity-50 cursor-not-allowed"
              />
            </div>
          </div>

          <Button type="submit" variant="primary" size="sm" leftIcon={<Save className="w-4 h-4" />}>
            Save Profile Changes
          </Button>
        </form>
      </GlassCard>

      {/* Password & Security Card */}
      <GlassCard hoverEffect glowColor="purple" className="p-6 space-y-4">
        <div className="flex items-center space-x-2 border-b border-slate-800 pb-3">
          <Lock className="w-5 h-5 text-purple-400" />
          <h3 className="font-bold text-lg text-slate-100 font-heading">Security & Authentication</h3>
        </div>

        {passError && (
          <div className="p-3 rounded-xl bg-rose-950/60 border border-rose-800 text-rose-300 text-xs">
            {passError}
          </div>
        )}

        <form onSubmit={handlePasswordSave} className="space-y-4">
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1.5">Current Password</label>
              <input
                type="password"
                required
                value={currentPass}
                onChange={(e) => setCurrentPass(e.target.value)}
                className="w-full glass-input px-3 py-2 text-xs"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1.5">New Password</label>
              <input
                type="password"
                required
                value={newPass}
                onChange={(e) => setNewPass(e.target.value)}
                className="w-full glass-input px-3 py-2 text-xs"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1.5">Confirm Password</label>
              <input
                type="password"
                required
                value={confirmPass}
                onChange={(e) => setConfirmPass(e.target.value)}
                className="w-full glass-input px-3 py-2 text-xs"
              />
            </div>
          </div>

          <Button type="submit" variant="secondary" size="sm" leftIcon={<Lock className="w-4 h-4 text-purple-400" />}>
            Update Password
          </Button>
        </form>
      </GlassCard>

      {/* Model Preferences Card */}
      <GlassCard hoverEffect glowColor="blue" className="p-6 space-y-4">
        <div className="flex items-center space-x-2 border-b border-slate-800 pb-3">
          <Cpu className="w-5 h-5 text-blue-400" />
          <h3 className="font-bold text-lg text-slate-100 font-heading">Model Preference & Defaults</h3>
        </div>

        <form onSubmit={handleModelSave} className="space-y-4">
          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1.5">Default Model Architecture</label>
            <select
              value={selectedModel}
              onChange={(e) => setSelectedModel(e.target.value)}
              className="w-full glass-input px-3 py-2 text-xs cursor-pointer"
            >
              <option value="deeplabv3plus_resnet101" className="bg-slate-900 text-slate-200">
                DeepLabV3+ (ResNet-101 ASPP) — Standard Benchmark Target
              </option>
              <option value="deeplabv3plus_mobilenet" className="bg-slate-900 text-slate-200">
                DeepLabV3+ (MobileNetV2 Lightweight)
              </option>
            </select>
          </div>

          <Button type="submit" variant="outline" size="sm" leftIcon={<Save className="w-4 h-4" />}>
            Save Model Preference
          </Button>
        </form>
      </GlassCard>
    </div>
  );
};
