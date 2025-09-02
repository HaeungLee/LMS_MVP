/**
 * Dynamic Subjects API Client
 * Phase 8.4: 동적 과목 관리 시스템 프론트엔드
 */

const API_BASE_URL = 'http://127.0.0.1:8000/api/v1/dynamic-subjects';

class DynamicSubjectsAPI {
  /**
   * 과목 목록 조회
   * @param {boolean} activeOnly - 활성 과목만 조회 여부
   * @returns {Promise<Array>} 과목 목록
   */
  async getSubjects(activeOnly = true) {
    try {
      const response = await fetch(`${API_BASE_URL}/subjects?active_only=${activeOnly}`);
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
      const response = await fetch(`${API_BASE_URL}/categories`);
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
   * 특정 과목의 토픽 목록 조회
   * @param {string} subjectKey - 과목 키
   * @returns {Promise<Array>} 토픽 목록
   */
  async getSubjectTopics(subjectKey) {
    try {
      const response = await fetch(`${API_BASE_URL}/subjects/${subjectKey}/topics`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return await response.json();
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
