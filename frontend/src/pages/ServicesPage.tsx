import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Layers, 
  Search, 
  Clock, 
  Wrench, 
  ChevronRight, 
  ArrowRight,
  Filter,
  Sparkles,
  Droplet,
  Zap,
  Wind,
  Monitor,
  Paintbrush,
  Bath,
  Home,
  ShieldCheck,
  TreePine,
  DoorOpen
} from 'lucide-react';
import { servicesApi } from '../api/services';
import { Service, ServiceCategory } from '../types';
import { EmptyState } from '../components/ui/EmptyState';
import { LoadingState } from '../components/ui/LoadingState';

export const ServicesPage: React.FC = () => {
  const navigate = useNavigate();
  const [categories, setCategories] = useState<ServiceCategory[]>([]);
  const [services, setServices] = useState<Service[]>([]);
  const [selectedCategory, setSelectedCategory] = useState<number | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const staticCategories = [
          { id: 1, name: 'Plumbing', description: '', icon: 'Droplet' },
          { id: 2, name: 'Electrical', description: '', icon: 'Zap' },
          { id: 3, name: 'AC & Cooling', description: '', icon: 'Wind' },
          { id: 4, name: 'Appliances', description: '', icon: 'Monitor' },
          { id: 5, name: 'Carpentry', description: '', icon: 'Wrench' },
          { id: 6, name: 'Cleaning', description: '', icon: 'Sparkles' },
          { id: 7, name: 'Painting', description: '', icon: 'Paintbrush' },
          { id: 8, name: 'Bathroom', description: '', icon: 'Bath' },
          { id: 9, name: 'Home Maintenance', description: '', icon: 'Home' },
          { id: 10, name: 'Security & Smart Home', description: '', icon: 'ShieldCheck' },
          { id: 11, name: 'Outdoor & Garden', description: '', icon: 'TreePine' },
          { id: 12, name: 'Windows & Doors', description: '', icon: 'DoorOpen' },
        ];
        
        const staticServices = [
          { id: 101, category_id: 1, name: 'Plumbing', description: 'Tap Repair, Pipe Leakage, Drain Cleaning, Sink Repair, Toilet Repair, Water Tank Repair, Bathroom Plumbing', price: 299, duration_minutes: 30 },
          { id: 102, category_id: 2, name: 'Electrical', description: 'Switch & Socket Repair, Fan Installation, Light Installation, Wiring Repair, MCB Repair, Short-Circuit Repair, Inverter Installation', price: 199, duration_minutes: 30 },
          { id: 103, category_id: 3, name: 'AC & Cooling', description: 'AC Service, AC Repair, AC Installation, AC Gas Refill, AC Cleaning, Cooler Repair', price: 499, duration_minutes: 60 },
          { id: 104, category_id: 4, name: 'Appliances', description: 'Refrigerator Repair, Washing Machine Repair, Microwave Repair, Geyser Repair, Water Purifier Service', price: 349, duration_minutes: 45 },
          { id: 105, category_id: 5, name: 'Carpentry', description: 'Furniture Repair, Door Repair, Lock Installation, Cabinet Repair, Shelf Installation, Bed Repair', price: 249, duration_minutes: 60 },
          { id: 106, category_id: 6, name: 'Cleaning', description: 'Full Home Cleaning, Kitchen Cleaning, Bathroom Cleaning, Sofa Cleaning, Carpet Cleaning, Floor Cleaning', price: 999, duration_minutes: 120 },
          { id: 107, category_id: 7, name: 'Painting', description: 'Room Painting, Full Home Painting, Wall Touch-up, Exterior Painting, Waterproof Painting', price: 1499, duration_minutes: 240 },
          { id: 108, category_id: 8, name: 'Bathroom', description: 'Bathroom Deep Cleaning, Shower Repair, Toilet Repair, Basin Repair, Exhaust Fan Installation', price: 399, duration_minutes: 60 },
          { id: 109, category_id: 9, name: 'Home Maintenance', description: 'General Inspection, Minor Repairs, Wall Repair, Grouting, Waterproofing, Home Inspection', price: 499, duration_minutes: 90 },
          { id: 110, category_id: 10, name: 'Security & Smart Home', description: 'CCTV Installation, Smart Lock Installation, Doorbell Installation, Wi-Fi Camera Setup', price: 599, duration_minutes: 90 },
          { id: 111, category_id: 11, name: 'Outdoor & Garden', description: 'Garden Maintenance, Lawn Cleaning, Plant Maintenance, Balcony Cleaning', price: 349, duration_minutes: 60 },
          { id: 112, category_id: 12, name: 'Windows & Doors', description: 'Door Alignment, Door Handle Repair, Window Repair, Glass Replacement, Mosquito Net Installation', price: 299, duration_minutes: 45 },
        ];

        setCategories(staticCategories as any);
        setServices(staticServices as any);
      } catch (err) {
        console.error('Failed to load services catalog:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  const filteredServices = services.filter((s) => {
    const matchCat = selectedCategory === null || s.category_id === selectedCategory;
    const matchQuery = !searchQuery || s.name.toLowerCase().includes(searchQuery.toLowerCase()) || (s.description && s.description.toLowerCase().includes(searchQuery.toLowerCase()));
    return matchCat && matchQuery;
  });

  return (
    <div className="min-h-screen bg-dark-950 py-12 text-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="max-w-3xl mb-12">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-dark-850 border border-dark-750 mb-3">
            <Layers className="w-3.5 h-3.5 text-sage-400" />
            <span className="text-xs font-mono tracking-wider text-slate-300 uppercase">OFFICIAL SERVICE CATALOG</span>
          </div>
          <h1 className="text-3xl sm:text-4xl lg:text-5xl font-extrabold tracking-tight text-white">
            Master Architectural Services
          </h1>
          <p className="text-sm text-slate-400 mt-2">
            Transparent, upfront rates. Background-verified master technicians with SmartVerify™ cryptographic validation.
          </p>
        </div>

        {/* Search & Category Filter Bar */}
        <div className="p-4 rounded-3xl bg-dark-900 border border-dark-750 mb-10 shadow-card flex flex-col md:flex-row gap-4 justify-between items-center">
          {/* Search Input */}
          <div className="relative w-full md:w-80">
            <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search services, repairs..."
              className="input-field pl-10 text-xs py-2.5"
            />
          </div>

          {/* Categories Pills */}
          <div className="flex items-center gap-2 overflow-x-auto w-full md:w-auto pb-2 md:pb-0 scrollbar-none">
            <button
              onClick={() => setSelectedCategory(null)}
              className={`px-3.5 py-1.5 rounded-xl text-xs font-semibold whitespace-nowrap transition-all border ${
                selectedCategory === null
                  ? 'bg-sage-400 text-dark-950 border-sage-400 shadow-accent'
                  : 'bg-dark-850 text-slate-400 hover:text-white border-dark-750 hover:border-dark-700'
              }`}
            >
              All Categories
            </button>
            {categories.map((c) => (
              <button
                key={c.id}
                onClick={() => setSelectedCategory(c.id)}
                className={`px-3.5 py-1.5 rounded-xl text-xs font-semibold whitespace-nowrap transition-all border ${
                  selectedCategory === c.id
                    ? 'bg-sage-400 text-dark-950 border-sage-400 shadow-accent'
                    : 'bg-dark-850 text-slate-400 hover:text-white border-dark-750 hover:border-dark-700'
                }`}
              >
                {c.name}
              </button>
            ))}
          </div>
        </div>

        {/* Services List */}
        {loading ? (
          <LoadingState message="Loading architectural service catalog..." />
        ) : filteredServices.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredServices.map((service) => {
              const iconMap: Record<number, any> = {
                1: Droplet,
                2: Zap,
                3: Wind,
                4: Monitor,
                5: Wrench,
                6: Sparkles,
                7: Paintbrush,
                8: Bath,
                9: Home,
                10: ShieldCheck,
                11: TreePine,
                12: DoorOpen,
              };
              const Icon = service.category_id ? iconMap[service.category_id as number] || Wrench : Wrench;

              return (
              <div
                key={service.id}
                onClick={() => navigate(`/booking/new?service_id=${service.id}`)}
                className="group p-6 rounded-3xl bg-dark-900/90 hover:bg-dark-850 border border-dark-750 hover:border-dark-700 transition-all duration-200 cursor-pointer flex flex-col justify-between shadow-card"
              >
                <div>
                  <div className="flex items-center justify-between mb-4">
                    <div className="w-12 h-12 rounded-2xl bg-dark-800 group-hover:bg-sage-400/15 border border-dark-750 group-hover:border-sage-400/30 flex items-center justify-center text-sage-400 transition-colors">
                      <Icon className="w-6 h-6" />
                    </div>
                    <span className="text-xs font-mono font-bold text-white px-2.5 py-1 rounded-lg bg-dark-800 border border-dark-750">
                      Starts ₹{(service.price || service.base_price || 0).toFixed(2)}
                    </span>
                  </div>

                  <h3 className="text-base font-bold text-white tracking-tight group-hover:text-sage-300 transition-colors mb-2">
                    {service.name}
                  </h3>
                  <p className="text-xs text-slate-400 leading-relaxed">
                    {service.description || 'Certified multi-point checkup, troubleshooting, precision servicing and workmanship guarantee.'}
                  </p>
                </div>

                <div className="pt-5 mt-5 border-t border-dark-750/70 flex items-center justify-between text-xs text-slate-400 font-mono">
                  <span className="flex items-center gap-1.5">
                    <Clock className="w-3.5 h-3.5 text-sage-400" />
                    <span>~{service.duration_minutes || 60} mins</span>
                  </span>
                  <span className="text-sage-400 group-hover:translate-x-1 transition-transform flex items-center gap-1 font-semibold">
                    <span>Book Service</span>
                    <ChevronRight className="w-3.5 h-3.5" />
                  </span>
                </div>
              </div>
            )})}
          </div>
        ) : (
          <EmptyState
            title="No Services Found"
            description="Try adjusting your search query or select another category filter."
            actionLabel="Reset Filters"
            onAction={() => {
              setSearchQuery('');
              setSelectedCategory(null);
            }}
          />
        )}
      </div>
    </div>
  );
};
