import React, { useEffect } from 'react';
import { getQuestions, submitAnswers } from '../services/apiClient';
import { useNavigate, useSearchParams, useParams } from 'react-router-dom';
import QuestionRenderer from '../components/quiz/QuestionRenderer';
import ProgressBar from '../components/quiz/ProgressBar';
import FeedbackModal from '../components/feedback/FeedbackModal';
import useQuizStore from '../stores/quizStore';
import { SUBJECTS, getSubjectName, getSubjectIcon } from '../constants/subjects';

function QuizPage() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const { subject: urlSubject } = useParams();
  const subject = urlSubject || searchParams.get('subject') || 'python_basics';
  // Zustand store에서 상태와 액션 가져오기
  const {
    questions,
    currentQuestion,
    answers,
    loading,
    error,
    quizComplete,
    skippedQuestions,
    showConfirmModal,
    showSkipModal,
    showSettings,
    feedbackData,
    showFeedback,
    quizSettings,
    // Actions
    setQuestions,
    setLoading,
    setError,
    nextQuestion,
    previousQuestion,
    setAnswer,
    skipQuestion,
    toggleModal,
    updateSettings,
    resetQuiz,
    completeQuiz
  } = useQuizStore();

  const totalTime = 2400; // 40분

  const loadQuestions = async (settings = quizSettings) => {
    try {
      setLoading(true);
      setError(null);
      const data = await getQuestions(subject, settings);
      setQuestions(data);
    } catch (err) {
      setError('문제를 불러오는데 실패했습니다.');
      console.error('Error loading questions:', err);
    }
  };

  useEffect(() => {
    loadQuestions();
  }, [subject]);

  const handleAnswerChange = (value) => {
    if (questions[currentQuestion]) {
      setAnswer(questions[currentQuestion].id, value);
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

  const confirmSkip = () => {
    if (questions[currentQuestion]) {
      skipQuestion(questions[currentQuestion].id);
    }
    toggleModal('showSkipModal', false);
    if (currentQuestion < questions.length - 1) {
      nextQuestion();
    } else {
      toggleModal('showConfirmModal', true);
    }
  };

  const handleSubmit = async () => {
    try {
      toggleModal('showConfirmModal', false);
      
      const answeredQuestions = questions.filter(q => 
        answers[q.id] !== undefined && answers[q.id].trim() !== ''
      );
      
      if (answeredQuestions.length === 0) {
        alert('최소 1문제는 답해주세요.');
        return;
      }

      const submissionData = {
        subject: subject,
        user_answers: questions.map(question => ({
          question_id: question.id,
          user_answer: answers[question.id] || '',
          // 백엔드 스키마에 skipped는 선택 필드이므로 필요 시 추가 가능
          // skipped: skippedQuestions.has(question.id)
        })),
      };

      const result = await submitAnswers(submissionData);
      
      // 퀴즈 완료 기록
      const { recordQuizCompletion } = useQuizStore.getState();
      recordQuizCompletion({
        totalAnswers: questions.length,
        correctAnswers: answeredQuestions.length,
        skippedCount: skippedQuestions.size,
        timeTaken: totalTime
      });
      
      // 결과 페이지로 이동 (submission_id 기반)
      if (result && result.submission_id) {
        navigate(`/results/${result.submission_id}`);
      } else {
        completeQuiz(null);
      }

    } catch (error) {
      console.error('제출 중 오류 발생:', error);
      alert('제출 중 오류가 발생했습니다. 다시 시도해주세요.');
    }
  };

  const handleTimeUp = () => {
    toggleModal('showConfirmModal', true);
  };

  const handleRetakeQuiz = () => {
    resetQuiz();
    loadQuestions();
  };

  const handleSettingsChange = (field, value) => {
    updateSettings(field, value);
  };

  const applySettings = () => {
    resetQuiz();
    loadQuestions(quizSettings);
    toggleModal('showSettings', false);
  };

  if (loading) {
    return (
      <div style={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        height: '100vh',
        fontSize: '18px'
      }}>
        문제를 불러오는 중...
      </div>
    );
  }

  if (error) {
    return (
      <div style={{
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'center',
        alignItems: 'center',
        height: '100vh',
        gap: '20px'
      }}>
        <div style={{ fontSize: '18px', color: '#d32f2f' }}>{error}</div>
        <button 
          onClick={() => loadQuestions()}
          style={{
            padding: '10px 20px',
            backgroundColor: '#1976d2',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer'
          }}
        >
          다시 시도
        </button>
      </div>
    );
  }

  if (questions.length === 0) {
    return (
      <div style={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        height: '100vh',
        fontSize: '18px'
      }}>
        문제가 없습니다.
      </div>
    );
  }

  if (quizComplete) {
    return (
      <div style={{
        maxWidth: '800px',
        margin: '0 auto',
        padding: '20px',
        textAlign: 'center'
      }}>
        <h1 style={{ color: '#1976d2', marginBottom: '30px' }}>
          🎉 퀴즈 완료!
        </h1>
        
        {feedbackData && (
          <div style={{
            backgroundColor: '#f5f5f5',
            padding: '20px',
            borderRadius: '8px',
            marginBottom: '30px',
            textAlign: 'left'
          }}>
            <h3>결과 요약</h3>
            <p><strong>제출 시각:</strong> {new Date(feedbackData.submitted_at).toLocaleString()}</p>
            <p><strong>답변한 문제:</strong> {Object.keys(answers).filter(id => answers[id]?.trim()).length}/{questions.length}</p>
            <p><strong>건너뛴 문제:</strong> {skippedQuestions.size}</p>
            {feedbackData.feedback_id && (
              <p><strong>피드백 ID:</strong> {feedbackData.feedback_id}</p>
            )}
          </div>
        )}

        <div style={{ display: 'flex', gap: '15px', justifyContent: 'center' }}>
          <button
            onClick={handleRetakeQuiz}
            style={{
              padding: '12px 24px',
              backgroundColor: '#1976d2',
              color: 'white',
              border: 'none',
              borderRadius: '6px',
              cursor: 'pointer',
              fontSize: '16px'
            }}
          >
            다시 시도
          </button>
          
          <button
            onClick={() => window.location.href = '/'}
            style={{
              padding: '12px 24px',
              backgroundColor: '#757575',
              color: 'white',
              border: 'none',
              borderRadius: '6px',
              cursor: 'pointer',
              fontSize: '16px'
            }}
          >
            대시보드로
          </button>
        </div>

        {feedbackData && (
          <FeedbackModal 
            isOpen={showFeedback}
            onClose={() => toggleModal('showFeedback', false)}
            feedbackId={feedbackData.feedback_id}
          />
        )}
      </div>
    );
  }

  return (
    <div style={{ 
      maxWidth: '900px', 
      margin: '0 auto', 
      padding: '20px',
      minHeight: '100vh'
    }}>
      {/* 헤더와 설정 버튼 */}
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: '20px'
      }}>
        <h1 style={{ color: '#1976d2' }}>
          {getSubjectIcon(subject)} {getSubjectName(subject)} 퀴즈
        </h1>
        <button
          onClick={() => toggleModal('showSettings', true)}
          style={{
            padding: '8px 16px',
            backgroundColor: '#757575',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer'
          }}
        >
          ⚙️ 설정
        </button>
      </div>

      {/* 진행률 표시 */}
      <ProgressBar totalSeconds={totalTime} onTimeUp={handleTimeUp} />

      {/* 문제 카드 */}
      <QuestionRenderer
        question={questions[currentQuestion]}
        onAnswerChange={(answer) => setAnswer(questions[currentQuestion]?.id, answer)}
        currentAnswer={answers[questions[currentQuestion]?.id] || ''}
      />

      {/* 네비게이션 버튼 */}
      <div style={{
        display: 'flex',
        flexDirection: window.innerWidth < 640 ? 'column' : 'row',
        justifyContent: 'space-between',
        alignItems: window.innerWidth < 640 ? 'stretch' : 'center',
        gap: window.innerWidth < 640 ? '15px' : '0',
        marginTop: '30px',
        padding: '20px',
        backgroundColor: 'white',
        borderRadius: '12px',
        boxShadow: '0 4px 6px rgba(0,0,0,0.1)',
        border: '1px solid #e5e7eb'
      }}>
        <div style={{ 
          display: 'flex', 
          gap: '12px',
          justifyContent: window.innerWidth < 640 ? 'center' : 'flex-start',
          flexWrap: 'wrap'
        }}>
          {currentQuestion > 0 && (
            <button
              onClick={handlePrevious}
              style={{
                backgroundColor: '#6b7280',
                color: 'white',
                padding: '12px 20px',
                border: 'none',
                borderRadius: '8px',
                fontSize: '15px',
                fontWeight: '500',
                cursor: 'pointer',
                transition: 'all 0.2s ease',
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
                minWidth: '100px'
              }}
              onMouseEnter={(e) => {
                e.target.style.backgroundColor = '#4b5563';
                e.target.style.transform = 'translateY(-1px)';
                e.target.style.boxShadow = '0 4px 8px rgba(0,0,0,0.15)';
              }}
              onMouseLeave={(e) => {
                e.target.style.backgroundColor = '#6b7280';
                e.target.style.transform = 'translateY(0)';
                e.target.style.boxShadow = '0 2px 4px rgba(0,0,0,0.1)';
              }}
            >
              ← 이전
            </button>
          )}
          <button
            onClick={handleSkip}
            style={{
              backgroundColor: '#f97316',
              color: 'white',
              padding: '12px 20px',
              border: 'none',
              borderRadius: '8px',
              fontSize: '15px',
              fontWeight: '500',
              cursor: 'pointer',
              transition: 'all 0.2s ease',
              boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
              minWidth: '100px'
            }}
            onMouseEnter={(e) => {
              e.target.style.backgroundColor = '#ea580c';
              e.target.style.transform = 'translateY(-1px)';
              e.target.style.boxShadow = '0 4px 8px rgba(0,0,0,0.15)';
            }}
            onMouseLeave={(e) => {
              e.target.style.backgroundColor = '#f97316';
              e.target.style.transform = 'translateY(0)';
              e.target.style.boxShadow = '0 2px 4px rgba(0,0,0,0.1)';
            }}
          >
            건너뛰기
          </button>
        </div>

        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '20px',
          justifyContent: window.innerWidth < 640 ? 'center' : 'flex-end',
          flexWrap: 'wrap'
        }}>
          <span style={{ 
            fontSize: '15px', 
            color: '#374151',
            fontWeight: '600',
            padding: '8px 16px',
            backgroundColor: '#f3f4f6',
            borderRadius: '20px',
            border: '1px solid #d1d5db',
            whiteSpace: 'nowrap'
          }}>
            {currentQuestion + 1} / {questions.length}
          </span>
          <button
            onClick={handleNext}
            style={{
              backgroundColor: currentQuestion < questions.length - 1 ? '#3b82f6' : '#10b981',
              color: 'white',
              padding: '14px 28px',
              border: 'none',
              borderRadius: '8px',
              fontSize: '16px',
              fontWeight: '600',
              cursor: 'pointer',
              transition: 'all 0.2s ease',
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
              whiteSpace: 'nowrap'
            }}
            onMouseEnter={(e) => {
              e.target.style.backgroundColor = currentQuestion < questions.length - 1 ? '#2563eb' : '#059669';
              e.target.style.transform = 'translateY(-1px)';
              e.target.style.boxShadow = '0 4px 8px rgba(0,0,0,0.15)';
            }}
            onMouseLeave={(e) => {
              e.target.style.backgroundColor = currentQuestion < questions.length - 1 ? '#3b82f6' : '#10b981';
              e.target.style.transform = 'translateY(0)';
              e.target.style.boxShadow = '0 2px 4px rgba(0,0,0,0.1)';
            }}
          >
            {currentQuestion < questions.length - 1 ? '다음 →' : '🎯 퀴즈 제출'}
          </button>
        </div>
      </div>

      {/* 설정 모달 */}
      {showSettings && (
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          backgroundColor: 'rgba(0, 0, 0, 0.5)',
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          zIndex: 1000
        }}>
          <div style={{
            backgroundColor: 'white',
            padding: '30px',
            borderRadius: '8px',
            maxWidth: '500px',
            width: '90%'
          }}>
            <h3 style={{ marginBottom: '20px' }}>퀴즈 설정</h3>
            
            <div style={{ marginBottom: '20px' }}>
              <label style={{ display: 'block', marginBottom: '5px' }}>
                문제 셔플링:
              </label>
              <label style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <input
                  type="checkbox"
                  checked={quizSettings.shuffle}
                  onChange={(e) => handleSettingsChange('shuffle', e.target.checked)}
                />
                문제 순서를 랜덤하게 섞기
              </label>
            </div>

            <div style={{ marginBottom: '20px' }}>
              <label style={{ display: 'block', marginBottom: '5px' }}>
                쉬운 문제 수:
              </label>
              <input
                type="number"
                min="0"
                max="10"
                value={quizSettings.easy_count}
                onChange={(e) => handleSettingsChange('easy_count', parseInt(e.target.value))}
                style={{
                  width: '100%',
                  padding: '8px',
                  border: '1px solid #ccc',
                  borderRadius: '4px'
                }}
              />
            </div>

            <div style={{ marginBottom: '20px' }}>
              <label style={{ display: 'block', marginBottom: '5px' }}>
                중간 문제 수:
              </label>
              <input
                type="number"
                min="0"
                max="10"
                value={quizSettings.medium_count}
                onChange={(e) => handleSettingsChange('medium_count', parseInt(e.target.value))}
                style={{
                  width: '100%',
                  padding: '8px',
                  border: '1px solid #ccc',
                  borderRadius: '4px'
                }}
              />
            </div>

            <div style={{ marginBottom: '20px' }}>
              <label style={{ display: 'block', marginBottom: '5px' }}>
                어려운 문제 수:
              </label>
              <input
                type="number"
                min="0"
                max="10"
                value={quizSettings.hard_count}
                onChange={(e) => handleSettingsChange('hard_count', parseInt(e.target.value))}
                style={{
                  width: '100%',
                  padding: '8px',
                  border: '1px solid #ccc',
                  borderRadius: '4px'
                }}
              />
            </div>

            <div style={{
              display: 'flex',
              gap: '10px',
              justifyContent: 'flex-end'
            }}>
              <button
                onClick={() => toggleModal('showSettings', false)}
                style={{
                  padding: '10px 20px',
                  backgroundColor: '#757575',
                  color: 'white',
                  border: 'none',
                  borderRadius: '4px',
                  cursor: 'pointer'
                }}
              >
                취소
              </button>
              <button
                onClick={applySettings}
                style={{
                  padding: '10px 20px',
                  backgroundColor: '#1976d2',
                  color: 'white',
                  border: 'none',
                  borderRadius: '4px',
                  cursor: 'pointer'
                }}
              >
                적용
              </button>
            </div>
          </div>
        </div>
      )}

      {/* 확인 모달들 */}
      {showConfirmModal && (
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          backgroundColor: 'rgba(0, 0, 0, 0.5)',
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          zIndex: 1000
        }}>
          <div style={{
            backgroundColor: 'white',
            padding: '30px',
            borderRadius: '8px',
            textAlign: 'center',
            maxWidth: '400px',
            width: '90%'
          }}>
            <h3 style={{ marginBottom: '15px' }}>퀴즈 제출</h3>
            <p style={{ marginBottom: '20px' }}>
              정말로 퀴즈를 제출하시겠습니까?<br/>
              답변한 문제: {Object.keys(answers).filter(id => answers[id]?.trim()).length}/{questions.length}
            </p>
            <div style={{ display: 'flex', gap: '10px', justifyContent: 'center' }}>
              <button
                onClick={() => toggleModal('showConfirmModal', false)}
                style={{
                  padding: '10px 20px',
                  backgroundColor: '#757575',
                  color: 'white',
                  border: 'none',
                  borderRadius: '4px',
                  cursor: 'pointer'
                }}
              >
                취소
              </button>
              <button
                onClick={handleSubmit}
                style={{
                  padding: '10px 20px',
                  backgroundColor: '#d32f2f',
                  color: 'white',
                  border: 'none',
                  borderRadius: '4px',
                  cursor: 'pointer'
                }}
              >
                제출
              </button>
            </div>
          </div>
        </div>
      )}

      {showSkipModal && (
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          backgroundColor: 'rgba(0, 0, 0, 0.5)',
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          zIndex: 1000
        }}>
          <div style={{
            backgroundColor: 'white',
            padding: '30px',
            borderRadius: '8px',
            textAlign: 'center',
            maxWidth: '400px',
            width: '90%'
          }}>
            <h3 style={{ marginBottom: '15px' }}>문제 건너뛰기</h3>
            <p style={{ marginBottom: '20px' }}>
              이 문제를 건너뛰시겠습니까?<br/>
              나중에 다시 풀 수 있습니다.
            </p>
            <div style={{ display: 'flex', gap: '10px', justifyContent: 'center' }}>
              <button
                onClick={() => toggleModal('showSkipModal', false)}
                style={{
                  padding: '10px 20px',
                  backgroundColor: '#757575',
                  color: 'white',
                  border: 'none',
                  borderRadius: '4px',
                  cursor: 'pointer'
                }}
              >
                취소
              </button>
              <button
                onClick={confirmSkip}
                style={{
                  padding: '10px 20px',
                  backgroundColor: '#ff9800',
                  color: 'white',
                  border: 'none',
                  borderRadius: '4px',
                  cursor: 'pointer'
                }}
              >
                건너뛰기
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default QuizPage;
