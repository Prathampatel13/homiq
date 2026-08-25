import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  ShieldCheck, 
  Sparkles, 
  Wind, 
  Droplet, 
  Zap, 
  Wrench, 
  Clock, 
  CheckCircle2, 
  Lock, 
  ArrowRight, 
  QrCode, 
  Navigation, 
  CreditCard, 
  UserCheck, 
  Briefcase,
  ChevronRight,
  Star,
  Layers,
  MapPin,
  Monitor,
  Paintbrush,
  Bath,
  Home,
  TreePine,
  DoorOpen
} from 'lucide-react';
import { HeroScene3D } from '../components/3d/HeroScene3D';
import { SmartHomeLayeredView } from '../components/3d/SmartHomeLayeredView';
import { HomiQLogo } from '../components/brand/HomiQLogo';
import { servicesApi } from '../api/services';
import { jobsApi } from '../api/jobs';
import { Service, ServiceCategory, JobPost } from '../types';

export const LandingPage: React.FC = () => {
  const navigate = useNavigate();
  const [categories, setCategories] = useState<ServiceCategory[]>([]);
  const [featuredServices, setFeaturedServices] = useState<Service[]>([]);
  const [recentJobs, setRecentJobs] = useState<JobPost[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadHomeData = async () => {
      setLoading(true);
      setTimeout(async () => {
        try {
          // MOCK TO PREVENT 15s HANG
          setCategories([]);
          setFeaturedServices([]);
          setRecentJobs([]);
        } finally {
          setLoading(false);
        }
      }, 100);
    };

    loadHomeData();
  }, []);

  return (
    <div className="min-h-screen bg-dark-950 text-slate-900 dark:text-white selection:bg-sage-400/20 selection:text-white">
      {/* ──────────────────────────────────────────────────────────────────────────
          1. CINEMATIC 3D HERO
      ────────────────────────────────────────────────────────────────────────── */}
      <section className="relative pt-6 pb-20 overflow-hidden">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 items-center min-h-[580px]">
            {/* Left Column: Editorial & Value Proposition */}
            <div className="lg:col-span-5 space-y-6 z-10">
              <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-dark-850 border border-dark-750 shadow-subtle">
                <span className="w-2 h-2 rounded-full bg-sage-400 animate-pulse" />
                <span className="text-[11px] font-mono tracking-widest text-slate-300 uppercase">
                  THE DIGITAL OS FOR HOME CARE
                </span>
              </div>

              <h1 className="text-4xl sm:text-5xl lg:text-6xl font-extrabold tracking-tight leading-[1.08]">
                SMART HOME<br />
                MAINTENANCE,<br />
                <span className="bg-gradient-to-r from-light-pure via-light-secondary to-slate-400 bg-clip-text text-transparent">
                  SIMPLIFIED.
                </span>
              </h1>

              <p className="text-sm sm:text-base text-slate-400 max-w-md leading-relaxed font-normal">
                One intelligent platform for trusted professionals, seamless bookings, secure verification, and effortless home maintenance.
              </p>

              {/* CTAs */}
              <div className="flex flex-wrap items-center gap-3.5 pt-2">
                <button
                  onClick={() => navigate('/booking/new')}
                  className="btn-primary px-6 py-3 text-xs sm:text-sm font-semibold shadow-subtle hover:shadow-metallic flex items-center gap-2 group"
                >
                  <span>BOOK A SERVICE</span>
                  <ArrowRight className="w-4 h-4 transition-transform group-hover:translate-x-1" />
                </button>

                <button
                  onClick={() => navigate('/services')}
                  className="btn-secondary px-6 py-3 text-xs sm:text-sm font-semibold flex items-center gap-2"
                >
                  <span>EXPLORE SERVICES</span>
                  <ChevronRight className="w-4 h-4 text-slate-400" />
                </button>
              </div>

              {/* Trust Indicators */}
              <div className="pt-6 border-t border-dark-750/80 grid grid-cols-3 gap-4 text-left">
                <div>
                  <span className="text-lg font-bold font-mono text-white block">100%</span>
                  <span className="text-[11px] text-slate-400">Verified Techs</span>
                </div>
                <div>
                  <span className="text-lg font-bold font-mono text-white block">30-Day</span>
                  <span className="text-[11px] text-slate-400">Work Guarantee</span>
                </div>
                <div>
                  <span className="text-lg font-bold font-mono text-white block">SmartVerify</span>
                  <span className="text-[11px] text-slate-400">Zero Fraud OTP</span>
                </div>
              </div>
            </div>

            {/* Right Column: Interactive 3D Architectural House Scene */}
            <div className="lg:col-span-7 relative">
              <HeroScene3D />
            </div>
          </div>
        </div>
      </section>

      {/* ──────────────────────────────────────────────────────────────────────────
          2. SMART HOME LAYERED VIEW ("YOUR HOME. ONE INTELLIGENT PLATFORM.")
      ────────────────────────────────────────────────────────────────────────── */}
      <SmartHomeLayeredView />

      {/* ──────────────────────────────────────────────────────────────────────────
          3. EDITORIAL SERVICES DISCOVERY
      ────────────────────────────────────────────────────────────────────────── */}
      <section className="py-20 border-t border-dark-750/80 relative">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex flex-col md:flex-row md:items-end justify-between mb-12 gap-4">
            <div>
              <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-dark-850 border border-dark-750 mb-3">
                <Layers className="w-3.5 h-3.5 text-sage-400" />
                <span className="text-xs font-mono tracking-wider text-slate-300 uppercase">SERVICE CATALOG</span>
              </div>
              <h2 className="text-3xl sm:text-4xl font-extrabold tracking-tight text-white">
                Engineered for Architectural Precision
              </h2>
              <p className="text-sm text-slate-400 mt-2 max-w-xl">
                Restrained, transparent, component-level pricing. Every job executed by background-verified specialists.
              </p>
            </div>

            <button
              onClick={() => navigate('/services')}
              className="btn-secondary text-xs px-5 py-2.5 flex items-center gap-2 self-start md:self-auto"
            >
              <span>View All Services</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </div>

          {/* Services Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {[
              { title: 'Plumbing', price: 299, time: 30, icon: Droplet, desc: 'Tap Repair, Pipe Leakage, Drain Cleaning, Sink Repair, Toilet Repair, Water Tank Repair, Bathroom Plumbing' },
              { title: 'Electrical', price: 199, time: 30, icon: Zap, desc: 'Switch & Socket Repair, Fan Installation, Light Installation, Wiring Repair, MCB Repair, Short-Circuit Repair, Inverter Installation' },
              { title: 'AC & Cooling', price: 499, time: 60, icon: Wind, desc: 'AC Service, AC Repair, AC Installation, AC Gas Refill, AC Cleaning, Cooler Repair' },
              { title: 'Appliances', price: 349, time: 45, icon: Monitor, desc: 'Refrigerator Repair, Washing Machine Repair, Microwave Repair, Geyser Repair, Water Purifier Service' },
              { title: 'Carpentry', price: 249, time: 60, icon: Wrench, desc: 'Furniture Repair, Door Repair, Lock Installation, Cabinet Repair, Shelf Installation, Bed Repair' },
              { title: 'Cleaning', price: 999, time: 120, icon: Sparkles, desc: 'Full Home Cleaning, Kitchen Cleaning, Bathroom Cleaning, Sofa Cleaning, Carpet Cleaning, Floor Cleaning' },
              { title: 'Painting', price: 1499, time: 240, icon: Paintbrush, desc: 'Room Painting, Full Home Painting, Wall Touch-up, Exterior Painting, Waterproof Painting' },
              { title: 'Bathroom', price: 399, time: 60, icon: Bath, desc: 'Bathroom Deep Cleaning, Shower Repair, Toilet Repair, Basin Repair, Exhaust Fan Installation' },
              { title: 'Home Maintenance', price: 499, time: 90, icon: Home, desc: 'General Inspection, Minor Repairs, Wall Repair, Grouting, Waterproofing, Home Inspection' },
              { title: 'Security & Smart Home', price: 599, time: 90, icon: ShieldCheck, desc: 'CCTV Installation, Smart Lock Installation, Doorbell Installation, Wi-Fi Camera Setup' },
              { title: 'Outdoor & Garden', price: 349, time: 60, icon: TreePine, desc: 'Garden Maintenance, Lawn Cleaning, Plant Maintenance, Balcony Cleaning' },
              { title: 'Windows & Doors', price: 299, time: 45, icon: DoorOpen, desc: 'Door Alignment, Door Handle Repair, Window Repair, Glass Replacement, Mosquito Net Installation' },
            ].map((item, idx) => (
              <div
                key={idx}
                onClick={() => navigate('/booking/new')}
                className="group p-6 rounded-3xl bg-dark-900/90 hover:bg-dark-850 border border-dark-750 hover:border-dark-700 transition-all duration-200 cursor-pointer flex flex-col justify-between shadow-card"
              >
                <div>
                  <div className="flex items-center justify-between mb-4">
                    <div className="w-12 h-12 rounded-2xl bg-dark-800 group-hover:bg-sage-400/15 border border-dark-750 group-hover:border-sage-400/30 flex items-center justify-center text-sage-400 transition-colors">
                      <item.icon className="w-6 h-6" />
                    </div>
                    <span className="text-xs font-mono font-bold text-white px-2.5 py-1 rounded-lg bg-dark-800 border border-dark-750">
                      Starts ₹{item.price}
                    </span>
                  </div>

                  <h3 className="text-base font-bold text-white tracking-tight group-hover:text-sage-300 transition-colors mb-2">
                    {item.title}
                  </h3>
                  <p className="text-xs text-slate-400 leading-relaxed">
                    {item.desc}
                  </p>
                </div>

                <div className="pt-5 mt-5 border-t border-dark-750/70 flex items-center justify-between text-xs text-slate-400 font-mono">
                  <span className="flex items-center gap-1.5">
                    <Clock className="w-3.5 h-3.5 text-sage-400" />
                    <span>~{item.time} mins</span>
                  </span>
                  <span className="text-sage-400 group-hover:translate-x-1 transition-transform flex items-center gap-1 font-semibold">
                    <span>Explore</span>
                    <ChevronRight className="w-3.5 h-3.5" />
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ──────────────────────────────────────────────────────────────────────────
          4. HOW HOMIQ WORKS (4 ARCHITECTURAL STEPS)
      ────────────────────────────────────────────────────────────────────────── */}
      <section className="py-20 border-t border-dark-750/80 relative overflow-hidden">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-2xl mx-auto mb-16">
            <h2 className="text-3xl sm:text-4xl font-extrabold tracking-tight text-white">
              How HomiQ Works
            </h2>
            <p className="text-sm text-slate-400 mt-2">
              A completely frictionless, end-to-end digital lifecycle designed for uncompromising home care.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            {[
              {
                step: '01',
                title: 'Select & Schedule',
                desc: 'Pick your home module, choose certified options, and set your preferred arrival slot.',
                icon: Layers,
              },
              {
                step: '02',
                title: 'Live Pro Dispatch',
                desc: 'A background-verified technician is routed with real-time ETA tracking.',
                icon: Navigation,
              },
              {
                step: '03',
                title: 'SmartVerify™ Handshake',
                desc: 'Scan QR or verify 6-digit passcode before work begins to eliminate unauthorized access.',
                icon: QrCode,
              },
              {
                step: '04',
                title: 'Guaranteed Completion',
                desc: 'Pay securely after digital quality audit with HomiQ 30-day workmanship warranty.',
                icon: ShieldCheck,
              },
            ].map((item, idx) => {
              const StepIcon = item.icon;
              return (
                <div
                  key={idx}
                  className="p-6 rounded-3xl bg-dark-900 border border-dark-750 relative flex flex-col justify-between shadow-card"
                >
                  <div>
                    <div className="flex items-center justify-between mb-6">
                      <span className="text-2xl font-extrabold font-mono text-sage-400/40">{item.step}</span>
                      <div className="w-10 h-10 rounded-xl bg-dark-850 border border-dark-750 flex items-center justify-center text-sage-400">
                        <StepIcon className="w-5 h-5" />
                      </div>
                    </div>
                    <h3 className="text-base font-bold text-white tracking-tight mb-2">{item.title}</h3>
                    <p className="text-xs text-slate-400 leading-relaxed">{item.desc}</p>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* ──────────────────────────────────────────────────────────────────────────
          5. SMARTVERIFY™ QR & OTP VERIFICATION SHOWCASE
      ────────────────────────────────────────────────────────────────────────── */}
      <section className="py-20 border-t border-dark-750/80 relative">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="p-8 sm:p-12 rounded-3xl bg-gradient-to-b from-dark-900 via-dark-850 to-dark-900 border border-dark-750 shadow-modal grid grid-cols-1 lg:grid-cols-12 gap-10 items-center">
            <div className="lg:col-span-6 space-y-5">
              <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-sage-400/10 border border-sage-400/25">
                <Lock className="w-3.5 h-3.5 text-sage-400" />
                <span className="text-xs font-mono tracking-widest text-sage-300 uppercase">SECURITY PROTOCOL</span>
              </div>
              <h2 className="text-3xl sm:text-4xl font-extrabold tracking-tight text-white">
                Zero Unauthorized Entry.<br />
                <span className="text-sage-400">SmartVerify™ Handshake.</span>
              </h2>
              <p className="text-sm text-slate-400 leading-relaxed">
                Every technician visit requires a cryptographic double-blind verification. Confirm the 6-digit dynamic passcode or scan the encrypted QR code on your HomiQ Dashboard before unlocking your door.
              </p>
              
              <ul className="space-y-3 text-xs text-slate-300 pt-2">
                <li className="flex items-center gap-2.5">
                  <CheckCircle2 className="w-4 h-4 text-sage-400 shrink-0" />
                  <span>Time-locked, single-use 256-bit token</span>
                </li>
                <li className="flex items-center gap-2.5">
                  <CheckCircle2 className="w-4 h-4 text-sage-400 shrink-0" />
                  <span>Real-time GPS boundary validation</span>
                </li>
                <li className="flex items-center gap-2.5">
                  <CheckCircle2 className="w-4 h-4 text-sage-400 shrink-0" />
                  <span>Automatic digital audit log recorded on backend</span>
                </li>
              </ul>
            </div>

            {/* Visual Handshake Graphic */}
            <div className="lg:col-span-6 flex justify-center">
              <div className="w-full max-w-sm p-6 rounded-3xl bg-dark-950 border border-dark-750 shadow-modal space-y-4 text-center">
                <div className="flex items-center justify-between pb-3 border-b border-dark-750 text-xs font-mono text-slate-400">
                  <span className="flex items-center gap-1 text-sage-400 font-bold">
                    <ShieldCheck className="w-4 h-4" /> SmartVerify
                  </span>
                  <span>STATUS: SECURE</span>
                </div>

                <div className="p-4 rounded-2xl bg-dark-900 border border-dark-750 flex items-center justify-center gap-2">
                  {['8', '4', '9', '2', '0', '1'].map((digit, idx) => (
                    <span
                      key={idx}
                      className="w-9 h-12 rounded-xl bg-dark-850 border border-sage-400/30 text-xl font-mono font-bold text-white flex items-center justify-center shadow-accent"
                    >
                      {digit}
                    </span>
                  ))}
                </div>

                <p className="text-[11px] font-mono text-slate-400">
                  Present to arriving technician to initiate verified session
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ──────────────────────────────────────────────────────────────────────────
          6. RECRUITMENT ("BUILD YOUR CAREER WITH HOMIQ")
      ────────────────────────────────────────────────────────────────────────── */}
      <section className="py-20 border-t border-dark-750/80 relative">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex flex-col md:flex-row md:items-end justify-between mb-12 gap-4">
            <div>
              <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-dark-850 border border-dark-750 mb-3">
                <Briefcase className="w-3.5 h-3.5 text-sage-400" />
                <span className="text-xs font-mono tracking-wider text-slate-300 uppercase">CAREERS & FLEETS</span>
              </div>
              <h2 className="text-3xl sm:text-4xl font-extrabold tracking-tight text-white">
                BUILD YOUR CAREER WITH HOMIQ.
              </h2>
              <p className="text-sm text-slate-400 mt-2 max-w-xl">
                Join a network of verified master craftsmen. Industry-leading compensation, flexible dispatch, and guaranteed payouts.
              </p>
            </div>

            <button
              onClick={() => navigate('/jobs')}
              className="btn-secondary text-xs px-5 py-2.5 flex items-center gap-2 self-start md:self-auto"
            >
              <span>Explore All Open Roles</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {recentJobs.length > 0 ? (
              recentJobs.map((job) => (
                <div
                  key={job.id}
                  onClick={() => navigate('/jobs')}
                  className="p-6 rounded-3xl bg-dark-900/90 hover:bg-dark-850 border border-dark-750 hover:border-dark-700 transition-all duration-200 cursor-pointer flex flex-col justify-between shadow-card"
                >
                  <div>
                    <span className="text-[10px] font-mono uppercase px-2.5 py-1 rounded-lg bg-dark-800 text-sage-300 border border-dark-750 mb-3 inline-block">
                      {job.salary_range || 'Competitive Rates'}
                    </span>
                    <h3 className="text-base font-bold text-white tracking-tight mb-1.5">{job.title}</h3>
                    <p className="text-xs text-slate-400 flex items-center gap-1 mb-4">
                      <MapPin className="w-3.5 h-3.5 text-slate-500" />
                      <span>{job.location || 'Pan-City Rapid Dispatch'}</span>
                    </p>
                  </div>
                  <div className="pt-4 border-t border-dark-750 flex items-center justify-between text-xs text-sage-400 font-semibold">
                    <span>Apply Now</span>
                    <ChevronRight className="w-3.5 h-3.5" />
                  </div>
                </div>
              ))
            ) : (
              [
                { title: 'Master HVAC Technician', type: 'Full-Time / Fleet', loc: 'Metro Zones' },
                { title: 'Licensed Electrical Specialist', type: 'Contractor', loc: 'North & West Hub' },
                { title: 'Senior Hydraulics Engineer', type: 'Enterprise Fleet', loc: 'Downtown Region' },
              ].map((item, idx) => (
                <div
                  key={idx}
                  onClick={() => navigate('/jobs')}
                  className="p-6 rounded-3xl bg-dark-900/90 hover:bg-dark-850 border border-dark-750 hover:border-dark-700 transition-all duration-200 cursor-pointer flex flex-col justify-between shadow-card"
                >
                  <div>
                    <span className="text-[10px] font-mono uppercase px-2.5 py-1 rounded-lg bg-dark-800 text-sage-300 border border-dark-750 mb-3 inline-block">
                      {item.type}
                    </span>
                    <h3 className="text-base font-bold text-white tracking-tight mb-1.5">{item.title}</h3>
                    <p className="text-xs text-slate-400 flex items-center gap-1 mb-4">
                      <MapPin className="w-3.5 h-3.5 text-slate-500" />
                      <span>{item.loc}</span>
                    </p>
                  </div>
                  <div className="pt-4 border-t border-dark-750 flex items-center justify-between text-xs text-sage-400 font-semibold">
                    <span>Apply Now</span>
                    <ChevronRight className="w-3.5 h-3.5" />
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </section>

      {/* ──────────────────────────────────────────────────────────────────────────
          7. FINAL CTA
      ────────────────────────────────────────────────────────────────────────── */}
      <section className="py-24 border-t border-dark-750/80 relative overflow-hidden">
        <div className="max-w-5xl mx-auto px-4 text-center space-y-6 relative z-10">
          <HomiQLogo variant="stacked" size="lg" showTagline className="mx-auto mb-6" />
          
          <h2 className="text-3xl sm:text-5xl font-extrabold tracking-tight text-white max-w-2xl mx-auto">
            Everything your home needs, intelligently connected.
          </h2>

          <p className="text-sm text-slate-400 max-w-xl mx-auto leading-relaxed">
            Experience the new standard in architectural residence maintenance. Book a certified master technician in under two minutes.
          </p>

          <div className="pt-4 flex flex-wrap items-center justify-center gap-4">
            <button
              onClick={() => navigate('/booking/new')}
              className="btn-primary px-8 py-3.5 text-sm font-semibold shadow-subtle hover:shadow-metallic flex items-center gap-2"
            >
              <span>BOOK A SERVICE NOW</span>
              <ArrowRight className="w-4 h-4" />
            </button>
            <button
              onClick={() => navigate('/register')}
              className="btn-secondary px-8 py-3.5 text-sm font-semibold"
            >
              Create Home Account
            </button>
          </div>
        </div>
      </section>
    </div>
  );
};
