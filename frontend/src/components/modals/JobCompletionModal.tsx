import React, { useState, useEffect } from 'react';
import { X, Upload, Camera, CheckCircle2, AlertCircle } from 'lucide-react';
import { mediaApi } from '../../api/media';
import { technicianApi } from '../../api/technician';

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
      const res = await mediaApi.uploadMedia({
        file,
        asset_type: type === 'before' ? 'booking_before' : 'booking_after',
        owner_id: bookingId,
        owner_type: 'booking',
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

  const handleComplete = async () => {
    if (beforeImages.length === 0 || afterImages.length === 0) {
      setError("Both Before and After photos are required to complete the job.");
      return;
    }

    setLoading(true);
    setError(null);
    try {
      // Finalize the job status on the backend using technician API
      await technicianApi.completeService(bookingId, remarks);
      onSuccess();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to mark job as completed.');
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm">
      <div className="bg-dark-900 border border-dark-800 rounded-2xl shadow-2xl w-full max-w-md overflow-hidden flex flex-col">
        <div className="px-6 py-4 border-b border-dark-800 flex items-center justify-between bg-dark-950">
          <h2 className="text-lg font-bold text-white flex items-center gap-2">
            <CheckCircle2 className="w-5 h-5 text-emerald-400" />
            Complete Job & Audit
          </h2>
          <button onClick={onClose} className="p-2 text-slate-400 hover:text-white rounded-full hover:bg-dark-800 transition-colors">
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="p-6 overflow-y-auto max-h-[80vh]">
          {error && (
            <div className="mb-6 p-3 rounded-xl bg-red-500/10 border border-red-500/20 flex items-start gap-3">
              <AlertCircle className="w-5 h-5 text-red-400 shrink-0 mt-0.5" />
              <p className="text-sm text-red-300">{error}</p>
            </div>
          )}

          <p className="text-sm text-slate-400 mb-6">
            Please upload photo evidence of the site before starting and after finishing the work. Customers cannot pay until these are provided.
          </p>

          <div className="space-y-6">
            {/* Before Images */}
            <div>
              <label className="block text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">Before Work Photo <span className="text-red-400">*</span></label>
              <div className="grid grid-cols-2 gap-3">
                {beforeImages.map(img => (
                  <div key={img.id} className="relative h-24 rounded-xl overflow-hidden border border-dark-700">
                    <img src={img.thumbnail_url || img.secure_url} alt="Before work" className="w-full h-full object-cover" />
                  </div>
                ))}
                <label className="h-24 rounded-xl border border-dashed border-dark-700 flex flex-col items-center justify-center cursor-pointer hover:bg-dark-850 hover:border-dark-600 transition-colors">
                  {uploading === 'before' ? (
                    <span className="text-xs text-sage-400 animate-pulse">Uploading...</span>
                  ) : (
                    <>
                      <Camera className="w-5 h-5 text-slate-500 mb-1" />
                      <span className="text-xs text-slate-500 font-medium">Add Photo</span>
                    </>
                  )}
                  <input type="file" accept="image/*" className="hidden" onChange={(e) => handleFileUpload(e, 'before')} disabled={uploading !== null} />
                </label>
              </div>
            </div>

            {/* After Images */}
            <div>
              <label className="block text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">After Work Photo <span className="text-red-400">*</span></label>
              <div className="grid grid-cols-2 gap-3">
                {afterImages.map(img => (
                  <div key={img.id} className="relative h-24 rounded-xl overflow-hidden border border-dark-700">
                    <img src={img.thumbnail_url || img.secure_url} alt="After work" className="w-full h-full object-cover" />
                  </div>
                ))}
                <label className="h-24 rounded-xl border border-dashed border-dark-700 flex flex-col items-center justify-center cursor-pointer hover:bg-dark-850 hover:border-dark-600 transition-colors">
                  {uploading === 'after' ? (
                    <span className="text-xs text-sage-400 animate-pulse">Uploading...</span>
                  ) : (
                    <>
                      <Camera className="w-5 h-5 text-slate-500 mb-1" />
                      <span className="text-xs text-slate-500 font-medium">Add Photo</span>
                    </>
                  )}
                  <input type="file" accept="image/*" className="hidden" onChange={(e) => handleFileUpload(e, 'after')} disabled={uploading !== null} />
                </label>
              </div>
            </div>

            {/* Remarks */}
            <div>
              <label className="block text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">Completion Remarks (Optional)</label>
              <textarea
                className="w-full bg-dark-950 border border-dark-800 rounded-xl p-3 text-sm text-slate-200 placeholder-slate-600 focus:outline-none focus:border-sage-500 focus:ring-1 focus:ring-sage-500 transition-all resize-none h-24"
                placeholder="Any notes about the completion..."
                value={remarks}
                onChange={(e) => setRemarks(e.target.value)}
              />
            </div>
          </div>
        </div>

        <div className="p-4 border-t border-dark-800 bg-dark-950 flex justify-end gap-3">
          <button
            onClick={onClose}
            disabled={loading || uploading !== null}
            className="px-5 py-2 text-sm font-semibold text-slate-300 hover:text-white transition-colors"
          >
            Cancel
          </button>
          <button
            onClick={handleComplete}
            disabled={loading || uploading !== null || beforeImages.length === 0 || afterImages.length === 0}
            className="btn-primary px-6 py-2 text-sm font-semibold flex items-center gap-2 disabled:opacity-50"
          >
            {loading ? 'Submitting...' : 'Complete Job'}
          </button>
        </div>
      </div>
    </div>
  );
};
