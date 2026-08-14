import React, { useRef } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { Html, Float, OrbitControls } from '@react-three/drei';
import * as THREE from 'three';

// Stylized Vehicle Geometry Component
const VehicleMesh: React.FC = () => {
  const vehicleRef = useRef<THREE.Group>(null);

  useFrame((state, delta) => {
    if (vehicleRef.current) {
      vehicleRef.current.rotation.y += delta * 0.2;
    }
  });

  return (
    <group ref={vehicleRef} position={[0, 0.4, 0]}>
      {/* Car Main Chassis */}
      <mesh position={[0, 0.2, 0]}>
        <boxGeometry args={[1.8, 0.5, 3.4]} />
        <meshStandardMaterial color="#0f172a" metalness={0.8} roughness={0.2} wireframe />
      </mesh>

      {/* Cabin Roof */}
      <mesh position={[0, 0.6, -0.2]}>
        <boxGeometry args={[1.4, 0.45, 1.8]} />
        <meshStandardMaterial color="#06b6d4" transparent opacity={0.6} wireframe />
      </mesh>

      {/* Sensor Pod (LiDAR Dome on Roof) */}
      <mesh position={[0, 0.95, -0.2]}>
        <cylinderGeometry args={[0.2, 0.2, 0.2, 16]} />
        <meshStandardMaterial color="#38bdf8" emissive="#06b6d4" emissiveIntensity={0.8} />
      </mesh>

      {/* Wheels */}
      {[-0.9, 0.9].map((x) =>
        [-1.1, 1.1].map((z) => (
          <mesh key={`${x}-${z}`} position={[x, 0, z]} rotation={[0, 0, Math.PI / 2]}>
            <cylinderGeometry args={[0.3, 0.3, 0.25, 16]} />
            <meshStandardMaterial color="#1e293b" wireframe />
          </mesh>
        ))
      )}
    </group>
  );
};

// Radar Scan Ring Component
const RadarRing: React.FC = () => {
  const ringRef = useRef<THREE.Mesh>(null);

  useFrame((_, delta) => {
    if (ringRef.current) {
      ringRef.current.rotation.z += delta * 0.8;
    }
  });

  return (
    <mesh ref={ringRef} position={[0, 0.05, 0]} rotation={[-Math.PI / 2, 0, 0]}>
      <ringGeometry args={[1.8, 2.2, 32]} />
      <meshBasicMaterial color="#06b6d4" side={THREE.DoubleSide} transparent opacity={0.3} wireframe />
    </mesh>
  );
};

// Perception Point Cloud Nodes
const PerceptionPoints: React.FC = () => {
  const pointsRef = useRef<THREE.Points>(null);

  const count = 120;
  const positions = new Float32Array(count * 3);

  for (let i = 0; i < count; i++) {
    positions[i * 3] = (Math.random() - 0.5) * 8;
    positions[i * 3 + 1] = Math.random() * 2.5;
    positions[i * 3 + 2] = (Math.random() - 0.5) * 8;
  }

  useFrame((_, delta) => {
    if (pointsRef.current) {
      pointsRef.current.rotation.y += delta * 0.05;
    }
  });

  return (
    <points ref={pointsRef}>
      <bufferGeometry>
        <bufferAttribute
          attach="attributes-position"
          args={[positions, 3]}
        />
      </bufferGeometry>
      <pointsMaterial size={0.06} color="#38bdf8" transparent opacity={0.8} />
    </points>
  );
};

export const PerceptionScene3D: React.FC = () => {
  return (
    <div className="relative w-full h-[420px] lg:h-[500px] rounded-2xl glass-card overflow-hidden border border-cyan-500/30 bg-[#070a12] shadow-2xl">
      <Canvas camera={{ position: [4, 3, 5], fov: 45 }}>
        <ambientLight intensity={0.6} />
        <directionalLight position={[10, 10, 5]} intensity={1.2} />
        <pointLight position={[-5, 5, -5]} color="#8b5cf6" intensity={1} />

        <Float speed={1.5} rotationIntensity={0.2} floatIntensity={0.3}>
          <VehicleMesh />
        </Float>

        <RadarRing />
        <PerceptionPoints />

        {/* Road Surface Grid */}
        <gridHelper args={[20, 20, '#06b6d4', '#1e293b']} position={[0, -0.05, 0]} />

        {/* Semantic Annotation HTML Overlay Pins */}
        <Html position={[0, 1.6, 0]} center>
          <div className="bg-cyan-950/90 text-cyan-200 border border-cyan-400 px-2 py-0.5 rounded text-[10px] font-bold shadow-lg flex items-center gap-1 backdrop-blur-md pointer-events-none">
            <span className="w-1.5 h-1.5 rounded-full bg-cyan-400 animate-ping" />
            [Vehicle LiDAR: 99.4%]
          </div>
        </Html>

        <Html position={[-2.2, 0.4, 1.5]} center>
          <div className="bg-purple-950/90 text-purple-200 border border-purple-400 px-2 py-0.5 rounded text-[10px] font-bold shadow-lg backdrop-blur-md pointer-events-none">
            [Road Surface]
          </div>
        </Html>

        <Html position={[2.2, 0.8, -1.8]} center>
          <div className="bg-rose-950/90 text-rose-200 border border-rose-400 px-2 py-0.5 rounded text-[10px] font-bold shadow-lg backdrop-blur-md pointer-events-none">
            [Pedestrian BBox]
          </div>
        </Html>

        <OrbitControls enableZoom={false} autoRotate autoRotateSpeed={0.5} maxPolarAngle={Math.PI / 2.1} />
      </Canvas>

      {/* Canvas HUD Legend */}
      <div className="absolute bottom-4 left-4 right-4 flex items-center justify-between text-[11px] font-medium text-slate-400 bg-slate-950/80 p-2.5 rounded-xl border border-slate-800 backdrop-blur-md">
        <span className="flex items-center gap-1.5">
          <span className="w-2 h-2 rounded-full bg-cyan-400" />
          Interactive 3D LiDAR & ASPP Feature Space
        </span>
        <span className="text-slate-500 font-mono text-[10px]">FPS: ~60 (WebGL 2.0)</span>
      </div>
    </div>
  );
};
