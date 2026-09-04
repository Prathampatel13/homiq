import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { User, Mail, Lock, Phone, AlertCircle, Loader2, ArrowRight, ShieldCheck, Building2, Wrench, Eye, EyeOff } from 'lucide-react';
import { authApi } from '../api/auth';
import { useAuthStore } from '../store/useAuthStore';
import { HomiQLogo } from '../components/brand/HomiQLogo';

export const RegisterPage: React.FC = () => {
  const navigate = useNavigate();
  const { login } = useAuthStore();

  const [role, setRole] = useState<'customer' | 'technician' | 'company'>('customer');
  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [phone, setPhone] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!fullName.trim() || !email.trim() || !password.trim()) {
      setError('Please complete all required fields.');
      return;
    }

    try {
      setLoading(true);
      setError(null);

      const res = await authApi.register({
        full_name: fullName,
        email,
        phone: phone || undefined,
        password,
        role: role.toUpperCase(),
      });

      login(res.access_token, res.refresh_token, res.user);

      if (role === 'technician') {
        navigate('/provider/dashboard');
      } else if (role === 'company') {
        navigate('/company/dashboard');
      } else {
        navigate('/customer/dashboard');
      }
    } catch (err: any) {
      console.error('Registration failed:', err);
      const detail = err?.response?.data?.detail;
      if (typeof detail === 'string') {
        setError(detail);
      } else if (Array.isArray(detail)) {
        setError(detail.map((d: any) => `${d.loc ? d.loc.slice(-1) + ': ' : ''}${d.msg || 'Invalid field'}`).join(', '));
      } else if (err?.message === 'Network Error' || !err?.response) {
        setError(`Network Error: Cannot reach backend at ${authApi ? import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000' : ''}. Check if the backend is awake or VITE_API_BASE_URL is set.`);
      } else {
        setError(err?.response?.data?.message || `Failed to create account (${err?.response?.status || 'Error'}). Please check your inputs.`);
      }
    } finally {
      setLoading(false);
    }
  };


  return (
    <div className="min-h-screen bg-dark-950 flex flex-col justify-center py-12 sm:px-6 lg:px-8 text-white relative">
      <div className="sm:mx-auto sm:w-full sm:max-w-md text-center space-y-4">
        <HomiQLogo variant="stacked" size="lg" showTagline className="mx-auto" />
        <h2 className="text-xl sm:text-2xl font-bold tracking-tight text-white mt-4">
          Create Your HomiQ Account
        </h2>
        <p className="text-xs text-slate-400">
          Select your account type to access specialized services and dispatch tools.
        </p>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-lg px-4 sm:px-0">
        <div className="p-6 sm:p-8 rounded-3xl bg-dark-900 border border-dark-750 shadow-modal space-y-6">
          {/* Account Role Selector */}
          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-2">Account Type</label>
            <div className="grid grid-cols-3 gap-2 p-1 rounded-2xl bg-dark-850 border border-dark-750">
              {[
                { id: 'customer', label: 'Customer', icon: ShieldCheck },
                { id: 'technician', label: 'Technician', icon: Wrench },
                { id: 'company', label: 'Company', icon: Building2 },
              ].map((r) => {
                const Icon = r.icon;
                const isSelected = role === r.id;
                return (
                  <button
                    key={r.id}
                    type="button"
                    onClick={() => setRole(r.id as any)}
                    className={`py-2 px-2 rounded-xl text-xs font-semibold flex items-center justify-center gap-1.5 transition-all ${
                      isSelected
                        ? 'bg-sage-400 text-dark-950 shadow-accent font-bold'
                        : 'text-slate-400 hover:text-white'
                    }`}
                  >
                    <Icon className="w-3.5 h-3.5" />
                    <span>{r.label}</span>
                  </button>
                );
              })}
            </div>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1.5">
                {role === 'company' ? 'Company Legal Name *' : 'Full Name *'}
              </label>
              <div className="relative">
                <User className="w-4 h-4 text-slate-500 absolute left-3.5 top-1/2 -translate-y-1/2" />
                <input
                  type="text"
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  placeholder={
                    role === 'company' ? 'Acme Facilities Corp' : 
                    role === 'technician' ? 'Jane Smith' : 
                    'John Doe'
                  }
                  className="input-field pl-10"
                  required
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1.5">Email Address *</label>
              <div className="relative">
                <Mail className="w-4 h-4 text-slate-500 absolute left-3.5 top-1/2 -translate-y-1/2" />
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="name@example.com"
                  className="input-field pl-10"
                  required
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1.5">Phone Number (Optional)</label>
              <div className="relative">
                <Phone className="w-4 h-4 text-slate-500 absolute left-3.5 top-1/2 -translate-y-1/2" />
                <input
                  type="tel"
                  inputMode="numeric"
                  value={phone}
                  onChange={(e) => setPhone(e.target.value.replace(/[^0-9]/g, ''))}
                  placeholder="9876543210"
                  className="input-field pl-10"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1.5">Password *</label>
              <div className="relative">
                <Lock className="w-4 h-4 text-slate-500 absolute left-3.5 top-1/2 -translate-y-1/2" />
                <input
                  type={showPassword ? "text" : "password"}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  className="input-field pl-10 pr-10"
                  required
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3.5 top-1/2 -translate-y-1/2 text-slate-500 hover:text-slate-300 transition-colors"
                >
                  {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
            </div>

            {error && (
              <div className="p-3 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-400 text-xs flex items-center gap-2">
                <AlertCircle className="w-4 h-4 shrink-0" />
                <span>{error}</span>
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              className="w-full btn-primary text-xs py-3 font-semibold flex items-center justify-center gap-1.5 shadow-subtle hover:shadow-metallic disabled:opacity-40"
            >
              {loading ? (
                <>
                  <Loader2 className="w-3.5 h-3.5 animate-spin" />
                  <span>Creating Account...</span>
                </>
              ) : (
                <>
                  <span>Create Account</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </>
              )}
            </button>
          </form>



          <div className="pt-4 border-t border-dark-750 text-center text-xs text-slate-400">
            Already have a HomiQ account?{' '}
            <Link to="/login" className="text-sage-300 hover:text-white font-semibold">
              Sign In
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
};
