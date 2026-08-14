import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { User, Lock, Mail, ArrowRight, ShieldCheck, CheckCircle2 } from 'lucide-react';
import { Button } from '../components/ui/Button';
import { GlassCard } from '../components/ui/GlassCard';
import { Badge } from '../components/ui/Badge';

export const RegisterPage: React.FC = () => {
  const { register, login } = useAuth();
  const navigate = useNavigate();

  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const getPasswordStrength = () => {
    if (!password) return null;
    if (password.length < 6) return { label: 'Weak', color: 'bg-rose-500' };
    if (password.length < 10) return { label: 'Medium', color: 'bg-amber-500' };
    return { label: 'Strong', color: 'bg-emerald-500' };
  };

  const strength = getPasswordStrength();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email.trim())) {
      setError('Please enter a valid email address.');
      return;
    }

    if (password.length < 8) {
      setError('Password must be at least 8 characters long.');
      return;
    }

    setIsSubmitting(true);

    try {
      await register(email.trim(), password, fullName.trim());
      await login(email.trim(), password);
      navigate('/', { replace: true });
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Registration failed. Email may already be registered.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-center min-h-[calc(100vh-140px)] max-w-6xl mx-auto py-4">
      {/* Left Column: Visual AI Branding Banner */}
      <div className="lg:col-span-6 space-y-6 hidden lg:block pr-6 border-r border-slate-800/80">
        <Badge variant="purple" dot>JOIN VISION AI PLATFORM</Badge>

        <h1 className="text-4xl font-extrabold text-slate-100 font-heading leading-tight">
          Create Your Autonomous{' '}
          <span className="bg-gradient-to-r from-purple-400 to-cyan-400 bg-clip-text text-transparent">
            Developer Account
          </span>
        </h1>

        <p className="text-sm text-slate-400 leading-relaxed">
          Access high-performance urban scene segmentation models, run asynchronous video processing jobs, and benchmark mIoU accuracy.
        </p>

        <div className="space-y-3 pt-2 text-xs text-slate-300">
          <div className="flex items-center space-x-3 p-3 rounded-xl bg-slate-900/60 border border-slate-800">
            <CheckCircle2 className="w-5 h-5 text-cyan-400 shrink-0" />
            <div>
              <div className="font-semibold text-slate-100">Full API & Dashboard Access</div>
              <div className="text-[10px] text-slate-400">Process images and multi-frame video feeds</div>
            </div>
          </div>

          <div className="flex items-center space-x-3 p-3 rounded-xl bg-slate-900/60 border border-slate-800">
            <CheckCircle2 className="w-5 h-5 text-purple-400 shrink-0" />
            <div>
              <div className="font-semibold text-slate-100">Saved Segmentation History</div>
              <div className="text-[10px] text-slate-400">Inspect historical perception artifacts</div>
            </div>
          </div>
        </div>
      </div>

      {/* Right Column: Glassmorphic Auth Form */}
      <div className="lg:col-span-6 max-w-md w-full mx-auto space-y-6">
        <div className="text-center sm:text-left space-y-2">
          <h2 className="text-2xl font-bold text-slate-100 font-heading">Register Account</h2>
          <p className="text-xs text-slate-400">Create an account to process scene vision streams</p>
        </div>

        {error && (
          <div className="p-3.5 rounded-xl bg-rose-950/60 border border-rose-800 text-rose-300 text-xs">
            {error}
          </div>
        )}

        <GlassCard hoverEffect glowColor="purple" className="p-6">
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1.5">
                Full Name
              </label>
              <div className="relative">
                <User className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
                <input
                  type="text"
                  required
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  placeholder="Autonomous Engineer"
                  className="w-full glass-input pl-9 pr-3 py-2 text-xs"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1.5">
                Email Address
              </label>
              <div className="relative">
                <Mail className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
                <input
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="engineer@selfdriving.com"
                  className="w-full glass-input pl-9 pr-3 py-2 text-xs"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1.5">
                Password
              </label>
              <div className="relative">
                <Lock className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
                <input
                  type="password"
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="At least 8 characters"
                  className="w-full glass-input pl-9 pr-3 py-2 text-xs"
                />
              </div>

              {strength && (
                <div className="mt-2 flex items-center space-x-2 text-[11px]">
                  <span className="text-slate-400">Strength:</span>
                  <div className="flex-1 bg-slate-900 rounded-full h-1.5 overflow-hidden border border-slate-800">
                    <div className={`h-full ${strength.color} transition-all duration-300 w-full`} />
                  </div>
                  <span className="font-semibold text-slate-200">{strength.label}</span>
                </div>
              )}
            </div>

            <Button
              type="submit"
              variant="primary"
              size="lg"
              isLoading={isSubmitting}
              className="w-full mt-2"
              rightIcon={<ArrowRight className="w-4 h-4" />}
            >
              Create Account
            </Button>

            <div className="text-center text-xs text-slate-400 pt-2 border-t border-slate-800/80">
              Already registered?{' '}
              <Link to="/login" className="text-cyan-400 font-semibold hover:underline">
                Sign In Here
              </Link>
            </div>
          </form>
        </GlassCard>
      </div>
    </div>
  );
};
