import React from 'react';
import { Video, Upload } from 'lucide-react';

export const UploadVideoPage: React.FC = () => {
  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      <div className="flex items-center space-x-3">
        <Video className="w-8 h-8 text-purple-400" />
        <h1 className="text-2xl font-bold">Asynchronous Video Segmentation (Celery Worker)</h1>
      </div>
      <div className="glass-card p-10 border-dashed border-2 border-slate-700 text-center space-y-4">
        <Upload className="w-12 h-12 mx-auto text-slate-500" />
        <h3 className="text-lg font-medium">Drag and drop dashcam video stream</h3>
        <p className="text-sm text-slate-400">Supports MP4, AVI, MOV up to 200MB (max 2 mins)</p>
        <button className="btn-primary bg-gradient-to-r from-purple-600 to-indigo-600">Browse Video File</button>
      </div>
    </div>
  );
};
