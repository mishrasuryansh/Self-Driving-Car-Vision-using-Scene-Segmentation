import React from 'react';
import { Upload, Camera } from 'lucide-react';

export const UploadImagePage: React.FC = () => {
  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      <div className="flex items-center space-x-3">
        <Camera className="w-8 h-8 text-cyan-400" />
        <h1 className="text-2xl font-bold">Image Scene Segmentation</h1>
      </div>
      <div className="glass-card p-10 border-dashed border-2 border-slate-700 text-center space-y-4">
        <Upload className="w-12 h-12 mx-auto text-slate-500" />
        <h3 className="text-lg font-medium">Drag and drop road scene image</h3>
        <p className="text-sm text-slate-400">Supports JPEG, PNG, WEBP up to 10MB</p>
        <button className="btn-primary">Browse Image File</button>
      </div>
    </div>
  );
};
