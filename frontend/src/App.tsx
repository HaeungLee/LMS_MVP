import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Toaster } from 'react-hot-toast';
import { ThemeProvider } from './shared/hooks/useTheme';
import MainLayout from './layouts/MainLayout';
import DashboardPage from './features/dashboard/DashboardPage';
import LearningPage from './features/learning/LearningPage';
import AnalyticsPage from './features/analytics/AnalyticsPage';
import AIAssistantPage from './features/ai-assistant/AIAssistantPage';
import SettingsPage from './features/settings/SettingsPage';
import QuestionsPage from './features/learning/QuestionsPage';
import AdminDashboard from './pages/admin/AdminDashboard';
import QuestionReviewSystem from './pages/admin/QuestionReviewSystem';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import OnboardingPage from './features/onboarding/OnboardingPage';

// TanStack Query 클라이언트 설정
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // 5분
      retry: 1,
    },
  },
});

function App() {
  return (
    <ThemeProvider>
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>
          <Routes>
            {/* 인증 페이지들 - MainLayout 없이 */}
            <Route path="/login" element={<LoginPage />} />
            <Route path="/register" element={<RegisterPage />} />
            <Route path="/onboarding" element={<OnboardingPage />} />
            
            {/* 메인 애플리케이션 - MainLayout 포함 */}
            <Route path="/" element={<MainLayout />}>
              <Route index element={<DashboardPage />} />
              <Route path="learning" element={<LearningPage />} />
              <Route path="learning/questions/:subjectKey" element={<QuestionsPage />} />
              <Route path="analytics/*" element={<AnalyticsPage />} />
              <Route path="ai-assistant/*" element={<AIAssistantPage />} />
              <Route path="settings/*" element={<SettingsPage />} />
              
              {/* 관리자 전용 라우트 */}
              <Route path="admin" element={<AdminDashboard />} />
              <Route path="admin/questions" element={<QuestionReviewSystem />} />
            </Route>
          </Routes>
        </BrowserRouter>
        
        {/* Toast 알림 컴포넌트 */}
        <Toaster
          position="top-right"
          reverseOrder={false}
          gutter={8}
          containerClassName=""
          containerStyle={{}}
          toastOptions={{
            // 기본 설정
            className: '',
            duration: 4000,
            style: {
              background: '#363636',
              color: '#fff',
            },
            // 성공 토스트
            success: {
              duration: 3000,
              style: {
                background: '#10b981',
              },
            },
            // 에러 토스트
            error: {
              duration: 4000,
              style: {
                background: '#ef4444',
              },
            },
          }}
        />
      </QueryClientProvider>
    </ThemeProvider>
  );
}

export default App;