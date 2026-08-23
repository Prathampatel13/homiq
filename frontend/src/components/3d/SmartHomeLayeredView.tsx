import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Utensils, 
  Tv, 
  BedDouble, 
  TreePine, 
  ArrowRight, 
  ShieldCheck, 
  ChevronRight,
  Sparkles,
  Zap,
  Droplet,
  Wind
} from 'lucide-react';

interface ZoneData {
  id: string;
  name: string;
  subtitle: string;
  icon: React.ElementType;
  description: string;
  services: { name: string; time: string; tag: string; price: number }[];
}

const ZONES: ZoneData[] = [
  {
    id: 'kitchen',
    name: 'Kitchen Suite',
    subtitle: 'HYDRAULIC & APPLIANCE CORE',
    icon: Utensils,
    description: 'High-traffic zone requiring precision water pressure balancing, appliance descaling, and food-grade sanitization.',
    services: [
      { name: 'Water Line & Filter Checkup', time: '45 mins', tag: 'Plumbing', price: 499 },
      { name: 'Dishwasher & Oven Suite Audit', time: '60 mins', tag: 'Appliances', price: 649 },
      { name: 'Deep Degreasing & Sanitization', time: '90 mins', tag: 'Sanitization', price: 899 },
    ],
  },
  {
    id: 'living',
    name: 'Living & Lounge',
    subtitle: 'SMART POWER & CLIMATE ZONE',
    icon: Tv,
    description: 'Central residence volume optimized for acoustic comfort, balanced airflow, and concealed wiring.',
    services: [
      { name: 'AC Master Coil Sanitization', time: '45 mins', tag: 'HVAC', price: 699 },
      { name: 'Smart Switch & Load Calibration', time: '30 mins', tag: 'Electrical', price: 449 },
      { name: 'Acoustic Wood & Wall Care', time: '60 mins', tag: 'Carpentry', price: 599 },
    ],
  },
  {
    id: 'bedroom',
    name: 'Private Quarters',
    subtitle: 'THERMAL & AIR PURITY CORE',
    icon: BedDouble,
    description: 'Sanctuary spaces requiring silent HVAC operation, HEPA air filtration, and ambient lighting stability.',
    services: [
      { name: 'Split AC Silent Purity Service', time: '40 mins', tag: 'HVAC', price: 599 },
      { name: 'Mattress & Upholstery Sanitize', time: '50 mins', tag: 'Hygiene', price: 699 },
      { name: 'Wardrobe Slider & Hinge Tune', time: '30 mins', tag: 'Hardware', price: 399 },
    ],
  },
  {
    id: 'exterior',
    name: 'Exterior & Perimeter',
    subtitle: 'FAÇADE & UTILITY MATRIX',
    icon: TreePine,
    description: 'Structural perimeter protecting main lines, rooftop units, water tanks, and architectural lighting.',
    services: [
      { name: 'Rooftop Tank Sterilization', time: '75 mins', tag: 'Hydraulics', price: 799 },
      { name: 'Perimeter Floodlight Inspection', time: '45 mins', tag: 'Power', price: 499 },
      { name: 'Façade Waterproofing Inspection', time: '60 mins', tag: 'Structural', price: 649 },
    ],
  },
];

