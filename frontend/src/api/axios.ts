import axios, { AxiosError, InternalAxiosRequestConfig } from 'axios';

export const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ||
  import.meta.env.VITE_API_URL ||
  import.meta.env.VITE_BACKEND_URL ||
  (import.meta.env.PROD ? 'https://homiq-backend.onrender.com' : 'http://localhost:8000');

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 15000,
});

let isRefreshing = false;
let failedQueue: Array<{
  resolve: (value?: unknown) => void;
  reject: (reason?: unknown) => void;
}> = [];

const processQueue = (error: unknown, token: string | null = null) => {
  failedQueue.forEach((prom) => {
    if (error) {
      prom.reject(error);
    } else {
      prom.resolve(token);
    }
  });
  failedQueue = [];
};

// Request Interceptor: Attach JWT Token
api.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = localStorage.getItem('homiq_access_token');
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response Interceptor: Seamless Refresh & Auth Expiration Handler
api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean };

    if (error.response?.status === 401 && originalRequest && !originalRequest._retry) {
      const refreshToken = localStorage.getItem('homiq_refresh_token');

      // If already on auth routes or no refresh token, clear and reject
      if (!refreshToken || originalRequest.url?.includes('/auth/login') || originalRequest.url?.includes('/auth/refresh')) {
        localStorage.removeItem('homiq_access_token');
        localStorage.removeItem('homiq_refresh_token');
        localStorage.removeItem('homiq_user');
        return Promise.reject(error);
      }

      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject });
        })
          .then((token) => {
            if (originalRequest.headers) {
              originalRequest.headers.Authorization = `Bearer ${token}`;
            }
            return api(originalRequest);
          })
          .catch((err) => Promise.reject(err));
      }

      originalRequest._retry = true;
      isRefreshing = true;

      try {
        const response = await axios.post(`${API_BASE_URL}/auth/refresh?refresh_token=${encodeURIComponent(refreshToken)}`);
        const { access_token, refresh_token: newRefreshToken } = response.data;

        localStorage.setItem('homiq_access_token', access_token);
        if (newRefreshToken) {
          localStorage.setItem('homiq_refresh_token', newRefreshToken);
        }

        if (originalRequest.headers) {
          originalRequest.headers.Authorization = `Bearer ${access_token}`;
        }
        processQueue(null, access_token);
        return api(originalRequest);
      } catch (refreshErr) {
        processQueue(refreshErr, null);
        localStorage.removeItem('homiq_access_token');
        localStorage.removeItem('homiq_refresh_token');
        localStorage.removeItem('homiq_user');
        if (window.location.pathname !== '/login' && !window.location.pathname.startsWith('/auth')) {
          window.location.href = '/login';
        }
        return Promise.reject(refreshErr);
      } finally {
        isRefreshing = false;
      }
    }

    return Promise.reject(error);
  }
);

/**
 * Universal error message extractor for backend FastAPI/Pydantic/HTTPException errors
 */
export const extractErrorMessage = (error: unknown, fallback: string = 'An unexpected error occurred'): string => {
  if (!error) return fallback;
  if (typeof error === 'string') return error;

  const axiosErr = error as AxiosError<{ detail?: any; message?: string }>;
  if (axiosErr.response?.data) {
    const data = axiosErr.response.data;
    if (typeof data.detail === 'string') {
      return data.detail;
    }
    if (Array.isArray(data.detail)) {
      // Pydantic validation array
      const first = data.detail[0];
      if (first && first.msg) {
        const field = first.loc ? first.loc[first.loc.length - 1] : '';
        return field ? `${field}: ${first.msg}` : first.msg;
      }
    }
    if (data.message) {
      return data.message;
    }
  }

  if (axiosErr.message) {
    return axiosErr.message;
  }

  return fallback;
};

export default api;
