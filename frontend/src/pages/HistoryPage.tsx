/**
 * Interactive Segmentation History Page Component (T069).
 *
 * Displays filterable table of all past image and video processing jobs,
 * status badges, progress indicators, and detailed job inspection modal.
 */

import React, { useEffect, useState } from 'react';
import apiClient from '../services/api';
import { JobDetails } from '../components/JobStatusStepper';
import { History, Filter, Loader2, AlertCircle, CheckCircle2, Clock, XCircle } from 'lucide-react';

export const HistoryPage: React.FC = () => {
  const [jobs, setJobs] = useState<JobDetails[]>([]);
  const [filterStatus, setFilterStatus] = useState<string>('all');
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedJob, setSelectedJob] = useState<JobDetails | null>(null);

  const fetchJobs = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const res = await apiClient.get<JobDetails[]>('/jobs');
      setJobs(res.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to retrieve job history.');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchJobs();
  }, []);

  const filteredJobs = jobs.filter((j) => filterStatus === 'all' || j.status === filterStatus);

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'completed':
        return <span className="bg-emerald-950/60 text-emerald-400 border border-emerald-800 px-2.5 py-0.5 rounded-full text-xs font-semibold">Completed</span>;
      case 'processing':
        return <span className="bg-purple-950/60 text-purple-400 border border-purple-800 px-2.5 py-0.5 rounded-full text-xs font-semibold">Processing</span>;
      case 'queued':
      case 'pending':
        return <span className="bg-cyan-950/60 text-cyan-400 border border-cyan-800 px-2.5 py-0.5 rounded-full text-xs font-semibold">Queued</span>;
      case 'failed':
        return <span className="bg-red-950/60 text-red-400 border border-red-800 px-2.5 py-0.5 rounded-full text-xs font-semibold">Failed</span>;
      case 'cancelled':
        return <span className="bg-slate-800 text-slate-400 border border-slate-700 px-2.5 py-0.5 rounded-full text-xs font-semibold">Cancelled</span>;
      default:
        return <span className="bg-slate-800 text-slate-400 px-2.5 py-0.5 rounded-full text-xs">{status}</span>;
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-4 border-b border-slate-800 pb-4">
        <div className="flex items-center space-x-3">
          <History className="w-8 h-8 text-cyan-400" />
          <div>
            <h1 className="text-2xl font-bold">Segmentation History</h1>
            <p className="text-xs text-slate-400">All image and video vision jobs created by your account</p>
          </div>
        </div>

        {/* Filter Dropdown */}
        <div className="flex items-center space-x-2 bg-slate-900 border border-slate-800 px-3 py-1.5 rounded-lg text-xs">
          <Filter className="w-4 h-4 text-slate-400" />
          <span className="text-slate-400 font-medium">Filter Status:</span>
          <select
            value={filterStatus}
            onChange={(e) => setFilterStatus(e.target.value)}
            className="bg-transparent text-slate-200 font-semibold focus:outline-none cursor-pointer"
          >
            <option value="all" className="bg-slate-900">All Jobs</option>
            <option value="completed" className="bg-slate-900">Completed</option>
            <option value="processing" className="bg-slate-900">Processing</option>
            <option value="queued" className="bg-slate-900">Queued</option>
            <option value="failed" className="bg-slate-900">Failed</option>
            <option value="cancelled" className="bg-slate-900">Cancelled</option>
          </select>
        </div>
      </div>

      {error && (
        <div className="p-4 rounded-lg bg-red-950/60 border border-red-800 text-red-300 text-sm flex items-center space-x-3">
          <AlertCircle className="w-5 h-5 text-red-400" />
          <span>{error}</span>
        </div>
      )}

      {isLoading ? (
        <div className="flex items-center justify-center p-12 glass-card">
          <Loader2 className="w-8 h-8 text-cyan-400 animate-spin mr-3" />
          <span className="text-sm text-slate-300">Loading segmentation history...</span>
        </div>
      ) : filteredJobs.length === 0 ? (
        <div className="glass-card p-12 text-center text-slate-500 text-sm">
          No segmentation jobs found matching filter criteria.
        </div>
      ) : (
        <div className="glass-card overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs text-slate-300">
              <thead className="bg-slate-900/80 text-slate-400 uppercase tracking-wider border-b border-slate-800">
                <tr>
                  <th className="p-4">Job ID</th>
                  <th className="p-4">Media ID</th>
                  <th className="p-4">Status</th>
                  <th className="p-4">Progress</th>
                  <th className="p-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {filteredJobs.map((j) => (
                  <tr key={j.job_id} className="hover:bg-slate-900/40 transition">
                    <td className="p-4 font-mono font-medium text-slate-200">{j.job_id.substring(0, 8)}...</td>
                    <td className="p-4 font-mono text-slate-400">{j.media_id ? j.media_id.substring(0, 8) : 'N/A'}</td>
                    <td className="p-4">{getStatusBadge(j.status)}</td>
                    <td className="p-4 font-semibold text-cyan-400">{j.progress_percent.toFixed(0)}%</td>
                    <td className="p-4 text-right">
                      <button
                        onClick={() => setSelectedJob(j)}
                        className="px-3 py-1 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-md font-medium text-xs transition"
                      >
                        Inspect Details
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Details Inspection Modal */}
      {selectedJob && (
        <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="glass-card max-w-lg w-full p-6 space-y-4">
            <div className="flex justify-between items-center border-b border-slate-800 pb-3">
              <h3 className="font-bold text-lg">Job Details: {selectedJob.job_id}</h3>
              <button onClick={() => setSelectedJob(null)} className="text-slate-400 hover:text-white font-bold text-lg">
                &times;
              </button>
            </div>
            <div className="space-y-2 text-xs text-slate-300">
              <p><strong className="text-slate-400">Status:</strong> {selectedJob.status}</p>
              <p><strong className="text-slate-400">Progress:</strong> {selectedJob.progress_percent}%</p>
              <p><strong className="text-slate-400">User ID:</strong> {selectedJob.user_id}</p>
              {selectedJob.output_path && (
                <p><strong className="text-slate-400">Output Artifact:</strong> <span className="font-mono text-cyan-400">{selectedJob.output_path}</span></p>
              )}
              {selectedJob.metrics && (
                <div className="pt-2 border-t border-slate-800 space-y-1">
                  <p><strong className="text-slate-400">Throughput:</strong> {selectedJob.metrics.fps} FPS</p>
                  <p><strong className="text-slate-400">Latency:</strong> {selectedJob.metrics.avgInferenceMs} ms</p>
                </div>
              )}
            </div>
            <button onClick={() => setSelectedJob(null)} className="w-full btn-primary py-2 text-xs">
              Close Details
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
