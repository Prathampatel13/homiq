import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { ShieldCheck, Mail, Lock, Eye, EyeOff, UserCheck, Wrench, ShieldAlert } from 'lucide-react';
import { useAuthStore } from '../store/useAuthStore';
import { authApi } from '../api/auth';
import { UserRole } from '../types';
import { Button } from '../components/ui/Button';
import { Input } from '../components/ui/Input';

export const LoginPage: React.FC = () => {
  const [selectedRole, setSelectedRole] = useState<UserRole>(UserRole.CUSTOMER);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');

  const { login } = useAuthStore();
  const navigate = useNavigate();

  const handleLoginSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMessage('');
    setIsLoading(true);

    try {
      const response = await authApi.login({
        email,
        password,
        role: selectedRole,
      });

      login(response.access_token, response.user);

      // Redirect to appropriate dashboard based on user role
      if (response.user.role === UserRole.ADMIN) {
        navigate('/admin/dashboard');
      } else if (response.user.role === UserRole.TECHNICIAN) {
        navigate('/provider/dashboard');
      } else {
        navigate('/customer/dashboard');
      }
    } catch (err: any) {
      setErrorMessage(
        err.response?.data?.detail || 'Invalid email or password. Please try again.'
      );
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-[80vh] flex items-center justify-center px-4 sm:px-6 lg:px-8 py-12">
      <div className="w-full max-w-md space-y-8">
        {/* Header */}
        <div className="text-center space-y-3">
          <Link to="/" className="inline-flex items-center gap-3">
            <div className="w-12 h-12 rounded-xl bg-gradient-to-tr from-brand-600 to-indigo-500 flex items-center justify-center text-white shadow-lg shadow-brand-500/20">
              <ShieldCheck className="w-7 h-7" />
            </div>
          </Link>
          <h2 className="text-3xl font-extrabold text-white">Welcome Back</h2>
          <p className="text-sm text-slate-400">Sign in to manage your bookings and services</p>
        </div>

        {/* Role Selector Tabs */}
        <div className="grid grid-cols-3 gap-2 p-1.5 glass-card border-slate-800 rounded-xl">
          <button
            type="button"
            onClick={() => setSelectedRole(UserRole.CUSTOMER)}
            className={`flex items-center justify-center gap-1.5 py-2 px-3 rounded-lg text-xs font-semibold transition-all ${
              selectedRole === UserRole.CUSTOMER
                ? 'bg-brand-600 text-white shadow-md'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            <UserCheck className="w-3.5 h-3.5" /> Customer
          </button>
          <button
            type="button"
            onClick={() => setSelectedRole(UserRole.TECHNICIAN)}
            className={`flex items-center justify-center gap-1.5 py-2 px-3 rounded-lg text-xs font-semibold transition-all ${
              selectedRole === UserRole.TECHNICIAN
                ? 'bg-brand-600 text-white shadow-md'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            <Wrench className="w-3.5 h-3.5" /> Technician
          </button>
          <button
            type="button"
            onClick={() => setSelectedRole(UserRole.ADMIN)}
            className={`flex items-center justify-center gap-1.5 py-2 px-3 rounded-lg text-xs font-semibold transition-all ${
              selectedRole === UserRole.ADMIN
                ? 'bg-brand-600 text-white shadow-md'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            <ShieldAlert className="w-3.5 h-3.5" /> Admin
          </button>
        </div>

        {/* Login Form Card */}
        <motion.div
          initial={{ opacity: 0, y: 15 }}
          animate={{ opacity: 1, y: 0 }}
          className="glass-card p-8 border-slate-800 space-y-6"
        >
          {errorMessage && (
            <div className="p-3.5 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-400 text-xs font-medium">
              {errorMessage}
            </div>
          )}

          <form onSubmit={handleLoginSubmit} className="space-y-5">
            <Input
              label="Email Address"
              type="email"
              placeholder="name@example.com"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              leftIcon={<Mail className="w-4 h-4" />}
            />

            <div className="space-y-1">
              <Input
                label="Password"
                type={showPassword ? 'text' : 'password'}
                placeholder="••••••••"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                leftIcon={<Lock className="w-4 h-4" />}
                rightIcon={
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="focus:outline-none hover:text-white transition-colors"
                  >
                    {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                  </button>
                }
              />
              <div className="flex justify-end pt-1">
                <Link to="/forgot-password" className="text-xs text-brand-400 hover:text-brand-300">
                  Forgot password?
                </Link>
              </div>
            </div>

            <Button type="submit" variant="primary" size="md" isLoading={isLoading} className="w-full">
              Sign In
            </Button>
          </form>

          <div className="text-center text-xs text-slate-400 pt-2 border-t border-slate-800">
            Don't have an account?{' '}
            <Link to="/register" className="text-brand-400 hover:text-brand-300 font-semibold">
              Create an account
            </Link>
          </div>
        </motion.div>
      </div>
    </div>
  );
};
