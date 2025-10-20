/**
 * MVP 대시보드 - 오늘의 학습 중심
 * 
 * 기존: 통계 중심 (문제 수, 정확도, 진도)
 * 새로운: 학습 행동 유도 (교과서 → 실습 → 퀴즈)
 */

import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { 
  BookOpen, 
  Code, 
  CheckCircle, 
  Clock, 
  Target,
  Calendar,
  RefreshCw,
  ArrowRight,
  Sparkles
} from 'lucide-react';
import useAuthStore from '../../shared/hooks/useAuthStore';
import { api } from '../../shared/services/apiClient';

interface DailyLearning {
  date: string;
  week: number;
  day: number;
  theme: string;
  task: string;
  deliverable: string;
  learning_objectives: string[];
  study_time_minutes: number;
  status: string;
  sections: {
    textbook: {
      available: boolean;
      completed: boolean;
      content?: any;
    };
    practice: {
      available: boolean;
      completed: boolean;
      problems?: any[];
    };
    quiz: {
      available: boolean;
      completed: boolean;
      questions?: any[];
    };
  };
  progress: {
    completion_percentage: number;
    completed_sections: number;
    total_sections: number;
  };
}

interface Curriculum {
  curriculum_id: number;
  goal: string;
  description: string;
  total_weeks: number;
  daily_minutes: number;
  core_technologies: string[];
  weekly_themes: any[];
}

