import React from 'react';
import { Info, Cpu, Users, GraduationCap, Code, ArrowRight, ShieldCheck, Layers, Server, Database, Sparkles } from 'lucide-react';
import { GlassCard } from '../components/ui/GlassCard';
import { Badge } from '../components/ui/Badge';

export const AboutPage: React.FC = () => {
  return (
    <div className="space-y-12 max-w-5xl mx-auto py-2">
      {/* Hero Section */}
      <div className="space-y-4 text-center max-w-3xl mx-auto">
        <div className="inline-flex items-center space-x-2">
          <Badge variant="cyan" dot>ACADEMIC & TECHNICAL SPECIFICATION</Badge>
          <span className="text-xs text-slate-400">PSIT Kanpur Final Year CS Project</span>
        </div>

        <h1 className="text-3xl sm:text-5xl font-extrabold text-slate-100 font-heading leading-tight">
          Engineering Intelligent{' '}
          <span className="bg-gradient-to-r from-cyan-400 via-blue-400 to-purple-400 bg-clip-text text-transparent">
            Autonomous Perception
          </span>
        </h1>

        <p className="text-sm text-slate-300 leading-relaxed">
          High-performance semantic scene segmentation delivering multi-scale spatial feature understanding for autonomous vehicle navigation in urban environments.
        </p>
      </div>

      {/* Animated Interactive Architecture Diagram (Phase 14) */}
      <GlassCard hoverEffect glowColor="cyan" className="p-8 space-y-6">
        <div className="flex items-center justify-between border-b border-slate-800 pb-3">
          <div className="flex items-center space-x-2">
            <div className="p-2 rounded-xl bg-cyan-500/10 border border-cyan-500/20 text-cyan-400">
              <Cpu className="w-5 h-5" />
            </div>
            <div>
              <h3 className="font-bold text-lg text-slate-100 font-heading">System Pipeline Architecture</h3>
              <p className="text-xs text-slate-400">End-to-End Autonomous Perception Flow</p>
            </div>
          </div>
          <Badge variant="purple" dot>Production Pipeline</Badge>
        </div>

        {/* Horizontal Pipeline Steps */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-6 gap-3 pt-2">
          <div className="p-3.5 rounded-xl bg-slate-900/80 border border-slate-800 space-y-1 text-center">
            <div className="text-[10px] font-bold text-cyan-400 uppercase">1. Client Layer</div>
            <div className="font-semibold text-slate-100 text-xs">Vite / React 18</div>
            <p className="text-[10px] text-slate-400">TypeScript SPA</p>
          </div>

          <div className="p-3.5 rounded-xl bg-slate-900/80 border border-slate-800 space-y-1 text-center">
            <div className="text-[10px] font-bold text-blue-400 uppercase">2. API Gateway</div>
            <div className="font-semibold text-slate-100 text-xs">FastAPI REST</div>
            <p className="text-[10px] text-slate-400">Pydantic v2 / JWT</p>
          </div>

          <div className="p-3.5 rounded-xl bg-slate-900/80 border border-slate-800 space-y-1 text-center">
            <div className="text-[10px] font-bold text-purple-400 uppercase">3. Message Broker</div>
            <div className="font-semibold text-slate-100 text-xs">Redis Cache</div>
            <p className="text-[10px] text-slate-400">Pub/Sub Queue</p>
          </div>

          <div className="p-3.5 rounded-xl bg-slate-900/80 border border-slate-800 space-y-1 text-center">
            <div className="text-[10px] font-bold text-purple-400 uppercase">4. Async Workers</div>
            <div className="font-semibold text-slate-100 text-xs">Celery Queue</div>
            <p className="text-[10px] text-slate-400">Distributed Task Exec</p>
          </div>

          <div className="p-3.5 rounded-xl bg-slate-900/80 border border-slate-800 space-y-1 text-center">
            <div className="text-[10px] font-bold text-emerald-400 uppercase">5. AI Model</div>
            <div className="font-semibold text-slate-100 text-xs">DeepLabV3+</div>
            <p className="text-[10px] text-slate-400">ResNet-101 ASPP</p>
          </div>

          <div className="p-3.5 rounded-xl bg-slate-900/80 border border-slate-800 space-y-1 text-center">
            <div className="text-[10px] font-bold text-amber-400 uppercase">6. Persistence</div>
            <div className="font-semibold text-slate-100 text-xs">MongoDB / Storage</div>
            <p className="text-[10px] text-slate-400">Artifact Store</p>
          </div>
        </div>
      </GlassCard>

      {/* Technology Stack Grid */}
      <GlassCard hoverEffect glowColor="purple" className="p-6 space-y-4">
        <div className="flex items-center space-x-2 border-b border-slate-800 pb-3">
          <Code className="w-5 h-5 text-purple-400" />
          <h3 className="font-bold text-lg text-slate-100 font-heading">Technology Stack Specification</h3>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4 text-xs">
          <div className="bg-slate-900/60 p-4 rounded-xl border border-slate-800 space-y-1">
            <div className="font-bold text-cyan-400">Frontend Presentation</div>
            <p className="text-slate-300">React 18, TypeScript 5.7, Vite 6, Tailwind CSS, Lucide React, Three.js / React Three Fiber</p>
          </div>

          <div className="bg-slate-900/60 p-4 rounded-xl border border-slate-800 space-y-1">
            <div className="font-bold text-purple-400">Backend API Services</div>
            <p className="text-slate-300">Python 3.13, FastAPI, Pydantic v2, Motor / PyMongo, OAuth2 JWT Bearer Tokens</p>
          </div>

          <div className="bg-slate-900/60 p-4 rounded-xl border border-slate-800 space-y-1">
            <div className="font-bold text-emerald-400">Deep Learning Perception</div>
            <p className="text-slate-300">PyTorch 2.x, Torchvision, DeepLabV3+ (ResNet-101 ASPP), OpenCV, NumPy</p>
          </div>

          <div className="bg-slate-900/60 p-4 rounded-xl border border-slate-800 space-y-1">
            <div className="font-bold text-amber-400">Task Queue & Broker</div>
            <p className="text-slate-300">Celery Distributed Task Workers, Redis In-Memory Cache & Message Broker</p>
          </div>

          <div className="bg-slate-900/60 p-4 rounded-xl border border-slate-800 space-y-1">
            <div className="font-bold text-rose-400">Database & Artifacts</div>
            <p className="text-slate-300">MongoDB 7.0 Document Store, Local File System & GCS Media Storage</p>
          </div>

          <div className="bg-slate-900/60 p-4 rounded-xl border border-slate-800 space-y-1">
            <div className="font-bold text-blue-400">DevOps & Deployment</div>
            <p className="text-slate-300">Docker Multi-Stage Containers, Docker Compose Services Orchestration, Nginx Reverse Proxy</p>
          </div>
        </div>
      </GlassCard>

      {/* Team Members & Institution */}
      <GlassCard hoverEffect glowColor="emerald" className="p-6 space-y-4">
        <div className="flex items-center space-x-2 border-b border-slate-800 pb-3">
          <Users className="w-5 h-5 text-emerald-400" />
          <h3 className="font-bold text-lg text-slate-100 font-heading">Development Team & Institution</h3>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-6 text-xs">
          {/* Engineering Roster */}
          <div className="bg-slate-900/60 p-5 rounded-xl border border-slate-800 space-y-3">
            <div className="font-bold text-slate-200 text-sm flex items-center gap-1.5">
              <Users className="w-4 h-4 text-cyan-400" /> Development Team Roster
            </div>
            <ul className="grid grid-cols-2 gap-2 text-slate-300 font-medium">
              <li className="flex items-center gap-1.5"><span className="w-1.5 h-1.5 rounded-full bg-cyan-400" /> Anshika Tiwari</li>
              <li className="flex items-center gap-1.5"><span className="w-1.5 h-1.5 rounded-full bg-cyan-400" /> Uday Kumar Shukla</li>
              <li className="flex items-center gap-1.5"><span className="w-1.5 h-1.5 rounded-full bg-cyan-400" /> Swastik Shukla</li>
              <li className="flex items-center gap-1.5"><span className="w-1.5 h-1.5 rounded-full bg-cyan-400" /> Suryansh Mishra</li>
              <li className="flex items-center gap-1.5"><span className="w-1.5 h-1.5 rounded-full bg-cyan-400" /> Akansha Rajpoot</li>
              <li className="flex items-center gap-1.5"><span className="w-1.5 h-1.5 rounded-full bg-cyan-400" /> Akansha Yadav</li>
            </ul>
          </div>

          {/* Academic Supervisor & Institution */}
          <div className="bg-slate-900/60 p-5 rounded-xl border border-slate-800 space-y-3">
            <div className="font-bold text-slate-200 text-sm flex items-center gap-1.5">
              <GraduationCap className="w-4 h-4 text-emerald-400" /> Project Supervision & Institution
            </div>
            <div className="space-y-2 text-slate-300">
              <p>
                <span className="text-slate-400">Project Supervisor:</span> <strong className="text-slate-100">Dr. Milli Dhar</strong>
              </p>
              <p>
                <span className="text-slate-400">Institution:</span> <strong className="text-slate-100">Pranveer Singh Institute of Technology (PSIT), Kanpur</strong>
              </p>
              <p>
                <span className="text-slate-400">Department:</span> <strong className="text-slate-100">Computer Science & Engineering (CSE)</strong>
              </p>
            </div>
          </div>
        </div>
      </GlassCard>
    </div>
  );
};
