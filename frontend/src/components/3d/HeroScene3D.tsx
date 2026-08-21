import React, { useState, useRef, Suspense, useEffect } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { Float, Html, PerspectiveCamera } from '@react-three/drei';
import * as THREE from 'three';
import { useNavigate } from 'react-router-dom';
import { 
  Wind, 
  Zap, 
  Droplet, 
  Sparkles, 
  Wrench, 
  Hammer, 
  Paintbrush, 
  ShieldCheck,
  ChevronRight,
  Eye
} from 'lucide-react';

interface ServiceHotspot {
  id: string;
  name: string;
  category: string;
  position: [number, number, number];
  icon: React.ElementType;
  description: string;
  tag: string;
}

const SERVICE_HOTSPOTS: ServiceHotspot[] = [
  {
    id: 'ac',
    name: 'AC & Climate',
    category: 'HVAC',
    position: [0.8, 1.9, 0.4],
    icon: Wind,
    description: 'Precision cooling, duct sanitization & thermostat calibration',
    tag: 'Verified Techs',
  },
  {
    id: 'electrical',
    name: 'Electrical & Power',
    category: 'Power',
    position: [-1.8, 0.2, 1.2],
    icon: Zap,
    description: 'Smart breakers, load balancing & certified rewiring',
    tag: 'Licensed Pros',
  },
  {
    id: 'plumbing',
    name: 'Plumbing & Water',
    category: 'Hydraulics',
    position: [1.8, -0.4, -0.6],
    icon: Droplet,
    description: 'Leak detection, pressure balance & water line maintenance',
    tag: '24/7 Rapid',
  },
  {
    id: 'cleaning',
    name: 'Deep Sanitization',
    category: 'Hygiene',
    position: [-0.3, 0.1, 1.4],
    icon: Sparkles,
    description: 'Medical-grade surface disinfection & architectural glass care',
    tag: 'Eco Certified',
  },
  {
    id: 'appliances',
    name: 'Appliance Care',
    category: 'Hardware',
    position: [1.2, -0.3, 1.1],
    icon: Wrench,
    description: 'Component-level diagnosis for premium kitchen & laundry suites',
    tag: 'OEM Parts',
  },
  {
    id: 'carpentry',
    name: 'Carpentry & Millwork',
    category: 'Structures',
    position: [-1.1, 0.9, -0.8],
    icon: Hammer,
    description: 'Precision cabinetry, acoustic wood finishes & frame repairs',
    tag: 'Craftsmen',
  },
  {
    id: 'painting',
    name: 'Façade & Painting',
    category: 'Finishes',
    position: [-1.9, 1.2, 0.5],
    icon: Paintbrush,
    description: 'Weather-resistant coating & interior architectural finishes',
    tag: 'Premium Coat',
  },
  {
    id: 'maintenance',
    name: 'General Maintenance',
    category: 'Diagnostics',
    position: [0, -0.8, 0],
    icon: ShieldCheck,
    description: 'Comprehensive home health checkup & preventive servicing',
    tag: 'SmartVerify',
  },
];

