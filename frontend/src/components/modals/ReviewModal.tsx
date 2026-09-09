import React, { useState } from 'react';
import { Star, X, AlertCircle, Loader2, CheckCircle2 } from 'lucide-react';
import { reviewsApi } from '../../api/reviews';
import { Booking } from '../../types';

export interface ReviewModalProps {
  booking: Booking;
  isOpen: boolean;
  onClose: () => void;
  onSubmitted: () => void;
}

export const ReviewModal: React.FC<ReviewModalProps> = ({
  booking,
  isOpen,
  onClose,
  onSubmitted,
}) => {
  const [rating, setRating] = useState<number>(5);
  const [comment, setComment] = useState<string>('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!comment.trim()) {
      setError('Please provide a brief comment on the service quality.');
      return;
    }

    try {
      setLoading(true);
      setError(null);
      await reviewsApi.createReview({
        booking_id: booking.id,
        technician_id: booking.technician_id || 1,
        rating,
        comment,
      });

      setSuccess(true);
      setTimeout(() => {
        onSubmitted();
        onClose();
      }, 1500);
    } catch (err: any) {
      console.error('Failed to submit review:', err);
      setError(err?.response?.data?.detail || 'Failed to submit review. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/40 backdrop-blur-sm animate-in fade-in duration-150">
      <div className="relative w-full max-w-md rounded-3xl bg-white border border-slate-200 p-6 sm:p-8 shadow-modal text-slate-900">
        <button
          onClick={onClose}
          className="absolute top-5 right-5 p-2 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-500 hover:text-slate-900 border border-slate-200 transition-colors"
        >
          <X className="w-4 h-4" />
        </button>

        <div className="flex items-center gap-3 mb-6">
          <div className="w-10 h-10 rounded-xl bg-amber-50 border border-amber-200 flex items-center justify-center text-amber-500 shrink-0">
            <Star className="w-5 h-5 fill-amber-400 text-amber-400" />
          </div>
          <div>
            <h3 className="text-base font-bold text-slate-900 tracking-tight">Service Quality Review</h3>
            <p className="text-xs text-slate-500 font-mono">Booking #{booking.booking_number || booking.id}</p>
          </div>
        </div>

        {success ? (
          <div className="py-8 text-center space-y-3">
            <div className="w-14 h-14 rounded-full bg-emerald-50 border border-emerald-200 flex items-center justify-center text-emerald-600 mx-auto">
              <CheckCircle2 className="w-7 h-7" />
            </div>
            <h4 className="text-base font-bold text-slate-900">Thank You For Your Feedback</h4>
            <p className="text-xs text-slate-600">Your verified review helps maintain HomiQ's master craftsmanship standards.</p>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="space-y-5">
            <div className="text-center py-2">
              <span className="text-xs text-slate-700 block mb-2 font-semibold">Rate Technician Workmanship</span>
              <div className="flex items-center justify-center gap-2">
                {[1, 2, 3, 4, 5].map((star) => (
                  <button
                    key={star}
                    type="button"
                    onClick={() => setRating(star)}
                    className="p-1 transition-transform hover:scale-125 focus:outline-none"
                  >
                    <Star
                      className={`w-7 h-7 ${
                        star <= rating
                          ? 'text-amber-400 fill-amber-400'
                          : 'text-slate-200 fill-slate-100'
                      }`}
                    />
                  </button>
                ))}
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1.5">Your Feedback</label>
              <textarea
                value={comment}
                onChange={(e) => setComment(e.target.value)}
                rows={4}
                placeholder="Detail the technician's punctuality, cleanliness, and service precision..."
                className="input-field resize-none"
                required
              />
            </div>

            {error && (
              <div className="p-3 rounded-xl bg-rose-50 border border-rose-200 text-rose-700 text-xs flex items-center gap-2">
                <AlertCircle className="w-4 h-4 shrink-0 text-rose-600" />
                <span>{error}</span>
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              className="w-full btn-primary text-xs py-3 font-semibold flex items-center justify-center gap-1.5 shadow-subtle hover:shadow-accent disabled:opacity-40"
            >
              {loading && <Loader2 className="w-3.5 h-3.5 animate-spin" />}
              <span>Submit Review</span>
            </button>
          </form>
        )}
      </div>
    </div>
  );
};
