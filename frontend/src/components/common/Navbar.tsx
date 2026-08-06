import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { ShieldCheck, Menu, X, LogOut, LayoutDashboard, Bell, MapPin, ChevronDown, User, Sparkles } from 'lucide-react';
import { useAuthStore } from '../../store/useAuthStore';
import { Button } from '../ui/Button';
import { UserRole } from '../../types';

export const Navbar: React.FC = () => {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [isProfileDropdownOpen, setIsProfileDropdownOpen] = useState(false);
  const [selectedCity, setSelectedCity] = useState('Mumbai');
  const [isCityDropdownOpen, setIsCityDropdownOpen] = useState(false);
  const { user, isAuthenticated, logout } = useAuthStore();
  const navigate = useNavigate();

  const cities = ['Mumbai', 'Delhi NCR', 'Bengaluru', 'Hyderabad', 'Pune', 'Chennai'];

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const getDashboardPath = () => {
    if (!user) return '/login';
    switch (user.role) {
      case UserRole.ADMIN:
        return '/admin/dashboard';
      case UserRole.TECHNICIAN:
        return '/provider/dashboard';
      default:
        return '/customer/dashboard';
    }
  };

  return (
    <header className="glass-navbar">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-20">
          {/* Brand Logo & City Selector */}
          <div className="flex items-center gap-6">
            <Link to="/" className="flex items-center gap-3 group">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-brand-600 via-indigo-600 to-emerald-500 flex items-center justify-center shadow-lg shadow-brand-500/20 group-hover:scale-105 transition-transform duration-200">
                <ShieldCheck className="w-6 h-6 text-white" />
              </div>
              <span className="text-2xl font-bold tracking-tight text-white">
                Homi<span className="gradient-text">Q</span>
              </span>
            </Link>

            {/* City Selector */}
            <div className="relative hidden sm:block">
              <button
                onClick={() => setIsCityDropdownOpen(!isCityDropdownOpen)}
                className="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-slate-900/80 border border-slate-800 text-xs font-semibold text-slate-300 hover:text-white hover:border-slate-700 transition-colors"
              >
                <MapPin className="w-3.5 h-3.5 text-brand-400" />
                <span>{selectedCity}</span>
                <ChevronDown className="w-3 h-3 text-slate-500" />
              </button>

              <AnimatePresence>
                {isCityDropdownOpen && (
                  <motion.div
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: 10 }}
                    className="absolute left-0 mt-2 w-44 glass-card p-2 shadow-2xl border border-slate-800 z-50"
                  >
                    {cities.map((city) => (
                      <button
                        key={city}
                        onClick={() => {
                          setSelectedCity(city);
                          setIsCityDropdownOpen(false);
                        }}
                        className={`w-full text-left px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${
                          selectedCity === city
                            ? 'bg-brand-600 text-white font-bold'
                            : 'text-slate-300 hover:bg-slate-800/80 hover:text-white'
                        }`}
                      >
                        {city}
                      </button>
                    ))}
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          </div>

          {/* Navigation Links */}
          <nav className="hidden md:flex items-center gap-8 text-sm font-medium text-slate-300">
            <Link to="/" className="hover:text-white transition-colors">Home</Link>
            <Link to="/services" className="hover:text-white transition-colors">All Services</Link>
            <Link to="/categories" className="hover:text-white transition-colors">Categories</Link>
            <Link to="/about" className="hover:text-white transition-colors">About Us</Link>
          </nav>

          {/* User & Auth Buttons */}
          <div className="hidden md:flex items-center gap-4">
            {isAuthenticated && user ? (
              <div className="flex items-center gap-3">
                {/* Notification Bell */}
                <Link to={getDashboardPath()}>
                  <button className="relative p-2 rounded-xl bg-slate-900 border border-slate-800 text-slate-300 hover:text-white hover:border-slate-700 transition-colors">
                    <Bell className="w-4 h-4" />
                    <span className="absolute top-1 right-1 w-2 h-2 rounded-full bg-brand-400 animate-ping" />
                  </button>
                </Link>

                {/* Profile Dropdown */}
                <div className="relative">
                  <button
                    onClick={() => setIsProfileDropdownOpen(!isProfileDropdownOpen)}
                    className="flex items-center gap-3 p-1.5 rounded-xl hover:bg-slate-900 border border-transparent hover:border-slate-800 transition-all duration-200"
                  >
                    <div className="w-9 h-9 rounded-lg bg-gradient-to-tr from-indigo-600 via-purple-600 to-brand-500 flex items-center justify-center text-white font-bold text-sm shadow-md">
                      {user.full_name?.charAt(0) || 'U'}
                    </div>
                    <div className="text-left hidden lg:block">
                      <div className="text-xs font-semibold text-white">{user.full_name}</div>
                      <div className="text-[10px] text-slate-400 capitalize">{user.role.replace('ROLE_', '').toLowerCase()}</div>
                    </div>
                    <ChevronDown className="w-3.5 h-3.5 text-slate-500 hidden lg:block" />
                  </button>

                  <AnimatePresence>
                    {isProfileDropdownOpen && (
                      <motion.div
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: 10 }}
                        className="absolute right-0 mt-2 w-56 glass-card p-2 shadow-2xl border border-slate-800 z-50 space-y-1"
                      >
                        <div className="px-3 py-2 border-b border-slate-800">
                          <div className="text-xs font-bold text-white">{user.full_name}</div>
                          <div className="text-[10px] text-slate-400">{user.email}</div>
                        </div>

                        <Link
                          to={getDashboardPath()}
                          onClick={() => setIsProfileDropdownOpen(false)}
                          className="flex items-center gap-2.5 px-3 py-2 text-xs font-medium text-slate-300 hover:text-white hover:bg-slate-800/80 rounded-lg transition-colors"
                        >
                          <LayoutDashboard className="w-4 h-4 text-brand-400" />
                          Dashboard Operations
                        </Link>

                        <button
                          onClick={handleLogout}
                          className="w-full flex items-center gap-2.5 px-3 py-2 text-xs font-medium text-rose-400 hover:bg-rose-500/10 rounded-lg transition-colors"
                        >
                          <LogOut className="w-4 h-4" />
                          Sign Out Account
                        </button>
                      </motion.div>
                    )}
                  </AnimatePresence>
                </div>
              </div>
            ) : (
              <div className="flex items-center gap-3">
                <Link to="/login">
                  <Button variant="outline" size="sm">Sign In</Button>
                </Link>
                <Link to="/register">
                  <Button variant="primary" size="sm">Get Started</Button>
                </Link>
              </div>
            )}
          </div>

          {/* Mobile Drawer Trigger */}
          <div className="md:hidden">
            <button
              onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
              className="p-2 text-slate-400 hover:text-white rounded-lg focus:outline-none"
            >
              {isMobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Navigation Drawer */}
      <AnimatePresence>
        {isMobileMenuOpen && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="md:hidden glass-card mx-4 mb-4 p-4 flex flex-col gap-3"
          >
            <Link to="/" onClick={() => setIsMobileMenuOpen(false)} className="text-sm font-medium text-slate-300 hover:text-white">Home</Link>
            <Link to="/services" onClick={() => setIsMobileMenuOpen(false)} className="text-sm font-medium text-slate-300 hover:text-white">Services</Link>
            <Link to="/categories" onClick={() => setIsMobileMenuOpen(false)} className="text-sm font-medium text-slate-300 hover:text-white">Categories</Link>
            {isAuthenticated ? (
              <>
                <Link to={getDashboardPath()} onClick={() => setIsMobileMenuOpen(false)} className="text-sm font-medium text-brand-400">Dashboard</Link>
                <button onClick={handleLogout} className="text-sm font-medium text-rose-400 text-left">Sign Out</button>
              </>
            ) : (
              <div className="flex flex-col gap-2 pt-2 border-t border-slate-800">
                <Link to="/login" onClick={() => setIsMobileMenuOpen(false)}>
                  <Button variant="outline" size="sm" className="w-full">Sign In</Button>
                </Link>
                <Link to="/register" onClick={() => setIsMobileMenuOpen(false)}>
                  <Button variant="primary" size="sm" className="w-full">Get Started</Button>
                </Link>
              </div>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </header>
  );
};