// Interactive 3D Modern Architectural Residence Model
const ArchitecturalHouse: React.FC<{
  activeHotspot: string | null;
  onSelectHotspot: (id: string) => void;
}> = ({ activeHotspot, onSelectHotspot }) => {
  const groupRef = useRef<THREE.Group>(null);
  const [mousePos, setMousePos] = useState({ x: 0, y: 0 });

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      const x = (e.clientX / window.innerWidth - 0.5) * 2;
      const y = -(e.clientY / window.innerHeight - 0.5) * 2;
      setMousePos({ x, y });
    };
    window.addEventListener('mousemove', handleMouseMove);
    return () => window.removeEventListener('mousemove', handleMouseMove);
  }, []);

  useFrame((state, delta) => {
    if (!groupRef.current) return;
    // Smooth camera / group parallax
    groupRef.current.rotation.y = THREE.MathUtils.lerp(
      groupRef.current.rotation.y,
      -0.45 + mousePos.x * 0.15,
      delta * 2.5
    );
    groupRef.current.rotation.x = THREE.MathUtils.lerp(
      groupRef.current.rotation.x,
      0.15 - mousePos.y * 0.08,
      delta * 2.5
    );
  });

  return (
    <group ref={groupRef} position={[0, -0.2, 0]}>
      {/* Concrete Foundation Plinth */}
      <mesh position={[0, -1.05, 0]} receiveShadow>
        <boxGeometry args={[4.8, 0.15, 3.8]} />
        <meshStandardMaterial color="#12151A" roughness={0.7} metalness={0.2} />
      </mesh>

      {/* Ground Grid Trim Ring */}
      <mesh position={[0, -1.13, 0]} receiveShadow>
        <boxGeometry args={[5.2, 0.02, 4.2]} />
        <meshStandardMaterial color="#0D0F12" roughness={0.9} />
      </mesh>

      {/* Main Ground Floor Volume - Dark Architectural Slate */}
      <mesh position={[-0.4, -0.35, 0.1]} castShadow receiveShadow>
        <boxGeometry args={[3.2, 1.25, 2.6]} />
        <meshStandardMaterial color="#181C22" roughness={0.35} metalness={0.4} />
      </mesh>

      {/* Ground Floor Panoramic Tinted Glass Pavilion */}
      <mesh position={[-0.1, -0.35, 1.22]}>
        <planeGeometry args={[2.6, 1.1]} />
        <meshPhysicalMaterial
          color="#8FA8A0"
          roughness={0.1}
          transmission={0.85}
          thickness={0.5}
          ior={1.5}
          transparent
          opacity={0.65}
        />
      </mesh>

      {/* Interior Warm Illumination Core */}
      <pointLight position={[-0.2, -0.3, 0.4]} intensity={2.5} distance={3.5} color="#F5E8D0" />
      <pointLight position={[1.0, 0.8, 0.2]} intensity={activeHotspot ? 4.0 : 2.0} distance={4.0} color="#8FA8A0" />

      {/* Upper Floor Cantilevered Architectural Cube */}
      <mesh position={[0.6, 0.85, -0.1]} castShadow receiveShadow>
        <boxGeometry args={[2.8, 1.15, 2.4]} />
        <meshStandardMaterial
          color="#22272F"
          roughness={0.25}
          metalness={0.6}
        />
      </mesh>

      {/* Upper Level Framed Glass Façade */}
      <mesh position={[0.6, 0.85, 1.12]}>
        <planeGeometry args={[2.4, 0.95]} />
        <meshPhysicalMaterial
          color="#E8E9E7"
          roughness={0.15}
          transmission={0.8}
          thickness={0.4}
          ior={1.4}
          transparent
          opacity={0.6}
        />
      </mesh>

      {/* Architectural Roof Overhang / Solar Canopy */}
      <mesh position={[0.6, 1.48, -0.05]} castShadow>
        <boxGeometry args={[3.3, 0.1, 2.9]} />
        <meshStandardMaterial color="#0D0F12" roughness={0.4} metalness={0.8} />
      </mesh>

      {/* Roof HVAC Unit (AC Service anchor) */}
      <mesh position={[0.8, 1.62, 0.3]} castShadow>
        <boxGeometry args={[0.7, 0.22, 0.6]} />
        <meshStandardMaterial
          color={activeHotspot === 'ac' ? '#8FA8A0' : '#2A303A'}
          roughness={0.3}
          metalness={0.7}
        />
      </mesh>

      {/* Architectural Timber Louvers on Right Volume */}
      {[-0.6, -0.2, 0.2, 0.6].map((xOffset, idx) => (
        <mesh key={idx} position={[1.9, 0.85, xOffset]} castShadow>
          <boxGeometry args={[0.08, 1.0, 0.18]} />
          <meshStandardMaterial color="#5C746D" roughness={0.6} metalness={0.2} />
        </mesh>
      ))}

      {/* Entry Glass Canopy & Porch */}
      <mesh position={[-1.6, -0.3, 1.4]} castShadow>
        <boxGeometry args={[0.9, 0.05, 0.8]} />
        <meshStandardMaterial color="#8FA8A0" transparent opacity={0.7} />
      </mesh>

      {/* Hotspots */}
      {SERVICE_HOTSPOTS.map((hotspot) => {
        const isSelected = activeHotspot === hotspot.id;
        const IconComponent = hotspot.icon;

        return (
          <group key={hotspot.id} position={hotspot.position}>
            <Html center distanceFactor={7} zIndexRange={[40, 0]}>
              <div 
                className="group relative cursor-pointer select-none"
                onClick={(e) => {
                  e.stopPropagation();
                  onSelectHotspot(hotspot.id);
                }}
              >
                {/* Outer Pulsing Ring */}
                <div className={`w-8 h-8 rounded-full flex items-center justify-center transition-all duration-300 ${
                  isSelected 
                    ? 'bg-sage-400 text-dark-950 ring-4 ring-sage-400/30 scale-110 shadow-accent' 
                    : 'bg-dark-900/90 text-sage-400 border border-sage-400/40 hover:border-sage-400 hover:scale-110 hover:bg-dark-850 shadow-card backdrop-blur-md'
                }`}>
                  <IconComponent className="w-4 h-4 transition-transform group-hover:scale-110" />
                </div>

                {/* Tooltip Card */}
                <div className={`absolute bottom-10 ${
                  hotspot.position[0] < -1.0 
                    ? 'left-0' 
                    : hotspot.position[0] > 1.0 
                      ? 'right-0' 
                      : 'left-1/2 -translate-x-1/2'
                } w-52 p-3 rounded-xl bg-dark-900/95 border border-dark-750 backdrop-blur-xl shadow-modal pointer-events-none transition-all duration-200 ${
                  isSelected ? 'opacity-100 translate-y-0 scale-100' : 'opacity-0 translate-y-2 scale-95 group-hover:opacity-100 group-hover:translate-y-0 group-hover:scale-100'
                }`}>
                  <div className="flex items-center justify-between gap-2 mb-1">
                    <span className="text-xs font-semibold text-white tracking-tight">{hotspot.name}</span>
                    <span className="text-[9px] font-mono uppercase px-1.5 py-0.5 rounded bg-sage-400/15 text-sage-300 border border-sage-400/30">
                      {hotspot.tag}
                    </span>
                  </div>
                  <p className="text-[11px] text-slate-400 leading-snug mb-2">{hotspot.description}</p>
                  <div className="flex items-center justify-between text-[10px] font-medium text-sage-400">
                    <span>Click to select</span>
                    <ChevronRight className="w-3 h-3" />
                  </div>
                </div>
              </div>
            </Html>
          </group>
        );
      })}
    </group>
  );
};

