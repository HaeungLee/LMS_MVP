import React, { useState, useEffect } from 'react';
import CodeDisplay from '../common/CodeDisplay';

function ShortAnswerQuestion({ question, onAnswerChange, currentAnswer }) {
  const [userAnswer, setUserAnswer] = useState('');
  const [charCount, setCharCount] = useState(0);
  const questionData = question.question_data || {};

  useEffect(() => {
    setUserAnswer(currentAnswer || '');
    setCharCount((currentAnswer || '').length);
  }, [currentAnswer]);

  const handleAnswerChange = (e) => {
    const value = e.target.value;
    setUserAnswer(value);
    setCharCount(value.length);
    onAnswerChange(value);
  };

  const questionText = questionData.question || question.code_snippet || '질문이 없습니다.';
  const minLength = questionData.min_length || 50;
  const maxLength = questionData.max_length || 200;
  const expectedKeywords = questionData.expected_keywords || [];

  const isValidLength = charCount >= minLength && charCount <= maxLength;

  return (
    <div className="space-y-6">
      {/* 문제 유형 표시 */}
      <div className="bg-green-50 p-4 rounded-lg">
        <h3 className="text-lg font-semibold mb-2 text-green-800">단답형 문제</h3>
        <p className="text-gray-700">
          질문에 대한 답변을 작성하세요. 핵심 내용을 중심으로 설명해주세요.
        </p>
      </div>

      {/* 질문 표시 */}
      <div className="bg-gray-50 p-6 rounded-lg border-l-4 border-green-500">
        <p className="text-lg text-gray-800 whitespace-pre-wrap">{questionText}</p>
      </div>

      {/* 예상 키워드 힌트 (있는 경우) */}
      {expectedKeywords.length > 0 && (
        <div className="bg-blue-50 p-4 rounded-lg">
          <h4 className="font-medium text-blue-800 mb-2">💡 포함하면 좋은 키워드</h4>
          <div className="flex flex-wrap gap-2">
            {expectedKeywords.map((keyword, index) => (
              <span
                key={index}
                className="px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-sm"
              >
                {keyword}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* 답변 입력 영역 */}
      <div className="space-y-3">
        <label className="block text-sm font-medium text-gray-700">
          답변 작성
        </label>
        <textarea
          value={userAnswer}
          onChange={handleAnswerChange}
          placeholder="답변을 입력하세요..."
          className={`w-full p-4 border-2 rounded-lg resize-vertical min-h-[120px] font-mono text-sm ${
            !isValidLength && userAnswer
              ? 'border-red-300 focus:border-red-500 focus:ring-red-500'
              : 'border-gray-300 focus:border-green-500 focus:ring-green-500'
          }`}
          maxLength={maxLength * 2} // 약간의 여유를 줌
        />

        {/* 글자 수 및 유효성 표시 */}
        <div className="flex justify-between items-center text-sm">
          <div className={`flex items-center space-x-2 ${
            isValidLength ? 'text-green-600' : userAnswer ? 'text-red-600' : 'text-gray-500'
          }`}>
            {isValidLength ? (
              <span>✅</span>
            ) : userAnswer ? (
              <span>⚠️</span>
            ) : (
              <span>📝</span>
            )}
            <span>
              {charCount}/{maxLength}자
              {charCount < minLength && userAnswer && (
                <span className="ml-2">(최소 {minLength}자 필요)</span>
              )}
            </span>
          </div>

          <div className="text-gray-500">
            권장: {minLength}-{maxLength}자
          </div>
        </div>

        {/* 진행 바 */}
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div
            className={`h-2 rounded-full transition-all duration-300 ${
              isValidLength ? 'bg-green-500' : 'bg-gray-400'
            }`}
            style={{ width: `${Math.min((charCount / maxLength) * 100, 100)}%` }}
          />
        </div>
      </div>

      {/* 샘플 답변 힌트 (있는 경우) */}
      {questionData.sample_answer && (
        <details className="bg-yellow-50 p-4 rounded-lg">
          <summary className="font-medium text-yellow-800 cursor-pointer">
            💡 샘플 답변 보기 (참고용)
          </summary>
          <div className="mt-3">
            <CodeDisplay
              code={questionData.sample_answer}
              language="python"
              title="샘플 답변"
              theme="light"
              showLineNumbers={false}
              showCopyButton={true}
              className="border border-yellow-200"
            />
          </div>
        </details>
      )}
    </div>
  );
}

export default ShortAnswerQuestion;
