import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, useScroll, useTransform, AnimatePresence } from 'framer-motion';
import { 
  ArrowRight, 
  Wind, 
  Droplet, 
  Zap, 
  Sparkles,
  ShieldCheck,
  CheckCircle2,
  Wrench,
  Clock,
  PhoneCall,
  Activity,
  Layers,
  ChevronRight,
  Flame,
  Cpu,
  Camera,
  Lock
} from 'lucide-react';
import { servicesApi } from '../api/services';
import { Service, ServiceCategory, UserRole } from '../types';
import { useAuthStore } from '../store/useAuthStore';
import { handleImageError } from '../utils/media';

// Refined, human-centered service data with modern pastel palette
const HERO_SERVICES = [
  {
    id: 'ac',
    name: 'AC & Cooling',
    subtitle: 'Installation, servicing & cooling repairs',
    category: 'CLIMATE',
    iconImg: '/assets/services/ac.jpg',
    heroImg: '/assets/hero_ac.jpg',
    price: '₹499',
    eta: '18 mins',
    rating: '4.98',
    specs: ['Deep Coil Cleaning', 'Gas Leak & Pressure Check', 'Thermostat Diagnostics'],
    accentColor: '#B8DB80',
    accentClass: 'text-sage-400 border-sage-400/30 bg-sage-400/10',
  },
  {
    id: 'electrical',
    name: 'Electrical & Wiring',
    subtitle: 'Power fixtures, circuit repairs & MCB',
    category: 'ELECTRICAL',
    iconImg: '/assets/services/electrical.jpg',
    heroImg: '/assets/services/electrical.jpg',
    price: '₹199',
    eta: '15 mins',
    rating: '4.99',
    specs: ['Circuit Diagnostics', 'Smart MCB Upgrade', 'Appliance & Switch Install'],
    accentColor: '#F7F6D3',
    accentClass: 'text-[#EDEBC0] border-[#F7F6D3]/30 bg-[#F7F6D3]/10',
  },
  {
    id: 'plumbing',
    name: 'Plumbing & Pipes',
    subtitle: 'Leak detection, taps & drainage solutions',
    category: 'PLUMBING',
    iconImg: '/assets/services/plumbing.jpg',
    heroImg: '/assets/service_plumbing.jpg',
    price: '₹299',
    eta: '22 mins',
    rating: '4.96',
    specs: ['Acoustic Leak Inspection', 'High-Pressure Valve Care', 'Drainage Clearance'],
    accentColor: '#FFE4EF',
    accentClass: 'text-rose-300 border-blush-200/30 bg-blush-100/10',
  },
  {
    id: 'security',
    name: 'Smart Security',
    subtitle: 'Smart locks, surveillance & sensors',
    category: 'SECURITY',
    iconImg: '/assets/services/security.jpg',
    heroImg: '/assets/services/security.jpg',
    price: '₹599',
    eta: '25 mins',
    rating: '4.99',
    specs: ['Smart Lock Calibration', 'CCTV Mesh Setup', 'Hub & Sensor Sync'],
    accentColor: '#F39EB6',
    accentClass: 'text-rose-400 border-rose-400/30 bg-rose-400/10',
  },
  {
    id: 'cleaning',
    name: 'Deep Cleaning',
    subtitle: 'Full home, kitchen & bathroom care',
    category: 'SANITIZATION',
    iconImg: '/assets/services/cleaning.jpg',
    heroImg: '/assets/services/cleaning.jpg',
    price: '₹999',
    eta: '30 mins',
    rating: '4.95',
    specs: ['Hospital-Grade Sanitization', 'Kitchen Degreasing', 'Upholstery & Fabric Care'],
    accentColor: '#B8DB80',
    accentClass: 'text-sage-400 border-sage-400/30 bg-sage-400/10',
  },
  {
    id: 'carpentry',
    name: 'Carpentry & Repairs',
    subtitle: 'Door fitting, hardware & structural care',
    category: 'CARPENTRY',
    iconImg: '/assets/services/carpentry.jpg',
    heroImg: '/assets/services/carpentry.jpg',
    price: '₹349',
    eta: '20 mins',
    rating: '4.97',
    specs: ['Door Alignment & Locks', 'Custom Shelving', 'Hardware Reinforcement'],
    accentColor: '#F39EB6',
    accentClass: 'text-rose-400 border-rose-400/30 bg-rose-400/10',
  },
];

