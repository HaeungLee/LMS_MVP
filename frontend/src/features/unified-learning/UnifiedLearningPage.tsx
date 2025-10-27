/**
 * 통합 학습 페이지 (Unified Learning Page)
 * 
 * GPTplan 철학: "교재 → AI 질문 → 실습 → 퀴즈" 하나의 흐름
 * 탭 전환 없이 스크롤만으로 학습 완료
 */

import { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { 
  BookOpen, 
  Code, 
  CheckCircle, 
  Clock
} from 'lucide-react';
import useAuthStore from '../../shared/hooks/useAuthStore';
import { api } from '../../shared/services/apiClient';

// 컴포넌트 import
import ProgressHeader from './components/ProgressHeader';
import TextbookSection from './components/TextbookSection';
import InlineAIMentor from './components/InlineAIMentor';
import PracticeSection from './components/PracticeSection';
import QuizSection from './components/QuizSection';
import CompletionSummary from './components/CompletionSummary';
import MotivationalQuote from '../../shared/components/MotivationalQuote';

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
    sections_completed: number;
    total_sections: number;
    percentage: number;
  };
}

export default function UnifiedLearningPage() {
  const { user } = useAuthStore();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [searchParams, setSearchParams] = useSearchParams();
  const curriculumId = searchParams.get('curriculum_id');
  const targetDate = searchParams.get('target_date'); // 특정 날짜 학습 조회용

  const [currentSection, setCurrentSection] = useState<'textbook' | 'practice' | 'quiz'>('textbook');
  const [completedSections, setCompletedSections] = useState<Set<string>>(new Set());
  const [localProgress, setLocalProgress] = useState(0);

  // 오늘의 학습 데이터 조회
  const { data: dailyLearning, isLoading, error } = useQuery<DailyLearning>({
    queryKey: ['daily-learning', curriculumId, targetDate],
    queryFn: async () => {
      let params = curriculumId ? `?curriculum_id=${curriculumId}` : '';
      if (targetDate) {
        params += curriculumId ? `&target_date=${targetDate}` : `?target_date=${targetDate}`;
      }
      // LLM 호출로 시간이 오래 걸리므로 60초 타임아웃 설정
      const response = await api.get(`/mvp/daily-learning${params}`, { timeoutMs: 60000 });
      return response as DailyLearning;
    },
    enabled: !!user,
    staleTime: 5 * 60 * 1000, // 5분간 캐시 유지
    refetchOnWindowFocus: true, // 포커스 시 재조회
  });

  // 서버 진도와 로컬 state 동기화
  useEffect(() => {
    if (dailyLearning?.sections) {
      const completed = new Set<string>();
      if (dailyLearning.sections.textbook?.completed) completed.add('textbook');
      if (dailyLearning.sections.practice?.completed) completed.add('practice');
      if (dailyLearning.sections.quiz?.completed) completed.add('quiz');
      setCompletedSections(completed);
      
      // 서버 진도율로 초기화
      setLocalProgress(dailyLearning.progress?.percentage || 0);
    }
  }, [dailyLearning]);

  // 실시간 진도율 계산
  useEffect(() => {
    const completedCount = completedSections.size;
    const newProgress = Math.round((completedCount / 3) * 100);
    setLocalProgress(newProgress);
  }, [completedSections]);

  // 섹션 완료 처리
  const handleSectionComplete = (section: 'textbook' | 'practice' | 'quiz') => {
    setCompletedSections(prev => new Set([...prev, section]));
    
    // React Query 캐시 무효화 - 대시보드 자동 갱신
    queryClient.invalidateQueries({ queryKey: ['daily-learning', curriculumId] });
    queryClient.invalidateQueries({ queryKey: ['today-learning'] });
    
    /* 자동 섹션 전환 (선택적 기능 - 필요시 활성화)
     * 사용자가 다시 위로 스크롤해서 내용을 확인하거나
     * 오늘의 학습 내용을 훑어보는 경우를 고려하여 비활성화
     * 사용자가 명시적으로 "다음 단계로" 버튼을 클릭하도록 유도
     * 
    setTimeout(() => {
      if (section === 'textbook' && currentSection === 'textbook') {
        setCurrentSection('practice');
        window.scrollTo({ top: 0, behavior: 'smooth' });
      } else if (section === 'practice' && currentSection === 'practice') {
        setCurrentSection('quiz');
        window.scrollTo({ top: 0, behavior: 'smooth' });
      }
    }, 2000);
    */
  };

  // DAY 네비게이션
  const handlePrevDay = () => {
    if (!dailyLearning) return;
    const prevDate = new Date(dailyLearning.date);
    prevDate.setDate(prevDate.getDate() - 1);
    const dateStr = prevDate.toISOString().split('T')[0];
    
    const params = new URLSearchParams(searchParams);
    params.set('target_date', dateStr);
    setSearchParams(params);
    
    // 섹션 상태 초기화
    setCurrentSection('textbook');
    setCompletedSections(new Set());
  };

  const handleNextDay = () => {
    if (!dailyLearning) return;
    const nextDate = new Date(dailyLearning.date);
    nextDate.setDate(nextDate.getDate() + 1);
    const dateStr = nextDate.toISOString().split('T')[0];
    
    const params = new URLSearchParams(searchParams);
    params.set('target_date', dateStr);
    setSearchParams(params);
    
    // 섹션 상태 초기화
    setCurrentSection('textbook');
    setCompletedSections(new Set());
  };

  const canGoPrevDay = dailyLearning ? dailyLearning.day > 1 : false;
  const canGoNextDay = true; // 항상 다음 날로 이동 가능

  // 콘텐츠 새로고침 (실습/퀴즈 재생성)
  const handleRefreshContent = async (section: 'practice' | 'quiz') => {
    if (!curriculumId || !dailyLearning) return;
    
    try {
      const confirmed = window.confirm(
        `${section === 'practice' ? '실습 문제' : '퀴즈'}를 새로 생성하시겠습니까?\n\n` +
        '기존 진도는 유지되지만, 문제가 완전히 새로 생성됩니다.'
      );
      
      if (!confirmed) return;
      
      // week와 day 정보를 함께 전송
      await api.post(
        `/mvp/refresh-content?curriculum_id=${curriculumId}&section=${section}&week=${dailyLearning.week}&day=${dailyLearning.day}`
      );
      
      // React Query 캐시 무효화하여 새로운 데이터 가져오기
      queryClient.invalidateQueries({ queryKey: ['daily-learning', curriculumId, targetDate] });
      
      alert(`${section === 'practice' ? '실습 문제' : '퀴즈'}가 재생성되었습니다! 🎉`);
    } catch (err) {
      console.error('콘텐츠 재생성 실패:', err);
      alert('콘텐츠 재생성에 실패했습니다. 다시 시도해주세요.');
    }
  };

  // 로딩 상태
  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-indigo-600 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-600">오늘의 학습을 불러오는 중...</p>
        </div>
      </div>
    );
  }

  // 에러 상태
  if (error || !dailyLearning) {
    return (
      <div className="min-h-screen flex items-center justify-center px-4">
        <div className="max-w-md w-full bg-red-50 border border-red-200 rounded-2xl p-8 text-center">
          <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <span className="text-3xl">😢</span>
          </div>
          <h2 className="text-xl font-bold text-gray-900 mb-2">학습 데이터를 불러올 수 없습니다</h2>
          <p className="text-gray-600 mb-6">
            커리큘럼을 먼저 생성해주세요.
          </p>
          <button
            onClick={() => navigate('/onboarding')}
            className="bg-indigo-600 text-white px-6 py-3 rounded-full hover:bg-indigo-700"
          >
            커리큘럼 생성하기
          </button>
        </div>
      </div>
    );
  }

  const { week, day, theme, task, sections, progress } = dailyLearning;
  const allSectionsCompleted = completedSections.size === 3;

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-purple-50">
      {/* 진행 헤더 */}
      <ProgressHeader 
        week={week}
        day={day}
        theme={theme}
        progress={progress.percentage}
        onPrevDay={handlePrevDay}
        onNextDay={handleNextDay}
        canGoPrev={canGoPrevDay}
        canGoNext={canGoNextDay}
      />

      {/* 메인 컨텐츠 */}
      <div className="max-w-4xl mx-auto px-4 py-8">
        {/* 오늘의 과제 카드 */}
        <div className="bg-white rounded-2xl shadow-lg p-8 mb-8">
          <div className="flex items-start gap-4">
            <div className="w-16 h-16 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-2xl flex items-center justify-center flex-shrink-0">
              <Target className="w-8 h-8 text-white" />
            </div>
            <div className="flex-1">
              <h1 className="text-2xl font-bold text-gray-900 mb-2">
                {task}
              </h1>
              <p className="text-gray-600 mb-4">
                Week {week} Day {day} · {theme}
              </p>
              
              {/* 학습 목표 */}
              <div className="bg-indigo-50 rounded-xl p-4 mb-4">
                <h3 className="text-sm font-semibold text-indigo-900 mb-2">📋 오늘의 학습 목표</h3>
                <ul className="space-y-2">
                  {dailyLearning.learning_objectives.map((objective, idx) => (
                    <li key={idx} className="flex items-start gap-2 text-sm text-indigo-800">
                      <CheckCircle className="w-4 h-4 mt-0.5 flex-shrink-0" />
                      <span>{objective}</span>
                    </li>
                  ))}
                </ul>
              </div>

              {/* 예상 시간 */}
              <div className="flex items-center gap-2 text-sm text-gray-500">
                <Clock className="w-4 h-4" />
                <span>예상 소요 시간: {dailyLearning.study_time_minutes}분</span>
              </div>
            </div>
          </div>

          {/* 진행률 바 - 실시간 업데이트 */}
          <div className="mt-6">
            <div className="flex items-center justify-between text-sm mb-2">
              <span className="text-gray-600">전체 진행률</span>
              <span className="font-semibold text-indigo-600">{localProgress}%</span>
            </div>
            <div className="h-3 bg-gray-100 rounded-full overflow-hidden">
              <div 
                className="h-full bg-gradient-to-r from-indigo-500 to-purple-600 rounded-full transition-all duration-500"
                style={{ width: `${localProgress}%` }}
              />
            </div>
            <p className="text-xs text-gray-500 mt-2">
              {completedSections.size} / 3 섹션 완료
            </p>
          </div>
        </div>

        {/* 섹션 네비게이션 - 자유 이동 가능 */}
        <div className="bg-white rounded-2xl shadow-lg p-4 mb-8">
          <div className="mb-3">
            <p className="text-xs text-gray-500">
              💡 원하는 순서대로 학습하세요! 교재→실습→퀴즈 순서를 따를 필요는 없습니다.
            </p>
          </div>
          <div className="grid grid-cols-3 gap-4">
            {[
              { key: 'textbook', icon: BookOpen, label: '📖 교재 학습', color: 'blue' },
              { key: 'practice', icon: Code, label: '💻 실습 코딩', color: 'purple' },
              { key: 'quiz', icon: CheckCircle, label: '✍️ 퀴즈', color: 'green' }
            ].map(({ key, icon: Icon, label, color }) => {
              const isActive = currentSection === key;
              const isCompleted = completedSections.has(key);

              return (
                <button
                  key={key}
                  onClick={() => setCurrentSection(key as any)}
                  className={`
                    relative p-4 rounded-xl transition-all duration-200
                    ${isActive 
                      ? `bg-gradient-to-br from-${color}-500 to-${color}-600 text-white shadow-lg scale-105` 
                      : isCompleted
                        ? `bg-${color}-50 text-${color}-700 hover:shadow-md`
                        : 'bg-gray-50 text-gray-600 hover:bg-gray-100'
                    }
                  `}
                >
                  <div className="flex flex-col items-center gap-2">
                    {isCompleted && (
                      <div className="absolute top-2 right-2 w-6 h-6 bg-green-500 rounded-full flex items-center justify-center">
                        <CheckCircle className="w-4 h-4 text-white" />
                      </div>
                    )}
                    <Icon className="w-6 h-6" />
                    <span className="text-sm font-medium">{label}</span>
                  </div>
                </button>
              );
            })}
          </div>
        </div>

        {/* 현재 섹션 렌더링 */}
        <div className="space-y-8">
          {currentSection === 'textbook' && (
            <>
              <TextbookSection 
                content={sections.textbook.content}
                curriculumId={curriculumId ? parseInt(curriculumId) : undefined}
                onComplete={() => handleSectionComplete('textbook')}
                onNextSection={() => setCurrentSection('practice')}
              />
              <InlineAIMentor 
                context="textbook" 
                topic={theme} 
                currentContent={typeof sections.textbook.content === 'string' ? sections.textbook.content : sections.textbook.content?.text || ''}
              />
            </>
          )}

          {currentSection === 'practice' && (
            <>
              <PracticeSection 
                problems={sections.practice ? [sections.practice] : []}
                curriculumId={curriculumId ? parseInt(curriculumId) : undefined}
                onComplete={() => handleSectionComplete('practice')}
                onRefresh={() => handleRefreshContent('practice')}
                onNextSection={() => setCurrentSection('quiz')}
              />
              <InlineAIMentor 
                context="practice" 
                topic={theme}
                currentContent={JSON.stringify(sections.practice || {})}
              />
            </>
          )}

          {currentSection === 'quiz' && (
            <>
              <QuizSection 
                questions={sections.quiz.questions || []}
                curriculumId={curriculumId ? parseInt(curriculumId) : undefined}
                onComplete={() => handleSectionComplete('quiz')}
                onRefresh={() => handleRefreshContent('quiz')}
              />
            </>
          )}
        </div>

        {/* 완료 요약 */}
        {allSectionsCompleted && (
          <CompletionSummary 
            week={week}
            day={day}
            theme={theme}
            onContinue={() => navigate('/dashboard')}
            onNextDay={handleNextDay}
          />
        )}

        {/* 명언 */}
        <MotivationalQuote />
      </div>
    </div>
  );
}

function Target({ className }: { className?: string }) {
  return (
    <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <circle cx="12" cy="12" r="10" strokeWidth="2"/>
      <circle cx="12" cy="12" r="6" strokeWidth="2"/>
      <circle cx="12" cy="12" r="2" fill="currentColor"/>
    </svg>
  );
}
