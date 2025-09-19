/**
 * Subject Detail Modal Component
 * Phase 8.4: 과목 상세 정보 및 토픽 목록 표시
 */

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import dynamicSubjectsAPI from '../../services/dynamicSubjectsApi';

const SubjectDetailModal = ({ subject, isOpen, onClose }) => {
  const [topics, setTopics] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (isOpen && subject) {
      loadTopics();
    }
  }, [isOpen, subject]);

  const loadTopics = async () => {
    try {
      setLoading(true);
      setError(null);
      const topicsData = await dynamicSubjectsAPI.getSubjectTopics(subject.key);
      setTopics(topicsData);
    } catch (err) {
      setError('토픽 데이터를 불러오는데 실패했습니다.');
      console.error('Error loading topics:', err);
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen || !subject) return null;

  const getDifficultyColor = (level) => {
    switch (level) {
      case 'beginner': return 'bg-green-100 text-green-800';
      case 'intermediate': return 'bg-yellow-100 text-yellow-800';
      case 'advanced': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getDifficultyLabel = (level) => {
    switch (level) {
      case 'beginner': return '초급';
      case 'intermediate': return '중급';
      case 'advanced': return '고급';
      default: return '미정';
    }
  };

  if (!isOpen || !subject) {
    return null;
  }

  return (
    <AnimatePresence>
      <motion.div 
        className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        transition={{ duration: 0.2 }}
        onClick={onClose}
      >
        <motion.div 
          className="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-hidden flex flex-col"
          initial={{ scale: 0.9, opacity: 0, y: 20 }}
          animate={{ scale: 1, opacity: 1, y: 0 }}
          exit={{ scale: 0.9, opacity: 0, y: 20 }}
          transition={{ duration: 0.3, ease: "easeOut" }}
          onClick={(e) => e.stopPropagation()}
        >
        {/* 헤더 */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <div className="flex items-center">
            {subject.icon_name && (
              <span className="text-3xl mr-4">{subject.icon_name}</span>
            )}
            <div>
              <h2 className="text-2xl font-bold text-gray-900">{subject.name}</h2>
              <div className="flex items-center mt-2 space-x-3">
                <span className="text-sm text-gray-500">#{subject.key}</span>
                <span
                  className={`px-2 py-1 rounded-full text-xs font-medium ${getDifficultyColor(subject.difficulty_level)}`}
                >
                  {getDifficultyLabel(subject.difficulty_level)}
                </span>
                <span className={`px-2 py-1 rounded-full text-xs ${
                  subject.is_active ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                }`}>
                  {subject.is_active ? '활성' : '비활성'}
                </span>
              </div>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* 본문 */}
        <div className="flex-1 overflow-y-auto">
          <div className="p-6">
            {/* 과목 정보 */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
              <div className="space-y-4">
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">과목 정보</h3>
                  {subject.description && (
                    <div className="mb-4">
                      <h4 className="text-sm font-medium text-gray-700 mb-1">설명</h4>
                      <p className="text-gray-600">{subject.description}</p>
                    </div>
                  )}
                  
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <span className="font-medium text-gray-700">예상 소요 시간:</span>
                      <p className="text-gray-600">{subject.estimated_duration || '미정'}</p>
                    </div>
                    <div>
                      <span className="font-medium text-gray-700">생성일:</span>
                      <p className="text-gray-600">
                        {subject.created_at ? new Date(subject.created_at).toLocaleDateString('ko-KR') : '미정'}
                      </p>
                    </div>
                  </div>
                </div>
              </div>

              <div className="space-y-4">
                <h3 className="text-lg font-semibold text-gray-900 mb-2">시각적 요소</h3>
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="font-medium text-gray-700">색상:</span>
                    <div className="flex items-center mt-1">
                      <div 
                        className="w-4 h-4 rounded-full mr-2"
                        style={{ backgroundColor: subject.color_code || '#6B7280' }}
                      ></div>
                      <span className="text-gray-600">{subject.color_code || '#6B7280'}</span>
                    </div>
                  </div>
                  <div>
                    <span className="font-medium text-gray-700">정렬 순서:</span>
                    <p className="text-gray-600">{subject.order_index}</p>
                  </div>
                </div>
              </div>
            </div>

            {/* 토픽 목록 */}
            <div>
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-gray-900">토픽 목록</h3>
                <span className="text-sm text-gray-500">{topics.length}개 토픽</span>
              </div>

              {loading ? (
                <div className="flex justify-center items-center py-8">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                  <span className="ml-3 text-gray-600">토픽을 불러오는 중...</span>
                </div>
              ) : error ? (
                <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-center">
                  <div className="text-red-600 mb-2">{error}</div>
                  <button
                    onClick={loadTopics}
                    className="bg-red-600 text-white px-3 py-1 rounded text-sm hover:bg-red-700 transition-colors"
                  >
                    다시 시도
                  </button>
                </div>
              ) : topics.length > 0 ? (
                <div className="space-y-3">
                  {topics.map((topic, index) => (
                    <div
                      key={topic.id}
                      className="bg-gray-50 rounded-lg p-4 border border-gray-200"
                    >
                      <div className="flex items-center justify-between">
                        <div className="flex items-center">
                          <span className="text-sm font-medium text-gray-500 mr-3">
                            #{index + 1}
                          </span>
                          <div>
                            <h4 className="font-medium text-gray-900">
                              {topic.topic_name || topic.name}
                            </h4>
                            <p className="text-sm text-gray-500">키: {topic.key}</p>
                          </div>
                        </div>
                        <div className="flex items-center space-x-2">
                          {topic.is_core && (
                            <span className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full">
                              핵심
                            </span>
                          )}
                          <span className="text-sm text-gray-500">
                            가중치: {topic.weight}
                          </span>
                        </div>
                      </div>
                      
                      {topic.description && (
                        <p className="mt-2 text-sm text-gray-600">{topic.description}</p>
                      )}
                      
                      <div className="mt-2 flex items-center text-xs text-gray-500 space-x-4">
                        <span>순서: {topic.display_order}</span>
                        {topic.estimated_duration && (
                          <span>소요시간: {topic.estimated_duration}</span>
                        )}
                        {topic.difficulty_level && (
                          <span
                            className={`px-2 py-1 rounded-full ${getDifficultyColor(topic.difficulty_level)}`}
                          >
                            {getDifficultyLabel(topic.difficulty_level)}
                          </span>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8">
                  <svg className="mx-auto h-8 w-8 text-gray-400 mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
                  </svg>
                  <p className="text-gray-500">토픽이 없습니다.</p>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* 푸터 */}
        <div className="border-t border-gray-200 px-6 py-4 bg-gray-50">
          <div className="flex justify-end">
            <motion.button
              onClick={onClose}
              className="bg-gray-600 text-white px-4 py-2 rounded-lg hover:bg-gray-700 transition-colors"
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              닫기
            </motion.button>
          </div>
        </div>
          </motion.div>
      </motion.div>
    </AnimatePresence>
  );
};

export default SubjectDetailModal;
