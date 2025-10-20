/**
 * 온보딩 페이지 - 사용자의 학습 목표 설정
 * 
 * 플로우:
 * Step 1: 환영 메시지 & 시작하기
 * Step 2: 목표 선택 (백엔드 개발자, 데이터 분석가, 자동화 전문가)
 * Step 3: 현재 수준 & 학습 시간 설정
 * Step 4: AI 커리큘럼 생성 중... (30초 로딩)
 * Step 5: 생성된 로드맵 미리보기 → 대시보드로 이동
 */

import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { api } from '../../shared/services/apiClient';

// ============= 타입 정의 =============

interface Goal {
  key: string;
  title: string;
  description: string;
  icon: string;
  color: string;
  defaultWeeks: number;
  technologies: string[];
}

interface GeneratedCurriculum {
  curriculum_id: number;
  goal: string;
  description: string;
  total_weeks: number;
  daily_minutes: number;
  core_technologies: string[];
  weekly_themes: Array<{
    week: number;
    theme: string;
    description: string;
    daily_tasks: Array<{
      day: number;
      title: string;
      type: string;
      duration_minutes: number;
      content: string;
    }>;
  }>;
}

// ============= Step 1: 환영 메시지 =============

const WelcomeStep: React.FC<{ onNext: () => void }> = ({ onNext }) => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-purple-50 flex items-center justify-center px-4">
      <div className="max-w-2xl w-full text-center space-y-8 animate-fade-in">
        {/* 로고 & 타이틀 */}
        <div className="space-y-4">
          <div className="inline-block p-6 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-3xl shadow-xl">
            <svg className="w-20 h-20 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
            </svg>
          </div>
          <h1 className="text-5xl font-bold text-gray-900">
            AI Learning Platform
          </h1>
          <p className="text-xl text-gray-600">
            당신만을 위한 12주 학습 로드맵을 만들어드립니다
          </p>
        </div>

        {/* 주요 특징 */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 py-8">
          <div className="p-6 bg-white rounded-2xl shadow-lg hover:shadow-xl transition-shadow">
            <div className="text-4xl mb-3">🎯</div>
            <h3 className="font-semibold text-gray-900 mb-2">목표 기반</h3>
            <p className="text-sm text-gray-600">백엔드 개발자, 데이터 분석가 등 직무별 맞춤 커리큘럼</p>
          </div>
          <div className="p-6 bg-white rounded-2xl shadow-lg hover:shadow-xl transition-shadow">
            <div className="text-4xl mb-3">🤖</div>
            <h3 className="font-semibold text-gray-900 mb-2">AI 튜터</h3>
            <p className="text-sm text-gray-600">매일 교과서 + 실습 + 퀴즈로 단계별 학습</p>
          </div>
          <div className="p-6 bg-white rounded-2xl shadow-lg hover:shadow-xl transition-shadow">
            <div className="text-4xl mb-3">📊</div>
            <h3 className="font-semibold text-gray-900 mb-2">진도 관리</h3>
            <p className="text-sm text-gray-600">실시간 학습 현황과 성취도 트래킹</p>
          </div>
        </div>

        {/* 시작 버튼 */}
        <button
          onClick={onNext}
          className="group px-12 py-4 bg-gradient-to-r from-indigo-600 to-purple-600 text-white text-lg font-semibold rounded-full shadow-xl hover:shadow-2xl transform hover:scale-105 transition-all duration-200"
        >
          <span className="flex items-center gap-2">
            시작하기
            <svg className="w-5 h-5 group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
            </svg>
          </span>
        </button>

        <p className="text-sm text-gray-500">
          설정은 2분이면 완료됩니다 ⏱️
        </p>
      </div>
    </div>
  );
};

// ============= Step 2: 목표 선택 =============

