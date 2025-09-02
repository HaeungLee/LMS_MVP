import React from 'react';
import './index.css';
import { BrowserRouter as Router, Routes, Route, Link, useLocation, Navigate } from 'react-router-dom';
import { AnimatePresence, motion } from 'framer-motion';
import { Toaster } from 'react-hot-toast';

import DashboardPage from './pages/DashboardPage';
import QuizPage from './pages/QuizPage';
import QuizModeSelectionPage from './pages/QuizModeSelectionPage';
import CodeExecutionPage from './pages/CodeExecutionPage';
import CodeProblemsPage from './pages/CodeProblemsPage';
import ResultsPage from './pages/ResultsPage';
import AuthLogin from './pages/AuthLogin';
import AuthRegister from './pages/AuthRegister';
import UnifiedRegistration from './components/registration/UnifiedRegistration';
import AdminQuestions from './pages/AdminQuestions';
import AdminCodeProblems from './pages/AdminCodeProblems';
import TeacherDashboard from './pages/TeacherDashboard';
import AIFeaturesPage2 from './pages/AIFeaturesPage2';
import BetaDashboard from './pages/BetaDashboard';
import DynamicSubjectsPage from './pages/DynamicSubjectsPage';
import BetaOnboarding2 from './components/onboarding/BetaOnboarding2';

import useAuthStore from './stores/authStore';
// (필요 시 사용) import { SUBJECTS, getSubjectName, getSubjectIcon } from './constants/subjects';
import lmsLogo from './image/LMS.png';

function Navigation() {
  const location = useLocation();
  const { user, logout } = useAuthStore();

  const navStyle = {
    backgroundColor: '#1f2937',
    padding: '16px 0',
    boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
  };

  const containerStyle = {
    maxWidth: '1200px',
    margin: '0 auto',
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: '0 24px',
  };

  const logoStyle = {
    display: 'flex',
    alignItems: 'center',
    textDecoration: 'none',
  };

  const navListStyle = {
    display: 'flex',
    listStyle: 'none',
    margin: 0,
    padding: 0,
    gap: '24px',
  };

  // 경로 활성화 표시용 클래스
  const getLinkClass = (path) => {
    const isActive = location.pathname === path;
    return `nav-link${isActive ? ' active' : ''}`;
  };

  return (
    <nav style={navStyle}>
      <div style={containerStyle}>
        <Link to="/" style={logoStyle}>
          <img
            src={lmsLogo}
            alt="LMS MVP"
            style={{ height: '60px', width: 'auto', marginRight: '8px' }}
          />
          <span style={{ color: '#ffffff', fontSize: '18px', fontWeight: 'bold' }}>
            {/* 로고 텍스트가 필요하면 여기에 */}
          </span>
        </Link>

        <ul style={navListStyle}>
          <li>
            <Link to="/" className={getLinkClass('/')}>대시보드</Link>
          </li>
          <li>
            <Link to="/quiz" className={getLinkClass('/quiz')}>퀴즈</Link>
          </li>
          <li>
            <Link to="/code" className={getLinkClass('/code')}>코딩 테스트</Link>
          </li>
          <li>
            <Link to="/ai-features" className={getLinkClass('/ai-features')}>AI 기능</Link>
          </li>

          {(user && (user.role === 'teacher' || user.role === 'admin')) && (
            <>
              <li>
                <Link to="/teacher/dashboard" className={getLinkClass('/teacher/dashboard')}>교사용 대시보드</Link>
              </li>
              <li>
                <Link to="/beta-dashboard" className={getLinkClass('/beta-dashboard')}>베타 대시보드</Link>
              </li>
            </>
          )}
        </ul>

        <div>
          {user ? (
            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              {(user.role === 'teacher' || user.role === 'admin') && (
                <>
                  <Link to="/admin/questions" style={{ color: '#d1d5db', textDecoration: 'none', fontSize: '13px', marginRight: 6 }}>문항 출제</Link>
                  <Link to="/admin/code-problems" style={{ color: '#d1d5db', textDecoration: 'none', fontSize: '13px', marginRight: 6 }}>코딩 문제</Link>
                  <Link to="/admin/dynamic-subjects" style={{ color: '#d1d5db', textDecoration: 'none', fontSize: '13px', marginRight: 6 }}>과목 관리</Link>
                </>
              )}
              <span
                style={{
                  color: '#d1d5db',
                  fontSize: '13px',
                  maxWidth: '120px',
                  overflow: 'hidden',
                  textOverflow: 'ellipsis',
                  whiteSpace: 'nowrap',
                }}
                title={user.display_name || user.email}
              >
                {user.display_name || user.email.split('@')[0]}
              </span>
              <button
                onClick={logout}
                style={{
                  padding: '4px 8px',
                  borderRadius: 4,
                  border: '1px solid #4b5563',
                  background: '#374151',
                  color: '#fff',
                  fontSize: '12px',
                }}
              >
                로그아웃
              </button>
            </div>
          ) : (
            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <Link to="/login" style={{ color: '#d1d5db', textDecoration: 'none', fontSize: '13px' }}>로그인</Link>
              <Link to="/register" style={{ color: '#d1d5db', textDecoration: 'none', fontSize: '13px' }}>회원가입</Link>
            </div>
          )}
        </div>
      </div>
    </nav>
  );
}

