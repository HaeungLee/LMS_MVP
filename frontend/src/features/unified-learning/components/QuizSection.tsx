/**
 * 퀴즈 섹션 - 이해도 확인
 */

import { useState } from 'react';
import { CheckCircle, XCircle, HelpCircle, RefreshCw } from 'lucide-react';

interface QuizSectionProps {
  questions: any[];
  curriculumId?: number;
  onComplete: () => void;
  onRefresh?: () => void;
}

export default function QuizSection({ questions, onComplete, onRefresh }: QuizSectionProps) {
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [selectedAnswer, setSelectedAnswer] = useState<number | null>(null);
  const [showFeedback, setShowFeedback] = useState(false);
  const [score, setScore] = useState(0);
  const [isCompleted, setIsCompleted] = useState(false);

  // 퀴즈가 없으면 안내
  const defaultQuestions = [
    {
      question: "퀴즈를 불러오는 중입니다",
      options: [
        "커리큘럼에서 퀴즈 데이터를 가져오고 있습니다",
        "잠시만 기다려주세요",
        "교재 학습 후 퀴즈가 제공됩니다",
        "곧 준비됩니다"
      ],
      correct: 0,
      explanation: "실제 커리큘럼 기반 퀴즈가 곧 제공됩니다."
    }
  ];

  const quizData = questions?.length > 0 ? questions : defaultQuestions;
  const current = quizData[currentQuestion];

  const handleAnswer = async (idx: number) => {
    setSelectedAnswer(idx);
    setShowFeedback(true);

    // 로컬 정답 확인 (객관식이므로 인덱스 비교로 충분)
    const isCorrect = idx === current.correct;
    
    if (isCorrect) {
      setScore(prev => prev + 1);
    }
    
    // 마지막 문제면 3초 후 자동 완료
    if (currentQuestion === quizData.length - 1) {
      setTimeout(() => {
        setIsCompleted(true);
        onComplete();
      }, 3000);
    }
    
    // TODO: 향후 DB 저장이 필요하면 백엔드 API 수정 필요
    // (정답 인덱스를 함께 보내서 단순 비교하도록)
  };

  const handleNext = () => {
    if (currentQuestion < quizData.length - 1) {
      setCurrentQuestion(currentQuestion + 1);
      setSelectedAnswer(null);
      setShowFeedback(false);
    } else {
      setIsCompleted(true);
      onComplete();
    }
  };

  const percentage = Math.round((score / quizData.length) * 100);

  if (isCompleted) {
    return (
      <div className="bg-white rounded-2xl shadow-lg p-8">
        <div className="text-center">
          <div className="w-24 h-24 bg-gradient-to-br from-green-500 to-emerald-500 rounded-full flex items-center justify-center mx-auto mb-6">
            <CheckCircle className="w-12 h-12 text-white" />
          </div>
          <h2 className="text-3xl font-bold text-gray-900 mb-4">
            🎉 퀴즈 완료!
          </h2>
          <p className="text-xl text-gray-600 mb-8">
            {quizData.length}문제 중 {score}문제 정답 ({percentage}%)
          </p>

          {percentage >= 80 ? (
            <div className="bg-green-50 border-2 border-green-200 rounded-xl p-6 mb-6">
              <p className="text-green-900 font-semibold">
                훌륭해요! 🌟 오늘 배운 내용을 완벽하게 이해하셨네요!
              </p>
            </div>
          ) : percentage >= 60 ? (
            <div className="bg-yellow-50 border-2 border-yellow-200 rounded-xl p-6 mb-6">
              <p className="text-yellow-900 font-semibold">
                괜찮아요! 👍 조금만 더 복습하면 완벽할 거예요.
              </p>
            </div>
          ) : (
            <div className="bg-orange-50 border-2 border-orange-200 rounded-xl p-6 mb-6">
              <p className="text-orange-900 font-semibold">
                아쉽지만 괜찮아요. 교재를 다시 한번 읽어보시는 걸 추천드려요.
              </p>
            </div>
          )}
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-2xl shadow-lg p-8">
      {/* 헤더 */}
      <div className="flex items-center justify-between mb-6 pb-4 border-b border-gray-200">
        <div className="flex items-center gap-3">
          <div className="w-12 h-12 bg-gradient-to-br from-green-500 to-emerald-500 rounded-xl flex items-center justify-center">
            <HelpCircle className="w-6 h-6 text-white" />
          </div>
          <div>
            <h2 className="text-2xl font-bold text-gray-900">✍️ 이해도 퀴즈</h2>
            <p className="text-sm text-gray-600">
              문제 {currentQuestion + 1}/{quizData.length}
            </p>
          </div>
        </div>
        
        {/* 새로고침 버튼 */}
        {onRefresh && (
          <button
            onClick={onRefresh}
            className="flex items-center gap-2 px-4 py-2 text-sm text-green-600 hover:bg-green-50 rounded-lg transition-colors"
            title="새로운 퀴즈로 재생성"
          >
            <RefreshCw className="w-4 h-4" />
            <span>새 퀴즈</span>
          </button>
        )}
      </div>

      {/* 질문 */}
      <div className="mb-8">
        <h3 className="text-lg font-bold text-gray-900 mb-6">
          {current.question}
        </h3>

        {/* 선택지 */}
        <div className="space-y-3">
          {current.options.map((option: string, idx: number) => {
            const isSelected = selectedAnswer === idx;
            const isCorrect = idx === current.correct;
            const showResult = showFeedback;

            return (
              <button
                key={idx}
                onClick={() => !showFeedback && handleAnswer(idx)}
                disabled={showFeedback}
                className={`
                  w-full p-4 rounded-xl text-left transition-all duration-200
                  ${!showResult 
                    ? 'bg-gray-50 hover:bg-gray-100 border-2 border-gray-200 hover:border-indigo-400'
                    : isSelected && isCorrect
                      ? 'bg-green-50 border-2 border-green-500'
                      : isSelected && !isCorrect
                        ? 'bg-red-50 border-2 border-red-500'
                        : isCorrect
                          ? 'bg-green-50 border-2 border-green-500'
                          : 'bg-gray-50 border-2 border-gray-200'
                  }
                `}
              >
                <div className="flex items-center justify-between">
                  <span className={`font-medium ${
                    showResult && isCorrect ? 'text-green-900' :
                    showResult && isSelected && !isCorrect ? 'text-red-900' :
                    'text-gray-900'
                  }`}>
                    {option}
                  </span>
                  {showResult && isCorrect && (
                    <CheckCircle className="w-5 h-5 text-green-600" />
                  )}
                  {showResult && isSelected && !isCorrect && (
                    <XCircle className="w-5 h-5 text-red-600" />
                  )}
                </div>
              </button>
            );
          })}
        </div>
      </div>

      {/* 피드백 */}
      {showFeedback && (
        <div className={`mb-6 p-4 rounded-xl ${
          selectedAnswer === current.correct
            ? 'bg-green-50 border-2 border-green-200'
            : 'bg-red-50 border-2 border-red-200'
        }`}>
          <p className={`font-semibold mb-2 ${
            selectedAnswer === current.correct ? 'text-green-900' : 'text-red-900'
          }`}>
            {selectedAnswer === current.correct ? '✅ 정답입니다!' : '❌ 틀렸습니다'}
          </p>
          <p className="text-gray-700 text-sm">
            {current.explanation}
          </p>
        </div>
      )}

      {/* 다음 버튼 */}
      {showFeedback && (
        <button
          onClick={handleNext}
          className="w-full bg-gradient-to-r from-indigo-600 to-purple-600 text-white py-4 px-6 rounded-xl hover:shadow-lg transition-all duration-200 font-semibold"
        >
          {currentQuestion < quizData.length - 1 ? '다음 문제' : '퀴즈 완료'}
        </button>
      )}
    </div>
  );
}
