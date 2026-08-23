import { create } from 'zustand';
import { User, UserRole } from '../types';

interface AuthState {
  user: User | null;
  token: string | null;
  refreshToken: string | null;
  isAuthenticated: boolean;
  login: (token: string, refreshToken: string, user: User) => void;
  logout: () => void;
  updateUser: (user: Partial<User>) => void;
  getEffectiveRole: () => UserRole;
}

const getInitialUser = (): User | null => {
  try {
    const saved = localStorage.getItem('homiq_user');
    return saved ? JSON.parse(saved) : null;
  } catch {
    return null;
  }
};

const getInitialToken = (): string | null => {
  return localStorage.getItem('homiq_access_token');
};

const getInitialRefreshToken = (): string | null => {
  return localStorage.getItem('homiq_refresh_token');
};

export const useAuthStore = create<AuthState>((set, get) => ({
  user: getInitialUser(),
  token: getInitialToken(),
  refreshToken: getInitialRefreshToken(),
  isAuthenticated: !!getInitialToken(),

  login: (token: string, refreshToken: string, user: User) => {
    localStorage.setItem('homiq_access_token', token);
    if (refreshToken) {
      localStorage.setItem('homiq_refresh_token', refreshToken);
    }
    localStorage.setItem('homiq_user', JSON.stringify(user));
    set({ token, refreshToken, user, isAuthenticated: true });
  },

  logout: () => {
    localStorage.removeItem('homiq_access_token');
    localStorage.removeItem('homiq_refresh_token');
    localStorage.removeItem('homiq_user');
    set({ token: null, refreshToken: null, user: null, isAuthenticated: false });
  },

  updateUser: (updatedFields: Partial<User>) => {
    set((state) => {
      if (!state.user) return state;
      const updatedUser = { ...state.user, ...updatedFields };
      localStorage.setItem('homiq_user', JSON.stringify(updatedUser));
      return { user: updatedUser };
    });
  },

  getEffectiveRole: (): UserRole => {
    const { user } = get();
    if (!user) return UserRole.CUSTOMER;
    const r = String(user.role).toUpperCase();
    if (r.includes('ADMIN') || user.is_superuser) return UserRole.ADMIN;
    if (r.includes('TECH')) return UserRole.TECHNICIAN;
    if (r.includes('COMP')) return UserRole.COMPANY;
    return UserRole.CUSTOMER;
  },
}));
