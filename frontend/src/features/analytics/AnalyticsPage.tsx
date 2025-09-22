import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { BarChart3, TrendingUp, Target, Clock, RefreshCw, AlertCircle } from 'lucide-react';
import { analyticsApi } from '../../shared/services/apiClient';
import useAuthStore from '../../shared/hooks/useAuthStore';

export default function AnalyticsPage() {
  const { user } = useAuthStore();
  
  // 실제 통합 학습 분석 데이터 조회
  const { data: analyticsData, isLoading: analyticsLoading, error: analyticsError, refetch } = useQuery({
    queryKey: ['analytics', user?.id],
    queryFn: () => analyticsApi.getUnifiedAnalytics(user!.id),
    enabled: !!user,
    staleTime: 5 * 60 * 1000, // 5분
  });

  // 일일 통계 데이터 조회 (실제 존재하는 엔드포인트)
  const { data: dailyStats } = useQuery({
    queryKey: ['dailyStats', user?.id],
    queryFn: () => analyticsApi.getDailyStats(user!.id),
    enabled: !!user,
    staleTime: 5 * 60 * 1000,
  });

  // 진도 데이터 조회
  const { data: progressData } = useQuery({
    queryKey: ['progress', user?.id],
    queryFn: () => analyticsApi.getProgress(user!.id),
    enabled: !!user,
    staleTime: 5 * 60 * 1000,
  });

  const isLoading = analyticsLoading;
  const error = analyticsError;

  if (isLoading) {
    return (
      <div className="max-w-7xl mx-auto">
        <div className="flex items-center justify-center h-64">
          <div className="text-center">
            <RefreshCw className="w-8 h-8 animate-spin mx-auto mb-4 text-blue-600" />
            <p className="text-gray-600">학습 분석 데이터를 불러오고 있습니다...</p>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-7xl mx-auto">
        <div className="bg-red-50 border border-red-200 rounded-lg p-6">
          <div className="flex items-center mb-4">
            <AlertCircle className="w-6 h-6 text-red-600 mr-3" />
            <h3 className="text-red-800 font-medium">분석 데이터 로드 실패</h3>
          </div>
          <p className="text-red-600 mb-4">
            {error instanceof Error ? error.message : '알 수 없는 오류가 발생했습니다.'}
          </p>
          <button 
            onClick={() => refetch()}
            className="bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700"
          >
            다시 시도
          </button>
        </div>
      </div>
    );
  }

  // 분석 데이터 처리
  const hasAnalyticsData = analyticsData?.success && analyticsData?.data;
  const analytics = hasAnalyticsData ? analyticsData.data : null;
  
  // 일일 통계 데이터 처리
  const daily = dailyStats || {};
  
  // 진도 데이터 처리
  const progress = progressData || {};

  return (
    <div className="max-w-7xl mx-auto">
      {/* 헤더 */}
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900 flex items-center">
          <BarChart3 className="w-8 h-8 text-blue-600 mr-3" />
          학습 분석
        </h1>
        <p className="text-gray-600 mt-1">
          실제 학습 데이터를 기반으로 한 상세 분석입니다.
        </p>
      </div>

      {/* 데이터 없음 안내 */}
      {!hasAnalyticsData && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-8 mb-8">
          <div className="text-center">
            <BarChart3 className="w-16 h-16 text-blue-600 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-blue-900 mb-3">학습 데이터를 수집 중입니다</h3>
            <p className="text-blue-800 mb-6">
              {analyticsData?.message || '충분한 학습 데이터가 수집되면 상세한 분석을 제공해드립니다.'}
            </p>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 max-w-2xl mx-auto">
              <div className="bg-white rounded-lg p-4 border border-blue-200">
                <Target className="w-8 h-8 text-blue-600 mx-auto mb-2" />
                <h4 className="font-medium text-blue-900 mb-1">문제 풀기</h4>
                <p className="text-sm text-blue-700">다양한 문제를 풀어 학습 패턴을 생성하세요</p>
              </div>
              <div className="bg-white rounded-lg p-4 border border-blue-200">
                <Clock className="w-8 h-8 text-blue-600 mx-auto mb-2" />
                <h4 className="font-medium text-blue-900 mb-1">꾸준한 학습</h4>
                <p className="text-sm text-blue-700">일주일 이상 꾸준히 학습하면 트렌드 분석이 가능합니다</p>
              </div>
              <div className="bg-white rounded-lg p-4 border border-blue-200">
                <TrendingUp className="w-8 h-8 text-blue-600 mx-auto mb-2" />
                <h4 className="font-medium text-blue-900 mb-1">진도 달성</h4>
                <p className="text-sm text-blue-700">여러 과목에서 진도를 달성하면 상세 분석을 볼 수 있습니다</p>
              </div>
            </div>
            <div className="mt-6 space-x-3">
              <button 
                onClick={() => window.location.href = '/learning'}
                className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 font-medium"
              >
                학습하러 가기
              </button>
              <button 
                onClick={() => window.location.href = '/ai-assistant'}
                className="bg-green-600 text-white px-6 py-3 rounded-lg hover:bg-green-700 font-medium"
              >
                AI 도우미 사용하기
              </button>
            </div>
          </div>
        </div>
      )}

      {/* 오늘의 학습 통계 (일일 데이터가 있는 경우) */}
      {daily && Object.keys(daily).length > 0 && (
        <div className="mb-8">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">오늘의 학습</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <div className="bg-white rounded-lg p-6 shadow-sm border border-gray-200">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">풀어낸 문제</p>
                  <p className="text-2xl font-bold text-gray-900">
                    {daily.total_questions || 0}개
                  </p>
                </div>
                <div className="p-2 bg-blue-100 rounded-lg">
                  <Target className="w-6 h-6 text-blue-600" />
                </div>
              </div>
            </div>

            <div className="bg-white rounded-lg p-6 shadow-sm border border-gray-200">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">정답률</p>
                  <p className="text-2xl font-bold text-gray-900">
                    {Math.round(daily.accuracy || 0)}%
                  </p>
                </div>
                <div className="p-2 bg-green-100 rounded-lg">
                  <TrendingUp className="w-6 h-6 text-green-600" />
                </div>
              </div>
            </div>

            <div className="bg-white rounded-lg p-6 shadow-sm border border-gray-200">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">학습 시간</p>
                  <p className="text-2xl font-bold text-gray-900">
                    {Math.round(daily.study_minutes || 0)}분
                  </p>
                </div>
                <div className="p-2 bg-purple-100 rounded-lg">
                  <Clock className="w-6 h-6 text-purple-600" />
                </div>
              </div>
            </div>

            <div className="bg-white rounded-lg p-6 shadow-sm border border-gray-200">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">학습한 과목</p>
                  <p className="text-2xl font-bold text-gray-900">
                    {daily.subjects_studied?.length || 0}개
                  </p>
                </div>
                <div className="p-2 bg-orange-100 rounded-lg">
                  <BarChart3 className="w-6 h-6 text-orange-600" />
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* 실제 분석 데이터가 있는 경우 */}
      {hasAnalyticsData && (
        <>
          {/* 주요 성과 지표 */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            <div className="bg-white rounded-lg p-6 shadow-sm border border-gray-200">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">전체 진도율</p>
                  <p className="text-2xl font-bold text-gray-900">
                    {Math.round(analytics.overall_progress || 0)}%
                  </p>
                </div>
                <div className="p-2 bg-blue-100 rounded-lg">
                  <TrendingUp className="w-6 h-6 text-blue-600" />
                </div>
              </div>
            </div>

            <div className="bg-white rounded-lg p-6 shadow-sm border border-gray-200">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">활성 과목</p>
                  <p className="text-2xl font-bold text-gray-900">
                    {analytics.active_subjects?.length || 0}
                  </p>
                </div>
                <div className="p-2 bg-green-100 rounded-lg">
                  <Target className="w-6 h-6 text-green-600" />
                </div>
              </div>
            </div>

            <div className="bg-white rounded-lg p-6 shadow-sm border border-gray-200">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">평균 점수</p>
                  <p className="text-2xl font-bold text-gray-900">
                    {Math.round(analytics.average_score || 0)}점
                  </p>
                </div>
                <div className="p-2 bg-purple-100 rounded-lg">
                  <BarChart3 className="w-6 h-6 text-purple-600" />
                </div>
              </div>
            </div>

            <div className="bg-white rounded-lg p-6 shadow-sm border border-gray-200">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">학습 시간</p>
                  <p className="text-2xl font-bold text-gray-900">
                    {Math.round(analytics.total_study_hours || 0)}h
                  </p>
                </div>
                <div className="p-2 bg-orange-100 rounded-lg">
                  <Clock className="w-6 h-6 text-orange-600" />
                </div>
              </div>
            </div>
          </div>

          {/* 상세 분석 */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* 과목별 성과 */}
            <div className="bg-white rounded-lg p-6 shadow-sm border border-gray-200">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">
                📚 과목별 성과
              </h2>
              {analytics.subjects_performance && analytics.subjects_performance.length > 0 ? (
                <div className="space-y-4">
                  {analytics.subjects_performance.map((subject: any, index: number) => (
                    <div key={index} className="border-b border-gray-100 pb-3 last:border-0">
                      <div className="flex justify-between items-center mb-2">
                        <span className="font-medium text-gray-900">
                          {subject.subject_name || subject.key}
                        </span>
                        <span className="text-sm text-gray-600">
                          {Math.round(subject.progress || 0)}%
                        </span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div 
                          className="bg-blue-600 h-2 rounded-full transition-all duration-300" 
                          style={{ width: `${subject.progress || 0}%` }}
                        />
                      </div>
                      <div className="flex justify-between text-xs text-gray-500 mt-1">
                        <span>점수: {Math.round(subject.average_score || 0)}점</span>
                        <span>문제: {subject.problems_solved || 0}개</span>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8">
                  <BarChart3 className="w-12 h-12 text-gray-300 mx-auto mb-3" />
                  <p className="text-gray-500">과목별 성과 데이터가 없습니다.</p>
                </div>
              )}
            </div>

            {/* 최근 활동 */}
            <div className="bg-white rounded-lg p-6 shadow-sm border border-gray-200">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">
                📈 최근 학습 활동
              </h2>
              {progress.recent_activities && progress.recent_activities.length > 0 ? (
                <div className="space-y-3">
                  {progress.recent_activities.slice(0, 5).map((activity: any, index: number) => (
                    <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                      <div>
                        <p className="font-medium text-gray-900">
                          {activity.activity_type || '학습 활동'}
                        </p>
                        <p className="text-sm text-gray-600">
                          {activity.subject || activity.topic || '일반'}
                        </p>
                      </div>
                      <div className="text-right">
                        <div className={`font-medium ${
                          activity.score >= 80 ? 'text-green-600' :
                          activity.score >= 60 ? 'text-yellow-600' : 'text-red-600'
                        }`}>
                          {activity.score ? `${activity.score}점` : '완료'}
                        </div>
                        <p className="text-sm text-gray-500">
                          {activity.timestamp ? 
                            new Date(activity.timestamp).toLocaleDateString('ko-KR') : 
                            '최근'
                          }
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8">
                  <Target className="w-12 h-12 text-gray-300 mx-auto mb-3" />
                  <p className="text-gray-500">최근 학습 활동이 없습니다.</p>
                  <p className="text-sm text-gray-400 mt-1">문제를 풀어보시면 여기에 기록됩니다!</p>
                </div>
              )}
            </div>
          </div>
        </>
      )}

      {/* 실제 데이터 연결 상태 */}
      <div className="mt-8 bg-green-50 border border-green-200 rounded-lg p-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center">
            <div className="w-2 h-2 bg-green-500 rounded-full mr-3"></div>
            <span className="text-green-800 font-medium">실제 통합 학습 분석 시스템 연결됨</span>
            <span className="text-green-600 ml-2">
              - Mock 데이터 완전 제거 ({user?.id})
            </span>
          </div>
          <button 
            onClick={() => refetch()}
            className="text-green-600 hover:text-green-700 p-1"
          >
            <RefreshCw className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  );
}