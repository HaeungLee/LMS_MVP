import { lazy, Suspense } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Toaster } from 'react-hot-toast';
import { ThemeProvider } from './shared/hooks/useTheme';

// ============================================
// 코드 스플리팅: React.lazy를 사용한 동적 임포트
// 각 페이지는 사용자가 접근할 때만 로드됨
// ============================================

// 레이아웃 (자주 사용되므로 동기 로드)
import MainLayout from './layouts/MainLayout';

// 랜딩 & 인증 페이지 (초기 로드에 필요)
const LandingPage = lazy(() => import('./pages/LandingPage'));
const LoginPage = lazy(() => import('./pages/LoginPage'));
const RegisterPage = lazy(() => import('./pages/RegisterPage'));
const OnboardingPage = lazy(() => import('./features/onboarding/OnboardingPage'));

// 메인 기능 페이지들 (사용 시 로드)
const DashboardPage = lazy(() => import('./features/dashboard/DashboardPage'));
const UnifiedLearningPage = lazy(() => import('./features/unified-learning/UnifiedLearningPage'));
const ReviewPage = lazy(() => import('./features/review/ReviewPage'));
const ReviewSessionPage = lazy(() => import('./features/review/ReviewSessionPage'));
const CurriculumSchedulePage = lazy(() => import('./features/learning/CurriculumSchedulePage'));
const LearningPage = lazy(() => import('./features/learning/LearningPage'));
const QuestionsPage = lazy(() => import('./features/learning/QuestionsPage'));
const AnalyticsPage = lazy(() => import('./features/analytics/AnalyticsPage'));
const AIAssistantPage = lazy(() => import('./features/ai-assistant/AIAssistantPage'));
const CommunityPage = lazy(() => import('./features/community/CommunityPage'));
const SettingsPage = lazy(() => import('./features/settings/SettingsPage'));
const EmotionalSupportPage = lazy(() => import('./features/emotional-support/EmotionalSupportPage'));

// 결제 관련 (사용 빈도 낮음)
const PricingPage = lazy(() => import('./features/pricing/PricingPage'));
const PaymentSuccessPage = lazy(() => import('./features/payment/PaymentSuccessPage'));
const PaymentFailPage = lazy(() => import('./features/payment/PaymentFailPage'));
const SubscriptionSettingsPage = lazy(() => import('./features/settings/SubscriptionSettingsPage'));

// 관리자 페이지 (관리자만 접근)
const AdminDashboard = lazy(() => import('./pages/admin/AdminDashboard'));
const QuestionReviewSystem = lazy(() => import('./pages/admin/QuestionReviewSystem'));

// ============================================
// 로딩 컴포넌트
// ============================================
const PageLoadingSpinner = () => (
  <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900">
    <div className="flex flex-col items-center gap-4">
      <div className="w-12 h-12 border-4 border-blue-500 border-t-transparent rounded-full animate-spin" />
      <p className="text-gray-600 dark:text-gray-400">로딩 중...</p>
    </div>
  </div>
);

// Suspense 래퍼 컴포넌트
const SuspenseWrapper = ({ children }: { children: React.ReactNode }) => (
  <Suspense fallback={<PageLoadingSpinner />}>
    {children}
  </Suspense>
);

// ============================================
// TanStack Query 클라이언트 설정
// ============================================
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // 5분 - 이 시간 동안 데이터는 fresh로 간주
      gcTime: 10 * 60 * 1000, // 10분 - 메모리에 캐시 유지 (v5에서 cacheTime → gcTime)
      refetchOnWindowFocus: false, // 창 포커스 시 자동 refetch 비활성화
      refetchOnMount: false, // 컴포넌트 마운트 시 자동 refetch 비활성화
      refetchOnReconnect: false, // 재연결 시 자동 refetch 비활성화
      retry: 1, // 실패 시 1번만 재시도
    },
  },
});

