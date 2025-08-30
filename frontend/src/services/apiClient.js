// Resolve VITE_API_BASE_URL and normalize common malformed values (e.g. ':8000')
const rawBase = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
function normalizeBase(url) {
  if (!url) return 'http://localhost:8000';
  // If value is like ':8000' -> prepend localhost
  if (/^:\d+$/.test(url)) return `http://localhost${url}`;
  // If value is like 'localhost:8000' -> add scheme
  if (/^[^:/]+:\d+$/.test(url) && !/^https?:\/\//.test(url)) return `http://${url}`;
  // If scheme-relative like '//example.com' -> add http:
  if (/^\/\//.test(url)) return `http:${url}`;
  // If missing scheme, add http://
  if (!/^https?:\/\//.test(url)) return `http://${url}`;
  return url.replace(/\/$/, '');
}
const API_BASE_URL = normalizeBase(rawBase) + '/api/v1';
// helpful runtime debug when developing
try { console.debug('[apiClient] API_BASE_URL =', API_BASE_URL); } catch (e) {}

// 공용 타임아웃 래퍼
async function fetchWithTimeout(resource, options = {}) {
  const { timeoutMs = 20000, ...rest } = options; // 기본 타임아웃을 20초로 증가
  const controller = new AbortController();
  const id = setTimeout(() => controller.abort(), timeoutMs);
  try {
    // CSRF: 더블 서브밋 - 쿠키의 csrf_token을 헤더로 동봉 (가능하면)
    const headers = new Headers(rest.headers || {});
    try {
      const method = (rest.method || 'GET').toUpperCase();
      const needsCsrf = !['GET', 'HEAD', 'OPTIONS'].includes(method);
      if (needsCsrf && !headers.has('x-csrf-token')) {
        const csrf = getCsrfToken();
        if (csrf) headers.set('x-csrf-token', csrf);
      }
    } catch {}
    const res = await fetch(resource, { ...rest, headers, signal: controller.signal, credentials: rest.credentials });
    if (res.status !== 401) return res;
    // 401 처리: auth 엔드포인트가 아니고, refresh 쿠키가 있으면 1회 자동 갱신 후 재시도
    const isAuthPath = typeof resource === 'string' && (/\/auth\//.test(resource));
    if (!isAuthPath) {
      try {
        const hasRes = await fetch(`${API_BASE_URL}/auth/has-refresh`, { credentials: 'include' });
        if (hasRes.ok) {
          const { has } = await hasRes.json();
          if (has) {
            const r = await fetch(`${API_BASE_URL}/auth/refresh`, { method: 'POST', credentials: 'include' });
            if (r.ok) {
              return await fetch(resource, { ...rest, headers, signal: controller.signal, credentials: rest.credentials });
            }
          }
        }
      } catch {}
    }
    return res;
  } finally {
    clearTimeout(id);
  }
}

export const getQuestions = async (subject = 'python_basics', options = {}) => {
  try {
    const {
      shuffle = true,
      easy_count = 4,
      medium_count = 4,
      hard_count = 2
    } = options;

    const params = new URLSearchParams({
      shuffle: shuffle.toString(),
      easy_count: easy_count.toString(),
      medium_count: medium_count.toString(),
      hard_count: hard_count.toString()
    });

    // fetchWithTimeout 사용으로 CSRF 토큰과 credentials 자동 설정
    const response = await fetchWithTimeout(`${API_BASE_URL}/questions/${subject}?${params}`, {
      method: 'GET',
      timeoutMs: 15000, // 15초 타임아웃
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error('❌ API 응답 오류:', {
        status: response.status,
        statusText: response.statusText,
        error: errorText
      });
      throw new Error(`HTTP error! status: ${response.status} - ${errorText}`);
    }

    const data = await response.json();
    console.log('✅ 문제 데이터 로드 성공:', data);
    return data;
  } catch (error) {
    console.error('❌ 문제를 가져오는 중 오류가 발생했습니다:', error);
    throw error;
  }
};

export const submitAnswers = async (submission) => {
  const response = await fetchWithTimeout(`${API_BASE_URL}/submit`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    credentials: 'include',
    timeoutMs: 15000,
    body: JSON.stringify(submission),
  });
  if (!response.ok) {
    throw new Error('Failed to submit answers');
  }
  return response.json();
};

export const getFeedback = async (questionId, userAnswer) => {
  try {
    // 피드백 요청 (CSRF 자동 부착 + 쿠키 포함)
    const requestResponse = await fetchWithTimeout(`${API_BASE_URL}/feedback`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      credentials: 'include',
      timeoutMs: 15000,
      body: JSON.stringify({ question_id: questionId, user_answer: userAnswer }),
    });
    
    if (!requestResponse.ok) {
      throw new Error('Failed to request feedback');
    }
    
    const { cache_key } = await requestResponse.json();
    
    // 피드백이 준비될 때까지 폴링
    let attempts = 0;
    const maxAttempts = 30; // 30초 타임아웃
    
    while (attempts < maxAttempts) {
      await new Promise(resolve => setTimeout(resolve, 1000)); // 1초 대기
      
      const statusResponse = await fetchWithTimeout(`${API_BASE_URL}/feedback/${cache_key}`, { timeoutMs: 10000 });
      if (!statusResponse.ok) {
        throw new Error('Failed to check feedback status');
      }
      
      const statusData = await statusResponse.json();
      
      if (statusData.status === 'ready') {
        return statusData;
      }
      
      attempts++;
    }
    
    throw new Error('Feedback generation timeout');
  } catch (error) {
    console.error('Feedback error:', error);
    // 에러 시 기본 피드백 반환
    return {
      feedback: "죄송합니다. 현재 AI 피드백 서비스에 일시적인 문제가 있습니다. 나중에 다시 시도해주세요."
    };
  }
};

// 대시보드 데이터 가져오기
export const getDashboardStats = async (subject) => {
  const url = subject ? `${API_BASE_URL}/dashboard/stats?subject=${encodeURIComponent(subject)}` : `${API_BASE_URL}/dashboard/stats`;
  const response = await fetchWithTimeout(url, { timeoutMs: 10000 });
  if (!response.ok) {
    throw new Error('Failed to fetch dashboard stats');
  }
  return response.json();
};

export const getSubmissionResults = async (submissionId) => {
  // 보안 점검 선행: 접근권한 확인(403 시 차단)
  const guard = await fetchWithTimeout(`${API_BASE_URL}/results/secure/${submissionId}`, { credentials: 'include', timeoutMs: 8000 });
  if (!guard.ok) {
    const msg = guard.status === 403 ? 'Forbidden' : 'Not Found';
    throw new Error(`results guard: ${msg}`);
  }
  const response = await fetchWithTimeout(`${API_BASE_URL}/results/${submissionId}`, { credentials: 'include', timeoutMs: 10000 });
  if (!response.ok) {
    throw new Error('Failed to fetch submission results');
  }
  return response.json();
};

// 학생 학습 지표(커버리지/약점/토픽 진행)
export const getLearningStatus = async (subject = 'python_basics') => {
  const response = await fetchWithTimeout(`${API_BASE_URL}/student/learning-status?subject=${encodeURIComponent(subject)}`, { timeoutMs: 10000 });
  if (!response.ok) {
    throw new Error('Failed to fetch learning status');
  }
  return response.json();
};

// 세션 유지용: 부팅 시 me → 실패하면 refresh → 재시도
export const getMe = async () => {
  const res = await fetchWithTimeout(`${API_BASE_URL}/auth/me`, { timeoutMs: 8000, credentials: 'include' });
  if (!res.ok) throw new Error('unauthorized');
  return res.json();
};

export const refreshSession = async () => {
  const res = await fetchWithTimeout(`${API_BASE_URL}/auth/refresh`, { method: 'POST', timeoutMs: 8000, credentials: 'include' });
  if (!res.ok) throw new Error('refresh failed');
  return res.json();
};

export const hasRefreshCookie = async () => {
  const res = await fetchWithTimeout(`${API_BASE_URL}/auth/has-refresh`, { timeoutMs: 5000, credentials: 'include' });
  if (!res.ok) return { has: false };
  return res.json();
};

export const logout = async () => {
  const res = await fetchWithTimeout(`${API_BASE_URL}/auth/logout`, { method: 'POST', timeoutMs: 8000, credentials: 'include' });
  if (!res.ok) throw new Error('logout failed');
  return res.json();
};

// Admin/Teacher: Questions CRUD
export const adminListQuestions = async ({ subject, topic, q, sort_by, limit = 50, offset = 0 } = {}) => {
  const params = new URLSearchParams();
  if (subject) params.set('subject', subject);
  if (topic) params.set('topic', topic);
  if (q) params.set('q', q);
  if (sort_by) params.set('sort_by', sort_by);
  params.set('limit', String(limit));
  params.set('offset', String(offset));
  const res = await fetchWithTimeout(`${API_BASE_URL}/admin/questions?${params.toString()}`, {
    timeoutMs: 10000,
    credentials: 'include',
  });
  if (!res.ok) throw new Error('list questions failed');
  return res.json();
};

// 학생 인사이트(오늘의 인사이트)
export const getStudentInsights = async (subject = 'python_basics') => {
  const res = await fetchWithTimeout(`${API_BASE_URL}/student/insights?subject=${encodeURIComponent(subject)}`, { timeoutMs: 8000 });
  if (!res.ok) throw new Error('Failed to fetch insights');
  return res.json();
};

export const adminCreateQuestion = async (payload) => {
  const res = await fetchWithTimeout(`${API_BASE_URL}/admin/questions`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    credentials: 'include',
    timeoutMs: 10000,
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error('create question failed');
  return res.json();
};

export const adminUpdateQuestion = async (qid, payload) => {
  const res = await fetchWithTimeout(`${API_BASE_URL}/admin/questions/${qid}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    credentials: 'include',
    timeoutMs: 10000,
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error('update question failed');
  return res.json();
};

export const adminDeleteQuestion = async (qid) => {
  const res = await fetchWithTimeout(`${API_BASE_URL}/admin/questions/${qid}`, {
    method: 'DELETE',
    credentials: 'include',
    timeoutMs: 10000,
  });
  if (!res.ok) throw new Error('delete question failed');
  return res.json();
};

// Teacher dashboard
export const getTeacherDashboardStats = async (subject, groupId) => {
  const params = new URLSearchParams();
  if (subject) params.set('subject', subject);
  if (groupId) params.set('group_id', String(groupId));
  const url = `${API_BASE_URL}/teacher/dashboard/stats?${params.toString()}`;
  const res = await fetchWithTimeout(url, { credentials: 'include', timeoutMs: 10000 });
  if (!res.ok) throw new Error('Failed to fetch teacher dashboard stats');
  return res.json();
};

export const adminImportQuestions = async (file, { dry_run = false } = {}) => {
  const form = new FormData();
  form.append('file', file);
  const url = `${API_BASE_URL}/admin/questions/import?dry_run=${dry_run ? 'true' : 'false'}`;
  const res = await fetchWithTimeout(url, {
    method: 'POST',
    body: form,
    credentials: 'include',
    timeoutMs: 30000,
  });
  if (!res.ok) throw new Error('import questions failed');
  return res.json();
};

// ====== AI Learning APIs ======

export const getDailyLearningPlan = async (subject = 'python_basics') => {
  const url = `${API_BASE_URL}/ai-learning/daily-plan?subject=${encodeURIComponent(subject)}`;
  const res = await fetchWithTimeout(url, { credentials: 'include', timeoutMs: 15000 });
  if (!res.ok) throw new Error('Failed to fetch daily learning plan');
  return res.json();
};

export const generateQuestionsForTopic = async (topic, difficulty = 'easy', count = 5) => {
  const url = `${API_BASE_URL}/ai-learning/generate-questions`;
  const res = await fetchWithTimeout(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ topic, difficulty, count }),
    credentials: 'include',
    timeoutMs: 30000,
  });
  if (!res.ok) throw new Error('Failed to generate questions');
  return res.json();
};

// 단일 문제 생성 (타입 지정)
export const generateSingleQuestion = async (questionType, topic, difficulty) => {
  const url = `${API_BASE_URL}/ai-learning/generate-single-question`;
  const res = await fetchWithTimeout(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ 
      question_type: questionType, 
      topic, 
      difficulty 
    }),
    credentials: 'include',
    timeoutMs: 30000, // 30초 타임아웃
  });
  if (!res.ok) throw new Error('Failed to generate single question');
  return res.json();
};

// 혼합 문제셋 생성
export const generateMixedQuestions = async (topic, difficulty, count = 4) => {
  const url = `${API_BASE_URL}/ai-learning/generate-mixed-questions`;
  const res = await fetchWithTimeout(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ topic, difficulty, count }),
    credentials: 'include',
    timeoutMs: 45000, // 45초 타임아웃 (여러 문제 생성이라 더 길게)
  });
  if (!res.ok) throw new Error('Failed to generate mixed questions');
  return res.json();
};

// 문제 저장 (생성된 AI 문제를 데이터베이스에 저장)
export const saveQuestion = async (questionData) => {
  const url = `${API_BASE_URL}/admin/questions`;
  const res = await fetchWithTimeout(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(questionData),
    credentials: 'include',
    timeoutMs: 10000,
  });
  if (!res.ok) throw new Error('Failed to save question');
  return res.json();
};

export const getAdaptiveQuestions = async (topic) => {
  const url = `${API_BASE_URL}/ai-learning/adaptive-questions?topic=${encodeURIComponent(topic)}`;
  const res = await fetchWithTimeout(url, { credentials: 'include', timeoutMs: 15000 });
  if (!res.ok) throw new Error('Failed to fetch adaptive questions');
  return res.json();
};

// 적응형 난이도 관련 새로운 API 함수들
export const getOptimalDifficulty = async (userId, topic = null, currentDifficulty = null) => {
  const url = `${API_BASE_URL}/ai-features/difficulty/optimal/${userId}`;
  const res = await fetchWithTimeout(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      topic: topic,
      current_difficulty: currentDifficulty
    }),
    credentials: 'include',
    timeoutMs: 15000
  });
  if (!res.ok) throw new Error('Failed to get optimal difficulty');
  return res.json();
};

export const getNextQuestionDifficulty = async (userId, topic) => {
  const url = `${API_BASE_URL}/ai-features/difficulty/next-question/${userId}?topic=${encodeURIComponent(topic)}`;
  const res = await fetchWithTimeout(url, { credentials: 'include', timeoutMs: 15000 });
  if (!res.ok) throw new Error('Failed to get next question difficulty');
  return res.json();
};

export const getClassProgressOverview = async (subject = 'python_basics') => {
  const url = `${API_BASE_URL}/ai-learning/class-overview?subject=${encodeURIComponent(subject)}`;
  const res = await fetchWithTimeout(url, { credentials: 'include', timeoutMs: 15000 });
  if (!res.ok) throw new Error('Failed to fetch class overview');
  return res.json();
};

export const assignLearningTopics = async (studentIds, subject, topicKeys) => {
  const url = `${API_BASE_URL}/ai-learning/assign-learning`;
  const res = await fetchWithTimeout(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ 
      student_ids: studentIds, 
      subject, 
      topic_keys: topicKeys 
    }),
    credentials: 'include',
    timeoutMs: 10000,
  });
  if (!res.ok) throw new Error('Failed to assign learning topics');
  return res.json();
};

export const getLearningRecommendations = async (subject = 'python_basics') => {
  const url = `${API_BASE_URL}/ai-learning/learning-recommendations?subject=${encodeURIComponent(subject)}`;
  const res = await fetchWithTimeout(url, { credentials: 'include', timeoutMs: 10000 });
  if (!res.ok) throw new Error('Failed to fetch learning recommendations');
  return res.json();
};

export const analyzeStudentWeaknesses = async (subject = 'python_basics') => {
  const url = `${API_BASE_URL}/ai-learning/weakness-analysis?subject=${encodeURIComponent(subject)}`;
  const res = await fetchWithTimeout(url, { credentials: 'include', timeoutMs: 10000 });
  if (!res.ok) throw new Error('Failed to analyze weaknesses');
  return res.json();
};

// Beta onboarding registration
export const registerBetaTester = async (payload) => {
  const url = `${API_BASE_URL}/beta/register`;
  const res = await fetchWithTimeout(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    credentials: 'include',
    timeoutMs: 20000,
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    const text = await res.text().catch(() => '');
    throw new Error(text || `Register failed: ${res.status}`);
  }
  return res.json();
};

export const submitQuestionQualityFeedback = async (questionId, qualityScore, feedbackText = '') => {
  const url = `${API_BASE_URL}/ai-learning/question-quality-feedback`;
  const res = await fetchWithTimeout(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ 
      question_id: questionId, 
      quality_score: qualityScore, 
      feedback_text: feedbackText 
    }),
    credentials: 'include',
    timeoutMs: 5000,
  });
  if (!res.ok) throw new Error('Failed to submit quality feedback');
  return res.json();
};

// AI 피드백 요청 - Results 페이지용
export const requestAiFeedback = async (submissionId) => {
  try {
    console.log('🚀 AI 피드백 요청 시작:', submissionId);
    
    const url = `${API_BASE_URL}/ai-learning/feedback/${submissionId}`;
    const res = await fetchWithTimeout(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      timeoutMs: 45000, // AI 모델 응답 시간 충분히 고려하여 45초로 증가하여 30초
    });
    
    console.log('📊 AI 피드백 응답 상태:', res.status, res.statusText);
    
    if (!res.ok) {
      const errorText = await res.text();
      console.error('❌ AI 피드백 API 오류:', errorText);
      throw new Error(`AI 피드백 요청 실패: ${res.status} ${errorText}`);
    }
    
    const data = await res.json();
    console.log('✅ AI 피드백 데이터 수신:', data);
    
    return data;
  } catch (error) {
    console.error('🚨 AI 피드백 요청 중 오류:', error);
    throw error;
  }
};

// EnhancedFeedbackTester용 단일 답안 피드백 요청 (비동기 폴링 방식)
export const submitAnswerForFeedback = async (questionId, questionType, userAnswer, userScore = null) => {
  try {
    console.log('🚀 단일 답안 AI 피드백 요청:', { questionId, questionType, userAnswer, userScore });

    // 1단계: 피드백 생성 요청
    const requestUrl = `${API_BASE_URL}/feedback`;
    const requestRes = await fetchWithTimeout(requestUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'X-CSRF-Token': getCsrfToken() // CSRF 토큰 추가
      },
      body: JSON.stringify({
        question_id: questionId,
        user_answer: userAnswer
      }),
      credentials: 'include',
      timeoutMs: 10000,
    });

    console.log('📊 피드백 요청 응답 상태:', requestRes.status, requestRes.statusText);

    if (!requestRes.ok) {
      const errorText = await requestRes.text();
      console.error('❌ 피드백 요청 API 오류:', {
        status: requestRes.status,
        statusText: requestRes.statusText,
        error: errorText
      });
      throw new Error(`AI 피드백 요청 실패: ${requestRes.status} ${requestRes.statusText}`);
    }

    const requestData = await requestRes.json();
    const cacheKey = requestData.cache_key;
    console.log('✅ 피드백 생성 시작됨. Cache Key:', cacheKey);

    // 2단계: 폴링으로 피드백 완료 대기
    let maxAttempts = 20; // 최대 20번 시도 (20초)
    let attempt = 0;

    while (attempt < maxAttempts) {
      await new Promise(resolve => setTimeout(resolve, 1000)); // 1초 대기
      attempt++;

      try {
        const checkUrl = `${API_BASE_URL}/feedback/${cacheKey}`;
        const checkRes = await fetchWithTimeout(checkUrl, {
          method: 'GET',
          credentials: 'include',
          timeoutMs: 5000,
        });

        if (checkRes.ok) {
          const checkData = await checkRes.json();
          console.log(`🔄 폴링 시도 ${attempt}:`, checkData);

          if (checkData.status === 'ready' && checkData.feedback) {
            console.log('✅ AI 피드백 완료:', checkData.feedback);
            return {
              feedback: checkData.feedback,
              status: 'success'
            };
          }
        }
      } catch (pollError) {
        console.warn(`⚠️ 폴링 시도 ${attempt} 실패:`, pollError);
      }
    }

    throw new Error('AI 피드백 생성 시간 초과 (20초)');

  } catch (error) {
    console.error('🚨 단일 답안 AI 피드백 요청 중 오류:', error);
    throw error;
  }
};

// AI 멘토링 세션 시작
export const startMentoringSession = async (userId, options = {}) => {
  try {
    console.log('🚀 AI 멘토링 세션 시작:', { userId, options });

    const url = `${API_BASE_URL}/ai-features/mentoring/start-session/${userId}`;
    const res = await fetchWithTimeout(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(options),
      credentials: 'include',
      timeoutMs: 45000, // AI 모델 응답 시간 충분히 고려하여 45초로 증가
    });

    console.log('📊 AI 멘토링 세션 시작 응답 상태:', res.status, res.statusText);

    if (!res.ok) {
      const errorText = await res.text();
      console.error('❌ AI 멘토링 세션 시작 오류:', errorText);
      throw new Error(`멘토링 세션 시작 실패: ${res.status} ${errorText}`);
    }

    const data = await res.json();
    console.log('✅ AI 멘토링 세션 시작됨:', data);
    return data;

  } catch (error) {
    console.error('🚨 AI 멘토링 세션 시작 중 오류:', error);
    throw error;
  }
};

// AI 멘토링 대화 계속하기
export const continueMentoringConversation = async (conversationData) => {
  try {
    console.log('🚀 AI 멘토링 대화 계속:', conversationData);

    const url = `${API_BASE_URL}/ai-features/mentoring/continue`;
    const res = await fetchWithTimeout(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(conversationData),
      credentials: 'include',
      timeoutMs: 45000, // AI 모델 응답 시간 충분히 고려하여 45초로 증가
    });

    console.log('📊 AI 멘토링 대화 응답 상태:', res.status, res.statusText);

    if (!res.ok) {
      const errorText = await res.text();
      console.error('❌ AI 멘토링 대화 오류:', errorText);
      throw new Error(`멘토링 대화 실패: ${res.status} ${errorText}`);
    }

    const data = await res.json();
    console.log('✅ AI 멘토링 응답 수신:', data);
    return data;

  } catch (error) {
    console.error('🚨 AI 멘토링 대화 중 오류:', error);
    throw error;
  }
};

// CSRF 토큰 가져오기 함수
function getCsrfToken() {
  // 쿠키에서 CSRF 토큰 추출 (두 이름 모두 지원)
  const cookies = document.cookie.split(';');
  for (let cookie of cookies) {
    const [name, value] = cookie.trim().split('=');
    if (name === 'csrftoken' || name === 'csrf_token') {
      return decodeURIComponent(value || '');
    }
  }
  return '';
}

// Default export 추가
const apiClient = {
  // 기존 함수들
  getDashboardStats,
  getLearningStatus,
  getDailyLearningPlan,
  generateQuestionsForTopic,
  generateSingleQuestion, // 새로 추가
  generateMixedQuestions, // 새로 추가
  saveQuestion, // 문제 저장 함수 추가
  getAdaptiveQuestions,
  getClassProgressOverview,
  assignLearningTopics,
  getLearningRecommendations,
  analyzeStudentWeaknesses,
  submitQuestionQualityFeedback,
  requestAiFeedback, // AI 피드백 함수 추가
  submitAnswerForFeedback, // 단일 답안 피드백 함수 추가
  startMentoringSession, // AI 멘토링 세션 시작
  continueMentoringConversation, // AI 멘토링 대화 계속

  // 새로 추가된 함수들 (POST 요청용)
  post: async (url, data, options = {}) => {
    return fetchWithTimeout(API_BASE_URL + url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
      credentials: 'include',
      timeoutMs: 30000, // 30초로 증가
      ...options
    });
  },

  get: async (url, options = {}) => {
    const response = await fetchWithTimeout(API_BASE_URL + url, {
      method: 'GET',
      credentials: 'include',
      timeoutMs: 15000, // 15초로 증가
      ...options
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error('❌ API GET 요청 오류:', {
        url: API_BASE_URL + url,
        status: response.status,
        statusText: response.statusText,
        error: errorText
      });
      throw new Error(`HTTP error! status: ${response.status} - ${errorText}`);
    }

    return response;
  }
};
// expose helper in default export as well
apiClient.registerBetaTester = registerBetaTester;

export default apiClient;

