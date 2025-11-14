import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Toaster } from 'react-hot-toast';
import { ThemeProvider } from './shared/hooks/useTheme';
import MainLayout from './layouts/MainLayout';
import DashboardPage from './features/dashboard/DashboardPage';
import LearningPage from './features/learning/LearningPage';
import CurriculumSchedulePage from './features/learning/CurriculumSchedulePage';
import AnalyticsPage from './features/analytics/AnalyticsPage';
import AIAssistantPage from './features/ai-assistant/AIAssistantPage';
import SettingsPage from './features/settings/SettingsPage';
import QuestionsPage from './features/learning/QuestionsPage';
import CommunityPage from './features/community/CommunityPage';
import AdminDashboard from './pages/admin/AdminDashboard';
import QuestionReviewSystem from './pages/admin/QuestionReviewSystem';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import OnboardingPage from './features/onboarding/OnboardingPage';
import LandingPage from './pages/LandingPage';
import UnifiedLearningPage from './features/unified-learning/UnifiedLearningPage';
import ReviewPage from './features/review/ReviewPage';
import ReviewSessionPage from './features/review/ReviewSessionPage';
import PricingPage from './features/pricing/PricingPage';
import PaymentSuccessPage from './features/payment/PaymentSuccessPage';
import PaymentFailPage from './features/payment/PaymentFailPage';
import SubscriptionSettingsPage from './features/settings/SubscriptionSettingsPage';
import EmotionalSupportPage from './features/emotional-support/EmotionalSupportPage';

// TanStack Query 클라이언트 설정 (Strict Mode 호환)
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // 5분 - 이 시간 동안 데이터는 fresh로 간주
      cacheTime: 10 * 60 * 1000, // 10분 - 메모리에 캐시 유지
      refetchOnWindowFocus: false, // 창 포커스 시 자동 refetch 비활성화 (중복 방지)
      refetchOnMount: false, // 컴포넌트 마운트 시 자동 refetch 비활성화 (Strict Mode 대응)
      refetchOnReconnect: false, // 재연결 시 자동 refetch 비활성화
      retry: 1, // 실패 시 1번만 재시도
    },
  },
});

function App() {
  return (
    <ThemeProvider>
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>
          <Routes>
            {/* 랜딩 페이지 */}
            <Route path="/" element={<LandingPage />} />
            
            {/* 인증 페이지들 - MainLayout 없이 */}
            <Route path="/login" element={<LoginPage />} />
            <Route path="/register" element={<RegisterPage />} />
            <Route path="/onboarding" element={<OnboardingPage />} />
            
            {/* 메인 애플리케이션 - MainLayout 포함 */}
            <Route path="/dashboard" element={<MainLayout />}>
              <Route index element={<DashboardPage />} />
              <Route path="learn" element={<UnifiedLearningPage />} />
              <Route path="review" element={<ReviewPage />} />
              <Route path="review/session/:sessionId" element={<ReviewSessionPage />} />
              <Route path="pricing" element={<PricingPage />} />
              <Route path="payment/success" element={<PaymentSuccessPage />} />
              <Route path="payment/fail" element={<PaymentFailPage />} />
              <Route path="community" element={<CommunityPage />} />
              <Route path="settings/subscription" element={<SubscriptionSettingsPage />} />
              <Route path="learning" element={<CurriculumSchedulePage />} />
              <Route path="learning/old" element={<LearningPage />} />
              <Route path="learning/questions/:subjectKey" element={<QuestionsPage />} />
              <Route path="analytics/*" element={<AnalyticsPage />} />
              <Route path="ai-assistant/*" element={<AIAssistantPage />} />
              <Route path="settings/*" element={<SettingsPage />} />
              
              {/* Phase C: 감성적 지원 */}
              <Route path="emotional-support" element={<EmotionalSupportPage />} />
              
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