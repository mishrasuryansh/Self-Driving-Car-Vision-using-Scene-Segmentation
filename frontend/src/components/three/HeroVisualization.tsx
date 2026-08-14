import React, { useState, useEffect, Suspense } from 'react';
import { FallbackPerception2D } from './FallbackPerception2D';
import { Loader2 } from 'lucide-react';

const PerceptionScene3D = React.lazy(() =>
  import('./PerceptionScene3D').then((module) => ({ default: module.PerceptionScene3D }))
);

export const HeroVisualization: React.FC = () => {
  const [isMobileOrReducedMotion, setIsMobileOrReducedMotion] = useState<boolean>(false);

  useEffect(() => {
    const mediaQueryMobile = window.matchMedia('(max-width: 768px)');
    const mediaQueryMotion = window.matchMedia('(prefers-reduced-motion: reduce)');

    const checkState = () => {
      setIsMobileOrReducedMotion(mediaQueryMobile.matches || mediaQueryMotion.matches);
    };

    checkState();
    mediaQueryMobile.addEventListener('change', checkState);
    mediaQueryMotion.addEventListener('change', checkState);

    return () => {
      mediaQueryMobile.removeEventListener('change', checkState);
      mediaQueryMotion.removeEventListener('change', checkState);
    };
  }, []);

  if (isMobileOrReducedMotion) {
    return <FallbackPerception2D />;
  }

  return (
    <Suspense
      fallback={
        <div className="w-full h-[420px] lg:h-[500px] rounded-2xl glass-card border border-slate-800 flex flex-col items-center justify-center space-y-3">
          <Loader2 className="w-8 h-8 text-cyan-400 animate-spin" />
          <span className="text-xs text-slate-400 font-medium">Initializing 3D Perception Canvas...</span>
        </div>
      }
    >
      <PerceptionScene3D />
    </Suspense>
  );
};
