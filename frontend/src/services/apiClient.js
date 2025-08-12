const API_BASE_URL = 'http://localhost:8000/api/v1';

// 공용 타임아웃 래퍼
async function fetchWithTimeout(resource, options = {}) {
  const { timeoutMs = 10000, ...rest } = options;
  const controller = new AbortController();
  const id = setTimeout(() => controller.abort(), timeoutMs);
  try {
    // CSRF: 더블 서브밋 - 쿠키의 csrf_token을 헤더로 동봉 (가능하면)
    const headers = new Headers(rest.headers || {});
    try {
      const method = (rest.method || 'GET').toUpperCase();
      const needsCsrf = !['GET', 'HEAD', 'OPTIONS'].includes(method);
      if (needsCsrf) {
        const csrf = document.cookie.split('; ').find((x) => x.startsWith('csrf_token='));
        if (csrf && !headers.has('x-csrf-token')) {
          headers.set('x-csrf-token', decodeURIComponent(csrf.split('=')[1]));
        }
      }
    } catch {}
    const res = await fetch(resource, { ...rest, headers, signal: controller.signal });
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
    
    const response = await fetch(`${API_BASE_URL}/questions/${subject}?${params}`);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    console.error('문제를 가져오는 중 오류가 발생했습니다:', error);
    throw error;
  }
};

export const submitAnswers = async (submission) => {
  const response = await fetch(`${API_BASE_URL}/submit`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    credentials: 'include',
    body: JSON.stringify(submission),
  });
  if (!response.ok) {
    throw new Error('Failed to submit answers');
  }
  return response.json();
};

export const getFeedback = async (questionId, userAnswer) => {
  try {
    // 피드백 요청
    const requestResponse = await fetch(`${API_BASE_URL}/feedback`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
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
      
      const statusResponse = await fetch(`${API_BASE_URL}/feedback/${cache_key}`);
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
export const adminListQuestions = async ({ subject, topic, q, limit = 50, offset = 0 } = {}) => {
  const params = new URLSearchParams();
  if (subject) params.set('subject', subject);
  if (topic) params.set('topic', topic);
  if (q) params.set('q', q);
  params.set('limit', String(limit));
  params.set('offset', String(offset));
  const res = await fetchWithTimeout(`${API_BASE_URL}/admin/questions?${params.toString()}`, {
    timeoutMs: 10000,
    credentials: 'include',
  });
  if (!res.ok) throw new Error('list questions failed');
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
export const getTeacherDashboardStats = async (subject) => {
  const url = subject ? `${API_BASE_URL}/teacher/dashboard/stats?subject=${encodeURIComponent(subject)}` : `${API_BASE_URL}/teacher/dashboard/stats`;
  const res = await fetchWithTimeout(url, { credentials: 'include', timeoutMs: 10000 });
  if (!res.ok) throw new Error('Failed to fetch teacher dashboard stats');
  return res.json();
};