// 페이지 전환 애니메이션 래퍼
function AnimatedPage({ children }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      transition={{ duration: 0.3, ease: 'easeInOut' }}
    >
      {children}
    </motion.div>
  );
}

function AppContent() {
  const location = useLocation();

  return (
    <div style={{ minHeight: '100vh', backgroundColor: '#f9fafb' }}>
      <Navigation />

      <main>
        <AnimatePresence mode="wait">
          <Routes location={location} key={location.pathname}>
            <Route path="/" element={<AnimatedPage><DashboardPage /></AnimatedPage>} />
            <Route path="/quiz" element={<Protected><AnimatedPage><QuizModeSelectionPage /></AnimatedPage></Protected>} />
            <Route path="/quiz/mixed" element={<Protected><AnimatedPage><QuizPage /></AnimatedPage></Protected>} />
            <Route path="/quiz/:subject" element={<Protected><AnimatedPage><QuizPage /></AnimatedPage></Protected>} />
            <Route path="/code/problems" element={<Protected><AnimatedPage><CodeProblemsPage /></AnimatedPage></Protected>} />
            <Route path="/code/:problemId" element={<Protected><AnimatedPage><CodeExecutionPage /></AnimatedPage></Protected>} />
            <Route path="/code" element={<Protected><AnimatedPage><CodeExecutionPage /></AnimatedPage></Protected>} />
            <Route path="/results/:submission_id" element={<AnimatedPage><ResultsPage /></AnimatedPage>} />
            <Route path="/ai-features" element={<AnimatedPage><AIFeaturesPage2 /></AnimatedPage>} />
            <Route path="/beta-onboarding2" element={<AnimatedPage><BetaOnboarding2 userId={1} onComplete={() => alert('온보딩 완료!')} /></AnimatedPage>} />
            <Route path="/beta-dashboard" element={<Protected><AnimatedPage><BetaDashboard /></AnimatedPage></Protected>} />
            <Route path="/teacher/dashboard" element={<Protected><AnimatedPage><TeacherDashboard /></AnimatedPage></Protected>} />
            <Route path="/admin/questions" element={<Protected><AnimatedPage><AdminQuestions /></AnimatedPage></Protected>} />
            <Route path="/admin/code-problems" element={<Protected><AnimatedPage><AdminCodeProblems /></AnimatedPage></Protected>} />
            <Route path="/admin/dynamic-subjects" element={<Protected><AnimatedPage><DynamicSubjectsPage /></AnimatedPage></Protected>} />
            <Route path="/login" element={<AnimatedPage><AuthLogin /></AnimatedPage>} />
            <Route path="/register" element={<AnimatedPage><UnifiedRegistration /></AnimatedPage>} />
            {/* 필요 시 404 처리: <Route path="*" element={<Navigate to="/" replace />} /> */}
          </Routes>
        </AnimatePresence>
      </main>

      {/* Toast 알림 */}
      <Toaster
        position="top-right"
        toastOptions={{
          duration: 4000,
          style: { background: '#363636', color: '#fff' },
          success: { duration: 3000, theme: { primary: 'green', secondary: 'black' } },
          error: { duration: 5000 },
        }}
      />
    </div>
  );
}

function Protected({ children }) {
  const { user } = useAuthStore();
  if (!user) return <Navigate to="/login" replace />;
  return children;
}

function App() {
  return (
    <Router>
      <AppContent />
    </Router>
  );
}

export default App;
