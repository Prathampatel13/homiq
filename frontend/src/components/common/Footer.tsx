import React from 'react';
import { Link } from 'react-router-dom';
import { HomiQLogo } from '../brand/HomiQLogo';
import { ShieldCheck, Lock, CheckCircle2 } from 'lucide-react';

export const Footer: React.FC = () => {
  return (
    <footer className="bg-white border-t border-slate-200 text-slate-600 relative overflow-hidden">
      {/* Background Grid Accent */}
      <div 
        className="absolute inset-0 opacity-5 pointer-events-none"
        style={{
          backgroundImage: 'radial-gradient(circle, #8FA8A0 1px, transparent 1px)',
          backgroundSize: '32px 32px'
        }}
      />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16 relative z-10">
        <div className="grid grid-cols-1 md:grid-cols-5 gap-10 lg:gap-12">
          {/* Brand Column (2 cols) */}
          <div className="md:col-span-2 space-y-4">
            <HomiQLogo variant="full" size="md" />
            <p className="text-xs text-slate-600 max-w-sm leading-relaxed mt-3">
              Modern, reliable home care delivered by verified professionals. Transparent pricing, instant booking, and guaranteed satisfaction.
            </p>
            
            <div className="flex items-center gap-4 pt-2">
              <div className="flex items-center gap-1.5 text-xs text-slate-700 font-medium">
                <ShieldCheck className="w-4 h-4 text-sage-600" />
                <span>Verified Professionals</span>
              </div>
              <div className="flex items-center gap-1.5 text-xs text-slate-700 font-medium">
                <Lock className="w-4 h-4 text-sage-600" />
                <span>Secure Payments</span>
              </div>
            </div>
          </div>

          {/* Services Column */}
          <div>
            <h4 className="text-xs font-mono uppercase tracking-widest text-slate-900 font-bold mb-4">Services</h4>
            <ul className="space-y-2.5 text-xs text-slate-600">
              <li><Link to="/services" className="hover:text-sage-600 transition-colors">AC & Cooling</Link></li>
              <li><Link to="/services" className="hover:text-sage-600 transition-colors">Electrical & Wiring</Link></li>
              <li><Link to="/services" className="hover:text-sage-600 transition-colors">Plumbing & Fixtures</Link></li>
              <li><Link to="/services" className="hover:text-sage-600 transition-colors">Smart Home & Security</Link></li>
              <li><Link to="/services" className="hover:text-sage-600 transition-colors">Deep Cleaning</Link></li>
              <li><Link to="/services" className="hover:text-sage-600 transition-colors">Carpentry & Repairs</Link></li>
            </ul>
          </div>

          {/* Professionals Column */}
          <div>
            <h4 className="text-xs font-mono uppercase tracking-widest text-slate-900 font-bold mb-4">Professionals</h4>
            <ul className="space-y-2.5 text-xs text-slate-600">
              <li><Link to="/register" className="hover:text-sage-600 transition-colors">Join as Technician</Link></li>
              <li><Link to="/register" className="hover:text-sage-600 transition-colors">Register Company Fleet</Link></li>
              <li><Link to="/provider/dashboard" className="hover:text-sage-600 transition-colors">Technician Portal</Link></li>
              <li><Link to="/company/dashboard" className="hover:text-sage-600 transition-colors">Partner Dashboard</Link></li>
            </ul>
          </div>

          {/* System & Trust */}
          <div>
            <h4 className="text-xs font-mono uppercase tracking-widest text-slate-900 font-bold mb-4">Quality & Trust</h4>
            <ul className="space-y-2.5 text-xs text-slate-600">
              <li className="flex items-center gap-1.5 text-slate-700">
                <CheckCircle2 className="w-3.5 h-3.5 text-sage-600" />
                <span>100% Background-Checked</span>
              </li>
              <li className="flex items-center gap-1.5 text-slate-700">
                <CheckCircle2 className="w-3.5 h-3.5 text-sage-600" />
                <span>30-Day Service Guarantee</span>
              </li>
              <li className="flex items-center gap-1.5 text-slate-700">
                <CheckCircle2 className="w-3.5 h-3.5 text-sage-600" />
                <span>Transparent Quotes</span>
              </li>
              <li className="pt-2">
                <div className="p-2.5 rounded-xl bg-slate-50 border border-slate-200 text-[11px] font-mono text-slate-600">
                  Platform Status: <span className="text-sage-600 font-bold">ALL SYSTEMS LIVE</span>
                </div>
              </li>
            </ul>
          </div>
        </div>

        {/* Bottom Bar */}
        <div className="pt-12 mt-12 border-t border-slate-200 flex flex-col sm:flex-row items-center justify-between gap-4 text-xs font-mono text-slate-500">
          <p>© {new Date().getFullYear()} HomiQ Technologies Inc. All rights reserved.</p>
          <div className="flex items-center gap-6">
            <span>Privacy Policy</span>
            <span>Terms of Service</span>
            <span>Security Audits</span>
          </div>
        </div>
      </div>
    </footer>
  );
};
