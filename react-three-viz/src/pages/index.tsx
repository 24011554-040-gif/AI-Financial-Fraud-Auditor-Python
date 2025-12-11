import React, { useState, useCallback, useEffect, Suspense } from 'react';
import { Canvas, useFrame, useThree } from '@react-three/fiber';
import { OrbitControls, Stats, Environment, ContactShadows } from '@react-three/drei';
import { ResponsiveLayout } from '../components/layout/ResponsiveLayout';
import { ControlPanel } from '../components/ui/ControlPanel';
import { PerformanceMonitor } from '../components/ui/PerformanceMonitor';
import { AnimatedMesh } from '../components/3d/AnimatedMesh';
import { useThreeOptimized } from '../lib/hooks/useThreeOptimized';

// Inner component to handle R3F logic and performance optimization
const SceneManager = ({ onPerfUpdate }: { onPerfUpdate: (data: any) => void }) => {
  const { dpr, perfData, adaptDpr } = useThreeOptimized();
  const { gl, scene } = useThree();
  
  // Apply adaptive DPR
  useEffect(() => {
    gl.setPixelRatio(dpr);
  }, [dpr, gl]);

  // Measure FPS and adapt
  useFrame((state) => {
    const fps = 1 / state.clock.getDelta();
    // Throttle adaptation to avoid flickering
    if (state.clock.elapsedTime % 1 < 0.1) {
       adaptDpr(fps);
       onPerfUpdate({ ...perfData, dpr });
    }
  });

  return null;
};

export default function Home() {
  // App State
  const [color, setColor] = useState('#00ff88');
  const [speed, setSpeed] = useState(0.5);
  const [distortion, setDistortion] = useState(0);
  
  // Performance State
  const [perfMetrics, setPerfMetrics] = useState({ fps: 60, dpr: 1, gpu: '' });

  const handlePerfUpdate = useCallback((data: any) => {
    setPerfMetrics(data);
  }, []);

  return (
    <ResponsiveLayout title="Next.js + Three.js Hologram">
      {/* UI Overlays */}
      <ControlPanel 
        onColorChange={setColor}
        onSpeedChange={setSpeed}
        onDistortionChange={setDistortion}
      />
      
      <PerformanceMonitor 
        fps={perfMetrics.fps}
        dpr={perfMetrics.dpr}
        gpu={perfMetrics.gpu}
      />

      {/* 3D Scene */}
      <div className="w-full h-full">
        <Canvas
          camera={{ position: [0, 0, 5], fov: 45 }}
          gl={{ 
            antialias: false, // Managed by DPR
            powerPreference: "high-performance",
            alpha: true
          }}
          dpr={[1, 2]} // Default range, controlled by SceneManager
        >
          <Suspense fallback={null}>
            <SceneManager onPerfUpdate={handlePerfUpdate} />
            
            {/* Lighting */}
            <ambientLight intensity={0.5} />
            <pointLight position={[10, 10, 10]} intensity={1} />
            <spotLight position={[-10, -10, -10]} intensity={0.5} />
            
            {/* Main Object */}
            <AnimatedMesh 
              color={color}
              speed={speed}
              distortion={distortion}
            />

            {/* Environment Enhancements */}
            <ContactShadows 
              position={[0, -1.5, 0]} 
              opacity={0.4} 
              scale={10} 
              blur={2.5} 
              far={4} 
            />
            <Environment preset="city" />
            
            <OrbitControls 
              enablePan={false}
              minPolarAngle={Math.PI / 4}
              maxPolarAngle={Math.PI / 1.5}
            />
          </Suspense>
        </Canvas>
      </div>
    </ResponsiveLayout>
  );
}