export default function DashboardPage() {
  const { user } = useAuthStore();
  const navigate = useNavigate();

  // 내 커리큘럼 목록 조회
  const { data: curricula, isLoading: isCurriculaLoading } = useQuery<Curriculum[]>({
    queryKey: ['my-curricula', user?.id],
    queryFn: () => api.get<Curriculum[]>('/mvp/curricula/my'),
    enabled: !!user,
  });

  // 현재 활성 커리큘럼 (첫 번째 것)
  const currentCurriculum = curricula?.[0];

  // 오늘의 학습 조회
  const { data: todayLearning, isLoading: isLearningLoading, error } = useQuery<DailyLearning>({
    queryKey: ['today-learning', currentCurriculum?.curriculum_id],
    queryFn: () => api.get<DailyLearning>(
      `/mvp/daily-learning?curriculum_id=${currentCurriculum?.curriculum_id}`
    ),
    enabled: !!currentCurriculum,
  });

  // 로딩 상태
  if (isCurriculaLoading || isLearningLoading) {
    return (
      <div className="max-w-7xl mx-auto">
        <div className="flex items-center justify-center h-64">
          <div className="text-center">
            <RefreshCw className="w-8 h-8 animate-spin mx-auto mb-4 text-indigo-600" />
            <p className="text-gray-600">학습 정보를 불러오고 있습니다...</p>
          </div>
        </div>
      </div>
    );
  }

  // 커리큘럼 없음 (온보딩 필요)
  if (!currentCurriculum) {
    return (
      <div className="max-w-7xl mx-auto">
        <div className="bg-gradient-to-br from-indigo-50 to-purple-50 rounded-3xl p-12 text-center">
          <div className="inline-block p-4 bg-indigo-100 rounded-full mb-6">
            <Target className="w-12 h-12 text-indigo-600" />
          </div>
          <h2 className="text-3xl font-bold text-gray-900 mb-4">
            학습 목표를 설정해주세요
          </h2>
          <p className="text-lg text-gray-600 mb-8">
            AI가 당신만을 위한 12주 학습 로드맵을 만들어드립니다
          </p>
          <button
            onClick={() => navigate('/onboarding')}
            className="inline-flex items-center gap-2 px-8 py-4 bg-gradient-to-r from-indigo-600 to-purple-600 text-white text-lg font-semibold rounded-full shadow-xl hover:shadow-2xl transform hover:scale-105 transition-all"
          >
            <Sparkles className="w-5 h-5" />
            목표 설정하러 가기
            <ArrowRight className="w-5 h-5" />
          </button>
        </div>
      </div>
    );
  }

  // 에러 처리
  if (error) {
    return (
      <div className="max-w-7xl mx-auto">
        <div className="bg-red-50 border border-red-200 rounded-lg p-6">
          <h3 className="text-red-800 font-medium mb-2">데이터 로드 실패</h3>
          <p className="text-red-600 mb-4">
            {error instanceof Error ? error.message : '알 수 없는 오류가 발생했습니다.'}
          </p>
          <button 
            onClick={() => window.location.reload()}
            className="bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700"
          >
            다시 시도
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto space-y-8">
      {/* 헤더 - 현재 진행 상황 */}
      <div className="bg-gradient-to-r from-indigo-600 to-purple-600 rounded-3xl p-8 text-white">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold mb-2">
              안녕하세요{user?.display_name ? `, ${user.display_name}` : ''}! 👋
            </h1>
            <p className="text-indigo-100 text-lg">
              {currentCurriculum.goal} 로드맵 진행 중
            </p>
          </div>
          <div className="text-right">
            <div className="inline-block bg-white/20 rounded-2xl px-6 py-3">
              <div className="flex items-center gap-2 mb-1">
                <Calendar className="w-5 h-5" />
                <span className="text-sm font-medium">Week {todayLearning?.week || 1}</span>
              </div>
              <p className="text-2xl font-bold">Day {todayLearning?.day || 1}</p>
            </div>
          </div>
        </div>

        {/* 주차 테마 */}
        {todayLearning && (
          <div className="mt-6 bg-white/10 rounded-xl p-4">
            <p className="text-indigo-100 text-sm mb-1">이번 주 학습 테마</p>
            <p className="text-xl font-semibold">{todayLearning.theme}</p>
          </div>
        )}
      </div>

      {/* 오늘의 학습 과제 */}
      {todayLearning && (
        <div className="bg-white rounded-2xl shadow-lg p-6">
          <div className="flex items-start justify-between mb-6">
            <div>
              <h2 className="text-2xl font-bold text-gray-900 mb-2">
                오늘의 학습 과제
              </h2>
              <p className="text-gray-600">{todayLearning.task}</p>
            </div>
            <div className="flex items-center gap-2 px-4 py-2 bg-indigo-50 rounded-full">
              <Clock className="w-4 h-4 text-indigo-600" />
              <span className="text-sm font-medium text-indigo-600">
                {todayLearning.study_time_minutes}분
              </span>
            </div>
          </div>

          {/* 학습 목표 */}
          <div className="mb-6">
            <h3 className="text-sm font-semibold text-gray-700 mb-3">학습 목표</h3>
            <ul className="space-y-2">
              {todayLearning.learning_objectives.map((objective, idx) => (
                <li key={idx} className="flex items-start gap-2">
                  <CheckCircle className="w-5 h-5 text-green-500 flex-shrink-0 mt-0.5" />
                  <span className="text-gray-700">{objective}</span>
                </li>
              ))}
            </ul>
          </div>

          {/* 진도율 */}
          <div className="mb-6">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium text-gray-700">진행률</span>
              <span className="text-sm font-bold text-indigo-600">
                {todayLearning.progress.completion_percentage}%
              </span>
            </div>
            <div className="h-3 bg-gray-200 rounded-full overflow-hidden">
              <div 
                className="h-full bg-gradient-to-r from-indigo-500 to-purple-500 transition-all duration-500"
                style={{ width: `${todayLearning.progress.completion_percentage}%` }}
              />
            </div>
          </div>
        </div>
      )}

      {/* 오늘의 학습 3단계 */}
      <div>
        <h2 className="text-xl font-bold text-gray-900 mb-6">오늘의 학습 단계</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* 1. 교과서 학습 */}
          <LearningCard
            icon={<BookOpen className="w-8 h-8" />}
            title="📖 개념 학습"
            description="AI 튜터의 맞춤 강의"
            status={todayLearning?.sections.textbook.completed ? 'completed' : 'available'}
            available={todayLearning?.sections.textbook.available ?? true}
            onClick={() => navigate('/learning')}
            gradient="from-blue-500 to-cyan-500"
          />

          {/* 2. 실습 코딩 */}
          <LearningCard
            icon={<Code className="w-8 h-8" />}
            title="💻 실습 코딩"
            description="직접 코드를 작성해보세요"
            status={todayLearning?.sections.practice.completed ? 'completed' : 'available'}
            available={todayLearning?.sections.practice.available ?? true}
            onClick={() => navigate('/learning')}
            gradient="from-purple-500 to-pink-500"
          />

          {/* 3. 퀴즈 */}
          <LearningCard
            icon={<CheckCircle className="w-8 h-8" />}
            title="✍️ 이해도 퀴즈"
            description="학습 내용을 확인하세요"
            status={todayLearning?.sections.quiz.completed ? 'completed' : 'locked'}
            available={todayLearning?.sections.quiz.available ?? false}
            onClick={() => navigate('/learning')}
            gradient="from-green-500 to-emerald-500"
          />
        </div>
      </div>

      {/* 전체 로드맵 보기 */}
      <div className="bg-gradient-to-br from-gray-50 to-gray-100 rounded-2xl p-8">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-lg font-bold text-gray-900 mb-2">
              전체 학습 로드맵
            </h3>
            <p className="text-gray-600">
              {currentCurriculum.total_weeks}주 완성 코스 • {currentCurriculum.core_technologies.length}개 핵심 기술
            </p>
          </div>
          <button
            onClick={() => navigate('/ai-assistant')}
            className="flex items-center gap-2 px-6 py-3 bg-white rounded-xl shadow-md hover:shadow-lg transition-shadow"
          >
            <span className="font-medium text-gray-900">로드맵 보기</span>
            <ArrowRight className="w-4 h-4" />
          </button>
        </div>

        {/* 핵심 기술 */}
        <div className="mt-6 flex flex-wrap gap-2">
          {currentCurriculum.core_technologies.map((tech, idx) => (
            <span
              key={idx}
              className="px-3 py-1 bg-white rounded-full text-sm font-medium text-gray-700 shadow-sm"
            >
              {tech}
            </span>
          ))}
        </div>
      </div>
    </div>
  );
}

