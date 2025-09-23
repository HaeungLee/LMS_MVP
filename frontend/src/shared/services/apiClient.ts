// API 클라이언트 - 실제 백엔드 연동
const rawBase = import.meta.env.VITE_API_BASE_URL || '';

function normalizeBase(url: string): string {
  if (!url) return ''; // 개발환경에서는 프록시 사용을 위해 빈 문자열
  // ':8000' -> 'http://localhost:8000'
  if (/^:\d+$/.test(url)) return `http://localhost${url}`;
  // 'localhost:8000' -> 'ht  // AI 커리큘럼 생성
  generateCurriculum: (data: {
    subject_key: string;
    learning_goals: string[];
    difficulty_level: number;
    duration_preference?: string;
    special_requirements?: string[];
  }) => api.post<{
    id: number;
    status: string;
    message: string;
  }>('/ai-curriculum/generate-curriculum', data, { timeoutMs: 120000 }),st:8000'
  if (/^[^:/]+:\d+$/.test(url) && !/^https?:\/\//.test(url)) return `http://${url}`;
  // '//example.com' -> 'http://example.com'
  if (/^\/\//.test(url)) return `http:${url}`;
  // 스킴이 없으면 http:// 추가
  if (!/^https?:\/\//.test(url)) return `http://${url}`;
  return url.replace(/\/$/, '');
}

const API_BASE_URL = normalizeBase(rawBase) + '/api/v1';

// CSRF 토큰 추출 함수
function getCsrfToken(): string | null {
  try {
    const match = document.cookie.match(/csrf_token=([^;]+)/);
    return match ? match[1] : null;
  } catch {
    return null;
  }
}

// 타임아웃이 있는 fetch 래퍼
async function fetchWithTimeout(resource: string, options: RequestInit & { timeoutMs?: number } = {}) {
  const { timeoutMs = 20000, ...rest } = options;
  const controller = new AbortController();
  const id = setTimeout(() => controller.abort(), timeoutMs);
  
  try {
    const headers = new Headers(rest.headers || {});
    
    // 기본 Content-Type 설정
    if (!headers.has('Content-Type') && rest.method && ['POST', 'PUT', 'PATCH'].includes(rest.method.toUpperCase())) {
      headers.set('Content-Type', 'application/json');
    }
    
    // CSRF 토큰 설정
    const method = (rest.method || 'GET').toUpperCase();
    const needsCsrf = !['GET', 'HEAD', 'OPTIONS'].includes(method);
    if (needsCsrf && !headers.has('x-csrf-token')) {
      const csrf = getCsrfToken();
      if (csrf) headers.set('x-csrf-token', csrf);
    }
    
    const response = await fetch(resource, {
      ...rest,
      headers,
      signal: controller.signal,
      credentials: rest.credentials || 'include',
    });
    
    clearTimeout(id);
    return response;
  } catch (error) {
    clearTimeout(id);
    throw error;
  }
}

// API 응답 처리 함수 - 에러 메시지 개선
async function handleResponse<T>(response: Response): Promise<T> {
  const text = await response.text();
  
  if (!response.ok) {
    let errorMessage = `HTTP ${response.status}`;
    
    if (text) {
      try {
        const errorData = JSON.parse(text);
        // FastAPI 표준 에러 형식
        if (errorData.detail) {
          errorMessage = Array.isArray(errorData.detail) 
            ? errorData.detail.map((err: any) => err.msg || err.message).join(', ')
            : errorData.detail;
        } else if (errorData.message) {
          errorMessage = errorData.message;
        } else if (typeof errorData === 'string') {
          errorMessage = errorData;
        }
      } catch {
        // JSON 파싱 실패 시 원본 텍스트 사용
        errorMessage = text || `HTTP ${response.status}`;
      }
    }
    
    throw new Error(errorMessage);
  }
  
  if (!text) return {} as T;
  
  try {
    return JSON.parse(text);
  } catch {
    return text as unknown as T;
  }
}

// 기본 API 함수들
export const api = {
  get: async <T>(endpoint: string, options: { timeoutMs?: number } = {}): Promise<T> => {
    const response = await fetchWithTimeout(`${API_BASE_URL}${endpoint}`, options);
    return handleResponse<T>(response);
  },
  
  post: async <T>(endpoint: string, data?: any, options: { timeoutMs?: number } = {}): Promise<T> => {
    const response = await fetchWithTimeout(`${API_BASE_URL}${endpoint}`, {
      method: 'POST',
      body: data ? JSON.stringify(data) : undefined,
      ...options,
    });
    return handleResponse<T>(response);
  },
  
  put: async <T>(endpoint: string, data?: any, options: { timeoutMs?: number } = {}): Promise<T> => {
    const response = await fetchWithTimeout(`${API_BASE_URL}${endpoint}`, {
      method: 'PUT',
      body: data ? JSON.stringify(data) : undefined,
      ...options,
    });
    return handleResponse<T>(response);
  },
  
  delete: async <T>(endpoint: string, options: { timeoutMs?: number } = {}): Promise<T> => {
    const response = await fetchWithTimeout(`${API_BASE_URL}${endpoint}`, {
      method: 'DELETE',
      ...options,
    });
    return handleResponse<T>(response);
  },
};

// 인증 관련 API - 올바른 엔드포인트 사용
export const authApi = {
  getMe: () => api.get<{ id: number; email: string; role: string; display_name?: string }>('/auth/me'),
  
  login: (data: { email: string; password: string }) => 
    api.post<{ id: number; email: string; role: string; display_name?: string }>('/auth/login', data),
  
  logout: () => api.post<{ message: string }>('/auth/logout'),
  
  register: (data: { email: string; password: string; display_name?: string }) => 
    api.post<{ id: number; email: string; role: string; display_name?: string }>('/auth/register', data),
};

// 대시보드 관련 API - 올바른 엔드포인트 사용
export const dashboardApi = {
  getStats: (userId?: number) => {
    if (userId) {
      // 특정 사용자의 통합 대시보드 데이터 - 정확한 하이픈 경로 사용
      return api.get<{
        success: boolean;
        dashboard: {
          has_data: boolean;
          progress: { value: number; total: number };
          topics: any;
          recent_activity: any[];
          total_questions: number;
          topic_accuracy: any;
          learning: any;
        };
      }>(`/unified-learning/dashboard/${userId}`);
    } else {
      // 현재 사용자의 기본 대시보드
      return api.get<{
        subjects_progress: any[];
        recent_activities: any[];
        daily_streak: number;
        total_problems_solved: number;
        average_score: number;
      }>('/dashboard');
    }
  },
  
  getBetaStats: () => api.get<{
    overview: any;
    daily_activity: any;
    feedback_by_type: any;
    feature_usage: any;
  }>('/beta/dashboard'),
};

// 과목 관련 API (Phase 8) - 올바른 엔드포인트 사용
export const subjectsApi = {
  // 실제 백엔드 엔드포인트: /dynamic-subjects/subjects
  getAll: () => api.get<Array<{
    id: number;
    key: string;
    name: string;
    description?: string;
    difficulty_level?: string;
    estimated_duration?: string;
    icon_name?: string;
    color_code?: string;
    is_active?: boolean;
    order_index?: number;
    topic_count?: number;
    created_at?: string;
  }>>('/dynamic-subjects/subjects'),
  
  getQuestions: (subjectKey: string, limit?: number) => 
    api.get<{ questions: any[] }>(`/questions/${subjectKey}?limit=${limit || 20}`),
  
  getCategories: () => api.get<Array<{
    id: number;
    key: string;
    name: string;
    color_code?: string;
    order_index?: number;
  }>>('/dynamic-subjects/categories'),
  
  getSubjectTopics: (subjectKey: string) => api.get<Array<{
    id: number;
    key: string;
    name: string;
    description?: string;
    subject_key: string;
    weight?: number;
    is_core?: boolean;
    display_order?: number;
    show_in_coverage?: boolean;
  }>>(`/dynamic-subjects/subjects/${subjectKey}/topics`),
};

// 문제 관련 API
export const questionsApi = {
  // 과목별 문제 조회
  getQuestions: (subjectKey: string, params?: {
    limit?: number;
    difficulty?: string;
    topic?: string;
  }) => {
    const query = new URLSearchParams();
    if (params?.limit) query.append('limit', params.limit.toString());
    if (params?.difficulty) query.append('difficulty', params.difficulty);
    if (params?.topic) query.append('topic', params.topic);
    
    return api.get<{
      questions: Array<{
        id: number;
        text: string;
        options?: string[];
        correct_answer?: string;
        question_type: string;
        difficulty_level: string;
        topic?: string;
        explanation?: string;
      }>;
      total: number;
    }>(`/questions/${subjectKey}${query.toString() ? '?' + query.toString() : ''}`);
  },

  // AI 문제 생성 (Phase 10)
  generateQuestions: (data: {
    subject_key: string;
    topic: string;
    difficulty_level: 'beginner' | 'intermediate' | 'advanced';
    count: number;
    question_type: 'multiple_choice' | 'short_answer' | 'coding' | 'essay';
    custom_requirements?: string[];
  }) => api.post<{
    success: boolean;
    questions: Array<{
      id: number;
      text: string;
      options?: string[];
      correct_answer?: string;
      question_type: string;
      difficulty_level: string;
      topic: string;
      explanation?: string;
      ai_generated: boolean;
    }>;
    generation_info: {
      model_used: string;
      generation_time: number;
      quality_score: number;
    };
  }>('/ai-questions/generate', data),

  // 문제 제출
  submitAnswer: (data: {
    question_id: number;
    answer: string;
    time_spent?: number;
  }) => api.post<{
    correct: boolean;
    score: number;
    explanation?: string;
    feedback?: string;
  }>('/submit', data),

  // 문제 피드백
  getFeedback: (submissionId: number) => api.get<{
    feedback: string;
    suggestions: string[];
    next_topics: string[];
  }>(`/feedback/${submissionId}`),
};

// Phase 9 AI 관련 API
export const aiApi = {
  // AI 커리큘럼 생성 (120초 타임아웃)
  generateCurriculum: (data: {
    subject_key: string;
    learning_goals: string[];
    difficulty_level: number;
    duration_preference?: string;
    special_requirements?: string[];
  }) => api.post<{
    id: number;
    status: string;
    message: string;
  }>('/ai-curriculum/generate-curriculum', data, { timeoutMs: 120000 }),

  // 스트리밍 커리큘럼 생성
  generateCurriculumStream: (data: {
    subject_key: string;
    learning_goals: string[];
    difficulty_level: number;
    duration_preference?: string;
    special_requirements?: string[];
  }) => {
    // POST 요청을 위한 fetch 사용
    return fetch(`${API_BASE_URL}/ai-curriculum/generate-curriculum-stream`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'text/event-stream',
      },
      body: JSON.stringify(data),
    });
  },
  
  // 생성된 커리큘럼 조회
  getCurriculum: (id: number) => api.get<{
    id: number;
    status: string;
    generated_syllabus: any;
    learning_goals: string[];
    agent_conversation_log?: string;
  }>(`/ai-curriculum/curricula/${id}`),
  
  // AI 교육 세션 시작
  startTeachingSession: (data: {
    curriculum_id?: number;
    subject_key: string;
    session_preferences?: any;
  }) => api.post<{
    session_id: number;
    status: string;
    message: string;
  }>('/ai-teaching/start-session', data),
  
  // AI 강사와 메시지 교환
  sendTeachingMessage: (data: {
    session_id: number;
    message: string;
    message_type?: string;
  }) => api.post<{
    response: string;
    teaching_guidance?: string;
    suggested_actions?: string[];
    session_progress?: any;
  }>('/ai-teaching/message', data),
  
  // AI 분석 및 피드백
  getAnalysis: (userId: number, analysisType = 'comprehensive') => 
    api.post<{
      analysis: any;
      recommendations: string[];
      insights: any;
    }>(`/ai-features/analysis/${userId}`, { analysis_type: analysisType }),
  
  // 적응형 난이도 추천
  getOptimalDifficulty: (userId: number, data: {
    topic: string;
    current_difficulty: number;
  }) => api.post<{
    recommendation: any;
    confidence_score: number;
    reasoning: string;
  }>(`/ai-features/difficulty/optimal/${userId}`, data),
};

// 학습 분석 관련 API - 통합된 버전
export const analyticsApi = {
  getProgress: (userId: number) => api.get<{
    subjects_progress: any[];
    overall_progress: number;
    recent_activities: any[];
  }>(`/personalization/progress/${userId}`),
  
  // 일일 통계 (실제 존재하는 엔드포인트)
  getDailyStats: (userId: number) => api.get<{
    total_questions: number;
    correct_answers: number;
    accuracy: number;
    study_minutes: number;
    subjects_studied: string[];
  }>(`/stats/user/${userId}/daily`),
  
  // 통합 학습 분석 (정확한 하이픈 경로)
  getUnifiedAnalytics: (userId: number) => api.get<{
    success: boolean;
    data: any;
    message?: string;
  }>(`/unified-learning/analytics/${userId}`),

  // 심층 학습 분석 (Phase 10 고급 기능)
  getDeepAnalysis: (userId: number) => api.get<{
    learning_patterns: Array<{
      pattern: string;
      value: string;
      impact: 'positive' | 'negative';
      confidence: number;
      description: string;
    }>;
    predictive_insights: Array<{
      type: string;
      title: string;
      prediction: string;
      confidence: number;
      recommendation: string;
    }>;
    performance_metrics: {
      accuracy: number;
      response_time: number;
      consistency: number;
      improvement_rate: number;
      engagement_score: number;
    };
  }>(`/analytics/deep-analysis/${userId}`),
};

// 관리자 API
export const adminApi = {
  // 대시보드
  getDashboard: () => api.get<{
    total_users: number;
    active_users: number;
    total_questions: number;
    total_topics: number;
    ai_questions_generated: number;
    system_health_score: number;
    recent_activities: Array<{
      type: string;
      count: number;
      period: string;
    }>;
  }>('/admin/dashboard'),

  // 검토 대기 문제 목록
  getPendingQuestions: (skip: number = 0, limit: number = 10) => 
    api.get<{
      questions: Array<{
        id: number;
        type: string;
        difficulty: string;
        subject: string;
        topic: string;
        question_text: string;
        options?: string[];
        correct_answer?: string;
        explanation?: string;
        created_at: string;
        ai_confidence: number;
        status: string;
      }>;
      total: number;
      has_more: boolean;
    }>(`/admin/questions/pending-review?skip=${skip}&limit=${limit}`),

  // 문제 검토
  reviewQuestion: (questionId: number, data: {
    status: string;
    feedback?: string;
    suggested_changes?: string;
  }) => api.post(`/admin/questions/${questionId}/review`, data),

  // 커리큘럼 템플릿 목록
  getCurriculumTemplates: (skip: number = 0, limit: number = 10, subjectFilter?: string) => {
    const params = new URLSearchParams({ skip: skip.toString(), limit: limit.toString() });
    if (subjectFilter) params.append('subject_filter', subjectFilter);
    return api.get<{
      templates: Array<{
        id: number;
        title: string;
        subject: string;
        difficulty_level: string;
        total_topics: number;
        estimated_duration: string;
        usage_count: number;
        rating: number;
        created_by: string;
        created_at: string;
        last_modified: string;
        is_active: boolean;
        tags: string[];
      }>;
      total: number;
      has_more: boolean;
    }>(`/admin/curriculum/templates?${params.toString()}`);
  },

  // 커리큘럼 템플릿 생성
  createCurriculumTemplate: (data: {
    title: string;
    subject: string;
    difficulty_level: string;
    description?: string;
    topics: Array<{
      title: string;
      description: string;
      estimated_duration: string;
      prerequisites?: string[];
      learning_objectives?: string[];
    }>;
    estimated_total_duration?: string;
    target_audience?: string;
    tags?: string[];
  }) => api.post('/admin/curriculum/template', data),

  // 시스템 건강도
  getSystemHealth: () => api.get<{
    overall_health: number;
    api_response_time: number;
    database_connections: number;
    active_users: number;
    memory_usage: number;
    cpu_usage: number;
    disk_usage: number;
    last_backup: string;
    uptime: string;
    error_rate: number;
    components: Array<{
      name: string;
      status: string;
      response_time: number;
      additional_info?: any;
    }>;
  }>('/admin/system/health'),

  // 사용자 분석
  getUserAnalytics: (period: string = '7d') => 
    api.get<{
      total_users: number;
      new_users: number;
      active_users: number;
      retention_rate: number;
      avg_session_duration: number;
      completion_rate: number;
      user_growth: Array<{
        date: string;
        new_users: number;
        active_users: number;
      }>;
      subject_popularity: Array<{
        subject: string;
        users: number;
        completion_rate: number;
      }>;
    }>(`/admin/analytics/users?period=${period}`),

  // AI 모델 성능
  getAIModelPerformance: () => api.get<{
    curriculum_generator: {
      status: string;
      success_rate: number;
      avg_response_time: number;
      requests_today: number;
      last_training: string;
    };
    question_generator: {
      status: string;
      success_rate: number;
      avg_response_time: number;
      requests_today: number;
      last_training: string;
    };
    ai_teacher: {
      status: string;
      success_rate: number;
      avg_response_time: number;
      requests_today: number;
      last_training: string;
    };
    feedback_analyzer: {
      status: string;
      success_rate: number;
      avg_response_time: number;
      requests_today: number;
      last_training: string;
    };
  }>('/admin/performance/ai-models'),
};

// Phase 10 적응형 학습 API
export const adaptiveLearningApi = {
  // 적응형 추천 생성
  getAdaptiveRecommendation: (data: {
    subject_key: string;
    current_performance: {
      accuracy: number;
      response_time: number;
      consistency: number;
      improvement_rate: number;
      engagement_score: number;
    };
    focus_areas: string[];
  }) => api.post<{
    current_difficulty: number;
    recommended_difficulty: number;
    adjustment_type: string;
    confidence: number;
    reasoning: string;
    suggested_actions: string[];
    estimated_mastery_time?: number;
  }>('/ai-questions/adaptive', data),

  // 현재 성과 지표 조회
  getCurrentPerformance: (userId: number, subjectKey: string) => api.get<{
    accuracy: number;
    response_time: number;
    consistency: number;
    improvement_rate: number;
    engagement_score: number;
    difficulty_comfort_zone: [number, number];
  }>(`/ai-questions/performance/${userId}/${subjectKey}`),
};

// AI 피드백 API
export const feedbackApi = {
  // 피드백 목록 조회
  getFeedbacks: (params: {
    type?: string;
    status?: string;
    user_id?: number;
    skip?: number;
    limit?: number;
  }) => {
    const queryParams = new URLSearchParams();
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined) {
        queryParams.append(key, value.toString());
      }
    });
    return api.get<{
      feedbacks: Array<{
        id: number;
        type: 'curriculum' | 'teaching' | 'question' | 'analysis';
        content: string;
        ai_response: string;
        rating: number;
        user_feedback: string;
        status: 'pending' | 'reviewed' | 'implemented';
        created_at: string;
        user_id: number;
        username: string;
        ai_confidence: number;
      }>;
      total: number;
      has_more: boolean;
    }>(`/feedback/list?${queryParams.toString()}`);
  },

  // 피드백 제출
  submitFeedback: (data: {
    type: 'curriculum' | 'teaching' | 'question' | 'analysis';
    interaction_id: string;
    rating: number;
    feedback_text: string;
    improvement_suggestions?: string[];
  }) => api.post('/feedback/ai-interaction', data),

  // 피드백 상태 업데이트 (관리자용)
  updateFeedbackStatus: (feedbackId: number, data: {
    status: 'pending' | 'reviewed' | 'implemented';
    admin_notes?: string;
  }) => api.put(`/feedback/${feedbackId}/status`, data),

  // 피드백 통계
  getFeedbackStats: () => api.get<{
    total_feedbacks: number;
    average_rating: number;
    satisfaction_rate: number;
    pending_count: number;
    type_distribution: Record<string, number>;
    rating_distribution: Record<string, number>;
  }>('/feedback/stats'),
};

