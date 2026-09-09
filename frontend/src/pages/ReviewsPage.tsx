import React, { useEffect, useState } from 'react';
import { reviewsApi } from '../api/reviews';
import { technicianApi } from '../api/technician';
import { useAuthStore } from '../store/useAuthStore';
import { UserRole, Review } from '../types';
import { Star, Calendar, MessageSquare } from 'lucide-react';
import { LoadingState } from '../components/ui/LoadingState';
import { EmptyState } from '../components/ui/EmptyState';

export const ReviewsPage: React.FC = () => {
  const { user, getEffectiveRole } = useAuthStore();
  const role = getEffectiveRole();
  const [reviews, setReviews] = useState<Review[]>([]);
  const [originalReviews, setOriginalReviews] = useState<Review[]>([]);
  const [loading, setLoading] = useState(true);
  const [summary, setSummary] = useState<any>(null);
  
  const [ratingFilter, setRatingFilter] = useState<number | null>(null);
  const [serviceFilter, setServiceFilter] = useState<string>('');

  useEffect(() => {
    const fetchReviews = async () => {
      try {
        setLoading(true);
        if (role === UserRole.TECHNICIAN && user?.id) {
          const profile = await technicianApi.getProfile();
          const techId = profile.id;
          const res = await reviewsApi.getTechnicianReviews(techId);
          const items = Array.isArray(res) ? res : ((res as any).items || []);
          setReviews(items);
          setOriginalReviews(items);
          
          try {
             const sum = await reviewsApi.getTechnicianSummary(techId);
             setSummary(sum);
          } catch(e) {
             console.error('Failed to fetch summary:', e);
          }
        } else if (role === UserRole.CUSTOMER && user?.id) {
           const res = await reviewsApi.getReviews({ offset: 0, limit: 100 });
           const items = Array.isArray(res) ? res : (res.items || []);
           const myReviews = items.filter((r: Review) => r.customer_id === user.id);
           setReviews(myReviews);
           setOriginalReviews(myReviews);
        } else {
           const res = await reviewsApi.getReviews({ offset: 0, limit: 100 });
           const items = Array.isArray(res) ? res : (res.items || []);
           setReviews(items);
           setOriginalReviews(items);
        }
      } catch (err) {
        console.error('Failed to fetch reviews:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchReviews();
  }, [role, user?.id]);

  const uniqueServices = Array.from(new Set(originalReviews.map(r => r.service_name).filter(Boolean)));

  const filteredReviews = originalReviews.filter(r => {
    if (ratingFilter !== null && r.rating < ratingFilter) return false;
    if (serviceFilter && r.service_name !== serviceFilter) return false;
    return true;
  });

  if (loading) return <LoadingState message="Loading Reviews..." />;

  return (
    <div className="min-h-screen bg-dark-950 py-8 text-white selection:bg-sage-400/20 selection:text-white">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 space-y-6">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Reviews & Ratings</h1>
          <p className="text-sm text-slate-400 mt-1">
            {role === UserRole.TECHNICIAN 
              ? 'See what customers are saying about your service.'
              : 'Your feedback and reviews.'}
          </p>
        </div>

        {role === UserRole.TECHNICIAN && (
          <div className="flex flex-col sm:flex-row gap-4 items-center mb-6">
            <select
              className="bg-dark-900 border border-dark-750 text-white text-sm rounded-xl px-4 py-2 focus:outline-none focus:border-sage-400 w-full sm:w-auto"
              value={ratingFilter === null ? '' : ratingFilter.toString()}
              onChange={(e) => {
                const val = e.target.value;
                setRatingFilter(val ? parseInt(val, 10) : null);
              }}
            >
              <option value="">All Ratings</option>
              <option value="5">5 Stars</option>
              <option value="4">4 Stars & Above</option>
              <option value="3">3 Stars & Above</option>
            </select>

            <select
              className="bg-dark-900 border border-dark-750 text-white text-sm rounded-xl px-4 py-2 focus:outline-none focus:border-sage-400 w-full sm:w-auto"
              value={serviceFilter}
              onChange={(e) => setServiceFilter(e.target.value)}
            >
              <option value="">All Services</option>
              {uniqueServices.map((service, idx) => (
                <option key={idx} value={service as string}>{service}</option>
              ))}
            </select>
          </div>
        )}

        {role === UserRole.TECHNICIAN && summary && (
           <div className="p-6 rounded-3xl bg-dark-900 border border-dark-750 flex items-center justify-between gap-6 shadow-card">
              <div>
                <p className="text-sm font-semibold text-slate-300">Average Rating</p>
                <div className="flex items-center gap-2 mt-1">
                  <Star className="w-6 h-6 text-sage-400 fill-sage-400" />
                  <span className="text-3xl font-bold">{summary.rating_avg?.toFixed(1) || '0.0'}</span>
                </div>
              </div>
              <div className="text-right">
                <p className="text-sm font-semibold text-slate-300">Total Reviews</p>
                <p className="text-3xl font-bold text-white mt-1">{summary.total_reviews || 0}</p>
              </div>
           </div>
        )}

        {filteredReviews.length === 0 ? (
          <EmptyState
            title="No reviews found"
            description="Try adjusting your filters or wait for more customer reviews."
            icon={MessageSquare}
          />
        ) : (
          <div className="space-y-4">
            {filteredReviews.map((review) => (
              <div key={review.id} className="p-5 rounded-2xl bg-dark-900 border border-dark-750 hover:border-dark-700 transition-colors shadow-card flex flex-col gap-4">
                <div className="flex items-start justify-between gap-4">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-full bg-sage-400/15 border border-sage-400/30 flex items-center justify-center text-sage-400 font-bold">
                      {review.customer_name?.charAt(0)?.toUpperCase() || 'C'}
                    </div>
                    <div>
                      <p className="font-semibold text-white">{review.customer_name || 'Customer'}</p>
                      <div className="flex items-center gap-2 text-[11px] text-slate-400 font-mono mt-0.5">
                        <Calendar className="w-3 h-3" />
                        <span>{new Date(review.created_at).toLocaleDateString()}</span>
                        {review.service_name && (
                          <>
                            <span>•</span>
                            <span className="text-sage-300">{review.service_name}</span>
                          </>
                        )}
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center gap-1 bg-dark-850 px-2 py-1 rounded-lg border border-dark-750">
                    <Star className="w-3.5 h-3.5 text-sage-400 fill-sage-400" />
                    <span className="text-xs font-bold">{review.rating.toFixed(1)}</span>
                  </div>
                </div>
                {review.comment && (
                  <div className="pt-4 border-t border-dark-800">
                    <p className="text-sm text-slate-300 leading-relaxed">"{review.comment}"</p>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
