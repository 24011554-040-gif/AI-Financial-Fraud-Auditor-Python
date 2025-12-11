import React from 'react';

interface PerformanceMonitorProps {
  fps: number;
  gpu?: string;
  dpr: number;
}

export const PerformanceMonitor: React.FC<PerformanceMonitorProps> = ({ fps, gpu, dpr }) => {
  // Determine performance health color
  const getHealthColor = (val: number) => {
    if (val >= 55) return 'text-green-400';
    if (val >= 30) return 'text-yellow-400';
    return 'text-red-400';
  };

  return (
    <div className="absolute bottom-4 left-4 p-3 bg-black/80 backdrop-blur-sm rounded border border-white/5 font-mono text-xs text-gray-400 select-none z-50 pointer-events-none">
      <div className="flex flex-col gap-1">
        <div className="flex justify-between gap-4">
          <span>FPS:</span>
          <span className={`font-bold ${getHealthColor(fps)}`}>{fps}</span>
        </div>
        <div className="flex justify-between gap-4">
          <span>DPR:</span>
          <span className="text-blue-300">{dpr.toFixed(2)}x</span>
        </div>
        {gpu && (
          <div className="border-t border-white/10 pt-1 mt-1 max-w-[200px] truncate" title={gpu}>
            <span className="opacity-50">GPU: </span>
            <span>{gpu.replace(/ANGLE \((.*)\)/, '$1')}</span>
          </div>
        )}
      </div>
    </div>
  );
};