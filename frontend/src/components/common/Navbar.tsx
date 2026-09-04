import React, { useState, useEffect } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { 
  User, 
  LogOut, 
  ChevronDown, 
  Menu, 
  X, 
  PlusCircle, 
  LayoutDashboard, 
  Briefcase, 
  Layers,
  Moon,
  Sun,
  Bell,
  Wallet,
  Settings,
  History,
  Star,
  BarChart3
} from 'lucide-react';
import { useAuthStore } from '../../store/useAuthStore';
import { UserRole } from '../../types';
import { HomiQLogo } from '../brand/HomiQLogo';
import { notificationsApi } from '../../api/notifications';

export const Navbar: React.FC = () => {
  const { user, isAuthenticated, logout, getEffectiveRole } = useAuthStore();
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [isProfileOpen, setIsProfileOpen] = useState(false);
  const [isNotificationsOpen, setIsNotificationsOpen] = useState(false);
  const [notifications, setNotifications] = useState<any[]>([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [isDarkMode, setIsDarkMode] = useState(() => {
    return localStorage.getItem('theme') !== 'light';
  });

  useEffect(() => {
    if (isAuthenticated) {
      notificationsApi.getNotifications({ limit: 5 }).then(res => {
        const items = Array.isArray(res) ? res : res.items;
        setNotifications(items);
        setUnreadCount(items.filter(i => !i.is_read).length);
      }).catch(console.error);
    }
  }, [isAuthenticated]);

  useEffect(() => {
    if (isDarkMode) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [isDarkMode]);

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
        <div className="flex items-center justify-between h-20">
          {/* Official HomiQ Logo */}
          <Link to="/" className="flex items-center gap-2 group">
            <HomiQLogo variant="horizontal" size="md" />
          </Link>

          {/* Desktop Nav Links */}
          <div className="hidden md:flex items-center gap-8 text-sm font-medium">
            {role !== UserRole.TECHNICIAN && (
              <Link
                to="/services"
                className={`transition-colors duration-150 flex items-center gap-1.5 ${
                  isCurrent('/services') ? 'text-sage-400 font-semibold' : 'text-slate-300 hover:text-white'
                }`}
              >
                <Layers className="w-4 h-4" />
                <span>Services</span>
              </Link>
            )}
            
            {role !== UserRole.TECHNICIAN && (
              <Link
                to="/jobs"
                className={`transition-colors duration-150 flex items-center gap-1.5 ${
                  isCurrent('/jobs') ? 'text-sage-400 font-semibold' : 'text-slate-300 hover:text-white'
                }`}
              >
                <Briefcase className="w-4 h-4" />
                <span>Recruitment</span>
              </Link>
            )}

            {isAuthenticated && (
              <Link
                to={getDashboardPath()}
                className={`flex items-center gap-1.5 transition-colors duration-150 ${
                  location.pathname.includes('dashboard') ? 'text-sage-400 font-semibold' : 'text-slate-300 hover:text-white'
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
                {/* Notification Dropdown */}
                <div className="relative">
                  <button
                    onClick={() => setIsNotificationsOpen(!isNotificationsOpen)}
                    className="p-2 relative rounded-xl bg-dark-850 hover:bg-dark-800 border border-dark-750 text-slate-300 hover:text-white transition-colors flex items-center justify-center"
                    aria-label="Notifications"
                  >
                    <Bell className="w-4 h-4" />
                    {unreadCount > 0 && (
                      <span className="absolute top-1.5 right-1.5 w-2 h-2 rounded-full bg-sage-400"></span>
                    )}
                  </button>

                  {isNotificationsOpen && (
                    <div 
                      className="absolute right-0 mt-2 w-80 rounded-2xl bg-dark-900 border border-dark-750 p-2 shadow-modal z-50 animate-in fade-in zoom-in-95 duration-100"
                      onMouseLeave={() => setIsNotificationsOpen(false)}
                    >
                      <div className="px-3 py-2 border-b border-dark-750 mb-1 flex items-center justify-between">
                        <p className="text-xs font-semibold text-white">Notifications</p>
                        <button 
                          onClick={async () => {
                            await notificationsApi.markAllRead();
                            setNotifications(notifications.map(n => ({ ...n, is_read: true })));
                            setUnreadCount(0);
                          }}
                          className="text-[10px] text-sage-400 hover:text-sage-300 font-medium"
                        >
                          Mark all as read
                        </button>
                      </div>

                      <div className="max-h-64 overflow-y-auto pr-1">
                        <div className="flex flex-col gap-1">
                          {notifications.length > 0 ? (
                            notifications.map((notification) => (
                              <button 
                                key={notification.id}
                                onClick={async () => {
                                  if (!notification.is_read) {
                                    await notificationsApi.markRead(notification.id);
                                    setNotifications(notifications.map(n => n.id === notification.id ? { ...n, is_read: true } : n));
                                    setUnreadCount(prev => Math.max(0, prev - 1));
                                  }
                                  setIsNotificationsOpen(false);
                                  navigate('/notifications');
                                }}
                                className={`w-full flex items-start gap-3 px-3 py-2 text-left hover:bg-dark-850 rounded-xl transition-colors relative group ${notification.is_read ? 'opacity-70' : ''}`}
                              >
                                {notification.is_read ? (
                                  <div className="w-2 h-2 rounded-full bg-transparent border border-dark-600 shrink-0 mt-1.5" />
                                ) : (
                                  <div className="w-2 h-2 rounded-full bg-sage-400 shrink-0 mt-1.5" />
                                )}
                                <div>
                                  <p className="text-xs font-medium text-white mb-0.5 truncate">{notification.title}</p>
                                  <p className="text-[11px] text-slate-400 leading-relaxed line-clamp-2">{notification.message}</p>
                                  <p className="text-[10px] text-slate-500 mt-1">{new Date(notification.created_at).toLocaleDateString()}</p>
                                </div>
                              </button>
                            ))
                          ) : (
                            <p className="text-xs text-slate-500 text-center py-4">No notifications yet.</p>
                          )}
                        </div>
                      </div>
                      
                      <div className="mt-1 pt-1 border-t border-dark-750">
                        <button 
                          onClick={() => {
                            setIsNotificationsOpen(false);
                            navigate('/notifications');
                          }}
                          className="w-full text-center py-2 text-xs font-medium text-slate-300 hover:text-white hover:bg-dark-850 rounded-xl transition-colors"
                        >
                          View all notifications
                        </button>
                      </div>
                    </div>
                  )}
                </div>


                {role === UserRole.CUSTOMER && (
                  <button
                    onClick={() => navigate('/booking/new')}
                    className="btn-primary flex items-center gap-1.5"
                  >
                    <PlusCircle className="w-4 h-4" />
                    <span>Book Service</span>
                  </button>
                )}

                {/* Profile dropdown */}
                <div className="relative">
                  <button
                    onClick={() => setIsProfileOpen(!isProfileOpen)}
                    className="flex items-center gap-2.5 p-1.5 pr-3 rounded-xl bg-dark-850 hover:bg-dark-800 border border-dark-750 transition-colors"
                  >
                    <div className="w-8 h-8 rounded-lg bg-sage-400/15 border border-sage-400/30 flex items-center justify-center text-sage-400 text-xs font-bold">
                      {user.full_name?.charAt(0).toUpperCase() || 'U'}
                    </div>
                    <div className="text-left">
                      <p className="text-xs font-semibold text-white leading-none">{user.full_name || 'User'}</p>
                      <span className="text-[10px] font-mono text-sage-400">
                        {role.replace('ROLE_', '')}
                      </span>
                    </div>
                    <ChevronDown className="w-3.5 h-3.5 text-slate-400 ml-1" />
                  </button>

                  {isProfileOpen && (
                    <div 
                      className="absolute right-0 mt-2 w-56 rounded-2xl bg-dark-900 border border-dark-750 p-2 shadow-modal z-50 animate-in fade-in zoom-in-95 duration-100"
                      onMouseLeave={() => setIsProfileOpen(false)}
                    >
                      <div className="px-3 py-2 border-b border-dark-750 mb-1">
                        <p className="text-xs font-semibold text-white">{user.full_name}</p>
                        <p className="text-[11px] text-slate-400 truncate">{user.email}</p>
                      </div>

                      <button
                        onClick={() => {
                          setIsProfileOpen(false);
                          navigate(getDashboardPath());
                        }}
                        className="w-full flex items-center gap-2 px-3 py-2 text-xs font-medium text-slate-300 hover:text-white hover:bg-dark-850 rounded-xl transition-colors text-left"
                      >
                        <LayoutDashboard className="w-4 h-4 text-sage-400" />
                        <span>Dashboard</span>
                      </button>

                      <button
                        onClick={() => {
                          setIsProfileOpen(false);
                          navigate('/history');
                        }}
                        className="w-full flex items-center gap-2 px-3 py-2 text-xs font-medium text-slate-300 hover:text-white hover:bg-dark-850 rounded-xl transition-colors text-left mt-0.5"
                      >
                        <History className="w-4 h-4 text-sage-400" />
                        <span>History</span>
                      </button>

                      <button
                        onClick={() => {
                          setIsProfileOpen(false);
                          navigate('/reviews');
                        }}
                        className="w-full flex items-center gap-2 px-3 py-2 text-xs font-medium text-slate-300 hover:text-white hover:bg-dark-850 rounded-xl transition-colors text-left mt-0.5"
                      >
                        <Star className="w-4 h-4 text-sage-400" />
                        <span>Review</span>
                      </button>

                      {role !== UserRole.CUSTOMER && (
                        <button
                          onClick={() => {
                            setIsProfileOpen(false);
                            navigate('/analytics');
                          }}
                          className="w-full flex items-center gap-2 px-3 py-2 text-xs font-medium text-slate-300 hover:text-white hover:bg-dark-850 rounded-xl transition-colors text-left mt-0.5"
                        >
                          <BarChart3 className="w-4 h-4 text-sage-400" />
                          <span>Analytics</span>
                        </button>
                      )}

                      <div className="h-px bg-dark-750 my-1 mx-3" />

                      <button
                        onClick={handleLogout}
                        className="w-full flex items-center gap-2 px-3 py-2 text-xs font-medium text-rose-400 hover:bg-rose-500/10 rounded-xl transition-colors text-left mt-1"
                      >
                        <LogOut className="w-4 h-4" />
                        <span>Sign Out</span>
                      </button>
                    </div>
                  )}
                </div>
              </div>
            ) : (
              <div className="flex items-center gap-2.5">

                <Link
                  to="/login"
                  className="btn-secondary text-xs px-4 py-2"
                >
                  Sign In
                </Link>
                <Link
                  to="/register"
                  className="btn-primary text-xs px-4 py-2"
                >
                  Get Started
                </Link>
              </div>
            )}
          </div>

          {/* Mobile menu button */}
          <div className="md:hidden flex items-center gap-2">
            {isAuthenticated && (
              <button
                onClick={() => navigate(getDashboardPath())}
                className="p-2 rounded-xl bg-dark-850 border border-dark-750 text-slate-300"
              >
                <LayoutDashboard className="w-4 h-4" />
              </button>
            )}
            <button
              onClick={() => setIsMenuOpen(!isMenuOpen)}
              className="p-2 rounded-xl bg-dark-850 border border-dark-750 text-slate-300 hover:text-white"
              aria-label="Toggle Navigation"
            >
              {isMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile dropdown drawer */}
      {isMenuOpen && (
        <div className="md:hidden border-t border-dark-750 bg-white/95 dark:bg-dark-950/95 backdrop-blur-2xl px-4 pt-3 pb-6 space-y-2">
          {role !== UserRole.TECHNICIAN && (
            <Link
              to="/services"
              onClick={() => setIsMenuOpen(false)}
              className="flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium text-slate-200 hover:bg-dark-850"
            >
              <Layers className="w-4 h-4 text-sage-400" />
              <span>Services</span>
            </Link>
          )}
          {role !== UserRole.TECHNICIAN && (
            <Link
              to="/jobs"
              onClick={() => setIsMenuOpen(false)}
              className="flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium text-slate-200 hover:bg-dark-850"
            >
              <Briefcase className="w-4 h-4 text-sage-400" />
              <span>Recruitment</span>
            </Link>
          )}
          {isAuthenticated ? (
            <>
              <Link
                to={getDashboardPath()}
                onClick={() => setIsMenuOpen(false)}
                className="flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium text-slate-200 hover:bg-dark-850"
              >
                <LayoutDashboard className="w-4 h-4 text-sage-400" />
                <span>Dashboard</span>
              </Link>
              <button
                onClick={handleLogout}
                className="w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium text-rose-400 hover:bg-rose-500/10 text-left"
              >
                <LogOut className="w-4 h-4" />
                <span>Sign Out</span>
              </button>
            </>
          ) : (
            <div className="pt-3 flex flex-col gap-2 border-t border-dark-750">
              <Link
                to="/login"
                onClick={() => setIsMenuOpen(false)}
                className="btn-secondary text-center text-xs py-2.5"
              >
                Sign In
              </Link>
              <Link
                to="/register"
                onClick={() => setIsMenuOpen(false)}
                className="btn-primary text-center text-xs py-2.5"
              >
                Get Started
              </Link>
            </div>
          )}
        </div>
      )}
    </nav>
  );
};