// 2D Interactive Fallback for devices without WebGL or reduced-motion
const FallbackArchitecturalView: React.FC<{
  activeHotspot: string | null;
  onSelectHotspot: (id: string) => void;
}> = ({ activeHotspot, onSelectHotspot }) => {
  return (
    <div className="relative w-full h-full min-h-[420px] rounded-3xl bg-gradient-to-b from-dark-900 via-dark-850 to-dark-950 border border-dark-750 p-6 flex flex-col justify-between overflow-hidden shadow-card">
      {/* Background Architectural Blueprint Grid */}
      <div 
        className="absolute inset-0 opacity-15 pointer-events-none"
        style={{
          backgroundImage: 'radial-gradient(circle, #8FA8A0 1px, transparent 1px)',
          backgroundSize: '24px 24px'
        }}
      />

      <div className="relative z-10 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className="w-2.5 h-2.5 rounded-full bg-sage-400 animate-pulse" />
          <span className="text-xs font-mono tracking-widest text-slate-400 uppercase">ARCHITECTURAL SERVICE ECOSYSTEM</span>
        </div>
        <span className="text-xs font-mono px-2.5 py-1 rounded bg-dark-800 text-slate-300 border border-dark-750">
          8 Service Points Active
        </span>
      </div>

      {/* Interactive Blueprint Service Grid */}
      <div className="relative z-10 grid grid-cols-2 sm:grid-cols-4 gap-3 my-6">
        {SERVICE_HOTSPOTS.map((hotspot) => {
          const isSelected = activeHotspot === hotspot.id;
          const Icon = hotspot.icon;
          return (
            <button
              key={hotspot.id}
              onClick={() => onSelectHotspot(hotspot.id)}
              className={`p-3.5 rounded-xl text-left transition-all duration-200 border ${
                isSelected
                  ? 'bg-sage-400/15 border-sage-400 text-white shadow-accent'
                  : 'bg-dark-900/80 border-dark-750 hover:border-dark-700 text-slate-300 hover:bg-dark-850'
              }`}
            >
              <div className="flex items-center justify-between mb-2">
                <div className={`p-2 rounded-lg ${isSelected ? 'bg-sage-400 text-dark-950' : 'bg-dark-800 text-sage-400'}`}>
                  <Icon className="w-4 h-4" />
                </div>
                <span className="text-[9px] font-mono text-slate-400">{hotspot.category}</span>
              </div>
              <p className="text-xs font-semibold text-white">{hotspot.name}</p>
              <p className="text-[10px] text-slate-400 line-clamp-1 mt-0.5">{hotspot.description}</p>
            </button>
          );
        })}
      </div>

      <div className="relative z-10 text-[11px] font-mono text-slate-400 text-center">
        Select any node to explore specialized technicians & instant booking.
      </div>
    </div>
  );
};

