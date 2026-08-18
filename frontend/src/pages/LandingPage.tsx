import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import {
  ShieldCheck,
  Search,
  ArrowRight,
  CheckCircle2,
  Calendar,
  Sparkles,
  Award,
  Lock,
  ChevronRight,
  QrCode,
  Users,
  Briefcase,
  Star,
  Clock,
} from 'lucide-react';
import { servicesApi } from '../api/services';
import { reviewsApi } from '../api/reviews';
import { Service, ServiceCategory, Review } from '../types';
import { Button } from '../components/ui/Button';
import { Card } from '../components/ui/Card';

export const LandingPage: React.FC = () => {
  const navigate = useNavigate();
  const [categories, setCategories] = useState<ServiceCategory[]>([]);
  const [popularServices, setPopularServices] = useState<Service[]>([]);
  const [recentReviews, setRecentReviews] = useState<Review[]>([]);
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    servicesApi
      .getCategories()
      .then((data) => setCategories(data.slice(0, 6)))
      .catch(() => setCategories([]));

    servicesApi
      .getServices({ limit: 6 })
      .then((data) => setPopularServices(data))
      .catch(() => setPopularServices([]));

    reviewsApi
      .getReviews({ limit: 3 })
      .then((data) => {
        if (Array.isArray(data)) setRecentReviews(data);
        else if (data && (data as any).items) setRecentReviews((data as any).items);
      })
      .catch(() => setRecentReviews([]));
  }, []);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      navigate(`/services?search=${encodeURIComponent(searchQuery.trim())}`);
    } else {
      navigate('/services');
    }
  };

  return (
    <div className="space-y-24 pb-20 overflow-hidden">
      {/* 1. HERO SECTION */}
      <section className="relative pt-16 sm:pt-24 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto text-center">
        {/* Subtle top pill */}
        <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-dark-850 border border-dark-700/80 text-xs font-medium text-slate-300 shadow-subtle mb-8">
          <span className="flex h-2 w-2 rounded-full bg-brand-400 animate-pulse" />
          <span className="text-slate-300">Next-Gen Home Infrastructure Platform</span>
          <ChevronRight className="w-3.5 h-3.5 text-slate-500" />
        </div>

        {/* Main Headline */}
        <h1 className="text-4xl sm:text-6xl lg:text-7xl font-bold tracking-tight text-white max-w-4xl mx-auto leading-[1.1] font-sans">
          Smart Home Maintenance,{' '}
          <span className="text-transparent bg-clip-text bg-gradient-to-r from-brand-400 via-sky-300 to-white">
            Simplified.
          </span>
        </h1>

        <p className="mt-6 text-base sm:text-lg text-slate-400 max-w-2xl mx-auto leading-relaxed">
          Book verified trade specialists in seconds with cryptographic SmartVerify QR handshakes, upfront transparent pricing, and instant real-time dispatch.
        </p>

        {/* Interactive Search Bar */}
        <form onSubmit={handleSearchSubmit} className="mt-10 max-w-2xl mx-auto">
          <div className="flex items-center p-2 rounded-2xl bg-dark-900/90 border border-dark-700/90 shadow-card focus-within:border-brand-500/80 focus-within:ring-1 focus-within:ring-brand-500 transition-all">
            <div className="pl-3.5 text-slate-400">
              <Search className="w-5 h-5" />
            </div>
            <input
              type="text"
              placeholder="Search AC repair, electrical wiring, plumbing, cleaning..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="flex-1 bg-transparent px-3.5 py-2.5 text-sm text-white placeholder-slate-500 focus:outline-none"
            />
            <Button variant="primary" size="md" type="submit">
              Find Services
            </Button>
          </div>
        </form>

        {/* Quick Service Categories Grid */}
        {categories.length > 0 && (
          <div className="mt-12 grid grid-cols-2 sm:grid-cols-3 md:grid-cols-6 gap-3 max-w-5xl mx-auto">
            {categories.map((cat) => (
              <button
                key={cat.id}
                onClick={() => navigate(`/services?category=${cat.id}`)}
                className="flex flex-col items-center justify-center p-4 rounded-xl bg-dark-900/60 hover:bg-dark-850 border border-dark-700/60 hover:border-dark-750 transition-all duration-150 group"
              >
                <div className="w-10 h-10 rounded-xl bg-dark-800 flex items-center justify-center text-slate-300 group-hover:text-brand-400 group-hover:scale-105 transition-all mb-2 shadow-subtle">
                  <Sparkles className="w-5 h-5" />
                </div>
                <span className="text-xs font-semibold text-slate-200 group-hover:text-white truncate max-w-full">
                  {cat.name}
                </span>
              </button>
            ))}
          </div>
        )}
      </section>

      {/* 2. HOW IT WORKS (4-STEP STREAMLINED FLOW) */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center max-w-2xl mx-auto mb-16">
          <p className="text-xs font-mono uppercase tracking-widest text-brand-400 font-semibold mb-2">
            Engineered For Reliability
          </p>
          <h2 className="text-3xl font-bold text-white tracking-tight">How HomiQ Works</h2>
          <p className="text-sm text-slate-400 mt-3">
            From instant online booking to cryptographic completion verification in 4 effortless steps.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          {[
            {
              step: '01',
              title: 'Select Service',
              desc: 'Choose from standardized, upfront pricing catalogs with guaranteed scope.',
              icon: Search,
            },
            {
              step: '02',
              title: 'Instant Dispatch',
              desc: 'Our matching algorithm assigns verified local technicians with live driving ETA.',
              icon: Clock,
            },
            {
              step: '03',
              title: 'SmartVerify Handshake',
              desc: 'Authenticate the pro using dynamic encrypted QR codes & OTP before work begins.',
              icon: QrCode,
            },
            {
              step: '04',
              title: '30-Day Guaranteed',
              desc: 'Pay safely upon verified completion with full workmanship warranty.',
              icon: ShieldCheck,
            },
          ].map((item, idx) => (
            <div
              key={idx}
              className="p-6 rounded-2xl bg-dark-900/80 border border-dark-700/60 relative group hover:border-dark-750 transition-all duration-200"
            >
              <span className="text-3xl font-bold font-mono text-dark-750 group-hover:text-brand-500/30 transition-colors">
                {item.step}
              </span>
              <div className="w-10 h-10 rounded-xl bg-dark-850 border border-dark-750 flex items-center justify-center text-brand-400 mt-4 mb-3">
                <item.icon className="w-5 h-5" />
              </div>
              <h3 className="text-base font-semibold text-white tracking-tight">{item.title}</h3>
              <p className="text-xs text-slate-400 mt-2 leading-relaxed">{item.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* 3. POPULAR SERVICES SHOWCASE */}
      {popularServices.length > 0 && (
        <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-end justify-between mb-10">
            <div>
              <p className="text-xs font-mono uppercase tracking-widest text-brand-400 font-semibold mb-2">
                Top Rated
              </p>
              <h2 className="text-2xl sm:text-3xl font-bold text-white tracking-tight">Popular Home Services</h2>
            </div>
            <Link
              to="/services"
              className="flex items-center gap-1.5 text-xs font-semibold text-brand-400 hover:text-brand-300 transition-colors"
            >
              <span>View All Services</span>
              <ArrowRight className="w-4 h-4" />
            </Link>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {popularServices.map((srv) => (
              <Card key={srv.id} className="flex flex-col justify-between group hover:border-dark-750">
                <div className="space-y-3">
                  <div className="flex items-start justify-between">
                    <span className="px-2.5 py-0.5 rounded-full text-[11px] font-medium bg-dark-800 text-slate-300 border border-dark-750">
                      {srv.category_name || 'Home Maintenance'}
                    </span>
                    <div className="flex items-center gap-1 text-xs font-semibold text-amber-400 font-mono">
                      <Star className="w-3.5 h-3.5 fill-amber-400" />
                      <span>{(srv.rating_avg || 4.9).toFixed(1)}</span>
                    </div>
                  </div>

                  <h3 className="text-base font-bold text-white group-hover:text-brand-400 transition-colors">
                    {srv.name}
                  </h3>
                  <p className="text-xs text-slate-400 line-clamp-2 leading-relaxed">
                    {srv.description || 'Professional certified installation and diagnostics.'}
                  </p>
                </div>

                <div className="pt-4 mt-4 border-t border-dark-800/80 flex items-center justify-between">
                  <div>
                    <span className="text-[11px] text-slate-500 block">Starting from</span>
                    <span className="text-lg font-bold text-white font-mono">
                      ₹{srv.price || srv.base_price || 499}
                    </span>
                  </div>
                  <Button
                    variant="primary"
                    size="sm"
                    onClick={() => navigate(`/booking/new?service_id=${srv.id}`)}
                  >
                    Book Now
                  </Button>
                </div>
              </Card>
            ))}
          </div>
        </section>
      )}

      {/* 4. SMARTVERIFY SECURITY SECTION */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="p-8 sm:p-12 rounded-3xl bg-gradient-to-b from-dark-900 to-dark-950 border border-dark-700/80 grid grid-cols-1 lg:grid-cols-2 gap-10 items-center">
          <div className="space-y-6">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-xs font-medium text-emerald-400">
              <ShieldCheck className="w-4 h-4" />
              <span>SmartVerify™ Zero-Trust Architecture</span>
            </div>

            <h2 className="text-3xl sm:text-4xl font-bold text-white tracking-tight leading-tight">
              Never let an unverified stranger into your home again.
            </h2>

            <p className="text-sm text-slate-400 leading-relaxed">
              Every HomiQ specialist undergoes government ID checks, trade qualification vetting, and criminal background screening. On arrival, proprietary SHA-256 QR tokens ensure absolute proof of identity.
            </p>

            <ul className="space-y-3 text-xs text-slate-300">
              <li className="flex items-center gap-2.5">
                <CheckCircle2 className="w-4 h-4 text-emerald-400 flex-shrink-0" />
                <span>Encrypted QR authentication before technician entry</span>
              </li>
              <li className="flex items-center gap-2.5">
                <CheckCircle2 className="w-4 h-4 text-emerald-400 flex-shrink-0" />
                <span>Live GPS location telemetry & ETA tracking</span>
              </li>
              <li className="flex items-center gap-2.5">
                <CheckCircle2 className="w-4 h-4 text-emerald-400 flex-shrink-0" />
                <span>Escrow payments released only upon confirmed completion</span>
              </li>
            </ul>

            <div className="pt-2">
              <Button variant="outline" size="md" onClick={() => navigate('/services')}>
                Explore Verified Services
              </Button>
            </div>
          </div>

          {/* Interactive UI Mockup card */}
          <div className="p-6 rounded-2xl bg-dark-850/90 border border-dark-750 space-y-4 shadow-modal">
            <div className="flex items-center justify-between pb-3 border-b border-dark-750">
              <div className="flex items-center gap-2.5">
                <div className="w-8 h-8 rounded-xl bg-emerald-500/20 text-emerald-400 flex items-center justify-center">
                  <ShieldCheck className="w-4 h-4" />
                </div>
                <div>
                  <p className="text-xs font-bold text-white">Cryptographic Handshake</p>
                  <p className="text-[10px] text-slate-400">Booking #HMQ-9482</p>
                </div>
              </div>
              <span className="px-2 py-0.5 rounded-full text-[10px] font-mono bg-emerald-500/15 text-emerald-400 border border-emerald-500/30">
                ACTIVE
              </span>
            </div>

            <div className="p-4 bg-dark-900 rounded-xl flex items-center justify-between">
              <div className="space-y-1">
                <p className="text-xs font-semibold text-white">Technician Verified</p>
                <p className="text-[11px] text-slate-400">Vikram S. • HVAC Master Certified</p>
              </div>
              <div className="w-12 h-12 bg-white rounded-lg p-1">
                <img
                  src="https://api.qrserver.com/v1/create-qr-code/?size=60x60&data=HOMIQ_VERIFIED"
                  alt="Verified QR"
                  className="w-full h-full"
                />
              </div>
            </div>

            <div className="text-[11px] text-slate-500 flex items-center justify-between pt-1">
              <span>Token: hmq_sec_9942bf7c8</span>
              <span>256-Bit SHA</span>
            </div>
          </div>
        </div>
      </section>

      {/* 5. RECRUITMENT & PARTNER CTA */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="p-8 sm:p-10 rounded-2xl bg-dark-900 border border-dark-700/80 flex flex-col md:flex-row items-center justify-between gap-6">
          <div className="space-y-2 text-center md:text-left">
            <h3 className="text-2xl font-bold text-white">Are You a Trade Specialist or Contractor?</h3>
            <p className="text-xs sm:text-sm text-slate-400 max-w-xl leading-relaxed">
              Join India's fastest growing network of certified technicians. Get consistent job dispatches, weekly guaranteed payouts, and professional tooling.
            </p>
          </div>
          <div className="flex items-center gap-3">
            <Button variant="outline" size="md" onClick={() => navigate('/jobs')} leftIcon={Briefcase}>
              View Openings
            </Button>
            <Button variant="primary" size="md" onClick={() => navigate('/register')} leftIcon={Users}>
              Join Network
            </Button>
          </div>
        </div>
      </section>
    </div>
  );
};
