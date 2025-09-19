import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Bot, Sparkles, Target, MessageCircle, BookOpen, Brain, CheckCircle, TrendingUp, Zap, BarChart3 } from 'lucide-react';
import { subjectsApi } from '../../shared/services/apiClient';
import useAuthStore from '../../shared/hooks/useAuthStore';
import CurriculumGenerator from './components/CurriculumGenerator';
import AITeachingSession from './components/AITeachingSession';
import SmartQuestionGenerator from './components/SmartQuestionGenerator';
import AdaptiveLearningSystem from './components/AdaptiveLearningSystem';
import LearningAnalyticsDashboard from './components/LearningAnalyticsDashboard';
import AIFeedbackCenter from './components/AIFeedbackCenter';
import CodeAnalyzer from './components/CodeAnalyzer';
import LearningCounselor from './components/LearningCounselor';

export default function AIAssistantPage() {
  const { user } = useAuthStore();
  const [activeFeature, setActiveFeature] = useState<string | null>(null);

  // 과목 데이터 조회 (커리큘럼 생성에 필요)
  const { data: subjectsData } = useQuery({
    queryKey: ['subjects'],
    queryFn: subjectsApi.getAll,
    enabled: !!user,
  });

  const subjects = subjectsData?.subjects || [];

  return (
    <div className="max-w-7xl mx-auto">
      {/* 헤더 */}
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900 flex items-center">
          <Bot className="w-8 h-8 text-blue-600 mr-3" />
          🤖 AI 학습 도우미
        </h1>
        <p className="text-gray-600 mt-1">
          최신 AI 기술로 개인 맞춤 학습을 지원합니다. Phase 9 실제 API가 연결되어 있습니다.
        </p>
      </div>

      {/* 활성화된 기능이 있으면 해당 컴포넌트 표시 */}
      {activeFeature === 'curriculum' && (
        <div className="mb-8">
          <CurriculumGenerator 
            subjects={subjects}
            onBack={() => setActiveFeature(null)}
          />
        </div>
      )}

      {activeFeature === 'teaching' && (
        <div className="mb-8">
          <AITeachingSession 
            subjects={subjects}
            onBack={() => setActiveFeature(null)}
          />
        </div>
      )}

      {activeFeature === 'question_generator' && (
        <div className="mb-8">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-bold text-gray-900">스마트 문제 생성기</h2>
            <button 
              onClick={() => setActiveFeature(null)}
              className="text-gray-600 hover:text-gray-800"
            >
              ← 돌아가기
            </button>
          </div>
          <SmartQuestionGenerator />
        </div>
      )}

      {activeFeature === 'adaptive_learning' && (
        <div className="mb-8">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-bold text-gray-900">적응형 학습 시스템</h2>
            <button 
              onClick={() => setActiveFeature(null)}
              className="text-gray-600 hover:text-gray-800"
            >
              ← 돌아가기
            </button>
          </div>
          <AdaptiveLearningSystem />
        </div>
      )}

      {activeFeature === 'learning_analytics' && (
        <div className="mb-8">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-bold text-gray-900">고급 학습 분석</h2>
            <button 
              onClick={() => setActiveFeature(null)}
              className="text-gray-600 hover:text-gray-800"
            >
              ← 돌아가기
            </button>
          </div>
          <LearningAnalyticsDashboard />
        </div>
      )}

      {activeFeature === 'feedback_center' && (
        <div className="mb-8">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-bold text-gray-900">AI 피드백 센터</h2>
            <button 
              onClick={() => setActiveFeature(null)}
              className="text-gray-600 hover:text-gray-800"
            >
              ← 돌아가기
            </button>
          </div>
          <AIFeedbackCenter />
        </div>
      )}

      {activeFeature === 'code_analysis' && (
        <div className="mb-8">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-bold text-gray-900">AI 코드 분석</h2>
            <button 
              onClick={() => setActiveFeature(null)}
              className="text-gray-600 hover:text-gray-800"
            >
              ← 돌아가기
            </button>
          </div>
          <CodeAnalyzer />
        </div>
      )}

      {activeFeature === 'counseling' && (
        <div className="mb-8">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-bold text-gray-900">AI 학습 상담</h2>
            <button 
              onClick={() => setActiveFeature(null)}
              className="text-gray-600 hover:text-gray-800"
            >
              ← 돌아가기
            </button>
          </div>
          <LearningCounselor />
        </div>
      )}

      {/* 기본 AI 기능 카드들 */}
      {!activeFeature && (
        <>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
            {/* 맞춤 커리큘럼 생성 - Phase 9 실제 연결 */}
            <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-lg p-6 border border-blue-200">
              <div className="flex items-center mb-4">
                <div className="p-2 bg-blue-600 rounded-lg">
                  <BookOpen className="w-6 h-6 text-white" />
                </div>
                <h3 className="text-lg font-semibold text-blue-900 ml-3">
                  맞춤 커리큘럼 생성
                </h3>
              </div>
              <p className="text-blue-800 mb-4">
                당신의 목표와 현재 실력에 맞는 개인화된 학습 계획을 AI가 생성해드립니다.
              </p>
              <button 
                onClick={() => setActiveFeature('curriculum')}
                className="w-full bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
              >
                커리큘럼 만들기
              </button>
              <div className="flex items-center mt-2 text-xs text-blue-600">
                <CheckCircle className="w-3 h-3 mr-1" />
                Phase 9 API 연결 완료
              </div>
            </div>

            {/* 1:1 AI 강사 세션 - Phase 9 실제 연결 */}
            <div className="bg-gradient-to-br from-green-50 to-green-100 rounded-lg p-6 border border-green-200">
              <div className="flex items-center mb-4">
                <div className="p-2 bg-green-600 rounded-lg">
                  <MessageCircle className="w-6 h-6 text-white" />
                </div>
                <h3 className="text-lg font-semibold text-green-900 ml-3">
                  1:1 AI 강사 세션
                </h3>
              </div>
              <p className="text-green-800 mb-4">
                실시간으로 AI 강사와 대화하며 개념을 배우고 문제를 해결해보세요.
              </p>
              <button 
                onClick={() => setActiveFeature('teaching')}
                className="w-full bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition-colors"
              >
                AI 강사와 대화하기
              </button>
              <div className="flex items-center mt-2 text-xs text-green-600">
                <CheckCircle className="w-3 h-3 mr-1" />
                Phase 9 API 연결 완료
              </div>
            </div>

            {/* 스마트 코딩 피드백 - 기존 API 활용 */}
            <div className="bg-gradient-to-br from-purple-50 to-purple-100 rounded-lg p-6 border border-purple-200">
              <div className="flex items-center mb-4">
                <div className="p-2 bg-purple-600 rounded-lg">
                  <Brain className="w-6 h-6 text-white" />
                </div>
                <h3 className="text-lg font-semibold text-purple-900 ml-3">
                  스마트 코딩 피드백
                </h3>
              </div>
              <p className="text-purple-800 mb-4">
                코드를 분석하고 개선점을 제안하는 AI 코드 리뷰를 받아보세요.
              </p>
              <button 
                onClick={() => setActiveFeature('code_analysis')}
                className="w-full bg-purple-600 text-white px-4 py-2 rounded-lg hover:bg-purple-700 transition-colors"
              >
                코드 분석하기
              </button>
              <div className="flex items-center mt-2 text-xs text-purple-600">
                <CheckCircle className="w-3 h-3 mr-1" />
                기존 AI 기능 활용
              </div>
            </div>

            {/* AI 문제 생성 (Phase 10) - 구현 완료 */}
            <div className="bg-gradient-to-br from-orange-50 to-orange-100 rounded-lg p-6 border border-orange-200">
              <div className="flex items-center mb-4">
                <div className="p-2 bg-orange-600 rounded-lg">
                  <Sparkles className="w-6 h-6 text-white" />
                </div>
                <h3 className="text-lg font-semibold text-orange-900 ml-3">
                  스마트 문제 생성
                </h3>
              </div>
              <p className="text-orange-800 mb-4">
                AI가 학습 목표와 약점 분석을 통해 맞춤형 문제를 자동 생성해드립니다.
              </p>
              <button 
                onClick={() => setActiveFeature('question_generator')}
                className="w-full bg-orange-600 text-white px-4 py-2 rounded-lg hover:bg-orange-700 transition-colors"
              >
                문제 생성하기
              </button>
              <div className="flex items-center mt-2 text-xs text-orange-600">
                <CheckCircle className="w-3 h-3 mr-1" />
                Phase 10 새로운 기능
              </div>
            </div>

            {/* 학습 상담 & 동기부여 */}
            <div className="bg-gradient-to-br from-pink-50 to-pink-100 rounded-lg p-6 border border-pink-200">
              <div className="flex items-center mb-4">
                <div className="p-2 bg-pink-600 rounded-lg">
                  <Target className="w-6 h-6 text-white" />
                </div>
                <h3 className="text-lg font-semibold text-pink-900 ml-3">
                  학습 상담 & 동기부여
                </h3>
              </div>
              <p className="text-pink-800 mb-4">
                AI가 당신의 학습 패턴을 분석하여 맞춤형 조언과 격려를 제공합니다.
              </p>
              <button 
                onClick={() => setActiveFeature('counseling')}
                className="w-full bg-pink-600 text-white px-4 py-2 rounded-lg hover:bg-pink-700 transition-colors"
              >
                상담 받기
              </button>
              <div className="flex items-center mt-2 text-xs text-pink-600">
                <CheckCircle className="w-3 h-3 mr-1" />
                기존 기능 확장
              </div>
            </div>

            {/* 적응형 학습 시스템 (Phase 10) - 구현 완료 */}
            <div className="bg-gradient-to-br from-indigo-50 to-indigo-100 rounded-lg p-6 border border-indigo-200">
              <div className="flex items-center mb-4">
                <div className="p-2 bg-indigo-600 rounded-lg">
                  <TrendingUp className="w-6 h-6 text-white" />
                </div>
                <h3 className="text-lg font-semibold text-indigo-900 ml-3">
                  적응형 학습 시스템
                </h3>
              </div>
              <p className="text-indigo-800 mb-4">
                실시간 성과 분석으로 최적의 난이도를 자동 조절하고 개인화된 학습 경로를 제안합니다.
              </p>
              <button 
                onClick={() => setActiveFeature('adaptive_learning')}
                className="w-full bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700 transition-colors"
              >
                적응형 분석 시작하기
              </button>
              <div className="flex items-center mt-2 text-xs text-indigo-600">
                <CheckCircle className="w-3 h-3 mr-1" />
                Phase 10 새로운 기능
              </div>
            </div>

            {/* 고급 학습 분석 (Phase 10) - 새로 추가 */}
            <div className="bg-gradient-to-br from-emerald-50 to-emerald-100 rounded-lg p-6 border border-emerald-200">
              <div className="flex items-center mb-4">
                <div className="p-2 bg-emerald-600 rounded-lg">
                  <BarChart3 className="w-6 h-6 text-white" />
                </div>
                <h3 className="text-lg font-semibold text-emerald-900 ml-3">
                  고급 학습 분석
                </h3>
              </div>
              <p className="text-emerald-800 mb-4">
                AI가 학습 패턴을 심층 분석하여 예측 인사이트와 맞춤형 추천을 제공합니다.
              </p>
              <button 
                onClick={() => setActiveFeature('learning_analytics')}
                className="w-full bg-emerald-600 text-white px-4 py-2 rounded-lg hover:bg-emerald-700 transition-colors"
              >
                분석 대시보드 보기
              </button>
              <div className="flex items-center mt-2 text-xs text-emerald-600">
                <CheckCircle className="w-3 h-3 mr-1" />
                Phase 10 새로운 기능
              </div>
            </div>

            {/* AI 피드백 센터 (Phase 10) - 새로 추가 */}
            <div className="bg-gradient-to-br from-cyan-50 to-cyan-100 rounded-lg p-6 border border-cyan-200">
              <div className="flex items-center mb-4">
                <div className="p-2 bg-cyan-600 rounded-lg">
                  <MessageCircle className="w-6 h-6 text-white" />
                </div>
                <h3 className="text-lg font-semibold text-cyan-900 ml-3">
                  AI 피드백 센터
                </h3>
              </div>
              <p className="text-cyan-800 mb-4">
                모든 AI 상호작용에 대한 피드백을 통합 관리하고 개선점을 파악합니다.
              </p>
              <button 
                onClick={() => setActiveFeature('feedback_center')}
                className="w-full bg-cyan-600 text-white px-4 py-2 rounded-lg hover:bg-cyan-700 transition-colors"
              >
                피드백 센터 열기
              </button>
              <div className="flex items-center mt-2 text-xs text-cyan-600">
                <CheckCircle className="w-3 h-3 mr-1" />
                Phase 10 새로운 기능
              </div>
            </div>
          </div>

          {/* Phase 9-10 구현 상태 - API 연결 현황 */}
          <div className="bg-white rounded-lg p-6 shadow-sm border border-gray-200 mb-8">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">
              🚀 Phase 9-10 시스템 현황
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              <div className="flex items-center justify-between p-3 bg-green-50 rounded-lg">
                <span className="font-medium text-green-900">AI 커리큘럼</span>
                <span className="text-green-600 font-bold">✅ Phase 9</span>
              </div>
              <div className="flex items-center justify-between p-3 bg-green-50 rounded-lg">
                <span className="font-medium text-green-900">AI 강사 세션</span>
                <span className="text-green-600 font-bold">✅ Phase 9</span>
              </div>
              <div className="flex items-center justify-between p-3 bg-blue-50 rounded-lg">
                <span className="font-medium text-blue-900">스마트 문제 생성</span>
                <span className="text-blue-600 font-bold">🆕 Phase 10</span>
              </div>
              <div className="flex items-center justify-between p-3 bg-blue-50 rounded-lg">
                <span className="font-medium text-blue-900">적응형 학습</span>
                <span className="text-blue-600 font-bold">🆕 Phase 10</span>
              </div>
              <div className="flex items-center justify-between p-3 bg-green-50 rounded-lg">
                <span className="font-medium text-green-900">고급 학습 분석</span>
                <span className="text-green-600 font-bold">✅ Phase 10</span>
              </div>
              <div className="flex items-center justify-between p-3 bg-green-50 rounded-lg">
                <span className="font-medium text-green-900">AI 피드백 센터</span>
                <span className="text-green-600 font-bold">✅ Phase 10</span>
              </div>
              <div className="flex items-center justify-between p-3 bg-cyan-50 rounded-lg">
                <span className="font-medium text-cyan-900">관리자 시스템</span>
                <span className="text-cyan-600 font-bold">✅ 완료</span>
              </div>
              <div className="flex items-center justify-between p-3 bg-purple-50 rounded-lg">
                <span className="font-medium text-purple-900">백엔드 API</span>
                <span className="text-purple-600 font-bold">✅ 전체 연결</span>
              </div>
            </div>
          </div>

          {/* API 엔드포인트 정보 */}
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
            <h2 className="text-lg font-semibold text-blue-900 mb-4">
              📡 Phase 9-10 API 엔드포인트
            </h2>
            
            <div className="mb-4">
              <h3 className="font-medium text-blue-800 mb-2">Phase 9 - AI 기본 기능</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-sm">
                <div className="bg-white rounded p-3">
                  <span className="font-mono text-blue-700">POST /api/v1/ai-curriculum/generate</span>
                  <p className="text-gray-600 text-xs mt-1">커리큘럼 생성</p>
                </div>
                <div className="bg-white rounded p-3">
                  <span className="font-mono text-blue-700">GET /api/v1/ai-curriculum/[ID]</span>
                  <p className="text-gray-600 text-xs mt-1">커리큘럼 조회</p>
                </div>
                <div className="bg-white rounded p-3">
                  <span className="font-mono text-blue-700">POST /api/v1/ai-teaching/start-session</span>
                  <p className="text-gray-600 text-xs mt-1">교육 세션 시작</p>
                </div>
                <div className="bg-white rounded p-3">
                  <span className="font-mono text-blue-700">POST /api/v1/ai-teaching/message</span>
                  <p className="text-gray-600 text-xs mt-1">AI 강사 대화</p>
                </div>
              </div>
            </div>

            <div>
              <h3 className="font-medium text-blue-800 mb-2">Phase 10 - 고급 AI 기능</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-sm">
                <div className="bg-white rounded p-3">
                  <span className="font-mono text-blue-700">POST /api/v1/ai-questions/generate</span>
                  <p className="text-gray-600 text-xs mt-1">스마트 문제 생성</p>
                </div>
                <div className="bg-white rounded p-3">
                  <span className="font-mono text-blue-700">POST /api/v1/ai-questions/adaptive</span>
                  <p className="text-gray-600 text-xs mt-1">적응형 문제 생성</p>
                </div>
                <div className="bg-white rounded p-3">
                  <span className="font-mono text-blue-700">GET /api/v1/ai-questions/analytics</span>
                  <p className="text-gray-600 text-xs mt-1">문제 생성 분석</p>
                </div>
                <div className="bg-white rounded p-3">
                  <span className="font-mono text-blue-700">POST /api/v1/ai-questions/[ID]/review</span>
                  <p className="text-gray-600 text-xs mt-1">문제 검토 시스템</p>
                </div>
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );
}