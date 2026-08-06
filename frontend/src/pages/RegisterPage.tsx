import React, { useState } from 'react';
import { Link, useNavigate, useSearchParams } from 'react-router-dom';
import { motion } from 'framer-motion';
import { ShieldCheck, User, Mail, Phone, Lock, UserCheck, Wrench } from 'lucide-react';
import { authApi } from '../api/auth';
import { useAuthStore } from '../store/useAuthStore';
import { UserRole } from '../types';
import { Button } from '../components/ui/Button';
import { Input } from '../components/ui/Input';

export const RegisterPage: React.FC = () => {
  const [searchParams] = useSearchParams();
  const initialRole = searchParams.get('role') === 'technician' ? UserRole.TECHNICIAN : UserRole.CUSTOMER;

  const [role, setRole] = useState<UserRole>(initialRole);
  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [phone, setPhone] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');

  const { login } = useAuthStore();
  const navigate = useNavigate();

  const handleRegisterSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMessage('');
    setIsLoading(true);

    try {
      const response = await authApi.register({
        full_name: fullName,
        email,
        phone,
        password,
        role,
      });

      login(response.access_token, response.user);

      if (response.user.role === UserRole.TECHNICIAN) {
        navigate('/provider/dashboard');
      } else {
        navigate('/customer/dashboard');
      }
    } catch (err: any) {
      setErrorMessage(
        err.response?.data?.detail || 'Registration failed. Please check your details and try again.'
      );
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-[85vh] flex items-center justify-center px-4 sm:px-6 lg:px-8 py-12">
      <div className="w-full max-w-md space-y-8">
        {/* Header */}
        <div className="text-center space-y-3">
          <Link to="/" className="inline-flex items-center gap-3">
            <div className="w-12 h-12 rounded-xl bg-gradient-to-tr from-brand-600 to-indigo-500 flex items-center justify-center text-white shadow-lg shadow-brand-500/20">
              <ShieldCheck className="w-7 h-7" />
            </div>
          </Link>
          <h2 className="text-3xl font-extrabold text-white">Create Account</h2>
          <p className="text-sm text-slate-400">Join HomiQ for verified home maintenance services</p>
        </div>

        {/* Role Selector Tabs */}
        <div className="grid grid-cols-2 gap-2 p-1.5 glass-card border-slate-800 rounded-xl">
          <button
            type="button"
            onClick={() => setRole(UserRole.CUSTOMER)}
            className={`flex items-center justify-center gap-2 py-2.5 px-4 rounded-lg text-xs font-semibold transition-all ${
              role === UserRole.CUSTOMER
                ? 'bg-brand-600 text-white shadow-md'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            <UserCheck className="w-4 h-4" /> Book Services (Customer)
          </button>
          <button
            type="button"
            onClick={() => setRole(UserRole.TECHNICIAN)}
            className={`flex items-center justify-center gap-2 py-2.5 px-4 rounded-lg text-xs font-semibold transition-all ${
              role === UserRole.TECHNICIAN
                ? 'bg-brand-600 text-white shadow-md'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            <Wrench className="w-4 h-4" /> Provide Services (Partner)
          </button>
        </div>

        {/* Form Card */}
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

          <form onSubmit={handleRegisterSubmit} className="space-y-4">
            <Input
              label="Full Name"
              type="text"
              placeholder="John Doe"
              required
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              leftIcon={<User className="w-4 h-4" />}
            />

            <Input
              label="Email Address"
              type="email"
              placeholder="name@example.com"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              leftIcon={<Mail className="w-4 h-4" />}
            />

            <Input
              label="Phone Number"
              type="tel"
              placeholder="+91 98765 43210"
              required
              value={phone}
              onChange={(e) => setPhone(e.target.value)}
              leftIcon={<Phone className="w-4 h-4" />}
            />

            <Input
              label="Password"
              type="password"
              placeholder="••••••••"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              leftIcon={<Lock className="w-4 h-4" />}
            />

            <Button type="submit" variant="primary" size="md" isLoading={isLoading} className="w-full mt-2">
              Create Account
            </Button>
          </form>

          <div className="text-center text-xs text-slate-400 pt-2 border-t border-slate-800">
            Already have an account?{' '}
            <Link to="/login" className="text-brand-400 hover:text-brand-300 font-semibold">
              Sign In
            </Link>
          </div>
        </motion.div>
      </div>
    </div>
  );
};
