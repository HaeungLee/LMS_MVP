import React, { useState } from 'react';
import { generateQuestionsForTopic, getClassProgressOverview, assignLearningTopics } from '../services/apiClient';

const AIQuestionGenerator = () => {
  const [generating, setGenerating] = useState(false);
  const [generatedQuestions, setGeneratedQuestions] = useState([]);
  const [formData, setFormData] = useState({
    topic: '',
    difficulty: 'easy',
    count: 5
  });
  const [error, setError] = useState(null);
  const [successMessage, setSuccessMessage] = useState(null);
  const [lastGenerationSummary, setLastGenerationSummary] = useState(null);
  const [classOverview, setClassOverview] = useState(null);

  const topics = [
    '딕셔너리', '리스트', '문자열', '반복문', '조건문', '함수', '집합', '변수와 자료형'
  ];

  const difficulties = [
    { value: 'easy', label: '기초' },
    { value: 'medium', label: '중급' },
    { value: 'hard', label: '고급' }
  ];

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: name === 'count' ? parseInt(value) || 1 : value
    }));
  };

  const handleGenerateQuestions = async () => {
    if (!formData.topic) {
      setError('주제를 선택해주세요.');
      return;
    }

    try {
      setGenerating(true);
      setError(null);
      setSuccessMessage(null);
      setLastGenerationSummary(null);

      const response = await generateQuestionsForTopic(
        formData.topic,
        formData.difficulty,
        formData.count
      );

      if (response.success) {
        setGeneratedQuestions(response.generated_questions);
        
        // 성공 메시지와 요약 정보 설정
        const summary = {
          topic: formData.topic,
          difficulty: difficulties.find(d => d.value === formData.difficulty)?.label,
          requestedCount: formData.count,
          actualCount: response.generated_questions.length,
          generatedAt: new Date().toLocaleString('ko-KR')
        };
        
        setLastGenerationSummary(summary);
        setSuccessMessage(`✅ 문제 생성 완료! ${response.generated_questions.length}개의 "${formData.topic}" 문제가 성공적으로 생성되었습니다.`);
        
        // 5초 후 성공 메시지 자동 사라짐
        setTimeout(() => {
          setSuccessMessage(null);
        }, 5000);
      } else {
        setError('문제 생성에 실패했습니다.');
      }
    } catch (err) {
      console.error('문제 생성 오류:', err);
      setError('문제 생성 중 오류가 발생했습니다: ' + err.message);
    } finally {
      setGenerating(false);
    }
  };

  const handleLoadClassOverview = async () => {
    try {
      const response = await getClassProgressOverview();
      if (response.success) {
        setClassOverview(response.class_overview);
      }
    } catch (err) {
      console.error('반 현황 로드 오류:', err);
      setError('반 현황을 불러오는데 실패했습니다.');
    }
  };

  const handleSaveQuestion = async (question, index) => {
    try {
      // AI 생성 문제 데이터를 DB 저장 형식으로 변환
      const questionData = {
        subject: 'python_basics', // 기본값
        topic: question.topic || formData.topic || 'AI 생성 문제',
        question_type: question.question_type || 'short_answer',
        code_snippet: question.question_text || question.code_snippet || question.question || '',
        correct_answer: question.correct_answer || question.answer || '',
        difficulty: question.difficulty || formData.difficulty || 'medium',
        rubric: question.explanation || question.rubric || '',
        created_by: 'AI Generator',
        is_active: true
      };

      console.log('💾 문제 저장 시도:', questionData);

      // 실제 API 호출
      const response = await apiClient.saveQuestion(questionData);

      // 더 상세한 저장 완료 메시지
      const questionPreview = questionData.code_snippet.length > 50 
        ? questionData.code_snippet.substring(0, 50) + '...' 
        : questionData.code_snippet;

      setSuccessMessage(`✅ 문제 저장 완료! 데이터베이스 ID: ${response.id}`);
      setTimeout(() => setSuccessMessage(null), 5000);

      alert(`✅ 문제 저장 완료!\n\n문제 번호: #${index + 1}\n주제: ${questionData.topic}\n미리보기: ${questionPreview}\n\n문제가 데이터베이스에 저장되었습니다.\nDB ID: ${response.id}`);

    } catch (error) {
      console.error('❌ 문제 저장 실패:', error);
      alert(`❌ 문제 저장 실패!\n\n오류: ${error.message}\n\n관리자에게 문의하세요.`);
    }
  };

  const handleDeleteQuestion = (index) => {
    const question = generatedQuestions[index];
    const questionPreview = question.question_text || question.code_snippet || '문제';
    const truncatedPreview = questionPreview.length > 30 
      ? questionPreview.substring(0, 30) + '...' 
      : questionPreview;
      
    if (confirm(`문제 #${index + 1}을 삭제하시겠습니까?\n\n"${truncatedPreview}"`)) {
      const updated = generatedQuestions.filter((_, i) => i !== index);
      setGeneratedQuestions(updated);
      
      // 성공 메시지 업데이트
      if (updated.length === 0) {
        setSuccessMessage(null);
        setLastGenerationSummary(null);
      } else if (lastGenerationSummary) {
        setLastGenerationSummary({
          ...lastGenerationSummary,
          actualCount: updated.length
        });
      }
    }
  };

  return (
    <div style={styles.container}>
      <div style={styles.header}>
        <h2 style={styles.title}>AI 문제 생성기</h2>
        <p style={styles.subtitle}>수업 진도에 맞는 맞춤형 문제를 AI로 자동 생성하세요</p>
      </div>

      {/* 문제 생성 폼 */}
      <div style={styles.card}>
        <h3 style={styles.cardTitle}>문제 생성 설정</h3>
        
        <div style={styles.formGrid}>
          <div style={styles.formGroup}>
            <label style={styles.label}>주제 선택</label>
            <select 
              name="topic"
              value={formData.topic}
              onChange={handleInputChange}
              style={styles.select}
            >
              <option value="">주제를 선택하세요</option>
              {topics.map(topic => (
                <option key={topic} value={topic}>{topic}</option>
              ))}
            </select>
          </div>

          <div style={styles.formGroup}>
            <label style={styles.label}>난이도</label>
            <select 
              name="difficulty"
              value={formData.difficulty}
              onChange={handleInputChange}
              style={styles.select}
            >
              {difficulties.map(diff => (
                <option key={diff.value} value={diff.value}>{diff.label}</option>
              ))}
            </select>
          </div>

          <div style={styles.formGroup}>
            <label style={styles.label}>문제 개수</label>
            <input
              type="number"
              name="count"
              value={formData.count}
              onChange={handleInputChange}
              min="1"
              max="10"
              style={styles.input}
            />
          </div>

          <div style={styles.formGroup}>
            <button 
              onClick={handleGenerateQuestions}
              disabled={generating || !formData.topic}
              style={{
                ...styles.generateButton,
                ...(generating || !formData.topic ? styles.disabledButton : {})
              }}
            >
              {generating ? '🔄 생성 중...' : '✨ 문제 생성'}
            </button>
          </div>
        </div>
      </div>

      {/* 성공 메시지 */}
      {successMessage && (
        <div style={styles.successCard}>
          <div style={styles.successMessage}>
            <p>{successMessage}</p>
          </div>
          {lastGenerationSummary && (
            <div style={styles.generationSummary}>
              <h4 style={styles.summaryTitle}>생성 요약</h4>
              <div style={styles.summaryGrid}>
                <div style={styles.summaryItem}>
                  <span style={styles.summaryLabel}>주제:</span>
                  <span style={styles.summaryValue}>{lastGenerationSummary.topic}</span>
                </div>
                <div style={styles.summaryItem}>
                  <span style={styles.summaryLabel}>난이도:</span>
                  <span style={styles.summaryValue}>{lastGenerationSummary.difficulty}</span>
                </div>
                <div style={styles.summaryItem}>
                  <span style={styles.summaryLabel}>요청 개수:</span>
                  <span style={styles.summaryValue}>{lastGenerationSummary.requestedCount}개</span>
                </div>
                <div style={styles.summaryItem}>
                  <span style={styles.summaryLabel}>실제 생성:</span>
                  <span style={styles.summaryValue}>{lastGenerationSummary.actualCount}개</span>
                </div>
                <div style={styles.summaryItem}>
                  <span style={styles.summaryLabel}>생성 시간:</span>
                  <span style={styles.summaryValue}>{lastGenerationSummary.generatedAt}</span>
                </div>
              </div>
            </div>
          )}
          <button onClick={() => setSuccessMessage(null)} style={styles.closeButton}>
            닫기
          </button>
        </div>
      )}

      {/* 오류 메시지 */}
      {error && (
        <div style={styles.errorCard}>
          <p>❌ {error}</p>
          <button onClick={() => setError(null)} style={styles.closeButton}>
            닫기
          </button>
        </div>
      )}

      {/* 생성된 문제들 */}
      {generatedQuestions.length > 0 && (
        <div style={styles.card}>
          <div style={styles.resultHeader}>
            <h3 style={styles.cardTitle}>
              생성된 문제 ({generatedQuestions.length}개)
            </h3>
            <div style={styles.resultActions}>
              <button 
                onClick={() => {
                  if (confirm(`모든 생성된 문제 ${generatedQuestions.length}개를 삭제하시겠습니까?\n\n이 작업은 되돌릴 수 없습니다.`)) {
                    setGeneratedQuestions([]);
                    setSuccessMessage(null);
                    setLastGenerationSummary(null);
                  }
                }}
                style={styles.clearButton}
              >
                전체 삭제
              </button>
            </div>
          </div>

          <div style={styles.questionsContainer}>
            {generatedQuestions.map((question, index) => (
              <div key={index} style={styles.questionCard}>
                <div style={styles.questionHeader}>
                  <span style={styles.questionNumber}>문제 #{index + 1}</span>
                  <div style={styles.questionBadges}>
                    <span style={styles.topicBadge}>{question.topic}</span>
                    <span style={styles.difficultyBadge}>
                      {difficulties.find(d => d.value === question.difficulty)?.label}
                    </span>
                  </div>
                </div>

                <div style={styles.questionContent}>
                  <div style={styles.codeSection}>
                    <h4 style={styles.sectionTitle}>코드</h4>
                    <pre style={styles.codeBlock}>
                      {question.code_snippet}
                    </pre>
                  </div>

                  <div style={styles.answerSection}>
                    <h4 style={styles.sectionTitle}>정답</h4>
                    <code style={styles.answerCode}>{question.answer}</code>
                  </div>

                  {question.rubric && (
                    <div style={styles.rubricSection}>
                      <h4 style={styles.sectionTitle}>채점 기준</h4>
                      <p style={styles.rubricText}>{question.rubric}</p>
                    </div>
                  )}

                  {question.explanation && (
                    <div style={styles.explanationSection}>
                      <h4 style={styles.sectionTitle}>해설</h4>
                      <p style={styles.explanationText}>{question.explanation}</p>
                    </div>
                  )}
                </div>

                <div style={styles.questionActions}>
                  <button 
                    onClick={() => handleSaveQuestion(question, index)}
                    style={styles.saveButton}
                  >
                    💾 저장
                  </button>
                  <button 
                    onClick={() => handleDeleteQuestion(index)}
                    style={styles.deleteButton}
                  >
                    🗑️ 삭제
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* 반 현황 개요 */}
      <div style={styles.card}>
        <div style={styles.overviewHeader}>
          <h3 style={styles.cardTitle}>반 학습 현황</h3>
          <button onClick={handleLoadClassOverview} style={styles.loadButton}>
            🔄 현황 불러오기
          </button>
        </div>

        {classOverview && (
          <div style={styles.overviewContent}>
            <div style={styles.statsGrid}>
              <div style={styles.statCard}>
                <span style={styles.statNumber}>{classOverview.total_students}</span>
                <span style={styles.statLabel}>전체 학생</span>
              </div>
              <div style={styles.statCard}>
                <span style={styles.statNumber}>{classOverview.struggling_students?.length || 0}</span>
                <span style={styles.statLabel}>도움 필요</span>
              </div>
              <div style={styles.statCard}>
                <span style={styles.statNumber}>{classOverview.advanced_students?.length || 0}</span>
                <span style={styles.statLabel}>우수 학생</span>
              </div>
            </div>

            {classOverview.struggling_students?.length > 0 && (
              <div style={styles.strugglingSection}>
                <h4 style={styles.sectionTitle}>⚠️ 도움이 필요한 학생들</h4>
                <div style={styles.studentList}>
                  {classOverview.struggling_students.map((student, index) => (
                    <div key={index} style={styles.studentItem}>
                      <span>{student.email}</span>
                      <span style={styles.accuracyBadge}>
                        {Math.round(student.avg_accuracy * 100)}%
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

const styles = {
  container: {
    maxWidth: '1000px',
    margin: '0 auto',
    padding: '20px',
    fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
  },

  header: {
    textAlign: 'center',
    marginBottom: '32px',
  },

  title: {
    fontSize: '32px',
    fontWeight: 'bold',
    color: '#1f2937',
    marginBottom: '8px',
  },

  subtitle: {
    fontSize: '16px',
    color: '#6b7280',
    margin: 0,
  },

  card: {
    backgroundColor: '#ffffff',
    borderRadius: '12px',
    boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
    padding: '24px',
    marginBottom: '24px',
    border: '1px solid #e5e7eb',
  },

  cardTitle: {
    fontSize: '20px',
    fontWeight: 'bold',
    color: '#374151',
    marginBottom: '16px',
  },

  formGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
    gap: '16px',
    alignItems: 'end',
  },

  formGroup: {
    display: 'flex',
    flexDirection: 'column',
  },

  label: {
    fontSize: '14px',
    fontWeight: '500',
    color: '#374151',
    marginBottom: '6px',
  },

  select: {
    padding: '8px 12px',
    border: '1px solid #d1d5db',
    borderRadius: '6px',
    fontSize: '14px',
    backgroundColor: '#ffffff',
  },

  input: {
    padding: '8px 12px',
    border: '1px solid #d1d5db',
    borderRadius: '6px',
    fontSize: '14px',
  },

  generateButton: {
    backgroundColor: '#3b82f6',
    color: 'white',
    border: 'none',
    padding: '10px 20px',
    borderRadius: '6px',
    fontSize: '14px',
    fontWeight: '500',
    cursor: 'pointer',
    transition: 'all 0.2s',
  },

  disabledButton: {
    backgroundColor: '#9ca3af',
    cursor: 'not-allowed',
  },

  errorCard: {
    backgroundColor: '#fef2f2',
    border: '1px solid #fecaca',
    borderRadius: '8px',
    padding: '16px',
    marginBottom: '20px',
    color: '#991b1b',
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
  },

  closeButton: {
    backgroundColor: 'transparent',
    border: 'none',
    color: '#991b1b',
    cursor: 'pointer',
    fontSize: '14px',
  },

  resultHeader: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '20px',
  },

  resultActions: {
    display: 'flex',
    gap: '8px',
  },

  clearButton: {
    backgroundColor: '#ef4444',
    color: 'white',
    border: 'none',
    padding: '6px 12px',
    borderRadius: '4px',
    fontSize: '12px',
    cursor: 'pointer',
  },

  questionsContainer: {
    display: 'flex',
    flexDirection: 'column',
    gap: '16px',
  },

  questionCard: {
    border: '1px solid #e5e7eb',
    borderRadius: '8px',
    padding: '16px',
    backgroundColor: '#f9fafb',
  },

  questionHeader: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '12px',
  },

  questionNumber: {
    fontSize: '16px',
    fontWeight: 'bold',
    color: '#374151',
  },

  questionBadges: {
    display: 'flex',
    gap: '8px',
  },

  topicBadge: {
    backgroundColor: '#3b82f6',
    color: 'white',
    padding: '2px 8px',
    borderRadius: '12px',
    fontSize: '12px',
  },

  difficultyBadge: {
    backgroundColor: '#10b981',
    color: 'white',
    padding: '2px 8px',
    borderRadius: '12px',
    fontSize: '12px',
  },

  questionContent: {
    marginBottom: '16px',
  },

  codeSection: {
    marginBottom: '12px',
  },

  sectionTitle: {
    fontSize: '14px',
    fontWeight: '600',
    color: '#374151',
    marginBottom: '6px',
  },

  codeBlock: {
    backgroundColor: '#1f2937',
    color: '#f9fafb',
    padding: '12px',
    borderRadius: '6px',
    fontSize: '13px',
    fontFamily: 'Monaco, Consolas, "Courier New", monospace',
    overflow: 'auto',
    margin: 0,
  },

  answerSection: {
    marginBottom: '12px',
  },

  answerCode: {
    backgroundColor: '#dcfce7',
    color: '#166534',
    padding: '4px 8px',
    borderRadius: '4px',
    fontSize: '13px',
    fontFamily: 'Monaco, Consolas, "Courier New", monospace',
  },

  rubricSection: {
    marginBottom: '12px',
  },

  rubricText: {
    fontSize: '14px',
    color: '#4b5563',
    margin: 0,
    padding: '8px',
    backgroundColor: '#f3f4f6',
    borderRadius: '4px',
  },

  explanationSection: {
    marginBottom: '12px',
  },

  explanationText: {
    fontSize: '14px',
    color: '#4b5563',
    margin: 0,
    padding: '8px',
    backgroundColor: '#eff6ff',
    borderRadius: '4px',
  },

  questionActions: {
    display: 'flex',
    gap: '8px',
  },

  saveButton: {
    backgroundColor: '#10b981',
    color: 'white',
    border: 'none',
    padding: '6px 12px',
    borderRadius: '4px',
    fontSize: '12px',
    cursor: 'pointer',
  },

  deleteButton: {
    backgroundColor: '#ef4444',
    color: 'white',
    border: 'none',
    padding: '6px 12px',
    borderRadius: '4px',
    fontSize: '12px',
    cursor: 'pointer',
  },

  overviewHeader: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '16px',
  },

  loadButton: {
    backgroundColor: '#6b7280',
    color: 'white',
    border: 'none',
    padding: '8px 16px',
    borderRadius: '6px',
    fontSize: '14px',
    cursor: 'pointer',
  },

  overviewContent: {
    display: 'flex',
    flexDirection: 'column',
    gap: '16px',
  },

  statsGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(3, 1fr)',
    gap: '16px',
  },

  statCard: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    padding: '16px',
    backgroundColor: '#f3f4f6',
    borderRadius: '8px',
  },

  statNumber: {
    fontSize: '24px',
    fontWeight: 'bold',
    color: '#1f2937',
  },

  statLabel: {
    fontSize: '12px',
    color: '#6b7280',
    marginTop: '4px',
  },

  strugglingSection: {
    borderTop: '1px solid #e5e7eb',
    paddingTop: '16px',
  },

  studentList: {
    display: 'flex',
    flexDirection: 'column',
    gap: '8px',
  },

  studentItem: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: '8px 12px',
    backgroundColor: '#fef2f2',
    borderRadius: '6px',
  },

  accuracyBadge: {
    backgroundColor: '#ef4444',
    color: 'white',
    padding: '2px 6px',
    borderRadius: '10px',
    fontSize: '12px',
  },

  // 성공 메시지 스타일
  successCard: {
    backgroundColor: '#f0fdf4',
    border: '1px solid #bbf7d0',
    borderRadius: '8px',
    padding: '20px',
    marginBottom: '20px',
    boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
  },

  successMessage: {
    marginBottom: '16px',
  },

  generationSummary: {
    backgroundColor: 'white',
    border: '1px solid #dcfce7',
    borderRadius: '6px',
    padding: '16px',
    marginBottom: '16px',
  },

  summaryTitle: {
    margin: '0 0 12px 0',
    fontSize: '16px',
    fontWeight: 'bold',
    color: '#166534',
  },

  summaryGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
    gap: '8px',
  },

  summaryItem: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: '8px 0',
    borderBottom: '1px solid #f0f0f0',
  },

  summaryLabel: {
    fontWeight: '500',
    color: '#374151',
  },

  summaryValue: {
    fontWeight: 'bold',
    color: '#059669',
  },
};

export default AIQuestionGenerator;
