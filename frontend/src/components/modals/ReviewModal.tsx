import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Star, X, Send } from 'lucide-react';
import { reviewsApi } from '../../api/reviews';
import { Review } from '../../types';
import { Button } from '../ui/Button';

interface ReviewModalProps {
  isOpen: boolean;
  bookingId: number;
  serviceName: string;
  onClose: () => void;
  onReviewSubmitted: (newReview: Review) => void;
}

export const ReviewModal: React.FC<ReviewModalProps> = ({
  isOpen,
  bookingId,
  serviceName,
  onClose,
  onReviewSubmitted,
}) => {
  const [rating, setRating] = useState(5);
  const [comment, setComment] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setErrorMessage('');

    try {
      const review = await reviewsApi.createReview({
        booking_id: bookingId,
        rating,
        comment,
      });

      onReviewSubmitted(review);
      onClose();
    } catch (err: any) {
      setErrorMessage(
        err.response?.data?.detail || 'Failed to submit review. Please try again.'
      );
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-slate-950/80 backdrop-blur-md flex items-center justify-center p-4 z-50">
      <motion.div
        initial={{ scale: 0.95, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        exit={{ scale: 0.95, opacity: 0 }}
        className="glass-card p-6 max-w-md w-full space-y-6 relative border-slate-800 text-center"
      >
        <div className="flex items-center justify-between border-b border-slate-800 pb-4">
          <div className="text-left">
            <h3 className="text-lg font-bold text-white">Rate Service Performance</h3>
            <p className="text-xs text-slate-400">{serviceName}</p>
          </div>
          <button onClick={onClose} className="text-slate-400 hover:text-white transition-colors">
            <X className="w-5 h-5" />
          </button>
        </div>

        {errorMessage && (
          <div className="p-3 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-400 text-xs font-medium">
            {errorMessage}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Star Selector */}
          <div className="space-y-2">
            <label className="text-xs font-medium text-slate-300">Your Rating Score</label>
            <div className="flex items-center justify-center gap-2">
              {[1, 2, 3, 4, 5].map((star) => (
                <button
                  type="button"
                  key={star}
                  onClick={() => setRating(star)}
                  className="p-1 hover:scale-125 transition-transform"
                >
                  <Star
                    className={`w-8 h-8 ${
                      star <= rating ? 'text-amber-400 fill-amber-400' : 'text-slate-700'
                    }`}
                  />
                </button>
              ))}
            </div>
          </div>

          {/* Feedback Textarea */}
          <div className="space-y-1.5 text-left">
            <label className="text-xs font-medium text-slate-300">Detailed Feedback & Experience</label>
            <textarea
              rows={3}
              placeholder="Tell us about the technician's punctuality, repair quality, and professionalism..."
              value={comment}
              onChange={(e) => setComment(e.target.value)}
              required
              className="w-full px-4 py-3 bg-slate-900 border border-slate-800 rounded-xl text-slate-100 placeholder-slate-500 text-xs focus:outline-none focus:ring-2 focus:ring-brand-500"
            />
          </div>

          <div className="flex gap-3 pt-2">
            <Button type="button" variant="secondary" size="md" className="w-1/2" onClick={onClose}>
              Cancel
            </Button>
            <Button type="submit" variant="primary" size="md" isLoading={isLoading} className="w-1/2" leftIcon={<Send className="w-4 h-4" />}>
              Submit Review
            </Button>
          </div>
        </form>
      </motion.div>
    </div>
  );
};
