import React, { useState, useEffect } from 'react';
import { Link, useNavigate, useSearchParams, useLocation } from 'react-router-dom';
import { Lock, AlertCircle, Loader2, CheckCircle2, Eye, EyeOff, KeyRound } from 'lucide-react';
import { authApi } from '../api/auth';
import { HomiQLogo } from '../components/brand/HomiQLogo';

export const ResetPasswordPage: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const [searchParams] = useSearchParams();
  
  // URL token for email link method
  const urlToken = searchParams.get('token');
  
  // State from OTP method
  const stateEmail = location.state?.email;
  const method = location.state?.method || (urlToken ? 'link' : null);

  const [otp, setOtp] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);
  
  // The token used to actually reset the password (either from URL or from OTP verify)
  const [resetToken, setResetToken] = useState<string>(urlToken || '');
  const [otpVerified, setOtpVerified] = useState(false);

  useEffect(() => {
    if (!method) {
      // If no token and no state, redirect to forgot password
      navigate('/forgot-password');
    }
  }, [method, navigate]);

  const handleVerifyOtp = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!otp || otp.length !== 6 || !stateEmail) {
      setError('Please enter a valid 6-digit OTP.');
      return;
    }

    try {
      setLoading(true);
      setError(null);
      const res = await authApi.verifyResetOtp(stateEmail, otp);
      setResetToken(res.reset_token);
      setOtpVerified(true);
    } catch (err: any) {
      console.error('OTP verification failed:', err);
      setError(err?.response?.data?.detail || 'Invalid or expired OTP.');
    } finally {
      setLoading(false);
    }
  };

  const handleResetPassword = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!password || password !== confirmPassword) {
      setError('Passwords do not match.');
      return;
    }
    if (!resetToken) {
      setError('Missing reset token.');
      return;
    }

    try {
      setLoading(true);
      setError(null);
      await authApi.resetPassword(resetToken, password);
      setSuccess(true);
      setTimeout(() => navigate('/login'), 2000);
    } catch (err: any) {
      console.error('Password reset failed:', err);
      setError(err?.response?.data?.detail || 'Password reset failed or link expired.');
    } finally {
      setLoading(false);
    }
  };

  const renderOtpForm = () => (
    <form onSubmit={handleVerifyOtp} className="space-y-4">
      <div>
        <label className="block text-xs font-semibold text-slate-300 mb-1.5">Enter 6-Digit OTP</label>
        <div className="relative">
          <KeyRound className="w-4 h-4 text-slate-500 absolute left-3.5 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            maxLength={6}
            value={otp}
            onChange={(e) => setOtp(e.target.value.replace(/[^0-9]/g, ''))}
            placeholder="123456"
            className="input-field pl-10 tracking-widest text-center text-lg"
            required
          />
        </div>
        <p className="text-xs text-slate-400 mt-2 text-center">
          Sent to: <span className="text-white font-mono">{stateEmail}</span>
        </p>
      </div>

      {error && (
        <div className="p-3 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-400 text-xs flex items-center gap-2">
          <AlertCircle className="w-4 h-4 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      <button
        type="submit"
        disabled={loading || otp.length !== 6}
        className="w-full btn-primary text-xs py-3 font-semibold flex items-center justify-center gap-1.5 shadow-subtle hover:shadow-metallic disabled:opacity-40"
      >
        {loading && <Loader2 className="w-3.5 h-3.5 animate-spin" />}
        <span>Verify OTP</span>
      </button>
    </form>
  );

  const renderPasswordForm = () => (
    <form onSubmit={handleResetPassword} className="space-y-4">
      <div>
        <label className="block text-xs font-semibold text-slate-300 mb-1.5">New Password</label>
        <div className="relative">
          <Lock className="w-4 h-4 text-slate-500 absolute left-3.5 top-1/2 -translate-y-1/2" />
          <input
            type={showPassword ? "text" : "password"}
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="••••••••"
            className="input-field pl-10 pr-10"
            required
            minLength={8}
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

      <div>
        <label className="block text-xs font-semibold text-slate-300 mb-1.5">Confirm New Password</label>
        <div className="relative">
          <Lock className="w-4 h-4 text-slate-500 absolute left-3.5 top-1/2 -translate-y-1/2" />
          <input
            type={showConfirmPassword ? "text" : "password"}
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            placeholder="••••••••"
            className="input-field pl-10 pr-10"
            required
            minLength={8}
          />
          <button
            type="button"
            onClick={() => setShowConfirmPassword(!showConfirmPassword)}
            className="absolute right-3.5 top-1/2 -translate-y-1/2 text-slate-500 hover:text-slate-300 transition-colors"
          >
            {showConfirmPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
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
        {loading && <Loader2 className="w-3.5 h-3.5 animate-spin" />}
        <span>Set New Password</span>
      </button>
    </form>
  );

  return (
    <div className="min-h-screen bg-dark-950 flex flex-col justify-center py-12 sm:px-6 lg:px-8 text-white relative">
      <div className="sm:mx-auto sm:w-full sm:max-w-md text-center space-y-4">
        <HomiQLogo variant="stacked" size="lg" showTagline className="mx-auto" />
        <h2 className="text-xl sm:text-2xl font-bold tracking-tight text-white mt-4">
          {method === 'otp' && !otpVerified ? 'Verify Identity' : 'Create New Password'}
        </h2>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md px-4 sm:px-0">
        <div className="p-6 sm:p-8 rounded-3xl bg-dark-900 border border-dark-750 shadow-modal space-y-6">
          {success ? (
            <div className="text-center py-4 space-y-3">
              <div className="w-12 h-12 rounded-full bg-emerald-500/15 border border-emerald-500/30 flex items-center justify-center text-emerald-400 mx-auto">
                <CheckCircle2 className="w-6 h-6" />
              </div>
              <h3 className="text-base font-bold text-white">Password Updated</h3>
              <p className="text-xs text-slate-400">Redirecting to sign in...</p>
            </div>
          ) : (
            method === 'otp' && !otpVerified ? renderOtpForm() : renderPasswordForm()
          )}
        </div>
      </div>
    </div>
  );
};
