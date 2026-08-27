import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Navbar } from './components/common/Navbar';
import { Footer } from './components/common/Footer';
import { MobileBottomNav } from './components/common/MobileBottomNav';
import { FloatingNav } from './components/common/FloatingNav';
import { ToastProvider } from './components/ui/Toast';

import { LandingPage } from './pages/LandingPage';
import { ServicesPage } from './pages/ServicesPage';
import { JobsPage } from './pages/JobsPage';
import { BookingPage } from './pages/BookingPage';
import { CustomerDashboard } from './pages/CustomerDashboard';
import { ProviderDashboard } from './pages/ProviderDashboard';
import { CompanyDashboard } from './pages/CompanyDashboard';
import { AdminDashboard } from './pages/AdminDashboard';
import { LoginPage } from './pages/LoginPage';
import { RegisterPage } from './pages/RegisterPage';
import { ForgotPasswordPage } from './pages/ForgotPasswordPage';
import { ResetPasswordPage } from './pages/ResetPasswordPage';
import { NotificationsPage } from './pages/NotificationsPage';
import { LiveTrackingPage } from './pages/LiveTrackingPage';

import { useAuthStore } from './store/useAuthStore';
import { UserRole } from './types';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});

interface ProtectedRouteProps {
  children: React.ReactNode;
  allowedRoles?: UserRole[];
}

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ children, allowedRoles }) => {
  const { user, isAuthenticated, getEffectiveRole } = useAuthStore();

  if (!isAuthenticated || !user) {
    return <Navigate to="/login" replace />;
  }

  const effectiveRole = getEffectiveRole();

  if (allowedRoles && !allowedRoles.includes(effectiveRole)) {
    // If admin, allow universal oversight access
    if (effectiveRole === UserRole.ADMIN) {
      return <>{children}</>;
    }
    return <Navigate to="/" replace />;
  }

  return <>{children}</>;
};

export const App: React.FC = () => {
  return (
    <QueryClientProvider client={queryClient}>
      <ToastProvider>
        <Router>
          <div className="min-h-screen flex flex-col justify-between bg-dark-950 text-light-primary font-sans selection:bg-sage-400/20 selection:text-white pb-16 md:pb-0">
            <Navbar />
            <main className="flex-1">
              <Routes>
                {/* Public Routes */}
                <Route path="/" element={<LandingPage />} />
                <Route path="/services" element={<ServicesPage />} />
                <Route path="/categories" element={<ServicesPage />} />
                <Route path="/jobs" element={<JobsPage />} />
                <Route path="/login" element={<LoginPage />} />
                <Route path="/register" element={<RegisterPage />} />
                <Route path="/forgot-password" element={<ForgotPasswordPage />} />
                <Route path="/reset-password" element={<ResetPasswordPage />} />

                {/* Customer Routes */}
                <Route
                  path="/customer/dashboard"
                  element={
                    <ProtectedRoute allowedRoles={[UserRole.CUSTOMER]}>
                      <CustomerDashboard />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/notifications"
                  element={
                    <ProtectedRoute>
                      <NotificationsPage />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/live-tracking"
                  element={
                    <ProtectedRoute>
                      <LiveTrackingPage />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/booking/new"
                  element={
                    <ProtectedRoute>
                      <BookingPage />
                    </ProtectedRoute>
                  }
                />

                {/* Technician Workspace */}
                <Route
                  path="/provider/dashboard"
                  element={
                    <ProtectedRoute allowedRoles={[UserRole.TECHNICIAN]}>
                      <ProviderDashboard />
                    </ProtectedRoute>
                  }
                />

                {/* Company Enterprise Workspace */}
                <Route
                  path="/company/dashboard"
                  element={
                    <ProtectedRoute allowedRoles={[UserRole.COMPANY]}>
                      <CompanyDashboard />
                    </ProtectedRoute>
                  }
                />

                {/* Admin Operations Platform */}
                <Route
                  path="/admin/dashboard"
                  element={
                    <ProtectedRoute allowedRoles={[UserRole.ADMIN]}>
                      <AdminDashboard />
                    </ProtectedRoute>
                  }
                />

                {/* Fallback 404 */}
                <Route path="*" element={<Navigate to="/" replace />} />
              </Routes>
            </main>
            <Footer />
            <MobileBottomNav />
            <FloatingNav />
          </div>
        </Router>
      </ToastProvider>
    </QueryClientProvider>
  );
};

export default App;
