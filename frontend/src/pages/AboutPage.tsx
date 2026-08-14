/**
 * Static Project Information & Academic Synopsis Credits Page (T073).
 *
 * Sourced accurately from project proposal documents, listing team members,
 * supervisor, technology stack, and platform description.
 */

import React from 'react';
import { Info, Cpu, Users, GraduationCap, Code } from 'lucide-react';

export const AboutPage: React.FC = () => {
  return (
    <div className="space-y-8 max-w-4xl mx-auto">
      <div className="flex items-center space-x-3 border-b border-slate-800 pb-4">
        <Info className="w-8 h-8 text-cyan-400" />
        <div>
          <h1 className="text-2xl font-bold">About Self-Driving Car Vision Platform</h1>
          <p className="text-xs text-slate-400">Deep Learning Scene Segmentation System for Autonomous Driving</p>
        </div>
      </div>

      {/* Project Executive Summary */}
      <div className="glass-card p-6 space-y-3">
        <h3 className="font-semibold text-lg text-slate-100 flex items-center">
          <Cpu className="w-5 h-5 mr-2 text-cyan-400" /> Executive Overview
        </h3>
        <p className="text-slate-300 text-sm leading-relaxed">
          The <strong>Self-Driving Car Vision Platform</strong> delivers high-performance semantic scene segmentation for autonomous vehicle navigation. Utilizing the DeepLabV3+ neural network architecture with a ResNet-101 backbone and Atrous Spatial Pyramid Pooling (ASPP), the system classifies complex urban traffic scenes into distinct environmental classes including roads, vehicles, pedestrians, lanes, and obstacles in real-time.
        </p>
      </div>

      {/* Technology Stack List */}
      <div className="glass-card p-6 space-y-4">
        <h3 className="font-semibold text-lg text-slate-100 flex items-center">
          <Code className="w-5 h-5 mr-2 text-purple-400" /> Technology Stack Architecture
        </h3>
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4 text-xs">
          <div className="bg-slate-900/60 p-3 rounded-lg border border-slate-800">
            <div className="font-bold text-cyan-400 mb-1">Frontend</div>
            <div className="text-slate-300">React 18, TypeScript, Tailwind CSS / Vanilla CSS, Axios, Lucide React</div>
          </div>

          <div className="bg-slate-900/60 p-3 rounded-lg border border-slate-800">
            <div className="font-bold text-purple-400 mb-1">Backend API</div>
            <div className="text-slate-300">Python 3.13, FastAPI, Pydantic v2, Motor / PyMongo, JWT Auth</div>
          </div>

          <div className="bg-slate-900/60 p-3 rounded-lg border border-slate-800">
            <div className="font-bold text-emerald-400 mb-1">Deep Learning Engine</div>
            <div className="text-slate-300">PyTorch 2.x, Torchvision, DeepLabV3+, OpenCV, NumPy</div>
          </div>

          <div className="bg-slate-900/60 p-3 rounded-lg border border-slate-800">
            <div className="font-bold text-amber-400 mb-1">Queue & Storage</div>
            <div className="text-slate-300">Celery Distributed Worker, Redis Cache & Broker, MongoDB 7.0</div>
          </div>

          <div className="bg-slate-900/60 p-3 rounded-lg border border-slate-800">
            <div className="font-bold text-pink-400 mb-1">DevOps & Containerization</div>
            <div className="text-slate-300">Docker, Docker Compose, Nginx Reverse Proxy</div>
          </div>
        </div>
      </div>

      {/* Team Roster & Supervisor Credits */}
      <div className="glass-card p-6 space-y-4">
        <h3 className="font-semibold text-lg text-slate-100 flex items-center">
          <Users className="w-5 h-5 mr-2 text-emerald-400" /> Project Team & Institution
        </h3>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
          <div className="bg-slate-900/60 p-4 rounded-lg border border-slate-800 space-y-2">
            <div className="font-bold text-slate-200 text-sm flex items-center">
              <Users className="w-4 h-4 mr-1.5 text-cyan-400" /> Development Team
            </div>
            <ul className="list-disc list-inside text-slate-300 space-y-1">
              <li>Anshika Tiwari</li>
              <li>Uday Kumar Shukla</li>
              <li>Swastik Shukla</li>
              <li>Suryansh Mishra</li>
              <li>Akansha Rajpoot</li>
              <li>Akansha Yadav</li>
            </ul>
          </div>

          <div className="bg-slate-900/60 p-4 rounded-lg border border-slate-800 space-y-2">
            <div className="font-bold text-slate-200 text-sm flex items-center">
              <GraduationCap className="w-4 h-4 mr-1.5 text-emerald-400" /> Project Supervision & Institution
            </div>
            <p className="text-slate-300">
              <strong className="text-slate-200">Supervisor:</strong> Dr. Milli Dhar
            </p>
            <p className="text-slate-300">
              <strong className="text-slate-200">Institution:</strong> Pranveer Singh Institute of Technology (PSIT), Kanpur
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};