export const SmartHomeLayeredView: React.FC = () => {
  const [activeZone, setActiveZone] = useState<string>('kitchen');
  const navigate = useNavigate();

  const selectedZone = ZONES.find((z) => z.id === activeZone) || ZONES[0];

  return (
    <section className="py-24 border-t border-dark-750/80 bg-dark-950 relative overflow-hidden">
      {/* Subtle Radial Glow */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-sage-400/5 rounded-full blur-3xl pointer-events-none" />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        {/* Section Headline */}
        <div className="text-center max-w-3xl mx-auto mb-16 space-y-3">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-dark-850 border border-dark-750">
            <span className="w-2 h-2 rounded-full bg-sage-400" />
            <span className="text-[11px] font-mono tracking-widest text-slate-300 uppercase">
              ARCHITECTURAL ECOSYSTEM
            </span>
          </div>

          <h2 className="text-3xl sm:text-4xl lg:text-5xl font-extrabold tracking-tight text-white uppercase">
            YOUR HOME. ONE INTELLIGENT PLATFORM.
          </h2>

          <p className="text-sm sm:text-base text-slate-400 max-w-xl mx-auto leading-relaxed">
            Every architectural zone of your residence is mapped to verified, certified maintenance procedures.
          </p>
        </div>

        {/* Zone Selector Buttons */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 max-w-4xl mx-auto mb-12">
          {ZONES.map((zone) => {
            const isSelected = activeZone === zone.id;
            const ZoneIcon = zone.icon;
            return (
              <button
                key={zone.id}
                onClick={() => setActiveZone(zone.id)}
                className={`p-4 rounded-2xl border text-left transition-all duration-200 flex flex-col justify-between ${
                  isSelected
                    ? 'bg-dark-850 border-sage-400 text-white shadow-accent ring-1 ring-sage-400/40'
                    : 'bg-dark-900/90 border-dark-750 hover:border-dark-700 text-slate-400 hover:text-white hover:bg-dark-850'
                }`}
              >
                <div className="flex items-center justify-between mb-3">
                  <div className={`p-2.5 rounded-xl ${isSelected ? 'bg-sage-400 text-dark-950 font-bold' : 'bg-dark-800 text-sage-400'}`}>
                    <ZoneIcon className="w-5 h-5" />
                  </div>
                  <ChevronRight className={`w-4 h-4 transition-transform ${isSelected ? 'rotate-90 text-sage-400' : 'text-slate-600'}`} />
                </div>
                <div>
                  <h4 className="text-xs font-bold text-white tracking-tight">{zone.name}</h4>
                  <span className="text-[10px] font-mono text-slate-400 block mt-0.5">{zone.subtitle}</span>
                </div>
              </button>
            );
          })}
        </div>

        {/* Active Zone Interactive Blueprint Card */}
        <div className="rounded-3xl bg-gradient-to-b from-dark-900 via-dark-850 to-dark-900 border border-dark-750 p-6 sm:p-10 shadow-modal grid grid-cols-1 lg:grid-cols-12 gap-8 items-center">
          {/* Left: Zone Schematic & Description */}
          <div className="lg:col-span-5 space-y-4">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-dark-800 border border-dark-750">
              <ShieldCheck className="w-3.5 h-3.5 text-sage-400" />
              <span className="text-xs font-mono tracking-wider text-sage-300 uppercase">{selectedZone.subtitle}</span>
            </div>

            <h3 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
              {selectedZone.name}
            </h3>

            <p className="text-xs sm:text-sm text-slate-400 leading-relaxed">
              {selectedZone.description}
            </p>

            <div className="pt-4 border-t border-dark-750 flex items-center gap-4 text-xs font-mono text-slate-400">
              <span className="flex items-center gap-1 text-slate-300">
                <ShieldCheck className="w-4 h-4 text-sage-400" /> SmartVerify Protocols
              </span>
              <span>•</span>
              <span>100% Guaranteed</span>
            </div>
          </div>

          {/* Right: Specialized Service Tasks */}
          <div className="lg:col-span-7 space-y-3">
            <span className="text-xs font-mono text-slate-400 uppercase tracking-wider block mb-2">
              Verified Maintenance Procedures
            </span>

            {selectedZone.services.map((service, idx) => (
              <div
                key={idx}
                onClick={() => navigate('/booking/new')}
                className="group p-4 rounded-2xl bg-dark-900/90 hover:bg-dark-800 border border-dark-750 hover:border-sage-400/50 transition-all duration-200 cursor-pointer flex items-center justify-between shadow-subtle"
              >
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <span className="text-xs sm:text-sm font-bold text-white group-hover:text-sage-300 transition-colors">
                      {service.name}
                    </span>
                    <span className="text-[9px] font-mono uppercase px-2 py-0.5 rounded bg-dark-800 text-slate-300 border border-dark-750">
                      {service.tag}
                    </span>
                  </div>
                  <p className="text-[11px] font-mono text-slate-400">Standard Duration: {service.time}</p>
                </div>

                <div className="flex items-center gap-3 shrink-0">
                  <span className="text-xs font-mono font-bold text-white px-2.5 py-1 rounded-lg bg-dark-850 border border-dark-750">
                    ₹{service.price.toFixed(2)}
                  </span>
                  <div className="w-8 h-8 rounded-xl bg-dark-800 group-hover:bg-sage-400 text-slate-400 group-hover:text-dark-950 flex items-center justify-center transition-colors">
                    <ArrowRight className="w-4 h-4" />
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
};
