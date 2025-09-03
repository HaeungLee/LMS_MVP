// 통합 학습 API 클라이언트 - Mock 데이터 없이 실제 데이터만 사용

const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || '') + '/api/v1';

/**
 * 사용자 통합 학습 분석 가져오기
 * Mock 데이터 없이 실제 데이터만 사용
 */
export const getUnifiedLearningAnalytics = async (userId) => {
  try {
    const response = await fetch(`${API_BASE_URL}/unified-learning/analytics/${userId}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error('통합 학습 분석 조회 실패:', error);
    throw error;
  }
};

/**
 * 통합 대시보드 데이터 가져오기
 * DashboardPage에서 사용할 실제 데이터
 */
export const getUnifiedDashboard = async (userId) => {
  try {
    const response = await fetch(`${API_BASE_URL}/unified-learning/dashboard/${userId}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error('통합 대시보드 조회 실패:', error);
    throw error;
  }
};

/**
 * 개인화 추천 가져오기 
 * Phase 8 과목 시스템 기반
 */
export const getPersonalizedRecommendations = async (userId) => {
  try {
    const response = await fetch(`${API_BASE_URL}/unified-learning/recommendations/${userId}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error('개인화 추천 조회 실패:', error);
    throw error;
  }
};

/**
 * 대시보드 데이터를 기존 형식으로 변환
 * 기존 DashboardPage 컴포넌트와 호환성 유지
 */
export const transformUnifiedDashboardData = (unifiedData) => {
  if (!unifiedData.success || !unifiedData.dashboard.has_data) {
    return null;
  }

  const dashboard = unifiedData.dashboard;
  
  return {
    progress: dashboard.progress,
    topics: dashboard.topics,
    recent_activity: dashboard.recent_activity,
    total_questions: dashboard.total_questions,
    topic_accuracy: dashboard.topic_accuracy,
    learning: dashboard.learning,
    // 추가 메타데이터
    user_profile: dashboard.user_profile,
    recommendations: dashboard.recommendations,
    has_data: dashboard.has_data,
    message: dashboard.message,
    suggestions: dashboard.suggestions
  };
};

/**
 * AI 분석 대시보드용 데이터 변환
 * AIAnalysisDashboard 컴포넌트와 호환성 유지
 */
export const transformAnalyticsForAIDashboard = (unifiedData) => {
  if (!unifiedData.success || !unifiedData.data) {
    return null;
  }

  const analytics = unifiedData.data;
  const patterns = analytics.learning_patterns;
  
  return {
    learner_profile: {
      type: patterns.learner_type,
      phase: patterns.current_phase,
      optimal_session_length: patterns.learner_type === 'fast_learner' ? 45 : 30,
      preferred_difficulty: Math.min(5, Math.max(1, Math.ceil(patterns.overall_accuracy * 5))),
      strengths: _getStrengthsFromPerformance(analytics.subject_performance),
      weaknesses: _getWeaknessesFromPerformance(analytics.subject_performance)
    },
    learning_metrics: {
      overall_accuracy: patterns.overall_accuracy,
      consistency_score: patterns.consistency_score,
      improvement_rate: patterns.improvement_rate,
      engagement_level: _calculateEngagementLevel(analytics.user_profile, patterns)
    },
    recommendations: analytics.recommendations.map(rec => ({
      title: rec.title,
      description: rec.description,
      priority: rec.priority,
      action_type: rec.action_type
    })),
    next_actions: _generateNextActions(analytics.recommendations)
  };
};

// === 헬퍼 함수들 ===

function _getStrengthsFromPerformance(subjectPerformance) {
  const strengths = [];
  
  for (const [subject, data] of Object.entries(subjectPerformance)) {
    if (data.accuracy >= 0.8 && data.total_submissions >= 5) {
      strengths.push(subject);
    }
  }
  
  return strengths.length > 0 ? strengths : ['꾸준한 학습'];
}

function _getWeaknessesFromPerformance(subjectPerformance) {
  const weaknesses = [];
  
  for (const [subject, data] of Object.entries(subjectPerformance)) {
    if (data.accuracy < 0.6 && data.total_submissions >= 3) {
      weaknesses.push(subject);
    }
  }
  
  return weaknesses.length > 0 ? weaknesses : ['기본 개념 정리'];
}

function _calculateEngagementLevel(userProfile, patterns) {
  const totalSubmissions = userProfile.total_submissions;
  const totalSubjects = userProfile.total_subjects;
  
  // 제출 수와 과목 수를 기반으로 참여도 계산
  const submissionScore = Math.min(1.0, totalSubmissions / 50); // 50개를 만점으로
  const subjectScore = Math.min(1.0, totalSubjects / 5); // 5개 과목을 만점으로
  const consistencyScore = patterns.consistency_score || 0;
  
  return (submissionScore * 0.4 + subjectScore * 0.3 + consistencyScore * 0.3);
}

function _generateNextActions(recommendations) {
  return recommendations.slice(0, 3).map((rec, index) => ({
    title: rec.title,
    description: rec.description,
    timeframe: index === 0 ? 'today' : index === 1 ? 'this_week' : 'this_month',
    priority: rec.priority
  }));
}

export default {
  getUnifiedLearningAnalytics,
  getUnifiedDashboard,
  getPersonalizedRecommendations,
  transformUnifiedDashboardData,
  transformAnalyticsForAIDashboard
};
