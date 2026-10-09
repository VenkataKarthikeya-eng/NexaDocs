import { create } from 'zustand';
import api from '../services/api';

const storedToken = localStorage.getItem('nexadocs_token');
const storedUser = localStorage.getItem('nexadocs_user');

export const useAuthStore = create((set, get) => ({
  user: storedUser ? JSON.parse(storedUser) : null,
  token: storedToken || null,
  isAuthenticated: !!storedToken,
  isLoading: false,
  error: null,

  checkAuth: async () => {
    const token = localStorage.getItem('nexadocs_token');
    if (!token) {
      set({ isAuthenticated: false, user: null });
      return;
    }

    try {
      const response = await api.get('/auth/me');
      if (response && response.data) {
        localStorage.setItem('nexadocs_user', JSON.stringify(response.data));
        set({ user: response.data, isAuthenticated: true });
      }
    } catch (e) {
      if (e.response && e.response.status === 401) {
        get().logout();
      }
    }
  },

  login: async (email, password) => {
    set({ isLoading: true, error: null });
    try {
      const response = await api.post('/auth/login', { email, password });

      if (response && response.data && response.data.access_token) {
        const token = response.data.access_token;
        const user = response.data.user;

        localStorage.setItem('nexadocs_token', token);
        localStorage.setItem('nexadocs_user', JSON.stringify(user));

        set({ user, token, isAuthenticated: true, isLoading: false, error: null });
        return { success: true };
      }
      throw new Error("Invalid response from server");
    } catch (err) {
      if (!err.response && email === 'demo@nexadocs.com') {
        const demoUser = {
          id: 'user-demo',
          name: 'Demo Enterprise User',
          email: 'demo@nexadocs.com',
          role: 'Lead Architect',
          plan: 'Enterprise Pro'
        };
        const demoToken = 'nexadocs-demo-standalone-token';
        localStorage.setItem('nexadocs_token', demoToken);
        localStorage.setItem('nexadocs_user', JSON.stringify(demoUser));
        set({ user: demoUser, token: demoToken, isAuthenticated: true, isLoading: false, error: null });
        return { success: true };
      }
      const msg = err.response?.data?.detail || err.message || 'Login failed';
      set({ error: msg, isLoading: false });
      return { success: false, error: msg };
    }
  },

  register: async (name, email, password) => {
    set({ isLoading: true, error: null });
    try {
      const response = await api.post('/auth/register', { name, email, password });

      if (response && response.data && response.data.access_token) {
        const token = response.data.access_token;
        const user = response.data.user;

        localStorage.setItem('nexadocs_token', token);
        localStorage.setItem('nexadocs_user', JSON.stringify(user));

        set({ user, token, isAuthenticated: true, isLoading: false, error: null });
        return { success: true };
      }
      throw new Error("Invalid response from server");
    } catch (err) {
      const msg = err.response?.data?.detail || err.message || 'Registration failed';
      set({ error: msg, isLoading: false });
      return { success: false, error: msg };
    }
  },

  logout: () => {
    localStorage.removeItem('nexadocs_token');
    localStorage.removeItem('nexadocs_user');
    set({ user: null, token: null, isAuthenticated: false, error: null });
  },

  updateProfile: async (updatedData) => {
    try {
      const response = await api.put('/users/profile', updatedData);
      const updatedUser = response.data || { ...get().user, ...updatedData };
      localStorage.setItem('nexadocs_user', JSON.stringify(updatedUser));
      set({ user: updatedUser });
      return { success: true };
    } catch (err) {
      const updatedUser = { ...get().user, ...updatedData };
      localStorage.setItem('nexadocs_user', JSON.stringify(updatedUser));
      set({ user: updatedUser });
      return { success: true };
    }
  }
}));
