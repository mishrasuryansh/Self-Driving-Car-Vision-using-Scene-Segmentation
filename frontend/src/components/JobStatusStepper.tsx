/**
 * Asynchronous Video Job Status Polling & Stepper Component (T066).
 *
 * Polling component for tracking video jobs through queued -> processing -> completed/failed states,
 * rendering a visual stepper, progress bar, and cancellation controls.
 */

import React, { useEffect, useState } from 'react';
import apiClient from '../services/api';
import { CheckCircle2, Clock, Loader2, AlertCircle, XCircle } from 'lucide-react';

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
      <div className="flex items-center justify-center p-8 glass-card">
        <Loader2 className="w-6 h-6 text-purple-400 animate-spin mr-3" />
        <span className="text-sm text-slate-300">Initializing job status...</span>
      </div>
    );
  }

  const isQueued = job.status === 'queued' || job.status === 'pending';
  const isProcessing = job.status === 'processing';
  const isCompleted = job.status === 'completed';
  const isFailed = job.status === 'failed';
  const isCancelled = job.status === 'cancelled';

  return (
    <div className="glass-card p-6 space-y-6">
      <div className="flex items-center justify-between border-b border-slate-800 pb-4">
        <div>
          <h3 className="font-semibold text-lg text-slate-100">Async Processing Stepper</h3>
          <p className="text-xs text-slate-400">Job ID: {jobId}</p>
        </div>

        {/* Cancellation Button */}
        {!isCompleted && !isFailed && !isCancelled && (
          <button
            onClick={handleCancel}
            disabled={isCancelling}
            className="px-3 py-1.5 rounded-lg border border-red-800/60 bg-red-950/40 text-red-300 text-xs hover:bg-red-900/60 transition flex items-center space-x-1.5"
          >
            {isCancelling ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <XCircle className="w-3.5 h-3.5" />}
            <span>Cancel Job</span>
          </button>
        )}
      </div>

      {error && (
        <div className="p-3 rounded-lg bg-red-950/60 border border-red-800 text-red-300 text-xs flex items-center space-x-2">
          <AlertCircle className="w-4 h-4 text-red-400" />
          <span>{error}</span>
        </div>
      )}

      {/* Visual Stepper Steps */}
      <div className="grid grid-cols-3 gap-2 text-center text-xs">
        <div className={`p-3 rounded-lg border ${isQueued ? 'border-cyan-400 bg-cyan-950/30' : isCompleted || isProcessing ? 'border-slate-700 bg-slate-900' : 'border-slate-800'}`}>
          <Clock className={`w-5 h-5 mx-auto mb-1 ${isQueued ? 'text-cyan-400 animate-pulse' : 'text-slate-500'}`} />
          <span className="font-medium text-slate-200">1. Queued</span>
        </div>

        <div className={`p-3 rounded-lg border ${isProcessing ? 'border-purple-400 bg-purple-950/30' : isCompleted ? 'border-slate-700 bg-slate-900' : 'border-slate-800'}`}>
          <Loader2 className={`w-5 h-5 mx-auto mb-1 ${isProcessing ? 'text-purple-400 animate-spin' : 'text-slate-500'}`} />
          <span className="font-medium text-slate-200">2. Processing</span>
        </div>

        <div className={`p-3 rounded-lg border ${isCompleted ? 'border-emerald-400 bg-emerald-950/30' : isFailed ? 'border-red-500 bg-red-950/30' : 'border-slate-800'}`}>
          {isFailed ? (
            <AlertCircle className="w-5 h-5 mx-auto mb-1 text-red-400" />
          ) : (
            <CheckCircle2 className={`w-5 h-5 mx-auto mb-1 ${isCompleted ? 'text-emerald-400' : 'text-slate-500'}`} />
          )}
          <span className="font-medium text-slate-200">{isFailed ? 'Failed' : '3. Complete'}</span>
        </div>
      </div>

      {/* Progress Bar */}
      <div className="space-y-1.5">
        <div className="flex justify-between text-xs font-medium text-slate-300">
          <span>Processing Progress</span>
          <span className="text-purple-400 font-bold">{job.progress_percent.toFixed(1)}%</span>
        </div>
        <div className="w-full bg-slate-900 rounded-full h-3 overflow-hidden border border-slate-800">
          <div
            className="bg-gradient-to-r from-cyan-400 via-blue-500 to-purple-500 h-full transition-all duration-300 rounded-full"
            style={{ width: `${job.progress_percent}%` }}
          />
        </div>
      </div>
    </div>
  );
};
