import useQuizStore from '../stores/quizStore';

// 퀴즈 네비게이션 훅
export const useQuizNavigation = () => {
  const { 
    currentQuestion, 
    questions, 
    nextQuestion, 
    previousQuestion 
  } = useQuizStore();

  const canGoNext = currentQuestion < questions.length - 1;
  const canGoPrevious = currentQuestion > 0;
  const isLastQuestion = currentQuestion === questions.length - 1;

  return {
    currentQuestion,
    canGoNext,
    canGoPrevious,
    isLastQuestion,
    nextQuestion,
    previousQuestion
  };
};

// 퀴즈 답변 관리 훅
export const useQuizAnswers = () => {
  const { answers, setAnswer, skippedQuestions, skipQuestion } = useQuizStore();

  const getAnswer = (questionId) => answers[questionId] || '';
  const isSkipped = (questionId) => skippedQuestions.has(questionId);
  const getAnsweredCount = () => Object.keys(answers).filter(id => answers[id]?.trim()).length;

  return {
    answers,
    getAnswer,
    setAnswer,
    isSkipped,
    skipQuestion,
    getAnsweredCount
  };
};
