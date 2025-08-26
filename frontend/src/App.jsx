import { BrowserRouter as Router, Routes, Route, Link, useLocation, Navigate } from 'react-router-dom';
import DashboardPage from './pages/DashboardPage';
import QuizPage from './pages/QuizPage';
import ResultsPage from './pages/ResultsPage';
import AuthLogin from './pages/AuthLogin';
import AuthRegister from './pages/AuthRegister';
import AdminQuestions from './pages/AdminQuestions';
import TeacherDashboard from './pages/TeacherDashboard';
import AIFeaturesPage from './pages/AIFeaturesPage';
import BetaDashboard from './pages/BetaDashboard';
import BetaOnboarding from './components/onboarding/BetaOnboarding';
import useAuthStore from './stores/authStore';

function Navigation() {
  const location = useLocation();
  const { user, logout } = useAuthStore();
  
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
    color: '#ffffff',
    fontSize: '20px',
    fontWeight: 'bold',
    textDecoration: 'none'
  };

  const navListStyle = {
    display: 'flex',
    listStyle: 'none',
    margin: 0,
    padding: 0,
    gap: '24px'
  };

  const getLinkStyle = (path) => ({
    color: location.pathname === path ? '#3b82f6' : '#d1d5db',
    textDecoration: 'none',
    fontWeight: '500',
    padding: '6px 12px',
    borderRadius: '6px',
    transition: 'all 0.2s',
    backgroundColor: location.pathname === path ? '#374151' : 'transparent',
    fontSize: '14px'
  });

  return (
    <nav style={navStyle}>
      <div style={containerStyle}>
        <Link to="/" style={logoStyle}>
          🎓 LMS MVP
        </Link>
        <ul style={navListStyle}>
          <li>
            <Link to="/" style={getLinkStyle('/')}>
              대시보드
            </Link>
          </li>
          <li>
            <Link to="/quiz" style={getLinkStyle('/quiz')}>
              퀴즈
            </Link>
          </li>
          <li>
            <Link to="/ai-features" style={getLinkStyle('/ai-features')}>
              🤖 AI 기능
            </Link>
          </li>
          <li>
            <Link to="/beta-onboarding" style={getLinkStyle('/beta-onboarding')}>
              🧪 베타 온보딩
            </Link>
          </li>
          {(user && (user.role === 'teacher' || user.role === 'admin')) && (
            <>
              <li>
                <Link to="/teacher/dashboard" style={getLinkStyle('/teacher/dashboard')}>
                  교사용 대시보드
                </Link>
              </li>
              <li>
                <Link to="/beta-dashboard" style={getLinkStyle('/beta-dashboard')}>
                  📊 베타 대시보드
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
            <Route path="/results/:submission_id" element={<ResultsPage />} />
            <Route path="/ai-features" element={<AIFeaturesPage />} />
            <Route path="/beta-onboarding" element={<BetaOnboarding userId={1} onComplete={() => alert('온보딩 완료!')} />} />
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