import React, { useState } from 'react';
import { useNavigate, useLocation, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { ShieldCheck, Lock, Mail, ArrowRight, Sparkles, CheckCircle2 } from 'lucide-react';
import { Button } from '../components/ui/Button';
import { GlassCard } from '../components/ui/GlassCard';
import { Badge } from '../components/ui/Badge';

export const LoginPage: React.FC = () => {
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [rememberMe, setRememberMe] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const from = (location.state as any)?.from?.pathname || '/';

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setIsSubmitting(true);

    try {
      await login(email, password);
      navigate(from, { replace: true });
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Invalid email or password. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-center min-h-[calc(100vh-140px)] max-w-6xl mx-auto py-4">
      {/* Left Column: Visual AI Branding Banner */}
      <div className="lg:col-span-6 space-y-6 hidden lg:block pr-6 border-r border-slate-800/80">
        <Badge variant="cyan" dot>AUTONOMOUS PERCEPTION SUITE</Badge>

        <h1 className="text-4xl font-extrabold text-slate-100 font-heading leading-tight">
          Secure Access to{' '}
          <span className="bg-gradient-to-r from-cyan-400 to-purple-400 bg-clip-text text-transparent">
            Vision Intelligence
          </span>
        </h1>

        <p className="text-sm text-slate-400 leading-relaxed">
          Log in to manage real-time scene segmentation jobs, monitor model inference latency, and inspect Cityscapes perception analytics.
        </p>

        <div className="space-y-3 pt-2 text-xs text-slate-300">
          <div className="flex items-center space-x-3 p-3 rounded-xl bg-slate-900/60 border border-slate-800">
            <CheckCircle2 className="w-5 h-5 text-cyan-400 shrink-0" />
            <div>
              <div className="font-semibold text-slate-100">DeepLabV3+ ASPP Architecture</div>
              <div className="text-[10px] text-slate-400">19-class semantic urban scene understanding</div>
            </div>
          </div>

          <div className="flex items-center space-x-3 p-3 rounded-xl bg-slate-900/60 border border-slate-800">
            <CheckCircle2 className="w-5 h-5 text-purple-400 shrink-0" />
            <div>
              <div className="font-semibold text-slate-100">Sub-50ms Inference Target</div>
              <div className="text-[10px] text-slate-400">Optimized real-time GPU throughput</div>
            </div>
          </div>

          <div className="flex items-center space-x-3 p-3 rounded-xl bg-slate-900/60 border border-slate-800">
            <CheckCircle2 className="w-5 h-5 text-emerald-400 shrink-0" />
            <div>
              <div className="font-semibold text-slate-100">Celery Distributed Queue</div>
              <div className="text-[10px] text-slate-400">Asynchronous multi-frame video streaming</div>
            </div>
          </div>
        </div>
      </div>

      {/* Right Column: Glassmorphic Auth Form */}
      <div className="lg:col-span-6 max-w-md w-full mx-auto space-y-6">
        <div className="text-center sm:text-left space-y-2">
          <h2 className="text-2xl font-bold text-slate-100 font-heading">Sign In</h2>
          <p className="text-xs text-slate-400">Enter your credentials to manage perception jobs</p>
        </div>

        {error && (
          <div className="p-3.5 rounded-xl bg-rose-950/60 border border-rose-800 text-rose-300 text-xs">
            {error}
          </div>
        )}

        <GlassCard hoverEffect glowColor="cyan" className="p-6">
          <form onSubmit={handleSubmit} className="space-y-4">
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
                  placeholder="pilot@selfdriving.com"
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
                  placeholder="••••••••"
                  className="w-full glass-input pl-9 pr-3 py-2 text-xs"
                />
              </div>
            </div>

            <div className="flex items-center justify-between text-xs pt-1">
              <label className="flex items-center space-x-2 text-slate-400 cursor-pointer">
                <input
                  type="checkbox"
                  checked={rememberMe}
                  onChange={(e) => setRememberMe(e.target.checked)}
                  className="rounded border-slate-700 bg-slate-900 text-cyan-400 focus:ring-0"
                />
                <span>Remember me</span>
              </label>

              <span className="text-cyan-400 text-[11px]">JWT Auth Guarded</span>
            </div>

            <Button
              type="submit"
              variant="primary"
              size="lg"
              isLoading={isSubmitting}
              className="w-full mt-2"
              rightIcon={<ArrowRight className="w-4 h-4" />}
            >
              Sign In
            </Button>

            <div className="text-center text-xs text-slate-400 pt-2 border-t border-slate-800/80">
              Don't have an account yet?{' '}
              <Link to="/register" className="text-cyan-400 font-semibold hover:underline">
                Create Account
              </Link>
            </div>
          </form>
        </GlassCard>
      </div>
    </div>
  );
};
