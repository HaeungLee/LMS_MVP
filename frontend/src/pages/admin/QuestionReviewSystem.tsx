import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { 
  Eye, 
  CheckCircle, 
  XCircle, 
  Edit3, 
  Clock, 
  Brain,
  Filter,
  Search,
  ChevronLeft,
  ChevronRight,
  Star,
  AlertCircle
} from 'lucide-react';
import { toast } from 'react-hot-toast';
import { adminApi } from '../../shared/services/apiClient';

interface QuestionReviewSystemProps {}

interface ReviewModalProps {
  question: any;
  isOpen: boolean;
  onClose: () => void;
  onReview: (questionId: number, status: string, feedback?: string) => void;
}

const ReviewModal: React.FC<ReviewModalProps> = ({ question, isOpen, onClose, onReview }) => {
  const [reviewStatus, setReviewStatus] = useState<string>('');
  const [feedback, setFeedback] = useState<string>('');
  const [suggestedChanges, setSuggestedChanges] = useState<string>('');

  if (!isOpen || !question) return null;

  const handleSubmitReview = () => {
    if (!reviewStatus) {
      toast.error('검토 결과를 선택해주세요');
      return;
    }
    
    onReview(question.id, reviewStatus, feedback);
    onClose();
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'approved': return 'bg-green-100 text-green-800';
      case 'rejected': return 'bg-red-100 text-red-800';
      case 'needs_revision': return 'bg-yellow-100 text-yellow-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        <div className="p-6 border-b border-gray-200">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-semibold text-gray-900">문제 검토</h3>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600"
            >
              <XCircle className="w-6 h-6" />
            </button>
          </div>
        </div>

        <div className="p-6 space-y-6">
          {/* 문제 정보 */}
          <div className="bg-gray-50 p-4 rounded-lg">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
              <div>
                <span className="text-sm font-medium text-gray-500">과목</span>
                <p className="text-sm text-gray-900">{question.subject}</p>
              </div>
              <div>
                <span className="text-sm font-medium text-gray-500">토픽</span>
                <p className="text-sm text-gray-900">{question.topic}</p>
              </div>
              <div>
                <span className="text-sm font-medium text-gray-500">난이도</span>
                <p className="text-sm text-gray-900">{question.difficulty}</p>
              </div>
            </div>
            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <Brain className="w-4 h-4 text-purple-600 mr-2" />
                <span className="text-sm text-gray-600">AI 신뢰도: {(question.ai_confidence * 100).toFixed(1)}%</span>
              </div>
              <div className="flex items-center">
                <Star className="w-4 h-4 text-yellow-500 mr-1" />
                <span className="text-sm text-gray-600">생성일: {new Date(question.created_at).toLocaleDateString()}</span>
              </div>
            </div>
          </div>

          {/* 문제 내용 */}
          <div>
            <h4 className="text-md font-semibold text-gray-900 mb-3">문제</h4>
            <div className="bg-white border border-gray-200 rounded-lg p-4">
              <p className="text-gray-900 mb-4">{question.question_text}</p>
              
              {question.options && (
                <div className="space-y-2">
                  <p className="text-sm font-medium text-gray-700">선택지:</p>
                  {question.options.map((option: string, index: number) => (
                    <div 
                      key={index} 
                      className={`p-2 rounded ${
                        option.startsWith(question.correct_answer) 
                          ? 'bg-green-50 border border-green-200' 
                          : 'bg-gray-50'
                      }`}
                    >
                      <span className="text-sm">{option}</span>
                      {option.startsWith(question.correct_answer) && (
                        <CheckCircle className="w-4 h-4 text-green-600 inline ml-2" />
                      )}
                    </div>
                  ))}
                </div>
              )}

              {question.explanation && (
                <div className="mt-4 p-3 bg-blue-50 rounded-lg">
                  <p className="text-sm font-medium text-blue-900 mb-1">해설</p>
                  <p className="text-sm text-blue-800">{question.explanation}</p>
                </div>
              )}
            </div>
          </div>

          {/* 검토 양식 */}
          <div>
            <h4 className="text-md font-semibold text-gray-900 mb-3">검토 결과</h4>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  검토 상태 <span className="text-red-500">*</span>
                </label>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                  {[
                    { value: 'approved', label: '승인', icon: CheckCircle, color: 'green' },
                    { value: 'needs_revision', label: '수정 필요', icon: Edit3, color: 'yellow' },
                    { value: 'rejected', label: '거부', icon: XCircle, color: 'red' }
                  ].map((status) => (
                    <button
                      key={status.value}
                      onClick={() => setReviewStatus(status.value)}
                      className={`p-3 border-2 rounded-lg transition-colors ${
                        reviewStatus === status.value
                          ? `border-${status.color}-500 bg-${status.color}-50`
                          : 'border-gray-200 hover:border-gray-300'
                      }`}
                    >
                      <status.icon className={`w-5 h-5 mx-auto mb-2 ${
                        reviewStatus === status.value 
                          ? `text-${status.color}-600` 
                          : 'text-gray-400'
                      }`} />
                      <span className={`text-sm font-medium ${
                        reviewStatus === status.value 
                          ? `text-${status.color}-900` 
                          : 'text-gray-700'
                      }`}>
                        {status.label}
                      </span>
                    </button>
                  ))}
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  검토 의견
                </label>
                <textarea
                  value={feedback}
                  onChange={(e) => setFeedback(e.target.value)}
                  rows={3}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="문제에 대한 검토 의견을 작성해주세요..."
                />
              </div>

              {reviewStatus === 'needs_revision' && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    수정 제안사항
                  </label>
                  <textarea
                    value={suggestedChanges}
                    onChange={(e) => setSuggestedChanges(e.target.value)}
                    rows={3}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="구체적인 수정 제안사항을 작성해주세요..."
                  />
                </div>
              )}
            </div>
          </div>
        </div>

        <div className="p-6 border-t border-gray-200 flex justify-end space-x-3">
          <button
            onClick={onClose}
            className="px-4 py-2 text-gray-700 border border-gray-300 rounded-lg hover:bg-gray-50"
          >
            취소
          </button>
          <button
            onClick={handleSubmitReview}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            검토 완료
          </button>
        </div>
      </div>
    </div>
  );
};

