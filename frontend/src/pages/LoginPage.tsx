import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { ShieldCheck, Mail, Lock, ArrowRight, Eye, EyeOff } from 'lucide-react';
import { authApi } from '../api/auth';
import { useAuthStore } from '../store/useAuthStore';
import { Button } from '../components/ui/Button';
import { Input } from '../components/ui/Input';
import { Card } from '../components/ui/Card';
import { useToast } from '../components/ui/Toast';
import { extractErrorMessage } from '../api/axios';
import { UserRole } from '../types';

export const LoginPage: React.FC = () => {
  const navigate = useNavigate();
  const toast = useToast();
  const { login } = useAuthStore();

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email.trim() || !password) {
      toast.error('Required Fields', 'Please enter your email and password.');
      return;
    }

    setIsLoading(true);
    try {
      const data = await authApi.login({ email: email.trim(), password });
      login(data.access_token, data.refresh_token, data.user);
      toast.success('Welcome Back!', `Signed in as ${data.user.full_name}.`);

      // Role-based redirect
      const role = String(data.user.role).toUpperCase();
      if (role.includes('ADMIN') || data.user.is_superuser) {
        navigate('/admin/dashboard');
      } else if (role.includes('TECH')) {
        navigate('/provider/dashboard');
      } else if (role.includes('COMP')) {
        navigate('/company/dashboard');
      } else {
        navigate('/customer/dashboard');
      }
    } catch (err) {
      toast.error('Authentication Failed', extractErrorMessage(err, 'Invalid email or password.'));
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-[85vh] flex items-center justify-center px-4 py-12">
      <div className="w-full max-w-md space-y-6 text-center">
        {/* Logo Badge */}
        <div className="inline-flex items-center justify-center w-12 h-12 rounded-2xl bg-gradient-to-tr from-brand-600 to-brand-400 text-white shadow-accent mx-auto">
          <ShieldCheck className="w-7 h-7" />
        </div>

        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight">Sign in to HomiQ</h1>
          <p className="text-xs text-slate-400 mt-1.5">
            Access your customer bookings, technician portal, or management console.
          </p>
        </div>

        <Card className="p-6 text-left shadow-card">
          <form onSubmit={handleSubmit} className="space-y-4">
            <Input
              label="Email Address"
              type="email"
              placeholder="name@example.com"
              leftIcon={Mail}
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              autoFocus
            />

            <div className="space-y-1.5">
              <Input
                label="Password"
                type={showPassword ? 'text' : 'password'}
                placeholder="••••••••"
                leftIcon={Lock}
                rightIcon={showPassword ? EyeOff : Eye}
                onRightIconClick={() => setShowPassword(!showPassword)}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
              />
              <div className="flex justify-end">
                <Link
                  to="/forgot-password"
                  className="text-[11px] text-brand-400 hover:text-brand-300 transition-colors"
                >
                  Forgot password?
                </Link>
              </div>
            </div>

            <div className="pt-2">
              <Button
                variant="primary"
                size="md"
                className="w-full"
                type="submit"
                isLoading={isLoading}
                rightIcon={ArrowRight}
              >
                Sign In
              </Button>
            </div>
          </form>

          <div className="mt-6 pt-4 border-t border-dark-800 text-center text-xs text-slate-400">
            <span>Don't have an account? </span>
            <Link to="/register" className="text-brand-400 hover:text-brand-300 font-semibold">
              Create an account
            </Link>
          </div>
        </Card>
      </div>
    </div>
  );
};
