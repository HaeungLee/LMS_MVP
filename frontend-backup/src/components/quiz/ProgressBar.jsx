import React from 'react';
import useQuizStore from '../../stores/quizStore';

import { useEffect, useRef, useState } from 'react';

function ProgressBar({ totalSeconds = 600, onTimeUp }) {
  const { 
    currentQuestion, 
    questions, 
    answers, 
    skippedQuestions,
    goToQuestion 
  } = useQuizStore();
  const [elapsedTime, setElapsedTime] = useState(0);
  const intervalRef = useRef(null);

  useEffect(() => {
    // 카운트다운 시작
    intervalRef.current = setInterval(() => {
      setElapsedTime((t) => {
        const next = t + 1;
        if (next >= totalSeconds) {
          clearInterval(intervalRef.current);
          onTimeUp && onTimeUp();
        }
        return next;
      });
    }, 1000);
    return () => clearInterval(intervalRef.current);
  }, [totalSeconds, onTimeUp]);
  
  const total = questions.length;
  const current = currentQuestion + 1; // 1-based for display
  const progress = (current / total) * 100;
  
  const containerStyle = {
    backgroundColor: 'white',
    padding: '20px',
    borderRadius: '8px',
    boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
    marginBottom: '20px'
  };

  const headerStyle = {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '16px'
  };

  const titleStyle = {
    fontSize: '18px',
    fontWeight: '600',
    color: '#374151'
  };

  const rightInfoStyle = {
    display: 'flex',
    alignItems: 'center',
    gap: '16px'
  };

  const counterStyle = {
    fontSize: '14px',
    color: '#6b7280'
  };

  const timerStyle = {
    display: 'flex',
    alignItems: 'center',
    gap: '4px',
    fontSize: '14px',
    color: '#3b82f6',
    fontWeight: '500'
  };

  const formatTime = (seconds) => {
    const remaining = Math.max(totalSeconds - seconds, 0);
    const minutes = Math.floor(remaining / 60);
    const secs = remaining % 60;
    return `${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  const progressBarBgStyle = {
    width: '100%',
    height: '8px',
    backgroundColor: '#e5e7eb',
    borderRadius: '4px',
    overflow: 'hidden',
    marginBottom: '16px'
  };

  const progressBarFillStyle = {
    height: '100%',
    backgroundColor: '#3b82f6',
    borderRadius: '4px',
    transition: 'width 0.3s ease',
    width: `${progress}%`
  };

  const dotsContainerStyle = {
    display: 'flex',
    gap: '8px',
    flexWrap: 'wrap'
  };

  const getDotStyle = (index) => {
    const questionId = questions[index]?.id;
    let backgroundColor = '#e5e7eb'; // 기본 (안 푼 문제)
    
    if (skippedQuestions.has(questionId)) {
      backgroundColor = '#9ca3af'; // 건너뛴 문제 (회색)
    } else if (answers[questionId] !== undefined && answers[questionId].trim()) {
      backgroundColor = '#10b981'; // 푼 문제 (녹색)
    } else if (index === currentQuestion) {
      backgroundColor = '#3b82f6'; // 현재 문제 (파란색)
    }

    return {
      width: '32px',
      height: '32px',
      borderRadius: '50%',
      backgroundColor,
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      fontSize: '12px',
      color: 'white',
      fontWeight: '500',
      cursor: 'pointer',
      transition: 'all 0.2s ease',
      border: index === currentQuestion ? '2px solid #1d4ed8' : '2px solid transparent',
      '&:hover': {
        transform: 'scale(1.1)'
      }
    };
  };

  const handleDotClick = (index) => {
    goToQuestion(index);
  };

  return (
    <div style={containerStyle}>
      <div style={headerStyle}>
        <h2 style={titleStyle}>문제 진행 상황</h2>
        <div style={rightInfoStyle}>
          <div style={timerStyle}>
            <span>⏱️</span>
            <span>{formatTime(elapsedTime)}</span>
          </div>
          <span style={counterStyle}>{current} / {total}</span>
        </div>
      </div>
      
      <div style={progressBarBgStyle}>
        <div style={progressBarFillStyle}></div>
      </div>
      
      <div style={dotsContainerStyle}>
        {Array.from({ length: total }, (_, index) => (
          <div 
            key={index} 
            style={getDotStyle(index)}
            onClick={() => handleDotClick(index)}
            title={`문제 ${index + 1}${index === currentQuestion ? ' (현재)' : ''}${skippedQuestions.has(questions[index]?.id) ? ' (건너뜀)' : ''}${answers[questions[index]?.id] ? ' (답변완료)' : ''}`}
          >
            {index + 1}
          </div>
        ))}
      </div>
    </div>
  );
}

export default ProgressBar;
