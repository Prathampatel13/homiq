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
import { ServiceEmblem } from '../components/brand/ServiceEmblem';

// Refined, human-centered service data with modern brand emblems
const HERO_SERVICES = [
  {
    id: 'ac',
    name: 'AC & Cooling',
    subtitle: 'Installation, servicing & cooling repairs',
    category: 'CLIMATE',
    price: '₹499',
    eta: '18 mins',
    rating: '4.98',
    specs: ['Deep Coil Cleaning', 'Gas Leak & Pressure Check', 'Thermostat Diagnostics'],
    accentColor: '#16A34A',
    accentClass: 'text-sage-600 border-sage-200 bg-sage-50',
  },
  {
    id: 'electrical',
    name: 'Electrical & Wiring',
    subtitle: 'Power fixtures, circuit repairs & MCB',
    category: 'ELECTRICAL',
    price: '₹199',
    eta: '15 mins',
    rating: '4.99',
    specs: ['Circuit Diagnostics', 'Smart MCB Upgrade', 'Appliance & Switch Install'],
    accentColor: '#D97706',
    accentClass: 'text-amber-700 border-amber-200 bg-amber-50',
  },
  {
    id: 'plumbing',
    name: 'Plumbing & Pipes',
    subtitle: 'Leak detection, taps & drainage solutions',
    category: 'PLUMBING',
    price: '₹299',
    eta: '22 mins',
    rating: '4.96',
    specs: ['Acoustic Leak Inspection', 'High-Pressure Valve Care', 'Drainage Clearance'],
    accentColor: '#0284C7',
    accentClass: 'text-sky-700 border-sky-200 bg-sky-50',
  },
  {
    id: 'security',
    name: 'Smart Security',
    subtitle: 'Smart locks, surveillance & sensors',
    category: 'SECURITY',
    price: '₹599',
    eta: '25 mins',
    rating: '4.99',
    specs: ['Smart Lock Calibration', 'CCTV Mesh Setup', 'Hub & Sensor Sync'],
    accentColor: '#E11D48',
    accentClass: 'text-rose-700 border-rose-200 bg-rose-50',
  },
  {
    id: 'cleaning',
    name: 'Deep Cleaning',
    subtitle: 'Full home, kitchen & bathroom care',
    category: 'SANITIZATION',
    price: '₹999',
    eta: '30 mins',
    rating: '4.95',
    specs: ['Hospital-Grade Sanitization', 'Kitchen Degreasing', 'Upholstery & Fabric Care'],
    accentColor: '#059669',
    accentClass: 'text-emerald-700 border-emerald-200 bg-emerald-50',
  },
  {
    id: 'carpentry',
    name: 'Carpentry & Repairs',
    subtitle: 'Door fitting, hardware & structural care',
    category: 'CARPENTRY',
    price: '₹349',
    eta: '20 mins',
    rating: '4.97',
    specs: ['Door Alignment & Locks', 'Custom Shelving', 'Hardware Reinforcement'],
    accentColor: '#C2410C',
    accentClass: 'text-orange-700 border-orange-200 bg-orange-50',
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
    <div className="bg-[#F8FAFC] text-slate-900 min-h-screen overflow-hidden selection:bg-sage-500 selection:text-white font-sans">
      
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
              <motion.div variants={itemVariants} className="inline-flex items-center gap-2.5 px-3.5 py-1.5 rounded-full bg-white border border-slate-200 shadow-subtle">
                <span className="w-2 h-2 rounded-full bg-sage-500 animate-pulse" />
                <span className="text-xs font-semibold tracking-wider text-slate-700 uppercase">
                  VERIFIED RESIDENTIAL CARE
                </span>
              </motion.div>

              {/* Minimal Editorial Headline */}
              <motion.h1 variants={itemVariants} className="text-4xl sm:text-6xl font-bold tracking-tight leading-[1.08] text-slate-900">
                Professional home care,<br />
                <span className="text-transparent bg-clip-text bg-gradient-to-r from-slate-900 via-slate-800 to-sage-600">
                  beautifully delivered.
                </span>
              </motion.h1>

              {/* Clean Subtitle */}
              <motion.p variants={itemVariants} className="text-base text-slate-600 font-normal leading-relaxed max-w-lg">
                Connect with background-verified specialists for AC, electrical, plumbing, smart security, and repairs. Transparent pricing, fast dispatch, and guaranteed quality.
              </motion.p>

              {/* Direct Actions */}
              <motion.div variants={itemVariants} className="flex flex-wrap items-center gap-3.5 pt-2">
                <button
                  onClick={() => navigate('/booking/new')}
                  className="px-7 py-3.5 bg-sage-500 hover:bg-sage-600 text-white font-bold text-sm rounded-xl transition-all duration-200 shadow-subtle hover:shadow-accent flex items-center gap-2.5 active:scale-98"
                >
                  <span>Book a Service</span>
                  <ArrowRight className="w-4 h-4" />
                </button>

                <button
                  onClick={() => navigate('/services')}
                  className="px-6 py-3.5 bg-white hover:bg-slate-50 text-slate-700 hover:text-slate-900 border border-slate-200 hover:border-slate-300 rounded-xl text-sm font-medium transition-all flex items-center gap-2 shadow-sm"
                >
                  <span>Explore Catalog</span>
                  <ChevronRight className="w-4 h-4 text-slate-400" />
                </button>
              </motion.div>

              {/* Key Trust Stats */}
              <motion.div variants={itemVariants} className="pt-6 border-t border-slate-200 grid grid-cols-3 gap-6 max-w-md">
                <div>
                  <span className="text-2xl font-bold text-slate-900 block">15 min</span>
                  <span className="text-xs text-slate-500 font-medium">Avg. Arrival</span>
                </div>
                <div>
                  <span className="text-2xl font-bold text-slate-900 block">100%</span>
                  <span className="text-xs text-slate-500 font-medium">Verified Pros</span>
                </div>
                <div>
                  <span className="text-2xl font-bold text-slate-900 block">4.9★</span>
                  <span className="text-xs text-slate-500 font-medium">Customer Rating</span>
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
                <div className="absolute inset-0 rounded-3xl border border-slate-200/80 bg-white/90 backdrop-blur-md shadow-card" />
                <div className="absolute inset-2 rounded-2xl border border-slate-100 pointer-events-none" />

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
                    <motion.div 
                      animate={{ y: [0, -8, 0] }}
                      transition={{ repeat: Infinity, duration: 5, ease: "easeInOut" }}
                      className="select-none flex items-center justify-center"
                    >
                      <ServiceEmblem category={activeService.id} size="hero" />
                    </motion.div>
                  </motion.div>
                </AnimatePresence>

                {/* Minimal Overlay Preview Pill (Bottom Center) */}
                <motion.div 
                  key={`pill-${activeService.id}`}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.2 }}
                  className="absolute bottom-4 inset-x-4 bg-white/95 backdrop-blur-md border border-slate-200 p-3.5 rounded-2xl shadow-card flex items-center justify-between z-20"
                >
                  <div className="flex items-center gap-3">
                    <ServiceEmblem category={activeService.id} size="sm" />
                    <div>
                      <h4 className="text-sm font-semibold text-slate-900 leading-tight">{activeService.name}</h4>
                      <p className="text-xs text-slate-500 mt-0.5">{activeService.subtitle}</p>
                    </div>
                  </div>

                  <div className="text-right shrink-0 pl-3 border-l border-slate-200">
                    <span className="text-sm font-bold text-sage-600 block">{activeService.price}</span>
                    <span className="text-[11px] text-slate-500">Starting price</span>
                  </div>
                </motion.div>

              </div>
            </motion.div>

          </div>

          {/* ──────────────────────────────────────────────────────────────────────────
              INTERACTIVE SERVICE DOCK
          ────────────────────────────────────────────────────────────────────────── */}
          <div className="mt-14 pt-8 border-t border-slate-200">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-sage-500" />
                <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-700">
                  Select a Service to Preview
                </h3>
              </div>
              <span className="text-xs text-slate-500">6 Core Categories</span>
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
                        ? 'bg-white border-sage-500 shadow-card ring-2 ring-sage-500/20' 
                        : 'bg-white/80 hover:bg-white border-slate-200 hover:border-slate-300 shadow-sm'
                    }`}
                  >
                    <div className="flex items-center justify-between mb-2.5 w-full">
                      <div className="rounded-xl overflow-hidden">
                        <ServiceEmblem category={srv.id} size="xs" />
                      </div>
                      
                      <span className={`w-2 h-2 rounded-full transition-all ${
                        isSelected ? 'bg-sage-500' : 'bg-slate-200'
                      }`} />
                    </div>

                    <div>
                      <h4 className={`text-xs font-semibold leading-tight ${
                        isSelected ? 'text-slate-900 font-bold' : 'text-slate-700'
                      }`}>
                        {srv.name}
                      </h4>
                      <div className="flex items-center justify-between mt-2 pt-1.5 border-t border-slate-100 text-[11px]">
                        <span className="font-bold text-sage-600">{srv.price}</span>
                        <span className="text-slate-500">{srv.eta}</span>
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
      <section className="py-20 bg-white/60 border-t border-slate-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          
          <div className="text-center max-w-2xl mx-auto mb-14 space-y-2">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white border border-slate-200 shadow-subtle mb-2">
              <Sparkles className="w-3.5 h-3.5 text-sage-600" />
              <span className="text-xs font-semibold tracking-wider text-slate-700 uppercase">SIMPLIFIED WORKFLOW</span>
            </div>
            <h2 className="text-3xl font-bold tracking-tight text-slate-900">
              How HomiQ Works
            </h2>
            <p className="text-sm text-slate-600">
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
                tagColor: 'text-sage-700 bg-sage-50 border-sage-200'
              },
              {
                step: '02',
                title: 'Verified Specialist Arrives',
                desc: 'Track arrival in real time. A secure 6-digit PIN ensures only your authorized technician initiates the job.',
                icon: ShieldCheck,
                tagColor: 'text-amber-800 bg-amber-50 border-amber-200'
              },
              {
                step: '03',
                title: 'Inspect & Pay with Guarantee',
                desc: 'Review Before & After photographic evidence before you authorize payment. Backed by our 30-day warranty.',
                icon: CheckCircle2,
                tagColor: 'text-rose-700 bg-rose-50 border-rose-200'
              }
            ].map((card, i) => {
              const Icon = card.icon;
              return (
                <div 
                  key={i} 
                  className="p-7 rounded-3xl bg-white border border-slate-200 shadow-card flex flex-col justify-between hover:border-slate-300 transition-all duration-200"
                >
                  <div className="space-y-4">
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-mono font-bold text-slate-400 tracking-wider">STEP {card.step}</span>
                      <div className={`w-9 h-9 rounded-xl border flex items-center justify-center ${card.tagColor}`}>
                        <Icon className="w-4 h-4" />
                      </div>
                    </div>
                    <h3 className="text-lg font-bold text-slate-900">{card.title}</h3>
                    <p className="text-xs text-slate-600 leading-relaxed font-normal">{card.desc}</p>
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
      <section className="py-20 border-t border-slate-200 bg-[#F8FAFC]">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          
          <div className="flex flex-col md:flex-row md:items-end justify-between mb-12 gap-4">
            <div>
              <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white border border-slate-200 shadow-subtle mb-2">
                <Layers className="w-3.5 h-3.5 text-sage-600" />
                <span className="text-xs font-semibold tracking-wider text-slate-700 uppercase">POPULAR CATEGORIES</span>
              </div>
              <h3 className="text-3xl font-bold tracking-tight text-slate-900">
                Services Built for Every Need
              </h3>
              <p className="text-slate-600 text-sm mt-1 max-w-xl">
                Fixed pricing with zero hidden fees. Certified technicians deployed to your location.
              </p>
            </div>

            <button
              onClick={() => navigate('/services')}
              className="px-5 py-2.5 bg-white hover:bg-slate-50 text-xs font-semibold uppercase tracking-wider text-slate-700 hover:text-slate-900 border border-slate-200 hover:border-slate-300 rounded-xl transition-all shadow-sm self-start md:self-auto flex items-center gap-2"
            >
              <span>View Full Catalog</span>
              <ArrowRight className="w-3.5 h-3.5 text-slate-500" />
            </button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {HERO_SERVICES.map((srv) => (
              <div
                key={srv.id}
                onClick={() => navigate('/booking/new')}
                className="p-6 bg-white rounded-3xl border border-slate-200 hover:border-sage-400/60 cursor-pointer transition-all duration-200 relative overflow-hidden shadow-card group"
              >
                {/* Header: Icon & Price */}
                <div className="flex items-center justify-between mb-5">
                  <div className="rounded-2xl overflow-hidden">
                    <ServiceEmblem category={srv.id} size="sm" />
                  </div>
                  <div className="text-right">
                    <span className="text-base font-bold text-slate-900 block">{srv.price}</span>
                    <span className="text-[11px] text-slate-500">{srv.eta} arrival</span>
                  </div>
                </div>

                <h4 className="text-lg font-bold text-slate-900 mb-1 group-hover:text-sage-600 transition-colors">
                  {srv.name}
                </h4>
                <p className="text-slate-600 text-xs leading-relaxed mb-5">{srv.subtitle}</p>
                
                {/* Service Specs */}
                <div className="space-y-2 pt-4 border-t border-slate-100 text-xs text-slate-600">
                  {srv.specs.map((sp, idx) => (
                    <div key={idx} className="flex items-center gap-2">
                      <span className="w-1.5 h-1.5 rounded-full bg-sage-500" />
                      <span>{sp}</span>
                    </div>
                  ))}
                </div>

                {/* Card CTA */}
                <div className="mt-5 flex items-center justify-between pt-3.5 border-t border-slate-100 text-xs font-semibold text-slate-700 group-hover:text-sage-600 transition-colors">
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
      <section className="py-20 border-t border-slate-200 bg-slate-50/70">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          
          <div className="inline-flex items-center gap-2.5 px-4 py-1.5 bg-white border border-slate-200 shadow-subtle rounded-full mb-6">
            <ShieldCheck className="w-4 h-4 text-sage-600" />
            <span className="text-xs font-semibold tracking-wider text-slate-800 uppercase">
              THE HOMIQ STANDARD
            </span>
          </div>

          <h2 className="text-3xl sm:text-4xl font-bold tracking-tight text-slate-900 mb-3">
            Peace of Mind on Every Visit
          </h2>
          <p className="text-slate-600 text-sm max-w-lg mx-auto mb-12">
            We hold all home care to rigorous quality and safety benchmarks.
          </p>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 text-left max-w-4xl mx-auto">
            {[
              { 
                icon: ShieldCheck,
                title: 'Vetted Specialists', 
                desc: 'Technicians undergo comprehensive background verification, trade screening, and continuous customer reviews.',
                badgeColor: 'text-sage-700 bg-sage-50 border-sage-200'
              },
              { 
                icon: Camera,
                title: 'Photo Proof of Work', 
                desc: 'Mandatory Before & After photographic documentation gives you full transparency before authorizing payment.',
                badgeColor: 'text-amber-800 bg-amber-50 border-amber-200'
              },
              { 
                icon: Lock,
                title: '30-Day Guarantee', 
                desc: 'Complete workmanship guarantee on repairs and installations. If something isn’t right, we re-service at no charge.',
                badgeColor: 'text-rose-700 bg-rose-50 border-rose-200'
              },
            ].map((feature, idx) => {
              const Icon = feature.icon;
              return (
                <div 
                  key={idx}
                  className="p-6 rounded-2xl bg-white border border-slate-200 space-y-3 shadow-card hover:border-slate-300 transition-all"
                >
                  <div className={`w-10 h-10 rounded-xl border flex items-center justify-center ${feature.badgeColor}`}>
                    <Icon className="w-5 h-5" />
                  </div>
                  <h4 className="font-bold text-slate-900 text-base">{feature.title}</h4>
                  <p className="text-xs text-slate-600 font-normal leading-relaxed">{feature.desc}</p>
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
