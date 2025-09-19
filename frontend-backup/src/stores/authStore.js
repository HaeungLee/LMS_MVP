import { create } from 'zustand';
import { devtools } from 'zustand/middleware';
import { getMe as apiGetMe, logout as apiLogout } from '../services/apiClient';

const useAuthStore = create(
  devtools(
    (set, get) => ({
      user: null,
      loading: false,
      error: null,

      setUser: (user) => set({ user }),
      setLoading: (loading) => set({ loading }),
      setError: (error) => set({ error }),

      fetchMe: async () => {
        try {
          set({ loading: true, error: null });
          const u = await apiGetMe();
          set({ user: u, loading: false });
          return u;
        } catch (e) {
          set({ user: null, loading: false, error: null });
          throw e;
        }
      },

      logout: async () => {
        try {
          await apiLogout();
        } finally {
          set({ user: null });
        }
      },
    }),
    { name: 'auth-store' }
  )
);

export default useAuthStore;


