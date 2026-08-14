/**
 * Main Perception Dashboard & Quick Upload Hub Component (T060, T077).
 */

import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import apiClient from '../services/api';
import { ResultViewer } from '../components/ResultViewer';
import { Camera, Video, Activity, ShieldCheck, Cpu, Upload, Zap, Loader2, PlayCircle } from 'lucide-react';

export const DashboardPage: React.FC = () => {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState<'image' | 'video'>('image');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [modelId, setModelId] = useState<string>('deeplabv3_resnet101');
  const [isProcessing, setIsProcessing] = useState<boolean>(false);
  const [quickResult, setQuickResult] = useState<any>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);

  const handleFileSelect = (file: File) => {
    setSelectedFile(file);
    setPreviewUrl(URL.createObjectURL(file));
    setQuickResult(null);
  };

  const handleQuickUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedFile) return;

    setIsProcessing(true);
    const formData = new FormData();
    formData.append('file', selectedFile);
    formData.append('model_id', modelId);

    try {
      if (activeTab === 'image') {
        const res = await apiClient.post('/inference/segment', formData, {
          headers: { 'Content-Type': 'multipart/form-data' },
        });
        setQuickResult(res.data);
      } else {
        const res = await apiClient.post('/jobs/video', formData, {
          headers: { 'Content-Type': 'multipart/form-data' },
        });
        navigate('/upload/video');
      }
    } catch (err) {
      console.error('Quick upload error:', err);
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div className="space-y-8">
      {/* Header Banner */}
      <div className="glass-card p-8 text-center space-y-4">
        <h1 className="text-3xl sm:text-4xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 via-blue-500 to-purple-500">
          Autonomous Vehicle Scene Segmentation
        </h1>
        <p className="text-slate-400 max-w-2xl mx-auto text-sm">
          High-performance semantic segmentation platform. Classify road environments, vehicles, pedestrians, lanes, and obstacles in real-time.
        </p>
      </div>

      {/* Quick Upload Widget (T077) */}
      <div className="glass-card p-6 space-y-6">
        <div className="flex flex-wrap items-center justify-between border-b border-slate-800 pb-3 gap-2">
          <div className="flex items-center space-x-2">
            <Upload className="w-5 h-5 text-cyan-400" />
            <h3 className="font-semibold text-lg text-slate-100">Quick Upload & Perception Launch</h3>
          </div>

          <div className="flex items-center space-x-2 bg-slate-900 p-1 rounded-lg border border-slate-800 text-xs">
            <button
              onClick={() => { setActiveTab('image'); setSelectedFile(null); setQuickResult(null); }}
              className={`px-3 py-1.5 rounded-md font-semibold transition ${activeTab === 'image' ? 'bg-cyan-500 text-white' : 'text-slate-400 hover:text-white'}`}
            >
              Image
            </button>
            <button
              onClick={() => { setActiveTab('video'); setSelectedFile(null); setQuickResult(null); }}
              className={`px-3 py-1.5 rounded-md font-semibold transition ${activeTab === 'video' ? 'bg-purple-500 text-white' : 'text-slate-400 hover:text-white'}`}
            >
              Video Stream
            </button>
          </div>
        </div>

        <form onSubmit={handleQuickUpload} className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="md:col-span-2 border-dashed border-2 border-slate-700 hover:border-cyan-400/60 p-4 rounded-lg text-center space-y-2 cursor-pointer bg-slate-900/40">
              <input
                type="file"
                accept={activeTab === 'image' ? 'image/*' : 'video/*'}
                id="quick-file-input"
                onChange={(e) => e.target.files?.[0] && handleFileSelect(e.target.files[0])}
                className="hidden"
              />
              <label htmlFor="quick-file-input" className="cursor-pointer block">
                <Upload className="w-6 h-6 mx-auto text-slate-400 mb-1" />
                <span className="text-xs font-medium text-slate-200">
                  {selectedFile ? selectedFile.name : `Select ${activeTab === 'image' ? 'road image' : 'dashcam video'}`}
                </span>
              </label>
            </div>

            {/* Model Selector Dropdown (T074) */}
            <div className="space-y-1">
              <label className="block text-xs font-medium text-slate-400">Model Architecture</label>
              <select
                value={modelId}
                onChange={(e) => setModelId(e.target.value)}
                className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-xs text-slate-200 focus:border-cyan-400 focus:outline-none cursor-pointer"
              >
                <option value="deeplabv3_resnet101">DeepLabV3+ (ResNet-101 ASPP)</option>
                <option value="deeplabv3_mobilenet_v3">DeepLabV3+ (MobileNetV3)</option>
              </select>
            </div>
          </div>

          {selectedFile && (
            <button
              type="submit"
              disabled={isProcessing}
              className="w-full btn-primary py-2.5 text-xs flex items-center justify-center space-x-2"
            >
              {isProcessing ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span>Processing Scene Segmentation...</span>
                </>
              ) : (
                <>
                  {activeTab === 'image' ? <Zap className="w-4 h-4" /> : <PlayCircle className="w-4 h-4" />}
                  <span>Run Quick Segmentation</span>
                </>
              )}
            </button>
          )}
        </form>

        {/* Quick Result Viewer */}
        {quickResult && previewUrl && (
          <ResultViewer
            mediaType={activeTab}
            originalUrl={previewUrl}
            resultUrl={quickResult.output_path || previewUrl}
            metrics={quickResult.metrics}
          />
        )}
      </div>

      {/* Feature Highlight Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="glass-card p-6 space-y-3">
          <div className="flex items-center space-x-3 text-cyan-400">
            <Cpu className="w-6 h-6" />
            <h3 className="font-bold text-lg text-slate-100">DeepLabV3+ ASPP</h3>
          </div>
          <p className="text-xs text-slate-400">
            Multi-scale receptive fields for fine-grained pixel classification.
          </p>
        </div>

        <div className="glass-card p-6 space-y-3">
          <div className="flex items-center space-x-3 text-blue-400">
            <Activity className="w-6 h-6" />
            <h3 className="font-bold text-lg text-slate-100">Sub-50ms Inference</h3>
          </div>
          <p className="text-xs text-slate-400">
            Optimized pipeline delivering >30 FPS real-time segmentation performance.
          </p>
        </div>

        <div className="glass-card p-6 space-y-3">
          <div className="flex items-center space-x-3 text-purple-400">
            <ShieldCheck className="w-6 h-6" />
            <h3 className="font-bold text-lg text-slate-100">Celery Async Queue</h3>
          </div>
          <p className="text-xs text-slate-400">
            Distributed worker queue with 60s Redis polling cache for long video streams.
          </p>
        </div>
      </div>
    </div>
  );
};
