import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { ShieldCheck, Mail, ArrowRight, ArrowLeft, CheckCircle2 } from 'lucide-react';
import { authApi } from '../api/auth';
import { Button } from '../components/ui/Button';
import { Input } from '../components/ui/Input';
import { Card } from '../components/ui/Card';
import { useToast } from '../components/ui/Toast';
import { extractErrorMessage } from '../api/axios';

export const ForgotPasswordPage: React.FC = () => {
  const toast = useToast();
  const [email, setEmail] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isSubmitted, setIsSubmitted] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email.trim()) {
      toast.error('Required', 'Please enter your registered email address.');
      return;
    }

    setIsLoading(true);
    try {
      await authApi.forgotPassword(email.trim());
      setIsSubmitted(true);
      toast.success('Instructions Sent', 'Check your email inbox for password recovery steps.');
    } catch (err) {
      toast.error('Request failed', extractErrorMessage(err));
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
          <h1 className="text-2xl font-bold text-white tracking-tight">Reset your password</h1>
          <p className="text-xs text-slate-400 mt-1.5">
            Enter your email and we'll send you recovery instructions.
          </p>
        </div>

        <Card className="p-6 text-left shadow-card">
          {isSubmitted ? (
            <div className="text-center py-4 space-y-3">
              <CheckCircle2 className="w-10 h-10 text-emerald-400 mx-auto" />
              <h4 className="text-sm font-bold text-white">Check Your Inbox</h4>
              <p className="text-xs text-slate-400">
                We've sent recovery instructions to <span className="text-white font-medium">{email}</span>.
              </p>
              <div className="pt-2">
                <Link to="/login" className="btn-primary text-xs px-4 py-2">
                  Return to Sign In
                </Link>
              </div>
            </div>
          ) : (
            <form onSubmit={handleSubmit} className="space-y-4">
              <Input
                label="Registered Email Address"
                type="email"
                placeholder="name@example.com"
                leftIcon={Mail}
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                autoFocus
              />

              <Button
                variant="primary"
                size="md"
                className="w-full"
                type="submit"
                isLoading={isLoading}
                rightIcon={ArrowRight}
              >
                Send Instructions
              </Button>
            </form>
          )}

          <div className="mt-6 pt-4 border-t border-dark-800 text-center">
            <Link to="/login" className="inline-flex items-center gap-1.5 text-xs text-slate-400 hover:text-white transition-colors">
              <ArrowLeft className="w-3.5 h-3.5" />
              <span>Back to Sign In</span>
            </Link>
          </div>
        </Card>
      </div>
    </div>
  );
};
