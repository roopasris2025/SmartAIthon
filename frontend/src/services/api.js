import axios from 'axios';

// Base API instance
const API = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:5000/api',
  headers: { 'Content-Type': 'application/json' },
});

// Request interceptor — attach JWT token
API.interceptors.request.use((config) => {
  const token = localStorage.getItem('swms_token');
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

// Response interceptor — handle errors globally
API.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401) {
      localStorage.removeItem('swms_token');
      localStorage.removeItem('swms_user');
      window.location.href = '/auth';
    }
    return Promise.reject(err);
  }
);

// ─── Auth ────────────────────────────────────────────────
export const loginUser = (data) => API.post('/auth/login', data);
export const registerUser = (data) => API.post('/auth/register', data);

// ─── Reports ─────────────────────────────────────────────
export const fetchReports = () => API.get('/reports');
export const createReport = (data) => API.post('/reports', data);
export const updateReport = (id, data) => API.patch(`/reports/${id}`, data);

// ─── Users ───────────────────────────────────────────────
export const fetchLeaderboard = () => API.get('/users/leaderboard');

export default API;
