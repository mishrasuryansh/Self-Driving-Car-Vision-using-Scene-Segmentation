import React, { useState } from 'react';
import { Video, Sparkles, Cpu, Clock, CheckCircle2, AlertCircle } from 'lucide-react';
import { Button } from '../components/ui/Button';
import { GlassCard } from '../components/ui/GlassCard';
import { Badge } from '../components/ui/Badge';
import { JobStatusStepper, JobDetails } from '../components/JobStatusStepper';
import { VideoPlayerWithMetrics } from '../components/VideoPlayerWithMetrics';
import apiClient from '../services/api';

export const UploadVideoPage: React.FC = () => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [modelName, setModelName] = useState<string>('deeplabv3plus_resnet101');
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  const [jobId, setJobId] = useState<string | null>(null);
  const [completedJob, setCompletedJob] = useState<JobDetails | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [dragActive, setDragActive] = useState<boolean>(false);

  const handleFileChange = (file: File) => {
    if (!file.type.startsWith('video/')) {
      setError('Please select a valid MP4/AVI/MOV video file.');
      return;
    }
    setError(null);
    setSelectedFile(file);
    setJobId(null);
    setCompletedJob(null);
  };

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileChange(e.dataTransfer.files[0]);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedFile) return;

    setIsSubmitting(true);
    setError(null);

    const formData = new FormData();
    formData.append('file', selectedFile);
    formData.append('model_name', modelName);

    try {
      const res = await apiClient.post<{ job_id: string }>('/jobs/video', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      setJobId(res.data.job_id);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to dispatch video processing job. Check Redis/Worker status.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="space-y-8 max-w-5xl mx-auto py-2">
      {/* Title Header */}
      <div className="space-y-2 text-center sm:text-left">
        <div className="inline-flex items-center space-x-2">
          <Badge variant="purple" dot>ASYNCHRONOUS PIPELINE</Badge>
          <span className="text-xs text-slate-400">Celery Distributed Queue & Redis Broker</span>
        </div>
        <h1 className="text-3xl sm:text-4xl font-extrabold text-slate-100 font-heading">
          Continuous Video Stream Perception
        </h1>
        <p className="text-xs sm:text-sm text-slate-400">
          Process multi-frame road footage through distributed workers with real-time frame status polling and aggregated analytics.
        </p>
      </div>

      {/* Video Upload Form */}
      {!jobId && (
        <GlassCard hoverEffect glowColor="purple" className="p-6">
          <form onSubmit={handleSubmit} className="space-y-6">
            <div
              onDragEnter={handleDrag}
              onDragLeave={handleDrag}
              onDragOver={handleDrag}
              onDrop={handleDrop}
              className={`rounded-2xl border-2 border-dashed p-8 text-center transition-all ${
                dragActive
                  ? 'border-purple-400 bg-purple-950/30 shadow-[0_0_30px_rgba(139,92,246,0.2)]'
                  : 'border-slate-800 hover:border-purple-500/40 bg-slate-950/50'
              }`}
            >
              {selectedFile ? (
                <div className="space-y-4 py-4">
                  <div className="mx-auto w-14 h-14 rounded-2xl bg-purple-500/10 border border-purple-500/30 flex items-center justify-center text-purple-400">
                    <Video className="w-7 h-7" />
                  </div>
                  <div>
                    <h3 className="text-base font-bold text-slate-200">{selectedFile.name}</h3>
                    <p className="text-xs text-slate-400 mt-1">
                      Size: {(selectedFile.size / 1024 / 1024).toFixed(2)} MB | Format: {selectedFile.type}
                    </p>
                  </div>
                  <Button
                    variant="ghost"
                    size="sm"
                    type="button"
                    onClick={() => setSelectedFile(null)}
                  >
                    Change Video File
                  </Button>
                </div>
              ) : (
                <div className="space-y-4 py-6">
                  <div className="mx-auto w-14 h-14 rounded-2xl bg-purple-500/10 border border-purple-500/30 flex items-center justify-center text-purple-400">
                    <Video className="w-7 h-7" />
                  </div>
                  <div>
                    <h3 className="text-base font-bold text-slate-200">
                      Drop road footage video here
                    </h3>
                    <p className="text-xs text-slate-400 mt-1">
                      Supports MP4, AVI, MOV up to 100 MB
                    </p>
                  </div>
                  <label className="inline-block cursor-pointer">
                    <Button variant="secondary" size="sm" type="button">
                      Browse Video Files
                    </Button>
                    <input
                      type="file"
                      accept="video/*"
                      className="hidden"
                      onChange={(e) => e.target.files?.[0] && handleFileChange(e.target.files[0])}
                    />
                  </label>
                </div>
              )}
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-12 gap-4 items-center pt-2">
              <div className="sm:col-span-8 flex items-center space-x-3 bg-slate-900/80 p-3 rounded-xl border border-slate-800">
                <Cpu className="w-5 h-5 text-purple-400 shrink-0" />
                <div className="flex-1">
                  <label className="block text-[10px] font-semibold uppercase text-slate-400">
                    Target Perception Engine
                  </label>
                  <select
                    value={modelName}
                    onChange={(e) => setModelName(e.target.value)}
                    className="bg-transparent text-xs text-slate-200 font-semibold focus:outline-none w-full"
                  >
                    <option value="deeplabv3plus_resnet101" className="bg-slate-900 text-slate-200">
                      DeepLabV3+ (ResNet-101 ASPP)
                    </option>
                  </select>
                </div>
              </div>

              <div className="sm:col-span-4 flex justify-end">
                <Button
                  variant="primary"
                  size="lg"
                  type="submit"
                  isLoading={isSubmitting}
                  disabled={!selectedFile}
                  className="w-full"
                  leftIcon={<Sparkles className="w-5 h-5" />}
                >
                  Dispatch Job
                </Button>
              </div>
            </div>

            {error && (
              <div className="p-3 rounded-xl bg-rose-950/60 border border-rose-800 text-rose-300 text-xs">
                {error}
              </div>
            )}
          </form>
        </GlassCard>
      )}

      {/* Async Job Status Polling Stepper */}
      {jobId && !completedJob && (
        <JobStatusStepper
          jobId={jobId}
          onComplete={(job) => setCompletedJob(job)}
        />
      )}

      {/* Completed Video Player & Aggregate Perception Metrics */}
      {completedJob && (
        <VideoPlayerWithMetrics job={completedJob} />
      )}
    </div>
  );
};