const GoalSelectionStep: React.FC<{
  goals: Goal[];
  selectedGoal: Goal | null;
  onSelect: (goal: Goal) => void;
  onNext: () => void;
  onBack: () => void;
}> = ({ goals, selectedGoal, onSelect, onNext, onBack }) => {
  const [showCustomInput, setShowCustomInput] = useState(false);
  const [customGoal, setCustomGoal] = useState('');

  const handleCustomGoalSubmit = () => {
    if (!customGoal.trim()) return;
    
    // 커스텀 목표를 Goal 객체로 변환
    const customGoalObject: Goal = {
      key: 'custom',
      title: '맞춤 목표',
      description: customGoal,
      icon: '🎯',
      color: 'from-orange-500 to-red-500',
      defaultWeeks: 12,
      technologies: ['AI 맞춤 추천']
    };
    
    onSelect(customGoalObject);
    setShowCustomInput(false);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-purple-50 py-12 px-4">
      <div className="max-w-6xl mx-auto">
        {/* 헤더 */}
        <div className="text-center mb-12">
          <h2 className="text-4xl font-bold text-gray-900 mb-4">
            어떤 개발자가 되고 싶으신가요?
          </h2>
          <p className="text-lg text-gray-600">
            목표에 맞춘 12주 커리큘럼을 AI가 생성해드립니다
          </p>
        </div>

        {/* 목표 카드들 + 직접 입력 */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          {goals.map((goal) => (
            <div
              key={goal.key}
              onClick={() => onSelect(goal)}
              className={`
                relative p-8 rounded-2xl cursor-pointer transform transition-all duration-200
                ${selectedGoal?.key === goal.key
                  ? `bg-gradient-to-br ${goal.color} text-white shadow-2xl scale-105`
                  : 'bg-white hover:shadow-xl hover:scale-102'
                }
              `}
            >
              {/* 선택 체크마크 */}
              {selectedGoal?.key === goal.key && (
                <div className="absolute top-4 right-4 w-8 h-8 bg-white text-indigo-600 rounded-full flex items-center justify-center">
                  <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                  </svg>
                </div>
              )}

              {/* 아이콘 */}
              <div className="text-6xl mb-4">{goal.icon}</div>

              {/* 제목 & 설명 */}
              <h3 className="text-2xl font-bold mb-3">{goal.title}</h3>
              <p className={`text-sm mb-6 ${selectedGoal?.key === goal.key ? 'text-white/90' : 'text-gray-600'}`}>
                {goal.description}
              </p>

              {/* 기술 스택 */}
              <div className="space-y-2">
                <p className={`text-xs font-semibold ${selectedGoal?.key === goal.key ? 'text-white/80' : 'text-gray-500'}`}>
                  배울 기술:
                </p>
                <div className="flex flex-wrap gap-2">
                  {goal.technologies.slice(0, 3).map((tech, idx) => (
                    <span
                      key={idx}
                      className={`px-3 py-1 rounded-full text-xs font-medium ${
                        selectedGoal?.key === goal.key
                          ? 'bg-white/20 text-white'
                          : 'bg-gray-100 text-gray-700'
                      }`}
                    >
                      {tech}
                    </span>
                  ))}
                </div>
              </div>

              {/* 기간 */}
              <div className="mt-4 pt-4 border-t border-current/20">
                <p className="text-sm font-semibold">
                  📅 기본 {goal.defaultWeeks}주 과정
                </p>
              </div>
            </div>
          ))}

          {/* 직접 입력 카드 */}
          <div
            onClick={() => !showCustomInput && setShowCustomInput(true)}
            className={`
              relative p-8 rounded-2xl cursor-pointer transform transition-all duration-200
              ${selectedGoal?.key === 'custom'
                ? 'bg-gradient-to-br from-orange-500 to-red-500 text-white shadow-2xl scale-105'
                : showCustomInput
                  ? 'bg-white border-2 border-orange-500 shadow-xl scale-105'
                  : 'bg-gradient-to-br from-orange-50 to-red-50 border-2 border-dashed border-orange-300 hover:border-orange-500 hover:shadow-xl'
              }
            `}
          >
            {/* 선택 체크마크 */}
            {selectedGoal?.key === 'custom' && (
              <div className="absolute top-4 right-4 w-8 h-8 bg-white text-orange-600 rounded-full flex items-center justify-center">
                <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                </svg>
              </div>
            )}

            {!showCustomInput ? (
              <>
                {/* 아이콘 */}
                <div className="text-6xl mb-4">✏️</div>
                {/* 제목 & 설명 */}
                <h3 className="text-2xl font-bold mb-3 text-orange-900">직접 입력</h3>
                <p className="text-sm mb-6 text-orange-700">
                  원하는 목표를 자유롭게 입력하고 AI가 맞춤 커리큘럼을 만들어드립니다
                </p>
                <div className="mt-4 pt-4 border-t border-orange-200">
                  <p className="text-sm font-semibold text-orange-800">
                    💡 예: "웹 크롤링 배우기", "Django REST API"
                  </p>
                </div>
              </>
            ) : (
              <div className="space-y-4">
                <h3 className="text-xl font-bold text-gray-900 mb-4">
                  🎯 학습 목표를 입력하세요
                </h3>
                <textarea
                  value={customGoal}
                  onChange={(e) => setCustomGoal(e.target.value)}
                  placeholder="예: Python으로 웹 크롤링 배우고 싶어요&#10;예: FastAPI로 REST API 서버 만들기&#10;예: 데이터 분석을 위한 Pandas 마스터"
                  className="w-full h-32 px-4 py-3 border-2 border-orange-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-orange-500 resize-none text-sm"
                  autoFocus
                />
                <div className="flex gap-2">
                  <button
                    onClick={handleCustomGoalSubmit}
                    disabled={!customGoal.trim()}
                    className="flex-1 bg-gradient-to-r from-orange-600 to-red-600 text-white py-3 px-4 rounded-xl hover:shadow-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed font-semibold"
                  >
                    ✨ AI 커리큘럼 생성
                  </button>
                  <button
                    onClick={() => {
                      setShowCustomInput(false);
                      setCustomGoal('');
                    }}
                    className="px-4 py-3 bg-gray-100 text-gray-700 rounded-xl hover:bg-gray-200 transition-colors"
                  >
                    취소
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* 하단 버튼 */}
        <div className="flex justify-between items-center">
          <button
            onClick={onBack}
            className="px-6 py-3 text-gray-600 hover:text-gray-900 font-medium flex items-center gap-2 transition-colors"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
            이전
          </button>

          <button
            onClick={onNext}
            disabled={!selectedGoal}
            className={`
              px-10 py-4 rounded-full font-semibold text-lg shadow-xl transition-all
              ${selectedGoal
                ? 'bg-gradient-to-r from-indigo-600 to-purple-600 text-white hover:shadow-2xl transform hover:scale-105'
                : 'bg-gray-200 text-gray-400 cursor-not-allowed'
              }
            `}
          >
            다음 단계
          </button>
        </div>
      </div>
    </div>
  );
};

// ============= Step 3: 세부 설정 =============

const DetailSettingsStep: React.FC<{
  selectedGoal: Goal;
  currentLevel: string;
  dailyMinutes: number;
  onLevelChange: (level: string) => void;
  onMinutesChange: (minutes: number) => void;
  onGenerate: () => void;
  onBack: () => void;
}> = ({ selectedGoal, currentLevel, dailyMinutes, onLevelChange, onMinutesChange, onGenerate, onBack }) => {
  const levels = [
    '처음 배웁니다 (프로그래밍 경험 없음)',
    '입문 수준 (간단한 코드 이해 가능)',
    '기초 수준 (함수, 조건문, 반복문 사용 가능)',
    '중급 이상 (객체지향, 비동기 처리 경험)'
  ];

  const minutesOptions = [30, 60, 90, 120];

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-purple-50 py-12 px-4">
      <div className="max-w-3xl mx-auto">
        {/* 헤더 */}
        <div className="text-center mb-12">
          <div className="inline-block px-6 py-2 bg-white rounded-full shadow-md mb-6">
            <span className="text-4xl">{selectedGoal.icon}</span>
            <span className="ml-3 text-lg font-semibold text-gray-900">{selectedGoal.title}</span>
          </div>
          <h2 className="text-3xl font-bold text-gray-900 mb-4">
            학습 환경을 설정해주세요
          </h2>
          <p className="text-gray-600">
            AI가 당신의 수준과 시간에 맞춰 최적의 커리큘럼을 생성합니다
          </p>
        </div>

        {/* 설정 카드 */}
        <div className="bg-white rounded-3xl shadow-2xl p-8 space-y-8">
          {/* 현재 수준 */}
          <div>
            <label className="block text-lg font-semibold text-gray-900 mb-4">
              � 프로그래밍 경험
            </label>
            <div className="grid grid-cols-1 gap-3">
              {levels.map((level) => (
                <button
                  key={level}
                  onClick={() => onLevelChange(level)}
                  className={`
                    p-4 rounded-xl text-left transition-all
                    ${currentLevel === level
                      ? 'bg-gradient-to-r from-indigo-600 to-purple-600 text-white shadow-lg'
                      : 'bg-gray-50 hover:bg-gray-100 text-gray-900'
                    }
                  `}
                >
                  <div className="flex items-center gap-3">
                    <div className={`w-5 h-5 rounded-full border-2 flex items-center justify-center ${
                      currentLevel === level ? 'border-white' : 'border-gray-300'
                    }`}>
                      {currentLevel === level && (
                        <div className="w-3 h-3 rounded-full bg-white"></div>
                      )}
                    </div>
                    <span className="font-medium">{level}</span>
                  </div>
                </button>
              ))}
            </div>
          </div>

          {/* 일일 학습 시간 */}
          <div>
            <label className="block text-lg font-semibold text-gray-900 mb-4">
              ⏰ 하루 학습 시간
            </label>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {minutesOptions.map((minutes) => (
                <button
                  key={minutes}
                  onClick={() => onMinutesChange(minutes)}
                  className={`
                    p-6 rounded-xl transition-all
                    ${dailyMinutes === minutes
                      ? 'bg-gradient-to-br from-indigo-600 to-purple-600 text-white shadow-lg transform scale-105'
                      : 'bg-gray-50 hover:bg-gray-100 text-gray-900'
                    }
                  `}
                >
                  <div className="text-3xl font-bold mb-1">{minutes}</div>
                  <div className="text-sm opacity-90">분</div>
                </button>
              ))}
            </div>
            <p className="mt-3 text-sm text-gray-500">
              💡 평균 수강생은 하루 60분 학습합니다
            </p>
          </div>

          {/* 예상 완료 시간 */}
          <div className="p-6 bg-gradient-to-r from-indigo-50 to-purple-50 rounded-2xl">
            <div className="flex items-center gap-4">
              <div className="text-4xl">🎯</div>
              <div>
                <p className="text-sm text-gray-600 mb-1">예상 완료 시간</p>
                <p className="text-2xl font-bold text-gray-900">
                  {selectedGoal.defaultWeeks}주 ({selectedGoal.defaultWeeks * 5}일)
                </p>
                <p className="text-sm text-gray-500 mt-1">
                  하루 {dailyMinutes}분 × 주 5일 = 총 {selectedGoal.defaultWeeks * 5 * dailyMinutes / 60}시간
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* 하단 버튼 */}
        <div className="flex justify-between items-center mt-8">
          <button
            onClick={onBack}
            className="px-6 py-3 text-gray-600 hover:text-gray-900 font-medium flex items-center gap-2 transition-colors"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
            이전
          </button>

          <button
            onClick={onGenerate}
            className="group px-10 py-4 bg-gradient-to-r from-indigo-600 to-purple-600 text-white text-lg font-semibold rounded-full shadow-xl hover:shadow-2xl transform hover:scale-105 transition-all"
          >
            <span className="flex items-center gap-2">
              🚀 AI 커리큘럼 생성
              <svg className="w-5 h-5 group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
              </svg>
            </span>
          </button>
        </div>
      </div>
    </div>
  );
};

