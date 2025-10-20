/**
 * 복습 세션 실행 페이지
 * 
 * - 선택된 문제들을 하나씩 풀이
 * - 실시간 피드백
 * - 세션 완료 요약
 */

import { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useMutation } from '@tanstack/react-query';
import { 
  CheckCircle, 
  XCircle, 
  ArrowRight, 
  Clock,
  Trophy,
  RefreshCw,
  Home,
  Brain,
  Loader
} from 'lucide-react';
import { api } from '../../shared/services/apiClient';

interface ReviewProblem {
  problem_id: number;
  problem_title: string;
  topic: string;
  concept: string;
  difficulty: string;
  incorrect_count: number;
  days_since_last: number;
  forgetting_risk: number;
  review_urgency: 'critical' | 'high' | 'medium' | 'low';
}

interface ReviewSession {
  session_id: string;
  problems: ReviewProblem[];
  total_count: number;
  estimated_time_minutes: number;
  focus_message: string;
}

interface SessionResult {
  problem_id: number;
  answered: boolean;
  correct: boolean;
  time_spent: number;
  feedback?: string;
  next_review_date?: string;
}

export default function ReviewSessionPage() {
  const navigate = useNavigate();
  const location = useLocation();
  
  const session = location.state?.session as ReviewSession | undefined;
  
  const [currentIndex, setCurrentIndex] = useState(0);
  const [results, setResults] = useState<SessionResult[]>([]);
  const [startTime, setStartTime] = useState(Date.now());
  const [sessionComplete, setSessionComplete] = useState(false);
  const [userAnswer, setUserAnswer] = useState('');
  const [showFeedback, setShowFeedback] = useState(false);
  const [currentFeedback, setCurrentFeedback] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  // 답안 제출 mutation
  const submitMutation = useMutation({
    mutationFn: async (data: { problem_id: number; user_answer: string; time_spent: number }) => 
      api.post('/review/submit', {
        session_id: session?.session_id,
        ...data
      }),
    onSuccess: (data: any) => {
      setCurrentFeedback(data.feedback);
      setShowFeedback(true);
    },
  });

  // 세션이 없으면 복습 페이지로 리다이렉트
  useEffect(() => {
    if (!session) {
      navigate('/review');
    }
  }, [session, navigate]);

  if (!session) {
    return null;
  }

  const currentProblem = session.problems[currentIndex];
  const progress = ((currentIndex + 1) / session.total_count) * 100;

  // 답안 제출
  const submitAnswer = async () => {
    const timeSpent = Math.floor((Date.now() - startTime) / 1000);
    setIsSubmitting(true);
    
    try {
      const response = await submitMutation.mutateAsync({
        problem_id: currentProblem.problem_id,
        user_answer: userAnswer,
        time_spent: timeSpent
      });
      
      const result: SessionResult = {
        problem_id: currentProblem.problem_id,
        answered: true,
        correct: response.is_correct,
        time_spent: timeSpent,
        feedback: response.feedback,
        next_review_date: response.next_review_date
      };
      
      setResults([...results, result]);
      
      // 3초 후 다음 문제로
      setTimeout(() => {
        setShowFeedback(false);
        setIsSubmitting(false);
        
        if (currentIndex + 1 < session.total_count) {
          setCurrentIndex(currentIndex + 1);
          setStartTime(Date.now());
          setUserAnswer('');
        } else {
          setSessionComplete(true);
        }
      }, 3000);
    } catch (error) {
      console.error('제출 실패:', error);
      setIsSubmitting(false);
    }
  };

  // 문제 건너뛰기
  const skipProblem = () => {
    const result: SessionResult = {
      problem_id: currentProblem.problem_id,
      answered: false,
      correct: false,
      time_spent: 0
    };
    
    setResults([...results, result]);
    
    if (currentIndex + 1 < session.total_count) {
      setCurrentIndex(currentIndex + 1);
      setStartTime(Date.now());
      setUserAnswer('');
    } else {
      setSessionComplete(true);
    }
  };

  // 세션 완료 화면
  if (sessionComplete) {
    const correctCount = results.filter(r => r.correct).length;
    const answeredCount = results.filter(r => r.answered).length;
    const totalTime = results.reduce((sum, r) => sum + r.time_spent, 0);
    const accuracy = answeredCount > 0 ? (correctCount / answeredCount * 100) : 0;

    return (
      <div className="max-w-4xl mx-auto space-y-8">
        {/* 완료 헤더 */}
        <div className="bg-gradient-to-r from-green-500 to-emerald-500 rounded-3xl p-8 text-white text-center">
          <Trophy className="w-20 h-20 mx-auto mb-4" />
          <h1 className="text-4xl font-bold mb-2">복습 완료! 🎉</h1>
          <p className="text-green-100 text-lg">
            훌륭해요! 꾸준한 복습이 실력을 만듭니다
          </p>
        </div>

        {/* 통계 */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <StatBox
            label="총 문제"
            value={session.total_count}
            unit="개"
            color="from-blue-500 to-cyan-500"
          />
          <StatBox
            label="정답"
            value={correctCount}
            unit="개"
            color="from-green-500 to-emerald-500"
          />
          <StatBox
            label="정확도"
            value={Math.round(accuracy)}
            unit="%"
            color="from-purple-500 to-pink-500"
          />
          <StatBox
            label="소요 시간"
            value={Math.floor(totalTime / 60)}
            unit="분"
            color="from-orange-500 to-red-500"
          />
        </div>

        {/* 문제별 결과 */}
        <div className="bg-white rounded-2xl shadow-lg p-6">
          <h2 className="text-xl font-bold text-gray-900 mb-6">문제별 결과</h2>
          <div className="space-y-3">
            {results.map((result, idx) => {
              const problem = session.problems[idx];
              return (
                <div
                  key={idx}
                  className="flex items-center justify-between p-4 bg-gray-50 rounded-lg"
                >
                  <div className="flex items-center gap-4">
                    {result.correct ? (
                      <CheckCircle className="w-6 h-6 text-green-500" />
                    ) : result.answered ? (
                      <XCircle className="w-6 h-6 text-red-500" />
                    ) : (
                      <div className="w-6 h-6 rounded-full bg-gray-300" />
                    )}
                    <div>
                      <p className="font-medium text-gray-900">{problem.problem_title}</p>
                      <p className="text-sm text-gray-600">{problem.concept}</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="text-sm text-gray-500">
                      {result.answered ? `${result.time_spent}초` : '건너뜀'}
                    </p>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* 액션 버튼 */}
        <div className="flex gap-4">
          <button
            onClick={() => navigate('/review')}
            className="flex-1 flex items-center justify-center gap-2 px-6 py-4 bg-purple-600 text-white font-semibold rounded-xl shadow-lg hover:shadow-xl transition-all"
          >
            <RefreshCw className="w-5 h-5" />
            다시 복습하기
          </button>
          <button
            onClick={() => navigate('/')}
            className="flex-1 flex items-center justify-center gap-2 px-6 py-4 bg-gray-600 text-white font-semibold rounded-xl shadow-lg hover:shadow-xl transition-all"
          >
            <Home className="w-5 h-5" />
            대시보드로
          </button>
        </div>
      </div>
    );
  }

  // 문제 풀이 화면
  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* 진행 상황 헤더 */}
      <div className="bg-white rounded-2xl shadow-lg p-6">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <Brain className="w-6 h-6 text-purple-600" />
            <h2 className="text-lg font-bold text-gray-900">
              복습 세션 진행 중
            </h2>
          </div>
          <div className="flex items-center gap-2 text-sm text-gray-600">
            <Clock className="w-4 h-4" />
            <span>문제 {currentIndex + 1} / {session.total_count}</span>
          </div>
        </div>

        {/* 진행률 바 */}
        <div className="h-3 bg-gray-200 rounded-full overflow-hidden">
          <div
            className="h-full bg-gradient-to-r from-purple-500 to-pink-500 transition-all duration-500"
            style={{ width: `${progress}%` }}
          />
        </div>
      </div>

      {/* 문제 카드 */}
      <div className="bg-white rounded-2xl shadow-lg p-8">
        {/* 문제 메타 정보 */}
        <div className="flex items-center gap-3 mb-6">
          <span className={`px-3 py-1 rounded-full text-sm font-semibold ${
            currentProblem.review_urgency === 'critical' ? 'bg-red-100 text-red-700' :
            currentProblem.review_urgency === 'high' ? 'bg-orange-100 text-orange-700' :
            currentProblem.review_urgency === 'medium' ? 'bg-yellow-100 text-yellow-700' :
            'bg-green-100 text-green-700'
          }`}>
            {currentProblem.review_urgency === 'critical' ? '긴급' :
             currentProblem.review_urgency === 'high' ? '높음' :
             currentProblem.review_urgency === 'medium' ? '보통' : '낮음'}
          </span>
          <span className="px-3 py-1 bg-gray-100 text-gray-700 rounded-full text-sm font-medium">
            {currentProblem.difficulty}
          </span>
          <span className="px-3 py-1 bg-purple-100 text-purple-700 rounded-full text-sm font-medium">
            {currentProblem.concept}
          </span>
        </div>

        {/* 문제 제목 */}
        <h3 className="text-2xl font-bold text-gray-900 mb-4">
          {currentProblem.problem_title}
        </h3>

        {/* 문제 상세 정보 */}
        <div className="bg-gradient-to-br from-orange-50 to-red-50 rounded-xl p-4 mb-6">
          <p className="text-sm text-gray-700 mb-2">
            🔥 <strong>망각 위험도:</strong> {currentProblem.forgetting_risk.toFixed(0)}%
          </p>
          <p className="text-sm text-gray-700 mb-2">
            📚 <strong>이전 틀린 횟수:</strong> {currentProblem.incorrect_count}회
          </p>
          <p className="text-sm text-gray-700">
            📅 <strong>마지막 시도:</strong> {currentProblem.days_since_last}일 전
          </p>
        </div>

        {/* 문제 내용 (임시 - 실제로는 백엔드에서 가져옴) */}
        <div className="bg-gray-50 rounded-xl p-6 mb-6">
          <p className="text-gray-800 leading-relaxed mb-4">
            다음 코드의 출력 결과를 예측하세요:
          </p>
          <pre className="bg-gray-900 text-green-400 rounded-lg p-4 overflow-x-auto">
            <code>{`def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

print(fibonacci(5))`}</code>
          </pre>
        </div>

        {/* 답안 입력 */}
        <div className="mb-6">
          <label className="block text-sm font-semibold text-gray-700 mb-2">
            답안 입력
          </label>
          <textarea
            value={userAnswer}
            onChange={(e) => setUserAnswer(e.target.value)}
            placeholder="답을 입력하세요..."
            className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-purple-500 focus:border-transparent resize-none"
            rows={4}
          />
        </div>

        {/* 액션 버튼 */}
        <div className="flex gap-4">
          <button
            onClick={skipProblem}
            className="px-6 py-3 bg-gray-200 text-gray-700 font-medium rounded-xl hover:bg-gray-300 transition-colors"
          >
            건너뛰기
          </button>
          <button
            onClick={submitAnswer}
            disabled={!userAnswer.trim() || isSubmitting}
            className="flex-1 flex items-center justify-center gap-2 px-6 py-3 bg-gradient-to-r from-purple-600 to-pink-600 text-white font-semibold rounded-xl shadow-lg hover:shadow-xl disabled:opacity-50 disabled:cursor-not-allowed transition-all"
          >
            {isSubmitting ? (
              <>
                <Loader className="w-5 h-5 animate-spin" />
                채점 중...
              </>
            ) : (
              <>
                제출하기
                <ArrowRight className="w-5 h-5" />
              </>
            )}
          </button>
        </div>
      </div>

      {/* 세션 정보 */}
      <div className="bg-gradient-to-br from-purple-50 to-pink-50 rounded-xl p-4 text-center">
        <p className="text-sm text-gray-700">
          💡 <strong>Tip:</strong> 틀린 문제는 1일 후 다시 복습하게 됩니다
        </p>
      </div>

      {/* 피드백 모달 */}
      {showFeedback && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-2xl p-8 max-w-md w-full shadow-2xl animate-bounce-in">
            <div className="text-center">
              {currentFeedback.includes('정답') ? (
                <CheckCircle className="w-20 h-20 text-green-500 mx-auto mb-4" />
              ) : (
                <XCircle className="w-20 h-20 text-red-500 mx-auto mb-4" />
              )}
              <p className="text-2xl font-bold text-gray-900 mb-2">
                {currentFeedback.includes('정답') ? '정답입니다! 🎉' : '아쉽지만 틀렸습니다 💡'}
              </p>
              <p className="text-gray-600 mb-4">{currentFeedback}</p>
              <div className="flex items-center justify-center gap-2 text-purple-600">
                <Loader className="w-5 h-5 animate-spin" />
                <span className="text-sm">다음 문제로 이동 중...</span>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

// ============= Sub Components =============

interface StatBoxProps {
  label: string;
  value: number;
  unit: string;
  color: string;
}

function StatBox({ label, value, unit, color }: StatBoxProps) {
  return (
    <div className="bg-white rounded-xl shadow-lg p-6 text-center">
      <p className="text-sm text-gray-600 mb-2">{label}</p>
      <div className="flex items-baseline justify-center gap-1">
        <span className={`text-4xl font-bold bg-gradient-to-r ${color} bg-clip-text text-transparent`}>
          {value}
        </span>
        <span className="text-gray-500 text-lg">{unit}</span>
      </div>
    </div>
  );
}
