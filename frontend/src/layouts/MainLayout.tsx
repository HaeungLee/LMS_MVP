import React, { useEffect, useState } from 'react';
import { Outlet, Link, useLocation, useNavigate } from 'react-router-dom';
import { 
  Home, 
  BookOpen, 
  BarChart3, 
  Bot, 
  Settings,
  LogOut,
  User,
  RefreshCw,
  Shield
} from 'lucide-react';
import useAuthStore from '../shared/hooks/useAuthStore';
import { api } from '../shared/services/apiClient';
import FloatingAIMentor from '../shared/components/FloatingAIMentor';

interface NavigationItem {
  id: string;
  title: string;
  icon: React.ComponentType<{ className?: string }>;
  path: string;
  description: string;
}

export default function MainLayout() {
  const location = useLocation();
  const navigate = useNavigate();
  const { user, loading, fetchMe, logout } = useAuthStore();
  const [checkingCurriculum, setCheckingCurriculum] = useState(true);

  // 사용자 역할에 따른 네비게이션 아이템 동적 생성
  const getNavigationItems = (): NavigationItem[] => {
    const baseItems = [
      {
        id: 'dashboard',
        title: '대시보드',
        icon: Home,
        path: '/',
        description: '개인화 학습 진도 overview'
      },
      {
        id: 'learning',
        title: '학습하기',
        icon: BookOpen,
        path: '/learning',
        description: '과목 선택 및 스마트 문제 풀이'
      },
      {
        id: 'analytics',
        title: '내 학습 분석',
        icon: BarChart3,
        path: '/analytics',
        description: '상세 진도 현황 및 성과 분석'
      },
      {
        id: 'ai-assistant',
        title: 'AI 학습 도우미',
        icon: Bot,
        path: '/ai-assistant',
        description: '맞춤 커리큘럼 및 1:1 AI 강사'
      },
      {
        id: 'settings',
        title: '설정 & 관리',
        icon: Settings,
        path: '/settings',
        description: '개인 프로필 및 학습 환경'
      }
    ];

    // 관리자인 경우 관리자 메뉴 추가
    if (user?.role === 'admin') {
      baseItems.push({
        id: 'admin',
        title: '시스템 관리',
        icon: Shield,
        path: '/admin',
        description: '사용자 및 시스템 관리 대시보드'
      });
    }

    return baseItems;
  };

  const navigationItems = getNavigationItems();

  // 사용자 정보 로드 - 한 번만 실행되도록 최적화
  useEffect(() => {
    if (!user && !loading) {
      console.log('🔐 사용자 정보 로드 시작');
      fetchMe().catch((error) => {
        console.log('❌ 인증 실패, 로그인 페이지로 이동:', error.message);
        // 인증 실패시 로그인 페이지로 이동
        navigate('/login');
      });
    }
  }, [user, loading]); // fetchMe와 navigate 의존성 제거로 최적화

  // 커리큘럼 체크 - 신규 사용자는 온보딩으로
  useEffect(() => {
    let mounted = true;
    
    const checkCurriculum = async () => {
      if (!user) {
        setCheckingCurriculum(false);
        return;
      }

      try {
        console.log('📚 커리큘럼 확인 중...');
        const curricula = await api.get<any[]>('/mvp/curricula/my', { timeoutMs: 5000 });
        
        if (!mounted) return;
        
        if (!curricula || curricula.length === 0) {
          console.log('❌ 커리큘럼 없음 → 온보딩으로 이동');
          navigate('/onboarding');
        } else {
          console.log('✅ 커리큘럼 있음:', curricula.length);
          setCheckingCurriculum(false);
        }
      } catch (error: any) {
        if (!mounted) return;
        
        console.log('⚠️ 커리큘럼 체크 실패:', error.message);
        // 404 에러 = 커리큘럼 없음 → 온보딩
        // 네트워크 에러 = 일단 대시보드 진입 허용
        if (error.message?.includes('404') || error.message?.includes('not found')) {
          console.log('→ 온보딩으로 이동');
          navigate('/onboarding');
        } else {
          console.log('→ 대시보드 진입 허용 (네트워크 문제일 수 있음)');
          setCheckingCurriculum(false);
        }
      }
    };

    if (user && checkingCurriculum) {
      checkCurriculum();
    }

    return () => {
      mounted = false;
    };
  }, [user, checkingCurriculum, navigate]);

  const isActiveRoute = (path: string) => {
    if (path === '/') {
      return location.pathname === '/';
    }
    return location.pathname.startsWith(path);
  };

  const handleLogout = async () => {
    try {
      await logout();
      navigate('/login');
    } catch (error) {
      console.error('로그아웃 실패:', error);
    }
  };

  // 로딩 중 (사용자 정보 + 커리큘럼 체크)
  if (loading || checkingCurriculum) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center">
        <div className="text-center">
          <RefreshCw className="w-8 h-8 animate-spin mx-auto mb-4 text-blue-600" />
          <p className="text-gray-600 dark:text-gray-300">
            {loading ? '사용자 정보를 불러오고 있습니다...' : '학습 정보를 확인하고 있습니다...'}
          </p>
        </div>
      </div>
    );
  }

  // 인증되지 않은 사용자
  if (!user) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center">
        <div className="text-center">
          <p className="text-gray-600 dark:text-gray-300 mb-4">로그인이 필요합니다.</p>
          <button 
            onClick={() => navigate('/login')}
            className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 dark:bg-blue-500 dark:hover:bg-blue-600"
          >
            로그인하기
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* 사이드 네비게이션 */}
      <aside className="fixed inset-y-0 left-0 z-50 w-64 bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700 shadow-sm">
        {/* 로고 영역 */}
        <div className="flex items-center justify-center h-16 px-6 border-b border-gray-200 dark:border-gray-700">
          <div className="flex items-center space-x-2">
            <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
              <Bot className="w-5 h-5 text-white" />
            </div>
            <span className="text-xl font-bold text-gray-900 dark:text-white">LMS Platform</span>
          </div>
        </div>

        {/* 네비게이션 메뉴 */}
        <nav className="flex-1 px-4 py-6 space-y-2">
          {navigationItems.map((item) => {
            const Icon = item.icon;
            const isActive = isActiveRoute(item.path);
            
            return (
              <Link
                key={item.id}
                to={item.path}
                className={`group flex items-center px-3 py-3 text-sm font-medium rounded-lg transition-all duration-200 ${
                  isActive
                    ? 'bg-blue-50 dark:bg-blue-900/20 border-r-2 border-blue-500 text-blue-700 dark:text-blue-400'
                    : 'text-gray-600 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 hover:text-gray-900 dark:hover:text-white'
                }`}
              >
                <Icon className={`mr-3 w-5 h-5 flex-shrink-0 ${
                  isActive ? 'text-blue-500 dark:text-blue-400' : 'text-gray-400 dark:text-gray-500 group-hover:text-gray-500 dark:group-hover:text-gray-400'
                }`} />
                <div className="flex-1 min-w-0">
                  <div className={`font-medium ${isActive ? 'text-blue-700 dark:text-blue-400' : ''}`}>
                    {item.title}
                  </div>
                  <div className="text-xs text-gray-500 dark:text-gray-400 mt-0.5 leading-tight">
                    {item.description}
                  </div>
                </div>
              </Link>
            );
          })}
        </nav>

        {/* 사용자 프로필 영역 - 실제 사용자 정보 */}
        <div className="border-t border-gray-200 dark:border-gray-700 p-4">
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 bg-blue-100 dark:bg-blue-900 rounded-full flex items-center justify-center">
              <User className="w-4 h-4 text-blue-600 dark:text-blue-400" />
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-gray-900 dark:text-white truncate">
                {user.display_name || user.email}
              </p>
              <p className="text-xs text-gray-500 dark:text-gray-400">
                {user.role === 'admin' ? '관리자' : 
                 user.role === 'teacher' ? '교사' : '학습자'}
              </p>
            </div>
            <button 
              onClick={handleLogout}
              className="p-1 text-gray-400 hover:text-gray-600 dark:text-gray-500 dark:hover:text-gray-300 transition-colors"
              title="로그아웃"
            >
              <LogOut className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* API 연결 상태 표시 */}
        <div className="px-4 pb-4">
          <div className="bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg p-2">
            <div className="flex items-center text-xs text-green-800 dark:text-green-400">
              <div className="w-2 h-2 bg-green-500 rounded-full mr-2"></div>
              <span>백엔드 API 연결됨</span>
            </div>
          </div>
        </div>
      </aside>

      {/* 메인 콘텐츠 영역 */}
      <main className="ml-64 min-h-screen">
        <div className="px-6 py-8">
          <Outlet />
        </div>
      </main>

      {/* 플로팅 AI 멘토 - 모든 페이지에서 접근 가능 */}
      <FloatingAIMentor />
    </div>
  );
}