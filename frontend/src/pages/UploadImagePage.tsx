/**
 * Synchronous Image Scene Segmentation Upload Page (T064).
 *
 * Provides drag-and-drop file upload, preview, inference submission,
 * and interactive mask overlay visualization.
 */

import React, { useState } from 'react';
import apiClient from '../services/api';
import { SegmentMaskOverlay } from '../components/SegmentMaskOverlay';
import { Camera, Upload, Loader2, AlertCircle, Zap, Clock, Activity } from 'lucide-react';

interface SegmentationResult {
  task_id: string;
  media_id: string;
  status: string;
  output_path: string;
  metrics?: {
    fps: number;
    avgInferenceMs: number;
    classDistribution: Record<string, number>;
  };
}

export const UploadImagePage: React.FC = () => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [isUploading, setIsUploading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<SegmentationResult | null>(null);

  const handleFileChange = (file: File) => {
    if (!file.type.startsWith('image/')) {
      setError('Please select a valid image file (JPEG, PNG, WEBP).');
      return;
    }
    setError(null);
    setSelectedFile(file);
    setPreviewUrl(URL.createObjectURL(file));
    setResult(null);
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

    setIsUploading(true);
    setError(null);

    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
      const res = await apiClient.post<SegmentationResult>('/inference/segment', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      setResult(res.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Inference processing failed. Please try again.');
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      <div className="flex items-center space-x-3 border-b border-slate-800 pb-4">
        <Camera className="w-8 h-8 text-cyan-400" />
        <div>
          <h1 className="text-2xl font-bold">Image Scene Segmentation</h1>
          <p className="text-xs text-slate-400">Synchronous real-time DeepLabV3+ segmentation</p>
        </div>
      </div>

      {error && (
        <div className="p-4 rounded-lg bg-red-950/60 border border-red-800 text-red-300 text-sm flex items-center space-x-3">
          <AlertCircle className="w-5 h-5 text-red-400 flex-shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Upload Dropzone */}
      <form onSubmit={handleSubmit} className="space-y-4">
        <div
          onDragOver={(e) => e.preventDefault()}
          onDrop={handleDrop}
          className="glass-card p-8 border-dashed border-2 border-slate-700 hover:border-cyan-400/60 transition text-center space-y-4 cursor-pointer"
        >
          <Upload className="w-10 h-10 mx-auto text-cyan-400" />
          <div>
            <h3 className="text-lg font-medium text-slate-200">Drag and drop road scene image</h3>
            <p className="text-xs text-slate-400 mt-1">Supports JPEG, PNG, WEBP up to 10MB</p>
          </div>
          <input
            type="file"
            accept="image/*"
            id="file-upload-input"
            onChange={(e) => e.target.files?.[0] && handleFileChange(e.target.files[0])}
            className="hidden"
          />
          <label htmlFor="file-upload-input" className="inline-block btn-primary text-xs cursor-pointer">
            Browse Image File
          </label>

          {selectedFile && (
            <p className="text-xs text-cyan-400 font-medium">Selected: {selectedFile.name} ({(selectedFile.size / 1024 / 1024).toFixed(2)} MB)</p>
          )}
        </div>

        {selectedFile && !result && (
          <button
            type="submit"
            disabled={isUploading}
            className="w-full btn-primary py-3 text-base flex items-center justify-center space-x-2"
          >
            {isUploading ? (
              <>
                <Loader2 className="w-5 h-5 animate-spin" />
                <span>Running Scene Segmentation Inference...</span>
              </>
            ) : (
              <>
                <Zap className="w-5 h-5" />
                <span>Run Scene Segmentation</span>
              </>
            )}
          </button>
        )}
      </form>

      {/* Inference Result Display (T065) */}
      {result && previewUrl && (
        <div className="space-y-6">
          {/* Section 8.2 Metrics Cards */}
          {result.metrics && (
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div className="glass-card p-4 flex items-center space-x-4">
                <Activity className="w-8 h-8 text-cyan-400" />
                <div>
                  <div className="text-xs text-slate-400 font-medium">Inference Throughput</div>
                  <div className="text-xl font-bold text-slate-100">{result.metrics.fps.toFixed(1)} FPS</div>
                </div>
              </div>

              <div className="glass-card p-4 flex items-center space-x-4">
                <Clock className="w-8 h-8 text-purple-400" />
                <div>
                  <div className="text-xs text-slate-400 font-medium">Average Frame Latency</div>
                  <div className="text-xl font-bold text-slate-100">{result.metrics.avgInferenceMs.toFixed(2)} ms</div>
                </div>
              </div>
            </div>
          )}

          {/* Interactive Mask Overlay */}
          <SegmentMaskOverlay
            originalUrl={previewUrl}
            maskUrl={result.output_path || previewUrl}
            classDistribution={result.metrics?.classDistribution}
          />
        </div>
      )}
    </div>
  );
};
