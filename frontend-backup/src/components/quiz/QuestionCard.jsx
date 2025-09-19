import React, { useState, useEffect } from 'react';
import useQuizStore from '../../stores/quizStore';

function QuestionCard({ question }) {
  const { 
    answers, 
    setAnswer, 
    nextQuestion, 
    previousQuestion, 
    skipQuestion,
    toggleModal,
    currentQuestion,
    questions
  } = useQuizStore();
  
  const [userAnswer, setUserAnswer] = useState('');

  // 문제가 바뀔 때마다 답변 불러오기
  useEffect(() => {
    if (question) {
      const savedAnswer = answers[question.id] || '';
      setUserAnswer(savedAnswer);
    }
  }, [question?.id, answers]);

  const handleAnswerChange = (e) => {
    const value = e.target.value;
    setUserAnswer(value);
    if (question) {
      setAnswer(question.id, value);
    }
  };

  const handleNext = () => {
    if (currentQuestion < questions.length - 1) {
      nextQuestion();
    } else {
      toggleModal('showConfirmModal', true);
    }
  };

  const handlePrevious = () => {
    if (currentQuestion > 0) {
      previousQuestion();
    }
  };

  const handleSkip = () => {
    toggleModal('showSkipModal', true);
  };

  if (!question) {
    return <div>문제를 불러오는 중...</div>;
  }

  const containerStyle = {
    backgroundColor: 'white',
    borderRadius: '12px',
    boxShadow: '0 4px 6px rgba(0,0,0,0.1)',
    padding: '32px',
    maxWidth: '800px',
    margin: '0 auto'
  };

  const headerStyle = {
    borderBottom: '2px solid #e5e7eb',
    paddingBottom: '16px',
    marginBottom: '24px'
  };

  const topicBadgeStyle = {
    display: 'inline-block',
    backgroundColor: '#eff6ff',
    color: '#1d4ed8',
    padding: '4px 12px',
    borderRadius: '20px',
    fontSize: '14px',
    fontWeight: '500',
    marginBottom: '8px'
  };

  const difficultyBadgeStyle = {
    display: 'inline-block',
    backgroundColor: question.difficulty === 'easy' ? '#dcfce7' : question.difficulty === 'medium' ? '#fef3c7' : '#fee2e2',
    color: question.difficulty === 'easy' ? '#166534' : question.difficulty === 'medium' ? '#92400e' : '#991b1b',
    padding: '4px 8px',
    borderRadius: '12px',
    fontSize: '12px',
    fontWeight: '500',
    marginLeft: '8px'
  };

  const codeContainerStyle = {
    backgroundColor: '#1f2937',
    color: '#f9fafb',
    padding: '20px',
    borderRadius: '8px',
    fontFamily: 'Monaco, Consolas, "Courier New", monospace',
    fontSize: '14px',
    lineHeight: '1.6',
    marginBottom: '24px',
    border: '1px solid #374151'
  };

  const inputSectionStyle = {
    marginBottom: '24px'
  };

  const labelStyle = {
    display: 'block',
    fontSize: '16px',
    fontWeight: '600',
    color: '#374151',
    marginBottom: '8px'
  };

  const inputStyle = {
    width: '90%',
    padding: '12px 16px',
    border: '2px solid #d1d5db',
    borderRadius: '8px',
    fontSize: '16px',
    transition: 'border-color 0.2s',
    outline: 'none'
  };

  const inputFocusStyle = {
    ...inputStyle,
    borderColor: '#3b82f6'
  };

  const buttonContainerStyle = {
    display: 'flex',
    gap: '12px',
    justifyContent: 'space-between',
    alignItems: 'center'
  };

  const buttonGroupStyle = {
    display: 'flex',
    gap: '12px'
  };

  const primaryButtonStyle = {
    backgroundColor: '#3b82f6',
    color: 'white',
    padding: '12px 24px',
    border: 'none',
    borderRadius: '8px',
    fontSize: '16px',
    fontWeight: '500',
    cursor: 'pointer',
    transition: 'background-color 0.2s'
  };

  const secondaryButtonStyle = {
    backgroundColor: '#6b7280',
    color: 'white',
    padding: '10px 20px',
    border: 'none',
    borderRadius: '6px',
    fontSize: '14px',
    cursor: 'pointer',
    transition: 'background-color 0.2s'
  };

  const skipButtonStyle = {
    backgroundColor: '#f97316',
    color: 'white',
    padding: '10px 20px',
    border: 'none',
    borderRadius: '6px',
    fontSize: '14px',
    cursor: 'pointer',
    transition: 'background-color 0.2s'
  };

  const formatCodeSnippet = (code) => {
    return code.replace(/____/g, '___입력칸___');
  };

  return (
    <div style={containerStyle}>
      <div style={headerStyle}>
        <div>
          <span style={topicBadgeStyle}>{question.topic}</span>
          <span style={difficultyBadgeStyle}>{question.difficulty}</span>
        </div>
      </div>

      <div style={codeContainerStyle}>
        <pre style={{ margin: 0, whiteSpace: 'pre-wrap' }}>
          {formatCodeSnippet(question.code_snippet)}
        </pre>
      </div>

      <div style={inputSectionStyle}>
        <label style={labelStyle}>
          정답을 입력하세요:
        </label>
        <input
          type="text"
          value={userAnswer}
          onChange={handleAnswerChange}
          placeholder="여기에 정답을 입력하세요..."
          style={inputStyle}
          onFocus={(e) => e.target.style.borderColor = '#3b82f6'}
          onBlur={(e) => e.target.style.borderColor = '#d1d5db'}
          autoFocus
        />
      </div>

      <div style={buttonContainerStyle}>
        <div style={buttonGroupStyle}>
          {currentQuestion > 0 && (
            <button
              onClick={handlePrevious}
              style={secondaryButtonStyle}
              onMouseOver={(e) => e.target.style.backgroundColor = '#4b5563'}
              onMouseOut={(e) => e.target.style.backgroundColor = '#6b7280'}
            >
              ← 이전
            </button>
          )}
          <button
            onClick={handleSkip}
            style={skipButtonStyle}
            onMouseOver={(e) => e.target.style.backgroundColor = '#ea580c'}
            onMouseOut={(e) => e.target.style.backgroundColor = '#f97316'}
          >
            건너뛰기
          </button>
        </div>

        <button
          onClick={handleNext}
          style={primaryButtonStyle}
          onMouseOver={(e) => e.target.style.backgroundColor = '#2563eb'}
          onMouseOut={(e) => e.target.style.backgroundColor = '#3b82f6'}
          disabled={!userAnswer.trim()}
        >
          {currentQuestion < questions.length - 1 ? '다음 →' : '제출하기'}
        </button>
      </div>
    </div>
  );
}

export default QuestionCard;