// ============================================
// 메인 App 컴포넌트
// ============================================
function App() {
  return (
    <ThemeProvider>
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>
          <Routes>
            {/* 랜딩 페이지 */}
            <Route path="/" element={
              <SuspenseWrapper>
                <LandingPage />
              </SuspenseWrapper>
            } />
            
            {/* 인증 페이지들 - MainLayout 없이 */}
            <Route path="/login" element={
              <SuspenseWrapper>
                <LoginPage />
              </SuspenseWrapper>
            } />
            <Route path="/register" element={
              <SuspenseWrapper>
                <RegisterPage />
              </SuspenseWrapper>
            } />
            <Route path="/onboarding" element={
              <SuspenseWrapper>
                <OnboardingPage />
              </SuspenseWrapper>
            } />
            
            {/* 메인 애플리케이션 - MainLayout 포함 */}
            <Route path="/dashboard" element={<MainLayout />}>
              <Route index element={
                <SuspenseWrapper>
                  <DashboardPage />
                </SuspenseWrapper>
              } />
              <Route path="learn" element={
                <SuspenseWrapper>
                  <UnifiedLearningPage />
                </SuspenseWrapper>
              } />
              <Route path="review" element={
                <SuspenseWrapper>
                  <ReviewPage />
                </SuspenseWrapper>
              } />
              <Route path="review/session/:sessionId" element={
                <SuspenseWrapper>
                  <ReviewSessionPage />
                </SuspenseWrapper>
              } />
              <Route path="pricing" element={
                <SuspenseWrapper>
                  <PricingPage />
                </SuspenseWrapper>
              } />
              <Route path="payment/success" element={
                <SuspenseWrapper>
                  <PaymentSuccessPage />
                </SuspenseWrapper>
              } />
              <Route path="payment/fail" element={
                <SuspenseWrapper>
                  <PaymentFailPage />
                </SuspenseWrapper>
              } />
              <Route path="community" element={
                <SuspenseWrapper>
                  <CommunityPage />
                </SuspenseWrapper>
              } />
              <Route path="settings/subscription" element={
                <SuspenseWrapper>
                  <SubscriptionSettingsPage />
                </SuspenseWrapper>
              } />
              <Route path="learning" element={
                <SuspenseWrapper>
                  <CurriculumSchedulePage />
                </SuspenseWrapper>
              } />
              <Route path="learning/old" element={
                <SuspenseWrapper>
                  <LearningPage />
                </SuspenseWrapper>
              } />
              <Route path="learning/questions/:subjectKey" element={
                <SuspenseWrapper>
                  <QuestionsPage />
                </SuspenseWrapper>
              } />
              <Route path="analytics/*" element={
                <SuspenseWrapper>
                  <AnalyticsPage />
                </SuspenseWrapper>
              } />
              <Route path="ai-assistant/*" element={
                <SuspenseWrapper>
                  <AIAssistantPage />
                </SuspenseWrapper>
              } />
              <Route path="settings/*" element={
                <SuspenseWrapper>
                  <SettingsPage />
                </SuspenseWrapper>
              } />
              
              {/* Phase C: 감성적 지원 */}
              <Route path="emotional-support" element={
                <SuspenseWrapper>
                  <EmotionalSupportPage />
                </SuspenseWrapper>
              } />
              
              {/* 관리자 전용 라우트 */}
              <Route path="admin" element={
                <SuspenseWrapper>
                  <AdminDashboard />
                </SuspenseWrapper>
              } />
              <Route path="admin/questions" element={
                <SuspenseWrapper>
                  <QuestionReviewSystem />
                </SuspenseWrapper>
              } />
            </Route>
          </Routes>
        </BrowserRouter>
        
        {/* Toast 알림 컴포넌트 */}
        <Toaster
          position="top-right"
          reverseOrder={false}
          gutter={8}
          toastOptions={{
            duration: 4000,
            style: {
              background: '#363636',
              color: '#fff',
            },
            success: {
              duration: 3000,
              style: {
                background: '#10b981',
              },
            },
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