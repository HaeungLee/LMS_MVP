import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import FeedbackModal from '../components/feedback/FeedbackModal';
import { getQuestions, getSubmissionResults } from '../services/apiClient';
import apiClient from '../services/apiClient';

function ResultsPage() {
  const navigate = useNavigate();
  const { submission_id } = useParams();
  const [results, setResults] = useState(null);
  const [questions, setQuestions] = useState({});
  const [selectedQuestion, setSelectedQuestion] = useState(null);
  const [showFeedbackModal, setShowFeedbackModal] = useState(false);
  const [feedbackStatus, setFeedbackStatus] = useState({});
  
  // AI 피드백 관련 상태
  const [aiFeedbackData, setAiFeedbackData] = useState({});
  const [aiFeedbackLoading, setAiFeedbackLoading] = useState({});

  useEffect(() => {
    const load = async () => {
      try {
        if (!submission_id) {
          navigate('/');
          return;
        }
        const data = await getSubmissionResults(submission_id);
        setResults(data);
        await loadQuestions(data);
      } catch (e) {
        console.error(e);
        alert('결과를 볼 수 없습니다. 권한이 없거나 존재하지 않는 결과입니다.');
        navigate('/');
      }
    };
    load();
  }, [navigate, submission_id]);

  const loadQuestions = async (results) => {
    try {
      const questionsData = await getQuestions('python_basics');
      const questionsMap = {};
      questionsData.forEach(q => {
        questionsMap[q.id] = q;
      });
      setQuestions(questionsMap);

      // 피드백 상태 초기화 (점수가 1점 미만인 문제들)
      const needsFeedback = {};
      results.results.forEach(result => {
        if (result.score < 1) {
          needsFeedback[result.question_id] = 'ready';
        }
      });
      setFeedbackStatus(needsFeedback);
    } catch (error) {
      console.error('Failed to load questions:', error);
    }
  };

  // AI 피드백 요청 함수
  const requestAiFeedback = async (result) => {
    const question = questions[result.question_id];
    if (!question) return;

    setAiFeedbackLoading(prev => ({ ...prev, [result.question_id]: true }));

    try {
      const response = await apiClient.post('/ai-learning/submit-answer-with-feedback', {
        question_id: result.question_id,
        answer: result.user_answer,
        question_type: question.question_type || 'short_answer', // 기본값 설정
        question_data: {
          correct_answer: result.correct_answer,
          topic: question.topic || '파이썬 기초',
          difficulty: question.difficulty || 'medium',
          code_snippet: question.code_snippet || '',
          choices: question.choices || [],
          required_keywords: question.required_keywords || [],
          bugs: question.bugs || []
        }
      });

      console.log(`✅ Results 페이지 AI 피드백:`, response.data);
      
      setAiFeedbackData(prev => ({
        ...prev,
        [result.question_id]: response.data
      }));

    } catch (err) {
      console.error(`❌ Results 페이지 AI 피드백 실패:`, err);
      alert('AI 피드백 생성에 실패했습니다: ' + (err.response?.data?.detail || err.message));
    } finally {
      setAiFeedbackLoading(prev => ({ ...prev, [result.question_id]: false }));
    }
  };

  const handleShowFeedback = (result) => {
    const question = questions[result.question_id];
    if (question) {
      // AI 피드백이 없으면 요청
      if (!aiFeedbackData[result.question_id]) {
        requestAiFeedback(result);
      }
      
      setSelectedQuestion({ 
        ...question, 
        userAnswer: result.user_answer, 
        score: result.score,
        aiFeedback: aiFeedbackData[result.question_id]
      });
      setShowFeedbackModal(true);
      setFeedbackStatus(prev => ({
        ...prev,
        [result.question_id]: 'viewed'
      }));
    }
  };

  if (!results) {
    return (
      <div style={{ 
        minHeight: '80vh', 
        display: 'flex', 
        alignItems: 'center', 
        justifyContent: 'center',
        padding: '20px'
      }}>
        <p>결과를 불러오는 중...</p>
      </div>
    );
  }

  const { total_score, max_score, results: questionResults, topic_analysis, summary, recommendations, submitted_at } = results;
  const percentage = Math.round((total_score / max_score) * 100);

  // 약점 토픽(정답률 오름차순 상위 3)
  const sortedWeakTopics = Object.entries(topic_analysis || {})
    .sort((a, b) => (a[1]?.percentage ?? 0) - (b[1]?.percentage ?? 0))
    .slice(0, 3)
    .map(([topic, stats]) => ({ topic, percentage: stats.percentage, correct: stats.correct, total: stats.total }));

  const getExplanation = (r) => {
    if (r.score === 1) {
      return '정답이에요! 개념을 잘 이해하고 있습니다.';
    }
    if (r.score === 0.5) {
      return '거의 맞았습니다. 핵심 키워드가 일부 부족했어요.';
    }
    return `오답입니다. '${r.topic}'의 기본 개념을 복습해보세요.`;
  };

  // 시간 표시는 Phase 1에서 DB 집계 도입 시 반영

  const containerStyle = {
    padding: '20px',
    maxWidth: '1000px',
    margin: '0 auto'
  };

  const headerStyle = {
    backgroundColor: 'white',
    borderRadius: '12px',
    padding: '32px',
    textAlign: 'center',
    marginBottom: '24px',
    boxShadow: '0 4px 6px rgba(0,0,0,0.1)'
  };

  const scoreStyle = {
    fontSize: '48px',
    fontWeight: 'bold',
    color: percentage >= 80 ? '#059669' : percentage >= 60 ? '#f59e0b' : '#dc2626',
    marginBottom: '8px'
  };

  const messageStyle = {
    fontSize: '20px',
    color: '#374151',
    marginBottom: '16px'
  };

  const statsStyle = {
    fontSize: '16px',
    color: '#6b7280'
  };

  const sectionStyle = {
    backgroundColor: 'white',
    borderRadius: '8px',
    padding: '24px',
    marginBottom: '24px',
    boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
  };

  const sectionTitleStyle = {
    fontSize: '20px',
    fontWeight: '600',
    marginBottom: '16px',
    color: '#374151'
  };

  const getScoreIcon = (score) => {
    if (score === 1) return { icon: '✅', color: '#059669' };
    if (score === 0.5) return { icon: '⚠️', color: '#f59e0b' };
    return { icon: '❌', color: '#dc2626' };
  };

  const buttonStyle = {
    backgroundColor: '#3b82f6',
    color: 'white',
    padding: '12px 24px',
    border: 'none',
    borderRadius: '8px',
    fontSize: '16px',
    fontWeight: '500',
    cursor: 'pointer',
    marginRight: '12px'
  };

  return (
    <div style={containerStyle}>
      {/* 결과 헤더 */}
      <div style={headerStyle}>
        <div style={scoreStyle}>{percentage}점</div>
        <div style={messageStyle}>
          {percentage >= 80 ? '🎉 훌륭합니다!' : 
           percentage >= 60 ? '👍 잘했습니다!' : 
           '📚 조금 더 공부해보세요!'}
        </div>
        <div style={statsStyle}>
          {total_score}점 / {max_score}점 ({questionResults.length}문제 중 {questionResults.filter(r => r.score >= 0.5).length}문제 정답)
          {submitted_at && (
            <>
              <br />제출 시각: {new Date(submitted_at).toLocaleString()}
            </>
          )}
          {summary && (
            <>
              <br />
              요약: {summary}
            </>
          )}
        </div>
      </div>

      {/* 주제별 분석 */}
      <div style={sectionStyle}>
        <h2 style={sectionTitleStyle}>📊 주제별 분석</h2>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px' }}>
          {Object.entries(topic_analysis).map(([topic, stats]) => (
            <div key={topic} style={{
              padding: '16px',
              backgroundColor: '#f9fafb',
              borderRadius: '8px',
              textAlign: 'center'
            }}>
              <div style={{ fontSize: '18px', fontWeight: '600', color: '#374151' }}>
                {topic}
              </div>
              <div style={{ 
                fontSize: '24px', 
                fontWeight: 'bold', 
                color: stats.percentage >= 70 ? '#059669' : stats.percentage >= 50 ? '#f59e0b' : '#dc2626',
                margin: '8px 0'
              }}>
                {stats.percentage}%
              </div>
              <div style={{ fontSize: '14px', color: '#6b7280' }}>
                {stats.correct}/{stats.total} 정답
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* 약점 기반 추천 */}
      {sortedWeakTopics.length > 0 && (
        <div style={sectionStyle}>
          <h2 style={sectionTitleStyle}>🎯 약점 기반 추천</h2>
          <div style={{ display:'flex', flexWrap:'wrap', gap:12 }}>
            {sortedWeakTopics.map((w, idx) => (
              <div key={idx} style={{ padding:12, border:'1px solid #e5e7eb', borderRadius:6 }}>
                <div style={{ fontWeight:600 }}>{w.topic}</div>
                <div style={{ fontSize:12, color:'#6b7280' }}>{w.correct}/{w.total} 정답 · {w.percentage}%</div>
              </div>
            ))}
          </div>
          <div style={{ marginTop:12 }}>
            <button onClick={()=>navigate('/quiz')} style={{ ...buttonStyle }}>약점 보완 퀴즈 시작</button>
          </div>
        </div>
      )}

      {/* 문제별 상세 결과 */}
      <div style={sectionStyle}>
        <h2 style={sectionTitleStyle}>📝 문제별 결과</h2>
        <div style={{ overflow: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr style={{ backgroundColor: '#f9fafb' }}>
                <th style={{ padding: '12px', textAlign: 'left', borderBottom: '2px solid #e5e7eb' }}>문제</th>
                <th style={{ padding: '12px', textAlign: 'left', borderBottom: '2px solid #e5e7eb' }}>주제</th>
                <th style={{ padding: '12px', textAlign: 'left', borderBottom: '2px solid #e5e7eb' }}>내 답안</th>
                <th style={{ padding: '12px', textAlign: 'left', borderBottom: '2px solid #e5e7eb' }}>정답</th>
                <th style={{ padding: '12px', textAlign: 'center', borderBottom: '2px solid #e5e7eb' }}>결과</th>
                <th style={{ padding: '12px', textAlign: 'center', borderBottom: '2px solid #e5e7eb' }}>AI 피드백</th>
                <th style={{ padding: '12px', textAlign: 'left', borderBottom: '2px solid #e5e7eb' }}>간단 해설</th>
              </tr>
            </thead>
            <tbody>
              {questionResults.map((result, index) => {
                const scoreInfo = getScoreIcon(result.score);
                return (
                  <tr key={index} style={{ borderBottom: '1px solid #e5e7eb' }}>
                    <td style={{ padding: '12px' }}>문제 {result.question_id}</td>
                    <td style={{ padding: '12px' }}>{result.topic}</td>
                    <td style={{ 
                      padding: '12px',
                      fontFamily: 'Monaco, Consolas, monospace',
                      backgroundColor: '#f3f4f6',
                      borderRadius: '4px'
                    }}>
                      {result.user_answer || '(건너뜀)'}
                    </td>
                    <td style={{ 
                      padding: '12px',
                      fontFamily: 'Monaco, Consolas, monospace',
                      backgroundColor: '#f0fdf4',
                      borderRadius: '4px'
                    }}>
                      {result.correct_answer}
                    </td>
                    <td style={{ 
                      padding: '12px', 
                      textAlign: 'center',
                      color: scoreInfo.color,
                      fontSize: '18px'
                    }}>
                      {scoreInfo.icon}
                    </td>
                    <td style={{ padding: '12px', textAlign: 'center' }}>
                      {result.score < 1 ? (
                        <button
                          onClick={() => handleShowFeedback(result)}
                          disabled={aiFeedbackLoading[result.question_id]}
                          style={{
                            backgroundColor: aiFeedbackLoading[result.question_id] 
                              ? '#9ca3af' 
                              : (feedbackStatus[result.question_id] === 'viewed' ? '#10b981' : '#3b82f6'),
                            color: 'white',
                            border: 'none',
                            padding: '6px 12px',
                            borderRadius: '6px',
                            fontSize: '12px',
                            cursor: aiFeedbackLoading[result.question_id] ? 'not-allowed' : 'pointer'
                          }}
                        >
                          {aiFeedbackLoading[result.question_id] 
                            ? '🔄 분석 중...' 
                            : (aiFeedbackData[result.question_id] 
                                ? '✅ AI 피드백 보기' 
                                : '🤖 AI 피드백 받기')}
                        </button>
                      ) : (
                        <span style={{ color: '#10b981', fontSize: '14px' }}>완벽!</span>
                      )}
                    </td>
                    <td style={{ padding: '12px', color:'#374151' }}>
                      {getExplanation(result)}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* 추천 학습 */}
      {Array.isArray(recommendations) && recommendations.length > 0 && (
        <div style={sectionStyle}>
          <h2 style={sectionTitleStyle}>🎯 추천 학습</h2>
          <ul style={{ margin: 0, paddingLeft: '20px' }}>
            {recommendations.map((rec, idx) => (
              <li key={idx} style={{ marginBottom: '8px', color: '#374151' }}>{rec}</li>
            ))}
          </ul>
        </div>
      )}

      {/* 액션 버튼 */}
      <div style={{ textAlign: 'center' }}>
        <button
          onClick={() => navigate('/quiz')}
          style={buttonStyle}
          onMouseOver={(e) => e.target.style.backgroundColor = '#2563eb'}
          onMouseOut={(e) => e.target.style.backgroundColor = '#3b82f6'}
        >
          다시 퀴즈하기
        </button>
        <button
          onClick={() => navigate('/')}
          style={{ ...buttonStyle, backgroundColor: '#6b7280' }}
          onMouseOver={(e) => e.target.style.backgroundColor = '#4b5563'}
          onMouseOut={(e) => e.target.style.backgroundColor = '#6b7280'}
        >
          대시보드로 돌아가기
        </button>
      </div>

      {/* AI 피드백 모달 */}
      {selectedQuestion && (
        <FeedbackModal
          question={selectedQuestion}
          userAnswer={selectedQuestion.userAnswer}
          score={selectedQuestion.score}
          isOpen={showFeedbackModal}
          onClose={() => setShowFeedbackModal(false)}
          aiFeedback={selectedQuestion.aiFeedback}
        />
      )}
    </div>
  );
}

export default ResultsPage;
