import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { 
  Home, 
  Layers, 
  PlusCircle, 
  Briefcase, 
  LayoutDashboard, 
  UserCheck,
  Wrench,
  Bell,
  History,
  Star
} from 'lucide-react';
import { useAuthStore } from '../../store/useAuthStore';
import { UserRole } from '../../types';

export const MobileBottomNav: React.FC = () => {
  const { isAuthenticated, getEffectiveRole } = useAuthStore();
  const navigate = useNavigate();
  const location = useLocation();
  const role = getEffectiveRole();

  const isCurrent = (path: string) => location.pathname === path;

  // Technicians have a strictly technical workflow mobile bar
  if (isAuthenticated && role === UserRole.TECHNICIAN) {
    return (
      <div className="md:hidden fixed bottom-0 left-0 right-0 z-50 bg-white/95 backdrop-blur-2xl border-t border-slate-200 px-4 py-2 shadow-lg">
        <div className="flex items-center justify-around">
          <button
            onClick={() => navigate('/provider/dashboard')}
            className={`flex flex-col items-center gap-1 py-1 px-3 rounded-xl transition-colors ${
              location.pathname.includes('/provider/dashboard') ? 'text-sage-600 font-semibold' : 'text-slate-500 hover:text-slate-800'
            }`}
          >
            <Wrench className="w-5 h-5" />
            <span className="text-[10px] font-medium">Workspace</span>
          </button>

          <button
            onClick={() => navigate('/notifications')}
            className={`flex flex-col items-center gap-1 py-1 px-3 rounded-xl transition-colors ${
              isCurrent('/notifications') ? 'text-sage-600 font-semibold' : 'text-slate-500 hover:text-slate-800'
            }`}
          >
            <Bell className="w-5 h-5" />
            <span className="text-[10px] font-medium">Alerts</span>
          </button>

          <button
            onClick={() => navigate('/history')}
            className={`flex flex-col items-center gap-1 py-1 px-3 rounded-xl transition-colors ${
              isCurrent('/history') ? 'text-sage-600 font-semibold' : 'text-slate-500 hover:text-slate-800'
            }`}
          >
            <History className="w-5 h-5" />
            <span className="text-[10px] font-medium">Missions</span>
          </button>

          <button
            onClick={() => navigate('/reviews')}
            className={`flex flex-col items-center gap-1 py-1 px-3 rounded-xl transition-colors ${
              isCurrent('/reviews') ? 'text-sage-600 font-semibold' : 'text-slate-500 hover:text-slate-800'
            }`}
          >
            <Star className="w-5 h-5" />
            <span className="text-[10px] font-medium">Ratings</span>
          </button>
        </div>
      </div>
    );
  }

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

  return (
    <div className="md:hidden fixed bottom-0 left-0 right-0 z-50 bg-dark-950/90 backdrop-blur-2xl border-t border-dark-750 px-4 py-2">
      <div className="flex items-center justify-around">
        <button
          onClick={() => navigate('/')}
          className={`flex flex-col items-center gap-1 py-1 px-2 rounded-xl transition-colors ${
            isCurrent('/') ? 'text-sage-400' : 'text-slate-400 hover:text-slate-200'
          }`}
        >
          <Home className="w-5 h-5" />
          <span className="text-[10px] font-medium">Home</span>
        </button>

        {role !== UserRole.TECHNICIAN && (
          <button
            onClick={() => navigate('/services')}
            className={`flex flex-col items-center gap-1 py-1 px-2 rounded-xl transition-colors ${
              isCurrent('/services') ? 'text-sage-400' : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <Layers className="w-5 h-5" />
            <span className="text-[10px] font-medium">Services</span>
          </button>
        )}

        {role === UserRole.CUSTOMER && (
          <button
            onClick={() => navigate('/booking/new')}
            className="flex flex-col items-center gap-1 -mt-5"
          >
            <div className="w-11 h-11 rounded-full bg-sage-400 text-dark-950 flex items-center justify-center shadow-accent ring-4 ring-dark-950">
              <PlusCircle className="w-6 h-6 stroke-[2.5]" />
            </div>
            <span className="text-[10px] font-semibold text-white mt-0.5">Book</span>
          </button>
        )}

        <button
          onClick={() => navigate('/jobs')}
          className={`flex flex-col items-center gap-1 py-1 px-2 rounded-xl transition-colors ${
            isCurrent('/jobs') ? 'text-sage-400' : 'text-slate-400 hover:text-slate-200'
          }`}
        >
          <Briefcase className="w-5 h-5" />
          <span className="text-[10px] font-medium">Careers</span>
        </button>

        {isAuthenticated ? (
          <button
            onClick={() => navigate(getDashboardPath())}
            className={`flex flex-col items-center gap-1 py-1 px-2 rounded-xl transition-colors ${
              location.pathname.includes('dashboard') ? 'text-sage-400' : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <LayoutDashboard className="w-5 h-5" />
            <span className="text-[10px] font-medium">Dashboard</span>
          </button>
        ) : (
          <button
            onClick={() => navigate('/login')}
            className="flex flex-col items-center gap-1 py-1 px-2 rounded-xl text-slate-400 hover:text-slate-200"
          >
            <UserCheck className="w-5 h-5" />
            <span className="text-[10px] font-medium">Sign In</span>
          </button>
        )}
      </div>
    </div>
  );
};
