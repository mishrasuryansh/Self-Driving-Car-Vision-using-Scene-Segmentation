/**
 * Asynchronous Video Stream Upload & Processing Page (T066 & T067).
 *
 * Provides video drag-and-drop submission, sub-second API queue dispatch,
 * real-time polling status stepper, and output video playback with perception metrics.
 */

import React, { useState } from 'react';
import apiClient from '../services/api';
import { JobStatusStepper, JobDetails } from '../components/JobStatusStepper';
import { VideoPlayerWithMetrics } from '../components/VideoPlayerWithMetrics';
import { Video, Upload, Loader2, AlertCircle, PlayCircle } from 'lucide-react';

export const UploadVideoPage: React.FC = () => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [activeJobId, setActiveJobId] = useState<string | null>(null);
  const [completedJob, setCompletedJob] = useState<JobDetails | null>(null);

  const handleFileChange = (file: File) => {
    if (!file.type.startsWith('video/') && !file.name.match(/\.(mp4|avi|mov)$/i)) {
      setError('Please select a valid MP4, AVI, or MOV video file.');
      return;
    }
    setError(null);
    setSelectedFile(file);
    setActiveJobId(null);
    setCompletedJob(null);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
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

    try {
      const res = await apiClient.post<JobDetails>('/jobs/video', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      setActiveJobId(res.data.job_id);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Video job submission failed.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      <div className="flex items-center space-x-3 border-b border-slate-800 pb-4">
        <Video className="w-8 h-8 text-purple-400" />
        <div>
          <h1 className="text-2xl font-bold">Asynchronous Video Stream Segmentation</h1>
          <p className="text-xs text-slate-400">Celery distributed worker queue with Redis result caching</p>
        </div>
      </div>

      {error && (
        <div className="p-4 rounded-lg bg-red-950/60 border border-red-800 text-red-300 text-sm flex items-center space-x-3">
          <AlertCircle className="w-5 h-5 text-red-400 flex-shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Video Upload Form */}
      {!activeJobId && (
        <form onSubmit={handleSubmit} className="space-y-4">
          <div
            onDragOver={(e) => e.preventDefault()}
            onDrop={handleDrop}
            className="glass-card p-8 border-dashed border-2 border-slate-700 hover:border-purple-400/60 transition text-center space-y-4 cursor-pointer"
          >
            <Upload className="w-10 h-10 mx-auto text-purple-400" />
            <div>
              <h3 className="text-lg font-medium text-slate-200">Drag and drop dashcam video file</h3>
              <p className="text-xs text-slate-400 mt-1">Supports MP4, AVI, MOV up to 200MB (max 2 minutes)</p>
            </div>
            <input
              type="file"
              accept="video/*"
              id="video-upload-input"
              onChange={(e) => e.target.files?.[0] && handleFileChange(e.target.files[0])}
              className="hidden"
            />
            <label htmlFor="video-upload-input" className="inline-block btn-primary bg-gradient-to-r from-purple-600 to-indigo-600 text-xs cursor-pointer">
              Browse Video File
            </label>

            {selectedFile && (
              <p className="text-xs text-purple-400 font-medium">Selected: {selectedFile.name} ({(selectedFile.size / 1024 / 1024).toFixed(2)} MB)</p>
            )}
          </div>

          {selectedFile && (
            <button
              type="submit"
              disabled={isSubmitting}
              className="w-full btn-primary bg-gradient-to-r from-purple-600 to-indigo-600 py-3 text-base flex items-center justify-center space-x-2"
            >
              {isSubmitting ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" />
                  <span>Submitting to Celery Queue...</span>
                </>
              ) : (
                <>
                  <PlayCircle className="w-5 h-5" />
                  <span>Start Async Video Segmentation</span>
                </>
              )}
            </button>
          )}
        </form>
      )}

      {/* Active Job Status Polling Stepper (T066) */}
      {activeJobId && !completedJob && (
        <JobStatusStepper
          jobId={activeJobId}
          onComplete={(completedData) => setCompletedJob(completedData)}
        />
      )}

      {/* Completed Video Output Player & Metrics (T067) */}
      {completedJob && (
        <VideoPlayerWithMetrics job={completedJob} />
      )}
    </div>
  );
};
