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
  Cpu
} from 'lucide-react';
import { servicesApi } from '../api/services';
import { Service, ServiceCategory, UserRole } from '../types';
import { useAuthStore } from '../store/useAuthStore';

// All Services Data with Dedicated 3D Logo Badges and Technical Specifications
const HERO_SERVICES = [
  {
    id: 'ac',
    tradeCode: 'HVAC-004',
    name: 'AC & Climate',
    subtitle: 'Industrial Chillers & Smart Thermostats',
    tag: 'CLIMATE ARCHITECTURE',
    iconImg: '/assets/services/ac.jpg',
    heroImg: '/assets/hero_ac.jpg',
    price: '₹499',
    eta: '18 mins',
    rating: '4.98',
    specs: ['Freon Leak Telemetry', 'Coil Anti-Corrosion Bio-Wash', 'Smart Inverter Diagnostics'],
    accentColor: '#D9381E',
  },
  {
    id: 'electrical',
    tradeCode: 'GRID-X',
    name: 'Electrical Core',
    subtitle: 'Power Grid, High-Voltage & MCB',
    tag: 'POWER INFRASTRUCTURE',
    iconImg: '/assets/services/electrical.jpg',
    heroImg: '/assets/services/electrical.jpg',
    price: '₹199',
    eta: '15 mins',
    rating: '4.99',
    specs: ['Short-Circuit Infrared Scan', 'Smart MCB Upgrade', 'Load Balancing & Earthing'],
    accentColor: '#FF6B4A',
  },
  {
    id: 'plumbing',
    tradeCode: 'HYDRA-750',
    name: 'Hydraulics & Pipes',
    subtitle: 'High-Pressure Valves & Line Diagnostics',
    tag: 'HYDRAULIC ENGINEERING',
    iconImg: '/assets/services/plumbing.jpg',
    heroImg: '/assets/service_plumbing.jpg',
    price: '₹299',
    eta: '22 mins',
    rating: '4.96',
    specs: ['Acoustic Leak Detection', 'Pressure Regulator Overhaul', 'Heavy-Duty Hydro-Jetting'],
    accentColor: '#D9381E',
  },
  {
    id: 'security',
    tradeCode: 'SECURAX-9',
    name: 'Smart Security',
    subtitle: 'Biometric Access & Perimeter Defense',
    tag: 'ACCESS & DEFENSE',
    iconImg: '/assets/services/security.jpg',
    heroImg: '/assets/services/security.jpg',
    price: '₹599',
    eta: '25 mins',
    rating: '4.99',
    specs: ['Biometric Lock Calibration', 'Encrypted AI Camera Mesh', 'Zero-Trust Hub Setup'],
    accentColor: '#FF5722',
  },
  {
    id: 'cleaning',
    tradeCode: 'BIO-SAN',
    name: 'Deep Sanitization',
    subtitle: 'UV-C Sterilization & Surface Restoration',
    tag: 'BIO-PURIFICATION',
    iconImg: '/assets/services/cleaning.jpg',
    heroImg: '/assets/services/cleaning.jpg',
    price: '₹999',
    eta: '30 mins',
    rating: '4.95',
    specs: ['Hospital-Grade UV-C Pods', 'Enzymatic Chemical Wash', 'HEPA Filtration Treatment'],
    accentColor: '#D9381E',
  },
  {
    id: 'carpentry',
    tradeCode: 'TITAN-PRO',
    name: 'Structural Repair',
    subtitle: 'Precision Mechanical & Framing Care',
    tag: 'HEAVY MECHANICAL',
    iconImg: '/assets/services/carpentry.jpg',
    heroImg: '/assets/services/carpentry.jpg',
    price: '₹349',
    eta: '20 mins',
    rating: '4.97',
    specs: ['Laser Axis Framing Alignment', 'Reinforced Heavy Hardware', 'Damp-Proof Barrier Prep'],
    accentColor: '#FF6B4A',
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
    <div className="bg-dark-950 text-white min-h-screen overflow-hidden selection:bg-sage-500 selection:text-white font-sans">
      
      {/* ──────────────────────────────────────────────────────────────────────────
          1. HERO SECTION: EKVATOR INDUSTRIAL AESTHETIC & SERVICE LOGOS
      ────────────────────────────────────────────────────────────────────────── */}
      <section className="relative min-h-screen flex flex-col justify-between pt-24 pb-16 overflow-hidden">
        
        {/* Massive Background Industrial Typographic Watermark */}
        <motion.div 
          style={{ y: yBg }}
          className="absolute inset-0 flex items-center justify-center pointer-events-none select-none z-0 overflow-hidden"
        >
          <h1 className="text-[26vw] font-black text-white/[0.035] tracking-tighter leading-none whitespace-nowrap opacity-50">
            HOMIQ
          </h1>
        </motion.div>

        {/* Ambient Subtle Flame Glow Blobs */}
        <div className="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[700px] h-[500px] bg-sage-500/10 rounded-full blur-[140px] pointer-events-none" />
        <div className="absolute top-1/3 right-10 w-[450px] h-[450px] bg-sage-600/10 rounded-full blur-[120px] pointer-events-none" />

        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 w-full relative z-10 pt-4">
          
          {/* Top Hero Grid: Headline vs 3D Centerpiece */}
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-10 lg:gap-6 items-center min-h-[500px]">
            
            {/* Left Column: Editorial & Value Proposition */}
            <motion.div 
              initial="hidden"
              animate="visible"
              variants={containerVariants}
              className="lg:col-span-6 space-y-7"
            >
              {/* Status Pill Badge */}
              <motion.div variants={itemVariants} className="inline-flex items-center gap-2.5 px-3.5 py-1.5 rounded-full bg-dark-900 border border-white/10 shadow-subtle">
                <span className="w-2 h-2 rounded-full bg-sage-500 animate-pulse shadow-[0_0_10px_rgba(217,56,30,0.9)]" />
                <span className="text-[11px] font-mono font-bold tracking-[0.25em] text-white uppercase">
                  GEAR UP. DIG IN. BUILD FORWARD.
                </span>
              </motion.div>

              {/* Bold Editorial Headline */}
              <motion.h1 variants={itemVariants} className="text-4xl sm:text-6xl lg:text-6xl font-black tracking-tight leading-[1.04] text-white">
                Designing and<br />
                maintaining the<br />
                backbone of<br />
                <span className="text-transparent bg-clip-text bg-gradient-to-r from-white via-slate-200 to-sage-400">
                  Smart Homes.
                </span>
              </motion.h1>

              {/* Description */}
              <motion.p variants={itemVariants} className="text-sm sm:text-base text-slate-400 font-normal leading-relaxed max-w-lg">
                HomiQ engineers heavy-duty residential care. Autonomous dispatch of background-verified master technicians with OTP verification, live telemetry, and photographic evidence.
              </motion.p>

              {/* CTAs */}
              <motion.div variants={itemVariants} className="flex flex-wrap items-center gap-4 pt-2">
                <button
                  onClick={() => navigate(role === UserRole.TECHNICIAN ? '/provider/dashboard' : '/booking/new')}
                  className="px-8 py-4 bg-sage-500 hover:bg-sage-400 text-white font-bold text-sm tracking-wide rounded-xl transition-all duration-300 shadow-[0_0_35px_-5px_rgba(217,56,30,0.5)] hover:shadow-[0_0_45px_rgba(217,56,30,0.8)] flex items-center gap-3 group active:scale-95"
                >
                  <span>{role === UserRole.TECHNICIAN ? 'Go To Command Center' : 'Get Fast Quote'}</span>
                  <ArrowRight className="w-4 h-4 transition-transform group-hover:translate-x-1.5" />
                </button>

                <button
                  onClick={() => navigate('/services')}
                  className="px-6 py-4 bg-dark-900/90 hover:bg-dark-850 text-slate-300 hover:text-white border border-white/10 hover:border-sage-500/40 rounded-xl text-sm font-semibold transition-all flex items-center gap-2"
                >
                  <span>Browse Full Fleet</span>
                  <ChevronRight className="w-4 h-4 text-slate-500" />
                </button>
              </motion.div>

              {/* Trust Indicators */}
              <motion.div variants={itemVariants} className="pt-4 border-t border-white/5 grid grid-cols-3 gap-6 max-w-md">
                <div>
                  <span className="text-xl font-mono font-black text-white block">15 MIN</span>
                  <span className="text-[11px] text-slate-400 uppercase tracking-wider font-mono">Response</span>
                </div>
                <div>
                  <span className="text-xl font-mono font-black text-white block">100%</span>
                  <span className="text-[11px] text-slate-400 uppercase tracking-wider font-mono">Audit Proof</span>
                </div>
                <div>
                  <span className="text-xl font-mono font-black text-white block">4.98★</span>
                  <span className="text-[11px] text-slate-400 uppercase tracking-wider font-mono">Fleet Rating</span>
                </div>
              </motion.div>
            </motion.div>

            {/* Right Column: 3D Render & Interactive Telemetry HUD */}
            <motion.div 
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 1, ease: [0.16, 1, 0.3, 1] }}
              className="lg:col-span-6 relative flex flex-col items-center justify-center"
            >
              {/* Dynamic 3D Product Showcase */}
              <div className="relative w-full max-w-[560px] aspect-square flex items-center justify-center">
                
                {/* Neon Aura Rings */}
                <div className="absolute inset-0 rounded-full border border-sage-500/20 scale-90 animate-pulse pointer-events-none" />
                <div className="absolute inset-0 rounded-full border border-white/5 scale-105 pointer-events-none" />

                {/* Animated 3D Floating Asset */}
                <AnimatePresence mode="wait">
                  <motion.div
                    key={activeService.id}
                    initial={{ opacity: 0, scale: 0.85, y: 30 }}
                    animate={{ opacity: 1, scale: 1, y: 0 }}
                    exit={{ opacity: 0, scale: 0.9, y: -20 }}
                    transition={{ duration: 0.5, ease: "easeOut" }}
                    className="relative w-full h-full flex items-center justify-center"
                  >
                    <motion.img 
                      animate={{ y: [0, -12, 0] }}
                      transition={{ repeat: Infinity, duration: 5, ease: "easeInOut" }}
                      src={activeService.heroImg} 
                      alt={activeService.name} 
                      className="max-h-[460px] w-auto object-contain rounded-2xl drop-shadow-[0_25px_60px_rgba(0,0,0,0.9)] filter contrast-125 select-none"
                      style={{ filter: "drop-shadow(0 0 45px rgba(217, 56, 30, 0.25))" }}
                    />
                  </motion.div>
                </AnimatePresence>

                {/* Floating Telemetry Glass HUD Card (Top Right) */}
                <motion.div 
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.4 }}
                  className="absolute top-4 right-0 bg-dark-900/90 backdrop-blur-xl border border-white/10 p-3.5 rounded-2xl shadow-modal flex items-center gap-3 z-20"
                >
                  <div className="w-9 h-9 rounded-xl bg-sage-500/20 border border-sage-500/40 flex items-center justify-center text-sage-500">
                    <Activity className="w-4 h-4 animate-pulse" />
                  </div>
                  <div>
                    <div className="flex items-center gap-1.5">
                      <span className="text-[10px] font-mono uppercase text-slate-400">STATUS</span>
                      <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-ping" />
                    </div>
                    <p className="text-xs font-mono font-bold text-white tracking-wide">FLEET DISPATCH READY</p>
                  </div>
                </motion.div>

                {/* Floating Active Spec HUD (Bottom Left) */}
                <motion.div 
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.5 }}
                  className="absolute bottom-6 left-0 bg-dark-900/95 backdrop-blur-xl border border-white/10 p-4 rounded-2xl shadow-modal max-w-[260px] z-20"
                >
                  <div className="flex items-center justify-between mb-1.5">
                    <span className="text-[10px] font-mono text-sage-500 font-bold uppercase tracking-widest">{activeService.tradeCode}</span>
                    <span className="text-xs font-mono font-black text-white">{activeService.price}</span>
                  </div>
                  <h4 className="text-sm font-bold text-white">{activeService.name}</h4>
                  <p className="text-[11px] text-slate-400 mt-1 leading-snug">{activeService.subtitle}</p>
                </motion.div>

              </div>
            </motion.div>

          </div>

          {/* ──────────────────────────────────────────────────────────────────────────
              SERVICE LOGO CAROUSEL / SELECTOR DOCK: "ONE BY ONE ADD SMALL LOGO IMAGES FOR ALL SERVICES"
          ────────────────────────────────────────────────────────────────────────── */}
          <motion.div 
            initial={{ opacity: 0, y: 40 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.3 }}
            className="mt-12 pt-8 border-t border-white/10"
          >
            {/* Subheader */}
            <div className="flex items-center justify-between mb-5">
              <div className="flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-sage-500 animate-pulse" />
                <h3 className="text-xs font-mono font-bold uppercase tracking-[0.25em] text-slate-300">
                  OUR SERVICES • SELECT TO INSPECT & DISPATCH
                </h3>
              </div>
              <span className="hidden sm:inline-block text-[11px] font-mono text-slate-500 uppercase tracking-widest">
                6 SPECIALIZED DIVISIONS
              </span>
            </div>

            {/* Service Logo Cards Grid (One by One) */}
            <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3.5">
              {HERO_SERVICES.map((srv, idx) => {
                const isSelected = activeService.id === srv.id;
                return (
                  <motion.button
                    key={srv.id}
                    onClick={() => setActiveService(srv)}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.1 * idx, duration: 0.5 }}
                    whileHover={{ y: -4, scale: 1.02 }}
                    whileTap={{ scale: 0.97 }}
                    className={`p-3.5 rounded-2xl text-left transition-all duration-200 relative group flex flex-col justify-between border ${
                      isSelected 
                        ? 'bg-dark-900 border-sage-500 shadow-[0_0_25px_rgba(217,56,30,0.35)] ring-1 ring-sage-500' 
                        : 'bg-dark-900/70 hover:bg-dark-900 border-white/5 hover:border-white/20'
                    }`}
                  >
                    {/* Top: 3D Logo Image */}
                    <div className="flex items-center justify-between mb-3 w-full">
                      <div className={`w-12 h-12 rounded-xl overflow-hidden border p-0.5 transition-transform duration-300 group-hover:scale-105 ${
                        isSelected ? 'border-sage-500 shadow-[0_0_15px_rgba(217,56,30,0.5)]' : 'border-white/10 group-hover:border-sage-500/40'
                      }`}>
                        <img 
                          src={srv.iconImg} 
                          alt={srv.name} 
                          className="w-full h-full object-cover rounded-lg"
                        />
                      </div>
                      
                      {/* Active Trade Dot */}
                      <span className={`w-2 h-2 rounded-full transition-all ${
                        isSelected ? 'bg-sage-500 shadow-[0_0_8px_rgba(217,56,30,1)]' : 'bg-dark-750 group-hover:bg-slate-500'
                      }`} />
                    </div>

                    {/* Bottom: Trade Title & Pricing */}
                    <div>
                      <span className="text-[9px] font-mono text-slate-400 block uppercase tracking-wider">{srv.tradeCode}</span>
                      <h4 className={`text-xs font-bold transition-colors leading-tight mt-0.5 ${
                        isSelected ? 'text-white' : 'text-slate-300 group-hover:text-white'
                      }`}>
                        {srv.name}
                      </h4>
                      <div className="flex items-center justify-between mt-2 pt-2 border-t border-white/5">
                        <span className="text-[11px] font-mono font-bold text-sage-400">{srv.price}</span>
                        <span className="text-[10px] font-mono text-slate-500">{srv.eta}</span>
                      </div>
                    </div>
                  </motion.button>
                );
              })}
            </div>
          </motion.div>

        </div>
      </section>

      {/* ──────────────────────────────────────────────────────────────────────────
          2. FEATURED SHOWCASE 1: CORE HYDRAULICS / PLUMBING (EKVATOR EDITORIAL SPLIT)
      ────────────────────────────────────────────────────────────────────────── */}
      <section className="py-24 bg-dark-900 border-t border-white/5 relative overflow-hidden">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 items-center">
            
            {/* Left Column: 3D Heavy Model */}
            <motion.div 
              initial={{ opacity: 0, x: -60 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true, margin: "-80px" }}
              transition={{ duration: 1, ease: [0.16, 1, 0.3, 1] }}
              className="lg:col-span-7 relative group"
            >
              <div className="relative rounded-3xl overflow-hidden border border-white/10 bg-dark-950 p-2 shadow-2xl">
                <img 
                  src="/assets/service_plumbing.jpg" 
                  alt="Plumbing Infrastructure" 
                  className="w-full h-auto object-cover rounded-2xl transition-transform duration-700 group-hover:scale-105 filter contrast-115"
                />
                
                {/* Floating Technical Badge Overlay */}
                <div className="absolute bottom-6 left-6 bg-dark-900/90 backdrop-blur-md border border-white/10 px-4 py-2.5 rounded-xl shadow-modal flex items-center gap-3">
                  <div className="w-2.5 h-2.5 rounded-full bg-sage-500 animate-pulse shadow-[0_0_10px_rgba(217,56,30,0.9)]" />
                  <span className="text-xs font-mono font-bold text-white tracking-widest uppercase">
                    HEX-GRIP 750 HYDRAULIC PRESSURE CORE
                  </span>
                </div>
              </div>
            </motion.div>

            {/* Right Column: Editorial Copy */}
            <motion.div 
              initial={{ opacity: 0, x: 60 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true, margin: "-80px" }}
              transition={{ duration: 1, ease: [0.16, 1, 0.3, 1] }}
              className="lg:col-span-5 space-y-6"
            >
              <div className="flex items-center gap-2.5">
                <div className="w-2.5 h-2.5 rounded-full bg-sage-500 shadow-[0_0_10px_rgba(217,56,30,0.8)]" />
                <span className="text-xs font-mono font-bold tracking-[0.25em] text-white uppercase">
                  OUR PRODUCTS & CAPABILITIES
                </span>
              </div>

              <h2 className="text-4xl sm:text-5xl font-black tracking-tight text-white leading-tight">
                Hydraulic Line & Core Plumbing
              </h2>

              <p className="text-slate-400 text-sm sm:text-base leading-relaxed font-light">
                HomiQ's high-pressure plumbing units are engineered for high-durability residential pipelines, acoustic leak detection, and tight-access diagnostics. Reliable, flexible, and executed with millimeter precision.
              </p>

              <div className="space-y-3 pt-2">
                {['High-Pressure Acoustic Hydro Leak Detection', 'Dual-Phase Check Valves & Backflow Prevention', 'Industrial Stainless Line & Tank Refurbishment'].map((feat, i) => (
                  <div key={i} className="flex items-center gap-3 text-xs font-mono text-slate-300">
                    <CheckCircle2 className="w-4 h-4 text-sage-500 shrink-0" />
                    <span>{feat}</span>
                  </div>
                ))}
              </div>

              <div className="pt-4">
                <button 
                  onClick={() => navigate('/booking/new')}
                  className="px-7 py-3.5 bg-sage-500 hover:bg-sage-400 text-white font-bold text-xs uppercase tracking-widest rounded-xl transition-all shadow-[0_0_25px_-5px_rgba(217,56,30,0.5)] active:scale-95"
                >
                  Get Fast Quote
                </button>
              </div>
            </motion.div>

          </div>
        </div>
      </section>

      {/* ──────────────────────────────────────────────────────────────────────────
          3. FEATURED SHOWCASE 2: HEAVY HVAC (REVERSE SPLIT)
      ────────────────────────────────────────────────────────────────────────── */}
      <section className="py-24 bg-dark-950 border-t border-white/5 relative overflow-hidden">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 items-center">
            
            {/* Left Column: Editorial Copy */}
            <motion.div 
              initial={{ opacity: 0, x: -60 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true, margin: "-80px" }}
              transition={{ duration: 1, ease: [0.16, 1, 0.3, 1] }}
              className="lg:col-span-5 space-y-6 order-2 lg:order-1"
            >
              <div className="flex items-center gap-2.5">
                <div className="w-2.5 h-2.5 rounded-full bg-sage-500 shadow-[0_0_10px_rgba(217,56,30,0.8)]" />
                <span className="text-xs font-mono font-bold tracking-[0.25em] text-white uppercase">
                  CLIMATE CONTROL ARCHITECTURE
                </span>
              </div>

              <h2 className="text-4xl sm:text-5xl font-black tracking-tight text-white leading-tight">
                Heavy HVAC & Chiller Systems
              </h2>

              <p className="text-slate-400 text-sm sm:text-base leading-relaxed font-light">
                Engineered for maximum thermal efficiency in extreme heat environments. Complete circuit diagnostics, anti-bacterial coil sanitization, and automated freon charging with instant proof of performance.
              </p>

              <div className="space-y-3 pt-2">
                {['Sub-Zero Deep Coil Cleansing & Bio-Treatment', 'Digital Compressor Telemetry & Gas Calibration', 'Smart Dual-Inverter PCB Diagnostics'].map((feat, i) => (
                  <div key={i} className="flex items-center gap-3 text-xs font-mono text-slate-300">
                    <CheckCircle2 className="w-4 h-4 text-sage-500 shrink-0" />
                    <span>{feat}</span>
                  </div>
                ))}
              </div>

              <div className="pt-4">
                <button 
                  onClick={() => navigate('/booking/new')}
                  className="px-7 py-3.5 bg-sage-500 hover:bg-sage-400 text-white font-bold text-xs uppercase tracking-widest rounded-xl transition-all shadow-[0_0_25px_-5px_rgba(217,56,30,0.5)] active:scale-95"
                >
                  Get Fast Quote
                </button>
              </div>
            </motion.div>

            {/* Right Column: 3D Heavy Model */}
            <motion.div 
              initial={{ opacity: 0, x: 60 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true, margin: "-80px" }}
              transition={{ duration: 1, ease: [0.16, 1, 0.3, 1] }}
              className="lg:col-span-7 relative group order-1 lg:order-2"
            >
              <div className="relative rounded-3xl overflow-hidden border border-white/10 bg-dark-900 p-6 shadow-2xl flex items-center justify-center min-h-[420px]">
                <img 
                  src="/assets/hero_ac.jpg" 
                  alt="Heavy Industrial HVAC" 
                  className="max-h-[380px] w-auto object-contain transition-transform duration-700 group-hover:scale-105 filter contrast-125 select-none"
                  style={{ filter: "drop-shadow(0 0 35px rgba(217, 56, 30, 0.3))" }}
                />

                <div className="absolute bottom-6 right-6 bg-dark-950/90 backdrop-blur-md border border-white/10 px-4 py-2.5 rounded-xl shadow-modal flex items-center gap-3">
                  <div className="w-2.5 h-2.5 rounded-full bg-sage-500 animate-pulse shadow-[0_0_10px_rgba(217,56,30,0.9)]" />
                  <span className="text-xs font-mono font-bold text-white tracking-widest uppercase">
                    AURONA INDUSTRIAL HVAC 004
                  </span>
                </div>
              </div>
            </motion.div>

          </div>
        </div>
      </section>

      {/* ──────────────────────────────────────────────────────────────────────────
          4. FULL FLEET CAPABILITIES (HIGH-TECH GRID)
      ────────────────────────────────────────────────────────────────────────── */}
      <section className="py-24 bg-dark-900 border-t border-white/5">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          
          <div className="flex flex-col md:flex-row md:items-end justify-between mb-16 gap-4">
            <div>
              <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-dark-850 border border-white/10 mb-3">
                <Layers className="w-3.5 h-3.5 text-sage-500" />
                <span className="text-xs font-mono tracking-wider text-slate-300 uppercase">FULL SPECIFICATION FLEET</span>
              </div>
              <h3 className="text-3xl sm:text-4xl font-black tracking-tight text-white">
                Engineered for Architectural Precision
              </h3>
              <p className="text-slate-400 text-sm mt-2 max-w-xl font-light">
                Transparent component-level pricing. Strict background-checked Master Technicians deployed on every dispatch.
              </p>
            </div>

            <button
              onClick={() => navigate('/services')}
              className="px-5 py-2.5 bg-dark-850 hover:bg-dark-800 text-xs font-mono font-bold uppercase tracking-wider text-slate-300 hover:text-white border border-white/10 rounded-xl transition-all self-start md:self-auto flex items-center gap-2"
            >
              <span>View All Services</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {HERO_SERVICES.map((srv, idx) => (
              <motion.div
                key={srv.id}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: idx * 0.08, duration: 0.5 }}
                whileHover={{ y: -6, backgroundColor: 'rgba(217, 56, 30, 0.04)' }}
                onClick={() => navigate(role === UserRole.TECHNICIAN ? '/provider/dashboard' : '/booking/new')}
                className="group p-8 bg-dark-950 rounded-3xl border border-white/5 hover:border-sage-500/40 cursor-pointer transition-all duration-300 relative overflow-hidden shadow-card"
              >
                {/* Neon Ember Glow on Hover */}
                <div className="absolute top-0 right-0 w-36 h-36 bg-sage-500/15 rounded-full blur-3xl opacity-0 group-hover:opacity-100 transition-opacity duration-500" />

                {/* 3D App Icon Badge */}
                <div className="w-16 h-16 rounded-2xl overflow-hidden border border-white/10 group-hover:border-sage-500/50 mb-6 transition-all duration-300 group-hover:scale-105 p-1 bg-dark-900 shadow-md">
                  <img 
                    src={srv.iconImg} 
                    alt={srv.name} 
                    className="w-full h-full object-cover rounded-xl"
                  />
                </div>

                <div className="flex items-center justify-between mb-2">
                  <span className="text-[10px] font-mono text-sage-500 font-bold uppercase tracking-widest">{srv.tradeCode}</span>
                  <span className="text-sm font-mono font-black text-white">{srv.price}</span>
                </div>

                <h4 className="text-xl font-bold text-white mb-2 group-hover:text-sage-400 transition-colors">{srv.name}</h4>
                <p className="text-slate-400 text-xs font-light leading-relaxed mb-6">{srv.subtitle}</p>
                
                {/* Tech Specs List */}
                <div className="space-y-2 pt-4 border-t border-white/5 text-[11px] font-mono text-slate-400">
                  {srv.specs.slice(0, 2).map((sp, i) => (
                    <div key={i} className="flex items-center gap-2">
                      <span className="w-1 h-1 rounded-full bg-sage-500" />
                      <span>{sp}</span>
                    </div>
                  ))}
                </div>

                {/* Deploy Trigger */}
                <div className="mt-6 flex items-center justify-between pt-4 border-t border-white/5 text-xs font-mono font-bold uppercase tracking-wider text-slate-400 group-hover:text-sage-400 transition-colors">
                  <span>Dispatch Division</span>
                  <ArrowRight className="w-4 h-4 transition-transform group-hover:translate-x-1" />
                </div>
              </motion.div>
            ))}
          </div>

        </div>
      </section>

      {/* ──────────────────────────────────────────────────────────────────────────
          5. PLATFORM AUDIT & SECURITY GUARANTEE
      ────────────────────────────────────────────────────────────────────────── */}
      <section className="py-24 border-t border-white/5 relative overflow-hidden bg-dark-950">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10 text-center">
          
          <motion.div 
            initial={{ opacity: 0, scale: 0.9 }}
            whileInView={{ opacity: 1, scale: 1 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6 }}
            className="inline-flex items-center gap-3 px-5 py-2.5 bg-dark-900 border border-sage-500/30 rounded-full shadow-[0_0_30px_rgba(217,56,30,0.15)] mb-8"
          >
            <ShieldCheck className="w-4 h-4 text-sage-500" />
            <span className="font-mono font-bold tracking-widest text-white text-xs uppercase">
              ZERO FRAUD PROTOCOL & 30-DAY WARRANTY
            </span>
          </motion.div>

          <h2 className="text-3xl md:text-5xl font-black tracking-tight mb-12">
            Engineered for Absolute Reliability.
          </h2>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 text-left max-w-4xl mx-auto">
            {[
              { 
                title: '100% Verified Specialists', 
                desc: 'Every technician undergoes exhaustive background checks, biometric verification, and rigorous technical testing before joining the fleet.' 
              },
              { 
                title: 'Photographic Proof of Work', 
                desc: 'Strict mandatory Before & After image audits are enforced on our ledger before customer checkout is ever authorized.' 
              },
              { 
                title: '30-Day Workmanship Guarantee', 
                desc: 'Full coverage warranty on all installations and component repairs. Hassle-free re-dispatch if anything fails.' 
              },
            ].map((feature, idx) => (
              <motion.div 
                key={idx}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: idx * 0.15, duration: 0.5 }}
                className="p-6 rounded-2xl bg-dark-900 border border-white/5 space-y-3"
              >
                <div className="flex items-center gap-2 text-sage-500">
                  <CheckCircle2 className="w-5 h-5" />
                  <h4 className="font-bold text-white text-base">{feature.title}</h4>
                </div>
                <p className="text-xs text-slate-400 font-light leading-relaxed pl-7">{feature.desc}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

    </div>
  );
};

export default LandingPage;
