import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import apiClient from '../services/api';
import { JobDetails } from '../components/JobStatusStepper';
import { History, Filter, Search, Eye, Download, Layers, Sparkles, Image as ImageIcon, Video, AlertCircle } from 'lucide-react';
import { GlassCard } from '../components/ui/GlassCard';
import { Badge } from '../components/ui/Badge';
import { Button } from '../components/ui/Button';
import { Spinner } from '../components/Spinner';

export const HistoryPage: React.FC = () => {
  const [jobs, setJobs] = useState<JobDetails[]>([]);
  const [filterStatus, setFilterStatus] = useState<string>('all');
  const [searchTerm, setSearchTerm] = useState<string>('');
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
      setError(err.response?.data?.detail || 'Failed to retrieve segmentation job history.');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchJobs();
  }, []);

  const filteredJobs = jobs.filter((j) => {
    const matchesStatus = filterStatus === 'all' || j.status === filterStatus;
    const matchesSearch = j.job_id.toLowerCase().includes(searchTerm.toLowerCase()) ||
                          (j.media_id && j.media_id.toLowerCase().includes(searchTerm.toLowerCase()));
    return matchesStatus && matchesSearch;
  });

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'completed':
        return <Badge variant="emerald" dot>Completed</Badge>;
      case 'processing':
        return <Badge variant="purple" dot>Processing</Badge>;
      case 'queued':
      case 'pending':
        return <Badge variant="cyan" dot>Queued</Badge>;
      case 'failed':
        return <Badge variant="rose" dot>Failed</Badge>;
      case 'cancelled':
        return <Badge variant="slate">Cancelled</Badge>;
      default:
        return <Badge variant="slate">{status}</Badge>;
    }
  };

  return (
    <div className="space-y-8 max-w-6xl mx-auto py-2">
      {/* Header & Controls Bar */}
      <div className="flex flex-wrap items-center justify-between gap-4 border-b border-slate-800 pb-4">
        <div className="flex items-center space-x-3">
          <div className="p-2.5 rounded-2xl bg-cyan-500/10 border border-cyan-500/20 text-cyan-400">
            <History className="w-6 h-6" />
          </div>
          <div>
            <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-100 font-heading">
              Perception Job History
            </h1>
            <p className="text-xs text-slate-400">
              Filter, search, and inspect past image and video segmentation jobs
            </p>
          </div>
        </div>

        {/* Search & Filter Bar */}
        <div className="flex flex-wrap items-center gap-3">
          {/* Search Input */}
          <div className="relative">
            <Search className="w-3.5 h-3.5 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              placeholder="Search by Job ID..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="glass-input pl-8 pr-3 py-1.5 text-xs w-48 focus:w-60 transition-all"
            />
          </div>

          {/* Status Filter */}
          <div className="flex items-center space-x-2 bg-slate-900/90 border border-slate-800 px-3 py-1.5 rounded-xl text-xs">
            <Filter className="w-3.5 h-3.5 text-cyan-400 shrink-0" />
            <select
              value={filterStatus}
              onChange={(e) => setFilterStatus(e.target.value)}
              className="bg-transparent text-slate-200 font-semibold focus:outline-none cursor-pointer text-xs"
            >
              <option value="all" className="bg-slate-900 text-slate-200">All Statuses</option>
              <option value="completed" className="bg-slate-900 text-slate-200">Completed</option>
              <option value="processing" className="bg-slate-900 text-slate-200">Processing</option>
              <option value="queued" className="bg-slate-900 text-slate-200">Queued</option>
              <option value="failed" className="bg-slate-900 text-slate-200">Failed</option>
              <option value="cancelled" className="bg-slate-900 text-slate-200">Cancelled</option>
            </select>
          </div>
        </div>
      </div>

      {error && (
        <div className="p-4 rounded-xl bg-rose-950/60 border border-rose-800 text-rose-300 text-xs flex items-center space-x-2">
          <AlertCircle className="w-4 h-4 text-rose-400 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {isLoading ? (
        <GlassCard className="p-12 text-center">
          <Spinner size="lg" label="Loading perception history records..." />
        </GlassCard>
      ) : filteredJobs.length === 0 ? (
        /* Empty State */
        <GlassCard glowColor="cyan" className="p-12 text-center space-y-4 max-w-md mx-auto">
          <div className="mx-auto w-16 h-16 rounded-2xl bg-cyan-500/10 border border-cyan-500/30 flex items-center justify-center text-cyan-400">
            <Layers className="w-8 h-8 animate-pulse" />
          </div>
          <div>
            <h3 className="text-lg font-bold text-slate-100 font-heading">No perception jobs found</h3>
            <p className="text-xs text-slate-400 mt-1">
              Upload your first urban road scene to begin real-time DeepLabV3+ segmentation.
            </p>
          </div>
          <Link to="/upload/image">
            <Button variant="primary" size="md" leftIcon={<ImageIcon className="w-4 h-4" />}>
              Analyze an Image
            </Button>
          </Link>
        </GlassCard>
      ) : (
        /* Job Records Table */
        <GlassCard hoverEffect glowColor="cyan" className="overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs text-slate-300">
              <thead className="bg-slate-950/80 text-slate-400 uppercase tracking-wider border-b border-slate-800/80 font-semibold">
                <tr>
                  <th className="p-4">Job ID</th>
                  <th className="p-4">Media Identifier</th>
                  <th className="p-4">Status</th>
                  <th className="p-4">Inference Progress</th>
                  <th className="p-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {filteredJobs.map((j) => (
                  <tr key={j.job_id} className="hover:bg-slate-900/50 transition">
                    <td className="p-4 font-mono font-semibold text-slate-200">
                      {j.job_id.substring(0, 10)}...
                    </td>
                    <td className="p-4 font-mono text-slate-400">
                      {j.media_id ? j.media_id.substring(0, 10) : 'N/A'}
                    </td>
                    <td className="p-4">{getStatusBadge(j.status)}</td>
                    <td className="p-4">
                      <div className="flex items-center space-x-2">
                        <div className="w-24 bg-slate-950 rounded-full h-1.5 overflow-hidden border border-slate-800">
                          <div
                            className="bg-gradient-to-r from-cyan-400 to-blue-500 h-full rounded-full"
                            style={{ width: `${j.progress_percent}%` }}
                          />
                        </div>
                        <span className="font-mono text-[11px] text-cyan-400 font-bold">
                          {j.progress_percent.toFixed(0)}%
                        </span>
                      </div>
                    </td>
                    <td className="p-4 text-right">
                      <Button
                        variant="secondary"
                        size="sm"
                        onClick={() => setSelectedJob(j)}
                        leftIcon={<Eye className="w-3.5 h-3.5 text-cyan-400" />}
                      >
                        Inspect
                      </Button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </GlassCard>
      )}

      {/* Details Inspection Modal */}
      {selectedJob && (
        <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-md flex items-center justify-center p-4">
          <GlassCard glowColor="cyan" className="max-w-lg w-full p-6 space-y-5 border-cyan-500/30">
            <div className="flex justify-between items-center border-b border-slate-800 pb-3">
              <div className="flex items-center space-x-2">
                <Sparkles className="w-5 h-5 text-cyan-400" />
                <h3 className="font-bold text-lg font-heading text-slate-100">Job Metadata Details</h3>
              </div>
              <button
                onClick={() => setSelectedJob(null)}
                className="text-slate-400 hover:text-white p-1 rounded-lg hover:bg-slate-800"
              >
                ✕
              </button>
            </div>

            <div className="space-y-3 text-xs text-slate-300">
              <div className="flex justify-between p-2.5 rounded-xl bg-slate-900/60 border border-slate-800">
                <span className="text-slate-400 font-medium">Job Identifier:</span>
                <span className="font-mono font-bold text-cyan-400">{selectedJob.job_id}</span>
              </div>

              <div className="flex justify-between p-2.5 rounded-xl bg-slate-900/60 border border-slate-800">
                <span className="text-slate-400 font-medium">Status:</span>
                <div>{getStatusBadge(selectedJob.status)}</div>
              </div>

              <div className="flex justify-between p-2.5 rounded-xl bg-slate-900/60 border border-slate-800">
                <span className="text-slate-400 font-medium">Progress:</span>
                <span className="font-mono font-bold text-slate-200">{selectedJob.progress_percent}%</span>
              </div>

              {selectedJob.output_path && (
                <div className="p-2.5 rounded-xl bg-slate-900/60 border border-slate-800 space-y-1">
                  <span className="text-slate-400 font-medium block">Output Artifact Path:</span>
                  <span className="font-mono text-cyan-400 break-all">{selectedJob.output_path}</span>
                </div>
              )}

              {selectedJob.metrics && (
                <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800 space-y-1.5">
                  <span className="text-slate-400 font-semibold uppercase text-[10px] block">Perception Performance</span>
                  <div className="flex justify-between font-mono">
                    <span>Throughput: <strong className="text-cyan-400">{selectedJob.metrics.fps} FPS</strong></span>
                    <span>Latency: <strong className="text-purple-400">{selectedJob.metrics.avgInferenceMs} ms</strong></span>
                  </div>
                </div>
              )}
            </div>

            <Button
              variant="primary"
              size="md"
              onClick={() => setSelectedJob(null)}
              className="w-full"
            >
              Close Details
            </Button>
          </GlassCard>
        </div>
      )}
    </div>
  );
};
