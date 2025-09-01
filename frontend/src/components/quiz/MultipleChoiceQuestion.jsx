import React, { useState, useEffect } from 'react';

function MultipleChoiceQuestion({ question, onAnswerChange, currentAnswer }) {
  const [selectedOption, setSelectedOption] = useState('');
  const [focusedIndex, setFocusedIndex] = useState(-1);
  const questionData = question.question_data || {};

  useEffect(() => {
    setSelectedOption(currentAnswer || '');
  }, [currentAnswer]);

  const handleOptionSelect = (option) => {
    setSelectedOption(option);
    onAnswerChange(option);
  };

  const options = questionData.options || [];
  const questionText = questionData.question || question.code_snippet || '질문이 없습니다.';

  // 키보드 네비게이션
  const handleKeyDown = (e, index) => {
    switch (e.key) {
      case 'Enter':
      case ' ':
        e.preventDefault();
        handleOptionSelect(options[index]);
        break;
      case 'ArrowDown':
        e.preventDefault();
        setFocusedIndex(Math.min(index + 1, options.length - 1));
        break;
      case 'ArrowUp':
        e.preventDefault();
        setFocusedIndex(Math.max(index - 1, 0));
        break;
      case 'Home':
        e.preventDefault();
        setFocusedIndex(0);
        break;
      case 'End':
        e.preventDefault();
        setFocusedIndex(options.length - 1);
        break;
      default:
        break;
    }
  };

  return (
    <div className="space-y-4">
      {/* 질문 표시 */}
      <div className="bg-gray-50 p-4 rounded-lg">
        <h3 className="text-lg font-semibold mb-2">객관식 문제</h3>
        <p
          id="question-label"
          className="text-gray-700 whitespace-pre-wrap"
        >
          {questionText}
        </p>
      </div>

      {/* 선택지 표시 */}
      <div className="space-y-3">
        <h4 className="font-medium text-gray-800">다음 중 정답을 선택하세요:</h4>
        <div
          className="grid gap-3"
          role="radiogroup"
          aria-labelledby="question-label"
        >
          {options.map((option, index) => (
            <button
              key={index}
              onClick={() => handleOptionSelect(option)}
              onKeyDown={(e) => handleKeyDown(e, index)}
              onFocus={() => setFocusedIndex(index)}
              role="radio"
              aria-checked={selectedOption === option}
              aria-describedby={`option-${index}-label`}
              tabIndex={focusedIndex === index ? 0 : -1}
              className={`w-full p-4 text-left rounded-lg border-2 transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 ${
                selectedOption === option
                  ? 'border-blue-500 bg-blue-50 text-blue-700'
                  : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
              }`}
            >
              <div className="flex items-start space-x-3">
                <span
                  className="font-medium text-gray-500 flex-shrink-0 mt-0.5"
                  id={`option-${index}-label`}
                >
                  {String.fromCharCode(65 + index)}.
                </span>
                <span className="flex-1 break-words">{option}</span>
              </div>
            </button>
          ))}
        </div>
      </div>

      {/* 선택된 답변 표시 */}
      {selectedOption && (
        <div className="mt-4 p-3 bg-blue-50 rounded-lg">
          <p className="text-sm text-blue-700">
            <span className="font-medium">선택한 답변:</span> {selectedOption}
          </p>
        </div>
      )}
    </div>
  );
}

export default MultipleChoiceQuestion;
