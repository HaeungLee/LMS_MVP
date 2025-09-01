import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';

const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000') + '/api/v1';

import { 
  Users, 
  Activity, 
  MessageSquare, 
  TrendingUp,
  RefreshCw,
  Calendar,
  BarChart3,
  AlertTriangle,
  CheckCircle,
  Clock,
  Brain,
  Target,
  Code,
  MessageCircle,
  Star
} from 'lucide-react';

const BetaDashboard = () => {
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [lastUpdated, setLastUpdated] = useState(null);

  const fetchDashboardData = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/beta/dashboard`);
      const data = await response.json();
      
      if (data.success) {
        setDashboardData(data);
        setLastUpdated(new Date());
      }
    } catch (error) {
      console.error('대시보드 데이터 조회 실패:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();
    
    // 5분마다 자동 새로고침
    const interval = setInterval(fetchDashboardData, 5 * 60 * 1000);
    
    return () => clearInterval(interval);
  }, []);

  if (loading && !dashboardData) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="flex items-center justify-center h-64">
          <div className="text-center">
            <RefreshCw className="w-8 h-8 animate-spin mx-auto mb-4" />
            <p>베타 테스트 데이터를 불러오고 있습니다...</p>
          </div>
        </div>
      </div>
    );
  }

  if (!dashboardData) {
    return (
      <div className="container mx-auto px-4 py-8">
        <Card className="border-red-200">
          <CardContent className="pt-6">
            <div className="text-center">
              <AlertTriangle className="w-12 h-12 mx-auto mb-4 text-red-500" />
              <h3 className="text-lg font-semibold mb-2">데이터 로드 실패</h3>
              <p className="text-gray-600 mb-4">베타 테스트 데이터를 불러올 수 없습니다.</p>
              <Button onClick={fetchDashboardData}>다시 시도</Button>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  const { overview, daily_activity, feedback_by_type, feature_usage } = dashboardData;

  return (
    <div className="container mx-auto px-4 py-8 max-w-7xl">
      {/* 헤더 */}
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-bold">베타 테스트 대시보드</h1>
          <p className="text-gray-600">실시간 베타 테스터 활동 및 피드백 현황</p>
        </div>
        <div className="flex items-center space-x-4">
          {lastUpdated && (
            <div className="text-sm text-gray-500">
              <Clock className="w-4 h-4 inline mr-1" />
              마지막 업데이트: {lastUpdated.toLocaleTimeString()}
            </div>
          )}
          <Button 
            onClick={fetchDashboardData} 
            variant="outline" 
            size="sm"
            disabled={loading}
          >
            <RefreshCw className={`w-4 h-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
            새로고침
          </Button>
        </div>
      </div>

      {/* 개요 통계 */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center">
              <Users className="w-8 h-8 text-blue-500" />
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">전체 베타 테스터</p>
                <p className="text-2xl font-bold">{overview.total_beta_testers}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center">
              <Activity className="w-8 h-8 text-green-500" />
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">활성 사용자 (7일)</p>
                <p className="text-2xl font-bold">{overview.active_testers_7d}</p>
                <p className="text-xs text-gray-500">
                  {((overview.active_testers_7d / overview.total_beta_testers) * 100).toFixed(1)}% 활성률
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center">
              <BarChart3 className="w-8 h-8 text-purple-500" />
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">총 세션 수</p>
                <p className="text-2xl font-bold">{overview.total_sessions}</p>
                <p className="text-xs text-gray-500">
                  사용자당 평균 {overview.avg_sessions_per_user}회
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center">
              <MessageSquare className="w-8 h-8 text-orange-500" />
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">총 피드백</p>
                <p className="text-2xl font-bold">{overview.total_feedback}</p>
                <p className="text-xs text-gray-500">
                  사용자당 평균 {(overview.total_feedback / overview.total_beta_testers).toFixed(1)}개
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* 일별 활동 현황 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <Calendar className="w-5 h-5 mr-2" />
              일별 활동 현황 (최근 7일)
            </CardTitle>
            <CardDescription>베타 테스터들의 일일 활동 수</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {Object.entries(daily_activity)
                .sort(([a], [b]) => new Date(b) - new Date(a))
                .map(([date, count]) => {
                  const maxCount = Math.max(...Object.values(daily_activity));
                  const percentage = maxCount > 0 ? (count / maxCount) * 100 : 0;
                  
                  return (
                    <div key={date} className="flex items-center justify-between">
                      <span className="text-sm font-medium w-24">
                        {new Date(date).toLocaleDateString('ko-KR', { 
                          month: 'short', 
                          day: 'numeric' 
                        })}
                      </span>
                      <div className="flex-1 mx-3">
                        <Progress value={percentage} className="h-2" />
                      </div>
                      <span className="text-sm text-gray-600 w-12 text-right">
                        {count}
                      </span>
                    </div>
                  );
                })}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <MessageSquare className="w-5 h-5 mr-2" />
              피드백 유형별 분포
            </CardTitle>
            <CardDescription>수집된 피드백의 카테고리별 현황</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {Object.entries(feedback_by_type).map(([type, count]) => {
                const total = Object.values(feedback_by_type).reduce((sum, c) => sum + c, 0);
                const percentage = total > 0 ? (count / total) * 100 : 0;
                
                const typeLabels = {
                  'bug': '버그 신고',
                  'feature_request': '기능 요청',
                  'general': '일반 피드백',
                  'improvement': '개선 제안'
                };
                
                const typeColors = {
                  'bug': 'bg-red-500',
                  'feature_request': 'bg-blue-500',
                  'general': 'bg-green-500',
                  'improvement': 'bg-purple-500'
                };
                
                return (
                  <div key={type} className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      <div className={`w-3 h-3 rounded-full ${typeColors[type] || 'bg-gray-500'}`} />
                      <span className="text-sm font-medium">
                        {typeLabels[type] || type}
                      </span>
                    </div>
                    <div className="flex items-center space-x-2">
                      <span className="text-sm text-gray-600">
                        {percentage.toFixed(1)}%
                      </span>
                      <Badge variant="secondary">{count}</Badge>
                    </div>
                  </div>
                );
              })}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* AI 기능 사용 현황 */}
      <Card className="mb-8">
        <CardHeader>
          <CardTitle className="flex items-center">
            <Brain className="w-5 h-5 mr-2" />
            AI 기능 사용 현황 (최근 7일)
          </CardTitle>
          <CardDescription>베타 테스터들이 가장 많이 사용한 AI 기능들</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {Object.entries(feature_usage).length > 0 ? (
              Object.entries(feature_usage)
                .sort(([,a], [,b]) => b - a)
                .map(([feature, count]) => {
                  const featureInfo = {
                    'deep_learning_analysis': { 
                      label: '심층 학습 분석', 
                      icon: Brain, 
                      color: 'blue' 
                    },
                    'ai_mentoring': { 
                      label: 'AI 멘토링', 
                      icon: MessageCircle, 
                      color: 'green' 
                    },
                    'adaptive_difficulty': { 
                      label: '적응형 난이도', 
                      icon: Target, 
                      color: 'purple' 
                    },
                    'code_review': { 
                      label: 'AI 코드 리뷰', 
                      icon: Code, 
                      color: 'orange' 
                    }
                  };
                  
                  const info = featureInfo[feature] || { 
                    label: feature, 
                    icon: Star, 
                    color: 'gray' 
                  };
                  const Icon = info.icon;
                  
                  return (
                    <Card key={feature} className="text-center">
                      <CardContent className="pt-6">
                        <Icon className={`w-8 h-8 mx-auto mb-2 text-${info.color}-500`} />
                        <p className="font-medium text-sm">{info.label}</p>
                        <p className="text-2xl font-bold">{count}</p>
                        <p className="text-xs text-gray-500">회 사용</p>
                      </CardContent>
                    </Card>
                  );
                })
            ) : (
              <div className="col-span-full text-center py-8 text-gray-500">
                아직 AI 기능 사용 데이터가 없습니다.
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* 시스템 상태 */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <CheckCircle className="w-5 h-5 mr-2 text-green-500" />
            시스템 상태
          </CardTitle>
          <CardDescription>베타 테스트 환경의 현재 상태</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="text-center p-4 bg-green-50 rounded-lg">
              <CheckCircle className="w-8 h-8 mx-auto mb-2 text-green-500" />
              <p className="font-medium">API 서버</p>
              <p className="text-sm text-green-600">정상 동작</p>
            </div>
            
            <div className="text-center p-4 bg-green-50 rounded-lg">
              <CheckCircle className="w-8 h-8 mx-auto mb-2 text-green-500" />
              <p className="font-medium">AI 기능</p>
              <p className="text-sm text-green-600">정상 동작</p>
            </div>
            
            <div className="text-center p-4 bg-blue-50 rounded-lg">
              <Activity className="w-8 h-8 mx-auto mb-2 text-blue-500" />
              <p className="font-medium">데이터 수집</p>
              <p className="text-sm text-blue-600">활성</p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* 베타 테스트 진행률 */}
      <Card className="mt-6">
        <CardHeader>
          <CardTitle>베타 테스트 진행률</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div>
              <div className="flex justify-between items-center mb-2">
                <span className="text-sm font-medium">전체 진행률</span>
                <span className="text-sm text-gray-600">
                  {overview.total_beta_testers}/30 테스터 참여
                </span>
              </div>
              <Progress value={(overview.total_beta_testers / 20) * 100} className="h-3" />
            </div>
            
            <div>
              <div className="flex justify-between items-center mb-2">
                <span className="text-sm font-medium">활성 참여율</span>
                <span className="text-sm text-gray-600">
                  {((overview.active_testers_7d / overview.total_beta_testers) * 100).toFixed(1)}%
                </span>
              </div>
              <Progress 
                value={(overview.active_testers_7d / overview.total_beta_testers) * 100} 
                className="h-3" 
              />
            </div>
            
            <div>
              <div className="flex justify-between items-center mb-2">
                <span className="text-sm font-medium">피드백 수집률</span>
                <span className="text-sm text-gray-600">
                  {overview.total_feedback > 0 ? 
                    `${((overview.total_feedback / overview.total_beta_testers) * 100).toFixed(1)}% 평균 참여` :
                    '피드백 대기 중'
                  }
                </span>
              </div>
              <Progress 
                value={Math.min(100, (overview.total_feedback / overview.total_beta_testers) * 25)} 
                className="h-3" 
              />
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default BetaDashboard;
