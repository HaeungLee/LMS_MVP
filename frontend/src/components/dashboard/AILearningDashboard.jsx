import React, { useState, useEffect } from 'react';
import { getDailyLearningPlan, getLearningRecommendations, analyzeStudentWeaknesses } from '../../services/apiClient';

const AILearningDashboard = () => {
  const [dailyPlan, setDailyPlan] = useState(null);
  const [recommendations, setRecommendations] = useState(null);
  const [weaknesses, setWeaknesses] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadAILearningData();
  }, []);

  const loadAILearningData = async () => {
    try {
      setLoading(true);
      setError(null);

      // 병렬로 데이터 로드
      const [planRes, recRes, weakRes] = await Promise.allSettled([
        getDailyLearningPlan(),
        getLearningRecommendations(),
        analyzeStudentWeaknesses()
      ]);

      if (planRes.status === 'fulfilled') {
        console.log('📊 Daily Plan Response:', JSON.stringify(planRes.value, null, 2));
        console.log('📋 Daily Plan Data:', JSON.stringify(planRes.value.daily_plan, null, 2));
        setDailyPlan(planRes.value.daily_plan);
      } else {
        console.error('❌ Daily Plan Error:', planRes.reason);
      }
      if (recRes.status === 'fulfilled') {
        setRecommendations(recRes.value);
      }
      if (weakRes.status === 'fulfilled') {
        setWeaknesses(weakRes.value);
      }

    } catch (err) {
      console.error('AI 학습 데이터 로드 실패:', err);
      setError('AI 학습 계획을 불러오는데 실패했습니다.');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div style={styles.container}>
        <div style={styles.loadingCard}>
          <div style={styles.spinner}></div>
          <p>AI가 맞춤 학습 계획을 생성중입니다...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div style={styles.container}>
        <div style={styles.errorCard}>
          <p>❌ {error}</p>
          <button style={styles.retryButton} onClick={loadAILearningData}>
            다시 시도
          </button>
        </div>
      </div>
    );
  }

  return (
    <div style={styles.container}>
      <h2 style={styles.title}>🤖 AI 맞춤 학습 계획</h2>
      
      {/* 오늘의 학습 계획 */}
      {dailyPlan && (
        <div style={styles.card}>
          {console.log('🎯 Rendering dailyPlan:', JSON.stringify(dailyPlan, null, 2))}
          {console.log('🔢 problem_count:', dailyPlan.problem_count)}
          {console.log('⏰ estimated_time:', dailyPlan.estimated_time)}
          {console.log('🎯 target_accuracy:', dailyPlan.target_accuracy)}
          <div style={styles.cardHeader}>
            <h3>오늘의 학습 목표</h3>
            <span style={styles.date}>{new Date().toLocaleDateString('ko-KR')}</span>
          </div>
          
          <div style={styles.planContent}>
            <div style={styles.topicSection}>
              <div style={styles.topicBadge}>
                {dailyPlan.topic}
              </div>
              <div style={styles.difficultyBadge}>
                {getDifficultyLabel(dailyPlan.difficulty)}
              </div>
            </div>
            
            <div style={styles.metricsRow}>
              <div style={styles.metric}>
                <span style={styles.metricLabel}>문제 수</span>
                <span style={styles.metricValue}>{dailyPlan.problem_count}개</span>
              </div>
              <div style={styles.metric}>
                <span style={styles.metricLabel}>예상 시간</span>
                <span style={styles.metricValue}>{Math.round(dailyPlan.estimated_time / 60)}분</span>
              </div>
              <div style={styles.metric}>
                <span style={styles.metricLabel}>목표 정답률</span>
                <span style={styles.metricValue}>{Math.round(dailyPlan.target_accuracy * 100)}%</span>
              </div>
            </div>
            
            {dailyPlan.focus_areas && dailyPlan.focus_areas.length > 0 && (
              <div style={styles.focusAreas}>
                <h4>집중 학습 영역</h4>
                <div style={styles.tagContainer}>
                  {dailyPlan.focus_areas.map((area, index) => (
                    <span key={index} style={styles.focusTag}>
                      {area}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* 학습 추천사항 */}
      {recommendations && (
        <div style={styles.card}>
          <h3 style={styles.cardTitle}>💡 AI 학습 추천</h3>
          
          {recommendations.recommendations && recommendations.recommendations.length > 0 && (
            <div style={styles.recommendationsSection}>
              <h4>📝 학습 가이드</h4>
              <ul style={styles.recommendationsList}>
                {recommendations.recommendations.map((rec, index) => (
                  <li key={index} style={styles.recommendationItem}>
                    {rec}
                  </li>
                ))}
              </ul>
            </div>
          )}
          
          {recommendations.next_topic && (
            <div style={styles.nextTopicSection}>
              <h4>🚀 다음 학습 주제</h4>
              <div style={styles.nextTopicCard}>
                <span style={styles.nextTopicName}>{recommendations.next_topic}</span>
                <span style={styles.nextTopicTime}>
                  예상 소요 시간: {Math.round(recommendations.estimated_time / 60)}분
                </span>
              </div>
            </div>
          )}
        </div>
      )}

      {/* 취약점 분석 */}
      {weaknesses && weaknesses.weaknesses && weaknesses.weaknesses.length > 0 && (
        <div style={styles.card}>
          <h3 style={styles.cardTitle}>🔍 학습 개선 포인트</h3>
          <div style={styles.weaknessesSection}>
            {weaknesses.weaknesses.map((weakness, index) => (
              <div key={index} style={styles.weaknessItem}>
                <span style={styles.weaknessIcon}>⚠️</span>
                <span style={styles.weaknessText}>{weakness}</span>
              </div>
            ))}
          </div>
          <div style={styles.improvementTip}>
            💪 이 영역들을 집중적으로 연습하면 실력이 크게 향상될 거예요!
          </div>
        </div>
      )}

      {/* 새로고침 버튼 */}
      <div style={styles.actionSection}>
        <button style={styles.refreshButton} onClick={loadAILearningData}>
          🔄 학습 계획 새로고침
        </button>
      </div>
    </div>
  );
};

const getDifficultyLabel = (difficulty) => {
  const labels = {
    'easy': '기초',
    'medium': '중급',
    'hard': '고급'
  };
  return labels[difficulty] || difficulty;
};

const styles = {
  container: {
    maxWidth: '800px',
    margin: '0 auto',
    padding: '20px',
    fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
  },
  
  title: {
    fontSize: '28px',
    fontWeight: 'bold',
    color: '#1f2937',
    marginBottom: '24px',
    textAlign: 'center',
  },
  
  card: {
    backgroundColor: '#ffffff',
    borderRadius: '12px',
    boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
    padding: '24px',
    marginBottom: '20px',
    border: '1px solid #e5e7eb',
  },
  
  cardHeader: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '20px',
  },
  
  cardTitle: {
    fontSize: '20px',
    fontWeight: 'bold',
    color: '#374151',
    marginBottom: '16px',
  },
  
  date: {
    fontSize: '14px',
    color: '#6b7280',
    backgroundColor: '#f3f4f6',
    padding: '4px 8px',
    borderRadius: '6px',
  },
  
  planContent: {
    display: 'flex',
    flexDirection: 'column',
    gap: '16px',
  },
  
  topicSection: {
    display: 'flex',
    gap: '12px',
    alignItems: 'center',
  },
  
  topicBadge: {
    backgroundColor: '#3b82f6',
    color: 'white',
    padding: '8px 16px',
    borderRadius: '20px',
    fontSize: '16px',
    fontWeight: '500',
  },
  
  difficultyBadge: {
    backgroundColor: '#10b981',
    color: 'white',
    padding: '4px 12px',
    borderRadius: '12px',
    fontSize: '14px',
  },
  
  metricsRow: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(120px, 1fr))',
    gap: '16px',
  },
  
  metric: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    padding: '12px',
    backgroundColor: '#f9fafb',
    borderRadius: '8px',
  },
  
  metricLabel: {
    fontSize: '12px',
    color: '#6b7280',
    marginBottom: '4px',
  },
  
  metricValue: {
    fontSize: '18px',
    fontWeight: 'bold',
    color: '#1f2937',
  },
  
  focusAreas: {
    marginTop: '8px',
  },
  
  tagContainer: {
    display: 'flex',
    flexWrap: 'wrap',
    gap: '8px',
    marginTop: '8px',
  },
  
  focusTag: {
    backgroundColor: '#fef3c7',
    color: '#92400e',
    padding: '4px 12px',
    borderRadius: '16px',
    fontSize: '14px',
  },
  
  recommendationsSection: {
    marginBottom: '20px',
  },
  
  recommendationsList: {
    listStyle: 'none',
    padding: 0,
    margin: '12px 0',
  },
  
  recommendationItem: {
    padding: '8px 0',
    borderLeft: '3px solid #3b82f6',
    paddingLeft: '12px',
    marginBottom: '8px',
    backgroundColor: '#f8fafc',
    borderRadius: '4px',
  },
  
  nextTopicSection: {
    borderTop: '1px solid #e5e7eb',
    paddingTop: '16px',
  },
  
  nextTopicCard: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: '12px 16px',
    backgroundColor: '#ecfdf5',
    border: '1px solid #10b981',
    borderRadius: '8px',
    marginTop: '8px',
  },
  
  nextTopicName: {
    fontWeight: '500',
    color: '#065f46',
  },
  
  nextTopicTime: {
    fontSize: '14px',
    color: '#059669',
  },
  
  weaknessesSection: {
    display: 'flex',
    flexDirection: 'column',
    gap: '8px',
    marginBottom: '16px',
  },
  
  weaknessItem: {
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
    padding: '8px 12px',
    backgroundColor: '#fef2f2',
    borderRadius: '6px',
  },
  
  weaknessIcon: {
    fontSize: '16px',
  },
  
  weaknessText: {
    color: '#991b1b',
  },
  
  improvementTip: {
    padding: '12px',
    backgroundColor: '#f0f9ff',
    border: '1px solid #0ea5e9',
    borderRadius: '8px',
    color: '#0c4a6e',
    textAlign: 'center',
  },
  
  actionSection: {
    textAlign: 'center',
    marginTop: '24px',
  },
  
  refreshButton: {
    backgroundColor: '#3b82f6',
    color: 'white',
    border: 'none',
    padding: '12px 24px',
    borderRadius: '8px',
    fontSize: '16px',
    cursor: 'pointer',
    transition: 'background-color 0.2s',
  },
  
  loadingCard: {
    textAlign: 'center',
    padding: '40px 20px',
    backgroundColor: '#ffffff',
    borderRadius: '12px',
    boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
  },
  
  spinner: {
    width: '32px',
    height: '32px',
    border: '3px solid #f3f4f6',
    borderTop: '3px solid #3b82f6',
    borderRadius: '50%',
    animation: 'spin 1s linear infinite',
    margin: '0 auto 16px',
  },
  
  errorCard: {
    textAlign: 'center',
    padding: '40px 20px',
    backgroundColor: '#fef2f2',
    borderRadius: '12px',
    border: '1px solid #fecaca',
    color: '#991b1b',
  },
  
  retryButton: {
    backgroundColor: '#dc2626',
    color: 'white',
    border: 'none',
    padding: '8px 16px',
    borderRadius: '6px',
    fontSize: '14px',
    cursor: 'pointer',
    marginTop: '12px',
  }
};

// CSS 애니메이션 추가
const styleSheet = document.createElement('style');
styleSheet.textContent = `
  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }
  
  .ai-learning-dashboard button:hover {
    opacity: 0.9;
    transform: translateY(-1px);
  }
`;
document.head.appendChild(styleSheet);

export default AILearningDashboard;
