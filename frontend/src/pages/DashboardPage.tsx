import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { HeroVisualization } from '../components/three/HeroVisualization';
import { Button } from '../components/ui/Button';
import { GlassCard } from '../components/ui/GlassCard';
import { Badge } from '../components/ui/Badge';
import { StatCard } from '../components/ui/StatCard';
import { Upload, Image as ImageIcon, Video, Cpu, Activity, ShieldCheck, ArrowRight, CheckCircle2, Zap, Layers, Sparkles } from 'lucide-react';
import apiClient from '../services/api';

export const DashboardPage: React.FC = () => {
  const navigate = useNavigate();
  const [dragActive, setDragActive] = useState<boolean>(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [isProcessing, setIsProcessing] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const handleFileChange = (file: File) => {
    if (!file.type.startsWith('image/')) {
      setError('Please select a valid image file (JPG, PNG).');
      return;
    }
    setError(null);
    setSelectedFile(file);
    setPreviewUrl(URL.createObjectURL(file));
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

  const handleQuickRunPerception = async () => {
    if (!selectedFile) return;
    setIsProcessing(true);
    setError(null);

    try {
      const uploadData = new FormData();
      uploadData.append('file', selectedFile);

      const uploadRes = await apiClient.post('/media/upload', uploadData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      const mediaId = uploadRes.data.id;

      const segRes = await apiClient.post('/inference/segment', { media_id: mediaId });
      const taskId = segRes.data.task_id;

      const taskRes = await apiClient.get(`/inference/tasks/${taskId}`);
      const taskData = taskRes.data;

      const rawPath = taskData.output_path || '';
      const filename = rawPath.split(/[\/\\]/).pop() || '';
      const resultImageUrl = filename ? `/storage/outputs/${filename}` : previewUrl || '';

      navigate('/upload/image', {
        state: {
          initialResult: {
            ...taskData,
            resultImageUrl,
          },
          initialFileUrl: previewUrl,
        },
      });
    } catch (err: any) {
      setError(
        err.response?.data?.detail ||
          err.response?.data?.error?.message ||
          'Inference failed. Please ensure backend services are running.'
      );
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div className="space-y-16 py-4">
      {/* HERO SECTION */}
      <section className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-center">
        {/* Left Hero Content */}
        <div className="lg:col-span-6 space-y-6">
          <div className="inline-flex items-center space-x-2">
            <Badge variant="cyan" dot size="md">
              AI PERCEPTION PLATFORM
            </Badge>
            <span className="text-xs text-slate-400 font-medium">DeepLabV3+ Architecture</span>
          </div>

          <h1 className="text-4xl sm:text-5xl lg:text-6xl font-extrabold text-slate-100 tracking-tight leading-[1.1] font-heading">
            See the Road.{' '}
            <span className="bg-gradient-to-r from-cyan-400 via-blue-400 to-purple-400 bg-clip-text text-transparent">
              Understand the World.
            </span>
          </h1>

          <p className="text-slate-300 text-base sm:text-lg leading-relaxed max-w-xl">
            DeepLabV3+ powered semantic segmentation for real-time understanding of roads, vehicles, pedestrians and surrounding environments.
          </p>

          <div className="flex flex-wrap items-center gap-4 pt-2">
            <Link to="/upload/image">
              <Button
                variant="primary"
                size="lg"
                leftIcon={<ImageIcon className="w-5 h-5" />}
                rightIcon={<ArrowRight className="w-4 h-4" />}
              >
                Analyze Image
              </Button>
            </Link>

            <Link to="/upload/video">
              <Button
                variant="secondary"
                size="lg"
                leftIcon={<Video className="w-5 h-5 text-purple-400" />}
              >
                Analyze Video
              </Button>
            </Link>
          </div>

          {/* Key Tech Badges */}
          <div className="pt-4 flex flex-wrap gap-3 text-xs text-slate-400 border-t border-slate-800/80">
            <span className="flex items-center gap-1.5">
              <CheckCircle2 className="w-4 h-4 text-emerald-400" /> Cityscapes Trained
            </span>
            <span className="flex items-center gap-1.5">
              <CheckCircle2 className="w-4 h-4 text-emerald-400" /> ResNet-101 Backbone
            </span>
            <span className="flex items-center gap-1.5">
              <CheckCircle2 className="w-4 h-4 text-emerald-400" /> 19 Semantic Classes
            </span>
          </div>
        </div>

        {/* Right Hero 3D Experience */}
        <div className="lg:col-span-6">
          <HeroVisualization />
        </div>
      </section>

      {/* CREDIBILITY METRICS BAR */}
      <section className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <StatCard
          icon={<CheckCircle2 className="w-6 h-6" />}
          label="Pixel Accuracy"
          value="87.99%"
          subValue="Cityscapes Benchmark Test Set"
          accentColor="emerald"
        />
        <StatCard
          icon={<Layers className="w-6 h-6" />}
          label="Mean IoU (mIoU)"
          value="78.55%"
          subValue="19-Class Semantic Overlap"
          accentColor="cyan"
        />
        <StatCard
          icon={<Zap className="w-6 h-6" />}
          label="Inference Target"
          value="<50ms"
          subValue="Real-Time FPS Throughput SLA"
          accentColor="purple"
        />
      </section>

      {/* QUICK UPLOAD EXPERIENCE */}
      <section className="space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold text-slate-100 font-heading flex items-center gap-2">
              <Sparkles className="w-5 h-5 text-cyan-400" /> Quick Perception Lab
            </h2>
            <p className="text-xs text-slate-400">
              Drag and drop an urban road scene to execute DeepLabV3+ segmentation in real-time.
            </p>
          </div>

          <span className="text-xs text-slate-400 font-mono bg-slate-900 border border-slate-800 px-3 py-1 rounded-lg">
            Model: DeepLabV3+ (ResNet-101 ASPP)
          </span>
        </div>

        <GlassCard hoverEffect glowColor="cyan" className="p-8">
          <div
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
            className={`relative rounded-2xl border-2 border-dashed p-8 text-center transition-all ${
              dragActive
                ? 'border-cyan-400 bg-cyan-950/30 shadow-[0_0_30px_rgba(6,182,212,0.2)]'
                : 'border-slate-800 hover:border-cyan-500/40 bg-slate-950/40'
            }`}
          >
            {previewUrl ? (
              <div className="space-y-6">
                <div className="relative max-w-md mx-auto rounded-xl overflow-hidden border border-slate-800 shadow-2xl">
                  <img src={previewUrl} alt="Selected preview" className="w-full h-56 object-cover" />
                  <button
                    onClick={() => { setSelectedFile(null); setPreviewUrl(null); }}
                    className="absolute top-2 right-2 bg-slate-900/90 text-slate-300 hover:text-white p-1.5 rounded-full border border-slate-700"
                  >
                    ✕
                  </button>
                </div>

                <div className="flex flex-wrap items-center justify-center gap-4 text-xs text-slate-300">
                  <span>Filename: <strong className="text-slate-100">{selectedFile?.name}</strong></span>
                  <span>Size: <strong className="text-slate-100">{((selectedFile?.size || 0) / 1024 / 1024).toFixed(2)} MB</strong></span>
                </div>

                <Button
                  variant="primary"
                  size="lg"
                  isLoading={isProcessing}
                  onClick={handleQuickRunPerception}
                  leftIcon={<Sparkles className="w-5 h-5" />}
                >
                  Run Perception Analysis
                </Button>
              </div>
            ) : (
              <div className="space-y-4 py-4">
                <div className="mx-auto w-16 h-16 rounded-2xl bg-cyan-500/10 border border-cyan-500/30 flex items-center justify-center text-cyan-400">
                  <Upload className="w-8 h-8 animate-pulse" />
                </div>

                <div>
                  <h3 className="text-base font-bold text-slate-200">
                    Drop your road scene here
                  </h3>
                  <p className="text-xs text-slate-400 mt-1">
                    Supports PNG, JPG, JPEG up to 10 MB
                  </p>
                </div>

                <label className="inline-block cursor-pointer">
                  <Button variant="secondary" size="sm" type="button">
                    Browse Files
                  </Button>
                  <input
                    type="file"
                    accept="image/*"
                    className="hidden"
                    onChange={(e) => e.target.files?.[0] && handleFileChange(e.target.files[0])}
                  />
                </label>
              </div>
            )}
          </div>

          {error && (
            <div className="mt-4 p-3 rounded-xl bg-rose-950/60 border border-rose-800 text-rose-300 text-xs">
              {error}
            </div>
          )}
        </GlassCard>
      </section>

      {/* FEATURE CARDS */}
      <section className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <GlassCard hoverEffect headerAccent className="p-6 space-y-3">
          <div className="p-3 rounded-xl bg-cyan-500/10 border border-cyan-500/20 text-cyan-400 w-fit">
            <Cpu className="w-6 h-6" />
          </div>
          <h3 className="font-bold text-lg text-slate-100 font-heading">
            DeepLabV3+ ASPP Architecture
          </h3>
          <p className="text-xs text-slate-400 leading-relaxed">
            Atrous Spatial Pyramid Pooling extracts multi-scale receptive field features for fine-grained urban boundary classification.
          </p>
        </GlassCard>

        <GlassCard hoverEffect headerAccent className="p-6 space-y-3">
          <div className="p-3 rounded-xl bg-blue-500/10 border border-blue-500/20 text-blue-400 w-fit">
            <Activity className="w-6 h-6" />
          </div>
          <h3 className="font-bold text-lg text-slate-100 font-heading">
            Sub-50ms Frame Latency
          </h3>
          <p className="text-xs text-slate-400 leading-relaxed">
            High-throughput inference pipeline delivering &gt;30 FPS real-time segmentation performance for autonomous vehicle streams.
          </p>
        </GlassCard>

        <GlassCard hoverEffect headerAccent className="p-6 space-y-3">
          <div className="p-3 rounded-xl bg-purple-500/10 border border-purple-500/20 text-purple-400 w-fit">
            <ShieldCheck className="w-6 h-6" />
          </div>
          <h3 className="font-bold text-lg text-slate-100 font-heading">
            Celery Distributed Queue
          </h3>
          <p className="text-xs text-slate-400 leading-relaxed">
            Asynchronous background video processing with Redis caching and real-time step status polling for long video feeds.
          </p>
        </GlassCard>
      </section>
    </div>
  );
};
