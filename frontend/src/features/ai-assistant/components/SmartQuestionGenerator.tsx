import React, { useState } from 'react';
import { useMutation, useQuery } from '@tanstack/react-query';
import { Brain, Zap, Target, Settings, PlayCircle, CheckCircle, AlertCircle, Lightbulb } from 'lucide-react';
import { toast } from 'react-hot-toast';
import { subjectsApi } from '../../../shared/services/apiClient';
import useAuthStore from '../../../shared/hooks/useAuthStore';

// Phase 10 API 타입 정의
interface QuestionGenerationRequest {
  subject_key: string;
  topic: string;
  question_type: string;
  difficulty_level: string;
  count: number;
  learning_goals?: string[];
  context?: string;
}

interface GeneratedQuestion {
  id: string;
  question_text: string;
  question_type: string;
  difficulty_level: string;
  options?: string[];
  correct_answer: string;
  explanation: string;
  hints?: string[];
  tags?: string[];
  estimated_time?: number;
  learning_objective?: string;
  quality_score: number;
  generated_at: string;
  status: string;
}

interface QuestionGenerationResponse {
  success: boolean;
  message: string;
  questions: GeneratedQuestion[];
  generation_info: {
    total_generated: number;
    avg_quality_score: number;
    estimated_total_time: number;
    ready_questions: number;
    needs_review: number;
  };
}

