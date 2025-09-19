import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import MainLayout from './layouts/MainLayout';
import DashboardPage from './features/dashboard/DashboardPage';
import LearningPage from './features/learning/LearningPage';
import AnalyticsPage from './features/analytics/AnalyticsPage';
import AIAssistantPage from './features/ai-assistant/AIAssistantPage';
import SettingsPage from './features/settings/SettingsPage';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';

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
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          {/* 인증 페이지들 - MainLayout 없이 */}
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
          
          {/* 메인 애플리케이션 - MainLayout 포함 */}
          <Route path="/" element={<MainLayout />}>
            <Route index element={<DashboardPage />} />
            <Route path="learning/*" element={<LearningPage />} />
            <Route path="analytics/*" element={<AnalyticsPage />} />
            <Route path="ai-assistant/*" element={<AIAssistantPage />} />
            <Route path="settings/*" element={<SettingsPage />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  );
}

export default App;