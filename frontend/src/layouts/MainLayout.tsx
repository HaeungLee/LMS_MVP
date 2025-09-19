import React, { useEffect } from 'react';
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
    if (user?.is_admin) {
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

  // 사용자 정보 로드
  useEffect(() => {
    if (!user && !loading) {
      fetchMe().catch(() => {
        // 인증 실패시 로그인 페이지로 이동
        navigate('/login');
      });
    }
  }, [user, loading, fetchMe, navigate]);

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

  // 로딩 중
  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <RefreshCw className="w-8 h-8 animate-spin mx-auto mb-4 text-blue-600" />
          <p className="text-gray-600">사용자 정보를 불러오고 있습니다...</p>
        </div>
      </div>
    );
  }

  // 인증되지 않은 사용자
  if (!user) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <p className="text-gray-600 mb-4">로그인이 필요합니다.</p>
          <button 
            onClick={() => navigate('/login')}
            className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
          >
            로그인하기
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* 사이드 네비게이션 */}
      <aside className="fixed inset-y-0 left-0 z-50 w-64 bg-white border-r border-gray-200 shadow-sm">
        {/* 로고 영역 */}
        <div className="flex items-center justify-center h-16 px-6 border-b border-gray-200">
          <div className="flex items-center space-x-2">
            <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
              <Bot className="w-5 h-5 text-white" />
            </div>
            <span className="text-xl font-bold text-gray-900">LMS Platform</span>
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
                    ? 'bg-blue-50 border-r-2 border-blue-500 text-blue-700'
                    : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                }`}
              >
                <Icon className={`mr-3 w-5 h-5 flex-shrink-0 ${
                  isActive ? 'text-blue-500' : 'text-gray-400 group-hover:text-gray-500'
                }`} />
                <div className="flex-1 min-w-0">
                  <div className={`font-medium ${isActive ? 'text-blue-700' : ''}`}>
                    {item.title}
                  </div>
                  <div className="text-xs text-gray-500 mt-0.5 leading-tight">
                    {item.description}
                  </div>
                </div>
              </Link>
            );
          })}
        </nav>

        {/* 사용자 프로필 영역 - 실제 사용자 정보 */}
        <div className="border-t border-gray-200 p-4">
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
              <User className="w-4 h-4 text-blue-600" />
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-gray-900 truncate">
                {user.display_name || user.email}
              </p>
              <p className="text-xs text-gray-500">
                {user.role === 'admin' ? '관리자' : 
                 user.role === 'teacher' ? '교사' : '학습자'}
              </p>
            </div>
            <button 
              onClick={handleLogout}
              className="p-1 text-gray-400 hover:text-gray-600 transition-colors"
              title="로그아웃"
            >
              <LogOut className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* API 연결 상태 표시 */}
        <div className="px-4 pb-4">
          <div className="bg-green-50 border border-green-200 rounded-lg p-2">
            <div className="flex items-center text-xs text-green-800">
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
    </div>
  );
}