// ============= Step 4: AI 생성 중 =============

const GeneratingStep: React.FC = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-purple-50 flex items-center justify-center px-4">
      <div className="max-w-2xl w-full text-center space-y-8">
        {/* 로딩 애니메이션 */}
        <div className="relative">
          <div className="w-32 h-32 mx-auto">
            <div className="absolute inset-0 border-8 border-indigo-200 rounded-full"></div>
            <div className="absolute inset-0 border-8 border-indigo-600 rounded-full border-t-transparent animate-spin"></div>
            <div className="absolute inset-0 flex items-center justify-center">
              <span className="text-4xl">🤖</span>
            </div>
          </div>
        </div>

        {/* 메시지 */}
        <div className="space-y-4">
          <h2 className="text-3xl font-bold text-gray-900">
            AI가 커리큘럼을 생성하고 있습니다...
          </h2>
          <p className="text-lg text-gray-600">
            2명의 AI 전문가가 협력하여 당신만의 학습 로드맵을 설계합니다
          </p>
        </div>

        {/* 진행 상황 */}
        <div className="space-y-4">
          <div className="flex items-center gap-4 p-4 bg-white rounded-xl shadow-md">
            <div className="w-10 h-10 bg-green-100 text-green-600 rounded-full flex items-center justify-center">
              <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
              </svg>
            </div>
            <p className="text-left flex-1 text-gray-900">학습 목표 분석 완료</p>
          </div>
          <div className="flex items-center gap-4 p-4 bg-white rounded-xl shadow-md">
            <div className="w-10 h-10 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center animate-pulse">
              <svg className="w-6 h-6 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
            </div>
            <p className="text-left flex-1 text-gray-900">주차별 커리큘럼 설계 중...</p>
          </div>
          <div className="flex items-center gap-4 p-4 bg-gray-50 rounded-xl">
            <div className="w-10 h-10 bg-gray-200 rounded-full"></div>
            <p className="text-left flex-1 text-gray-400">일일 학습 과제 생성 대기</p>
          </div>
        </div>

        <p className="text-sm text-gray-500">
          ⏱️ 약 30초 소요됩니다...
        </p>
      </div>
    </div>
  );
};

