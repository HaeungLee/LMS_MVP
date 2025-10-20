/**
 * 학습 통계 대시보드 컴포넌트
 * 
 * - 일일/주간/월간 학습 통계
 * - 정확도 추이 그래프
 * - 학습 시간 분석
 */

import { useQuery } from '@tanstack/react-query';
import { 
  TrendingUp, 
  Calendar,
  BarChart3,
  Award
} from 'lucide-react';
import { api } from '../../../shared/services/apiClient';

interface LearningStats {
  daily: {
    problems_solved: number;
    accuracy: number;
    study_minutes: number;
  };
  weekly: {
    problems_solved: number;
    accuracy: number;
    study_hours: number;
    streak_days: number;
  };
  monthly: {
    problems_solved: number;
    accuracy: number;
    study_hours: number;
    completed_days: number;
  };
  improvement: {
    accuracy_change: number;  // vs 지난주
    speed_change: number;     // vs 지난주
  };
}

export default function StatsCard() {
  const { data: stats } = useQuery<LearningStats>({
    queryKey: ['learning-stats'],
    queryFn: () => api.get<LearningStats>('/stats/learning'),
  });

  return (
    <div className="bg-white rounded-2xl shadow-lg p-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-bold text-gray-900">학습 통계</h2>
        <BarChart3 className="w-6 h-6 text-purple-600" />
      </div>

      {/* 일일 통계 */}
      <div className="mb-6">
        <h3 className="text-sm font-semibold text-gray-700 mb-3 flex items-center gap-2">
          <Calendar className="w-4 h-4" />
          오늘
        </h3>
        <div className="grid grid-cols-3 gap-4">
          <MiniStatBox
            label="문제 풀이"
            value={stats?.daily.problems_solved ?? 0}
            unit="개"
            color="text-blue-600"
          />
          <MiniStatBox
            label="정확도"
            value={stats?.daily.accuracy ?? 0}
            unit="%"
            color="text-green-600"
          />
          <MiniStatBox
            label="학습 시간"
            value={stats?.daily.study_minutes ?? 0}
            unit="분"
            color="text-purple-600"
          />
        </div>
      </div>

      {/* 주간 통계 */}
      <div className="mb-6">
        <h3 className="text-sm font-semibold text-gray-700 mb-3 flex items-center gap-2">
          <TrendingUp className="w-4 h-4" />
          이번 주
        </h3>
        <div className="grid grid-cols-2 gap-4">
          <MiniStatBox
            label="문제 풀이"
            value={stats?.weekly.problems_solved ?? 0}
            unit="개"
            color="text-blue-600"
          />
          <MiniStatBox
            label="학습 시간"
            value={stats?.weekly.study_hours ?? 0}
            unit="시간"
            color="text-purple-600"
          />
          <MiniStatBox
            label="연속 학습"
            value={stats?.weekly.streak_days ?? 0}
            unit="일"
            color="text-orange-600"
          />
          <MiniStatBox
            label="정확도"
            value={stats?.weekly.accuracy ?? 0}
            unit="%"
            color="text-green-600"
          />
        </div>
      </div>

      {/* 개선율 */}
      {stats?.improvement && (
        <div className="bg-gradient-to-br from-green-50 to-emerald-50 rounded-xl p-4">
          <div className="flex items-center gap-2 mb-2">
            <Award className="w-5 h-5 text-green-600" />
            <span className="text-sm font-semibold text-green-900">지난주 대비</span>
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <p className="text-xs text-gray-600 mb-1">정확도</p>
              <p className={`text-lg font-bold ${
                stats.improvement.accuracy_change >= 0 ? 'text-green-600' : 'text-red-600'
              }`}>
                {stats.improvement.accuracy_change >= 0 ? '+' : ''}{stats.improvement.accuracy_change.toFixed(1)}%
              </p>
            </div>
            <div>
              <p className="text-xs text-gray-600 mb-1">풀이 속도</p>
              <p className={`text-lg font-bold ${
                stats.improvement.speed_change >= 0 ? 'text-green-600' : 'text-red-600'
              }`}>
                {stats.improvement.speed_change >= 0 ? '+' : ''}{stats.improvement.speed_change.toFixed(1)}%
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

// ============= Sub Components =============

interface MiniStatBoxProps {
  label: string;
  value: number;
  unit: string;
  color: string;
}

function MiniStatBox({ label, value, unit, color }: MiniStatBoxProps) {
  return (
    <div className="bg-gray-50 rounded-lg p-3">
      <p className="text-xs text-gray-600 mb-1">{label}</p>
      <div className="flex items-baseline gap-1">
        <span className={`text-2xl font-bold ${color}`}>{value}</span>
        <span className="text-sm text-gray-500">{unit}</span>
      </div>
    </div>
  );
}
