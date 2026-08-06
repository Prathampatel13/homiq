import { create } from 'zustand';
import { User } from '../types';

interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  login: (token: string, user: User) => void;
  logout: () => void;
  updateUser: (user: Partial<User>) => void;
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

export const useAuthStore = create<AuthState>((set) => ({
  user: getInitialUser(),
  token: getInitialToken(),
  isAuthenticated: !!getInitialToken(),

  login: (token: string, user: User) => {
    localStorage.setItem('homiq_access_token', token);
    localStorage.setItem('homiq_user', JSON.stringify(user));
    set({ token, user, isAuthenticated: true });
  },

  logout: () => {
    localStorage.removeItem('homiq_access_token');
    localStorage.removeItem('homiq_user');
    set({ token: null, user: null, isAuthenticated: false });
  },

  updateUser: (updatedFields: Partial<User>) => {
    set((state) => {
      if (!state.user) return state;
      const updatedUser = { ...state.user, ...updatedFields };
      localStorage.setItem('homiq_user', JSON.stringify(updatedUser));
      return { user: updatedUser };
    });
  },
}));
