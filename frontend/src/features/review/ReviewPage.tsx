/**
 * 복습 시스템 페이지
 * 
 * - 약점 분석 대시보드
 * - 복습 추천 문제 목록
 * - 망각 곡선 기반 우선순위
 */

import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useQuery, useMutation } from '@tanstack/react-query';
import { 
  Brain, 
  Target, 
  AlertTriangle, 
  TrendingUp,
  ArrowRight,
  RefreshCw,
  Flame,
  Award,
  BarChart3
} from 'lucide-react';
import { api } from '../../shared/services/apiClient';

interface ReviewStats {
  total_weak_concepts: number;
  critical_reviews: number;
  high_priority_reviews: number;
  total_incorrect_problems: number;
  average_accuracy: number;
  improvement_rate: number;
}

interface WeaknessAnalysis {
  topic: string;
  concept: string;
  incorrect_count: number;
  total_attempts: number;
  accuracy: number;
  last_attempt: string;
  priority_score: number;
}

interface ReviewRecommendation {
  problem_id: number;
  problem_title: string;
  topic: string;
  concept: string;
  difficulty: string;
  incorrect_count: number;
  days_since_last: number;
  forgetting_risk: number;
  review_urgency: 'critical' | 'high' | 'medium' | 'low';
  recommended_review_date: string;
}

interface ReviewSession {
  session_id: string;
  problems: ReviewRecommendation[];
  total_count: number;
  estimated_time_minutes: number;
  focus_message: string;
}

