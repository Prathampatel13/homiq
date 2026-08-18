import React, { useState, useEffect, useCallback } from 'react';
import {
  ShieldCheck,
  CheckCircle2,
  Clock,
  Car,
  QrCode,
  DollarSign,
  Star,
  MapPin,
  Phone,
  Power,
  Upload,
  Calendar,
  User,
  Briefcase,
  AlertCircle,
  FileCheck,
} from 'lucide-react';
import { technicianApi, TechnicianDashboardStats, VerificationDocument } from '../api/technician';
import { Booking, TechnicianProfile } from '../types';
import { Button } from '../components/ui/Button';
import { Card } from '../components/ui/Card';
import { StatsCard } from '../components/ui/StatsCard';
import { StatusBadge } from '../components/ui/StatusBadge';
import { Tabs } from '../components/ui/Tabs';
import { Input } from '../components/ui/Input';
import { TechnicianVerifyModal } from '../components/modals/TechnicianVerifyModal';
import { BookingDetailsModal } from '../components/modals/BookingDetailsModal';
import { LoadingState } from '../components/ui/LoadingState';
import { EmptyState } from '../components/ui/EmptyState';
import { useToast } from '../components/ui/Toast';
import { extractErrorMessage } from '../api/axios';
import { useAuthStore } from '../store/useAuthStore';

