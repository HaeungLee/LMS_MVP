/**
 * 커리큘럼 전체 일정 페이지
 * 
 * 주차별/일별 학습 계획을 한눈에 보여줍니다.
 * - 현재 진행 중인 위치 표시
 * - 완료된 학습 체크마크
 * - 각 Day 클릭 시 학습 페이지로 이동
 */

import { useQuery } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { 
  Calendar, 
  CheckCircle, 
  Clock, 
  Play,
  Target,
  RefreshCw,
  ChevronRight
} from 'lucide-react';
import { api } from '../../shared/services/apiClient';
import useAuthStore from '../../shared/hooks/useAuthStore';

interface DaySchedule {
  day: number;
  task: string;
  deliverable: string;
  study_time_minutes: number;
  completed: boolean;
  in_progress: boolean;
}

interface WeekSchedule {
  week: number;
  theme: string;
  days: DaySchedule[];
}

interface CurriculumSchedule {
  curriculum_id: number;
  goal: string;
  total_weeks: number;
  current_week: number;
  current_day: number;
  weeks: WeekSchedule[];
}

interface Curriculum {
  curriculum_id: number;
  goal: string;
  description: string;
  total_weeks: number;
  daily_minutes: number;
  core_technologies: string[];
}

export default function CurriculumSchedulePage() {
  const { user } = useAuthStore();
  const navigate = useNavigate();

  // 내 커리큘럼 조회
  const { data: curricula } = useQuery<Curriculum[]>({
    queryKey: ['my-curricula', user?.id],
    queryFn: () => api.get<Curriculum[]>('/mvp/curricula/my'),
    enabled: !!user,
  });

  const currentCurriculum = curricula?.[0];

  // 전체 일정 조회
  const { data: schedule, isLoading, error } = useQuery<CurriculumSchedule>({
    queryKey: ['curriculum-schedule', currentCurriculum?.curriculum_id],
    queryFn: () => api.get<CurriculumSchedule>(`/mvp/curricula/${currentCurriculum?.curriculum_id}/schedule`),
    enabled: !!currentCurriculum,
  });

  const handleDayClick = (week: number, day: number) => {
    if (!currentCurriculum) return;
    
    // Day 클릭 시 학습 페이지로 이동
    const targetDate = calculateTargetDate(week, day);
    navigate(`/learning?curriculum_id=${currentCurriculum.curriculum_id}&target_date=${targetDate}`);
  };

  const calculateTargetDate = (week: number, day: number): string => {
    // 간단한 날짜 계산 (시작일 기준)
    const today = new Date();
    const daysOffset = (week - 1) * 5 + (day - 1);
    const targetDate = new Date(today);
    targetDate.setDate(today.getDate() + daysOffset - ((schedule?.current_week || 1) - 1) * 5 - ((schedule?.current_day || 1) - 1));
    return targetDate.toISOString().split('T')[0];
  };

  if (isLoading) {
    return (
      <div className="max-w-7xl mx-auto p-6">
        <div className="flex items-center justify-center h-64">
          <div className="text-center">
            <RefreshCw className="w-8 h-8 animate-spin mx-auto mb-4 text-indigo-600" />
            <p className="text-gray-600">학습 일정을 불러오고 있습니다...</p>
          </div>
        </div>
      </div>
    );
  }

  if (error || !schedule) {
    return (
      <div className="max-w-7xl mx-auto p-6">
        <div className="bg-red-50 border border-red-200 rounded-xl p-6">
          <p className="text-red-600">학습 일정을 불러올 수 없습니다.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto p-6">
      {/* 헤더 */}
      <div className="mb-8">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
              <Calendar className="w-8 h-8 text-indigo-600" />
              {schedule.goal}
            </h1>
            <p className="text-gray-600 mt-2">
              총 {schedule.total_weeks}주 과정 • 현재 Week {schedule.current_week}, Day {schedule.current_day}
            </p>
          </div>
          <button
            onClick={() => navigate('/dashboard')}
            className="px-6 py-3 bg-indigo-600 text-white rounded-xl hover:bg-indigo-700 transition-colors font-medium"
          >
            대시보드로 돌아가기
          </button>
        </div>
      </div>

      {/* 진도 요약 */}
      <div className="grid grid-cols-3 gap-6 mb-8">
        <div className="bg-white rounded-xl shadow-lg p-6">
          <div className="flex items-center gap-3 mb-2">
            <Target className="w-5 h-5 text-blue-600" />
            <span className="text-sm font-medium text-gray-600">전체 학습일</span>
          </div>
          <p className="text-2xl font-bold text-gray-900">{schedule.total_weeks * 5}일</p>
        </div>
        <div className="bg-white rounded-xl shadow-lg p-6">
          <div className="flex items-center gap-3 mb-2">
            <CheckCircle className="w-5 h-5 text-green-600" />
            <span className="text-sm font-medium text-gray-600">완료</span>
          </div>
          <p className="text-2xl font-bold text-gray-900">
            {schedule.weeks.reduce((total, week) => 
              total + week.days.filter(d => d.completed).length, 0
            )}일
          </p>
        </div>
        <div className="bg-white rounded-xl shadow-lg p-6">
          <div className="flex items-center gap-3 mb-2">
            <Play className="w-5 h-5 text-indigo-600" />
            <span className="text-sm font-medium text-gray-600">남은 학습</span>
          </div>
          <p className="text-2xl font-bold text-gray-900">
            {schedule.weeks.reduce((total, week) => 
              total + week.days.filter(d => !d.completed && !d.in_progress).length, 0
            )}일
          </p>
        </div>
      </div>

      {/* 주차별 일정 */}
      <div className="space-y-6">
        {schedule.weeks.map((week) => (
          <div key={week.week} className="bg-white rounded-2xl shadow-lg p-6">
            {/* 주차 헤더 */}
            <div className="flex items-center gap-3 mb-6 pb-4 border-b">
              <div className="w-12 h-12 bg-indigo-100 rounded-xl flex items-center justify-center">
                <span className="text-indigo-600 font-bold">W{week.week}</span>
              </div>
              <div>
                <h2 className="text-xl font-bold text-gray-900">Week {week.week}</h2>
                <p className="text-gray-600">{week.theme}</p>
              </div>
            </div>

            {/* 일별 학습 */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
              {week.days.map((day) => (
                <button
                  key={day.day}
                  onClick={() => handleDayClick(week.week, day.day)}
                  className={`
                    relative p-4 rounded-xl border-2 transition-all text-left
                    ${day.completed 
                      ? 'border-green-200 bg-green-50 hover:bg-green-100' 
                      : day.in_progress
                        ? 'border-indigo-500 bg-indigo-50 hover:bg-indigo-100 shadow-lg'
                        : 'border-gray-200 bg-white hover:bg-gray-50 hover:border-gray-300'
                    }
                  `}
                >
                  {/* 상태 아이콘 */}
                  <div className="absolute top-3 right-3">
                    {day.completed ? (
                      <CheckCircle className="w-5 h-5 text-green-600" />
                    ) : day.in_progress ? (
                      <Play className="w-5 h-5 text-indigo-600" />
                    ) : (
                      <Clock className="w-5 h-5 text-gray-400" />
                    )}
                  </div>

                  {/* Day 번호 */}
                  <div className="mb-2">
                    <span className={`
                      text-sm font-bold
                      ${day.completed ? 'text-green-700' : day.in_progress ? 'text-indigo-700' : 'text-gray-500'}
                    `}>
                      Day {day.day}
                    </span>
                  </div>

                  {/* 학습 내용 */}
                  <h3 className="text-sm font-semibold text-gray-900 mb-2 line-clamp-2">
                    {day.task}
                  </h3>
                  <p className="text-xs text-gray-600 mb-3 line-clamp-2">
                    {day.deliverable}
                  </p>

                  {/* 학습 시간 */}
                  <div className="flex items-center gap-1 text-xs text-gray-500">
                    <Clock className="w-3 h-3" />
                    <span>{day.study_time_minutes}분</span>
                  </div>

                  {/* 진행 중 표시 */}
                  {day.in_progress && (
                    <div className="mt-3 pt-3 border-t border-indigo-200">
                      <div className="flex items-center gap-1 text-xs font-medium text-indigo-600">
                        <ChevronRight className="w-3 h-3" />
                        <span>학습 시작하기</span>
                      </div>
                    </div>
                  )}
                </button>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
