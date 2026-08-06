import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { Wrench, CheckCircle2, Clock, MapPin, QrCode, Power, Navigation, DollarSign } from 'lucide-react';
import { bookingApi } from '../api/booking';
import { useAuthStore } from '../store/useAuthStore';
import { Booking, BookingStatus } from '../types';
import { Card } from '../components/ui/Card';
import { Badge } from '../components/ui/Badge';
import { Button } from '../components/ui/Button';

export const ProviderDashboard: React.FC = () => {
  const { user } = useAuthStore();
  const [isOnline, setIsOnline] = useState(true);
  const [assignedBookings, setAssignedBookings] = useState<Booking[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [qrInput, setQrInput] = useState('');
  const [activeQRModalBookingId, setActiveQRModalBookingId] = useState<number | null>(null);
  const [statusMessage, setStatusMessage] = useState('');

  useEffect(() => {
    fetchTechnicianJobs();
  }, []);

  const fetchTechnicianJobs = async () => {
    setIsLoading(true);
    try {
      const data = await bookingApi.getTechnicianBookings();
      setAssignedBookings(data);
    } catch (err) {
      console.error('Failed to fetch technician jobs', err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleAcceptJob = async (bookingId: number) => {
    try {
      await bookingApi.acceptBooking(bookingId);
      fetchTechnicianJobs();
    } catch (err) {
      console.error('Failed to accept job', err);
    }
  };

  const handleUpdateStatus = async (bookingId: number, nextStatus: BookingStatus) => {
    try {
      await bookingApi.updateBookingStatus(bookingId, nextStatus);
      fetchTechnicianJobs();
    } catch (err) {
      console.error('Failed to update status', err);
    }
  };

  const handleVerifyQRSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!activeQRModalBookingId || !qrInput) return;

    try {
      const result = await bookingApi.verifyQR(activeQRModalBookingId, qrInput);
      setStatusMessage(result.message || 'QR verified successfully!');
      setActiveQRModalBookingId(null);
      setQrInput('');
      fetchTechnicianJobs();
    } catch (err: any) {
      setStatusMessage(err.response?.data?.detail || 'Invalid QR code.');
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-10">
      {/* ── 1. Header & Online Toggle ────────────────────────────────────────── */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 glass-card p-8 border-brand-500/20">
        <div className="space-y-2">
          <div className="flex items-center gap-3">
            <h1 className="text-3xl font-extrabold text-white">Technician Portal</h1>
            <span className="px-3 py-1 rounded-full bg-emerald-500/10 text-emerald-400 text-xs font-semibold border border-emerald-500/20">
              PRO PARTNER
            </span>
          </div>
          <p className="text-slate-400 text-sm">Welcome back, {user?.full_name}. Manage active job requests and earnings.</p>
        </div>

        <button
          onClick={() => setIsOnline(!isOnline)}
          className={`flex items-center gap-3 px-5 py-3 rounded-2xl border transition-all duration-300 ${
            isOnline
              ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400 shadow-lg shadow-emerald-500/10'
              : 'bg-slate-900 border-slate-800 text-slate-500'
          }`}
        >
          <Power className={`w-5 h-5 ${isOnline ? 'text-emerald-400 animate-pulse' : 'text-slate-500'}`} />
          <div className="text-left">
            <div className="text-xs font-bold uppercase tracking-wider">{isOnline ? 'Online & Available' : 'Offline'}</div>
            <div className="text-[10px] opacity-75">{isOnline ? 'Receiving Nearby Jobs' : 'Not Accepting Jobs'}</div>
          </div>
        </button>
      </div>

      {/* ── 2. Earnings Stats ────────────────────────────────────────────────── */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-6">
        <Card className="flex items-center gap-4">
          <div className="w-12 h-12 rounded-xl bg-emerald-500/10 text-emerald-400 flex items-center justify-center font-bold text-xl border border-emerald-500/20">
            ₹3,450
          </div>
          <div>
            <div className="text-xs text-slate-400 font-medium">Today's Earnings</div>
            <div className="text-lg font-bold text-white">4 Completed Jobs</div>
          </div>
        </Card>

        <Card className="flex items-center gap-4">
          <div className="w-12 h-12 rounded-xl bg-blue-500/10 text-blue-400 flex items-center justify-center font-bold text-xl border border-blue-500/20">
            ₹48,200
          </div>
          <div>
            <div className="text-xs text-slate-400 font-medium">Monthly Payout</div>
            <div className="text-lg font-bold text-white">August 2026</div>
          </div>
        </Card>

        <Card className="flex items-center gap-4">
          <div className="w-12 h-12 rounded-xl bg-amber-500/10 text-amber-400 flex items-center justify-center font-bold text-xl border border-amber-500/20">
            ⭐ 4.95
          </div>
          <div>
            <div className="text-xs text-slate-400 font-medium">Technician Score</div>
            <div className="text-lg font-bold text-white">Top 5% Partner</div>
          </div>
        </Card>
      </div>

      {/* ── 3. Assigned Jobs Queue ───────────────────────────────────────────── */}
      {(() => {
        const safeJobs = Array.isArray(assignedBookings) ? assignedBookings : [];
        return (
          <div className="space-y-6">
            <h2 className="text-xl font-bold text-white flex items-center gap-2">
              <Wrench className="w-5 h-5 text-brand-400" />
              Assigned Service Queue ({safeJobs.length})
            </h2>

            {statusMessage && (
              <div className="p-4 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs font-semibold">
                {statusMessage}
              </div>
            )}

            {safeJobs.length === 0 ? (
              <Card className="text-center py-12 space-y-3">
                <Clock className="w-8 h-8 text-slate-500 mx-auto" />
                <div className="text-slate-300 font-semibold text-sm">No Pending Service Dispatches</div>
                <p className="text-slate-500 text-xs">Keep your availability toggle online to receive instant dispatches.</p>
              </Card>
            ) : (
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {safeJobs.map((job) => (
                  <Card key={job.id} className="space-y-5 border-slate-800">
                    <div className="flex items-start justify-between">
                      <div>
                        <span className="text-xs font-mono text-brand-400 font-semibold">#{job.booking_number}</span>
                        <h3 className="text-lg font-bold text-white mt-1">{job.service?.name || 'Maintenance Request'}</h3>
                      </div>
                      <Badge status={job.status} />
                    </div>

                    <div className="space-y-2 text-xs text-slate-300 bg-slate-950/60 p-4 rounded-xl border border-slate-800">
                      <div className="flex items-center gap-2">
                        <MapPin className="w-4 h-4 text-brand-400 shrink-0" />
                        <span>Customer Address: {job.address?.house_no}, {job.address?.area}, {job.address?.city}</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <DollarSign className="w-4 h-4 text-emerald-400 shrink-0" />
                        <span>Payout: ₹{job.final_price} (Escrow Protected)</span>
                      </div>
                    </div>

                    {/* Job Action Buttons */}
                    <div className="pt-2 flex items-center gap-3">
                      {job.status === BookingStatus.ASSIGNED && (
                        <Button variant="primary" size="sm" className="w-full" onClick={() => handleAcceptJob(job.id)}>
                          Accept Booking Request
                        </Button>
                      )}

                      {job.status === BookingStatus.ACCEPTED && (
                        <Button
                          variant="primary"
                          size="sm"
                          className="w-full"
                          leftIcon={<Navigation className="w-4 h-4" />}
                          onClick={() => handleUpdateStatus(job.id, BookingStatus.ON_THE_WAY)}
                        >
                          Start Navigation (On The Way)
                        </Button>
                      )}

                      {job.status === BookingStatus.ON_THE_WAY && (
                        <Button
                          variant="glass"
                          size="sm"
                          className="w-full"
                          onClick={() => handleUpdateStatus(job.id, BookingStatus.ARRIVED)}
                        >
                          Mark Arrived at Location
                        </Button>
                      )}

                      {job.status === BookingStatus.ARRIVED && (
                        <Button
                          variant="primary"
                          size="sm"
                          className="w-full"
                          leftIcon={<QrCode className="w-4 h-4" />}
                          onClick={() => setActiveQRModalBookingId(job.id)}
                        >
                          Scan & Verify Customer QR
                        </Button>
                      )}

                      {job.status === BookingStatus.IN_PROGRESS && (
                        <Button
                          variant="primary"
                          size="sm"
                          className="w-full"
                          leftIcon={<CheckCircle2 className="w-4 h-4" />}
                          onClick={() => handleUpdateStatus(job.id, BookingStatus.COMPLETED)}
                        >
                          Mark Work Completed
                        </Button>
                      )}
                    </div>
                  </Card>
                ))}
              </div>
            )}
          </div>
        );
      })()}

      {/* ── 4. QR Verification Input Modal ───────────────────────────────────── */}
      {activeQRModalBookingId && (
        <div className="fixed inset-0 bg-slate-950/80 backdrop-blur-md flex items-center justify-center p-4 z-50">
          <motion.div initial={{ scale: 0.9, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} className="glass-card p-6 max-w-sm w-full space-y-4 text-center">
            <h3 className="text-lg font-bold text-white">SmartVerify QR Code Scan</h3>
            <p className="text-xs text-slate-400">Enter or scan the customer's QR code token to begin service.</p>
            
            <form onSubmit={handleVerifyQRSubmit} className="space-y-4">
              <input
                type="text"
                placeholder="HMQ-VERIFY-XXXX"
                value={qrInput}
                onChange={(e) => setQrInput(e.target.value)}
                required
                className="w-full px-4 py-2.5 bg-slate-900 border border-slate-700 rounded-xl text-white text-center text-sm font-mono focus:outline-none focus:ring-2 focus:ring-brand-500"
              />
              <div className="flex gap-2">
                <Button type="button" variant="secondary" size="sm" className="w-1/2" onClick={() => setActiveQRModalBookingId(null)}>
                  Cancel
                </Button>
                <Button type="submit" variant="primary" size="sm" className="w-1/2">
                  Verify QR Code
                </Button>
              </div>
            </form>
          </motion.div>
        </div>
      )}
    </div>
  );
};
