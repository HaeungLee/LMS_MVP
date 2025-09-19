import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { 
  Users, 
  BookOpen, 
  Brain, 
  TrendingUp, 
  AlertTriangle,
  CheckCircle,
  Clock,
  Activity,
  Database,
  Cpu,
  HardDrive,
  Shield
} from 'lucide-react';
import { adminApi } from '../../shared/services/apiClient';

interface AdminDashboardProps {}

const AdminDashboard: React.FC<AdminDashboardProps> = () => {
  // 관리자 대시보드 데이터 가져오기
  const { data: dashboardData, isLoading: isDashboardLoading } = useQuery({
    queryKey: ['admin', 'dashboard'],
    queryFn: adminApi.getDashboard,
  });

  // 시스템 건강도 데이터 가져오기
  const { data: systemHealth, isLoading: isHealthLoading } = useQuery({
    queryKey: ['admin', 'system-health'],
    queryFn: adminApi.getSystemHealth,
    refetchInterval: 30000, // 30초마다 갱신
  });

  if (isDashboardLoading || isHealthLoading) {
    return (
      <div className="p-6">
        <div className="animate-pulse space-y-6">
          <div className="h-8 bg-gray-200 rounded w-1/3"></div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="h-32 bg-gray-200 rounded-lg"></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  const getHealthColor = (score: number) => {
    if (score >= 95) return 'text-green-600 bg-green-100';
    if (score >= 85) return 'text-yellow-600 bg-yellow-100';
    return 'text-red-600 bg-red-100';
  };

  const getComponentStatusColor = (status: string) => {
    switch (status) {
      case 'healthy': return 'text-green-600 bg-green-100';
      case 'warning': return 'text-yellow-600 bg-yellow-100';
      case 'error': return 'text-red-600 bg-red-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  return (
    <div className="p-6 max-w-7xl mx-auto">
      {/* 헤더 */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">관리자 대시보드</h1>
        <p className="text-gray-600">LMS 시스템의 전체 현황을 모니터링하고 관리합니다</p>
      </div>

      {/* 주요 통계 카드 */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <div className="flex items-center">
            <div className="p-3 bg-blue-100 rounded-lg">
              <Users className="w-6 h-6 text-blue-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">전체 사용자</p>
              <p className="text-2xl font-bold text-gray-900">{dashboardData?.total_users?.toLocaleString()}</p>
            </div>
          </div>
          <div className="mt-4 flex items-center text-sm">
            <span className="text-green-600">활성 사용자: {dashboardData?.active_users}</span>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <div className="flex items-center">
            <div className="p-3 bg-green-100 rounded-lg">
              <BookOpen className="w-6 h-6 text-green-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">전체 문제</p>
              <p className="text-2xl font-bold text-gray-900">{dashboardData?.total_questions?.toLocaleString()}</p>
            </div>
          </div>
          <div className="mt-4 flex items-center text-sm">
            <span className="text-blue-600">토픽: {dashboardData?.total_topics}</span>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <div className="flex items-center">
            <div className="p-3 bg-purple-100 rounded-lg">
              <Brain className="w-6 h-6 text-purple-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">AI 생성 문제</p>
              <p className="text-2xl font-bold text-gray-900">{dashboardData?.ai_questions_generated?.toLocaleString()}</p>
            </div>
          </div>
          <div className="mt-4 flex items-center text-sm">
            <span className="text-purple-600">오늘 생성: +45</span>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <div className="flex items-center">
            <div className={`p-3 rounded-lg ${getHealthColor(systemHealth?.overall_health || 0)}`}>
              <Activity className="w-6 h-6" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">시스템 상태</p>
              <p className="text-2xl font-bold text-gray-900">{systemHealth?.overall_health?.toFixed(1)}%</p>
            </div>
          </div>
          <div className="mt-4 flex items-center text-sm">
            <span className="text-gray-600">응답시간: {systemHealth?.api_response_time}ms</span>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
        {/* 최근 활동 */}
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">최근 활동</h3>
          <div className="space-y-4">
            {dashboardData?.recent_activities?.map((activity, index) => (
              <div key={index} className="flex items-center justify-between py-3 border-b border-gray-100 last:border-b-0">
                <div className="flex items-center">
                  <div className="p-2 bg-blue-100 rounded-lg mr-3">
                    {activity.type === 'user_registration' && <Users className="w-4 h-4 text-blue-600" />}
                    {activity.type === 'ai_questions_generated' && <Brain className="w-4 h-4 text-purple-600" />}
                    {activity.type === 'curriculum_created' && <BookOpen className="w-4 h-4 text-green-600" />}
                  </div>
                  <div>
                    <p className="text-sm font-medium text-gray-900">
                      {activity.type === 'user_registration' && '새 사용자 등록'}
                      {activity.type === 'ai_questions_generated' && 'AI 문제 생성'}
                      {activity.type === 'curriculum_created' && '커리큘럼 생성'}
                    </p>
                    <p className="text-xs text-gray-500">{activity.period}</p>
                  </div>
                </div>
                <span className="text-lg font-bold text-gray-900">+{activity.count}</span>
              </div>
            ))}
          </div>
        </div>

        {/* 시스템 리소스 */}
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">시스템 리소스</h3>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <Cpu className="w-5 h-5 text-blue-600 mr-3" />
                <span className="text-sm font-medium text-gray-700">CPU 사용률</span>
              </div>
              <div className="flex items-center">
                <span className="text-sm font-bold text-gray-900 mr-2">{systemHealth?.cpu_usage?.toFixed(1)}%</span>
                <div className="w-20 h-2 bg-gray-200 rounded-full">
                  <div 
                    className="h-2 bg-blue-600 rounded-full" 
                    style={{ width: `${systemHealth?.cpu_usage}%` }}
                  ></div>
                </div>
              </div>
            </div>

            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <Database className="w-5 h-5 text-green-600 mr-3" />
                <span className="text-sm font-medium text-gray-700">메모리 사용률</span>
              </div>
              <div className="flex items-center">
                <span className="text-sm font-bold text-gray-900 mr-2">{systemHealth?.memory_usage?.toFixed(1)}%</span>
                <div className="w-20 h-2 bg-gray-200 rounded-full">
                  <div 
                    className="h-2 bg-green-600 rounded-full" 
                    style={{ width: `${systemHealth?.memory_usage}%` }}
                  ></div>
                </div>
              </div>
            </div>

            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <HardDrive className="w-5 h-5 text-yellow-600 mr-3" />
                <span className="text-sm font-medium text-gray-700">디스크 사용률</span>
              </div>
              <div className="flex items-center">
                <span className="text-sm font-bold text-gray-900 mr-2">{systemHealth?.disk_usage?.toFixed(1)}%</span>
                <div className="w-20 h-2 bg-gray-200 rounded-full">
                  <div 
                    className="h-2 bg-yellow-600 rounded-full" 
                    style={{ width: `${systemHealth?.disk_usage}%` }}
                  ></div>
                </div>
              </div>
            </div>

            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <Shield className="w-5 h-5 text-purple-600 mr-3" />
                <span className="text-sm font-medium text-gray-700">활성 연결</span>
              </div>
              <span className="text-sm font-bold text-gray-900">{systemHealth?.database_connections}</span>
            </div>
          </div>
        </div>
      </div>

      {/* 컴포넌트 상태 */}
      <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">시스템 컴포넌트 상태</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {systemHealth?.components?.map((component, index) => (
            <div key={index} className="p-4 border border-gray-200 rounded-lg">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium text-gray-700">{component.name}</span>
                <div className={`px-2 py-1 rounded-full text-xs font-medium ${getComponentStatusColor(component.status)}`}>
                  {component.status === 'healthy' && <CheckCircle className="w-3 h-3 inline mr-1" />}
                  {component.status === 'warning' && <AlertTriangle className="w-3 h-3 inline mr-1" />}
                  {component.status === 'error' && <AlertTriangle className="w-3 h-3 inline mr-1" />}
                  {component.status === 'healthy' ? '정상' : component.status === 'warning' ? '주의' : '오류'}
                </div>
              </div>
              <div className="flex items-center text-xs text-gray-500">
                <Clock className="w-3 h-3 mr-1" />
                <span>{component.response_time}ms</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default AdminDashboard;
