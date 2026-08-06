import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Search,
  ShieldCheck,
  Zap,
  Clock,
  Star,
  Wrench,
  Flame,
  Droplets,
  Sparkles,
  ChevronRight,
  MapPin,
  CheckCircle2,
  Lock,
  Bot,
  Send,
  X,
  Sliders,
  Award,
  Users,
  Shield,
} from 'lucide-react';
import { Button } from '../components/ui/Button';
import { Card } from '../components/ui/Card';

export const LandingPage: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [isAiAssistantOpen, setIsAiAssistantOpen] = useState(false);
  const [aiPrompt, setAiPrompt] = useState('');
  const [aiMessages, setAiMessages] = useState<Array<{ role: 'user' | 'ai'; text: string }>>([
    { role: 'ai', text: 'Hello! I am HomiQ AI Assistant. Describe your issue (e.g. "AC not cooling" or "water pipe leak") for an instant maintenance diagnosis and cost estimate!' }
  ]);
  const [isAiThinking, setIsAiThinking] = useState(false);

  const navigate = useNavigate();

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      navigate(`/services?search=${encodeURIComponent(searchQuery)}`);
    }
  };

  const handleAiDiagnoseSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!aiPrompt.trim()) return;

    const userText = aiPrompt;
    setAiMessages((prev) => [...prev, { role: 'user', text: userText }]);
    setAiPrompt('');
    setIsAiThinking(true);

    setTimeout(() => {
      let aiReply = "Based on your description, we recommend an Electrician Diagnostic inspection. Estimated time: 45 mins. Estimated cost: ₹499. Includes SmartVerify QR protection.";
      if (userText.toLowerCase().includes('ac') || userText.toLowerCase().includes('cool')) {
        aiReply = "AI Diagnosis: AC Gas Refill & Compressor Check required. Recommended Specialist: HVAC Certified Tech. Estimated Price: ₹999. Instant 15-min dispatch available.";
      } else if (userText.toLowerCase().includes('water') || userText.toLowerCase().includes('leak') || userText.toLowerCase().includes('pipe')) {
        aiReply = "AI Diagnosis: Ultrasonic Leak Detection & Pipe Fitting required. Recommended Specialist: Master Plumber. Estimated Price: ₹699.";
      }

      setAiMessages((prev) => [...prev, { role: 'ai', text: aiReply }]);
      setIsAiThinking(false);
    }, 1200);
  };

  const categories = [
    { id: 1, name: 'Electrical Repairs', icon: Zap, color: 'from-amber-500 to-orange-600', count: '45+ Verified Pros', avgPrice: '₹499' },
    { id: 2, name: 'Plumbing Services', icon: Droplets, color: 'from-blue-500 to-cyan-600', count: '60+ Master Plumbers', avgPrice: '₹599' },
    { id: 3, name: 'Appliance Care', icon: Flame, color: 'from-rose-500 to-red-600', count: '30+ HVAC Techs', avgPrice: '₹799' },
    { id: 4, name: 'Deep Cleaning', icon: Sparkles, color: 'from-emerald-500 to-teal-600', count: '25+ Sanitation Teams', avgPrice: '₹1,299' },
    { id: 5, name: 'Home Renovations', icon: Wrench, color: 'from-indigo-500 to-purple-600', count: '50+ Civil Engineers', avgPrice: '₹1,999' },
  ];

  const features = [
    {
      title: 'SmartVerify™ QR Authorization',
      desc: 'Cryptographic two-way QR scan verification prevents unauthorized entry and guarantees technician authenticity.',
      icon: ShieldCheck,
    },
    {
      title: 'Real-Time GPS Live Stream',
      desc: 'Watch technician movement in real-time on Google Maps with traffic-adjusted live arrival countdown.',
      icon: MapPin,
    },
    {
      title: 'AI Smart Match Engine',
      desc: 'Our neural dispatcher pairs your request with the highest-rated technician within a 5 km radius in under 60s.',
      icon: Bot,
    },
    {
      title: 'Razorpay Escrow Safety',
      desc: 'Payments held safely in escrow and released only when you scan the completion QR code.',
      icon: Lock,
    },
  ];

  return (
    <div className="space-y-24 pb-24 relative">
      {/* ── 1. Hero Section ─────────────────────────────────────────────────── */}
      <section className="relative pt-12 lg:pt-20 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto overflow-hidden">
        {/* Glow Effects */}
        <div className="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[700px] h-[700px] bg-gradient-to-tr from-brand-600/20 via-indigo-600/15 to-emerald-500/10 rounded-full blur-3xl -z-10 pointer-events-none" />

        <div className="text-center space-y-8 max-w-4xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="inline-flex items-center gap-2 px-4 py-2 rounded-full glass-card border-brand-500/30 text-xs font-semibold text-brand-400 shadow-glow"
          >
            <Sparkles className="w-4 h-4 text-brand-400 animate-pulse" />
            <span>AI-Powered Smart House Maintenance & SmartVerify QR</span>
          </motion.div>

          <motion.h1
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="text-4xl sm:text-6xl lg:text-7xl font-extrabold tracking-tight text-white leading-tight"
          >
            Next-Gen House Maintenance,{' '}
            <span className="gradient-text">Powered by AI & QR</span>
          </motion.h1>

          <motion.p
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="text-lg sm:text-xl text-slate-300 max-w-2xl mx-auto font-normal leading-relaxed"
          >
            Book background-checked electricians, plumbers, and repair specialists with live GPS tracking, AI diagnostics, and instant escrow protection.
          </motion.p>

          {/* Search Bar */}
          <motion.form
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            onSubmit={handleSearchSubmit}
            className="glass-card p-2.5 max-w-2xl mx-auto flex items-center gap-2 shadow-2xl border-slate-800"
          >
            <div className="flex items-center gap-3 px-3 flex-1">
              <Search className="w-5 h-5 text-brand-400" />
              <input
                type="text"
                placeholder="Search 'AC not cooling', 'Electrical repair', 'Water leak'..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full bg-transparent text-slate-100 placeholder-slate-500 focus:outline-none text-sm"
              />
            </div>
            <Button type="submit" variant="primary" size="md">
              Search Services
            </Button>
          </motion.form>

          {/* Stats Bar */}
          <div className="pt-6 grid grid-cols-2 sm:grid-cols-4 gap-4 max-w-3xl mx-auto border-t border-slate-800/80">
            <div>
              <div className="text-2xl font-extrabold text-white">4,800+</div>
              <div className="text-xs text-slate-400 font-medium">Verified Technicians</div>
            </div>
            <div>
              <div className="text-2xl font-extrabold text-white">15 Mins</div>
              <div className="text-xs text-slate-400 font-medium">Average ETA</div>
            </div>
            <div>
              <div className="text-2xl font-extrabold text-white">100%</div>
              <div className="text-xs text-slate-400 font-medium">SmartVerify QR</div>
            </div>
            <div>
              <div className="text-2xl font-extrabold text-white">4.92 ★</div>
              <div className="text-xs text-slate-400 font-medium">Average Rating</div>
            </div>
          </div>
        </div>
      </section>

      {/* ── 2. Category Grid Section ───────────────────────────────────────── */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-10">
        <div className="flex flex-col md:flex-row md:items-end justify-between gap-4">
          <div>
            <h2 className="text-2xl sm:text-4xl font-extrabold text-white">Browse Maintenance Categories</h2>
            <p className="text-slate-400 text-sm mt-1">Instant upfront pricing with certified technician guarantees</p>
          </div>
          <Link to="/categories" className="text-sm font-semibold text-brand-400 hover:text-brand-300 flex items-center gap-1">
            View All Categories <ChevronRight className="w-4 h-4" />
          </Link>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-6">
          {categories.map((cat, idx) => (
            <motion.div
              key={cat.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: idx * 0.08 }}
            >
              <Link to={`/services?category=${cat.id}`}>
                <Card hoverable className="h-full flex flex-col justify-between group border-slate-800 hover:border-brand-500/40">
                  <div className="space-y-4">
                    <div className={`w-12 h-12 rounded-2xl bg-gradient-to-tr ${cat.color} flex items-center justify-center text-white shadow-lg group-hover:scale-110 transition-transform duration-300`}>
                      <cat.icon className="w-6 h-6" />
                    </div>
                    <div>
                      <h3 className="text-lg font-bold text-white group-hover:text-brand-400 transition-colors">{cat.name}</h3>
                      <p className="text-xs text-slate-400 mt-1">{cat.count}</p>
                    </div>
                  </div>
                  <div className="mt-4 pt-4 border-t border-slate-800/80 flex items-center justify-between text-xs font-bold text-white">
                    <span>From {cat.avgPrice}</span>
                    <ChevronRight className="w-4 h-4 text-brand-400 group-hover:translate-x-1 transition-transform" />
                  </div>
                </Card>
              </Link>
            </motion.div>
          ))}
        </div>
      </section>

      {/* ── 3. Features & SmartVerify Showcase ─────────────────────────────── */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="glass-card p-8 lg:p-14 border-brand-500/20 relative overflow-hidden shadow-2xl">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
            <div className="space-y-6">
              <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 text-xs font-semibold">
                <CheckCircle2 className="w-4 h-4" /> Enterprise Security Standard
              </div>
              <h2 className="text-3xl sm:text-4xl font-bold text-white leading-tight">
                SmartVerify™ QR & Live GPS Security System
              </h2>
              <p className="text-slate-400 text-sm leading-relaxed">
                HomiQ eliminates home entry uncertainty. Every technician generates a cryptographic QR code that must be scanned by your smartphone before work can commence.
              </p>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-6 pt-2">
                {features.map((feat, i) => (
                  <div key={i} className="space-y-2">
                    <div className="w-8 h-8 rounded-lg bg-slate-800 flex items-center justify-center text-brand-400">
                      <feat.icon className="w-4 h-4" />
                    </div>
                    <h4 className="text-sm font-semibold text-white">{feat.title}</h4>
                    <p className="text-xs text-slate-400 leading-relaxed">{feat.desc}</p>
                  </div>
                ))}
              </div>
            </div>

            {/* SmartVerify Simulator Card */}
            <div className="relative flex justify-center">
              <div className="glass-card p-6 border-slate-800 space-y-6 max-w-md w-full shadow-2xl bg-slate-900/90">
                <div className="flex items-center justify-between border-b border-slate-800 pb-4">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-full bg-gradient-to-tr from-brand-600 to-indigo-600 flex items-center justify-center font-bold text-white">
                      RK
                    </div>
                    <div>
                      <div className="text-sm font-bold text-white">Rajesh Kumar</div>
                      <div className="text-xs text-slate-400">Licensed Electrician (⭐ 4.95)</div>
                    </div>
                  </div>
                  <span className="px-2.5 py-1 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 text-[10px] font-semibold">
                    VERIFIED
                  </span>
                </div>

                <div className="space-y-3 bg-slate-950 p-4 rounded-xl border border-slate-800 text-xs">
                  <div className="flex justify-between text-slate-400">
                    <span>Booking Reference:</span>
                    <span className="font-mono text-white font-bold">#HMQ-84920</span>
                  </div>
                  <div className="flex justify-between text-slate-400">
                    <span>SmartVerify QR Code:</span>
                    <span className="text-brand-400 font-bold">READY TO SCAN</span>
                  </div>
                  <div className="flex justify-between text-slate-400">
                    <span>Live GPS Location:</span>
                    <span className="text-emerald-400 font-bold">2.4 km away (ETA 8 mins)</span>
                  </div>
                </div>

                <Link to="/register">
                  <Button variant="primary" size="md" className="w-full">
                    Book Certified Technician Now
                  </Button>
                </Link>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ── 4. Floating AI Smart Maintenance Assistant Widget ───────────────── */}
      <div className="fixed bottom-6 right-6 z-50">
        <AnimatePresence>
          {isAiAssistantOpen ? (
            <motion.div
              initial={{ opacity: 0, scale: 0.9, y: 20 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.9, y: 20 }}
              className="glass-card w-80 sm:w-96 p-4 shadow-2xl border-brand-500/40 space-y-4 mb-2 bg-slate-900/95"
            >
              <div className="flex items-center justify-between border-b border-slate-800 pb-3">
                <div className="flex items-center gap-2">
                  <div className="w-8 h-8 rounded-lg bg-gradient-to-tr from-brand-600 to-indigo-600 flex items-center justify-center text-white">
                    <Bot className="w-4 h-4" />
                  </div>
                  <div>
                    <div className="text-xs font-bold text-white">HomiQ AI Maintenance Assistant</div>
                    <div className="text-[10px] text-emerald-400">Instant AI Diagnosis</div>
                  </div>
                </div>
                <button onClick={() => setIsAiAssistantOpen(false)} className="text-slate-400 hover:text-white">
                  <X className="w-4 h-4" />
                </button>
              </div>

              <div className="h-60 overflow-y-auto space-y-3 pr-1 text-xs">
                {aiMessages.map((m, i) => (
                  <div
                    key={i}
                    className={`p-3 rounded-xl max-w-[85%] ${
                      m.role === 'user'
                        ? 'bg-brand-600 text-white ml-auto'
                        : 'bg-slate-800 text-slate-200 border border-slate-700'
                    }`}
                  >
                    {m.text}
                  </div>
                ))}
                {isAiThinking && (
                  <div className="p-3 rounded-xl bg-slate-800 text-slate-400 italic text-xs animate-pulse">
                    AI is analyzing your maintenance issue...
                  </div>
                )}
              </div>

              <form onSubmit={handleAiDiagnoseSubmit} className="flex gap-2 pt-2 border-t border-slate-800">
                <input
                  type="text"
                  placeholder="Describe issue (e.g. AC leaking)..."
                  value={aiPrompt}
                  onChange={(e) => setAiPrompt(e.target.value)}
                  className="flex-1 px-3 py-2 bg-slate-950 border border-slate-800 rounded-xl text-white text-xs focus:outline-none focus:border-brand-500"
                />
                <Button type="submit" variant="primary" size="sm" className="px-3">
                  <Send className="w-3.5 h-3.5" />
                </Button>
              </form>
            </motion.div>
          ) : (
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => setIsAiAssistantOpen(true)}
              className="flex items-center gap-2.5 px-4 py-3 rounded-full gradient-btn shadow-glow text-xs font-bold"
            >
              <Bot className="w-5 h-5 text-white animate-bounce" />
              <span>Ask AI Maintenance Diagnosis</span>
            </motion.button>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
};
