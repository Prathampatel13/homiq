import React, { useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import {
  LayoutGrid,
  X,
  Home,
  Calendar,
  Navigation,
  QrCode,
  Briefcase,
  Building2,
  ShieldCheck,
  Wrench,
  ChevronUp
} from 'lucide-react';

import { useAuthStore } from '../../store/useAuthStore';
import { UserRole } from '../../types';

export const FloatingNav: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);
  const location = useLocation();
  const navigate = useNavigate();
  const { getEffectiveRole } = useAuthStore();
  const role = getEffectiveRole();

  const getPageInfo = (pathname: string) => {
    if (pathname === '/') return { name: 'Landing Page', icon: Home };
    if (pathname === '/customer/dashboard') return { name: 'Customer Dashboard', icon: LayoutGrid };
    if (pathname === '/booking/new') return { name: 'Book Service', icon: Calendar };
    if (pathname.includes('/provider/dashboard')) return { name: 'Technician Workspace', icon: Wrench };
    if (pathname.includes('/jobs')) return { name: 'Recruitment', icon: Briefcase };
    if (pathname.includes('/company/dashboard')) return { name: 'Company Dashboard', icon: Building2 };
    if (pathname.includes('/admin/dashboard')) return { name: 'Admin Panel', icon: ShieldCheck };
    return { name: 'HomiQ Platform', icon: LayoutGrid };
  };

  const currentInfo = getPageInfo(location.pathname);

  const handleNavigate = (path: string) => {
    navigate(path);
    setIsOpen(false);
  };

  const NavItem = ({ path, icon: Icon, label, isActive }: { path: string, icon: any, label: string, isActive: boolean }) => (
    <button 
      onClick={() => handleNavigate(path)}
      className={`w-full flex items-center p-3 rounded-2xl transition-all mb-2 ${isActive ? 'bg-dark-800 ring-1 ring-sage-400/50' : 'hover:bg-dark-800/50'}`}
    >
      <div className={`p-2.5 rounded-xl mr-4 ${isActive ? 'bg-sage-400 text-dark-950 shadow-md shadow-sage-400/20' : 'bg-dark-850 text-slate-400'}`}>
        <Icon className="w-5 h-5" />
      </div>
      <div className="flex flex-col items-start flex-1">
        <span className={`font-bold text-sm ${isActive ? 'text-sage-400' : 'text-slate-300'}`}>{label}</span>
        {isActive && <span className="text-xs font-medium text-sage-400/70 mt-0.5">Current view</span>}
      </div>
      {isActive && <div className="w-2 h-2 rounded-full bg-sage-400 ml-2 mr-1" />}
    </button>
  );

  return (
    <div className="fixed bottom-24 md:bottom-6 left-1/2 -translate-x-1/2 z-[100] flex flex-col items-center w-[340px]">
      {/* Menu Popup */}
      {isOpen && (
        <div className="mb-4 w-full bg-dark-900/95 backdrop-blur-xl rounded-3xl shadow-modal overflow-hidden border border-dark-750 flex flex-col animate-in fade-in slide-in-from-bottom-4 duration-200">
          <div className="p-5 border-b border-dark-750 pb-3">
            <p className="text-[10px] font-semibold text-slate-400 tracking-wider mb-0.5 uppercase">SWITCH VIEW</p>
            <h3 className="text-lg font-bold text-white">Platform Navigation</h3>
          </div>
          
          <div className="p-4 max-h-[60vh] overflow-y-auto">
            {/* PUBLIC (Only for Non-Technicians) */}
            {role !== UserRole.TECHNICIAN && (
              <div className="mb-6">
                <p className="text-[11px] font-bold text-slate-500 tracking-widest mb-3 px-3 uppercase">PUBLIC</p>
                <NavItem path="/" icon={Home} label="Landing Page" isActive={location.pathname === '/'} />
              </div>
            )}

            {/* CUSTOMER (Only for Customers / Admins) */}
            {role !== UserRole.TECHNICIAN && (!role || role === UserRole.CUSTOMER || role === UserRole.ADMIN) && (
              <div className="mb-6">
                <p className="text-[11px] font-bold text-slate-500 tracking-widest mb-3 px-3 uppercase">CUSTOMER</p>
                <NavItem path="/customer/dashboard" icon={LayoutGrid} label="Customer Dashboard" isActive={location.pathname === '/customer/dashboard'} />
                <NavItem path="/booking/new" icon={Calendar} label="Book Service" isActive={location.pathname === '/booking/new'} />
                <NavItem path="/live-tracking" icon={Navigation} label="Live Tracking" isActive={location.pathname === '/live-tracking'} />
                <NavItem path="/qr-verification" icon={QrCode} label="QR Verification" isActive={location.pathname === '/qr-verification'} />
              </div>
            )}

            {/* PROFESSIONAL / TECHNICIAN */}
            {(role === UserRole.TECHNICIAN || role === UserRole.ADMIN) && (
              <div className="mb-6">
                <p className="text-[11px] font-bold text-slate-500 tracking-widest mb-3 px-3 uppercase">TECHNICIAN WORKSPACE</p>
                <NavItem path="/provider/dashboard" icon={Wrench} label="Technician Workspace" isActive={location.pathname.includes('/provider/dashboard')} />
                {role === UserRole.TECHNICIAN && (
                  <>
                    <NavItem path="/history" icon={LayoutGrid} label="Mission History" isActive={location.pathname === '/history'} />
                    <NavItem path="/reviews" icon={ShieldCheck} label="Ratings & Feedback" isActive={location.pathname === '/reviews'} />
                  </>
                )}
              </div>
            )}

            {/* JOBS */}
            {role !== UserRole.TECHNICIAN && (
              <div className="mb-6">
                <p className="text-[11px] font-bold text-slate-500 tracking-widest mb-3 px-3 uppercase">JOBS</p>
                <NavItem path="/jobs" icon={Briefcase} label="Recruitment" isActive={location.pathname === '/jobs'} />
                {(role === UserRole.COMPANY || role === UserRole.ADMIN) && (
                  <NavItem path="/company/dashboard" icon={Building2} label="Company Dashboard" isActive={location.pathname.includes('/company/dashboard')} />
                )}
              </div>
            )}

            {/* ADMIN */}
            {role === UserRole.ADMIN && (
              <div className="mb-2">
                <p className="text-[11px] font-bold text-slate-500 tracking-widest mb-3 px-3 uppercase">ADMIN</p>
                <NavItem path="/admin/dashboard" icon={ShieldCheck} label="Admin Panel" isActive={location.pathname.includes('/admin/dashboard')} />
              </div>
            )}
          </div>
        </div>
      )}

      {/* Floating Button */}
      <div className="flex items-center bg-dark-900 rounded-2xl shadow-modal overflow-hidden border border-dark-750 text-white transition-all hover:border-sage-400/50">
        <button 
          onClick={() => setIsOpen(!isOpen)}
          className="flex items-center px-5 py-3.5 hover:bg-dark-850 transition-colors"
        >
          <currentInfo.icon className="w-4 h-4 mr-2 text-sage-400" />
          <span className="text-sm font-semibold whitespace-nowrap">{currentInfo.name}</span>
        </button>
        <div className="w-px h-6 bg-dark-750"></div>
        <button 
          onClick={(e) => {
            e.stopPropagation();
            setIsOpen(!isOpen);
          }}
          className="px-5 py-3.5 hover:bg-dark-850 transition-colors"
        >
          {isOpen ? (
            <X className="w-4 h-4 text-slate-400 hover:text-slate-900 transition-colors" />
          ) : (
            <ChevronUp className="w-4 h-4 text-slate-400 hover:text-slate-900 transition-colors" />
          )}
        </button>
      </div>
    </div>
  );
};
