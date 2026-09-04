import React, { useState, useEffect, useMemo } from 'react';
import { 
  MapPin, 
  Navigation2, 
  Phone, 
  MessageSquare, 
  ShieldCheck, 
  Clock, 
  Car,
  CheckCircle2
} from 'lucide-react';
import { Booking } from '../../types';
import { BookingMediaSection } from '../media/BookingMediaSection';
import { GoogleMap, useJsApiLoader, Marker } from '@react-google-maps/api';

export interface LiveTrackingWidgetProps {
  booking: Booking;
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

export const LiveTrackingWidget: React.FC<LiveTrackingWidgetProps> = ({ booking }) => {
  const { isLoaded } = useJsApiLoader({
    id: 'google-map-script',
    googleMapsApiKey: import.meta.env.VITE_GOOGLE_MAPS_API_KEY || ''
  });

  const [progress, setProgress] = useState(0);

  // Status mapping
  const statusLevels = {
    pending: 1,
    assigned: 2,
    accepted: 2,
    on_the_way: 3,
    arrived: 4,
    waiting_qr: 4,
    qr_verified: 4,
    in_progress: 5,
    completed: 6,
    cancelled: -1,
    rejected: -1
  };
  
  const currentLevel = statusLevels[booking.status as keyof typeof statusLevels] || 1;

  useEffect(() => {
    // If on the way, simulate moving
    if (currentLevel === 3) {
      setProgress(10);
      const interval = setInterval(() => {
        setProgress(prev => {
          if (prev >= 90) {
            clearInterval(interval);
            return 90;
          }
          return prev + 2;
        });
      }, 500);
      return () => clearInterval(interval);
    } else if (currentLevel > 3) {
      setProgress(100);
    } else {
      setProgress(0);
    }
  }, [currentLevel]);

  const steps = [
    { title: 'Booking Confirmed', done: currentLevel >= 1, active: currentLevel === 1 },
    { title: 'Technician Assigned', done: currentLevel >= 2, active: currentLevel === 2 },
    { title: 'En Route', done: currentLevel >= 3, active: currentLevel === 3 },
    { title: 'Arrived', done: currentLevel >= 4, active: currentLevel === 4 },
    { title: 'Service Started', done: currentLevel >= 5, active: currentLevel === 5 },
    { title: 'Completed', done: currentLevel >= 6, active: currentLevel === 6 }
  ];

  const getTechName = (tech: any) => {
    if (!tech) return 'Unassigned';
    if (typeof tech.full_name === 'string') return tech.full_name;
    if (tech.user?.full_name) return tech.user.full_name;
    return 'Master Technician';
  };

  const getTechPhone = (tech: any) => {
    if (!tech) return '';
    if (typeof tech.phone_number === 'string' && tech.phone_number.trim() !== '') return tech.phone_number;
    if (tech.user?.phone_number && tech.user.phone_number.trim() !== '') return tech.user.phone_number;
    return '+1234567890';
  };

  const technicianUserId = (booking.technician as any)?.user_id || (booking.technician as any)?.id;

  const defaultCenter = { lat: 28.6139, lng: 77.2090 }; // Default to New Delhi if missing
  
  const homeLocation = useMemo(() => {
    if (booking.address?.latitude && booking.address?.longitude) {
      return { lat: booking.address.latitude, lng: booking.address.longitude };
    }
    return defaultCenter;
  }, [booking.address]);

  const techLocation = useMemo(() => {
    if ((booking.technician as any)?.latitude && (booking.technician as any)?.longitude) {
      return { lat: (booking.technician as any).latitude, lng: (booking.technician as any).longitude };
    }
    // Simulate technician slightly offset from home if no location yet
    return { lat: homeLocation.lat - 0.02, lng: homeLocation.lng - 0.02 };
  }, [booking.technician, homeLocation]);

  return (
    <div className="w-full bg-dark-900 border border-dark-750 rounded-3xl overflow-hidden shadow-card mb-8">
      <div className="grid grid-cols-1 lg:grid-cols-3">
        
        {/* Map Area */}
        <div className="lg:col-span-2 relative h-[400px] lg:h-auto min-h-[400px] bg-dark-950 flex flex-col overflow-hidden border-b lg:border-b-0 lg:border-r border-dark-750">
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
              
              {/* Technician Marker (Only show if assigned) */}
              {currentLevel >= 2 && currentLevel < 6 && (
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
              )}
            </GoogleMap>
          )}


        </div>

        {/* Sidebar Tracking Info */}
        <div className="flex flex-col h-full bg-gradient-to-b from-dark-900 to-dark-950/50 border-l border-dark-750">
          <div className="p-6 sm:p-8 flex-1">
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
                    {booking.technician && <ShieldCheck className="w-4 h-4 text-sage-400" />}
                  </h4>
                  {booking.technician && (
                    <div className="flex items-center gap-2 mt-1 text-xs text-slate-400 font-mono">
                      <span className="bg-dark-900 px-2 py-0.5 rounded text-sage-400">{(booking.technician as any).rating || '4.9'}★</span>
                      <span>{(booking.technician as any).jobs_completed || '142'} Jobs</span>
                    </div>
                  )}
                </div>
              </div>
              <div className="flex gap-3">
                {booking.technician ? (
                  <a href={`tel:${getTechPhone(booking.technician)}`} className="flex-1 py-2.5 rounded-xl bg-dark-800 hover:bg-dark-750 border border-dark-700 text-xs font-bold text-white transition-colors flex items-center justify-center gap-2">
                    <Phone className="w-4 h-4" />
                    {getTechPhone(booking.technician)}
                  </a>
                ) : (
                  <button className="flex-1 py-2.5 rounded-xl bg-dark-800 hover:bg-dark-750 border border-dark-700 text-xs font-bold text-white transition-colors flex items-center justify-center gap-2 disabled:opacity-50" disabled={true}>
                    <Phone className="w-4 h-4" />
                    Call Tech
                  </button>
                )}
                <button className="flex-1 py-2.5 rounded-xl bg-sage-400/10 hover:bg-sage-400/20 border border-sage-400/20 text-xs font-bold text-sage-400 transition-colors flex items-center justify-center gap-2 disabled:opacity-50" disabled={!booking.technician}>
                  <MessageSquare className="w-4 h-4" />
                  Message
                </button>
              </div>
            </div>

            {/* Timeline */}
            <div className="flex-1 relative pl-4 mt-2 mb-6">
              <div className="absolute top-2 bottom-2 left-[19px] w-[2px] bg-dark-750 rounded-full" />
              <div className="space-y-6 relative">
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
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
      
      {/* Work Evidence Section integrated smoothly at the bottom */}
      <div className="border-t border-dark-750 bg-dark-950/50 p-6 sm:p-8">
        <BookingMediaSection 
          bookingId={booking.id} 
          assignedTechnicianId={technicianUserId} 
        />
      </div>
    </div>
  );
};
