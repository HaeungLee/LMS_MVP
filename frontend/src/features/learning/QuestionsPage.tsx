import React, { useState, useEffect } from 'react';
import { useParams, useLocation, useNavigate } from 'react-router-dom';
import { useQuery, useMutation } from '@tanstack/react-query';
import { ArrowLeft, Play, CheckCircle, AlertCircle, Brain, Clock, Target } from 'lucide-react';
import { toast } from 'react-hot-toast';
import { subjectsApi, questionsApi } from '../../shared/services/apiClient';
import useAuthStore from '../../shared/hooks/useAuthStore';

interface Question {
  id: number;
  text: string;
  options?: string[];
  correct_answer?: string;
  question_type: string;
  difficulty_level: string;
}

export default function QuestionsPage() {
  const { subjectKey } = useParams<{ subjectKey: string }>();
  const location = useLocation();
  const navigate = useNavigate();
  const { user } = useAuthStore();
  
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [selectedAnswer, setSelectedAnswer] = useState<string>('');
  const [showResult, setShowResult] = useState(false);
  const [score, setScore] = useState(0);
  const [answers, setAnswers] = useState<{ [key: number]: string }>({});

  const subject = location.state?.subject;

  // AI 문제 생성 뮤테이션
  const { data: questions, isLoading, refetch: generateQuestions } = useQuery({
    queryKey: ['ai-questions', subjectKey],
    queryFn: async () => {
      if (!subjectKey) return [];
      
      try {
        // AI 문제 생성 API 호출
        const response = await questionsApi.generateQuestions({
          subject_key: subjectKey,
          topic: subject?.name || subjectKey,
          difficulty_level: 'beginner',
          count: 5,
          question_type: 'multiple_choice'
        });
        
        if (response.success && response.questions.length > 0) {
          // API 응답을 컴포넌트 형식으로 변환
          return response.questions.map((q, index) => ({
            id: index + 1,
            text: q.question_text,
            options: q.options || ['옵션 1', '옵션 2', '옵션 3', '옵션 4'],
            correct_answer: q.correct_answer,
            question_type: q.question_type,
            difficulty_level: q.difficulty_level,
            explanation: q.explanation,
            hints: q.hints
          }));
        }
      } catch (error) {
        console.error('AI 문제 생성 실패:', error);
      }
      
      // 폴백: 기본 문제 사용
      return generateDefaultQuestions(subjectKey);
    },
    enabled: !!subjectKey,
  });

  // 기본 문제 생성 함수
  const generateDefaultQuestions = (subject: string): Question[] => {
    const questionTemplates = {
      python: [
        {
          id: 1,
          text: "Python에서 변수를 선언하는 올바른 방법은?",
          options: ["var x = 5", "let x = 5", "x = 5", "int x = 5"],
          correct_answer: "x = 5",
          question_type: "multiple_choice",
          difficulty_level: "beginner"
        },
        {
          id: 2,
          text: "Python에서 리스트를 만드는 올바른 방법은?",
          options: ["array = {1, 2, 3}", "array = [1, 2, 3]", "array = (1, 2, 3)", "array = <1, 2, 3>"],
          correct_answer: "array = [1, 2, 3]",
          question_type: "multiple_choice",
          difficulty_level: "beginner"
        },
        {
          id: 3,
          text: "다음 중 Python의 반복문이 아닌 것은?",
          options: ["for", "while", "do-while", "for-in"],
          correct_answer: "do-while",
          question_type: "multiple_choice",
          difficulty_level: "intermediate"
        }
      ],
      javascript: [
        {
          id: 1,
          text: "JavaScript에서 변수를 선언하는 최신 방법은?",
          options: ["var x = 5", "let x = 5", "x = 5", "declare x = 5"],
          correct_answer: "let x = 5",
          question_type: "multiple_choice",
          difficulty_level: "beginner"
        },
        {
          id: 2,
          text: "JavaScript에서 함수를 선언하는 방법이 아닌 것은?",
          options: ["function myFunc() {}", "const myFunc = () => {}", "const myFunc = function() {}", "def myFunc() {}"],
          correct_answer: "def myFunc() {}",
          question_type: "multiple_choice",
          difficulty_level: "intermediate"
        }
      ],
      react: [
        {
          id: 1,
          text: "React에서 상태를 관리하기 위해 사용하는 Hook은?",
          options: ["useEffect", "useState", "useContext", "useReducer"],
          correct_answer: "useState",
          question_type: "multiple_choice",
          difficulty_level: "beginner"
        },
        {
          id: 2,
          text: "React 컴포넌트에서 렌더링될 때마다 실행되는 Hook은?",
          options: ["useState", "useEffect", "useMemo", "useCallback"],
          correct_answer: "useEffect",
          question_type: "multiple_choice",
          difficulty_level: "intermediate"
        }
      ]
    };

    return questionTemplates[subject.toLowerCase() as keyof typeof questionTemplates] || [
      {
        id: 1,
        text: `${subject}에 대한 기본 질문입니다. 이 기술의 주요 특징은 무엇인가요?`,
        options: ["옵션 1", "옵션 2", "옵션 3", "옵션 4"],
        correct_answer: "옵션 1",
        question_type: "multiple_choice",
        difficulty_level: "beginner"
      }
    ];
  };

  const currentQuestion = questions?.[currentQuestionIndex];

  const handleAnswerSelect = (answer: string) => {
    setSelectedAnswer(answer);
  };

  const handleSubmitAnswer = () => {
    if (!selectedAnswer) {
      toast.error('답안을 선택해주세요');
      return;
    }

    const isCorrect = selectedAnswer === currentQuestion?.correct_answer;
    setAnswers(prev => ({ ...prev, [currentQuestionIndex]: selectedAnswer }));
    
    if (isCorrect) {
      setScore(prev => prev + 1);
      toast.success('정답입니다!');
    } else {
      toast.error(`오답입니다. 정답: ${currentQuestion?.correct_answer}`);
    }

    setShowResult(true);
  };

  const handleNextQuestion = () => {
    if (currentQuestionIndex < (questions?.length || 0) - 1) {
      setCurrentQuestionIndex(prev => prev + 1);
      setSelectedAnswer('');
      setShowResult(false);
    } else {
      // 마지막 문제 완료
      showFinalResult();
    }
  };

  const showFinalResult = () => {
    const finalScore = score;
    const totalQuestions = questions?.length || 0;
    const percentage = ((finalScore / totalQuestions) * 100).toFixed(1);
    
    toast.success(`학습 완료! 점수: ${finalScore}/${totalQuestions} (${percentage}%)`);
    
    // 결과 페이지로 이동하거나 학습 완료 처리
    setTimeout(() => {
      navigate('/learning', { 
        state: { 
          completedSubject: subjectKey, 
          score: finalScore, 
          total: totalQuestions 
        } 
      });
    }, 2000);
  };

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty?.toLowerCase()) {
      case 'beginner': return 'bg-green-100 text-green-800';
      case 'intermediate': return 'bg-yellow-100 text-yellow-800';
      case 'advanced': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getDifficultyLabel = (difficulty: string) => {
    switch (difficulty?.toLowerCase()) {
      case 'beginner': return '초급';
      case 'intermediate': return '중급';
      case 'advanced': return '고급';
      default: return '기본';
    }
  };

  if (isLoading) {
    return (
      <div className="max-w-4xl mx-auto p-6">
        <div className="text-center py-12">
          <div className="flex items-center justify-center mb-4">
            <Brain className="w-12 h-12 text-blue-600 animate-pulse mr-3" />
            <div className="text-xl font-semibold text-gray-900">AI가 맞춤형 문제를 생성중입니다...</div>
          </div>
          <p className="text-gray-600 mb-6">
            {subject?.name || subjectKey} 과목에 최적화된 학습 문제를 만들고 있어요
          </p>
          <div className="animate-pulse">
            <div className="bg-white rounded-lg p-6 shadow-sm border border-gray-200 max-w-2xl mx-auto">
              <div className="h-6 bg-gray-200 rounded w-3/4 mb-4 mx-auto"></div>
              <div className="space-y-3">
                {[...Array(4)].map((_, i) => (
                  <div key={i} className="h-12 bg-gray-200 rounded"></div>
                ))}
              </div>
            </div>
          </div>
          <div className="mt-6 text-sm text-blue-600">
            ⚡ Phase 10 스마트 문제 생성 시스템 작동중
          </div>
        </div>
      </div>
    );
  }

  if (!questions || questions.length === 0) {
    return (
      <div className="max-w-4xl mx-auto p-6">
        <div className="text-center py-12">
          <AlertCircle className="w-16 h-16 text-orange-400 mx-auto mb-4" />
          <h3 className="text-xl font-semibold text-gray-900 mb-2">문제 생성에 실패했습니다</h3>
          <p className="text-gray-600 mb-6">
            AI 문제 생성 중 오류가 발생했습니다. 다시 시도해보시거나 다른 과목을 선택해주세요.
          </p>
          <div className="flex justify-center space-x-4">
            <button
              onClick={() => generateQuestions()}
              className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 flex items-center"
            >
              <RefreshCw className="w-4 h-4 mr-2" />
              AI 문제 다시 생성
            </button>
            <button
              onClick={() => navigate('/learning')}
              className="bg-gray-600 text-white px-6 py-3 rounded-lg hover:bg-gray-700"
            >
              학습 목록으로 돌아가기
            </button>
          </div>
          <div className="mt-6 p-4 bg-yellow-50 border border-yellow-200 rounded-lg max-w-md mx-auto">
            <p className="text-sm text-yellow-800">
              💡 <strong>팁:</strong> 네트워크 연결을 확인하거나 잠시 후 다시 시도해보세요.
            </p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto">
      {/* 헤더 */}
      <div className="mb-8">
        <div className="flex items-center justify-between">
          <div className="flex items-center">
            <button
              onClick={() => navigate('/learning')}
              className="flex items-center text-gray-600 hover:text-gray-800 mr-4"
            >
              <ArrowLeft className="w-5 h-5 mr-1" />
              돌아가기
            </button>
            <div>
              <h1 className="text-2xl font-bold text-gray-900">
                {subject?.name || subjectKey} 문제 풀이
              </h1>
              <p className="text-gray-600 mt-1">
                문제 {currentQuestionIndex + 1}/{questions.length}
              </p>
            </div>
          </div>
          
          {/* 진행률 */}
          <div className="text-right">
            <div className="text-sm text-gray-600 mb-1">진행률</div>
            <div className="w-32 h-2 bg-gray-200 rounded-full">
              <div 
                className="h-2 bg-blue-600 rounded-full transition-all duration-300"
                style={{ width: `${((currentQuestionIndex + 1) / questions.length) * 100}%` }}
              ></div>
            </div>
            <div className="text-xs text-gray-500 mt-1">
              {Math.round(((currentQuestionIndex + 1) / questions.length) * 100)}%
            </div>
          </div>
        </div>
      </div>

      {/* 현재 점수 */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center">
            <Target className="w-5 h-5 text-blue-600 mr-2" />
            <span className="text-blue-900 font-medium">현재 점수</span>
          </div>
          <div className="text-blue-900 font-bold">
            {score}/{currentQuestionIndex + (showResult ? 1 : 0)}
          </div>
        </div>
      </div>

      {/* 문제 카드 */}
      {currentQuestion && (
        <div className="bg-white rounded-lg p-8 shadow-sm border border-gray-200 mb-6">
          {/* 문제 메타데이터 */}
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center space-x-3">
              <span className={`px-3 py-1 text-sm font-medium rounded-full ${getDifficultyColor(currentQuestion.difficulty_level)}`}>
                {getDifficultyLabel(currentQuestion.difficulty_level)}
              </span>
              <span className="text-sm text-gray-500">
                {currentQuestion.question_type === 'multiple_choice' ? '객관식' : '주관식'}
              </span>
              <div className="flex items-center px-2 py-1 bg-gradient-to-r from-blue-50 to-purple-50 border border-blue-200 rounded-full">
                <Brain className="w-3 h-3 text-blue-600 mr-1" />
                <span className="text-xs text-blue-700 font-medium">AI 생성</span>
              </div>
            </div>
            <div className="flex items-center text-sm text-gray-500">
              <Clock className="w-4 h-4 mr-1" />
              문제 {currentQuestion.id}
            </div>
          </div>

          {/* 문제 텍스트 */}
          <div className="mb-8">
            <h2 className="text-xl font-semibold text-gray-900 leading-relaxed">
              {currentQuestion.text}
            </h2>
          </div>

          {/* 선택지 */}
          {currentQuestion.options && (
            <div className="space-y-3 mb-8">
              {currentQuestion.options.map((option, index) => (
                <button
                  key={index}
                  onClick={() => !showResult && handleAnswerSelect(option)}
                  disabled={showResult}
                  className={`w-full p-4 text-left rounded-lg border-2 transition-all ${
                    selectedAnswer === option
                      ? showResult
                        ? option === currentQuestion.correct_answer
                          ? 'border-green-500 bg-green-50 text-green-900'
                          : 'border-red-500 bg-red-50 text-red-900'
                        : 'border-blue-500 bg-blue-50 text-blue-900'
                      : showResult && option === currentQuestion.correct_answer
                        ? 'border-green-500 bg-green-50 text-green-900'
                        : 'border-gray-200 hover:border-gray-300 text-gray-700'
                  } ${showResult ? 'cursor-not-allowed' : 'cursor-pointer hover:bg-gray-50'}`}
                >
                  <div className="flex items-center">
                    <div className={`w-6 h-6 rounded-full border-2 mr-3 flex items-center justify-center ${
                      selectedAnswer === option
                        ? showResult
                          ? option === currentQuestion.correct_answer
                            ? 'border-green-500 bg-green-500 text-white'
                            : 'border-red-500 bg-red-500 text-white'
                          : 'border-blue-500 bg-blue-500 text-white'
                        : showResult && option === currentQuestion.correct_answer
                          ? 'border-green-500 bg-green-500 text-white'
                          : 'border-gray-300'
                    }`}>
                      {showResult && (selectedAnswer === option || option === currentQuestion.correct_answer) && (
                        option === currentQuestion.correct_answer 
                          ? <CheckCircle className="w-4 h-4" />
                          : <AlertCircle className="w-4 h-4" />
                      )}
                    </div>
                    <span className="font-medium">{option}</span>
                  </div>
                </button>
              ))}
            </div>
          )}

          {/* 버튼 영역 */}
          <div className="flex justify-end space-x-3">
            {!showResult ? (
              <button
                onClick={handleSubmitAnswer}
                disabled={!selectedAnswer}
                className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed flex items-center"
              >
                <CheckCircle className="w-5 h-5 mr-2" />
                답안 제출
              </button>
            ) : (
              <button
                onClick={handleNextQuestion}
                className="bg-green-600 text-white px-6 py-3 rounded-lg hover:bg-green-700 flex items-center"
              >
                {currentQuestionIndex < questions.length - 1 ? (
                  <>
                    <Play className="w-5 h-5 mr-2" />
                    다음 문제
                  </>
                ) : (
                  <>
                    <CheckCircle className="w-5 h-5 mr-2" />
                    학습 완료
                  </>
                )}
              </button>
            )}
          </div>
        </div>
      )}

      {/* 학습 진행 정보 */}
      <div className="bg-gray-50 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">학습 진행 상황</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-center">
          <div className="bg-white rounded-lg p-4">
            <div className="text-2xl font-bold text-blue-600">{questions.length}</div>
            <div className="text-sm text-gray-600">총 문제 수</div>
          </div>
          <div className="bg-white rounded-lg p-4">
            <div className="text-2xl font-bold text-green-600">{score}</div>
            <div className="text-sm text-gray-600">맞힌 문제</div>
          </div>
          <div className="bg-white rounded-lg p-4">
            <div className="text-2xl font-bold text-purple-600">
              {currentQuestionIndex + (showResult ? 1 : 0)}
            </div>
            <div className="text-sm text-gray-600">진행된 문제</div>
          </div>
        </div>
      </div>
    </div>
  );
}
