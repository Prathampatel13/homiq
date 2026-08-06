import React, { useState, useEffect } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Search, Star, Clock, ShieldCheck, ArrowRight, Sparkles, Filter } from 'lucide-react';
import { servicesApi } from '../api/services';
import { Service, ServiceCategory } from '../types';
import { Button } from '../components/ui/Button';
import { Card } from '../components/ui/Card';

export const ServicesPage: React.FC = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const initialCategory = searchParams.get('category')
    ? parseInt(searchParams.get('category') || '0', 10)
    : undefined;

  const [categories, setCategories] = useState<ServiceCategory[]>([]);
  const [services, setServices] = useState<Service[]>([]);
  const [selectedCategory, setSelectedCategory] = useState<number | undefined>(initialCategory);
  const [searchQuery, setSearchQuery] = useState('');
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    fetchInitialData();
  }, []);

  useEffect(() => {
    fetchServices(selectedCategory);
  }, [selectedCategory]);

  const fetchInitialData = async () => {
    try {
      const categoriesData = await servicesApi.getCategories().catch(() => []);
      setCategories(Array.isArray(categoriesData) ? categoriesData : []);
    } catch (err) {
      console.error('Failed to load categories:', err);
    }
  };

  const fetchServices = async (catId?: number) => {
    try {
      setIsLoading(true);
      const servicesData = await servicesApi.getServices(catId);
      setServices(Array.isArray(servicesData) ? servicesData : []);
    } catch (err) {
      console.error('Failed to load services:', err);
      setServices([]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleCategorySelect = (id?: number) => {
    setSelectedCategory(id);
    if (id) {
      setSearchParams({ category: id.toString() });
    } else {
      setSearchParams({});
    }
  };

  const safeServices = Array.isArray(services) ? services : [];
  const filteredServices = safeServices.filter((s) =>
    s.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    (s.description && s.description.toLowerCase().includes(searchQuery.toLowerCase()))
  );

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-10">
      {/* ── 1. Page Header & Search ──────────────────────────────────────────── */}
      <div className="text-center space-y-4 max-w-3xl mx-auto">
        <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-brand-500/10 border border-brand-500/20 text-brand-400 text-xs font-semibold">
          <Sparkles className="w-3.5 h-3.5" /> Certified Expert Maintenance Services
        </div>
        <h1 className="text-4xl font-extrabold text-white tracking-tight">
          Explore On-Demand <span className="gradient-text">Home Services</span>
        </h1>
        <p className="text-slate-400 text-sm">
          Book verified technicians for plumbing, electrical, AC repair, home cleaning, and painting.
        </p>

        {/* Search Bar */}
        <div className="relative max-w-xl mx-auto pt-2">
          <Search className="w-5 h-5 text-slate-400 absolute left-4 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Search for AC repair, ceiling fan, tap leaking, deep cleaning..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-12 pr-4 py-3.5 bg-slate-900/90 border border-slate-800 rounded-2xl text-slate-100 placeholder-slate-500 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500 shadow-xl shadow-slate-950/50"
          />
        </div>
      </div>

      {/* ── 2. Category Filter Chips ────────────────────────────────────────── */}
      <div className="flex items-center gap-2 overflow-x-auto pb-2 scrollbar-none justify-center">
        <button
          onClick={() => handleCategorySelect(undefined)}
          className={`px-4 py-2 rounded-xl text-xs font-semibold whitespace-nowrap transition-all ${
            selectedCategory === undefined
              ? 'bg-gradient-to-r from-brand-600 to-indigo-600 text-white shadow-lg shadow-brand-500/25'
              : 'bg-slate-900 text-slate-300 border border-slate-800 hover:border-slate-700'
          }`}
        >
          All Categories
        </button>
        {categories.map((cat) => (
          <button
            key={cat.id}
            onClick={() => handleCategorySelect(cat.id)}
            className={`px-4 py-2 rounded-xl text-xs font-semibold whitespace-nowrap transition-all ${
              selectedCategory === cat.id
                ? 'bg-gradient-to-r from-brand-600 to-indigo-600 text-white shadow-lg shadow-brand-500/25'
                : 'bg-slate-900 text-slate-300 border border-slate-800 hover:border-slate-700'
            }`}
          >
            {cat.name}
          </button>
        ))}
      </div>

      {/* ── 3. Services Grid ────────────────────────────────────────────────── */}
      {isLoading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[1, 2, 3, 4, 5, 6].map((i) => (
            <div key={i} className="glass-card p-6 h-64 animate-pulse bg-slate-900/50" />
          ))}
        </div>
      ) : filteredServices.length === 0 ? (
        <Card className="text-center py-16 space-y-4">
          <Filter className="w-10 h-10 text-slate-500 mx-auto" />
          <h3 className="text-lg font-bold text-white">No Services Found</h3>
          <p className="text-xs text-slate-400 max-w-sm mx-auto">
            We couldn't find any services matching "{searchQuery}". Try searching for electrical or cleaning.
          </p>
          <Button variant="secondary" size="sm" onClick={() => { setSearchQuery(''); setSelectedCategory(undefined); }}>
            Reset Filters
          </Button>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredServices.map((service) => (
            <motion.div
              key={service.id}
              whileHover={{ y: -4 }}
              transition={{ duration: 0.2 }}
            >
              <Card className="p-6 space-y-5 border-slate-800 flex flex-col justify-between h-full relative group">
                <div className="space-y-3">
                  <div className="flex items-start justify-between gap-4">
                    <h3 className="text-lg font-bold text-white group-hover:text-brand-400 transition-colors">
                      {service.name}
                    </h3>
                    <div className="flex items-center gap-1 text-amber-400 text-xs font-bold shrink-0 bg-amber-400/10 px-2 py-1 rounded-lg border border-amber-400/20">
                      <Star className="w-3.5 h-3.5 fill-amber-400" />
                      <span>{service.rating_avg || 4.8}</span>
                      <span className="text-slate-500 font-normal">({service.total_reviews || 42})</span>
                    </div>
                  </div>

                  <p className="text-slate-400 text-xs line-clamp-2">
                    {service.description || 'Professional home service with guaranteed quality and verified technicians.'}
                  </p>
                </div>

                <div className="space-y-4 pt-4 border-t border-slate-800/80">
                  <div className="flex items-center justify-between text-xs text-slate-400">
                    <div className="flex items-center gap-1.5">
                      <Clock className="w-3.5 h-3.5 text-brand-400" />
                      <span>{service.duration_minutes || 60} mins</span>
                    </div>
                    <div className="flex items-center gap-1 text-emerald-400 font-medium">
                      <ShieldCheck className="w-3.5 h-3.5" />
                      <span>SmartVerify Protected</span>
                    </div>
                  </div>

                  <div className="flex items-center justify-between pt-1">
                    <div>
                      <span className="text-[10px] text-slate-500 uppercase font-semibold">Starting At</span>
                      <div className="text-xl font-extrabold text-white">₹{service.price || 499}</div>
                    </div>
                    <Link to={`/booking/new?serviceId=${service.id}`}>
                      <Button variant="primary" size="sm" rightIcon={<ArrowRight className="w-3.5 h-3.5" />}>
                        Book Now
                      </Button>
                    </Link>
                  </div>
                </div>
              </Card>
            </motion.div>
          ))}
        </div>
      )}
    </div>
  );
};
