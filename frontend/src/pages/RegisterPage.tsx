import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { ShieldCheck, Mail, Lock, User, Phone, ArrowRight, Eye, EyeOff, Briefcase, Building2 } from 'lucide-react';
import { authApi } from '../api/auth';
import { useAuthStore } from '../store/useAuthStore';
import { Button } from '../components/ui/Button';
import { Input } from '../components/ui/Input';
import { Card } from '../components/ui/Card';
import { useToast } from '../components/ui/Toast';
import { extractErrorMessage } from '../api/axios';

export const RegisterPage: React.FC = () => {
  const navigate = useNavigate();
  const toast = useToast();
  const { login } = useAuthStore();

  const [role, setRole] = useState<'customer' | 'technician' | 'company'>('customer');
  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [phone, setPhone] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!fullName.trim() || !email.trim() || !password) {
      toast.error('Required Fields', 'Please complete the registration fields.');
      return;
    }
    if (password.length < 8) {
      toast.error('Weak Password', 'Password must be at least 8 characters long.');
      return;
    }

    setIsLoading(true);
    try {
      const data = await authApi.register({
        full_name: fullName.trim(),
        email: email.trim(),
        phone: phone.trim() || undefined,
        password,
        role,
      });

      login(data.access_token, data.refresh_token, data.user);
      toast.success('Account Created!', `Welcome to HomiQ, ${data.user.full_name}.`);

      if (role === 'technician') {
        navigate('/provider/dashboard');
      } else if (role === 'company') {
        navigate('/company/dashboard');
      } else {
        navigate('/customer/dashboard');
      }
    } catch (err) {
      toast.error('Registration Failed', extractErrorMessage(err));
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
          <h1 className="text-2xl font-bold text-white tracking-tight">Create your HomiQ account</h1>
          <p className="text-xs text-slate-400 mt-1.5">
            Join thousands of homeowners, verified specialists, and enterprise teams.
          </p>
        </div>

        <Card className="p-6 text-left shadow-card space-y-4">
          {/* Account Role Selector */}
          <div className="space-y-1.5">
            <label className="text-xs font-medium text-slate-300">Account Type</label>
            <div className="grid grid-cols-3 gap-2">
              {[
                { id: 'customer', label: 'Homeowner', icon: User },
                { id: 'technician', label: 'Technician', icon: Briefcase },
                { id: 'company', label: 'Enterprise', icon: Building2 },
              ].map((r) => (
                <button
                  key={r.id}
                  type="button"
                  onClick={() => setRole(r.id as any)}
                  className={`p-2.5 rounded-xl border text-xs font-medium flex flex-col items-center gap-1.5 transition-all ${
                    role === r.id
                      ? 'bg-dark-800 border-brand-500 text-white shadow-subtle'
                      : 'bg-dark-850/50 border-dark-750 text-slate-400 hover:text-slate-200'
                  }`}
                >
                  <r.icon className={`w-4 h-4 ${role === r.id ? 'text-brand-400' : 'text-slate-500'}`} />
                  <span>{r.label}</span>
                </button>
              ))}
            </div>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            <Input
              label="Full Name *"
              placeholder="e.g. Rahul Sharma"
              leftIcon={User}
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              required
            />

            <Input
              label="Email Address *"
              type="email"
              placeholder="name@example.com"
              leftIcon={Mail}
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />

            <Input
              label="Phone Number"
              placeholder="+91 98765 43210"
              leftIcon={Phone}
              value={phone}
              onChange={(e) => setPhone(e.target.value)}
            />

            <Input
              label="Password (min 8 characters) *"
              type={showPassword ? 'text' : 'password'}
              placeholder="••••••••"
              leftIcon={Lock}
              rightIcon={showPassword ? EyeOff : Eye}
              onRightIconClick={() => setShowPassword(!showPassword)}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />

            <div className="pt-2">
              <Button
                variant="primary"
                size="md"
                className="w-full"
                type="submit"
                isLoading={isLoading}
                rightIcon={ArrowRight}
              >
                Create Account
              </Button>
            </div>
          </form>

          <div className="mt-6 pt-4 border-t border-dark-800 text-center text-xs text-slate-400">
            <span>Already have an account? </span>
            <Link to="/login" className="text-brand-400 hover:text-brand-300 font-semibold">
              Sign in
            </Link>
          </div>
        </Card>
      </div>
    </div>
  );
};
