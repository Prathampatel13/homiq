import React, { useState, useEffect } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { Search, Star, Clock, Filter, Sparkles, ArrowRight, ShieldCheck } from 'lucide-react';
import { servicesApi } from '../api/services';
import { Service, ServiceCategory } from '../types';
import { Button } from '../components/ui/Button';
import { Card } from '../components/ui/Card';
import { LoadingState, CardSkeleton } from '../components/ui/LoadingState';
import { EmptyState } from '../components/ui/EmptyState';

export const ServicesPage: React.FC = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const navigate = useNavigate();

  const [categories, setCategories] = useState<ServiceCategory[]>([]);
  const [services, setServices] = useState<Service[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  const selectedCategory = searchParams.get('category');
  const searchParam = searchParams.get('search') || '';
  const [searchQuery, setSearchQuery] = useState(searchParam);

  useEffect(() => {
    servicesApi
      .getCategories()
      .then(setCategories)
      .catch(() => setCategories([]));
  }, []);

  useEffect(() => {
    setIsLoading(true);
    servicesApi
      .getServices({
        category_id: selectedCategory ? Number(selectedCategory) : undefined,
        search: searchParam || undefined,
      })
      .then((data) => setServices(data))
      .catch(() => setServices([]))
      .finally(() => setIsLoading(false));
  }, [selectedCategory, searchParam]);

  const handleCategorySelect = (categoryId: number | null) => {
    const params = new URLSearchParams(searchParams);
    if (categoryId) {
      params.set('category', String(categoryId));
    } else {
      params.delete('category');
    }
    setSearchParams(params);
  };

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    const params = new URLSearchParams(searchParams);
    if (searchQuery.trim()) {
      params.set('search', searchQuery.trim());
    } else {
      params.delete('search');
    }
    setSearchParams(params);
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-8">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4 pb-6 border-b border-dark-750">
        <div>
          <p className="text-xs font-mono uppercase tracking-widest text-brand-400 font-semibold mb-1">
            Standardized Quality Catalog
          </p>
          <h1 className="text-3xl font-bold text-white tracking-tight">Services & Solutions</h1>
          <p className="text-xs sm:text-sm text-slate-400 mt-1">
            Transparent pricing, vetted professionals, and guaranteed quality.
          </p>
        </div>

        {/* Search Input */}
        <form onSubmit={handleSearch} className="w-full md:w-80">
          <div className="relative">
            <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              placeholder="Search catalog..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full bg-dark-850 border border-dark-700/80 rounded-xl pl-10 pr-4 py-2 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-brand-500 transition-colors"
            />
          </div>
        </form>
      </div>

      {/* Category Pills */}
      <div className="flex items-center gap-2 overflow-x-auto pb-2 scrollbar-none">
        <button
          onClick={() => handleCategorySelect(null)}
          className={`px-3.5 py-1.5 rounded-xl text-xs font-medium transition-all whitespace-nowrap ${
            !selectedCategory
              ? 'bg-brand-500 text-white shadow-subtle'
              : 'bg-dark-850 hover:bg-dark-800 text-slate-300 border border-dark-700'
          }`}
        >
          All Categories
        </button>
        {categories.map((cat) => {
          const isSelected = selectedCategory === String(cat.id);
          return (
            <button
              key={cat.id}
              onClick={() => handleCategorySelect(cat.id)}
              className={`px-3.5 py-1.5 rounded-xl text-xs font-medium transition-all whitespace-nowrap flex items-center gap-1.5 ${
                isSelected
                  ? 'bg-brand-500 text-white shadow-subtle'
                  : 'bg-dark-850 hover:bg-dark-800 text-slate-300 border border-dark-700'
              }`}
            >
              <span>{cat.name}</span>
            </button>
          );
        })}
      </div>

      {/* Services Grid */}
      {isLoading ? (
        <CardSkeleton count={6} />
      ) : services.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {services.map((srv) => (
            <Card key={srv.id} className="flex flex-col justify-between group hover:border-dark-750">
              <div className="space-y-3">
                <div className="flex items-start justify-between">
                  <span className="px-2.5 py-0.5 rounded-full text-[10px] font-medium bg-dark-800 text-slate-300 border border-dark-700">
                    {srv.category_name || 'Standard Service'}
                  </span>
                  <div className="flex items-center gap-1 text-xs font-semibold text-amber-400 font-mono">
                    <Star className="w-3.5 h-3.5 fill-amber-400" />
                    <span>{(srv.rating_avg || 4.9).toFixed(1)}</span>
                    <span className="text-[10px] text-slate-500">({srv.total_reviews || 12})</span>
                  </div>
                </div>

                <h3 className="text-base font-bold text-white group-hover:text-brand-400 transition-colors">
                  {srv.name}
                </h3>
                <p className="text-xs text-slate-400 line-clamp-3 leading-relaxed">
                  {srv.description || 'Certified multi-point inspection, diagnostics, and repairs.'}
                </p>

                <div className="flex items-center gap-4 text-xs text-slate-400 pt-1">
                  <div className="flex items-center gap-1">
                    <Clock className="w-3.5 h-3.5 text-slate-500" />
                    <span>{srv.duration_minutes || 60} mins</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
                    <span>Verified Pro</span>
                  </div>
                </div>
              </div>

              <div className="pt-4 mt-4 border-t border-dark-800/80 flex items-center justify-between">
                <div>
                  <span className="text-[10px] text-slate-500 block">Upfront Price</span>
                  <span className="text-lg font-bold text-white font-mono">
                    ₹{(srv.price || srv.base_price || 499).toFixed(2)}
                  </span>
                </div>
                <Button
                  variant="primary"
                  size="sm"
                  onClick={() => navigate(`/booking/new?service_id=${srv.id}`)}
                  rightIcon={ArrowRight}
                >
                  Book Service
                </Button>
              </div>
            </Card>
          ))}
        </div>
      ) : (
        <EmptyState
          icon={Search}
          title="No services found"
          description="We couldn't find any services matching your search or selected category."
          actionLabel="Clear Filters"
          onAction={() => {
            setSearchQuery('');
            setSearchParams({});
          }}
        />
      )}
    </div>
  );
};
