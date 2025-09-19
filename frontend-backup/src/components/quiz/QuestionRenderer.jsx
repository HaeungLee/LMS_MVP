import React from 'react';
import MultipleChoiceQuestion from './MultipleChoiceQuestion';
import TrueFalseQuestion from './TrueFalseQuestion';
import ShortAnswerQuestion from './ShortAnswerQuestion';
import FillInTheBlankQuestion from './FillInTheBlankQuestion';

function QuestionRenderer({ question, onAnswerChange, currentAnswer }) {
  if (!question) {
    return <div className="text-center text-gray-500">문제를 불러오는 중...</div>;
  }

  const questionType = question.question_type || question.type || 'fill_in_the_blank';
  const questionData = question.question_data || {};

  // 문제 유형에 따라 적절한 컴포넌트 선택
  const renderQuestionComponent = () => {
    switch (questionType) {
      case 'multiple_choice':
        return (
          <MultipleChoiceQuestion
            question={question}
            onAnswerChange={onAnswerChange}
            currentAnswer={currentAnswer}
          />
        );

      case 'true_false':
        return (
          <TrueFalseQuestion
            question={question}
            onAnswerChange={onAnswerChange}
            currentAnswer={currentAnswer}
          />
        );

      case 'short_answer':
        return (
          <ShortAnswerQuestion
            question={question}
            onAnswerChange={onAnswerChange}
            currentAnswer={currentAnswer}
          />
        );

      case 'fill_in_the_blank':
      default:
        return (
          <FillInTheBlankQuestion
            question={question}
            onAnswerChange={onAnswerChange}
            currentAnswer={currentAnswer}
          />
        );
    }
  };

  return (
    <div className="w-full max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
      {/* 문제 헤더 정보 */}
      <div className="mb-6">
        {/* 데스크톱: 가로 배치, 모바일: 세로 배치 */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between mb-4 gap-3">
          <div className="flex flex-col sm:flex-row sm:items-center gap-3">
            <div className="flex items-center space-x-3">
              <span className="text-sm font-medium text-gray-500">주제:</span>
              <span className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm font-medium">
                {question.subject || '일반'}
              </span>
            </div>

            <div className="flex items-center space-x-3">
              <span className="text-sm font-medium text-gray-500">난이도:</span>
              <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                question.difficulty === 'easy'
                  ? 'bg-green-100 text-green-800'
                  : question.difficulty === 'medium'
                  ? 'bg-yellow-100 text-yellow-800'
                  : 'bg-red-100 text-red-800'
              }`}>
                {question.difficulty === 'easy' ? '쉬움' :
                 question.difficulty === 'medium' ? '보통' : '어려움'}
              </span>
            </div>
          </div>

          <div className="flex flex-col sm:flex-row sm:items-center gap-3">
            <div className="flex items-center space-x-3">
              <span className="text-sm font-medium text-gray-500">문제 유형:</span>
              <span className="px-3 py-1 bg-purple-100 text-purple-800 rounded-full text-sm font-medium">
                {questionType === 'multiple_choice' ? '객관식' :
                 questionType === 'true_false' ? '참/거짓' :
                 questionType === 'short_answer' ? '단답형' :
                 '빈칸 채우기'}
              </span>
            </div>

            {/* AI 생성 표시 */}
            {question.ai_generated && (
              <span className="px-3 py-1 bg-indigo-100 text-indigo-800 rounded-full text-sm font-medium flex items-center justify-center">
                <span className="mr-1">🤖</span>
                AI 생성
              </span>
            )}
          </div>
        </div>
      </div>

      {/* 실제 문제 컴포넌트 렌더링 */}
      {renderQuestionComponent()}
    </div>
  );
}

export default QuestionRenderer;