const QuestionReviewSystem: React.FC<QuestionReviewSystemProps> = () => {
  const [currentPage, setCurrentPage] = useState(0);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterSubject, setFilterSubject] = useState('');
  const [filterDifficulty, setFilterDifficulty] = useState('');
  const [selectedQuestion, setSelectedQuestion] = useState<any>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);

  const queryClient = useQueryClient();
  const pageSize = 10;

  // 검토 대기 문제 목록 가져오기
  const { data: questionsData, isLoading } = useQuery({
    queryKey: ['admin', 'pending-questions', currentPage, searchTerm, filterSubject, filterDifficulty],
    queryFn: () => adminApi.getPendingQuestions(currentPage * pageSize, pageSize),
  });

  // 문제 검토 뮤테이션
  const reviewMutation = useMutation({
    mutationFn: ({ questionId, status, feedback }: { questionId: number; status: string; feedback?: string }) =>
      adminApi.reviewQuestion(questionId, { status, feedback }),
    onSuccess: () => {
      toast.success('문제 검토가 완료되었습니다');
      queryClient.invalidateQueries({ queryKey: ['admin', 'pending-questions'] });
    },
    onError: (error: any) => {
      toast.error(`검토 실패: ${error.message}`);
    },
  });

  const handleReviewQuestion = (questionId: number, status: string, feedback?: string) => {
    reviewMutation.mutate({ questionId, status, feedback });
  };

  const openReviewModal = (question: any) => {
    setSelectedQuestion(question);
    setIsModalOpen(true);
  };

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty.toLowerCase()) {
      case 'easy': return 'bg-green-100 text-green-800';
      case 'medium': return 'bg-yellow-100 text-yellow-800';
      case 'hard': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.9) return 'text-green-600';
    if (confidence >= 0.7) return 'text-yellow-600';
    return 'text-red-600';
  };

  if (isLoading) {
    return (
      <div className="p-6">
        <div className="animate-pulse space-y-4">
          <div className="h-8 bg-gray-200 rounded w-1/3"></div>
          {[...Array(5)].map((_, i) => (
            <div key={i} className="h-20 bg-gray-200 rounded-lg"></div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 max-w-7xl mx-auto">
      {/* 헤더 */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">문제 검토 시스템</h1>
        <p className="text-gray-600">AI가 생성한 문제들을 검토하고 승인/거부를 결정합니다</p>
      </div>

      {/* 필터 및 검색 */}
      <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200 mb-6">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">검색</label>
            <div className="relative">
              <Search className="w-5 h-5 absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
              <input
                type="text"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                placeholder="문제 내용 검색..."
                className="w-full pl-10 pr-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">과목</label>
            <select
              value={filterSubject}
              onChange={(e) => setFilterSubject(e.target.value)}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">모든 과목</option>
              <option value="Python">Python</option>
              <option value="JavaScript">JavaScript</option>
              <option value="React">React</option>
              <option value="SQL">SQL</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">난이도</label>
            <select
              value={filterDifficulty}
              onChange={(e) => setFilterDifficulty(e.target.value)}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">모든 난이도</option>
              <option value="easy">쉬움</option>
              <option value="medium">보통</option>
              <option value="hard">어려움</option>
            </select>
          </div>

          <div className="flex items-end">
            <button
              onClick={() => {
                setSearchTerm('');
                setFilterSubject('');
                setFilterDifficulty('');
                setCurrentPage(0);
              }}
              className="w-full bg-gray-100 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-200"
            >
              필터 초기화
            </button>
          </div>
        </div>
      </div>

      {/* 문제 목록 */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200">
        <div className="p-6 border-b border-gray-200">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-semibold text-gray-900">
              검토 대기 문제 ({questionsData?.total || 0}개)
            </h3>
            <div className="flex items-center text-sm text-gray-500">
              <Clock className="w-4 h-4 mr-1" />
              마지막 업데이트: {new Date().toLocaleTimeString()}
            </div>
          </div>
        </div>

        <div className="divide-y divide-gray-200">
          {questionsData?.questions?.map((question: any) => (
            <div key={question.id} className="p-6 hover:bg-gray-50">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center space-x-3 mb-3">
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${getDifficultyColor(question.difficulty)}`}>
                      {question.difficulty}
                    </span>
                    <span className="text-sm text-gray-600">{question.subject}</span>
                    <span className="text-sm text-gray-400">|</span>
                    <span className="text-sm text-gray-600">{question.topic}</span>
                  </div>

                  <h4 className="text-md font-medium text-gray-900 mb-2 line-clamp-2">
                    {question.question_text}
                  </h4>

                  <div className="flex items-center space-x-4 text-sm text-gray-500">
                    <div className="flex items-center">
                      <Brain className="w-4 h-4 mr-1" />
                      <span className={getConfidenceColor(question.ai_confidence)}>
                        신뢰도 {(question.ai_confidence * 100).toFixed(1)}%
                      </span>
                    </div>
                    <div className="flex items-center">
                      <Clock className="w-4 h-4 mr-1" />
                      <span>{new Date(question.created_at).toLocaleDateString()}</span>
                    </div>
                    <div className="flex items-center">
                      <span className="px-2 py-1 bg-orange-100 text-orange-800 rounded-full text-xs">
                        {question.status === 'pending_review' ? '검토 대기' : question.status}
                      </span>
                    </div>
                  </div>
                </div>

                <div className="flex items-center space-x-2 ml-4">
                  <button
                    onClick={() => openReviewModal(question)}
                    className="flex items-center px-3 py-2 text-sm bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                  >
                    <Eye className="w-4 h-4 mr-1" />
                    검토하기
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* 페이지네이션 */}
        <div className="p-6 border-t border-gray-200">
          <div className="flex items-center justify-between">
            <div className="text-sm text-gray-700">
              총 {questionsData?.total || 0}개 중 {currentPage * pageSize + 1}-{Math.min((currentPage + 1) * pageSize, questionsData?.total || 0)}개 표시
            </div>
            <div className="flex items-center space-x-2">
              <button
                onClick={() => setCurrentPage(Math.max(0, currentPage - 1))}
                disabled={currentPage === 0}
                className="p-2 border border-gray-300 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
              >
                <ChevronLeft className="w-4 h-4" />
              </button>
              <span className="px-3 py-1 text-sm">
                {currentPage + 1} / {Math.ceil((questionsData?.total || 0) / pageSize)}
              </span>
              <button
                onClick={() => setCurrentPage(currentPage + 1)}
                disabled={!questionsData?.has_more}
                className="p-2 border border-gray-300 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
              >
                <ChevronRight className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* 검토 모달 */}
      <ReviewModal
        question={selectedQuestion}
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onReview={handleReviewQuestion}
      />
    </div>
  );
};

export default QuestionReviewSystem;
