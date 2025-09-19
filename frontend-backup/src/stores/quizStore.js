import { create } from 'zustand';
import { devtools } from 'zustand/middleware';

const useQuizStore = create(
  devtools(
    (set, get) => ({
      // 퀴즈 상태
      questions: [],
      currentQuestion: 0,
      answers: {},
      loading: true,
      error: null,
      quizComplete: false,
      skippedQuestions: new Set(),
      
      // 혼합 모드 상태 (NEW)
      quizMode: 'single', // 'single' | 'mixed' | 'adaptive'
      activeSubjects: [], // 현재 활성 과목들
      mixedModeConfig: null,
      subjectProgress: {}, // 과목별 진행률 추적
      
      // 모달 상태
      showConfirmModal: false,
      showSkipModal: false,
      showSettings: false,
      
      // 피드백 상태
      feedbackData: null,
      showFeedback: false,
      
      // 퀴즈 설정
      quizSettings: {
        shuffle: true,
        easy_count: 4,
        medium_count: 4,
        hard_count: 2
      },
      
      // 최근 활동 상태
      recentActivities: [],
      
      // Actions
      setQuestions: (questions) => set({ questions, loading: false }),
      setLoading: (loading) => set({ loading }),
      setError: (error) => set({ error, loading: false }),
      
      nextQuestion: () => set((state) => ({
        currentQuestion: Math.min(state.currentQuestion + 1, state.questions.length - 1)
      })),
      
      previousQuestion: () => set((state) => ({
        currentQuestion: Math.max(state.currentQuestion - 1, 0)
      })),
      
      // 특정 문제로 이동 (진행률 바에서 클릭)
      goToQuestion: (questionIndex) => set({
        currentQuestion: questionIndex
      }),
      
      setAnswer: (questionId, answer) => set((state) => ({
        answers: { ...state.answers, [questionId]: answer }
      })),
      
      skipQuestion: (questionId) => set((state) => ({
        skippedQuestions: new Set([...state.skippedQuestions, questionId])
      })),
      
      toggleModal: (modalName, value) => set({ [modalName]: value }),
      
      updateSettings: (field, value) => set((state) => ({
        quizSettings: { ...state.quizSettings, [field]: value }
      })),
      
      resetQuiz: () => set({
        questions: [],
        currentQuestion: 0,
        answers: {},
        quizComplete: false,
        skippedQuestions: new Set(),
        feedbackData: null,
        showFeedback: false,
        showConfirmModal: false,
        showSkipModal: false,
        showSettings: false
      }),
      
      completeQuiz: (feedbackData) => set({
        quizComplete: true,
        feedbackData,
        showFeedback: !!feedbackData
      }),
      
      // 최근 활동 추가
      addRecentActivity: (activity) => set((state) => ({
        recentActivities: [activity, ...state.recentActivities].slice(0, 10) // 최근 10개만 유지
      })),
      
      // 퀴즈 완료 시 최근 활동에 추가
      recordQuizCompletion: (sessionData) => {
        const activity = {
          id: Date.now(),
          activity_type: 'quiz_completed',
          activity: `Python 기초 퀴즈 완료`,
          date: new Date().toLocaleDateString('ko-KR'),
          score: Math.round((sessionData.correctAnswers / sessionData.totalAnswers) * 100),
          details: {
            total_questions: sessionData.totalAnswers,
            answered: sessionData.correctAnswers,
            skipped: sessionData.skippedCount,
            time_taken: sessionData.timeTaken
          }
        };
        
        get().addRecentActivity(activity);
      },

      // 혼합 모드 액션들 (NEW)
      setQuizMode: (mode, config = null) => set({
        quizMode: mode,
        mixedModeConfig: config,
        activeSubjects: mode === 'mixed' ? config?.subjects || [] : []
      }),
      
      updateSubjectProgress: (subject, progress) => set((state) => ({
        subjectProgress: {
          ...state.subjectProgress,
          [subject]: progress
        }
      })),
      
      // 현재 문제의 과목 정보 추가
      getCurrentQuestionSubjects: () => {
        const state = get();
        const current = state.questions[state.currentQuestion];
        return current?.subjects || [current?.subject];
      },
      
      // 과목별 통계 계산
      getSubjectStats: () => {
        const state = get();
        const stats = {};
        
        state.activeSubjects.forEach(subject => {
          const subjectQuestions = state.questions.filter(q => 
            q.subjects?.includes(subject) || q.subject === subject
          );
          const answered = subjectQuestions.filter(q => 
            state.answers[q.id]
          ).length;
          
          stats[subject] = {
            total: subjectQuestions.length,
            answered,
            progress: subjectQuestions.length > 0 ? answered / subjectQuestions.length : 0
          };
        });
        
        return stats;
      }
    }),
    {
      name: 'quiz-store', // DevTools에서 식별용
    }
  )
);

export default useQuizStore;
export { useQuizStore };
