import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, useScroll, useTransform } from 'framer-motion';
import { 
  ArrowRight, 
  Wind, 
  Droplet, 
  Zap, 
  Sparkles,
  ShieldCheck,
  CheckCircle2,
  Wrench
} from 'lucide-react';
import { servicesApi } from '../api/services';
import { Service, ServiceCategory, UserRole } from '../types';
import { useAuthStore } from '../store/useAuthStore';

export const LandingPage: React.FC = () => {
  const navigate = useNavigate();
  const [categories, setCategories] = useState<ServiceCategory[]>([]);
  const [featuredServices, setFeaturedServices] = useState<Service[]>([]);
  const { getEffectiveRole } = useAuthStore();
  const role = getEffectiveRole();
  const { scrollYProgress } = useScroll();

  const yBg = useTransform(scrollYProgress, [0, 1], ['0%', '20%']);
  const yHeroText = useTransform(scrollYProgress, [0, 1], ['0%', '50%']);

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
      transition: { staggerChildren: 0.1, delayChildren: 0.2 }
    }
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 30 },
    visible: { opacity: 1, y: 0, transition: { duration: 0.8, ease: [0.16, 1, 0.3, 1] } }
  };

  return (
    <div className="bg-dark-950 text-white min-h-screen overflow-hidden selection:bg-sage-500 selection:text-white font-sans">
      
      {/* ──────────────────────────────────────────────────────────────────────────
          1. HERO SECTION
      ────────────────────────────────────────────────────────────────────────── */}
      <section className="relative min-h-[90vh] flex items-center pt-24 pb-12">
        {/* Massive Background Text */}
        <motion.div 
          style={{ y: yBg }}
          className="absolute inset-0 flex items-center justify-center pointer-events-none select-none z-0 overflow-hidden"
        >
          <h1 className="text-[25vw] font-black text-white/5 tracking-tighter leading-none whitespace-nowrap opacity-40">
            HOMIQ
          </h1>
        </motion.div>

        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 w-full relative z-10">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 lg:gap-8 items-center">
            
            {/* Left: Text & CTA */}
            <motion.div 
              style={{ y: yHeroText }}
              initial="hidden"
              animate="visible"
              variants={containerVariants}
              className="space-y-8 order-2 lg:order-1 pt-12 lg:pt-32"
            >
              <motion.div variants={itemVariants} className="flex items-center gap-3">
                <div className="w-2.5 h-2.5 rounded-full bg-sage-500 animate-pulse shadow-[0_0_10px_rgba(217,56,30,0.8)]" />
                <span className="text-xs font-bold tracking-[0.2em] text-white uppercase">
                  GEAR UP. DIG IN. BUILD FORWARD.
                </span>
              </motion.div>

              <motion.h2 variants={itemVariants} className="text-5xl sm:text-6xl lg:text-7xl font-extrabold tracking-tight leading-[1.05] text-white">
                Designing and<br />
                maintaining<br />
                the backbone of<br />
                Smart Homes.
              </motion.h2>

              <motion.div variants={itemVariants} className="pt-6">
                <button
                  onClick={() => navigate(role === UserRole.TECHNICIAN ? '/provider/dashboard' : '/booking/new')}
                  className="bg-sage-500 hover:bg-sage-400 text-white px-8 py-4 font-bold tracking-wide transition-all hover:scale-105 active:scale-95 shadow-[0_0_30px_-5px_rgba(217,56,30,0.4)]"
                >
                  {role === UserRole.TECHNICIAN ? 'Go to Dashboard' : 'Book Maintenance'}
                </button>
              </motion.div>
            </motion.div>

            {/* Right: Floating 3D Render */}
            <motion.div 
              initial={{ opacity: 0, x: 100, rotateY: -15 }}
              animate={{ opacity: 1, x: 0, rotateY: 0 }}
              transition={{ duration: 1.5, ease: "easeOut" }}
              className="order-1 lg:order-2 flex justify-center lg:justify-end relative"
            >
              <motion.img 
                animate={{ y: [0, -20, 0] }}
                transition={{ repeat: Infinity, duration: 6, ease: "easeInOut" }}
                src="/assets/hero_ac.jpg" 
                alt="Industrial HVAC Unit" 
                className="w-full max-w-[600px] object-contain drop-shadow-2xl mix-blend-screen mix-blend-lighten pointer-events-none filter contrast-125"
                style={{ filter: "drop-shadow(0 0 50px rgba(217,56,30,0.15))" }}
              />
            </motion.div>
          </div>
        </div>
      </section>

      {/* ──────────────────────────────────────────────────────────────────────────
          2. FEATURED SERVICE (Plumbing / Infrastructure)
      ────────────────────────────────────────────────────────────────────────── */}
      <section className="py-24 bg-dark-900 border-t border-white/5 overflow-hidden">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-16 items-center">
            
            {/* Left: 3D Render */}
            <motion.div 
              initial={{ opacity: 0, x: -100 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true, margin: "-100px" }}
              transition={{ duration: 1.2, ease: "easeOut" }}
            >
              <motion.img 
                whileHover={{ scale: 1.05, rotateZ: 2 }}
                transition={{ duration: 0.5 }}
                src="/assets/service_plumbing.jpg" 
                alt="Plumbing Infrastructure" 
                className="w-full max-w-[650px] object-cover rounded-xl shadow-[0_20px_50px_-10px_rgba(0,0,0,0.8)] border border-white/5 filter contrast-110"
              />
            </motion.div>

            {/* Right: Text Details */}
            <motion.div 
              initial="hidden"
              whileInView="visible"
              viewport={{ once: true, margin: "-100px" }}
              variants={containerVariants}
              className="space-y-6"
            >
              <motion.div variants={itemVariants} className="flex items-center gap-3">
                <div className="w-2.5 h-2.5 rounded-full bg-sage-500 animate-pulse shadow-[0_0_10px_rgba(217,56,30,0.8)]" />
                <span className="text-[11px] font-bold tracking-[0.25em] text-white uppercase">
                  OUR SERVICES
                </span>
              </motion.div>

              <motion.h2 variants={itemVariants} className="text-4xl lg:text-5xl font-extrabold tracking-tight text-white">
                Core Infrastructure
              </motion.h2>

              <motion.p variants={itemVariants} className="text-lg text-slate-400 font-light leading-relaxed max-w-lg">
                HomiQ's plumbing and electrical services are perfect for urban construction, major renovations, and tight-access diagnostics. Reliable, flexible, and heavily engineered for maximum durability.
              </motion.p>

              <motion.div variants={itemVariants} className="pt-4">
                <button 
                  onClick={() => navigate('/services')}
                  className="bg-sage-500 hover:bg-sage-400 text-white px-8 py-3 font-bold transition-all shadow-[0_0_20px_-5px_rgba(217,56,30,0.5)]"
                >
                  View Catalog
                </button>
              </motion.div>
            </motion.div>

          </div>
        </div>
      </section>

      {/* ──────────────────────────────────────────────────────────────────────────
          3. FULL CATALOG GRID
      ────────────────────────────────────────────────────────────────────────── */}
      <section className="py-24 bg-dark-950">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          
          <div className="mb-16">
            <h3 className="text-3xl font-extrabold tracking-tight">Full Capabilities</h3>
            <p className="text-slate-400 mt-2 font-light">Every job executed by background-verified specialists.</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[
              { title: 'Plumbing', icon: Droplet, desc: 'Heavy-duty pipe maintenance, leakage diagnostics, and hydro-jetting.' },
              { title: 'Electrical', icon: Zap, desc: 'Core wiring, smart panel upgrades, and high-voltage repairs.' },
              { title: 'AC & Climate', icon: Wind, desc: 'Industrial HVAC cleaning, gas refill, and smart thermostat integration.' },
              { title: 'Deep Sanitization', icon: Sparkles, desc: 'Abrasive surface cleaning, chemical treatments, and bio-wash.' },
              { title: 'Structural Repair', icon: Wrench, desc: 'Concrete diagnostics, core drilling, and wall restorations.' },
              { title: 'Security Audits', icon: ShieldCheck, desc: 'Smart lock installation, perimeter cameras, and network defense.' },
            ].map((item, idx) => (
              <motion.div
                key={idx}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: idx * 0.1, duration: 0.5 }}
                whileHover={{ y: -5, backgroundColor: 'rgba(217, 56, 30, 0.05)' }}
                onClick={() => navigate(role === UserRole.TECHNICIAN ? '/provider/dashboard' : '/booking/new')}
                className="group p-8 bg-dark-900 border border-white/5 hover:border-sage-500/50 cursor-pointer transition-all duration-300 relative overflow-hidden"
              >
                <div className="absolute top-0 right-0 w-32 h-32 bg-sage-500/10 rounded-full blur-3xl opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
                <div className="w-12 h-12 bg-dark-950 border border-white/10 group-hover:border-sage-500/50 flex items-center justify-center text-slate-400 group-hover:text-sage-500 mb-6 transition-colors">
                  <item.icon className="w-6 h-6" />
                </div>
                <h4 className="text-xl font-bold text-white mb-3">{item.title}</h4>
                <p className="text-slate-400 text-sm font-light leading-relaxed">{item.desc}</p>
                
                <div className="mt-8 flex items-center gap-2 text-sage-500 font-bold text-xs uppercase tracking-widest opacity-0 group-hover:opacity-100 transition-all transform translate-y-2 group-hover:translate-y-0">
                  <span>Deploy</span>
                  <ArrowRight className="w-4 h-4" />
                </div>
              </motion.div>
            ))}
          </div>

        </div>
      </section>

      {/* ──────────────────────────────────────────────────────────────────────────
          4. TRUST & SECURITY BANNER
      ────────────────────────────────────────────────────────────────────────── */}
      <section className="py-24 border-t border-white/5 relative overflow-hidden bg-dark-900">
        <div className="absolute inset-0 opacity-20 bg-[url('https://www.transparenttextures.com/patterns/carbon-fibre.png')]" />
        
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10 text-center">
          <motion.div 
            initial={{ opacity: 0, scale: 0.9 }}
            whileInView={{ opacity: 1, scale: 1 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6 }}
            className="inline-flex items-center gap-3 px-6 py-3 bg-dark-950 border border-sage-500/30 rounded-full shadow-[0_0_30px_rgba(217,56,30,0.15)] mb-8"
          >
            <ShieldCheck className="w-5 h-5 text-sage-500" />
            <span className="font-bold tracking-widest text-white text-sm">SECURE PLATFORM GUARANTEE</span>
          </motion.div>

          <h2 className="text-3xl md:text-5xl font-extrabold tracking-tight mb-12">Built for Absolute Reliability</h2>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 text-left max-w-4xl mx-auto">
            {[
              { title: '100% Verified Fleet', desc: 'Every technician passes exhaustive background checks and skill audits before deployment.' },
              { title: 'Zero Fraud Execution', desc: 'Secure OTP handshakes and strict Before/After photographic evidence policies.' },
              { title: 'Insured Workmanship', desc: '30-day transparent warranty on all major service installations and repairs.' },
            ].map((feature, idx) => (
              <motion.div 
                key={idx}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: idx * 0.15, duration: 0.5 }}
                className="space-y-3"
              >
                <div className="flex items-center gap-2 text-sage-500">
                  <CheckCircle2 className="w-5 h-5" />
                  <h4 className="font-bold text-white">{feature.title}</h4>
                </div>
                <p className="text-sm text-slate-400 font-light leading-relaxed pl-7">{feature.desc}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

    </div>
  );
};

export default LandingPage;