export default function ReviewPage() {
  const navigate = useNavigate();
  const [selectedUrgency, setSelectedUrgency] = useState<string>('all');

  // 복습 통계
  const { data: stats, isLoading: statsLoading } = useQuery<ReviewStats>({
    queryKey: ['review-stats'],
    queryFn: () => api.get<ReviewStats>('/review/stats'),
  });

  // 약점 분석
  const { data: weaknesses, isLoading: weaknessLoading } = useQuery<WeaknessAnalysis[]>({
    queryKey: ['weaknesses'],
    queryFn: () => api.get<WeaknessAnalysis[]>('/review/weaknesses?limit=20'),
  });

  // 복습 세션 시작
  const startSession = useMutation({
    mutationFn: (maxProblems: number) => 
      api.post<ReviewSession>('/review/session/start', { max_problems: maxProblems }),
    onSuccess: (data) => {
      // 복습 세션 페이지로 이동
      navigate(`/review/session/${data.session_id}`, { state: { session: data } });
    },
  });

  if (statsLoading || weaknessLoading) {
    return (
      <div className="max-w-7xl mx-auto">
        <div className="flex items-center justify-center h-64">
          <div className="text-center">
            <RefreshCw className="w-8 h-8 animate-spin mx-auto mb-4 text-indigo-600" />
            <p className="text-gray-600">복습 데이터를 불러오는 중...</p>
          </div>
        </div>
      </div>
    );
  }

  // 긴급도별 필터링
  const filteredWeaknesses = selectedUrgency === 'all' 
    ? weaknesses 
    : weaknesses?.filter(w => {
        if (selectedUrgency === 'critical') return w.priority_score >= 80;
        if (selectedUrgency === 'high') return w.priority_score >= 60 && w.priority_score < 80;
        if (selectedUrgency === 'medium') return w.priority_score >= 40 && w.priority_score < 60;
        return w.priority_score < 40;
      });

  return (
    <div className="max-w-7xl mx-auto space-y-8">
      {/* 헤더 */}
      <div className="bg-gradient-to-r from-purple-600 to-pink-600 rounded-3xl p-8 text-white">
        <div className="flex items-center gap-3 mb-4">
          <Brain className="w-10 h-10" />
          <h1 className="text-3xl font-bold">복습 시스템</h1>
        </div>
        <p className="text-purple-100 text-lg">
          망각 곡선 기반 맞춤 복습으로 학습 효과를 극대화하세요
        </p>
      </div>

      {/* 통계 카드 */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {/* 약점 개념 */}
        <StatCard
          icon={<Target className="w-6 h-6" />}
          title="약점 개념"
          value={stats?.total_weak_concepts ?? 0}
          unit="개"
          color="from-orange-500 to-red-500"
        />

        {/* 긴급 복습 */}
        <StatCard
          icon={<AlertTriangle className="w-6 h-6" />}
          title="긴급 복습"
          value={stats?.critical_reviews ?? 0}
          unit="개"
          color="from-red-500 to-pink-500"
          badge={stats && stats.critical_reviews > 0 ? "⚠️" : undefined}
        />

        {/* 평균 정확도 */}
        <StatCard
          icon={<BarChart3 className="w-6 h-6" />}
          title="평균 정확도"
          value={stats?.average_accuracy ?? 0}
          unit="%"
          color="from-blue-500 to-cyan-500"
        />

        {/* 개선율 */}
        <StatCard
          icon={<TrendingUp className="w-6 h-6" />}
          title="주간 개선율"
          value={stats?.improvement_rate ?? 0}
          unit="%"
          color="from-green-500 to-emerald-500"
          isImprovement={true}
        />
      </div>

      {/* 빠른 시작 버튼 */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <QuickStartCard
          title="긴급 복습"
          description="망각 위험 높은 문제부터"
          icon={<Flame className="w-8 h-8" />}
          gradient="from-red-500 to-orange-500"
          problemCount={stats?.critical_reviews ?? 0}
          onClick={() => startSession.mutate(stats?.critical_reviews ?? 5)}
        />
        
        <QuickStartCard
          title="일반 복습"
          description="우선순위 높은 10문제"
          icon={<Target className="w-8 h-8" />}
          gradient="from-purple-500 to-pink-500"
          problemCount={10}
          onClick={() => startSession.mutate(10)}
        />
        
        <QuickStartCard
          title="약점 집중"
          description="틀린 문제 전체 복습"
          icon={<Brain className="w-8 h-8" />}
          gradient="from-indigo-500 to-purple-500"
          problemCount={stats?.total_incorrect_problems ?? 0}
          onClick={() => startSession.mutate(stats?.total_incorrect_problems ?? 20)}
        />
      </div>

      {/* 약점 분석 */}
      <div className="bg-white rounded-2xl shadow-lg p-6">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-2xl font-bold text-gray-900">약점 분석</h2>
          
          {/* 긴급도 필터 */}
          <div className="flex gap-2">
            {[
              { key: 'all', label: '전체' },
              { key: 'critical', label: '긴급' },
              { key: 'high', label: '높음' },
              { key: 'medium', label: '보통' },
              { key: 'low', label: '낮음' },
            ].map((filter) => (
              <button
                key={filter.key}
                onClick={() => setSelectedUrgency(filter.key)}
                className={`px-4 py-2 rounded-lg font-medium transition-all ${
                  selectedUrgency === filter.key
                    ? 'bg-purple-600 text-white shadow-lg'
                    : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                }`}
              >
                {filter.label}
              </button>
            ))}
          </div>
        </div>

        {/* 약점 목록 */}
        {filteredWeaknesses && filteredWeaknesses.length > 0 ? (
          <div className="space-y-4">
            {filteredWeaknesses.map((weakness, idx) => (
              <WeaknessCard key={idx} weakness={weakness} />
            ))}
          </div>
        ) : (
          <div className="text-center py-12">
            <Award className="w-16 h-16 mx-auto mb-4 text-gray-400" />
            <p className="text-gray-600 text-lg">약점이 발견되지 않았습니다!</p>
            <p className="text-gray-500 text-sm mt-2">계속 열심히 하세요! 🎉</p>
          </div>
        )}
      </div>
    </div>
  );
}


// ============= Sub Components =============

interface StatCardProps {
  icon: React.ReactNode;
  title: string;
  value: number;
  unit: string;
  color: string;
  badge?: string;
  isImprovement?: boolean;
}

function StatCard({ icon, title, value, unit, color, badge, isImprovement }: StatCardProps) {
  const displayValue = isImprovement && value > 0 ? `+${value}` : value;
  
  return (
    <div className="bg-white rounded-xl shadow-lg p-6 relative overflow-hidden">
      {/* 배경 그라디언트 */}
      <div className={`absolute top-0 right-0 w-32 h-32 bg-gradient-to-br ${color} opacity-10 rounded-full -mr-16 -mt-16`} />
      
      <div className="relative">
        <div className="flex items-center justify-between mb-4">
          <div className={`p-3 rounded-xl bg-gradient-to-br ${color} text-white`}>
            {icon}
          </div>
          {badge && <span className="text-2xl">{badge}</span>}
        </div>
        
        <p className="text-gray-600 text-sm mb-1">{title}</p>
        <div className="flex items-baseline gap-1">
          <span className={`text-3xl font-bold bg-gradient-to-r ${color} bg-clip-text text-transparent`}>
            {displayValue}
          </span>
          <span className="text-gray-500 text-lg">{unit}</span>
        </div>
      </div>
    </div>
  );
}


interface QuickStartCardProps {
  title: string;
  description: string;
  icon: React.ReactNode;
  gradient: string;
  problemCount: number;
  onClick: () => void;
}

function QuickStartCard({ title, description, icon, gradient, problemCount, onClick }: QuickStartCardProps) {
  return (
    <button
      onClick={onClick}
      disabled={problemCount === 0}
      className={`
        bg-white rounded-xl shadow-lg p-6 text-left transition-all duration-200
        ${problemCount > 0 
          ? 'hover:shadow-xl transform hover:-translate-y-1 cursor-pointer' 
          : 'opacity-50 cursor-not-allowed'
        }
      `}
    >
      <div className={`inline-flex p-3 rounded-xl bg-gradient-to-br ${gradient} text-white mb-4`}>
        {icon}
      </div>
      
      <h3 className="text-lg font-bold text-gray-900 mb-2">{title}</h3>
      <p className="text-gray-600 text-sm mb-4">{description}</p>
      
      <div className="flex items-center justify-between">
        <span className="text-2xl font-bold text-gray-900">{problemCount}</span>
        <span className="text-sm text-gray-500">문제</span>
      </div>
      
      {problemCount > 0 && (
        <div className="mt-4 flex items-center gap-2 text-sm font-medium text-purple-600">
          시작하기
          <ArrowRight className="w-4 h-4" />
        </div>
      )}
    </button>
  );
}


interface WeaknessCardProps {
  weakness: WeaknessAnalysis;
}

function WeaknessCard({ weakness }: WeaknessCardProps) {
  const getUrgencyColor = (score: number) => {
    if (score >= 80) return 'bg-red-100 text-red-700';
    if (score >= 60) return 'bg-orange-100 text-orange-700';
    if (score >= 40) return 'bg-yellow-100 text-yellow-700';
    return 'bg-green-100 text-green-700';
  };

  const getUrgencyLabel = (score: number) => {
    if (score >= 80) return '긴급';
    if (score >= 60) return '높음';
    if (score >= 40) return '보통';
    return '낮음';
  };

  const daysSince = Math.floor(
    (new Date().getTime() - new Date(weakness.last_attempt).getTime()) / (1000 * 60 * 60 * 24)
  );

  return (
    <div className="border border-gray-200 rounded-xl p-6 hover:shadow-md transition-shadow">
      <div className="flex items-start justify-between mb-4">
        <div>
          <h3 className="text-lg font-bold text-gray-900 mb-1">{weakness.concept}</h3>
          <p className="text-sm text-gray-600">{weakness.topic}</p>
        </div>
        
        <span className={`px-3 py-1 rounded-full text-sm font-semibold ${getUrgencyColor(weakness.priority_score)}`}>
          {getUrgencyLabel(weakness.priority_score)}
        </span>
      </div>

      <div className="grid grid-cols-4 gap-4 mb-4">
        <div>
          <p className="text-xs text-gray-500 mb-1">틀린 횟수</p>
          <p className="text-lg font-bold text-red-600">{weakness.incorrect_count}</p>
        </div>
        
        <div>
          <p className="text-xs text-gray-500 mb-1">총 시도</p>
          <p className="text-lg font-bold text-gray-900">{weakness.total_attempts}</p>
        </div>
        
        <div>
          <p className="text-xs text-gray-500 mb-1">정확도</p>
          <p className="text-lg font-bold text-blue-600">{weakness.accuracy}%</p>
        </div>
        
        <div>
          <p className="text-xs text-gray-500 mb-1">경과일</p>
          <p className="text-lg font-bold text-purple-600">{daysSince}일</p>
        </div>
      </div>

      {/* 우선순위 바 */}
      <div className="mb-3">
        <div className="flex items-center justify-between text-xs text-gray-600 mb-1">
          <span>복습 우선순위</span>
          <span className="font-bold">{weakness.priority_score.toFixed(0)}점</span>
        </div>
        <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
          <div 
            className={`h-full transition-all duration-500 ${
              weakness.priority_score >= 80 ? 'bg-red-500' :
              weakness.priority_score >= 60 ? 'bg-orange-500' :
              weakness.priority_score >= 40 ? 'bg-yellow-500' :
              'bg-green-500'
            }`}
            style={{ width: `${weakness.priority_score}%` }}
          />
        </div>
      </div>

      <button className="w-full py-2 bg-purple-50 hover:bg-purple-100 text-purple-700 font-medium rounded-lg transition-colors">
        이 개념 복습하기
      </button>
    </div>
  );
}