// ============= Step 5: 생성 완료 & 미리보기 =============

const PreviewStep: React.FC<{
  curriculum: GeneratedCurriculum;
  onStart: () => void;
}> = ({ curriculum, onStart }) => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-purple-50 py-12 px-4">
      <div className="max-w-5xl mx-auto">
        {/* 성공 헤더 */}
        <div className="text-center mb-12">
          <div className="inline-block p-4 bg-green-100 rounded-full mb-4">
            <svg className="w-16 h-16 text-green-600" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
            </svg>
          </div>
          <h2 className="text-4xl font-bold text-gray-900 mb-4">
            🎉 커리큘럼 생성 완료!
          </h2>
          <p className="text-lg text-gray-600">
            {curriculum.goal} 로드맵이 준비되었습니다
          </p>
        </div>

        {/* 커리큘럼 요약 */}
        <div className="bg-white rounded-3xl shadow-2xl p-8 mb-8">
          {/* 기본 정보 */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8 pb-8 border-b">
            <div className="text-center">
              <p className="text-gray-600 mb-2">총 학습 기간</p>
              <p className="text-3xl font-bold text-indigo-600">{curriculum.total_weeks}주</p>
            </div>
            <div className="text-center">
              <p className="text-gray-600 mb-2">일일 학습 시간</p>
              <p className="text-3xl font-bold text-purple-600">{curriculum.daily_minutes}분</p>
            </div>
            <div className="text-center">
              <p className="text-gray-600 mb-2">핵심 기술</p>
              <p className="text-3xl font-bold text-pink-600">{curriculum.core_technologies.length}개</p>
            </div>
          </div>

          {/* 핵심 기술 */}
          <div className="mb-8">
            <h3 className="text-xl font-bold text-gray-900 mb-4">🛠️ 배울 핵심 기술</h3>
            <div className="flex flex-wrap gap-3">
              {curriculum.core_technologies.map((tech, idx) => (
                <span
                  key={idx}
                  className="px-4 py-2 bg-gradient-to-r from-indigo-500 to-purple-500 text-white rounded-full font-medium"
                >
                  {tech}
                </span>
              ))}
            </div>
          </div>

          {/* 주차별 테마 (처음 4주만 표시) */}
          <div>
            <h3 className="text-xl font-bold text-gray-900 mb-4">📅 주차별 로드맵 (미리보기)</h3>
            <div className="space-y-3">
              {curriculum.weekly_themes?.slice(0, 4).map((weekData) => (
                <div key={weekData.week} className="p-4 bg-gradient-to-r from-indigo-50 to-purple-50 rounded-xl">
                  <div className="flex items-start gap-4">
                    <div className="flex-shrink-0 w-12 h-12 bg-gradient-to-br from-indigo-600 to-purple-600 text-white rounded-xl flex items-center justify-center font-bold">
                      {weekData.week}
                    </div>
                    <div className="flex-1">
                      <h4 className="font-bold text-gray-900 mb-2">{weekData.theme}</h4>
                      <p className="text-sm text-gray-600 mb-2">{weekData.description}</p>
                      <div className="flex flex-wrap gap-2">
                        {weekData.daily_tasks?.slice(0, 3).map((task, idx) => (
                          <span key={idx} className="text-sm px-3 py-1 bg-white rounded-full text-gray-700">
                            Day {task.day}: {task.title}
                          </span>
                        ))}
                        {(weekData.daily_tasks?.length || 0) > 3 && (
                          <span className="text-sm px-3 py-1 bg-gray-100 rounded-full text-gray-500">
                            +{(weekData.daily_tasks?.length || 0) - 3}개 더
                          </span>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
            <p className="text-sm text-gray-500 text-center mt-4">
              ... 총 {curriculum.total_weeks}주 커리큘럼
            </p>
          </div>
        </div>

        {/* 시작 버튼 */}
        <div className="text-center">
          <button
            onClick={onStart}
            className="group px-16 py-5 bg-gradient-to-r from-indigo-600 to-purple-600 text-white text-xl font-bold rounded-full shadow-2xl hover:shadow-3xl transform hover:scale-105 transition-all"
          >
            <span className="flex items-center gap-3">
              <span>🚀</span>
              <span>학습 시작하기</span>
              <svg className="w-6 h-6 group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
              </svg>
            </span>
          </button>
          <p className="mt-4 text-gray-600">
            대시보드에서 오늘의 학습을 시작할 수 있습니다
          </p>
        </div>
      </div>
    </div>
  );
};

// ============= 메인 온보딩 컴포넌트 =============

const OnboardingPage: React.FC = () => {
  const navigate = useNavigate();
  const [step, setStep] = useState(1);
  const [goals, setGoals] = useState<Goal[]>([]);
  const [selectedGoal, setSelectedGoal] = useState<Goal | null>(null);
  const [currentLevel, setCurrentLevel] = useState('기초 수준 (함수, 조건문, 반복문 사용 가능)');
  const [dailyMinutes, setDailyMinutes] = useState(60);
  const [generatedCurriculum, setGeneratedCurriculum] = useState<GeneratedCurriculum | null>(null);
  const [isGenerating, setIsGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isLoadingGoals, setIsLoadingGoals] = useState(false);

  // 목표 목록 불러오기
  React.useEffect(() => {
    let mounted = true;
    
    const fetchGoals = async () => {
      if (isLoadingGoals) return; // 중복 요청 방지
      
      setIsLoadingGoals(true);
      try {
        console.log('🎯 목표 목록 불러오기 시작...');
        const goals = await api.get<Goal[]>('/mvp/onboarding/goals', { timeoutMs: 10000 });
        
        if (mounted) {
          console.log('✅ 목표 목록 로드 성공:', goals);
          setGoals(goals);
        }
      } catch (err: any) {
        console.error('❌ 목표 불러오기 실패:', err);
        if (mounted) {
          setError('목표를 불러올 수 없습니다. 잠시 후 다시 시도해주세요.');
        }
      } finally {
        if (mounted) {
          setIsLoadingGoals(false);
        }
      }
    };

    fetchGoals();

    return () => {
      mounted = false;
    };
  }, []); // 빈 배열로 한 번만 실행

  // 커리큘럼 생성
  const handleGenerateCurriculum = async () => {
    if (!selectedGoal) return;

    setIsGenerating(true);
    setStep(4); // 로딩 화면으로 이동

    try {
      const requestData: any = {
        goal_key: selectedGoal.key,
        current_level: currentLevel,
        target_weeks: null, // 기본값 사용
        daily_study_minutes: dailyMinutes
      };
      
      // 커스텀 목표인 경우 custom_goal 필드 추가
      if (selectedGoal.key === 'custom') {
        requestData.custom_goal = selectedGoal.description;
      }

      const curriculum = await api.post<GeneratedCurriculum>(
        '/mvp/onboarding/generate-curriculum',
        requestData,
        { timeoutMs: 120000 } // 120초 타임아웃 (2-Agent 협력 시간 고려)
      );

      setGeneratedCurriculum(curriculum);
      setStep(5); // 미리보기 화면으로
    } catch (err: any) {
      console.error('커리큘럼 생성 실패:', err);
      setError('커리큘럼 생성에 실패했습니다. 다시 시도해주세요.');
      setStep(3); // 설정 화면으로 돌아가기
    } finally {
      setIsGenerating(false);
    }
  };

  // 학습 시작 (대시보드로 이동)
  const handleStartLearning = () => {
    navigate('/dashboard');
  };

  // 에러 표시
  if (error) {
    return (
      <div className="min-h-screen bg-red-50 flex items-center justify-center px-4">
        <div className="max-w-md bg-white rounded-2xl shadow-xl p-8 text-center">
          <div className="text-6xl mb-4">⚠️</div>
          <h2 className="text-2xl font-bold text-gray-900 mb-4">오류 발생</h2>
          <p className="text-gray-600 mb-6">{error}</p>
          <div className="space-y-3">
            <button
              onClick={() => {
                setError(null);
                setStep(1);
                window.location.reload(); // 페이지 새로고침
              }}
              className="w-full px-6 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700"
            >
              다시 시도하기
            </button>
            <button
              onClick={() => navigate('/dashboard')}
              className="w-full px-6 py-3 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300"
            >
              대시보드로 이동
            </button>
          </div>
        </div>
      </div>
    );
  }

  // 목표 로딩 중
  if (isLoadingGoals && goals.length === 0) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-purple-50 flex items-center justify-center px-4">
        <div className="text-center">
          <div className="w-16 h-16 mx-auto mb-4">
            <div className="w-16 h-16 border-4 border-indigo-200 border-t-indigo-600 rounded-full animate-spin"></div>
          </div>
          <h2 className="text-xl font-bold text-gray-900 mb-2">목표 목록을 불러오는 중...</h2>
          <p className="text-gray-600">잠시만 기다려주세요</p>
        </div>
      </div>
    );
  }

  // Step별 렌더링
  return (
    <>
      {step === 1 && <WelcomeStep onNext={() => setStep(2)} />}
      
      {step === 2 && (
        <GoalSelectionStep
          goals={goals}
          selectedGoal={selectedGoal}
          onSelect={setSelectedGoal}
          onNext={() => setStep(3)}
          onBack={() => setStep(1)}
        />
      )}
      
      {step === 3 && selectedGoal && (
        <DetailSettingsStep
          selectedGoal={selectedGoal}
          currentLevel={currentLevel}
          dailyMinutes={dailyMinutes}
          onLevelChange={setCurrentLevel}
          onMinutesChange={setDailyMinutes}
          onGenerate={handleGenerateCurriculum}
          onBack={() => setStep(2)}
        />
      )}
      
      {step === 4 && <GeneratingStep />}
      
      {step === 5 && generatedCurriculum && (
        <PreviewStep
          curriculum={generatedCurriculum}
          onStart={handleStartLearning}
        />
      )}
    </>
  );
};

export default OnboardingPage;
