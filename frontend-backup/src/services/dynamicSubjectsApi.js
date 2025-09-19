/**
 * Dynamic Subjects API Client
 * Phase 8.4: 동적 과목 관리 시스템 프론트엔드
 */

const API_BASE_URL = 'http://127.0.0.1:8000/api/v1/dynamic-subjects';

class DynamicSubjectsAPI {
  /**
   * API 요청 헤더 생성 (쿠키 기반 인증 - GET 요청용)
   * @returns {Object} 헤더 객체
   */
  getRequestOptions() {
    return {
      credentials: 'include' // 쿠키 포함, Content-Type 제거
    };
  }

  /**
   * API 요청 헤더 생성 (쿠키 기반 인증 - POST/PUT 요청용)
   * @returns {Object} 헤더 객체
   */
  getRequestOptionsWithContentType() {
    return {
      credentials: 'include', // 쿠키 포함
      headers: {
        'Content-Type': 'application/json'
      }
    };
  }

  /**
   * 과목 목록 조회
   * @param {boolean} activeOnly - 활성 과목만 조회 여부
   * @returns {Promise<Array>} 과목 목록
   */
  async getSubjects(activeOnly = true) {
    try {
      const response = await fetch(`${API_BASE_URL}/subjects?active_only=${activeOnly}`, {
        ...this.getRequestOptions()
      });
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return await response.json();
    } catch (error) {
      console.error('Error fetching subjects:', error);
      throw error;
    }
  }

  /**
   * 카테고리 목록 조회
   * @returns {Promise<Array>} 카테고리 목록
   */
  async getCategories() {
    try {
      const response = await fetch(`${API_BASE_URL}/categories`, {
        ...this.getRequestOptions()
      });
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return await response.json();
    } catch (error) {
      console.error('Error fetching categories:', error);
      throw error;
    }
  }

  /**
   * 특정 과목의 토픽 목록 조회 (수정된 버전)
   * @param {string} subjectKey - 과목 키
   * @returns {Promise<Array>} 토픽 목록
   */
  async getSubjectTopics(subjectKey) {
    try {
      // 올바른 API 경로 사용: /api/v1/simple-topics/{subject_key}
      const response = await fetch(`http://127.0.0.1:8000/api/v1/simple-topics/${subjectKey}`, {
        ...this.getRequestOptions()
      });
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      
      // 기존 형식과 호환되도록 변환
      if (data.success) {
        return {
          success: true,
          topics: data.topics || []
        };
      } else {
        throw new Error(data.error || 'Unknown error');
      }
    } catch (error) {
      console.error('Error fetching subject topics:', error);
      throw error;
    }
  }

  /**
   * 시스템 통계 조회
   * @returns {Promise<Object>} 통계 데이터
   */
  async getStats() {
    try {
      const response = await fetch(`${API_BASE_URL}/stats`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return await response.json();
    } catch (error) {
      console.error('Error fetching stats:', error);
      throw error;
    }
  }

  /**
   * API 상태 확인
   * @returns {Promise<Object>} 상태 정보
   */
  async getHealth() {
    try {
      const response = await fetch(`${API_BASE_URL}/health`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return await response.json();
    } catch (error) {
      console.error('Error checking health:', error);
      throw error;
    }
  }
}

// 싱글톤 인스턴스 생성
const dynamicSubjectsAPI = new DynamicSubjectsAPI();

export default dynamicSubjectsAPI;
