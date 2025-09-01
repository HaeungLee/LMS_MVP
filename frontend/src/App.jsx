import React from 'react';
import './index.css';
import { BrowserRouter as Router, Routes, Route, Link, useLocation, Navigate } from 'react-router-dom';
import DashboardPage from './pages/DashboardPage';
import QuizPage from './pages/QuizPage';
import ResultsPage from './pages/ResultsPage';
import AuthLogin from './pages/AuthLogin';
import AuthRegister from './pages/AuthRegister';
import AdminQuestions from './pages/AdminQuestions';
import TeacherDashboard from './pages/TeacherDashboard';
import AIFeaturesPage2 from './pages/AIFeaturesPage2';
import BetaDashboard from './pages/BetaDashboard';
import BetaOnboarding2 from './components/onboarding/BetaOnboarding2';
import useAuthStore from './stores/authStore';
import { SUBJECTS, getSubjectName, getSubjectIcon } from './constants/subjects';
import lmsLogo from './image/LMS.png';

function Navigation() {
  const location = useLocation();
  const { user, logout } = useAuthStore();
  const [showQuizDropdown, setShowQuizDropdown] = React.useState(false);
  
  const navStyle = {
    backgroundColor: '#1f2937',
    padding: '16px 0',
    boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
  };

  const containerStyle = {
    maxWidth: '1200px',
    margin: '0 auto',
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: '0 24px'
  };

  const logoStyle = {
    display: 'flex',
    alignItems: 'center',
    textDecoration: 'none'
  };

  const navListStyle = {
    display: 'flex',
    listStyle: 'none',
    margin: 0,
    padding: 0,
    gap: '24px'
  };

  // Prefer class-based styling (more reliable and visible in DevTools).
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
            style={{
              height: '60px',
              width: 'auto',
              marginRight: '8px'
            }}
          />
          <span style={{
            color: '#ffffff',
            fontSize: '18px',
            fontWeight: 'bold'
          }}>
            
          </span>
        </Link>
        <ul style={navListStyle}>
          <li>
            <Link to="/" className={getLinkClass('/')}>
              대시보드
            </Link>
          </li>
          <li>
            <div 
              style={{ 
                position: 'relative',
                display: 'inline-block'
              }}
              onMouseLeave={() => setShowQuizDropdown(false)}
            >
              <button
                onClick={() => setShowQuizDropdown(!showQuizDropdown)}
                onMouseEnter={() => setShowQuizDropdown(true)}
                style={{
                  backgroundColor: 'transparent',
                  border: 'none',
                  color: location.pathname.includes('/quiz') ? '#3b82f6' : '#d1d5db',
                  fontSize: '16px',
                  cursor: 'pointer',
                  padding: '8px 12px',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '4px',
                  height: '40px', // 고정 높이
                  minWidth: '80px' // 최소 너비
                }}
              >
                퀴즈 ▼
              </button>
              {showQuizDropdown && (
                <div style={{
                  position: 'absolute',
                  top: 'calc(100% + 2px)', // 버튼 바로 아래
                  left: '0',
                  backgroundColor: '#374151',
                  border: '1px solid #4b5563',
                  borderRadius: '8px',
                  padding: '8px 0',
                  minWidth: '200px',
                  zIndex: 9999, // 높은 z-index
                  boxShadow: '0 8px 16px rgba(0, 0, 0, 0.2)',
                  // 레이아웃에 영향을 주지 않도록 완전히 격리
                  transform: 'translateZ(0)', // 하드웨어 가속
                  willChange: 'transform' // 성능 최적화
                }}>
                  {Object.entries(SUBJECTS).map(([key, name]) => (
                    <Link
                      key={key}
                      to={`/quiz/${key}`}
                      onClick={() => setShowQuizDropdown(false)}
                      style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: '8px',
                        padding: '8px 16px',
                        color: '#d1d5db',
                        textDecoration: 'none',
                        fontSize: '14px',
                        transition: 'background-color 0.2s'
                      }}
                      onMouseEnter={(e) => e.target.style.backgroundColor = '#4b5563'}
                      onMouseLeave={(e) => e.target.style.backgroundColor = 'transparent'}
                    >
                      {getSubjectIcon(key)} {name}
                    </Link>
                  ))}
                </div>
              )}
            </div>
          </li>
          <li>
            <Link to="/ai-features" className={getLinkClass('/ai-features')}>
              AI 기능
            </Link>
          </li>
          <li>
            <Link to="/beta-onboarding2" className={getLinkClass('/beta-onboarding2')}>
              베타 온보딩
            </Link>
          </li>
          {(user && (user.role === 'teacher' || user.role === 'admin')) && (
            <>
              <li>
                <Link to="/teacher/dashboard" className={getLinkClass('/teacher/dashboard')}>
                  교사용 대시보드
                </Link>
              </li>
              <li>
                <Link to="/beta-dashboard" className={getLinkClass('/beta-dashboard')}>
                  베타 대시보드
                </Link>
              </li>
            </>
          )}
          {/* 결과 페이지는 제출 후 라우팅으로만 접근 */}
        </ul>
        <div>
          {user ? (
            <div style={{ display:'flex', alignItems:'center', gap:8 }}>
              {(user.role === 'teacher' || user.role === 'admin') && (
                <Link to="/admin/questions" style={{ color:'#d1d5db', textDecoration:'none', fontSize:'13px', marginRight: 6 }}>문항 출제</Link>
              )}
              <span style={{ color:'#d1d5db', fontSize:'13px', maxWidth:'120px', overflow:'hidden', textOverflow:'ellipsis', whiteSpace:'nowrap' }}>
                {user.display_name || user.email.split('@')[0]}
              </span>
              <button onClick={logout} style={{ padding:'4px 8px', borderRadius:4, border:'1px solid #4b5563', background:'#374151', color:'#fff', fontSize:'12px' }}>로그아웃</button>
            </div>
          ) : (
            <div style={{ display:'flex', alignItems:'center', gap:8 }}>
              <Link to="/login" style={{ color:'#d1d5db', textDecoration:'none', fontSize:'13px' }}>로그인</Link>
              <Link to="/register" style={{ color:'#d1d5db', textDecoration:'none', fontSize:'13px' }}>회원가입</Link>
            </div>
          )}
        </div>
      </div>
    </nav>
  );
}

function App() {
  return (
    <Router>
      <div style={{ minHeight: '100vh', backgroundColor: '#f9fafb' }}>
        <Navigation />
        
        <main>
          <Routes>
            <Route path="/" element={<DashboardPage />} />
            <Route path="/quiz" element={<Protected><QuizPage /></Protected>} />
            <Route path="/quiz/:subject" element={<Protected><QuizPage /></Protected>} />
            <Route path="/results/:submission_id" element={<ResultsPage />} />
            <Route path="/ai-features" element={<AIFeaturesPage2 />} />
            <Route path="/beta-onboarding2" element={<BetaOnboarding2 userId={1} onComplete={() => alert('온보딩 완료!')} />} />
            <Route path="/beta-dashboard" element={<Protected><BetaDashboard /></Protected>} />
            <Route path="/teacher/dashboard" element={<Protected><TeacherDashboard /></Protected>} />
            <Route path="/admin/questions" element={<Protected><AdminQuestions /></Protected>} />
            <Route path="/login" element={<AuthLogin />} />
            <Route path="/register" element={<AuthRegister />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

function Protected({ children }) {
  const { user } = useAuthStore();
  if (!user) return <Navigate to="/login" replace />
  return children;
}

export default App;