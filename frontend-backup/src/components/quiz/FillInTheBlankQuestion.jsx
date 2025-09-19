import React, { useState, useEffect } from 'react';
import CodeDisplay from '../common/CodeDisplay';

function FillInTheBlankQuestion({ question, onAnswerChange, currentAnswer }) {
  const [userAnswer, setUserAnswer] = useState('');
  const questionData = question.question_data || {};

  useEffect(() => {
    setUserAnswer(currentAnswer || '');
  }, [currentAnswer]);

  const handleAnswerChange = (e) => {
    const value = e.target.value;
    setUserAnswer(value);
    onAnswerChange(value);
  };

  const template = questionData.template || question.code_snippet || '코드 템플릿이 없습니다.';
  const placeholder = questionData.placeholder || '답변을 입력하세요';

  return (
    <div className="space-y-6">
      {/* 문제 유형 표시 */}
      <div className="bg-purple-50 p-4 rounded-lg">
        <h3 className="text-lg font-semibold mb-2 text-purple-800">빈칸 채우기 문제</h3>
        <p className="text-gray-700">
          코드의 빈칸을 채워서 완성하세요.
        </p>
      </div>

      {/* 코드 템플릿 표시 */}
      <CodeDisplay
        code={template}
        language="python"
        title="코드 템플릿"
        theme="dark"
        showLineNumbers={true}
        showCopyButton={true}
        className="mb-4"
      />

      {/* 답변 입력 영역 */}
      <div className="space-y-3">
        <label className="block text-sm font-medium text-gray-700">
          빈칸에 들어갈 코드 입력
        </label>
        <input
          type="text"
          value={userAnswer}
          onChange={handleAnswerChange}
          placeholder={placeholder}
          className="w-full p-4 border-2 border-gray-300 rounded-lg font-mono text-sm focus:border-purple-500 focus:ring-purple-500"
        />

        {/* 입력된 답변 표시 */}
        {userAnswer && (
          <div className="mt-4 p-4 bg-purple-50 rounded-lg">
            <p className="text-sm text-purple-700">
              <span className="font-medium">입력한 답변:</span> <code className="bg-purple-100 px-2 py-1 rounded text-purple-800">{userAnswer}</code>
            </p>
          </div>
        )}
      </div>

      {/* 코드 실행 힌트 */}
      <div className="bg-blue-50 p-4 rounded-lg">
        <h4 className="font-medium text-blue-800 mb-2">💡 코드 작성 팁</h4>
        <ul className="text-blue-700 text-sm space-y-1">
          <li>• 올바른 Python 문법을 사용하세요</li>
          <li>• 변수명은 의미있게 지으세요</li>
          <li>• 불필요한 공백은 제거하세요</li>
          <li>• 대소문자를 정확히 구분하세요</li>
        </ul>
      </div>
    </div>
  );
}

export default FillInTheBlankQuestion;
