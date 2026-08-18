import React from 'react';
import { Link } from 'react-router-dom';
import { ShieldCheck, Lock, CheckCircle2, Award } from 'lucide-react';

export const Footer: React.FC = () => {
  return (
    <footer className="border-t border-dark-700/60 bg-dark-950 text-slate-400 text-xs mt-auto">
      {/* Top trust bar */}
      <div className="border-b border-dark-800/80 bg-dark-900/40 py-6">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 grid grid-cols-2 md:grid-cols-4 gap-6 text-center sm:text-left">
          <div className="flex items-center gap-3 justify-center sm:justify-start">
            <div className="w-8 h-8 rounded-xl bg-dark-850 border border-dark-700 flex items-center justify-center text-brand-400">
              <ShieldCheck className="w-4 h-4" />
            </div>
            <div>
              <p className="font-semibold text-white">SmartVerify System</p>
              <p className="text-[11px] text-slate-500">Cryptographic QR & OTP</p>
            </div>
          </div>

          <div className="flex items-center gap-3 justify-center sm:justify-start">
            <div className="w-8 h-8 rounded-xl bg-dark-850 border border-dark-700 flex items-center justify-center text-emerald-400">
              <CheckCircle2 className="w-4 h-4" />
            </div>
            <div>
              <p className="font-semibold text-white">Verified Specialists</p>
              <p className="text-[11px] text-slate-500">Govt ID & Skill Verified</p>
            </div>
          </div>

          <div className="flex items-center gap-3 justify-center sm:justify-start">
            <div className="w-8 h-8 rounded-xl bg-dark-850 border border-dark-700 flex items-center justify-center text-sky-400">
              <Lock className="w-4 h-4" />
            </div>
            <div>
              <p className="font-semibold text-white">Secure Payments</p>
              <p className="text-[11px] text-slate-500">Escrow & Razorpay Gateway</p>
            </div>
          </div>

          <div className="flex items-center gap-3 justify-center sm:justify-start">
            <div className="w-8 h-8 rounded-xl bg-dark-850 border border-dark-700 flex items-center justify-center text-amber-400">
              <Award className="w-4 h-4" />
            </div>
            <div>
              <p className="font-semibold text-white">30-Day Guarantee</p>
              <p className="text-[11px] text-slate-500">Workmanship Protection</p>
            </div>
          </div>
        </div>
      </div>

      {/* Main navigation columns */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid grid-cols-2 md:grid-cols-5 gap-8">
          <div className="col-span-2 space-y-4">
            <div className="flex items-center gap-2">
              <div className="w-7 h-7 rounded-xl bg-brand-500 flex items-center justify-center text-white font-bold text-xs">
                HQ
              </div>
              <span className="text-base font-bold text-white tracking-tight font-mono">HomiQ</span>
            </div>
            <p className="text-slate-400 max-w-sm leading-relaxed text-xs">
              Smart home maintenance ecosystem connecting homeowners with vetted trade professionals and enterprises.
            </p>
            <div className="pt-2 flex items-center gap-3 text-slate-500 text-[11px]">
              <span>ISO 27001 Certified</span>
              <span>•</span>
              <span>256-bit Encryption</span>
            </div>
          </div>

          <div>
            <p className="font-semibold text-white mb-3 uppercase tracking-wider text-[11px]">Platform</p>
            <ul className="space-y-2.5">
              <li>
                <Link to="/services" className="hover:text-white transition-colors">
                  Services Catalog
                </Link>
              </li>
              <li>
                <Link to="/booking/new" className="hover:text-white transition-colors">
                  Book a Service
                </Link>
              </li>
              <li>
                <Link to="/customer/dashboard" className="hover:text-white transition-colors">
                  Customer Portal
                </Link>
              </li>
            </ul>
          </div>

          <div>
            <p className="font-semibold text-white mb-3 uppercase tracking-wider text-[11px]">Professionals</p>
            <ul className="space-y-2.5">
              <li>
                <Link to="/jobs" className="hover:text-white transition-colors">
                  Job Openings
                </Link>
              </li>
              <li>
                <Link to="/register" className="hover:text-white transition-colors">
                  Partner with Us
                </Link>
              </li>
              <li>
                <Link to="/provider/dashboard" className="hover:text-white transition-colors">
                  Technician Portal
                </Link>
              </li>
            </ul>
          </div>

          <div>
            <p className="font-semibold text-white mb-3 uppercase tracking-wider text-[11px]">Company</p>
            <ul className="space-y-2.5">
              <li>
                <Link to="/company/dashboard" className="hover:text-white transition-colors">
                  Enterprise B2B
                </Link>
              </li>
              <li>
                <Link to="/admin/dashboard" className="hover:text-white transition-colors">
                  Operations Command
                </Link>
              </li>
            </ul>
          </div>
        </div>

        <div className="pt-8 mt-8 border-t border-dark-800/80 flex flex-col sm:flex-row items-center justify-between gap-4 text-slate-500 text-[11px]">
          <p>© {new Date().getFullYear()} HomiQ Technologies Inc. All rights reserved.</p>
          <div className="flex items-center gap-6">
            <span>Privacy Policy</span>
            <span>Terms of Service</span>
            <span>Security Compliance</span>
          </div>
        </div>
      </div>
    </footer>
  );
};