// ============= 학습 카드 컴포넌트 =============

interface LearningCardProps {
  icon: React.ReactNode;
  title: string;
  description: string;
  status: 'available' | 'completed' | 'locked';
  available: boolean;
  onClick: () => void;
  gradient: string;
}

function LearningCard({ icon, title, description, status, available, onClick, gradient }: LearningCardProps) {
  const isCompleted = status === 'completed';
  const isLocked = !available || status === 'locked';

  return (
    <button
      onClick={onClick}
      disabled={isLocked}
      className={`
        relative p-6 rounded-2xl transition-all duration-200 text-left
        ${isLocked 
          ? 'bg-gray-100 cursor-not-allowed opacity-60' 
          : 'bg-white shadow-lg hover:shadow-xl transform hover:-translate-y-1'
        }
      `}
    >
      {/* 완료 배지 */}
      {isCompleted && (
        <div className="absolute top-4 right-4">
          <div className="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center">
            <CheckCircle className="w-5 h-5 text-green-600" />
          </div>
        </div>
      )}

      {/* 잠금 배지 */}
      {isLocked && (
        <div className="absolute top-4 right-4">
          <div className="w-8 h-8 bg-gray-200 rounded-full flex items-center justify-center">
            <span className="text-gray-500 text-xl">🔒</span>
          </div>
        </div>
      )}

      {/* 아이콘 */}
      <div className={`
        inline-flex p-3 rounded-xl mb-4
        ${isLocked ? 'bg-gray-200 text-gray-400' : `bg-gradient-to-br ${gradient} text-white`}
      `}>
        {icon}
      </div>

      {/* 제목 */}
      <h3 className="text-lg font-bold text-gray-900 mb-2">
        {title}
      </h3>

      {/* 설명 */}
      <p className="text-sm text-gray-600 mb-4">
        {description}
      </p>

      {/* 상태 */}
      <div className="flex items-center gap-2">
        {isCompleted ? (
          <span className="text-sm font-medium text-green-600">완료됨 ✓</span>
        ) : isLocked ? (
          <span className="text-sm font-medium text-gray-400">잠김</span>
        ) : (
          <span className={`text-sm font-medium bg-gradient-to-r ${gradient} bg-clip-text text-transparent`}>
            시작하기 →
          </span>
        )}
      </div>
    </button>
  );
}