export const HeroScene3D: React.FC = () => {
  const [activeHotspot, setActiveHotspot] = useState<string | null>('ac');
  const [hasWebGL, setHasWebGL] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    try {
      const canvas = document.createElement('canvas');
      const gl = canvas.getContext('webgl') || canvas.getContext('experimental-webgl');
      if (!gl) setHasWebGL(false);
    } catch {
      setHasWebGL(false);
    }
  }, []);

  const selectedData = SERVICE_HOTSPOTS.find((s) => s.id === activeHotspot) || SERVICE_HOTSPOTS[0];

  return (
    <div className="relative w-full h-[520px] lg:h-[620px] rounded-3xl overflow-hidden border border-dark-750 bg-gradient-to-b from-dark-950 via-dark-900 to-dark-950 shadow-modal">
      {/* 3D Canvas / Fallback */}
      {hasWebGL ? (
        <Suspense fallback={<FallbackArchitecturalView activeHotspot={activeHotspot} onSelectHotspot={setActiveHotspot} />}>
          <Canvas
            shadows
            dpr={[1, 2]}
            gl={{ antialias: true, alpha: true }}
            className="w-full h-full cursor-grab active:cursor-grabbing"
          >
            <PerspectiveCamera makeDefault position={[0, 1.2, 5.2]} fov={45} />
            
            {/* Ambient & Key Architectural Lighting */}
            <ambientLight intensity={0.65} color="#E8E9E7" />
            <directionalLight
              position={[5, 8, 5]}
              intensity={1.8}
              castShadow
              shadow-mapSize-width={1024}
              shadow-mapSize-height={1024}
              color="#FFFFFF"
            />
            <directionalLight position={[-5, 4, -4]} intensity={0.6} color="#8FA8A0" />

            <Float speed={1.5} rotationIntensity={0.1} floatIntensity={0.25}>
              <ArchitecturalHouse
                activeHotspot={activeHotspot}
                onSelectHotspot={(id) => setActiveHotspot(id === activeHotspot ? null : id)}
              />
            </Float>
          </Canvas>
        </Suspense>
      ) : (
        <FallbackArchitecturalView activeHotspot={activeHotspot} onSelectHotspot={setActiveHotspot} />
      )}

      {/* Floating Active Service Highlight Bar at Bottom */}
      <div className="absolute bottom-4 left-4 right-4 sm:left-6 sm:right-6 p-4 rounded-2xl bg-dark-900/90 backdrop-blur-xl border border-dark-750 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 shadow-card">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-sage-400/15 border border-sage-400/30 flex items-center justify-center text-sage-400 shrink-0">
            <selectedData.icon className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h4 className="text-sm font-semibold text-white">{selectedData.name}</h4>
              <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-dark-800 text-slate-300 border border-dark-750">
                {selectedData.category}
              </span>
            </div>
            <p className="text-xs text-slate-400 line-clamp-1 mt-0.5">{selectedData.description}</p>
          </div>
        </div>

        <div className="flex items-center gap-2 w-full sm:w-auto shrink-0">
          <button
            onClick={() => navigate('/services')}
            className="flex-1 sm:flex-none px-3.5 py-2 rounded-xl text-xs font-medium bg-dark-850 hover:bg-dark-800 text-slate-300 hover:text-white border border-dark-750 transition-colors flex items-center justify-center gap-1.5"
          >
            <Eye className="w-3.5 h-3.5" />
            <span>Details</span>
          </button>
          <button
            onClick={() => navigate('/booking/new')}
            className="flex-1 sm:flex-none px-4 py-2 rounded-xl text-xs font-semibold bg-sage-400 hover:bg-sage-300 text-dark-950 shadow-accent transition-all flex items-center justify-center gap-1.5"
          >
            <span>Book Service</span>
            <ChevronRight className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>
    </div>
  );
};
