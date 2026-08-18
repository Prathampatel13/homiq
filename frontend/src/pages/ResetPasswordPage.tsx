import React, { useState } from 'react';
import { useSearchParams, useNavigate, Link } from 'react-router-dom';
import { ShieldCheck, Lock, ArrowRight, Eye, EyeOff, CheckCircle2 } from 'lucide-react';
import { authApi } from '../api/auth';
import { Button } from '../components/ui/Button';
import { Input } from '../components/ui/Input';
import { Card } from '../components/ui/Card';
import { useToast } from '../components/ui/Toast';
import { extractErrorMessage } from '../api/axios';

export const ResetPasswordPage: React.FC = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const toast = useToast();

  const token = searchParams.get('token') || '';
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [isSuccess, setIsSuccess] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!token) {
      toast.error('Invalid Reset Link', 'Password reset token is missing.');
      return;
    }
    if (newPassword.length < 8) {
      toast.error('Weak Password', 'Password must be at least 8 characters long.');
      return;
    }
    if (newPassword !== confirmPassword) {
      toast.error('Mismatch', 'Passwords do not match.');
      return;
    }

    setIsLoading(true);
    try {
      await authApi.resetPassword(token, newPassword);
      setIsSuccess(true);
      toast.success('Password Updated', 'Your account credentials have been reset.');
    } catch (err) {
      toast.error('Reset Failed', extractErrorMessage(err));
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-[85vh] flex items-center justify-center px-4 py-12">
      <div className="w-full max-w-md space-y-6 text-center">
        <div className="inline-flex items-center justify-center w-12 h-12 rounded-2xl bg-gradient-to-tr from-brand-600 to-brand-400 text-white shadow-accent mx-auto">
          <ShieldCheck className="w-7 h-7" />
        </div>

        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight">Create new password</h1>
          <p className="text-xs text-slate-400 mt-1.5">
            Your new password must be at least 8 characters long.
          </p>
        </div>

        <Card className="p-6 text-left shadow-card">
          {isSuccess ? (
            <div className="text-center py-4 space-y-3">
              <CheckCircle2 className="w-10 h-10 text-emerald-400 mx-auto" />
              <h4 className="text-sm font-bold text-white">Password Reset Complete</h4>
              <p className="text-xs text-slate-400">
                You can now log in with your updated credentials.
              </p>
              <div className="pt-2">
                <Button variant="primary" size="md" className="w-full" onClick={() => navigate('/login')}>
                  Sign In Now
                </Button>
              </div>
            </div>
          ) : (
            <form onSubmit={handleSubmit} className="space-y-4">
              <Input
                label="New Password *"
                type={showPassword ? 'text' : 'password'}
                placeholder="••••••••"
                leftIcon={Lock}
                rightIcon={showPassword ? EyeOff : Eye}
                onRightIconClick={() => setShowPassword(!showPassword)}
                value={newPassword}
                onChange={(e) => setNewPassword(e.target.value)}
                required
              />

              <Input
                label="Confirm New Password *"
                type={showPassword ? 'text' : 'password'}
                placeholder="••••••••"
                leftIcon={Lock}
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                required
              />

              <Button
                variant="primary"
                size="md"
                className="w-full"
                type="submit"
                isLoading={isLoading}
                rightIcon={ArrowRight}
              >
                Reset Password
              </Button>
            </form>
          )}
        </Card>
      </div>
    </div>
  );
};