export const LandingPage: React.FC = () => {
  const navigate = useNavigate();
  const [categories, setCategories] = useState<ServiceCategory[]>([]);
  const [featuredServices, setFeaturedServices] = useState<Service[]>([]);
  const [activeService, setActiveService] = useState(HERO_SERVICES[0]);
  const { getEffectiveRole } = useAuthStore();
  const role = getEffectiveRole();
  const { scrollYProgress } = useScroll();

  const yBg = useTransform(scrollYProgress, [0, 1], ['0%', '25%']);

  useEffect(() => {
    if (role === UserRole.TECHNICIAN) {
      navigate('/provider/dashboard', { replace: true });
    }
  }, [role, navigate]);

  useEffect(() => {
    const loadHomeData = async () => {
      try {
        const [cats, servs] = await Promise.all([
          servicesApi.getCategories(),
          servicesApi.getServices({ limit: 4 })
        ]);
        setCategories(cats);
        setFeaturedServices(servs);
      } catch (e) {
        console.error('Failed to load home data', e);
      }
    };
    loadHomeData();
  }, []);

  // Animation variants
  const containerVariants = {
    hidden: { opacity: 0 },
    visible: { 
      opacity: 1,
      transition: { staggerChildren: 0.08, delayChildren: 0.15 }
    }
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 25 },
    visible: { opacity: 1, y: 0, transition: { duration: 0.7, ease: [0.16, 1, 0.3, 1] } }
  };

  return (
    <div className="bg-dark-950 text-slate-900 min-h-screen overflow-hidden selection:bg-sage-500 selection:text-white font-sans">
      
      {/* ──────────────────────────────────────────────────────────────────────────
          1. HERO SECTION: MINIMAL & ELEGANT
      ────────────────────────────────────────────────────────────────────────── */}
      <section className="relative pt-20 pb-16 overflow-hidden">
        
        {/* Soft Ambient Pastel Atmosphere */}
        <div className="absolute top-1/4 left-1/4 w-[500px] h-[400px] bg-sage-400/8 rounded-full blur-[140px] pointer-events-none" />
        <div className="absolute top-1/3 right-1/4 w-[400px] h-[350px] bg-rose-400/6 rounded-full blur-[130px] pointer-events-none" />

        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
          
          {/* Main Hero Split */}
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 lg:gap-8 items-center min-h-[500px]">
            
            {/* Left Column: Clear Value Proposition */}
            <motion.div 
              initial="hidden"
              animate="visible"
              variants={containerVariants}
              className="lg:col-span-6 space-y-6"
            >
              {/* Refined Status Pill */}
              <motion.div variants={itemVariants} className="inline-flex items-center gap-2.5 px-3.5 py-1.5 rounded-full bg-dark-900 border border-dark-750 shadow-subtle">
                <span className="w-2 h-2 rounded-full bg-sage-400 animate-pulse shadow-[0_0_8px_rgba(184,219,128,0.8)]" />
                <span className="text-xs font-semibold tracking-wider text-slate-300 uppercase">
                  VERIFIED RESIDENTIAL CARE
                </span>
              </motion.div>

              {/* Minimal Editorial Headline */}
              <motion.h1 variants={itemVariants} className="text-4xl sm:text-6xl font-bold tracking-tight leading-[1.08] text-white">
                Professional home care,<br />
                <span className="text-transparent bg-clip-text bg-gradient-to-r from-white via-cream-200 to-sage-400">
                  beautifully delivered.
                </span>
              </motion.h1>

              {/* Clean Subtitle */}
              <motion.p variants={itemVariants} className="text-base text-slate-400 font-normal leading-relaxed max-w-lg">
                Connect with background-verified specialists for AC, electrical, plumbing, smart security, and repairs. Transparent pricing, fast dispatch, and guaranteed quality.
              </motion.p>

              {/* Direct Actions */}
              <motion.div variants={itemVariants} className="flex flex-wrap items-center gap-3.5 pt-2">
                <button
                  onClick={() => navigate('/booking/new')}
                  className="px-7 py-3.5 bg-sage-400 hover:bg-sage-300 text-dark-950 font-bold text-sm rounded-xl transition-all duration-200 shadow-subtle hover:shadow-accent flex items-center gap-2.5 active:scale-98"
                >
                  <span>Book a Service</span>
                  <ArrowRight className="w-4 h-4" />
                </button>

                <button
                  onClick={() => navigate('/services')}
                  className="px-6 py-3.5 bg-dark-900 hover:bg-dark-850 text-slate-300 hover:text-white border border-dark-750 hover:border-dark-700 rounded-xl text-sm font-medium transition-all flex items-center gap-2"
                >
                  <span>Explore Catalog</span>
                  <ChevronRight className="w-4 h-4 text-slate-500" />
                </button>
              </motion.div>

              {/* Key Trust Stats */}
              <motion.div variants={itemVariants} className="pt-6 border-t border-dark-750/70 grid grid-cols-3 gap-6 max-w-md">
                <div>
                  <span className="text-2xl font-bold text-white block">15 min</span>
                  <span className="text-xs text-slate-400 font-medium">Avg. Arrival</span>
                </div>
                <div>
                  <span className="text-2xl font-bold text-white block">100%</span>
                  <span className="text-xs text-slate-400 font-medium">Verified Pros</span>
                </div>
                <div>
                  <span className="text-2xl font-bold text-white block">4.9★</span>
                  <span className="text-xs text-slate-400 font-medium">Customer Rating</span>
                </div>
              </motion.div>
            </motion.div>

            {/* Right Column: Clean Visual Showcase */}
            <motion.div 
              initial={{ opacity: 0, scale: 0.96 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.8, ease: [0.16, 1, 0.3, 1] }}
              className="lg:col-span-6 relative flex flex-col items-center justify-center"
            >
              <div className="relative w-full max-w-[500px] aspect-square flex items-center justify-center">
                
                {/* Subtle Geometric Framing */}
                <div className="absolute inset-0 rounded-3xl border border-dark-750/60 bg-gradient-to-b from-dark-900/60 to-dark-950/80 backdrop-blur-sm" />
                <div className="absolute inset-2 rounded-2xl border border-white/5 pointer-events-none" />

                {/* Animated Service Asset */}
                <AnimatePresence mode="wait">
                  <motion.div
                    key={activeService.id}
                    initial={{ opacity: 0, scale: 0.92, y: 15 }}
                    animate={{ opacity: 1, scale: 1, y: 0 }}
                    exit={{ opacity: 0, scale: 0.95, y: -10 }}
                    transition={{ duration: 0.4, ease: "easeOut" }}
                    className="relative w-full h-full p-8 flex items-center justify-center z-10"
                  >
                    <motion.img 
                      animate={{ y: [0, -8, 0] }}
                      transition={{ repeat: Infinity, duration: 5, ease: "easeInOut" }}
                      src={activeService.heroImg} 
                      alt={activeService.name} 
                      onError={(e) => handleImageError(e, 'service')}
                      className="max-h-[360px] w-auto object-contain rounded-2xl drop-shadow-[0_20px_40px_rgba(0,0,0,0.6)] select-none"
                    />
                  </motion.div>
                </AnimatePresence>

                {/* Minimal Overlay Preview Pill (Bottom Center) */}
                <motion.div 
                  key={`pill-${activeService.id}`}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.2 }}
                  className="absolute bottom-4 inset-x-4 bg-dark-900/90 backdrop-blur-md border border-dark-750/80 p-3.5 rounded-2xl shadow-card flex items-center justify-between z-20"
                >
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-xl overflow-hidden border border-dark-750 shrink-0">
                      <img 
                        src={activeService.iconImg} 
                        alt={activeService.name}
                        onError={(e) => handleImageError(e, 'service')}
                        className="w-full h-full object-cover" 
                      />
                    </div>
                    <div>
                      <h4 className="text-sm font-semibold text-white leading-tight">{activeService.name}</h4>
                      <p className="text-xs text-slate-400 mt-0.5">{activeService.subtitle}</p>
                    </div>
                  </div>

                  <div className="text-right shrink-0 pl-3 border-l border-dark-750">
                    <span className="text-sm font-bold text-sage-400 block">{activeService.price}</span>
                    <span className="text-[11px] text-slate-400">Starting price</span>
                  </div>
                </motion.div>

              </div>
            </motion.div>

          </div>

          {/* ──────────────────────────────────────────────────────────────────────────
              INTERACTIVE SERVICE DOCK
          ────────────────────────────────────────────────────────────────────────── */}
          <div className="mt-14 pt-8 border-t border-dark-750/70">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-sage-400" />
                <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-300">
                  Select a Service to Preview
                </h3>
              </div>
              <span className="text-xs text-slate-400">6 Core Categories</span>
            </div>

            <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
              {HERO_SERVICES.map((srv) => {
                const isSelected = activeService.id === srv.id;
                return (
                  <button
                    key={srv.id}
                    onClick={() => setActiveService(srv)}
                    className={`p-3 rounded-2xl text-left transition-all duration-200 relative border flex flex-col justify-between ${
                      isSelected 
                        ? 'bg-dark-850 border-sage-400 shadow-[0_0_20px_rgba(184,219,128,0.2)] ring-1 ring-sage-400' 
                        : 'bg-dark-900/60 hover:bg-dark-850/60 border-dark-750/70 hover:border-dark-700'
                    }`}
                  >
                    <div className="flex items-center justify-between mb-2.5 w-full">
                      <div className={`w-10 h-10 rounded-xl overflow-hidden border p-0.5 transition-all ${
                        isSelected ? 'border-sage-400' : 'border-dark-750'
                      }`}>
                        <img 
                          src={srv.iconImg} 
                          alt={srv.name} 
                          onError={(e) => handleImageError(e, 'service')}
                          className="w-full h-full object-cover rounded-lg"
                        />
                      </div>
                      
                      <span className={`w-2 h-2 rounded-full transition-all ${
                        isSelected ? 'bg-sage-400' : 'bg-dark-750'
                      }`} />
                    </div>

                    <div>
                      <h4 className={`text-xs font-semibold leading-tight ${
                        isSelected ? 'text-white' : 'text-slate-300'
                      }`}>
                        {srv.name}
                      </h4>
                      <div className="flex items-center justify-between mt-2 pt-1.5 border-t border-dark-750/50 text-[11px]">
                        <span className="font-semibold text-sage-400">{srv.price}</span>
                        <span className="text-slate-400">{srv.eta}</span>
                      </div>
                    </div>
                  </button>
                );
              })}
            </div>
          </div>

        </div>
      </section>

      {/* ──────────────────────────────────────────────────────────────────────────
          2. HOW IT WORKS: 3-STEP SEAMLESS FLOW
      ────────────────────────────────────────────────────────────────────────── */}
      <section className="py-20 bg-dark-900/50 border-t border-dark-750/70">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          
          <div className="text-center max-w-2xl mx-auto mb-14 space-y-2">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-dark-850 border border-dark-750 mb-2">
              <Sparkles className="w-3.5 h-3.5 text-sage-400" />
              <span className="text-xs font-semibold tracking-wider text-slate-300 uppercase">SIMPLIFIED WORKFLOW</span>
            </div>
            <h2 className="text-3xl font-bold tracking-tight text-white">
              How HomiQ Works
            </h2>
            <p className="text-sm text-slate-400">
              From instant booking to verified completion — seamless, safe, and transparent.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {[
              {
                step: '01',
                title: 'Choose Service & Schedule',
                desc: 'Select what you need with upfront rates. Pick a time slot that fits your schedule without surprise charges.',
                icon: Layers,
                tagColor: 'text-sage-400 bg-sage-400/10 border-sage-400/30'
              },
              {
                step: '02',
                title: 'Verified Specialist Arrives',
                desc: 'Track arrival in real time. A secure 6-digit PIN ensures only your authorized technician initiates the job.',
                icon: ShieldCheck,
                tagColor: 'text-[#EDEBC0] bg-[#F7F6D3]/10 border-[#F7F6D3]/30'
              },
              {
                step: '03',
                title: 'Inspect & Pay with Guarantee',
                desc: 'Review Before & After photographic evidence before you authorize payment. Backed by our 30-day warranty.',
                icon: CheckCircle2,
                tagColor: 'text-rose-400 bg-rose-400/10 border-rose-400/30'
              }
            ].map((card, i) => {
              const Icon = card.icon;
              return (
                <div 
                  key={i} 
                  className="p-7 rounded-3xl bg-dark-900 border border-dark-750/80 shadow-card flex flex-col justify-between hover:border-dark-700 transition-all duration-200"
                >
                  <div className="space-y-4">
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-mono font-bold text-slate-500 tracking-wider">STEP {card.step}</span>
                      <div className={`w-9 h-9 rounded-xl border flex items-center justify-center ${card.tagColor}`}>
                        <Icon className="w-4 h-4" />
                      </div>
                    </div>
                    <h3 className="text-lg font-bold text-white">{card.title}</h3>
                    <p className="text-xs text-slate-400 leading-relaxed font-normal">{card.desc}</p>
                  </div>
                </div>
              );
            })}
          </div>

        </div>
      </section>

      {/* ──────────────────────────────────────────────────────────────────────────
          3. POPULAR SERVICES GRID
      ────────────────────────────────────────────────────────────────────────── */}
      <section className="py-20 border-t border-dark-750/70">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          
          <div className="flex flex-col md:flex-row md:items-end justify-between mb-12 gap-4">
            <div>
              <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-dark-850 border border-dark-750 mb-2">
                <Layers className="w-3.5 h-3.5 text-sage-400" />
                <span className="text-xs font-semibold tracking-wider text-slate-300 uppercase">POPULAR CATEGORIES</span>
              </div>
              <h3 className="text-3xl font-bold tracking-tight text-white">
                Services Built for Every Need
              </h3>
              <p className="text-slate-400 text-sm mt-1 max-w-xl">
                Fixed pricing with zero hidden fees. Certified technicians deployed to your location.
              </p>
            </div>

            <button
              onClick={() => navigate('/services')}
              className="px-5 py-2.5 bg-dark-900 hover:bg-dark-850 text-xs font-semibold uppercase tracking-wider text-slate-300 hover:text-white border border-dark-750 hover:border-dark-700 rounded-xl transition-all self-start md:self-auto flex items-center gap-2"
            >
              <span>View Full Catalog</span>
              <ArrowRight className="w-3.5 h-3.5 text-slate-400" />
            </button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {HERO_SERVICES.map((srv) => (
              <div
                key={srv.id}
                onClick={() => navigate('/booking/new')}
                className="p-6 bg-dark-900 rounded-3xl border border-dark-750/70 hover:border-sage-400/40 cursor-pointer transition-all duration-200 relative overflow-hidden shadow-card group"
              >
                {/* Header: Icon & Price */}
                <div className="flex items-center justify-between mb-5">
                  <div className="w-14 h-14 rounded-2xl overflow-hidden border border-dark-750 p-1 bg-dark-850">
                    <img 
                      src={srv.iconImg} 
                      alt={srv.name} 
                      onError={(e) => handleImageError(e, 'service')}
                      className="w-full h-full object-cover rounded-xl"
                    />
                  </div>
                  <div className="text-right">
                    <span className="text-base font-bold text-white block">{srv.price}</span>
                    <span className="text-[11px] text-slate-400">{srv.eta} arrival</span>
                  </div>
                </div>

                <h4 className="text-lg font-bold text-white mb-1 group-hover:text-sage-400 transition-colors">
                  {srv.name}
                </h4>
                <p className="text-slate-400 text-xs leading-relaxed mb-5">{srv.subtitle}</p>
                
                {/* Service Specs */}
                <div className="space-y-2 pt-4 border-t border-dark-750/60 text-xs text-slate-400">
                  {srv.specs.map((sp, idx) => (
                    <div key={idx} className="flex items-center gap-2">
                      <span className="w-1.5 h-1.5 rounded-full bg-sage-400/70" />
                      <span>{sp}</span>
                    </div>
                  ))}
                </div>

                {/* Card CTA */}
                <div className="mt-5 flex items-center justify-between pt-3.5 border-t border-dark-750/60 text-xs font-semibold text-slate-300 group-hover:text-sage-400 transition-colors">
                  <span>Book Service</span>
                  <ArrowRight className="w-3.5 h-3.5 transition-transform group-hover:translate-x-1" />
                </div>
              </div>
            ))}
          </div>

        </div>
      </section>

      {/* ──────────────────────────────────────────────────────────────────────────
          4. THE HOMIQ STANDARD & TRUST
      ────────────────────────────────────────────────────────────────────────── */}
      <section className="py-20 border-t border-dark-750/70 bg-dark-900/40">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          
          <div className="inline-flex items-center gap-2.5 px-4 py-1.5 bg-dark-900 border border-dark-750 rounded-full mb-6">
            <ShieldCheck className="w-4 h-4 text-sage-400" />
            <span className="text-xs font-semibold tracking-wider text-white uppercase">
              THE HOMIQ STANDARD
            </span>
          </div>

          <h2 className="text-3xl sm:text-4xl font-bold tracking-tight text-white mb-3">
            Peace of Mind on Every Visit
          </h2>
          <p className="text-slate-400 text-sm max-w-lg mx-auto mb-12">
            We hold all home care to rigorous quality and safety benchmarks.
          </p>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 text-left max-w-4xl mx-auto">
            {[
              { 
                icon: ShieldCheck,
                title: 'Vetted Specialists', 
                desc: 'Technicians undergo comprehensive background verification, trade screening, and continuous customer reviews.',
                badgeColor: 'text-sage-400 bg-sage-400/10 border-sage-400/30'
              },
              { 
                icon: Camera,
                title: 'Photo Proof of Work', 
                desc: 'Mandatory Before & After photographic documentation gives you full transparency before authorizing payment.',
                badgeColor: 'text-[#EDEBC0] bg-[#F7F6D3]/10 border-[#F7F6D3]/30'
              },
              { 
                icon: Lock,
                title: '30-Day Guarantee', 
                desc: 'Complete workmanship guarantee on repairs and installations. If something isn’t right, we re-service at no charge.',
                badgeColor: 'text-rose-400 bg-rose-400/10 border-rose-400/30'
              },
            ].map((feature, idx) => {
              const Icon = feature.icon;
              return (
                <div 
                  key={idx}
                  className="p-6 rounded-2xl bg-dark-900 border border-dark-750 space-y-3 shadow-card"
                >
                  <div className={`w-10 h-10 rounded-xl border flex items-center justify-center ${feature.badgeColor}`}>
                    <Icon className="w-5 h-5" />
                  </div>
                  <h4 className="font-bold text-white text-base">{feature.title}</h4>
                  <p className="text-xs text-slate-400 font-normal leading-relaxed">{feature.desc}</p>
                </div>
              );
            })}
          </div>
        </div>
      </section>

    </div>
  );
};

export default LandingPage;
