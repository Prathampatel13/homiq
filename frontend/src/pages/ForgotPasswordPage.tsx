import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Mail, AlertCircle, Loader2, CheckCircle2, ArrowLeft, KeyRound } from 'lucide-react';
import { authApi } from '../api/auth';
import { HomiQLogo } from '../components/brand/HomiQLogo';

export const ForgotPasswordPage: React.FC = () => {
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const [loadingOtp, setLoadingOtp] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);
  const [method, setMethod] = useState<'link' | 'otp' | null>(null);

  const handleSendLink = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email.trim()) return;

    try {
      setLoading(true);
      setError(null);
      await authApi.forgotPassword(email);
      setMethod('link');
      setSuccess(true);
    } catch (err: any) {
      console.error('Forgot password error:', err);
      setError(err?.response?.data?.detail || 'Failed to send recovery email. Please check your address.');
    } finally {
      setLoading(false);
    }
  };

  const handleSendOtp = async () => {
    if (!email.trim()) {
      setError('Please enter your email first.');
      return;
    }

    try {
      setLoadingOtp(true);
      setError(null);
      await authApi.sendResetOtp(email);
      navigate('/reset-password', { state: { email, method: 'otp' } });
    } catch (err: any) {
      console.error('Send OTP error:', err);
      setError(err?.response?.data?.detail || 'Failed to send OTP. Please check your address.');
    } finally {
      setLoadingOtp(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#F8FAFC] flex flex-col justify-center py-12 sm:px-6 lg:px-8 text-slate-900 relative">
      <div className="sm:mx-auto sm:w-full sm:max-w-md text-center space-y-4">
        <HomiQLogo variant="stacked" size="lg" showTagline className="mx-auto" />
        <h2 className="text-xl sm:text-2xl font-bold tracking-tight text-slate-900 mt-4">
          Reset Your Access Password
        </h2>
        <p className="text-xs text-slate-600">
          Enter your registered email to receive secure recovery instructions.
        </p>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md px-4 sm:px-0">
        <div className="p-6 sm:p-8 rounded-3xl bg-white border border-slate-200 shadow-card space-y-6">
          {success && method === 'link' ? (
            <div className="text-center py-4 space-y-3">
              <div className="w-12 h-12 rounded-full bg-emerald-50 border border-emerald-200 flex items-center justify-center text-emerald-600 mx-auto">
                <CheckCircle2 className="w-6 h-6" />
              </div>
              <h3 className="text-base font-bold text-slate-900">Instructions Dispatched</h3>
              <p className="text-xs text-slate-600 leading-relaxed">
                If an account exists with <span className="text-slate-900 font-mono font-semibold">{email}</span>, password reset instructions have been transmitted.
              </p>
              <Link to="/login" className="btn-secondary text-xs px-4 py-2 inline-flex items-center gap-1.5 mt-2">
                <ArrowLeft className="w-3.5 h-3.5" />
                <span>Return to Sign In</span>
              </Link>
            </div>
          ) : (
            <form onSubmit={handleSendLink} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1.5">Registered Email</label>
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

              {error && (
                <div className="p-3 rounded-xl bg-rose-50 border border-rose-200 text-rose-700 text-xs flex items-center gap-2">
                  <AlertCircle className="w-4 h-4 shrink-0" />
                  <span>{error}</span>
                </div>
              )}

              <div className="flex flex-col gap-3 pt-2">
                <button
                  type="submit"
                  disabled={loading || loadingOtp}
                  className="w-full btn-primary text-xs py-3 font-semibold flex items-center justify-center gap-1.5 shadow-subtle hover:shadow-metallic disabled:opacity-40"
                >
                  {loading && <Loader2 className="w-3.5 h-3.5 animate-spin" />}
                  <span>Send Reset Link</span>
                </button>
                
                <div className="relative flex items-center py-1">
                  <div className="flex-grow border-t border-slate-200"></div>
                  <span className="mx-4 text-xs font-semibold text-slate-400 uppercase">Or</span>
                  <div className="flex-grow border-t border-slate-200"></div>
                </div>

                <button
                  type="button"
                  onClick={handleSendOtp}
                  disabled={loading || loadingOtp}
                  className="w-full btn-secondary text-xs py-3 font-semibold flex items-center justify-center gap-1.5 disabled:opacity-40"
                >
                  {loadingOtp ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <KeyRound className="w-3.5 h-3.5" />}
                  <span>Send 6-Digit OTP</span>
                </button>
              </div>

              <div className="pt-4 text-center">
                <Link to="/login" className="text-xs text-slate-600 hover:text-slate-900 inline-flex items-center gap-1 font-medium">
                  <ArrowLeft className="w-3 h-3" />
                  <span>Back to Sign In</span>
                </Link>
              </div>
            </form>
          )}
        </div>
      </div>
    </div>
  );
};

