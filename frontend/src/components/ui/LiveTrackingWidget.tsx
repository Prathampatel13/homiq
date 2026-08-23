import React, { useState, useEffect } from 'react';
import { 
  MapPin, 
  Navigation2, 
  Phone, 
  MessageSquare, 
  ShieldCheck, 
  Clock, 
  Car
} from 'lucide-react';
import { Booking } from '../../types';

export interface LiveTrackingWidgetProps {
  booking: Booking;
}

export const LiveTrackingWidget: React.FC<LiveTrackingWidgetProps> = ({ booking }) => {
  const [progress, setProgress] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setProgress(prev => {
        if (prev >= 95) {
          clearInterval(interval);
          return 100;
        }
        return prev + 1;
      });
    }, 300);

    return () => clearInterval(interval);
  }, []);

  const steps = [
    { title: 'Booking Confirmed', time: '09:00 AM', done: true },
    { title: 'Technician Assigned', time: '09:15 AM', done: true },
    { title: 'En Route to Location', time: '09:30 AM', done: true, active: progress < 100 },
    { title: 'Arrived at Destination', time: 'ETA 09:45 AM', done: progress === 100 }
  ];

  const getTechName = (tech: any) => {
    if (!tech) return 'Unassigned';
    if (typeof tech.full_name === 'string') return tech.full_name;
    if (tech.user?.full_name) return tech.user.full_name;
    return 'Master Technician';
  };

  return (
    <div className="w-full bg-dark-900 border border-dark-750 rounded-3xl overflow-hidden shadow-card mb-8">
      <div className="grid grid-cols-1 lg:grid-cols-3">
        
        {/* Map Area */}
        <div className="lg:col-span-2 relative h-64 lg:h-auto min-h-[350px] bg-dark-950 flex items-center justify-center overflow-hidden border-b lg:border-b-0 lg:border-r border-dark-750">
          {/* Simulated Map Background */}
          <div className="absolute inset-0 bg-[linear-gradient(to_right,#1e293b_1px,transparent_1px),linear-gradient(to_bottom,#1e293b_1px,transparent_1px)] bg-[size:2rem_2rem] [mask-image:radial-gradient(ellipse_80%_80%_at_50%_50%,#000_70%,transparent_100%)] opacity-30"></div>
          
          {/* Map Route Line */}
          <div className="absolute top-1/2 left-[15%] right-[15%] h-1.5 bg-dark-800 rounded-full overflow-hidden transform -translate-y-1/2">
            <div 
              className="h-full bg-sage-500 transition-all duration-300 ease-linear shadow-[0_0_10px_rgba(74,222,128,0.5)]"
              style={{ width: `${progress}%` }}
            />
          </div>

          {/* Starting Point */}
          <div className="absolute top-1/2 left-[15%] transform -translate-x-1/2 -translate-y-1/2 flex flex-col items-center">
            <div className="w-5 h-5 bg-dark-800 border-4 border-slate-600 rounded-full z-10" />
            <span className="text-xs font-mono font-bold text-slate-400 mt-3 bg-dark-950/90 px-3 py-1.5 rounded-lg border border-dark-800 shadow-sm backdrop-blur-sm">Dispatch</span>
          </div>

          {/* Moving Vehicle */}
          <div 
            className="absolute top-1/2 transform -translate-y-1/2 z-20 transition-all duration-300 ease-linear"
            style={{ left: `calc(15% + (${progress} * 0.7%))` }}
          >
            <div className="relative">
              <div className="absolute -inset-2 bg-sage-400/20 rounded-full blur-md animate-pulse"></div>
              <div className="relative w-10 h-10 bg-sage-400 text-dark-950 rounded-full flex items-center justify-center shadow-[0_0_20px_rgba(74,222,128,0.4)] ring-4 ring-dark-950">
                <Car className="w-5 h-5" />
              </div>
            </div>
          </div>

          {/* Destination */}
          <div className="absolute top-1/2 right-[15%] transform translate-x-1/2 -translate-y-1/2 flex flex-col items-center">
            <div className="w-7 h-7 bg-dark-800 border-4 border-sage-400 rounded-full z-10 flex items-center justify-center shadow-[0_0_15px_rgba(74,222,128,0.2)]">
              <div className="w-2 h-2 bg-sage-400 rounded-full" />
            </div>
            <span className="text-xs font-mono font-bold text-sage-400 mt-3 bg-dark-950/90 px-3 py-1.5 rounded-lg border border-sage-400/30 shadow-sm backdrop-blur-sm">Your Home</span>
          </div>

          {/* Overlay Status Box */}
          <div className="absolute top-5 left-5 p-4 rounded-2xl bg-dark-900/95 backdrop-blur-md border border-dark-750 shadow-xl">
            <div className="flex items-center gap-2.5 mb-1.5">
              <div className="w-2 h-2 rounded-full bg-sage-400 animate-pulse" />
              <span className="text-sm font-bold text-white tracking-wide uppercase">Live Tracking</span>
            </div>
            <div className="text-xs font-mono text-slate-400">
              {progress < 100 ? `${15 - Math.floor(progress * 0.15)} MINS AWAY` : 'ARRIVED'}
            </div>
          </div>
        </div>

        {/* Sidebar Tracking Info */}
        <div className="p-6 sm:p-8 flex flex-col h-full bg-gradient-to-b from-dark-900 to-dark-950/50">
          <h3 className="text-lg font-bold text-white tracking-tight mb-1">Dispatch Details</h3>
          <p className="text-xs text-slate-400 mb-6 pb-6 border-b border-dark-750">Order #{booking.id.toString().padStart(5, '0')}</p>

          {/* Technician Profile Card */}
          <div className="p-4 rounded-2xl bg-dark-850/80 border border-dark-750 mb-8 shadow-inner">
            <div className="flex items-center gap-4 mb-4">
              <div className="w-14 h-14 rounded-full bg-dark-800 border-2 border-dark-700 flex items-center justify-center shrink-0">
                <span className="text-xl font-bold text-sage-400">{getTechName(booking.technician).charAt(0)}</span>
              </div>
              <div>
                <h4 className="text-base font-bold text-white flex items-center gap-1.5">
                  {getTechName(booking.technician)}
                  <ShieldCheck className="w-4 h-4 text-sage-400" />
                </h4>
                <div className="flex items-center gap-2 mt-1 text-xs text-slate-400 font-mono">
                  <span className="bg-dark-900 px-2 py-0.5 rounded text-sage-400">4.9★</span>
                  <span>142 Jobs</span>
                </div>
              </div>
            </div>
            <div className="flex gap-3">
              <button className="flex-1 py-2.5 rounded-xl bg-dark-800 hover:bg-dark-750 border border-dark-700 text-xs font-bold text-white transition-colors flex items-center justify-center gap-2">
                <Phone className="w-4 h-4" />
                Call Tech
              </button>
              <button className="flex-1 py-2.5 rounded-xl bg-sage-400/10 hover:bg-sage-400/20 border border-sage-400/20 text-xs font-bold text-sage-400 transition-colors flex items-center justify-center gap-2">
                <MessageSquare className="w-4 h-4" />
                Message
              </button>
            </div>
          </div>

          {/* Timeline */}
          <div className="flex-1 relative pl-4 mt-2">
            <div className="absolute top-2 bottom-2 left-[19px] w-[2px] bg-dark-750 rounded-full" />
            <div className="space-y-7 relative">
              {steps.map((step, idx) => (
                <div key={idx} className="flex gap-5 items-start relative group">
                  <div className={`w-3 h-3 mt-1.5 rounded-full shrink-0 relative z-10 transition-colors duration-300 ${
                    step.active ? 'bg-sage-400 ring-4 ring-sage-400/20 shadow-[0_0_15px_rgba(74,222,128,0.5)]' : 
                    step.done ? 'bg-sage-500/80 border-2 border-dark-900' : 'bg-dark-700 border-2 border-dark-900'
                  }`} />
                  <div>
                    <h5 className={`text-sm font-bold transition-colors ${step.active ? 'text-sage-400' : step.done ? 'text-white' : 'text-slate-600'}`}>
                      {step.title}
                    </h5>
                    <div className={`flex items-center gap-1.5 mt-1.5 text-xs font-mono ${step.active ? 'text-slate-300' : 'text-slate-500'}`}>
                      <Clock className="w-3.5 h-3.5" />
                      {step.time}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

      </div>
    </div>
  );
};
