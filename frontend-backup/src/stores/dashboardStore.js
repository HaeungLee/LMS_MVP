import { create } from 'zustand';
import { devtools } from 'zustand/middleware';

const useDashboardStore = create(
  devtools(
    (set, get) => ({
      // 대시보드 상태
      dashboardData: null,
      loading: true,
      error: null,
      
      // Actions
      setDashboardData: (data) => set({ dashboardData: data, loading: false }),
      setLoading: (loading) => set({ loading }),
      setError: (error) => set({ error, loading: false }),
      
      // 최근 활동을 quizStore에서 가져와서 병합
      getDashboardWithRecentActivities: () => {
        const state = get();
        const quizStore = require('./quizStore').default.getState();
        
        if (state.dashboardData && quizStore.recentActivities.length > 0) {
          return {
            ...state.dashboardData,
            recent_activity: quizStore.recentActivities
          };
        }
        
        return state.dashboardData;
      },
      
      resetDashboard: () => set({
        dashboardData: null,
        loading: true,
        error: null
      })
    }),
    {
      name: 'dashboard-store',
    }
  )
);

export default useDashboardStore;