export const ProviderDashboard: React.FC = () => {
  const toast = useToast();
  const { user } = useAuthStore();

  const [activeTab, setActiveTab] = useState('assigned');
  const [profile, setProfile] = useState<TechnicianProfile | null>(null);
  const [stats, setStats] = useState<TechnicianDashboardStats | null>(null);
  const [assignedBookings, setAssignedBookings] = useState<Booking[]>([]);
  const [availableJobs, setAvailableJobs] = useState<Booking[]>([]);
  const [documents, setDocuments] = useState<VerificationDocument[]>([]);
  const [earnings, setEarnings] = useState<{ total_earnings: number; pending_payout: number; completed_jobs: number } | null>(null);

  const [isOnline, setIsOnline] = useState<boolean>(true);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [actionLoadingId, setActionLoadingId] = useState<number | null>(null);

  // Modals
  const [selectedBookingForVerify, setSelectedBookingForVerify] = useState<Booking | null>(null);
  const [isVerifyModalOpen, setIsVerifyModalOpen] = useState(false);
  const [selectedBookingDetails, setSelectedBookingDetails] = useState<Booking | null>(null);
  const [isDetailsModalOpen, setIsDetailsModalOpen] = useState(false);

  // Document upload state
  const [docType, setDocType] = useState<string>('government_id');
  const [uploadingDoc, setUploadingDoc] = useState<boolean>(false);

  const fetchTechnicianData = useCallback(async () => {
    try {
      const [profData, statsData, bookingsData, jobsData, docsData, earnData] = await Promise.all([
        technicianApi.getProfile().catch(() => null),
        technicianApi.getDashboard().catch(() => null),
        technicianApi.getMyBookings().catch(() => []),
        technicianApi.getMyJobs().catch(() => []),
        technicianApi.getDocuments().catch(() => []),
        technicianApi.getEarnings().catch(() => null),
      ]);

      if (profData) {
        setProfile(profData);
        setIsOnline(profData.is_online);
      }
      if (statsData) setStats(statsData);
      setAssignedBookings(Array.isArray(bookingsData) ? bookingsData : (bookingsData as any).items || []);
      setAvailableJobs(Array.isArray(jobsData) ? jobsData : (jobsData as any).items || []);
      setDocuments(docsData);
      if (earnData) setEarnings(earnData);
    } catch (err) {
      toast.error('Could not load technician data', extractErrorMessage(err));
    } finally {
      setIsLoading(false);
    }
  }, [toast]);

  useEffect(() => {
    fetchTechnicianData();
  }, [fetchTechnicianData]);

  // Toggle Online/Offline Switch
  const handleToggleOnline = async () => {
    try {
      if (isOnline) {
        await technicianApi.setOffline();
        setIsOnline(false);
        toast.info('Status Changed', 'You are now offline.');
      } else {
        await technicianApi.setOnline();
        setIsOnline(true);
        toast.success('Status Changed', 'You are now online and available for job dispatches.');
      }
    } catch (err) {
      toast.error('Could not toggle status', extractErrorMessage(err));
    }
  };

  // Status Action Handlers
  const handleAcceptJob = async (id: number) => {
    setActionLoadingId(id);
    try {
      await technicianApi.acceptBooking(id);
      toast.success('Job Accepted', 'Assigned to your active service queue.');
      fetchTechnicianData();
    } catch (err) {
      toast.error('Failed to accept job', extractErrorMessage(err));
    } finally {
      setActionLoadingId(null);
    }
  };

  const handleStartTrip = async (id: number) => {
    setActionLoadingId(id);
    try {
      await technicianApi.startTrip(id);
      toast.success('Trip Started', 'Customer notified of your departure.');
      fetchTechnicianData();
    } catch (err) {
      toast.error('Failed to start trip', extractErrorMessage(err));
    } finally {
      setActionLoadingId(null);
    }
  };

  const handleMarkArrived = async (id: number) => {
    setActionLoadingId(id);
    try {
      await technicianApi.markArrived(id);
      toast.success('Arrived at Location', 'Prompt customer for SmartVerify QR code.');
      fetchTechnicianData();
    } catch (err) {
      toast.error('Failed to update arrival', extractErrorMessage(err));
    } finally {
      setActionLoadingId(null);
    }
  };

  const handleCompleteService = async (id: number) => {
    setActionLoadingId(id);
    try {
      await technicianApi.completeService(id);
      toast.success('Service Completed!', 'Earnings added to your technician ledger.');
      fetchTechnicianData();
    } catch (err) {
      toast.error('Failed to complete service', extractErrorMessage(err));
    } finally {
      setActionLoadingId(null);
    }
  };

  const handleUploadDocument = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setUploadingDoc(true);
    try {
      await technicianApi.uploadDocument(docType, file);
      toast.success('Document Submitted', 'Submitted for admin verification review.');
      fetchTechnicianData();
    } catch (err) {
      toast.error('Upload failed', extractErrorMessage(err));
    } finally {
      setUploadingDoc(false);
    }
  };

  // Active in-flight booking for technician
  const inFlightBooking = assignedBookings.find((b) =>
    ['accepted', 'on_the_way', 'arrived', 'waiting_qr', 'qr_verified', 'in_progress'].includes(
      String(b.status).toLowerCase()
    )
  );

  if (isLoading) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-20">
        <LoadingState message="Connecting to technician dispatch gateway..." />
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-8">
      {/* Top Header & Availability Toggle */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-6 border-b border-dark-750">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="text-xs font-mono uppercase tracking-widest text-brand-400 font-semibold">
              Trade Specialist Portal
            </span>
            {profile?.is_verified ? (
              <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] bg-emerald-500/15 text-emerald-400 border border-emerald-500/30">
                <ShieldCheck className="w-3 h-3" />
                <span>VERIFIED PRO</span>
              </span>
            ) : (
              <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] bg-amber-500/15 text-amber-400 border border-amber-500/30">
                <Clock className="w-3 h-3" />
                <span>PENDING VERIFICATION</span>
              </span>
            )}
          </div>
          <h1 className="text-3xl font-bold text-white tracking-tight">
            {profile?.user?.full_name || user?.full_name || 'Technician'} Dashboard
          </h1>
          <p className="text-xs sm:text-sm text-slate-400 mt-1">
            {profile?.specialization || 'Certified Field Specialist'} • Real-time Job Dispatch Feed
          </p>
        </div>

        {/* Online Switch Button */}
        <button
          type="button"
          onClick={handleToggleOnline}
          className={`flex items-center gap-2.5 px-4 py-2 rounded-xl font-medium text-xs border transition-all ${
            isOnline
              ? 'bg-emerald-500/15 text-emerald-400 border-emerald-500/30 shadow-subtle hover:bg-emerald-500/25'
              : 'bg-dark-850 text-slate-400 border-dark-700 hover:text-white'
          }`}
        >
          <Power className={`w-4 h-4 ${isOnline ? 'text-emerald-400' : 'text-slate-500'}`} />
          <span>{isOnline ? 'Online & Available' : 'Offline'}</span>
        </button>
      </div>

      {/* KPI STATS OVERVIEW */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <StatsCard
          label="Today's Jobs"
          value={stats?.today_jobs_count || assignedBookings.length}
          icon={Calendar}
          subtext="Assigned queue"
        />
        <StatsCard
          label="Active In-Progress"
          value={inFlightBooking ? 1 : 0}
          icon={Clock}
          subtext="Currently executing"
        />
        <StatsCard
          label="Completed Jobs"
          value={stats?.completed_jobs_count || earnings?.completed_jobs || 0}
          icon={CheckCircle2}
          subtext="Lifetime jobs"
        />
        <StatsCard
          label="Total Earnings"
          value={`₹${(stats?.total_earnings || earnings?.total_earnings || 0).toFixed(2)}`}
          icon={DollarSign}
          subtext={`Pending payout: ₹${(earnings?.pending_payout || 0).toFixed(2)}`}
        />
      </div>

      {/* ACTIVE JOB LIFECYCLE BAR */}
      {inFlightBooking && (
        <Card className="p-6 bg-gradient-to-r from-dark-900 via-dark-850 to-dark-900 border-brand-500/40 space-y-4">
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-4 border-b border-dark-750">
            <div>
              <div className="flex items-center gap-2.5">
                <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-brand-500/15 text-brand-400 border border-brand-500/30">
                  CURRENT ACTIVE SERVICE
                </span>
                <StatusBadge status={inFlightBooking.status} />
              </div>
              <h3 className="text-xl font-bold text-white mt-2">
                {inFlightBooking.service?.name || 'Home Service'}
              </h3>
              <p className="text-xs text-slate-300">
                Customer: <span className="font-semibold text-white">{inFlightBooking.customer?.full_name || 'Homeowner'}</span> • {inFlightBooking.booking_date} at {inFlightBooking.preferred_time}
              </p>
            </div>

            <div className="text-right">
              <span className="text-xs text-slate-400 block">Job Payout</span>
              <span className="text-xl font-bold text-white font-mono">
                ₹{(inFlightBooking.final_price || inFlightBooking.base_price || 499).toFixed(2)}
              </span>
            </div>
          </div>

          {/* Location & Instructions */}
          {inFlightBooking.address && (
            <div className="p-3.5 bg-dark-950 rounded-xl flex items-center justify-between text-xs text-slate-300">
              <div className="flex items-center gap-2">
                <MapPin className="w-4 h-4 text-brand-400 flex-shrink-0" />
                <span>
                  {inFlightBooking.address.house_no}, {inFlightBooking.address.area}, {inFlightBooking.address.city}
                </span>
              </div>
              {inFlightBooking.customer?.phone && (
                <a
                  href={`tel:${inFlightBooking.customer.phone}`}
                  className="flex items-center gap-1 text-brand-400 font-semibold hover:underline"
                >
                  <Phone className="w-3.5 h-3.5" />
                  <span>Call Customer</span>
                </a>
              )}
            </div>
          )}

          {/* Action Button Workflow */}
          <div className="flex flex-wrap items-center justify-end gap-3 pt-2">
            {String(inFlightBooking.status).toLowerCase() === 'accepted' && (
              <Button
                variant="primary"
                size="md"
                leftIcon={Car}
                onClick={() => handleStartTrip(inFlightBooking.id)}
                isLoading={actionLoadingId === inFlightBooking.id}
              >
                Start Driving to Location
              </Button>
            )}

            {String(inFlightBooking.status).toLowerCase() === 'on_the_way' && (
              <Button
                variant="primary"
                size="md"
                leftIcon={ShieldCheck}
                onClick={() => handleMarkArrived(inFlightBooking.id)}
                isLoading={actionLoadingId === inFlightBooking.id}
              >
                Mark Arrived at Doorstep
              </Button>
            )}

            {['arrived', 'waiting_qr'].includes(String(inFlightBooking.status).toLowerCase()) && (
              <Button
                variant="primary"
                size="md"
                leftIcon={QrCode}
                onClick={() => {
                  setSelectedBookingForVerify(inFlightBooking);
                  setIsVerifyModalOpen(true);
                }}
              >
                Scan Customer QR / OTP
              </Button>
            )}

            {['qr_verified', 'in_progress'].includes(String(inFlightBooking.status).toLowerCase()) && (
              <Button
                variant="primary"
                size="md"
                leftIcon={CheckCircle2}
                onClick={() => handleCompleteService(inFlightBooking.id)}
                isLoading={actionLoadingId === inFlightBooking.id}
              >
                Mark Service Completed
              </Button>
            )}

            <Button
              variant="outline"
              size="md"
              onClick={() => {
                setSelectedBookingDetails(inFlightBooking);
                setIsDetailsModalOpen(true);
              }}
            >
              Full Details
            </Button>
          </div>
        </Card>
      )}

      {/* DASHBOARD TABS */}
      <div className="space-y-6">
        <Tabs
          tabs={[
            { id: 'assigned', label: 'My Bookings', count: assignedBookings.length },
            { id: 'available', label: 'Available Jobs Feed', count: availableJobs.length },
            { id: 'earnings', label: 'Earnings & Ledger' },
            { id: 'documents', label: 'Certifications & Docs', count: documents.length },
          ]}
          activeTab={activeTab}
          onChange={setActiveTab}
          variant="underline"
        />

        {/* TAB 1: ASSIGNED BOOKINGS */}
        {activeTab === 'assigned' && (
          <div className="space-y-4">
            {assignedBookings.length > 0 ? (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {assignedBookings.map((b) => (
                  <Card key={b.id} className="p-5 flex flex-col justify-between space-y-3">
                    <div>
                      <div className="flex items-start justify-between">
                        <div>
                          <span className="text-[11px] font-mono text-slate-500 block">
                            #{b.booking_number || b.id}
                          </span>
                          <h4 className="text-sm font-bold text-white">{b.service?.name || 'Service Job'}</h4>
                        </div>
                        <StatusBadge status={b.status} />
                      </div>

                      <div className="grid grid-cols-2 gap-2 text-xs text-slate-300 py-2">
                        <div className="flex items-center gap-1.5">
                          <Calendar className="w-3.5 h-3.5 text-brand-400" />
                          <span>{b.booking_date}</span>
                        </div>
                        <div className="flex items-center gap-1.5">
                          <Clock className="w-3.5 h-3.5 text-brand-400" />
                          <span>{b.preferred_time}</span>
                        </div>
                      </div>

                      {b.address && (
                        <p className="text-xs text-slate-400 truncate">
                          📍 {b.address.house_no}, {b.address.area}, {b.address.city}
                        </p>
                      )}
                    </div>

                    <div className="pt-3 border-t border-dark-800 flex items-center justify-between">
                      <span className="text-sm font-bold text-white font-mono">
                        ₹{(b.final_price || b.base_price || 499).toFixed(2)}
                      </span>
                      <Button
                        variant="secondary"
                        size="sm"
                        onClick={() => {
                          setSelectedBookingDetails(b);
                          setIsDetailsModalOpen(true);
                        }}
                      >
                        Inspect
                      </Button>
                    </div>
                  </Card>
                ))}
              </div>
            ) : (
              <EmptyState
                icon={Briefcase}
                title="No assigned bookings"
                description="Check the Available Jobs Feed to accept new jobs in your radius."
                actionLabel="View Jobs Feed"
                onAction={() => setActiveTab('available')}
              />
            )}
          </div>
        )}

        {/* TAB 2: AVAILABLE JOBS FEED */}
        {activeTab === 'available' && (
          <div className="space-y-4">
            {availableJobs.length > 0 ? (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {availableJobs.map((job) => (
                  <Card key={job.id} className="p-5 flex flex-col justify-between space-y-3">
                    <div>
                      <div className="flex justify-between items-start">
                        <span className="text-[11px] font-mono text-slate-500">#{job.booking_number || job.id}</span>
                        <span className="text-sm font-bold text-white font-mono">
                          ₹{(job.final_price || job.base_price || 499).toFixed(2)}
                        </span>
                      </div>
                      <h4 className="text-sm font-bold text-white mt-1">{job.service?.name || 'Incoming Job Request'}</h4>
                      <p className="text-xs text-slate-400 mt-1">{job.customer_note || 'Standard installation / repair.'}</p>

                      <div className="flex items-center gap-4 text-xs text-slate-300 pt-2">
                        <span>📅 {job.booking_date}</span>
                        <span>⏰ {job.preferred_time}</span>
                      </div>
                    </div>

                    <div className="pt-3 border-t border-dark-800 flex justify-end">
                      <Button
                        variant="primary"
                        size="sm"
                        onClick={() => handleAcceptJob(job.id)}
                        isLoading={actionLoadingId === job.id}
                      >
                        Accept & Dispatch
                      </Button>
                    </div>
                  </Card>
                ))}
              </div>
            ) : (
              <EmptyState
                icon={Briefcase}
                title="No available jobs right now"
                description="Stay online. You will receive notifications as soon as new bookings are requested in your service area."
              />
            )}
          </div>
        )}

        {/* TAB 3: EARNINGS */}
        {activeTab === 'earnings' && (
          <div className="space-y-6">
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              <Card className="p-5">
                <p className="text-xs text-slate-400">Total Lifetime Earnings</p>
                <p className="text-2xl font-bold text-white font-mono mt-1">
                  ₹{(earnings?.total_earnings || 0).toFixed(2)}
                </p>
              </Card>
              <Card className="p-5">
                <p className="text-xs text-slate-400">Pending Payout</p>
                <p className="text-2xl font-bold text-emerald-400 font-mono mt-1">
                  ₹{(earnings?.pending_payout || 0).toFixed(2)}
                </p>
              </Card>
              <Card className="p-5">
                <p className="text-xs text-slate-400">Completed Jobs</p>
                <p className="text-2xl font-bold text-white font-mono mt-1">
                  {earnings?.completed_jobs || 0}
                </p>
              </Card>
            </div>
          </div>
        )}

        {/* TAB 4: DOCUMENTS & CERTIFICATIONS */}
        {activeTab === 'documents' && (
          <div className="space-y-6">
            <div className="p-5 bg-dark-900 border border-dark-750 rounded-2xl space-y-4">
              <h3 className="text-sm font-bold text-white">Upload Trade Credential or Government ID</h3>
              <p className="text-xs text-slate-400">
                Upload Aadhaar, Trade License, or Skill Certificates to maintain verified status.
              </p>

              <div className="flex flex-col sm:flex-row items-center gap-3">
                <select
                  value={docType}
                  onChange={(e) => setDocType(e.target.value)}
                  className="bg-dark-850 border border-dark-700 rounded-xl px-3 py-2 text-xs text-white focus:outline-none"
                >
                  <option value="government_id">Government ID (Aadhaar / Passport)</option>
                  <option value="trade_certificate">Trade Qualification / ITI Certificate</option>
                  <option value="police_verification">Police Clearance Record</option>
                </select>

                <label className="btn-primary text-xs cursor-pointer flex items-center gap-2 px-4 py-2">
                  <Upload className="w-3.5 h-3.5" />
                  <span>{uploadingDoc ? 'Uploading...' : 'Choose File & Submit'}</span>
                  <input
                    type="file"
                    onChange={handleUploadDocument}
                    disabled={uploadingDoc}
                    className="hidden"
                    accept="image/*,.pdf"
                  />
                </label>
              </div>
            </div>

            {/* Document list */}
            {documents.length > 0 && (
              <div className="p-4 bg-dark-900 border border-dark-750 rounded-2xl divide-y divide-dark-800">
                {documents.map((doc) => (
                  <div key={doc.id} className="py-3 flex items-center justify-between text-xs">
                    <div className="flex items-center gap-2.5">
                      <FileCheck className="w-4 h-4 text-brand-400" />
                      <span className="font-semibold text-white capitalize">{doc.doc_type.replace(/_/g, ' ')}</span>
                    </div>
                    <span
                      className={`px-2 py-0.5 rounded-full text-[10px] ${
                        doc.is_verified
                          ? 'bg-emerald-500/15 text-emerald-400 border border-emerald-500/30'
                          : 'bg-amber-500/15 text-amber-400 border border-amber-500/30'
                      }`}
                    >
                      {doc.is_verified ? 'Verified' : 'Under Review'}
                    </span>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>

      {/* Technician QR / OTP Verify Modal */}
      {selectedBookingForVerify && (
        <TechnicianVerifyModal
          isOpen={isVerifyModalOpen}
          onClose={() => {
            setIsVerifyModalOpen(false);
            setSelectedBookingForVerify(null);
          }}
          booking={selectedBookingForVerify}
          onSuccess={() => {
            fetchTechnicianData();
          }}
        />
      )}

      {/* Detailed Booking Modal */}
      <BookingDetailsModal
        isOpen={isDetailsModalOpen}
        onClose={() => {
          setIsDetailsModalOpen(false);
          setSelectedBookingDetails(null);
        }}
        booking={selectedBookingDetails}
        onBookingUpdated={fetchTechnicianData}
      />
    </div>
  );
};
