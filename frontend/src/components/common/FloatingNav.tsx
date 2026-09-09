import React, { useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import {
  LayoutGrid,
  X,
  Home,
  Calendar,
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
    if (pathname.includes('/company/dashboard')) return { name: 'Company Dashboard', icon: Building2 };
    if (pathname.includes('/admin/dashboard')) return { name: 'Admin Panel', icon: ShieldCheck };
    return { name: 'HomiQ Platform', icon: LayoutGrid };
  };

  const currentInfo = getPageInfo(location.pathname);

  const handleNavigate = (path: string) => {
    navigate(path);
    setIsOpen(false);
  };

  const NavItem = ({ path, icon: Icon, label, isActive }: { path: string; icon: any; label: string; isActive: boolean }) => (
    <button 
      onClick={() => handleNavigate(path)}
      className={`w-full flex items-center p-3 rounded-2xl transition-all mb-2 ${
        isActive ? 'bg-sage-50 ring-1 ring-sage-500/30' : 'hover:bg-slate-50'
      }`}
    >
      <div className={`p-2.5 rounded-xl mr-4 ${
        isActive ? 'bg-sage-500 text-white shadow-md shadow-sage-500/20' : 'bg-slate-100 text-slate-600'
      }`}>
        <Icon className="w-5 h-5" />
      </div>
      <div className="flex flex-col items-start flex-1">
        <span className={`font-bold text-sm ${isActive ? 'text-sage-700' : 'text-slate-800'}`}>{label}</span>
        {isActive && <span className="text-xs font-medium text-sage-600 mt-0.5">Current view</span>}
      </div>
      {isActive && <div className="w-2 h-2 rounded-full bg-sage-500 ml-2 mr-1" />}
    </button>
  );

  return (
    <div className="fixed bottom-24 md:bottom-6 left-1/2 -translate-x-1/2 z-[100] flex flex-col items-center w-[340px]">
      {/* Menu Popup */}
      {isOpen && (
        <div className="mb-4 w-full bg-white/98 backdrop-blur-xl rounded-3xl shadow-modal overflow-hidden border border-slate-200 flex flex-col animate-in fade-in slide-in-from-bottom-4 duration-200">
          <div className="p-5 border-b border-slate-100 pb-3">
            <p className="text-[10px] font-semibold text-slate-400 tracking-wider mb-0.5 uppercase">SWITCH VIEW</p>
            <h3 className="text-lg font-bold text-slate-900">Platform Navigation</h3>
          </div>
          
          <div className="p-4 max-h-[60vh] overflow-y-auto">
            {/* PUBLIC (Only for Non-Technicians) */}
            {role !== UserRole.TECHNICIAN && (
              <div className="mb-5">
                <p className="text-[11px] font-bold text-slate-400 tracking-widest mb-2.5 px-3 uppercase">PUBLIC</p>
                <NavItem path="/" icon={Home} label="Landing Page" isActive={location.pathname === '/'} />
              </div>
            )}

            {/* CUSTOMER (Only for Customers / Admins) */}
            {role !== UserRole.TECHNICIAN && (!role || role === UserRole.CUSTOMER || role === UserRole.ADMIN) && (
              <div className="mb-5">
                <p className="text-[11px] font-bold text-slate-400 tracking-widest mb-2.5 px-3 uppercase">CUSTOMER</p>
                <NavItem path="/customer/dashboard" icon={LayoutGrid} label="Customer Dashboard" isActive={location.pathname === '/customer/dashboard'} />
                <NavItem path="/booking/new" icon={Calendar} label="Book Service" isActive={location.pathname === '/booking/new'} />
              </div>
            )}

            {/* PROFESSIONAL / TECHNICIAN */}
            {(role === UserRole.TECHNICIAN || role === UserRole.ADMIN) && (
              <div className="mb-5">
                <p className="text-[11px] font-bold text-slate-400 tracking-widest mb-2.5 px-3 uppercase">TECHNICIAN WORKSPACE</p>
                <NavItem path="/provider/dashboard" icon={Wrench} label="Technician Workspace" isActive={location.pathname.includes('/provider/dashboard')} />
                {role === UserRole.TECHNICIAN && (
                  <>
                    <NavItem path="/history" icon={LayoutGrid} label="Mission History" isActive={location.pathname === '/history'} />
                    <NavItem path="/reviews" icon={ShieldCheck} label="Ratings & Feedback" isActive={location.pathname === '/reviews'} />
                  </>
                )}
              </div>
            )}

            {/* ENTERPRISE FLEET / COMPANY */}
            {(role === UserRole.COMPANY || role === UserRole.ADMIN) && (
              <div className="mb-5">
                <p className="text-[11px] font-bold text-slate-400 tracking-widest mb-2.5 px-3 uppercase">ENTERPRISE</p>
                <NavItem path="/company/dashboard" icon={Building2} label="Company Dashboard" isActive={location.pathname.includes('/company/dashboard')} />
              </div>
            )}

            {/* ADMIN */}
            {role === UserRole.ADMIN && (
              <div className="mb-2">
                <p className="text-[11px] font-bold text-slate-400 tracking-widest mb-2.5 px-3 uppercase">ADMIN</p>
                <NavItem path="/admin/dashboard" icon={ShieldCheck} label="Admin Panel" isActive={location.pathname.includes('/admin/dashboard')} />
              </div>
            )}
          </div>
        </div>
      )}

      {/* Floating Button */}
      <div className="flex items-center bg-white rounded-2xl shadow-modal overflow-hidden border border-slate-200 text-slate-800 transition-all hover:border-slate-300">
        <button 
          onClick={() => setIsOpen(!isOpen)}
          className="flex items-center px-5 py-3.5 hover:bg-slate-50 transition-colors"
        >
          <currentInfo.icon className="w-4 h-4 mr-2 text-sage-600" />
          <span className="text-sm font-semibold whitespace-nowrap text-slate-900">{currentInfo.name}</span>
        </button>
        <div className="w-px h-6 bg-slate-200"></div>
        <button 
          onClick={(e) => {
            e.stopPropagation();
            setIsOpen(!isOpen);
          }}
          className="px-5 py-3.5 hover:bg-slate-50 transition-colors"
          aria-label="Toggle Menu"
        >
          {isOpen ? (
            <X className="w-4 h-4 text-slate-500 hover:text-slate-900 transition-colors" />
          ) : (
            <ChevronUp className="w-4 h-4 text-slate-500 hover:text-slate-900 transition-colors" />
          )}
        </button>
      </div>
    </div>
  );
};
