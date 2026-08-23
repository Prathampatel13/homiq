import React, { useState, useEffect } from 'react';
import { 
  X, 
  MapPin, 
  Navigation2, 
  Phone, 
  MessageSquare, 
  ShieldCheck, 
  Clock, 
  CheckCircle2,
  Car
} from 'lucide-react';
import { Booking } from '../../types';

export interface LiveTrackingModalProps {
  booking: Booking | null;
  isOpen: boolean;
  onClose: () => void;
}

export const LiveTrackingModal: React.FC<LiveTrackingModalProps> = ({ booking, isOpen, onClose }) => {
  const [progress, setProgress] = useState(0);

  // Simulate vehicle movement
  useEffect(() => {
    if (!isOpen) {
      setProgress(0);
      return;
    }
    
    // Simulate technician moving towards destination
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
  }, [isOpen]);

  if (!isOpen || !booking) return null;

  // Assuming status is 'on_the_way' or similar, we calculate steps
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
    <div className="fixed inset-0 z-[60] flex items-center justify-center p-4 bg-dark-950/85 backdrop-blur-md animate-in fade-in duration-150">
      <div className="relative w-full max-w-4xl rounded-3xl bg-dark-900 border border-dark-750 p-6 sm:p-8 shadow-modal text-white max-h-[90vh] overflow-y-auto grid grid-cols-1 md:grid-cols-3 gap-6">
        
        {/* Close Button */}
        <button
          onClick={onClose}
          className="absolute top-5 right-5 p-2 rounded-xl bg-dark-850 hover:bg-dark-800 text-slate-400 hover:text-white border border-dark-750 transition-colors z-10"
        >
          <X className="w-4 h-4" />
        </button>

        {/* Map Area (Left side, takes 2 columns on desktop) */}
        <div className="md:col-span-2 relative h-64 md:h-full min-h-[300px] rounded-2xl overflow-hidden bg-dark-950 border border-dark-750 flex items-center justify-center">
          {/* Simulated Map Background Grid */}
          <div className="absolute inset-0 bg-[linear-gradient(to_right,#1e293b_1px,transparent_1px),linear-gradient(to_bottom,#1e293b_1px,transparent_1px)] bg-[size:2rem_2rem] [mask-image:radial-gradient(ellipse_60%_60%_at_50%_50%,#000_70%,transparent_100%)] opacity-20"></div>
          
          {/* Map Route Line */}
          <div className="absolute top-1/2 left-1/4 right-1/4 h-1 bg-dark-750 rounded-full overflow-hidden transform -translate-y-1/2">
            <div 
              className="h-full bg-sage-400 transition-all duration-300 ease-linear"
              style={{ width: `${progress}%` }}
            />
          </div>

          {/* Starting Point */}
          <div className="absolute top-1/2 left-1/4 transform -translate-x-1/2 -translate-y-1/2 flex flex-col items-center">
            <div className="w-4 h-4 bg-dark-800 border-2 border-slate-500 rounded-full z-10" />
            <span className="text-[10px] font-mono text-slate-400 mt-2 bg-dark-950/80 px-2 py-1 rounded">Depot</span>
          </div>

          {/* Moving Vehicle */}
          <div 
            className="absolute top-1/2 transform -translate-y-1/2 z-20 transition-all duration-300 ease-linear"
            style={{ left: `calc(25% + (${progress} * 0.5%))` }}
          >
            <div className="w-8 h-8 bg-sage-400 text-dark-950 rounded-full flex items-center justify-center shadow-[0_0_15px_rgba(74,222,128,0.3)] animate-pulse">
              <Car className="w-4 h-4" />
            </div>
          </div>

          {/* Destination */}
          <div className="absolute top-1/2 right-1/4 transform translate-x-1/2 -translate-y-1/2 flex flex-col items-center">
            <div className="w-6 h-6 bg-dark-800 border-2 border-sage-400 rounded-full z-10 flex items-center justify-center">
              <MapPin className="w-3 h-3 text-sage-400" />
            </div>
            <span className="text-[10px] font-mono text-sage-400 mt-2 bg-dark-950/80 px-2 py-1 rounded border border-sage-400/20">Destination</span>
          </div>

          {/* Overlay Status Box */}
          <div className="absolute top-4 left-4 p-3 rounded-xl bg-dark-900/90 backdrop-blur border border-dark-750 shadow-lg">
            <div className="flex items-center gap-2 mb-1">
              <Navigation2 className="w-4 h-4 text-sage-400" />
              <span className="text-xs font-bold text-white tracking-wide">LIVE GPS</span>
            </div>
            <div className="text-[10px] font-mono text-slate-400">
              {progress < 100 ? `${15 - Math.floor(progress * 0.15)} mins away` : 'Arrived'}
            </div>
          </div>
        </div>

        {/* Sidebar Tracking Info */}
        <div className="flex flex-col h-full">
          <h3 className="text-xl font-bold text-white tracking-tight mb-1">Dispatch Tracker</h3>
          <p className="text-xs text-slate-400 mb-6">Real-time technician tracking & ETA</p>

          {/* Technician Profile Card */}
          <div className="p-4 rounded-2xl bg-dark-850 border border-dark-750 mb-6">
            <div className="flex items-center gap-4 mb-4">
              <div className="w-12 h-12 rounded-full bg-dark-800 border-2 border-dark-700 flex items-center justify-center shrink-0">
                <span className="text-lg font-bold text-sage-400">{getTechName(booking.technician).charAt(0)}</span>
              </div>
              <div>
                <h4 className="text-sm font-bold text-white flex items-center gap-1.5">
                  {getTechName(booking.technician)}
                  <ShieldCheck className="w-3.5 h-3.5 text-sage-400" />
                </h4>
                <div className="flex items-center gap-2 mt-0.5 text-xs text-slate-400 font-mono">
                  <span>4.9★</span>
                  <span>•</span>
                  <span>142 Jobs</span>
                </div>
              </div>
            </div>
            <div className="flex gap-2">
              <button className="flex-1 py-2 rounded-xl bg-dark-800 hover:bg-dark-750 border border-dark-750 text-xs font-semibold text-white transition-colors flex items-center justify-center gap-1.5">
                <Phone className="w-3.5 h-3.5" />
                Call
              </button>
              <button className="flex-1 py-2 rounded-xl bg-dark-800 hover:bg-dark-750 border border-dark-750 text-xs font-semibold text-white transition-colors flex items-center justify-center gap-1.5">
                <MessageSquare className="w-3.5 h-3.5" />
                Chat
              </button>
            </div>
          </div>

          {/* Timeline */}
          <div className="flex-1 relative pl-3">
            <div className="absolute top-0 bottom-0 left-[15px] w-px bg-dark-750" />
            <div className="space-y-6 relative">
              {steps.map((step, idx) => (
                <div key={idx} className="flex gap-4 items-start relative">
                  <div className={`w-2 h-2 mt-1.5 rounded-full shrink-0 relative z-10 ${
                    step.active ? 'bg-sage-400 shadow-[0_0_10px_rgba(74,222,128,0.5)]' : 
                    step.done ? 'bg-sage-500' : 'bg-dark-700'
                  }`} />
                  <div>
                    <h5 className={`text-sm font-semibold ${step.active || step.done ? 'text-white' : 'text-slate-500'}`}>
                      {step.title}
                    </h5>
                    <div className="flex items-center gap-1 mt-1 text-[11px] font-mono text-slate-400">
                      <Clock className="w-3 h-3" />
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
