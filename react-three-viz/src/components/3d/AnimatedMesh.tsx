import React, { useRef, useMemo } from 'react';
import { useFrame } from '@react-three/fiber';
import { shaderMaterial } from '@react-three/drei';
import * as THREE from 'three';
import { extend } from '@react-three/fiber';

// Import fragment shader (assuming raw-loader is configured)
// @ts-ignore
import fragmentShader from '../../shaders/materials/holographic.frag';

interface AnimatedMeshProps {
  color: string;
  speed: number;
  distortion: number;
}

// Basic vertex shader for holographic effect
const vertexShader = `
varying vec2 vUv;
varying vec3 vNormal;
varying vec3 vPosition;

void main() {
  vUv = uv;
  vNormal = normalize(normalMatrix * normal);
  vPosition = (modelViewMatrix * vec4(position, 1.0)).xyz;
  gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
}
`;

// Create custom shader material
const HolographicMaterial = shaderMaterial(
  {
    uTime: 0,
    uColor: new THREE.Color('#00ff88'),
    uDistortion: 0,
  },
  vertexShader,
  fragmentShader
);

extend({ HolographicMaterial });

// Add type support for the custom material in JSX
declare global {
  namespace JSX {
    interface IntrinsicElements {
      holographicMaterial: any;
    }
  }
}

export const AnimatedMesh: React.FC<AnimatedMeshProps> = ({ color, speed, distortion }) => {
  const meshRef = useRef<THREE.Mesh>(null);
  const materialRef = useRef<THREE.ShaderMaterial>(null);

  const uniforms = useMemo(
    () => ({
      uTime: { value: 0 },
      uColor: { value: new THREE.Color(color) },
      uDistortion: { value: distortion },
    }),
    [] // Initial uniforms
  );

  useFrame((state, delta) => {
    if (meshRef.current) {
      meshRef.current.rotation.x += delta * speed * 0.2;
      meshRef.current.rotation.y += delta * speed * 0.5;
    }

    if (materialRef.current) {
      materialRef.current.uniforms.uTime.value += delta;
      // Smoothly interpolate color
      const targetColor = new THREE.Color(color);
      materialRef.current.uniforms.uColor.value.lerp(targetColor, 0.1);
      
      // Update distortion (passed to shader if we add it to frag later)
       materialRef.current.uniforms.uDistortion.value = distortion;
    }
  });

  return (
    <mesh ref={meshRef} position={[0, 0, 0]} scale={1.5}>
      <icosahedronGeometry args={[1, 64]} />
      {/* 
        // @ts-ignore - Custom material element */}
      <holographicMaterial
        ref={materialRef}
        transparent
        side={THREE.DoubleSide}
        // uniforms are updated via ref in useFrame for performance
      />
    </mesh>
  );
};