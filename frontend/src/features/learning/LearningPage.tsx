import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { BookOpen, Play, Star, Clock, Target, RefreshCw, AlertCircle, ChevronRight } from 'lucide-react';
import { subjectsApi } from '../../shared/services/apiClient';
import useAuthStore from '../../shared/hooks/useAuthStore';

export default function LearningPage() {
  const { user } = useAuthStore();
  const navigate = useNavigate();
  const [selectedSubject, setSelectedSubject] = useState<string | null>(null);

  // 실제 과목 데이터 조회
  const { data: subjects, isLoading, error, refetch } = useQuery({
    queryKey: ['subjects'],
    queryFn: subjectsApi.getAll,
    enabled: !!user,
    staleTime: 10 * 60 * 1000, // 10분
  });

  // 선택된 과목의 토픽 조회
  const { data: topics } = useQuery({
    queryKey: ['topics', selectedSubject],
    queryFn: () => subjectsApi.getSubjectTopics(selectedSubject!),
    enabled: !!selectedSubject,
    staleTime: 10 * 60 * 1000,
  });

  if (isLoading) {
    return (
      <div className="max-w-7xl mx-auto">
        <div className="flex items-center justify-center h-64">
          <div className="text-center">
            <RefreshCw className="w-8 h-8 animate-spin mx-auto mb-4 text-blue-600" />
            <p className="text-gray-600">과목 데이터를 불러오고 있습니다...</p>
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
            <h3 className="text-red-800 font-medium">과목 데이터 로드 실패</h3>
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

  const activeSubjects = Array.isArray(subjects) ? subjects.filter(s => s.is_active) : [];

  // 난이도별 색상 매핑
  const getDifficultyColor = (level: string) => {
    switch (level?.toLowerCase()) {
      case 'beginner': return 'bg-green-100 text-green-800';
      case 'intermediate': return 'bg-yellow-100 text-yellow-800';
      case 'advanced': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  // 난이도별 한국어 매핑
  const getDifficultyLabel = (level: string) => {
    switch (level?.toLowerCase()) {
      case 'beginner': return '초급';
      case 'intermediate': return '중급';
      case 'advanced': return '고급';
      default: return '기본';
    }
  };

  return (
    <div className="max-w-7xl mx-auto">
      {/* 헤더 */}
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900 flex items-center">
          <BookOpen className="w-8 h-8 text-blue-600 mr-3" />
          📚 학습하기
        </h1>
        <p className="text-gray-600 mt-1">
          실제 과목 데이터로 구성된 학습 과정입니다. 단계별로 체계적인 학습을 진행하세요.
        </p>
      </div>

      {/* 과목 없음 안내 */}
      {activeSubjects.length === 0 && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-8">
          <div className="text-center">
            <BookOpen className="w-16 h-16 text-blue-600 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-blue-900 mb-3">활성화된 과목이 없습니다</h3>
            <p className="text-blue-800 mb-6">
              관리자에게 문의하여 학습 과목을 활성화해주세요.
            </p>
            <button 
              onClick={() => refetch()}
              className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 font-medium"
            >
              새로고침
            </button>
          </div>
        </div>
      )}

      {/* 과목 목록 */}
      {activeSubjects.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
          {activeSubjects.map((subject) => (
            <div 
              key={subject.id} 
              className={`bg-white rounded-lg p-6 shadow-sm border transition-all duration-200 cursor-pointer hover:shadow-md ${
                selectedSubject === subject.key ? 'border-blue-500 ring-2 ring-blue-200' : 'border-gray-200'
              }`}
              onClick={() => setSelectedSubject(selectedSubject === subject.key ? null : subject.key)}
            >
              {/* 과목 헤더 */}
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center">
                  <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mr-3">
                    <span className="text-2xl">{subject.icon_name || '📚'}</span>
                  </div>
                  <div>
                    <h3 className="font-semibold text-gray-900 text-lg">
                      {subject.name}
                    </h3>
                    <div className="flex items-center space-x-2 mt-1">
                      <span className={`text-xs px-2 py-1 rounded-full ${getDifficultyColor(subject.difficulty_level || '')}`}>
                        {getDifficultyLabel(subject.difficulty_level || '')}
                      </span>
                      {subject.estimated_duration && (
                        <span className="text-xs text-gray-500 flex items-center">
                          <Clock className="w-3 h-3 mr-1" />
                          {subject.estimated_duration}
                        </span>
                      )}
                    </div>
                  </div>
                </div>
                <ChevronRight className={`w-5 h-5 text-gray-400 transition-transform ${
                  selectedSubject === subject.key ? 'rotate-90' : ''
                }`} />
              </div>

              {/* 과목 설명 */}
              {subject.description && (
                <p className="text-gray-600 text-sm mb-4 line-clamp-2">
                  {subject.description}
                </p>
              )}

              {/* 과목 통계 */}
              <div className="flex items-center justify-between text-sm text-gray-500">
                <span className="flex items-center">
                  <Target className="w-4 h-4 mr-1" />
                  토픽 {subject.topic_count || 0}개
                </span>
                <span className="text-blue-600 font-medium">
                  {selectedSubject === subject.key ? '접기' : '자세히 보기'}
                </span>
              </div>

              {/* 학습 시작 버튼 */}
              <div className="mt-4 pt-4 border-t border-gray-100">
                <button 
                  className="w-full bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700 transition-colors flex items-center justify-center"
                  onClick={(e) => {
                    e.stopPropagation();
                    // 학습 문제 페이지로 이동
                    navigate(`/learning/questions/${subject.key}`, { 
                      state: { subject: subject } 
                    });
                  }}
                >
                  <Play className="w-4 h-4 mr-2" />
                  학습 시작
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* 선택된 과목의 토픽 상세 */}
      {selectedSubject && topics && (
        <div className="bg-white rounded-lg p-6 shadow-sm border border-gray-200">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">
            📝 {activeSubjects.find(s => s.key === selectedSubject)?.name} - 학습 토픽
          </h2>
          
          {topics.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {topics.map((topic, index) => (
                <div key={topic.id} className="bg-gray-50 rounded-lg p-4 hover:bg-gray-100 transition-colors">
                  <div className="flex items-start justify-between mb-2">
                    <h4 className="font-medium text-gray-900">{topic.name}</h4>
                    {topic.is_core && (
                      <Star className="w-4 h-4 text-yellow-500" title="핵심 토픽" />
                    )}
                  </div>
                  
                  {topic.description && (
                    <p className="text-sm text-gray-600 mb-3">{topic.description}</p>
                  )}
                  
                  <div className="flex items-center justify-between">
                    <span className="text-xs text-gray-500">
                      {index + 1}번째 토픽
                    </span>
                    <button 
                      className="text-blue-600 hover:text-blue-700 text-sm font-medium"
                      onClick={() => navigate(`/learning/topics/${topic.id}`, { 
                        state: { topic: topic, subject: activeSubjects.find(s => s.key === selectedSubject) } 
                      })}
                    >
                      학습하기
                    </button>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8">
              <BookOpen className="w-12 h-12 text-gray-300 mx-auto mb-3" />
              <p className="text-gray-500">이 과목에는 아직 토픽이 없습니다.</p>
            </div>
          )}
        </div>
      )}

      {/* AI 도우미 추천 */}
      <div className="mt-8 bg-gradient-to-r from-green-50 to-blue-50 border border-green-200 rounded-lg p-6">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-lg font-semibold text-green-900 mb-2">
              🤖 AI 맞춤 학습 추천
            </h3>
            <p className="text-green-800">
              AI가 당신의 수준에 맞는 학습 경로를 제안해드립니다. 
              개인화된 커리큘럼으로 더 효율적으로 학습하세요.
            </p>
          </div>
          <button 
            onClick={() => window.location.href = '/ai-assistant'}
            className="bg-green-600 text-white px-6 py-3 rounded-lg hover:bg-green-700 font-medium"
          >
            AI 도우미 사용하기
          </button>
        </div>
      </div>

      {/* 실제 데이터 연결 상태 */}
      <div className="mt-6 bg-green-50 border border-green-200 rounded-lg p-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center">
            <div className="w-2 h-2 bg-green-500 rounded-full mr-3"></div>
            <span className="text-green-800 font-medium">실제 동적 과목 시스템 연결됨</span>
            <span className="text-green-600 ml-2">
              - {activeSubjects.length}개 활성 과목
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