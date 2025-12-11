import { useState, useEffect, useCallback } from 'react';
import { useThree } from '@react-three/fiber';

/**
 * Custom hook for managing Three.js performance optimizations.
 * Adjusts pixel ratio (DPR) dynamically to maintain target FPS.
 */
export const useThreeOptimized = (targetFps = 60) => {
  const [dpr, setDpr] = useState(1);
  const gl = useThree((state) => state.gl);
  
  // Performance monitoring state
  const [perfData, setPerfData] = useState({
    fps: 0,
    gpu: 'Unknown'
  });

  useEffect(() => {
    // Initial capability check
    const pixelRatio = typeof window !== 'undefined' ? window.devicePixelRatio : 1;
    setDpr(Math.min(pixelRatio, 2)); // Cap at 2x for performance

    // get unmasked renderer info if available (for debugging/monitoring)
    const debugInfo = gl.getContext().getExtension('WEBGL_debug_renderer_info');
    if (debugInfo) {
      const renderer = gl.getContext().getParameter(debugInfo.UNMASKED_RENDERER_WEBGL);
      setPerfData(prev => ({ ...prev, gpu: renderer }));
    }

  }, [gl]);

  // Adaptive DPR callback
  const adaptDpr = useCallback((currentFps: number) => {
    setDpr((prevDpr) => {
      if (currentFps < targetFps * 0.8) {
        return Math.max(0.5, prevDpr * 0.9); // Reduce quality
      } else if (currentFps > targetFps * 0.95 && prevDpr < (window.devicePixelRatio || 2)) {
        return Math.min(window.devicePixelRatio || 2, prevDpr * 1.1); // Increase quality
      }
      return prevDpr;
    });
    
    setPerfData(prev => ({ ...prev, fps: Math.round(currentFps) }));
  }, [targetFps]);

  return {
    dpr,
    perfData,
    adaptDpr
  };
};