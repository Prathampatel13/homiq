import React, { useState, useEffect } from 'react';
import { X, CheckCircle2, AlertTriangle, ShieldCheck, Camera, MessageSquare, ArrowRight } from 'lucide-react';
import { Booking } from '../../types';
import { mediaApi } from '../../api/media';
import { bookingsApi } from '../../api/bookings';
import { getSafeMediaUrl, handleImageError } from '../../utils/media';

interface ProofReviewModalProps {
  booking: Booking;
  isOpen: boolean;
  onClose: () => void;
  onApproved: () => void;
}

export const ProofReviewModal: React.FC<ProofReviewModalProps> = ({
  booking,
  isOpen,
  onClose,
  onApproved,
}) => {
  const [beforeImages, setBeforeImages] = useState<any[]>([]);
  const [afterImages, setAfterImages] = useState<any[]>([]);
  const [loadingMedia, setLoadingMedia] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [feedback, setFeedback] = useState('');
  const [showReworkInput, setShowReworkInput] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Parse technician remarks from admin_note if stored as JSON
  let techRemarks = '';
  if (booking.admin_note) {
    try {
      const parsed = JSON.parse(booking.admin_note);
      if (typeof parsed === 'object' && parsed.remarks) {
        techRemarks = parsed.remarks;
      } else if (typeof parsed === 'string') {
        techRemarks = parsed;
      }
    } catch {
      techRemarks = booking.admin_note;
    }
  }

  useEffect(() => {
    if (isOpen) {
      loadMedia();
    }
  }, [isOpen, booking.id]);

  const loadMedia = async () => {
    try {
      setLoadingMedia(true);
      const res = await mediaApi.getOwnerMedia('booking', booking.id);
      const items = res.items || [];
      setBeforeImages(items.filter(i => i.asset_type === 'booking_before'));
      setAfterImages(items.filter(i => i.asset_type === 'booking_after'));
    } catch (err) {
      console.error('Failed to load proof media', err);
    } finally {
      setLoadingMedia(false);
    }
  };

  const handleApprove = async () => {
    setSubmitting(true);
    setError(null);
    try {
      await bookingsApi.approveProofOfWork(booking.id, true, feedback);
      alert('Work evidence approved! Please proceed to complete the payment to finalize the job.');
      onApproved();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to approve work evidence.');
    } finally {
      setSubmitting(false);
    }
  };

  const handleRequestRework = async () => {
    if (!feedback.trim()) {
      setError('Please specify what adjustments or corrections are required.');
      return;
    }
    setSubmitting(true);
    setError(null);
    try {
      await bookingsApi.approveProofOfWork(booking.id, false, feedback);
      alert('Rework request sent to technician.');
      onApproved();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to send rework request.');
    } finally {
      setSubmitting(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/40 backdrop-blur-sm animate-in fade-in duration-200">
      <div className="bg-white border border-slate-200 rounded-3xl shadow-modal w-full max-w-2xl overflow-hidden flex flex-col max-h-[90vh]">
        
        {/* Header */}
        <div className="px-6 py-5 border-b border-slate-100 flex items-center justify-between bg-slate-50">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-2xl bg-sage-50 border border-sage-200 flex items-center justify-center text-sage-600">
              <ShieldCheck className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-base font-bold text-slate-900 tracking-tight">
                Inspect Proof of Work
              </h2>
              <p className="text-[11px] text-slate-500 font-mono">
                Booking #{booking.booking_number || booking.id} • Customer Approval Step
              </p>
            </div>
          </div>
          <button onClick={onClose} className="p-2 text-slate-400 hover:text-slate-900 rounded-xl hover:bg-slate-200 transition-colors">
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content Body */}
        <div className="p-6 overflow-y-auto space-y-6">
          {error && (
            <div className="p-3.5 rounded-xl bg-rose-50 border border-rose-200 flex items-start gap-3">
              <AlertTriangle className="w-5 h-5 text-rose-600 shrink-0 mt-0.5" />
              <p className="text-xs text-rose-700 font-mono">{error}</p>
            </div>
          )}

          {/* Intro description */}
          <p className="text-xs text-slate-600 leading-relaxed font-sans">
            Please carefully review the photographic evidence uploaded by your technician. Once you approve the work, the technician will finalize the job and the secure payment gateway will unlock.
          </p>

          {/* Photographic Comparison Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Before Photos Column */}
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-xs font-mono font-bold uppercase text-slate-600 tracking-wider">
                  Before Work
                </span>
                <span className="text-[10px] font-mono text-slate-400">
                  {beforeImages.length} Photo(s)
                </span>
              </div>
              <div className="space-y-2">
                {beforeImages.length > 0 ? (
                  beforeImages.map(img => (
                    <div key={img.id} className="relative h-44 rounded-2xl overflow-hidden border border-slate-200 bg-slate-100 shadow-subtle">
                      <img
                        src={getSafeMediaUrl(img.secure_url || (img as any).url || img.thumbnail_url, 'before')}
                        alt="Before"
                        onError={(e) => handleImageError(e, 'before')}
                        className="w-full h-full object-cover"
                      />
                      <div className="absolute bottom-2 left-2 bg-slate-900/80 backdrop-blur-md px-2.5 py-1 rounded-lg text-[10px] font-mono text-white">
                        Initial Condition
                      </div>
                    </div>
                  ))
                ) : (
                  <div className="h-44 rounded-2xl border border-dashed border-slate-300 flex items-center justify-center text-xs font-mono text-slate-400 bg-slate-50">
                    No Before Photos
                  </div>
                )}
              </div>
            </div>

            {/* After Photos Column */}
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-xs font-mono font-bold uppercase text-sage-700 tracking-wider">
                  After Work (Finished)
                </span>
                <span className="text-[10px] font-mono text-slate-400">
                  {afterImages.length} Photo(s)
                </span>
              </div>
              <div className="space-y-2">
                {afterImages.length > 0 ? (
                  afterImages.map(img => (
                    <div key={img.id} className="relative h-44 rounded-2xl overflow-hidden border border-sage-300 bg-slate-100 shadow-subtle">
                      <img
                        src={getSafeMediaUrl(img.secure_url || (img as any).url || img.thumbnail_url, 'after')}
                        alt="After"
                        onError={(e) => handleImageError(e, 'after')}
                        className="w-full h-full object-cover"
                      />
                      <div className="absolute bottom-2 left-2 bg-sage-600/90 backdrop-blur-md px-2.5 py-1 rounded-lg text-[10px] font-mono text-white font-bold">
                        Work Completed
                      </div>
                    </div>
                  ))
                ) : (
                  <div className="h-44 rounded-2xl border border-dashed border-slate-300 flex items-center justify-center text-xs font-mono text-slate-400 bg-slate-50">
                    No After Photos
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Technician Remarks */}
          {techRemarks && (
            <div className="p-4 rounded-2xl bg-slate-50 border border-slate-200 space-y-1.5">
              <span className="text-[10px] font-mono uppercase tracking-widest text-slate-500 font-semibold">Technician Remarks</span>
              <p className="text-xs font-mono text-slate-700 leading-relaxed">{techRemarks}</p>
            </div>
          )}

          {/* Rework Input Drawer */}
          {showReworkInput && (
            <div className="space-y-2 animate-in fade-in duration-150">
              <label className="block text-xs font-mono text-amber-700 font-semibold">Describe What Needs Adjustment:</label>
              <textarea
                className="w-full bg-white border border-amber-300 rounded-2xl p-3 text-xs text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-1 focus:ring-amber-500 resize-none h-20 font-mono"
                placeholder="E.g. Clean up debris near unit, tighten secondary fitting..."
                value={feedback}
                onChange={(e) => setFeedback(e.target.value)}
              />
            </div>
          )}

        </div>

        {/* Footer Actions */}
        <div className="p-5 border-t border-slate-100 bg-slate-50 flex flex-wrap items-center justify-between gap-3">
          <div>
            {!showReworkInput ? (
              <button
                type="button"
                onClick={() => setShowReworkInput(true)}
                className="text-xs font-mono text-slate-500 hover:text-amber-700 font-semibold transition-colors"
              >
                Request Adjustments / Rework
              </button>
            ) : (
              <button
                type="button"
                onClick={handleRequestRework}
                disabled={submitting}
                className="px-4 py-2 bg-amber-100 text-amber-800 border border-amber-300 rounded-xl text-xs font-mono font-bold hover:bg-amber-200 transition-all"
              >
                {submitting ? 'Sending...' : 'Submit Rework Request'}
              </button>
            )}
          </div>

          <div className="flex items-center gap-3">
            <button
              onClick={onClose}
              disabled={submitting}
              className="px-4 py-2 text-xs font-mono text-slate-500 hover:text-slate-900 transition-colors"
            >
              Cancel
            </button>

            <button
              onClick={handleApprove}
              disabled={submitting || beforeImages.length === 0 || afterImages.length === 0}
              className="btn-primary px-6 py-2.5 text-xs font-bold flex items-center gap-2 shadow-subtle active:scale-95 disabled:opacity-40"
            >
              <CheckCircle2 className="w-4 h-4" />
              <span>{submitting ? 'Approving...' : 'Approve Work Evidence'}</span>
            </button>
          </div>
        </div>

      </div>
    </div>
  );
};

export default ProofReviewModal;
