import React, { useState, useEffect } from 'react';

function TrueFalseQuestion({ question, onAnswerChange, currentAnswer }) {
  const [selectedAnswer, setSelectedAnswer] = useState('');
  const questionData = question.question_data || {};

  useEffect(() => {
    setSelectedAnswer(currentAnswer || '');
  }, [currentAnswer]);

  const handleAnswerSelect = (answer) => {
    setSelectedAnswer(answer);
    onAnswerChange(answer);
  };

  const statement = questionData.statement || question.code_snippet || '진술이 없습니다.';

  return (
    <div className="space-y-6">
      {/* 문제 유형 표시 */}
      <div className="bg-blue-50 p-4 rounded-lg">
        <h3 className="text-lg font-semibold mb-2 text-blue-800">참/거짓 판단 문제</h3>
        <p className="text-gray-700">
          다음 진술이 참인지 거짓인지 판단하세요.
        </p>
      </div>

      {/* 진술 표시 */}
      <div className="bg-gray-50 p-6 rounded-lg border-l-4 border-blue-500">
        <p className="text-lg text-gray-800 whitespace-pre-wrap">{statement}</p>
      </div>

      {/* 참/거짓 버튼 */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <button
          onClick={() => handleAnswerSelect('true')}
          className={`p-6 rounded-lg border-2 transition-all duration-200 ${
            selectedAnswer === 'true'
              ? 'border-green-500 bg-green-50 text-green-700'
              : 'border-gray-200 hover:border-green-300 hover:bg-green-50'
          }`}
        >
          <div className="text-center">
            <div className="text-2xl mb-2">✅</div>
            <div className="font-semibold text-sm sm:text-base">참 (True)</div>
          </div>
        </button>

        <button
          onClick={() => handleAnswerSelect('false')}
          className={`p-6 rounded-lg border-2 transition-all duration-200 ${
            selectedAnswer === 'false'
              ? 'border-red-500 bg-red-50 text-red-700'
              : 'border-gray-200 hover:border-red-300 hover:bg-red-50'
          }`}
        >
          <div className="text-center">
            <div className="text-2xl mb-2">❌</div>
            <div className="font-semibold text-sm sm:text-base">거짓 (False)</div>
          </div>
        </button>
      </div>

      {/* 선택된 답변 표시 */}
      {selectedAnswer && (
        <div className="mt-4 p-4 rounded-lg bg-gray-50">
          <p className="text-sm">
            <span className="font-medium">선택한 답변:</span>
            <span className={`ml-2 px-3 py-1 rounded-full text-sm font-medium ${
              selectedAnswer === 'true'
                ? 'bg-green-100 text-green-800'
                : 'bg-red-100 text-red-800'
            }`}>
              {selectedAnswer === 'true' ? '참' : '거짓'}
            </span>
          </p>
        </div>
      )}

      {/* 일반적인 오해 설명 (있는 경우) */}
      {questionData.common_misconception && (
        <div className="mt-4 p-4 bg-yellow-50 border-l-4 border-yellow-400 rounded-lg">
          <h4 className="font-medium text-yellow-800 mb-2">💡 알아두면 좋은 점</h4>
          <p className="text-yellow-700 text-sm">{questionData.common_misconception}</p>
        </div>
      )}
    </div>
  );
}

export default TrueFalseQuestion;
