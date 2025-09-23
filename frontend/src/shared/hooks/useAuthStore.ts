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
        const state = get();
        
        // 이미 로딩 중이거나 사용자가 있으면 중복 요청 방지
        if (state.loading || state.user) {
          console.log('🔄 fetchMe 중복 요청 방지 - loading:', state.loading, 'user:', !!state.user);
          return state.user!;
        }
        
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
        const state = get();
        
        // 이미 로딩 중이면 중복 요청 방지
        if (state.loading) {
          console.log('🔄 로그인 중복 요청 방지');
          throw new Error('이미 로그인 중입니다.');
        }
        
        try {
          console.log('🔑 로그인 시작:', email);
          set({ loading: true, error: null });
          const user = await authApi.login({ email, password });
          console.log('✅ 로그인 성공:', user.email);
          set({ user, loading: false });
          return user;
        } catch (error) {
          console.error('❌ 로그인 실패:', error);
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
          const user = await authApi.register({ 
            email, 
            password, 
            display_name: displayName 
          });
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
