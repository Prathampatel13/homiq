import React from 'react';
import { Link } from 'react-router-dom';
import { HomiQLogo } from '../brand/HomiQLogo';
import { ShieldCheck, Lock, CheckCircle2 } from 'lucide-react';

export const Footer: React.FC = () => {
  return (
    <footer className="bg-dark-950 border-t border-dark-750 text-slate-400 relative overflow-hidden">
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
            <p className="text-xs text-slate-400 max-w-sm leading-relaxed mt-3">
              The digital operating system for architectural home maintenance. Certified master technicians, cryptographic SmartVerify check-in, and guaranteed precision care.
            </p>
            
            <div className="flex items-center gap-4 pt-2">
              <div className="flex items-center gap-1.5 text-xs text-slate-300 font-mono">
                <ShieldCheck className="w-4 h-4 text-sage-400" />
                <span>SmartVerify Protected</span>
              </div>
              <div className="flex items-center gap-1.5 text-xs text-slate-300 font-mono">
                <Lock className="w-4 h-4 text-sage-400" />
                <span>256-Bit Encrypted</span>
              </div>
            </div>
          </div>

          {/* Services Column */}
          <div>
            <h4 className="text-xs font-mono uppercase tracking-widest text-white mb-4">Service Ecosystem</h4>
            <ul className="space-y-2.5 text-xs">
              <li><Link to="/services" className="hover:text-sage-400 transition-colors">AC & Climate Control</Link></li>
              <li><Link to="/services" className="hover:text-sage-400 transition-colors">Electrical & Smart Power</Link></li>
              <li><Link to="/services" className="hover:text-sage-400 transition-colors">Plumbing & Hydraulics</Link></li>
              <li><Link to="/services" className="hover:text-sage-400 transition-colors">Appliance Diagnostics</Link></li>
              <li><Link to="/services" className="hover:text-sage-400 transition-colors">Deep Sanitization</Link></li>
              <li><Link to="/services" className="hover:text-sage-400 transition-colors">Carpentry & Millwork</Link></li>
            </ul>
          </div>

          {/* Professionals Column */}
          <div>
            <h4 className="text-xs font-mono uppercase tracking-widest text-white mb-4">Professionals</h4>
            <ul className="space-y-2.5 text-xs">
              <li><Link to="/jobs" className="hover:text-sage-400 transition-colors">Careers & Open Roles</Link></li>
              <li><Link to="/register" className="hover:text-sage-400 transition-colors">Join as Technician</Link></li>
              <li><Link to="/register" className="hover:text-sage-400 transition-colors">Register Company Fleet</Link></li>
              <li><Link to="/provider/dashboard" className="hover:text-sage-400 transition-colors">Technician Portal</Link></li>
              <li><Link to="/company/dashboard" className="hover:text-sage-400 transition-colors">Enterprise Workspace</Link></li>
            </ul>
          </div>

          {/* System & Trust */}
          <div>
            <h4 className="text-xs font-mono uppercase tracking-widest text-white mb-4">Architecture & Trust</h4>
            <ul className="space-y-2.5 text-xs">
              <li className="flex items-center gap-1.5 text-slate-300">
                <CheckCircle2 className="w-3.5 h-3.5 text-sage-400" />
                <span>Zero Fake Data</span>
              </li>
              <li className="flex items-center gap-1.5 text-slate-300">
                <CheckCircle2 className="w-3.5 h-3.5 text-sage-400" />
                <span>30-Day Work Guarantee</span>
              </li>
              <li className="flex items-center gap-1.5 text-slate-300">
                <CheckCircle2 className="w-3.5 h-3.5 text-sage-400" />
                <span>Real-Time Dispatch</span>
              </li>
              <li className="pt-2">
                <div className="p-2.5 rounded-xl bg-dark-900 border border-dark-750 text-[11px] font-mono text-slate-400">
                  System Status: <span className="text-sage-400 font-bold">OPERATIONAL</span>
                </div>
              </li>
            </ul>
          </div>
        </div>

        {/* Bottom Bar */}
        <div className="pt-12 mt-12 border-t border-dark-750/70 flex flex-col sm:flex-row items-center justify-between gap-4 text-xs font-mono text-slate-500">
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
