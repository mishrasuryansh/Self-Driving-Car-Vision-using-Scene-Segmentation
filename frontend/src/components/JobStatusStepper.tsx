import React, { useEffect, useState } from 'react';
import apiClient from '../services/api';
import { CheckCircle2, Clock, Loader2, AlertCircle, XCircle, Activity, Layers } from 'lucide-react';
import { GlassCard } from './ui/GlassCard';
import { Badge } from './ui/Badge';
import { Button } from './ui/Button';

export interface JobDetails {
  job_id: string;
  user_id: string;
  media_id: string;
  status: 'queued' | 'pending' | 'processing' | 'completed' | 'failed' | 'cancelled';
  progress_percent: number;
  output_path?: string;
  metrics?: {
    fps: number;
    avgInferenceMs: number;
    classDistribution: Record<string, number>;
  };
  error?: string;
}

interface JobStatusStepperProps {
  jobId: string;
  onComplete: (job: JobDetails) => void;
}

export const JobStatusStepper: React.FC<JobStatusStepperProps> = ({ jobId, onComplete }) => {
  const [job, setJob] = useState<JobDetails | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isCancelling, setIsCancelling] = useState<boolean>(false);

  const fetchJobStatus = async () => {
    try {
      const res = await apiClient.get<JobDetails>(`/jobs/${jobId}`);
      setJob(res.data);

      if (res.data.status === 'completed') {
        onComplete(res.data);
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to poll job status.');
    }
  };

  useEffect(() => {
    fetchJobStatus();
    const interval = setInterval(() => {
      if (job?.status !== 'completed' && job?.status !== 'failed' && job?.status !== 'cancelled') {
        fetchJobStatus();
      }
    }, 1000);

    return () => clearInterval(interval);
  }, [jobId, job?.status]);

  const handleCancel = async () => {
    setIsCancelling(true);
    try {
      const res = await apiClient.post<JobDetails>(`/jobs/${jobId}/cancel`);
      setJob(res.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to cancel job.');
    } finally {
      setIsCancelling(false);
    }
  };

  if (!job) {
    return (
      <GlassCard glowColor="purple" className="p-8 text-center space-y-3">
        <Loader2 className="w-8 h-8 text-purple-400 animate-spin mx-auto" />
        <p className="text-xs text-slate-300 font-semibold">Initializing Celery Job Pipeline...</p>
      </GlassCard>
    );
  }

  const isQueued = job.status === 'queued' || job.status === 'pending';
  const isProcessing = job.status === 'processing';
  const isCompleted = job.status === 'completed';
  const isFailed = job.status === 'failed';
  const isCancelled = job.status === 'cancelled';

  return (
    <GlassCard glowColor="purple" className="p-6 space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-4 border-b border-slate-800 pb-4">
        <div>
          <div className="flex items-center space-x-2">
            <h3 className="font-bold text-lg text-slate-100 font-heading">Async Video Stepper</h3>
            <Badge variant={isCompleted ? 'emerald' : isFailed ? 'rose' : 'purple'} dot>
              {job.status.toUpperCase()}
            </Badge>
          </div>
          <p className="text-xs text-slate-400 font-mono mt-0.5">Job ID: {jobId}</p>
        </div>

        {!isCompleted && !isFailed && !isCancelled && (
          <Button
            variant="danger"
            size="sm"
            onClick={handleCancel}
            isLoading={isCancelling}
            leftIcon={<XCircle className="w-3.5 h-3.5" />}
          >
            Cancel Job
          </Button>
        )}
      </div>

      {error && (
        <div className="p-3 rounded-xl bg-rose-950/60 border border-rose-800 text-rose-300 text-xs flex items-center space-x-2">
          <AlertCircle className="w-4 h-4 text-rose-400 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Visual Stepper Steps */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 text-center text-xs">
        <div className={`p-4 rounded-xl border transition-all ${
          isQueued ? 'border-cyan-400 bg-cyan-950/40 shadow-[0_0_15px_rgba(6,182,212,0.2)]' : 'border-slate-800 bg-slate-950/40'
        }`}>
          <Clock className={`w-6 h-6 mx-auto mb-2 ${isQueued ? 'text-cyan-400 animate-pulse' : 'text-slate-500'}`} />
          <div className="font-bold text-slate-200">1. Dispatched & Queued</div>
          <p className="text-[10px] text-slate-400 mt-0.5">Redis Queue Broker</p>
        </div>

        <div className={`p-4 rounded-xl border transition-all ${
          isProcessing ? 'border-purple-400 bg-purple-950/40 shadow-[0_0_15px_rgba(139,92,246,0.2)]' : 'border-slate-800 bg-slate-950/40'
        }`}>
          <Loader2 className={`w-6 h-6 mx-auto mb-2 ${isProcessing ? 'text-purple-400 animate-spin' : 'text-slate-500'}`} />
          <div className="font-bold text-slate-200">2. DeepLabV3+ Processing</div>
          <p className="text-[10px] text-slate-400 mt-0.5">PyTorch Celery Worker</p>
        </div>

        <div className={`p-4 rounded-xl border transition-all ${
          isCompleted ? 'border-emerald-400 bg-emerald-950/40 shadow-[0_0_15px_rgba(16,185,129,0.2)]' : isFailed ? 'border-rose-500 bg-rose-950/40' : 'border-slate-800 bg-slate-950/40'
        }`}>
          {isFailed ? (
            <AlertCircle className="w-6 h-6 mx-auto mb-2 text-rose-400" />
          ) : (
            <CheckCircle2 className={`w-6 h-6 mx-auto mb-2 ${isCompleted ? 'text-emerald-400' : 'text-slate-500'}`} />
          )}
          <div className="font-bold text-slate-200">{isFailed ? 'Processing Failed' : '3. Complete & Cached'}</div>
          <p className="text-[10px] text-slate-400 mt-0.5">Ready for Playback</p>
        </div>
      </div>

      {/* Progress Bar */}
      <div className="space-y-2">
        <div className="flex justify-between text-xs font-semibold text-slate-300">
          <span>Frame Inference Progress</span>
          <span className="text-purple-400 font-bold font-mono">{job.progress_percent.toFixed(1)}%</span>
        </div>
        <div className="w-full bg-slate-950 rounded-full h-3 overflow-hidden border border-slate-800">
          <div
            className="bg-gradient-to-r from-cyan-400 via-blue-500 to-purple-500 h-full transition-all duration-300 rounded-full"
            style={{ width: `${job.progress_percent}%` }}
          />
        </div>
      </div>
    </GlassCard>
  );
};
