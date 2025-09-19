// API 호환성을 위한 re-export 파일
// apiClient.js의 함수들을 다시 export하여 기존 import 구문과 호환성 유지

export { 
  getQuestions, 
  submitAnswers,
  // 기타 필요한 함수들도 export
  fetchWithTimeout,
  getCsrfToken,
  getMe,
  refreshAuth,
  hasRefreshToken,
  login,
  register,
  logout,
  getDashboardStats,
  getResults,
  submitFeedback,
  getFeedback,
  getAdminQuestions,
  createQuestion,
  updateQuestion,
  deleteQuestion,
  getStudentLearningStatus,
  updateLearningProgress
} from './apiClient';

// 기본 export도 제공
import * as apiClient from './apiClient';
export default apiClient;