// AI 학습 상담 API (Phase 10)
export const counselingApi = {
  // 사용자 인사이트 조회
  getUserInsights: () => api.get<{
    achievements: Array<{
      type: string;
      title: string;
      message: string;
      icon: string;
    }>;
    progress_stats: {
      weekly_study_hours: number;
      completion_rate: number;
      improvement_rate: number;
    };
    recommendations: Array<{
      type: string;
      title: string;
      description: string;
      priority: 'high' | 'medium' | 'low';
    }>;
  }>('/ai-counseling/insights'),

  // 일일 동기부여 메시지
  getDailyMotivation: () => api.get<{
    message: string;
    type: 'motivation' | 'encouragement' | 'challenge';
    mood_boost_tips: string[];
    personalized: boolean;
  }>('/ai-counseling/daily-motivation'),

  // AI 상담 세션 시작
  startCounselingSession: (data: {
    type: 'motivation' | 'guidance' | 'goal_setting' | 'habit_building';
    initial_message: string;
    mood_score?: number;
  }) => api.post<{
    session_id: string;
    ai_response: string;
    suggestions: string[];
  }>('/ai-counseling/start-session', data),

  // 상담 메시지 전송
  sendCounselingMessage: (data: {
    session_id: string;
    message: string;
    mood_score?: number;
  }) => api.post<{
    ai_response: string;
    mood_analysis: {
      detected_mood: string;
      confidence: number;
      suggestions: string[];
    };
    next_actions: string[];
  }>('/ai-counseling/message', data),

  // 상담 세션 히스토리
  getCounselingHistory: () => api.get<Array<{
    session_id: string;
    type: string;
    started_at: string;
    last_message_at: string;
    mood_trend: number[];
    summary: string;
  }>>('/ai-counseling/history'),

  // 개인화된 학습 목표 설정
  setLearningGoals: (data: {
    goals: Array<{
      title: string;
      description: string;
      target_date: string;
      priority: 'high' | 'medium' | 'low';
    }>;
    motivation_factors: string[];
  }) => api.post('/ai-counseling/goals', data),

  // 습관 형성 도우미
  getHabitRecommendations: () => api.get<{
    daily_habits: Array<{
      habit: string;
      description: string;
      difficulty: 'easy' | 'medium' | 'hard';
      estimated_time: string;
    }>;
    weekly_challenges: Array<{
      challenge: string;
      description: string;
      reward: string;
    }>;
  }>('/ai-counseling/habits'),
};

export default api;