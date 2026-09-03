import React, { useState } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { Lock, User as UserIcon, AlertCircle, Loader2, ArrowRight, Eye, EyeOff } from 'lucide-react';
import { authApi } from '../api/auth';
import { useAuthStore } from '../store/useAuthStore';
import { HomiQLogo } from '../components/brand/HomiQLogo';
import { useGoogleLogin } from '@react-oauth/google';

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

  const loginWithGoogle = useGoogleLogin({
    onSuccess: async (tokenResponse) => {
      try {
        setLoading(true);
        setError(null);
        // Using access_token instead of credential
        const res = await authApi.googleLogin({ token: tokenResponse.access_token });
        
        login(res.access_token, res.refresh_token, res.user);

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
        console.error('Google login error:', err);
        setError(err?.response?.data?.detail || 'Google sign-in failed. Please try again.');
      } finally {
        setLoading(false);
      }
    },
    onError: (error) => {
      console.error('Google Login Failed', error);
      setError('Google Login Failed');
    }
  });

  return (
    <div className="min-h-screen bg-dark-950 flex flex-col justify-center py-12 sm:px-6 lg:px-8 text-white relative">
      <div className="sm:mx-auto sm:w-full sm:max-w-md text-center space-y-4">
        <HomiQLogo variant="stacked" size="lg" showTagline className="mx-auto" />
        <h2 className="text-xl sm:text-2xl font-bold tracking-tight text-white mt-4">
          Sign In to Your Workspace
        </h2>
        <p className="text-xs text-slate-400">
          Enter your registered credentials to access your home or fleet console.
        </p>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md px-4 sm:px-0">
        <div className="p-6 sm:p-8 rounded-3xl bg-dark-900 border border-dark-750 shadow-modal space-y-6">
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1.5">Email, Mobile Number or Username</label>
              <div className="relative">
                <UserIcon className="w-4 h-4 text-slate-500 absolute left-3.5 top-1/2 -translate-y-1/2" />
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
                <label className="block text-xs font-semibold text-slate-300">Password</label>
                <Link to="/forgot-password" className="text-[11px] text-sage-400 hover:underline">
                  Forgot Password?
                </Link>
              </div>
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

          <div className="relative flex items-center py-2">
            <div className="flex-grow border-t border-dark-750"></div>
            <span className="mx-4 text-xs font-semibold text-slate-500 uppercase">Or continue with</span>
            <div className="flex-grow border-t border-dark-750"></div>
          </div>

          <div className="flex justify-center">
            <button
              type="button"
              onClick={() => loginWithGoogle()}
              className="w-full bg-dark-800 hover:bg-dark-750 border border-dark-700 text-white rounded-xl py-3 px-4 flex items-center justify-center gap-3 transition-colors duration-200 text-xs font-semibold shadow-subtle hover:shadow-metallic"
            >
              <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4"/>
                <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/>
                <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" fill="#FBBC05"/>
                <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335"/>
              </svg>
              Sign in with Google
            </button>
          </div>

          <div className="pt-4 border-t border-dark-750 text-center text-xs text-slate-400">
            Don't have a HomiQ account yet?{' '}
            <Link to="/register" className="text-sage-300 hover:text-white font-semibold">
              Create Account
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
};
