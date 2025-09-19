import { create } from 'zustand';
import { devtools } from 'zustand/middleware';
import { authApi } from '../services/apiClient';

interface User {
  id: number;
  email: string;
  role: string;
  display_name?: string;
}

interface AuthStore {
  user: User | null;
  loading: boolean;
  error: string | null;
  
  // Actions
  setUser: (user: User | null) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  fetchMe: () => Promise<User>;
  login: (email: string, password: string) => Promise<User>;
  logout: () => Promise<void>;
  register: (email: string, password: string, displayName?: string) => Promise<User>;
}

export const useAuthStore = create<AuthStore>()(
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
          const user = await authApi.getMe();
          set({ user, loading: false });
          return user;
        } catch (error) {
          set({ user: null, loading: false, error: null });
          throw error;
        }
      },

      login: async (email: string, password: string) => {
        try {
          set({ loading: true, error: null });
          const response = await authApi.login({ email, password });
          const user = response.user;
          set({ user, loading: false });
          return user;
        } catch (error) {
          const errorMessage = error instanceof Error ? error.message : '로그인 실패';
          set({ loading: false, error: errorMessage });
          throw error;
        }
      },

      logout: async () => {
        try {
          await authApi.logout();
        } finally {
          set({ user: null, error: null });
        }
      },

      register: async (email: string, password: string, displayName?: string) => {
        try {
          set({ loading: true, error: null });
          const response = await authApi.register({ 
            email, 
            password, 
            display_name: displayName 
          });
          const user = response.user;
          set({ user, loading: false });
          return user;
        } catch (error) {
          const errorMessage = error instanceof Error ? error.message : '회원가입 실패';
          set({ loading: false, error: errorMessage });
          throw error;
        }
      },
    }),
    { name: 'auth-store' }
  )
);

export default useAuthStore;
