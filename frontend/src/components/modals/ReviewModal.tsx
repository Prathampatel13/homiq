import React, { useState } from 'react';
import { Star, CheckCircle2 } from 'lucide-react';
import { Modal } from '../ui/Modal';
import { Button } from '../ui/Button';
import { Textarea } from '../ui/Textarea';
import { reviewsApi } from '../../api/reviews';
import { useToast } from '../ui/Toast';
import { extractErrorMessage } from '../../api/axios';
import { Booking } from '../../types';

interface ReviewModalProps {
  isOpen: boolean;
  onClose: () => void;
  booking: Booking;
  onSuccess?: () => void;
}

export const ReviewModal: React.FC<ReviewModalProps> = ({
  isOpen,
  onClose,
  booking,
  onSuccess,
}) => {
  const toast = useToast();
  const [rating, setRating] = useState<number>(5);
  const [hoverRating, setHoverRating] = useState<number>(0);
  const [comment, setComment] = useState<string>('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!comment.trim()) {
      toast.error('Review Required', 'Please share a brief comment about your service experience.');
      return;
    }

    const techId = booking.technician_id || (booking.technician ? (booking.technician as any).id : 1);

    setIsLoading(true);
    try {
      await reviewsApi.createReview({
        booking_id: booking.id,
        technician_id: techId,
        rating,
        comment: comment.trim(),
      });
      toast.success('Thank You!', 'Your review has been verified and published.');
      if (onSuccess) onSuccess();
      onClose();
    } catch (err) {
      toast.error('Could not submit review', extractErrorMessage(err));
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="Rate Your Experience"
      description={`Service: ${booking.service?.name || 'Home Service'}`}
      maxWidth="md"
    >
      <form onSubmit={handleSubmit} className="space-y-5">
        {/* Star Selector */}
        <div className="flex flex-col items-center justify-center p-4 bg-dark-850 border border-dark-750 rounded-2xl space-y-2">
          <p className="text-xs text-slate-400 font-medium">How would you rate the service quality?</p>
          <div className="flex items-center gap-2">
            {[1, 2, 3, 4, 5].map((star) => {
              const filled = (hoverRating || rating) >= star;
              return (
                <button
                  key={star}
                  type="button"
                  onMouseEnter={() => setHoverRating(star)}
                  onMouseLeave={() => setHoverRating(0)}
                  onClick={() => setRating(star)}
                  className="p-1 text-slate-600 hover:scale-110 transition-transform focus:outline-none"
                >
                  <Star
                    className={`w-7 h-7 ${
                      filled ? 'text-amber-400 fill-amber-400' : 'text-slate-600'
                    } transition-colors`}
                  />
                </button>
              );
            })}
          </div>
          <span className="text-xs font-semibold text-amber-400 font-mono">
            {rating === 5
              ? 'Excellent (5.0 / 5)'
              : rating === 4
              ? 'Very Good (4.0 / 5)'
              : rating === 3
              ? 'Average (3.0 / 5)'
              : rating === 2
              ? 'Below Expectations (2.0 / 5)'
              : 'Poor (1.0 / 5)'}
          </span>
        </div>

        <Textarea
          label="Your Feedback *"
          placeholder="Describe punctuality, quality of work, cleanliness, and overall satisfaction..."
          rows={4}
          value={comment}
          onChange={(e) => setComment(e.target.value)}
          required
        />

        <div className="flex items-center justify-end gap-3 pt-3 border-t border-dark-750">
          <Button variant="outline" size="sm" type="button" onClick={onClose} disabled={isLoading}>
            Cancel
          </Button>
          <Button variant="primary" size="sm" type="submit" isLoading={isLoading} leftIcon={CheckCircle2}>
            Submit Review
          </Button>
        </div>
      </form>
    </Modal>
  );
};
