import React, { useState, useEffect } from 'react';
import { X, Upload, Camera, CheckCircle2, AlertCircle, Clock, ShieldCheck } from 'lucide-react';
import { mediaApi } from '../../api/media';
import { bookingsApi } from '../../api/bookings';
import { getSafeMediaUrl, handleImageError } from '../../utils/media';

interface JobCompletionModalProps {
  bookingId: number;
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
}

export const JobCompletionModal: React.FC<JobCompletionModalProps> = ({
  bookingId,
  isOpen,
  onClose,
  onSuccess,
}) => {
  const [beforeImages, setBeforeImages] = useState<any[]>([]);
  const [afterImages, setAfterImages] = useState<any[]>([]);
  const [remarks, setRemarks] = useState('');
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState<'before' | 'after' | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (isOpen) {
      loadExistingMedia();
    }
  }, [isOpen, bookingId]);

  const loadExistingMedia = async () => {
    try {
      const res = await mediaApi.getOwnerMedia('booking', bookingId);
      const items = res.items || [];
      setBeforeImages(items.filter(i => i.asset_type === 'booking_before'));
      setAfterImages(items.filter(i => i.asset_type === 'booking_after'));
    } catch (err) {
      console.error("Failed to load existing media", err);
    }
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>, type: 'before' | 'after') => {
    const file = e.target.files?.[0];
    if (!file) return;

    setUploading(type);
    setError(null);
    try {
      const assetType = type === 'before' ? 'booking_before' : 'booking_after';
      const res = await mediaApi.uploadMedia({
        file,
        asset_type: assetType,
        owner_id: bookingId,
        owner_type: 'booking'
      });
      if (type === 'before') {
        setBeforeImages(prev => [...prev, res]);
      } else {
        setAfterImages(prev => [...prev, res]);
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to upload image. Please try again.');
    } finally {
      setUploading(null);
    }
  };

  const handleSubmitProof = async () => {
    if (beforeImages.length === 0 || afterImages.length === 0) {
      setError("Both Before and After photos are strictly required for proof of work.");
      return;
    }

    setLoading(true);
    setError(null);
    try {
      // Submit proof of work for customer review & approval
      await bookingsApi.submitProofOfWork(bookingId, remarks);
      alert('Proof of work submitted successfully! The customer has been notified to inspect and approve the photos. Once approved, you can finalize the job.');
      onSuccess();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to submit proof of work.');
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/75 backdrop-blur-md animate-in fade-in duration-200">
      <div className="bg-dark-900 border border-dark-750 rounded-3xl shadow-modal w-full max-w-lg overflow-hidden flex flex-col">
        {/* Modal Header */}
        <div className="px-6 py-5 border-b border-dark-750 flex items-center justify-between bg-dark-950">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-2xl bg-sage-500/15 border border-sage-500/30 flex items-center justify-center text-sage-400">
              <ShieldCheck className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-base font-bold text-white tracking-tight">
                Submit Proof of Work
              </h2>
              <p className="text-[11px] text-slate-400 font-mono">
                Mandatory Before & After Audit • Customer Review Step
              </p>
            </div>
          </div>
          <button onClick={onClose} className="p-2 text-slate-400 hover:text-white rounded-xl hover:bg-dark-850 transition-colors">
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Modal Content */}
        <div className="p-6 overflow-y-auto max-h-[75vh] space-y-6">
          {error && (
            <div className="p-3.5 rounded-xl bg-red-500/10 border border-red-500/30 flex items-start gap-3">
              <AlertCircle className="w-5 h-5 text-red-400 shrink-0 mt-0.5" />
              <p className="text-xs text-red-300 font-mono leading-relaxed">{error}</p>
            </div>
          )}

          {/* Workflow Notice */}
          <div className="p-4 rounded-2xl bg-dark-850 border border-dark-750 space-y-2">
            <div className="flex items-center gap-2 text-xs font-mono font-bold text-sage-400">
              <Clock className="w-4 h-4" />
              <span>STAGE: CUSTOMER APPROVAL REQUIRED</span>
            </div>
            <p className="text-xs text-slate-400 leading-relaxed">
              Upload clear evidence of the site before and after the work. Once you submit, the customer will receive an alert to inspect and approve the photos. Final completion and checkout unlock immediately upon customer approval.
            </p>
          </div>

          <div className="space-y-6">
            {/* Before Images */}
            <div>
              <div className="flex items-center justify-between mb-2">
                <label className="text-xs font-bold text-slate-300 uppercase font-mono tracking-wider">
                  1. Before-Work Evidence <span className="text-sage-500">*</span>
                </label>
                <span className="text-[10px] font-mono text-slate-500">
                  {beforeImages.length > 0 ? `${beforeImages.length} uploaded` : 'Required'}
                </span>
              </div>
              <div className="grid grid-cols-2 gap-3">
                {beforeImages.map(img => (
                  <div key={img.id} className="relative h-28 rounded-2xl overflow-hidden border border-dark-700 bg-dark-950 group">
                    <img
                      src={getSafeMediaUrl(img.secure_url || (img as any).url || img.thumbnail_url, 'before')}
                      alt="Before work"
                      onError={(e) => handleImageError(e, 'before')}
                      className="w-full h-full object-cover"
                    />
                    <div className="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
                      <span className="text-[10px] font-mono text-white bg-dark-900/80 px-2 py-1 rounded">Before</span>
                    </div>
                  </div>
                ))}
                <label className="h-28 rounded-2xl border border-dashed border-dark-700 hover:border-sage-500/50 flex flex-col items-center justify-center cursor-pointer bg-dark-950 hover:bg-dark-850 transition-colors group">
                  {uploading === 'before' ? (
                    <span className="text-xs font-mono text-sage-400 animate-pulse">Uploading...</span>
                  ) : (
                    <>
                      <Camera className="w-5 h-5 text-slate-500 group-hover:text-sage-400 mb-1 transition-colors" />
                      <span className="text-xs text-slate-400 font-medium group-hover:text-white transition-colors">Add Before Photo</span>
                    </>
                  )}
                  <input type="file" accept="image/*" className="hidden" onChange={(e) => handleFileUpload(e, 'before')} disabled={uploading !== null} />
                </label>
              </div>
            </div>

            {/* After Images */}
            <div>
              <div className="flex items-center justify-between mb-2">
                <label className="text-xs font-bold text-slate-300 uppercase font-mono tracking-wider">
                  2. After-Work Evidence <span className="text-sage-500">*</span>
                </label>
                <span className="text-[10px] font-mono text-slate-500">
                  {afterImages.length > 0 ? `${afterImages.length} uploaded` : 'Required'}
                </span>
              </div>
              <div className="grid grid-cols-2 gap-3">
                {afterImages.map(img => (
                  <div key={img.id} className="relative h-28 rounded-2xl overflow-hidden border border-dark-700 bg-dark-950 group">
                    <img
                      src={getSafeMediaUrl(img.thumbnail_url || img.secure_url, 'after')}
                      alt="After work"
                      onError={(e) => handleImageError(e, 'after')}
                      className="w-full h-full object-cover"
                    />
                    <div className="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
                      <span className="text-[10px] font-mono text-white bg-dark-900/80 px-2 py-1 rounded">After</span>
                    </div>
                  </div>
                ))}
                <label className="h-28 rounded-2xl border border-dashed border-dark-700 hover:border-sage-500/50 flex flex-col items-center justify-center cursor-pointer bg-dark-950 hover:bg-dark-850 transition-colors group">
                  {uploading === 'after' ? (
                    <span className="text-xs font-mono text-sage-400 animate-pulse">Uploading...</span>
                  ) : (
                    <>
                      <Camera className="w-5 h-5 text-slate-500 group-hover:text-sage-400 mb-1 transition-colors" />
                      <span className="text-xs text-slate-400 font-medium group-hover:text-white transition-colors">Add After Photo</span>
                    </>
                  )}
                  <input type="file" accept="image/*" className="hidden" onChange={(e) => handleFileUpload(e, 'after')} disabled={uploading !== null} />
                </label>
              </div>
            </div>

            {/* Remarks */}
            <div>
              <label className="block text-xs font-bold text-slate-300 uppercase font-mono tracking-wider mb-2">
                Technician Notes & Diagnostics (Optional)
              </label>
              <textarea
                className="w-full bg-dark-950 border border-dark-750 rounded-2xl p-3.5 text-xs text-slate-200 placeholder-slate-600 focus:outline-none focus:border-sage-500 focus:ring-1 focus:ring-sage-500 transition-all resize-none h-24 font-mono"
                placeholder="Details of the repair, replaced parts, or recommendations for the customer..."
                value={remarks}
                onChange={(e) => setRemarks(e.target.value)}
              />
            </div>
          </div>
        </div>

        {/* Modal Footer */}
        <div className="p-5 border-t border-dark-750 bg-dark-950 flex items-center justify-between">
          <button
            onClick={onClose}
            disabled={loading || uploading !== null}
            className="px-4 py-2 text-xs font-mono text-slate-400 hover:text-white transition-colors"
          >
            Cancel
          </button>
          
          <button
            onClick={handleSubmitProof}
            disabled={loading || uploading !== null || beforeImages.length === 0 || afterImages.length === 0}
            className="btn-primary px-6 py-2.5 text-xs font-bold flex items-center gap-2 disabled:opacity-40 disabled:cursor-not-allowed shadow-[0_0_20px_-5px_rgba(217,56,30,0.5)]"
          >
            <ShieldCheck className="w-4 h-4" />
            <span>{loading ? 'Submitting Evidence...' : 'Submit Proof for Customer Approval'}</span>
          </button>
        </div>
      </div>
    </div>
  );
};

export default JobCompletionModal;
