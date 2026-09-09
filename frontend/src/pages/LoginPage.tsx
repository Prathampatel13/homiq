import React, { useState } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { Lock, User as UserIcon, AlertCircle, Loader2, ArrowRight, Eye, EyeOff } from 'lucide-react';
import { authApi } from '../api/auth';
import { useAuthStore } from '../store/useAuthStore';
import { HomiQLogo } from '../components/brand/HomiQLogo';

export const LoginPage: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { login } = useAuthStore();

  const [identifier, setIdentifier] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!identifier.trim() || !password.trim()) {
      setError('Please enter your email, mobile number, or username and password.');
      return;
    }

    try {
      setLoading(true);
      setError(null);
      const res = await authApi.login({ identifier, password });
      
      // Save tokens and user in store
      login(res.access_token, res.refresh_token, res.user);

      // Redirect based on role or search query
      const params = new URLSearchParams(location.search);
      const redirect = params.get('redirect');

      if (redirect) {
        navigate(redirect);
      } else {
        const role = String(res.user.role || '').toUpperCase();
        if (role.includes('ADMIN') || res.user.is_superuser) {
          navigate('/admin/dashboard');
        } else if (role.includes('TECH')) {
          navigate('/provider/dashboard');
        } else if (role.includes('COMP')) {
          navigate('/company/dashboard');
        } else {
          navigate('/customer/dashboard');
        }
      }
    } catch (err: any) {
      console.error('Login error:', err);
      const detail = err?.response?.data?.detail;
      if (typeof detail === 'string') {
        setError(detail);
      } else if (Array.isArray(detail)) {
        setError(detail.map((d: any) => d.msg || 'Invalid field').join(', '));
      } else {
        setError('Invalid credentials or account suspended. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };



  return (
    <div className="min-h-screen bg-[#F8FAFC] flex flex-col justify-center py-12 sm:px-6 lg:px-8 text-slate-900 relative selection:bg-sage-500/20 selection:text-slate-900">
      <div className="sm:mx-auto sm:w-full sm:max-w-md text-center space-y-4">
        <HomiQLogo variant="stacked" size="lg" showTagline className="mx-auto" />
        <h2 className="text-xl sm:text-2xl font-extrabold tracking-tight text-slate-900 mt-4">
          Sign In to Your Workspace
        </h2>
        <p className="text-xs text-slate-600">
          Enter your registered credentials to access your home or fleet console.
        </p>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md px-4 sm:px-0">
        <div className="p-6 sm:p-8 rounded-3xl bg-white border border-slate-200 shadow-modal space-y-6">
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-xs font-bold text-slate-700 mb-1.5">Email, Mobile Number or Username</label>
              <div className="relative">
                <UserIcon className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
                <input
                  type="text"
                  value={identifier}
                  onChange={(e) => setIdentifier(e.target.value)}
                  placeholder="Enter email, mobile number or username"
                  className="input-field pl-10"
                  required
                />
              </div>
            </div>

            <div>
              <div className="flex items-center justify-between mb-1.5">
                <label className="block text-xs font-bold text-slate-700">Password</label>
                <Link to="/forgot-password" className="text-[11px] text-sage-600 hover:text-sage-700 font-semibold hover:underline">
                  Forgot Password?
                </Link>
              </div>
              <div className="relative">
                <Lock className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
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
                  className="absolute right-3.5 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-700 transition-colors"
                >
                  {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
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
              {loading ? (
                <>
                  <Loader2 className="w-3.5 h-3.5 animate-spin" />
                  <span>Authenticating...</span>
                </>
              ) : (
                <>
                  <span>Sign In</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </>
              )}
            </button>
          </form>

          <div className="pt-4 border-t border-slate-100 text-center text-xs text-slate-600">
            Don't have a HomiQ account yet?{' '}
            <Link to="/register" className="text-sage-600 hover:text-sage-700 font-bold hover:underline">
              Create Account
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
};
