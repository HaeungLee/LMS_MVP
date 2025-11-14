/**
 * 자기 대비 대시보드
 * 
 * 과거의 나와 비교하여 성장을 추적
 */
import { useState, useEffect } from 'react';
import { TrendingUp, TrendingDown, Minus, Flame, Battery, Brain } from 'lucide-react';
import apiClient from '../../shared/services/apiClient';

interface SelfComparisonData {
  comparison_period_days: number;
  learning_sessions: {
    current: number;
    past: number;
    change: number;
    change_percentage: number;
  };
  confidence_level: {
    current: number;
    past: number;
    change: number;
  };
  average_study_time: {
    current_minutes: number;
    past_minutes: number;
    change_minutes: number;
  };
  current_streak_days: number;
  insights: string[];
}

interface SelfComparisonDashboardProps {
  compareDays?: number;
}

export function SelfComparisonDashboard({ compareDays = 30 }: SelfComparisonDashboardProps) {
  const [data, setData] = useState<SelfComparisonData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchDashboardData();
  }, [compareDays]);

  const fetchDashboardData = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await apiClient.get('/api/v1/emotional/dashboard/self-comparison', {
        params: { compare_days: compareDays }
      });
      setData(response.data);
    } catch (err) {
      console.error('자기 대비 대시보드 로드 실패:', err);
      setError('데이터를 불러오는데 실패했습니다.');
    } finally {
      setLoading(false);
    }
  };

  const renderChangeIndicator = (change: number, isPercentage = false) => {
    const suffix = isPercentage ? '%' : '';
    
    if (change > 0) {
      return (
        <div className="flex items-center text-green-600">
          <TrendingUp className="w-4 h-4 mr-1" />
          <span className="text-sm font-semibold">+{change.toFixed(1)}{suffix}</span>
        </div>
      );
    } else if (change < 0) {
      return (
        <div className="flex items-center text-red-600">
          <TrendingDown className="w-4 h-4 mr-1" />
          <span className="text-sm font-semibold">{change.toFixed(1)}{suffix}</span>
        </div>
      );
    } else {
      return (
        <div className="flex items-center text-gray-500">
          <Minus className="w-4 h-4 mr-1" />
          <span className="text-sm font-semibold">0{suffix}</span>
        </div>
      );
    }
  };

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="animate-pulse space-y-4">
          <div className="h-6 bg-gray-200 rounded w-1/3"></div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {[1, 2, 3].map(i => (
              <div key={i} className="h-32 bg-gray-200 rounded"></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6">
        <p className="text-red-600">{error || '데이터를 불러올 수 없습니다.'}</p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-md p-6 space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold text-gray-800">
          자기 대비 성장 추적 💪
        </h2>
        <div className="text-sm text-gray-500">
          최근 {data.comparison_period_days}일 vs 이전 {data.comparison_period_days}일
        </div>
      </div>

      {/* 연속 학습 일수 - 강조 */}
      {data.current_streak_days > 0 && (
        <div className="bg-gradient-to-r from-orange-50 to-red-50 border-2 border-orange-200 rounded-lg p-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <Flame className="w-8 h-8 text-orange-500" />
              <div>
                <p className="text-sm text-gray-600">연속 학습 일수</p>
                <p className="text-3xl font-bold text-orange-600">
                  {data.current_streak_days}일
                </p>
              </div>
            </div>
            <div className="text-4xl">🔥</div>
          </div>
        </div>
      )}

      {/* 통계 카드들 */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* 학습 세션 수 */}
        <div className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition">
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-sm font-semibold text-gray-600">학습 세션</h3>
            <Brain className="w-5 h-5 text-blue-500" />
          </div>
          <div className="space-y-2">
            <div className="flex items-baseline justify-between">
              <span className="text-2xl font-bold text-gray-800">
                {data.learning_sessions.current}회
              </span>
              {renderChangeIndicator(data.learning_sessions.change)}
            </div>
            <p className="text-xs text-gray-500">
              이전: {data.learning_sessions.past}회
            </p>
            {data.learning_sessions.change_percentage !== 0 && (
              <p className="text-xs font-medium text-blue-600">
                {data.learning_sessions.change_percentage > 0 ? '+' : ''}
                {data.learning_sessions.change_percentage.toFixed(1)}% 변화
              </p>
            )}
          </div>
        </div>

        {/* 자신감 레벨 */}
        <div className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition">
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-sm font-semibold text-gray-600">평균 자신감</h3>
            <span className="text-2xl">💪</span>
          </div>
          <div className="space-y-2">
            <div className="flex items-baseline justify-between">
              <span className="text-2xl font-bold text-gray-800">
                {data.confidence_level.current}/10
              </span>
              {renderChangeIndicator(data.confidence_level.change)}
            </div>
            <p className="text-xs text-gray-500">
              이전: {data.confidence_level.past}/10
            </p>
          </div>
        </div>

        {/* 평균 학습 시간 */}
        <div className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition">
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-sm font-semibold text-gray-600">평균 학습 시간</h3>
            <Battery className="w-5 h-5 text-green-500" />
          </div>
          <div className="space-y-2">
            <div className="flex items-baseline justify-between">
              <span className="text-2xl font-bold text-gray-800">
                {data.average_study_time.current_minutes.toFixed(0)}분
              </span>
              {renderChangeIndicator(data.average_study_time.change_minutes)}
            </div>
            <p className="text-xs text-gray-500">
              이전: {data.average_study_time.past_minutes.toFixed(0)}분
            </p>
          </div>
        </div>
      </div>

      {/* 인사이트 */}
      {data.insights && data.insights.length > 0 && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <h3 className="text-sm font-semibold text-gray-700 mb-3">💡 성장 인사이트</h3>
          <ul className="space-y-2">
            {data.insights.map((insight, index) => (
              <li key={index} className="text-sm text-gray-700 flex items-start">
                <span className="mr-2">•</span>
                <span>{insight}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* 격려 메시지 */}
      <div className="bg-gradient-to-r from-purple-50 to-pink-50 border border-purple-200 rounded-lg p-4 text-center">
        <p className="text-sm text-gray-700">
          💙 <strong>당신은 어제보다 나아지고 있습니다!</strong> 💛
        </p>
        <p className="text-xs text-gray-600 mt-1">
          비교는 과거의 나와만. 지금 이 순간, 당신의 노력이 가장 중요합니다.
        </p>
      </div>
    </div>
  );
}

