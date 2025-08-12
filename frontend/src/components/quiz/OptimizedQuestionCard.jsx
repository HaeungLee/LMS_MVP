import React, { memo } from 'react';
import useQuizStore from '../stores/quizStore';

const OptimizedQuestionCard = memo(({ question }) => {
  const { answers, setAnswer } = useQuizStore(
    state => ({ 
      answers: state.answers, 
      setAnswer: state.setAnswer 
    })
  );

  // 컴포넌트 로직...
  
  return (
    // JSX...
  );
});

export default OptimizedQuestionCard;
