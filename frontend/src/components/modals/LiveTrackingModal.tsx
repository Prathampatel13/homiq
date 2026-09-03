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
import { GoogleMap, useJsApiLoader, Marker } from '@react-google-maps/api';

export interface LiveTrackingModalProps {
  booking: Booking | null;
  isOpen: boolean;
  onClose: () => void;
}

const mapStyles = [
  { elementType: "geometry", stylers: [{ color: "#1e293b" }] },
  { elementType: "labels.text.stroke", stylers: [{ color: "#1e293b" }] },
  { elementType: "labels.text.fill", stylers: [{ color: "#94a3b8" }] },
  { featureType: "administrative.locality", elementType: "labels.text.fill", stylers: [{ color: "#cbd5e1" }] },
  { featureType: "poi", elementType: "labels.text.fill", stylers: [{ color: "#94a3b8" }] },
  { featureType: "poi.park", elementType: "geometry", stylers: [{ color: "#0f172a" }] },
  { featureType: "poi.park", elementType: "labels.text.fill", stylers: [{ color: "#64748b" }] },
  { featureType: "road", elementType: "geometry", stylers: [{ color: "#334155" }] },
  { featureType: "road", elementType: "geometry.stroke", stylers: [{ color: "#1e293b" }] },
  { featureType: "road", elementType: "labels.text.fill", stylers: [{ color: "#94a3b8" }] },
  { featureType: "road.highway", elementType: "geometry", stylers: [{ color: "#475569" }] },
  { featureType: "road.highway", elementType: "geometry.stroke", stylers: [{ color: "#1e293b" }] },
  { featureType: "road.highway", elementType: "labels.text.fill", stylers: [{ color: "#f3f4f6" }] },
  { featureType: "transit", elementType: "geometry", stylers: [{ color: "#1e293b" }] },
  { featureType: "transit.station", elementType: "labels.text.fill", stylers: [{ color: "#cbd5e1" }] },
  { featureType: "water", elementType: "geometry", stylers: [{ color: "#0f172a" }] },
  { featureType: "water", elementType: "labels.text.fill", stylers: [{ color: "#475569" }] },
  { featureType: "water", elementType: "labels.text.stroke", stylers: [{ color: "#1e293b" }] }
];

const containerStyle = {
  width: '100%',
  height: '100%'
};

export const LiveTrackingModal: React.FC<LiveTrackingModalProps> = ({ booking, isOpen, onClose }) => {
  const { isLoaded } = useJsApiLoader({
    id: 'google-map-script',
    googleMapsApiKey: import.meta.env.VITE_GOOGLE_MAPS_API_KEY || ''
  });

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

  const defaultCenter = { lat: 28.6139, lng: 77.2090 }; // Default to New Delhi
  
  const homeLocation = React.useMemo(() => {
    if (booking?.address?.latitude && booking?.address?.longitude) {
      return { lat: booking.address.latitude, lng: booking.address.longitude };
    }
    return defaultCenter;
  }, [booking?.address]);

  const techLocation = React.useMemo(() => {
    if ((booking?.technician as any)?.latitude && (booking?.technician as any)?.longitude) {
      return { lat: (booking.technician as any).latitude, lng: (booking.technician as any).longitude };
    }
    return { lat: homeLocation.lat - 0.02, lng: homeLocation.lng - 0.02 };
  }, [booking?.technician, homeLocation]);

  if (!isOpen || !booking) return null;

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
        <div className="md:col-span-2 relative h-64 md:h-full min-h-[300px] rounded-2xl overflow-hidden bg-dark-950 border border-dark-750 flex flex-col">
          {!isLoaded ? (
            <div className="flex-1 flex items-center justify-center text-sage-400/50 animate-pulse font-mono text-sm">
              INITIALIZING RADAR...
            </div>
          ) : (
            <GoogleMap
              mapContainerStyle={containerStyle}
              center={homeLocation}
              zoom={13}
              options={{
                styles: mapStyles,
                disableDefaultUI: true,
                zoomControl: true,
              }}
            >
              {/* Home Marker */}
              <Marker 
                position={homeLocation} 
                icon={{
                  path: "M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z",
                  fillColor: "#4ade80",
                  fillOpacity: 1,
                  strokeWeight: 1,
                  strokeColor: "#22c55e",
                  scale: 1.5,
                  anchor: new window.google.maps.Point(12, 24),
                }} 
              />
              
              {/* Technician Marker */}
              <Marker 
                position={techLocation} 
                icon={{
                  path: "M18.92 6.01C18.72 5.42 18.16 5 17.5 5h-11c-.66 0-1.21.42-1.42 1.01L3 12v8c0 .55.45 1 1 1h1c.55 0 1-.45 1-1v-1h12v1c0 .55.45 1 1 1h1c.55 0 1-.45 1-1v-8l-2.08-5.99zM6.5 16c-.83 0-1.5-.67-1.5-1.5S5.67 13 6.5 13s1.5.67 1.5 1.5S7.33 16 6.5 16zm11 0c-.83 0-1.5-.67-1.5-1.5s.67-1.5 1.5-1.5 1.5.67 1.5 1.5-.67 1.5-1.5 1.5zM5 11l1.5-4.5h11L19 11H5z",
                  fillColor: "#94a3b8",
                  fillOpacity: 1,
                  strokeWeight: 1,
                  strokeColor: "#475569",
                  scale: 1.2,
                  anchor: new window.google.maps.Point(12, 12),
                }} 
              />
            </GoogleMap>
          )}

          {/* Overlay Status Box */}
          <div className="absolute top-4 left-4 p-3 rounded-xl bg-dark-900/90 backdrop-blur border border-dark-750 shadow-lg z-10">
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