const SmartQuestionGenerator: React.FC = () => {
  const { user } = useAuthStore();
  const [selectedSubject, setSelectedSubject] = useState<string>('');
  const [topic, setTopic] = useState<string>('');
  const [questionType, setQuestionType] = useState<string>('multiple_choice');
  const [difficultyLevel, setDifficultyLevel] = useState<string>('intermediate');
  const [questionCount, setQuestionCount] = useState<number>(3);
  const [learningGoals, setLearningGoals] = useState<string[]>(['']);
  const [context, setContext] = useState<string>('');
  const [generatedQuestions, setGeneratedQuestions] = useState<GeneratedQuestion[]>([]);
  const [selectedQuestionId, setSelectedQuestionId] = useState<string | null>(null);

  // 과목 데이터 조회
  const { data: subjects } = useQuery({
    queryKey: ['subjects'],
    queryFn: subjectsApi.getAll,
    enabled: !!user,
  });

  // Phase 10 API 호출 함수 (임시 구현)
  const generateQuestionsAPI = async (request: QuestionGenerationRequest): Promise<QuestionGenerationResponse> => {
    // 실제 API 호출 대신 임시 응답 생성
    await new Promise(resolve => setTimeout(resolve, 2000)); // 2초 지연
    
    const mockQuestions: GeneratedQuestion[] = Array.from({ length: request.count }, (_, i) => ({
      id: `gen_${Date.now()}_${i}`,
      question_text: `${request.topic}에 관한 ${request.question_type} 문제 ${i + 1}번입니다. 이 문제는 ${request.difficulty_level} 수준으로 설계되었습니다.`,
      question_type: request.question_type,
      difficulty_level: request.difficulty_level,
      options: request.question_type === 'multiple_choice' ? 
        ['선택지 1', '선택지 2', '선택지 3', '선택지 4'] : undefined,
      correct_answer: request.question_type === 'multiple_choice' ? '선택지 1' : '모범 답안',
      explanation: `이 문제의 핵심은 ${request.topic}의 기본 개념을 이해하는 것입니다.`,
      hints: ['힌트 1: 기본 개념부터 생각해보세요', '힌트 2: 예시를 들어 생각해보세요'],
      tags: [request.topic, request.difficulty_level],
      estimated_time: request.question_type === 'coding' ? 15 : 5,
      learning_objective: `${request.topic}의 핵심 개념 이해`,
      quality_score: 7.5 + Math.random() * 2, // 7.5-9.5 랜덤
      generated_at: new Date().toISOString(),
      status: Math.random() > 0.3 ? 'ready' : 'needs_review'
    }));

    return {
      success: true,
      message: `${request.count}개의 문제가 생성되었습니다.`,
      questions: mockQuestions,
      generation_info: {
        total_generated: mockQuestions.length,
        avg_quality_score: mockQuestions.reduce((sum, q) => sum + q.quality_score, 0) / mockQuestions.length,
        estimated_total_time: mockQuestions.reduce((sum, q) => sum + (q.estimated_time || 5), 0),
        ready_questions: mockQuestions.filter(q => q.status === 'ready').length,
        needs_review: mockQuestions.filter(q => q.status === 'needs_review').length
      }
    };
  };

  // 문제 생성 뮤테이션
  const { mutate: generateQuestions, isPending: isGenerating } = useMutation<
    QuestionGenerationResponse,
    Error,
    QuestionGenerationRequest
  >({
    mutationFn: generateQuestionsAPI,
    onSuccess: (data) => {
      setGeneratedQuestions(data.questions);
      toast.success(data.message);
    },
    onError: (error) => {
      toast.error(`문제 생성 실패: ${error.message}`);
    },
  });

  const handleGenerateQuestions = () => {
    if (!selectedSubject || !topic.trim()) {
      toast.error('과목과 토픽을 입력해주세요.');
      return;
    }

    const request: QuestionGenerationRequest = {
      subject_key: selectedSubject,
      topic: topic.trim(),
      question_type: questionType,
      difficulty_level: difficultyLevel,
      count: questionCount,
      learning_goals: learningGoals.filter(goal => goal.trim()),
      context: context.trim() || undefined
    };

    generateQuestions(request);
  };

  const addLearningGoal = () => {
    setLearningGoals([...learningGoals, '']);
  };

  const updateLearningGoal = (index: number, value: string) => {
    const updated = [...learningGoals];
    updated[index] = value;
    setLearningGoals(updated);
  };

  const removeLearningGoal = (index: number) => {
    setLearningGoals(learningGoals.filter((_, i) => i !== index));
  };

  const getQualityColor = (score: number) => {
    if (score >= 8.5) return 'text-green-600 bg-green-100';
    if (score >= 7.0) return 'text-yellow-600 bg-yellow-100';
    return 'text-red-600 bg-red-100';
  };

  const getStatusColor = (status: string) => {
    if (status === 'ready') return 'text-green-600 bg-green-100';
    return 'text-orange-600 bg-orange-100';
  };

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      {/* 헤더 */}
      <div className="bg-gradient-to-r from-purple-50 to-blue-50 border border-purple-200 rounded-lg p-6">
        <div className="flex items-center mb-4">
          <Brain className="w-8 h-8 text-purple-600 mr-3" />
          <div>
            <h2 className="text-2xl font-bold text-purple-900">🧠 스마트 문제 생성기</h2>
            <p className="text-purple-700">AI가 맞춤형 문제를 자동으로 생성해드립니다</p>
          </div>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
          <div className="bg-white rounded p-3">
            <span className="font-medium text-purple-700">✨ 개인화 문제</span>
            <p className="text-gray-600">학습 목표와 약점 기반</p>
          </div>
          <div className="bg-white rounded p-3">
            <span className="font-medium text-purple-700">🎯 적응형 난이도</span>
            <p className="text-gray-600">실력에 맞는 도전</p>
          </div>
          <div className="bg-white rounded p-3">
            <span className="font-medium text-purple-700">📊 품질 보장</span>
            <p className="text-gray-600">AI 품질 검증 시스템</p>
          </div>
        </div>
      </div>

      {/* 문제 생성 설정 */}
      <div className="bg-white rounded-lg p-6 shadow-sm border border-gray-200">
        <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
          <Settings className="w-5 h-5 mr-2 text-blue-600" />
          문제 생성 설정
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* 기본 설정 */}
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                과목 선택
              </label>
              <select
                value={selectedSubject}
                onChange={(e) => setSelectedSubject(e.target.value)}
                className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              >
                <option value="">과목을 선택하세요</option>
                {subjects?.map((subject) => (
                  <option key={subject.key} value={subject.key}>
                    {subject.name}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                토픽
              </label>
              <input
                type="text"
                value={topic}
                onChange={(e) => setTopic(e.target.value)}
                placeholder="예: 변수와 자료형, 조건문, 함수 등"
                className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  문제 유형
                </label>
                <select
                  value={questionType}
                  onChange={(e) => setQuestionType(e.target.value)}
                  className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                >
                  <option value="multiple_choice">객관식</option>
                  <option value="coding">코딩 문제</option>
                  <option value="short_answer">단답형</option>
                  <option value="essay">서술형</option>
                  <option value="fill_blank">빈칸 채우기</option>
                  <option value="true_false">참/거짓</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  난이도
                </label>
                <select
                  value={difficultyLevel}
                  onChange={(e) => setDifficultyLevel(e.target.value)}
                  className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                >
                  <option value="beginner">초급</option>
                  <option value="intermediate">중급</option>
                  <option value="advanced">고급</option>
                  <option value="expert">전문가</option>
                </select>
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                생성할 문제 수: {questionCount}개
              </label>
              <input
                type="range"
                min="1"
                max="10"
                value={questionCount}
                onChange={(e) => setQuestionCount(parseInt(e.target.value))}
                className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
              />
              <div className="flex justify-between text-xs text-gray-500 mt-1">
                <span>1개</span>
                <span>5개</span>
                <span>10개</span>
              </div>
            </div>
          </div>

          {/* 고급 설정 */}
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                학습 목표 (선택사항)
              </label>
              <div className="space-y-2">
                {learningGoals.map((goal, index) => (
                  <div key={index} className="flex items-center space-x-2">
                    <input
                      type="text"
                      value={goal}
                      onChange={(e) => updateLearningGoal(index, e.target.value)}
                      placeholder={`학습 목표 ${index + 1}`}
                      className="flex-1 p-2 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500"
                    />
                    {learningGoals.length > 1 && (
                      <button
                        onClick={() => removeLearningGoal(index)}
                        className="p-2 text-red-600 hover:bg-red-50 rounded"
                      >
                        ×
                      </button>
                    )}
                  </div>
                ))}
                <button
                  onClick={addLearningGoal}
                  className="text-blue-600 hover:text-blue-700 text-sm font-medium"
                >
                  + 학습 목표 추가
                </button>
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                추가 컨텍스트 (선택사항)
              </label>
              <textarea
                value={context}
                onChange={(e) => setContext(e.target.value)}
                placeholder="특별한 요구사항이나 문제 스타일을 설명해주세요..."
                rows={4}
                className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>
        </div>

        {/* 생성 버튼 */}
        <div className="mt-6 pt-6 border-t border-gray-200">
          <button
            onClick={handleGenerateQuestions}
            disabled={isGenerating || !selectedSubject || !topic.trim()}
            className={`w-full md:w-auto px-8 py-3 rounded-lg font-medium flex items-center justify-center ${
              isGenerating || !selectedSubject || !topic.trim()
                ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                : 'bg-gradient-to-r from-purple-600 to-blue-600 text-white hover:from-purple-700 hover:to-blue-700'
            }`}
          >
            {isGenerating ? (
              <>
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                AI 문제 생성 중...
              </>
            ) : (
              <>
                <Zap className="w-5 h-5 mr-2" />
                스마트 문제 생성
              </>
            )}
          </button>
        </div>
      </div>

      {/* 생성된 문제들 */}
      {generatedQuestions.length > 0 && (
        <div className="bg-white rounded-lg p-6 shadow-sm border border-gray-200">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-lg font-semibold text-gray-900 flex items-center">
              <Target className="w-5 h-5 mr-2 text-green-600" />
              생성된 문제 ({generatedQuestions.length}개)
            </h3>
            
            {/* 품질 요약 */}
            <div className="text-sm text-gray-600">
              평균 품질: <span className="font-medium text-blue-600">
                {(generatedQuestions.reduce((sum, q) => sum + q.quality_score, 0) / generatedQuestions.length).toFixed(1)}점
              </span>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* 문제 목록 */}
            <div className="space-y-4">
              {generatedQuestions.map((question, index) => (
                <div
                  key={question.id}
                  className={`border rounded-lg p-4 cursor-pointer transition-all ${
                    selectedQuestionId === question.id
                      ? 'border-blue-500 bg-blue-50'
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                  onClick={() => setSelectedQuestionId(question.id)}
                >
                  <div className="flex items-start justify-between mb-3">
                    <h4 className="font-medium text-gray-900">문제 {index + 1}</h4>
                    <div className="flex items-center space-x-2">
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${getQualityColor(question.quality_score)}`}>
                        {question.quality_score.toFixed(1)}점
                      </span>
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(question.status)}`}>
                        {question.status === 'ready' ? '준비완료' : '검토필요'}
                      </span>
                    </div>
                  </div>
                  
                  <p className="text-gray-700 text-sm line-clamp-2 mb-2">
                    {question.question_text}
                  </p>
                  
                  <div className="flex items-center justify-between text-xs text-gray-500">
                    <span>{question.question_type} · {question.difficulty_level}</span>
                    <span>예상 소요시간: {question.estimated_time}분</span>
                  </div>
                </div>
              ))}
            </div>

            {/* 선택된 문제 상세 */}
            <div className="bg-gray-50 rounded-lg p-4">
              {selectedQuestionId ? (
                (() => {
                  const selectedQuestion = generatedQuestions.find(q => q.id === selectedQuestionId);
                  if (!selectedQuestion) return null;

                  return (
                    <div className="space-y-4">
                      <div className="flex items-center justify-between">
                        <h4 className="font-semibold text-gray-900">문제 상세보기</h4>
                        <div className="flex items-center space-x-2">
                          {selectedQuestion.status === 'ready' ? (
                            <CheckCircle className="w-5 h-5 text-green-600" />
                          ) : (
                            <AlertCircle className="w-5 h-5 text-orange-600" />
                          )}
                        </div>
                      </div>

                      <div className="bg-white rounded p-4 border">
                        <p className="font-medium text-gray-900 mb-3">
                          {selectedQuestion.question_text}
                        </p>

                        {selectedQuestion.options && (
                          <div className="space-y-2 mb-4">
                            {selectedQuestion.options.map((option, idx) => (
                              <div key={idx} className="flex items-center space-x-2">
                                <span className="w-6 h-6 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center text-sm font-medium">
                                  {String.fromCharCode(65 + idx)}
                                </span>
                                <span className="text-gray-700">{option}</span>
                              </div>
                            ))}
                          </div>
                        )}

                        <div className="border-t pt-3">
                          <p className="text-sm font-medium text-gray-700 mb-1">정답:</p>
                          <p className="text-sm text-gray-600 mb-3">{selectedQuestion.correct_answer}</p>
                          
                          <p className="text-sm font-medium text-gray-700 mb-1">해설:</p>
                          <p className="text-sm text-gray-600">{selectedQuestion.explanation}</p>
                        </div>

                        {selectedQuestion.hints && selectedQuestion.hints.length > 0 && (
                          <div className="border-t pt-3 mt-3">
                            <p className="text-sm font-medium text-gray-700 mb-2 flex items-center">
                              <Lightbulb className="w-4 h-4 mr-1" />
                              힌트:
                            </p>
                            <ul className="text-sm text-gray-600 space-y-1">
                              {selectedQuestion.hints.map((hint, idx) => (
                                <li key={idx} className="flex items-start">
                                  <span className="text-gray-400 mr-2">•</span>
                                  <span>{hint}</span>
                                </li>
                              ))}
                            </ul>
                          </div>
                        )}
                      </div>

                      <div className="flex space-x-2">
                        <button className="flex-1 bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700 flex items-center justify-center">
                          <PlayCircle className="w-4 h-4 mr-2" />
                          문제 풀어보기
                        </button>
                        <button className="flex-1 bg-gray-200 text-gray-700 py-2 px-4 rounded-lg hover:bg-gray-300">
                          문제 수정하기
                        </button>
                      </div>
                    </div>
                  );
                })()
              ) : (
                <div className="text-center text-gray-500 py-8">
                  <Target className="w-12 h-12 text-gray-300 mx-auto mb-3" />
                  <p>문제를 선택하면 상세 내용을 볼 수 있습니다</p>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Phase 10 기능 안내 */}
      <div className="bg-gradient-to-r from-green-50 to-purple-50 border border-green-200 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-green-900 mb-3">
          🚀 Phase 10 - 스마트 문제 생성 시스템
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
          <div>
            <h4 className="font-medium text-green-800 mb-2">✨ 새로운 기능</h4>
            <ul className="text-green-700 space-y-1">
              <li>• AI 기반 맞춤형 문제 자동 생성</li>
              <li>• 적응형 난이도 조절 시스템</li>
              <li>• 실시간 품질 검증 및 개선</li>
              <li>• 개인화된 학습 목표 반영</li>
            </ul>
          </div>
          <div>
            <h4 className="font-medium text-green-800 mb-2">🎯 예정 기능</h4>
            <ul className="text-green-700 space-y-1">
              <li>• 관리자 문제 검토 시스템</li>
              <li>• 학습 패턴 기반 추천</li>
              <li>• 동급생 비교 분석</li>
              <li>• 고급 학습 분석 리포트</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SmartQuestionGenerator;
