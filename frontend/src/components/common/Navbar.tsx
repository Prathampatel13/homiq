import React, { useState } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { ShieldCheck, User, LogOut, ChevronDown, Menu, X, PlusCircle, LayoutDashboard, Bell } from 'lucide-react';
import { useAuthStore } from '../../store/useAuthStore';
import { UserRole } from '../../types';
import { Button } from '../ui/Button';

export const Navbar: React.FC = () => {
  const { user, isAuthenticated, logout, getEffectiveRole } = useAuthStore();
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [isProfileOpen, setIsProfileOpen] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();

  const role = getEffectiveRole();

  const handleLogout = () => {
    logout();
    setIsProfileOpen(false);
    setIsMenuOpen(false);
    navigate('/');
  };

  const getDashboardPath = () => {
    switch (role) {
      case UserRole.ADMIN:
        return '/admin/dashboard';
      case UserRole.TECHNICIAN:
        return '/provider/dashboard';
      case UserRole.COMPANY:
        return '/company/dashboard';
      default:
        return '/customer/dashboard';
    }
  };

  const isCurrent = (path: string) => location.pathname === path;

  return (
    <nav className="surface-navbar">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link to="/" className="flex items-center gap-2.5 group">
            <div className="w-8 h-8 rounded-xl bg-gradient-to-tr from-brand-600 to-brand-400 flex items-center justify-center text-white shadow-accent">
              <ShieldCheck className="w-5 h-5" />
            </div>
            <div className="flex items-center gap-1.5">
              <span className="text-lg font-bold tracking-tight text-white font-mono">HomiQ</span>
              <span className="text-[10px] font-semibold tracking-widest uppercase px-1.5 py-0.5 rounded bg-dark-800 text-slate-400 border border-dark-700">
                PRO
              </span>
            </div>
          </Link>

          {/* Desktop Nav Links */}
          <div className="hidden md:flex items-center gap-7 text-sm font-medium">
            <Link
              to="/services"
              className={`transition-colors ${
                isCurrent('/services') ? 'text-brand-400 font-semibold' : 'text-slate-300 hover:text-white'
              }`}
            >
              Services
            </Link>
            <Link
              to="/jobs"
              className={`transition-colors ${
                isCurrent('/jobs') ? 'text-brand-400 font-semibold' : 'text-slate-300 hover:text-white'
              }`}
            >
              Recruitment
            </Link>
            {isAuthenticated && (
              <Link
                to={getDashboardPath()}
                className={`flex items-center gap-1.5 transition-colors ${
                  location.pathname.includes('dashboard') ? 'text-brand-400 font-semibold' : 'text-slate-300 hover:text-white'
                }`}
              >
                <LayoutDashboard className="w-4 h-4" />
                <span>Dashboard</span>
              </Link>
            )}
          </div>

          {/* Action CTAs / User profile */}
          <div className="hidden md:flex items-center gap-3">
            {isAuthenticated && user ? (
              <div className="flex items-center gap-3">
                {role === UserRole.CUSTOMER && (
                  <Button
                    variant="primary"
                    size="sm"
                    leftIcon={PlusCircle}
                    onClick={() => navigate('/booking/new')}
                  >
                    Book Service
                  </Button>
                )}

                {/* Profile menu */}
                <div className="relative">
                  <button
                    onClick={() => setIsProfileOpen(!isProfileOpen)}
                    className="flex items-center gap-2.5 p-1.5 pr-3 rounded-xl bg-dark-850 border border-dark-700 hover:border-dark-750 text-slate-200 transition-all text-xs font-medium"
                  >
                    <div className="w-7 h-7 rounded-lg bg-dark-750 flex items-center justify-center font-bold text-brand-400">
                      {user.full_name?.charAt(0).toUpperCase() || 'U'}
                    </div>
                    <span className="max-w-[120px] truncate text-slate-200 font-medium">{user.full_name}</span>
                    <ChevronDown className="w-3.5 h-3.5 text-slate-400" />
                  </button>

                  {/* Dropdown */}
                  {isProfileOpen && (
                    <div className="absolute right-0 mt-2 w-56 bg-dark-900 border border-dark-700/90 rounded-2xl shadow-modal p-1.5 z-50 text-left">
                      <div className="px-3 py-2.5 border-b border-dark-800">
                        <p className="text-xs font-semibold text-white truncate">{user.full_name}</p>
                        <p className="text-[11px] text-slate-400 truncate mt-0.5">{user.email}</p>
                        <div className="mt-1.5">
                          <span className="inline-block px-2 py-0.5 text-[10px] uppercase font-mono font-semibold rounded bg-brand-500/10 text-brand-400 border border-brand-500/20">
                            {role.replace('ROLE_', '')}
                          </span>
                        </div>
                      </div>

                      <div className="py-1">
                        <Link
                          to={getDashboardPath()}
                          onClick={() => setIsProfileOpen(false)}
                          className="flex items-center gap-2 px-3 py-2 text-xs text-slate-300 hover:text-white hover:bg-dark-850 rounded-xl transition-colors"
                        >
                          <LayoutDashboard className="w-4 h-4 text-slate-400" />
                          <span>Dashboard</span>
                        </Link>
                      </div>

                      <div className="pt-1 border-t border-dark-800">
                        <button
                          onClick={handleLogout}
                          className="flex items-center gap-2 w-full px-3 py-2 text-xs text-rose-400 hover:bg-rose-500/10 rounded-xl transition-colors"
                        >
                          <LogOut className="w-4 h-4" />
                          <span>Sign Out</span>
                        </button>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            ) : (
              <div className="flex items-center gap-2.5">
                <Button variant="ghost" size="sm" onClick={() => navigate('/login')}>
                  Sign In
                </Button>
                <Button variant="primary" size="sm" onClick={() => navigate('/register')}>
                  Get Started
                </Button>
              </div>
            )}
          </div>

          {/* Mobile Menu Button */}
          <div className="flex md:hidden items-center gap-2">
            <button
              onClick={() => setIsMenuOpen(!isMenuOpen)}
              className="p-2 rounded-xl text-slate-400 hover:text-white bg-dark-850 border border-dark-700"
            >
              {isMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Drawer */}
      {isMenuOpen && (
        <div className="md:hidden bg-dark-900 border-b border-dark-700/80 px-4 py-4 space-y-3">
          <Link
            to="/services"
            onClick={() => setIsMenuOpen(false)}
            className="block px-3 py-2 text-sm text-slate-300 hover:text-white hover:bg-dark-850 rounded-xl"
          >
            Services Catalog
          </Link>
          <Link
            to="/jobs"
            onClick={() => setIsMenuOpen(false)}
            className="block px-3 py-2 text-sm text-slate-300 hover:text-white hover:bg-dark-850 rounded-xl"
          >
            Recruitment
          </Link>
          {isAuthenticated && (
            <Link
              to={getDashboardPath()}
              onClick={() => setIsMenuOpen(false)}
              className="block px-3 py-2 text-sm text-slate-300 hover:text-white hover:bg-dark-850 rounded-xl"
            >
              Dashboard
            </Link>
          )}

          <div className="pt-3 border-t border-dark-800">
            {isAuthenticated ? (
              <button
                onClick={handleLogout}
                className="flex items-center gap-2 w-full px-3 py-2 text-sm text-rose-400 hover:bg-rose-500/10 rounded-xl"
              >
                <LogOut className="w-4 h-4" />
                <span>Sign Out</span>
              </button>
            ) : (
              <div className="flex flex-col gap-2">
                <Button variant="outline" size="sm" onClick={() => { setIsMenuOpen(false); navigate('/login'); }}>
                  Sign In
                </Button>
                <Button variant="primary" size="sm" onClick={() => { setIsMenuOpen(false); navigate('/register'); }}>
                  Create Account
                </Button>
              </div>
            )}
          </div>
        </div>
      )}
    </nav>
  );
};
