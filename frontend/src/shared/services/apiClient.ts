// API 클라이언트 - 실제 백엔드 연동
const rawBase = import.meta.env.VITE_API_BASE_URL || '';

function normalizeBase(url: string): string {
  if (!url) return ''; // 개발환경에서는 프록시 사용을 위해 빈 문자열
  // ':8000' -> 'http://localhost:8000'
  if (/^:\d+$/.test(url)) return `http://localhost${url}`;
  // 'localhost:8000' -> 'http://localhost:8000'
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
  get: async <T>(endpoint: string): Promise<T> => {
    const response = await fetchWithTimeout(`${API_BASE_URL}${endpoint}`);
    return handleResponse<T>(response);
  },
  
  post: async <T>(endpoint: string, data?: any): Promise<T> => {
    const response = await fetchWithTimeout(`${API_BASE_URL}${endpoint}`, {
      method: 'POST',
      body: data ? JSON.stringify(data) : undefined,
    });
    return handleResponse<T>(response);
  },
  
  put: async <T>(endpoint: string, data?: any): Promise<T> => {
    const response = await fetchWithTimeout(`${API_BASE_URL}${endpoint}`, {
      method: 'PUT',
      body: data ? JSON.stringify(data) : undefined,
    });
    return handleResponse<T>(response);
  },
  
  delete: async <T>(endpoint: string): Promise<T> => {
    const response = await fetchWithTimeout(`${API_BASE_URL}${endpoint}`, {
      method: 'DELETE',
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

// Phase 9 AI 관련 API
export const aiApi = {
  // AI 커리큘럼 생성
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
  }>('/ai-curriculum/generate', data),
  
  // 생성된 커리큘럼 조회
  getCurriculum: (id: number) => api.get<{
    id: number;
    status: string;
    generated_syllabus: any;
    learning_goals: string[];
    agent_conversation_log?: string;
  }>(`/ai-curriculum/${id}`),
  
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

// 학습 분석 관련 API - 실제 존재하는 엔드포인트만 사용
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
};

export default api;