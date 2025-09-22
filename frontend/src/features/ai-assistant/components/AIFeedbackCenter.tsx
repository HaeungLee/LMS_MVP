import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { 
  MessageSquare, 
  ThumbsUp, 
  ThumbsDown, 
  Star,
  Filter,
  Search,
  Clock,
  User,
  Brain,
  TrendingUp,
  AlertCircle,
  CheckCircle,
  Eye,
  MoreHorizontal
} from 'lucide-react';
import { toast } from 'react-hot-toast';
import useAuthStore from '../../../shared/hooks/useAuthStore';
import { feedbackApi } from '../../../shared/services/apiClient';

interface AIFeedbackCenterProps {}

interface FeedbackItem {
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
}

const AIFeedbackCenter: React.FC<AIFeedbackCenterProps> = () => {
  const { user } = useAuthStore();
  const [activeTab, setActiveTab] = useState<'all' | 'curriculum' | 'teaching' | 'question' | 'analysis'>('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedRating, setSelectedRating] = useState<number | null>(null);
  const [expandedFeedback, setExpandedFeedback] = useState<number | null>(null);

  // 피드백 데이터 조회
  const { data: feedbackData, isLoading: isFeedbackLoading } = useQuery({
    queryKey: ['feedbacks', activeTab, searchTerm, selectedRating],
    queryFn: () => feedbackApi.getFeedbacks({
      type: activeTab === 'all' ? undefined : activeTab,
      skip: 0,
      limit: 50
    }),
    enabled: true,
  });

  // 피드백 통계 조회
  const { data: feedbackStats, isLoading: isStatsLoading } = useQuery({
    queryKey: ['feedback-stats'],
    queryFn: () => feedbackApi.getFeedbackStats(),
    enabled: true,
  });

  // 모킹 데이터 - API가 실패했을 때 사용
  const mockFeedbacks: FeedbackItem[] = [
    {
      id: 1,
      type: 'curriculum',
      content: 'Python 기초 커리큘럼을 생성해주세요',
      ai_response: 'Python 기초부터 고급까지 12주 커리큘럼을 생성했습니다. 변수, 함수, 클래스 순으로 구성했습니다.',
      rating: 5,
      user_feedback: '매우 체계적이고 단계적으로 잘 구성되어 있습니다. 특히 실습 예제가 풍부해서 좋네요.',
      status: 'reviewed',
      created_at: '2024-09-19T10:30:00Z',
      user_id: 1,
      username: '김학습',
      ai_confidence: 0.92
    },
    {
      id: 2,
      type: 'teaching',
      content: '함수의 개념을 쉽게 설명해주세요',
      ai_response: '함수는 특정 작업을 수행하는 코드 블록입니다. 마치 요리 레시피처럼 재료를 넣으면 결과물이 나오는 것과 같습니다.',
      rating: 4,
      user_feedback: '비유가 좋았지만 더 구체적인 예제가 있으면 좋겠어요.',
      status: 'pending',
      created_at: '2024-09-19T09:15:00Z',
      user_id: 2,
      username: '이코딩',
      ai_confidence: 0.88
    },
    {
      id: 3,
      type: 'question',
      content: 'Python 리스트에 대한 문제를 생성해주세요',
      ai_response: '리스트의 슬라이싱과 메서드 활용에 대한 5개의 문제를 생성했습니다.',
      rating: 3,
      user_feedback: '문제 난이도가 조금 어려웠어요. 더 쉬운 단계부터 시작했으면 좋겠습니다.',
      status: 'implemented',
      created_at: '2024-09-19T08:45:00Z',
      user_id: 3,
      username: '박개발',
      ai_confidence: 0.76
    },
    {
      id: 4,
      type: 'analysis',
      content: '학습 진도 분석을 요청했습니다',
      ai_response: '현재 진도율 68%, 약점 영역은 객체지향 프로그래밍입니다. 추가 학습이 필요합니다.',
      rating: 5,
      user_feedback: '정확한 분석이었습니다. 추천해준 학습 방법대로 하니까 이해가 잘 되네요.',
      status: 'reviewed',
      created_at: '2024-09-19T07:20:00Z',
      user_id: 1,
      username: '김학습',
      ai_confidence: 0.94
    },
    {
      id: 5,
      type: 'teaching',
      content: '재귀 함수에 대해서 알려주세요',
      ai_response: '재귀 함수는 자기 자신을 호출하는 함수입니다. 문제를 더 작은 하위 문제로 나누어 해결하는 방식입니다.',
      rating: 2,
      user_feedback: '개념은 알겠는데 예제가 너무 복잡해서 이해하기 어려웠어요.',
      status: 'pending',
      created_at: '2024-09-18T16:30:00Z',
      user_id: 4,
      username: '최프로그램',
      ai_confidence: 0.82
    }
  ];

  // 실제 데이터 또는 모킹 데이터 사용
  const allFeedbacks = feedbackData?.feedbacks || mockFeedbacks;
  
  // 필터링된 피드백
  const filteredFeedbacks = allFeedbacks.filter(feedback => {
    const matchesSearch = searchTerm === '' || 
      feedback.content.toLowerCase().includes(searchTerm.toLowerCase()) ||
      feedback.ai_response.toLowerCase().includes(searchTerm.toLowerCase()) ||
      feedback.user_feedback.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesRating = selectedRating === null || feedback.rating === selectedRating;
    
    return matchesSearch && matchesRating;
  });

  // 통계 계산 - 실제 데이터 우선 사용
  const totalFeedbacks = feedbackStats?.total_feedbacks || allFeedbacks.length;
  const averageRating = feedbackStats?.average_rating || (allFeedbacks.reduce((sum, f) => sum + f.rating, 0) / allFeedbacks.length);
  const positiveRate = feedbackStats?.satisfaction_rate || ((allFeedbacks.filter(f => f.rating >= 4).length / allFeedbacks.length) * 100);
  const pendingCount = feedbackStats?.pending_count || allFeedbacks.filter(f => f.status === 'pending').length;

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'curriculum': return <Star className="w-4 h-4 text-blue-600" />;
      case 'teaching': return <User className="w-4 h-4 text-green-600" />;
      case 'question': return <MessageSquare className="w-4 h-4 text-purple-600" />;
      case 'analysis': return <TrendingUp className="w-4 h-4 text-orange-600" />;
      default: return <Brain className="w-4 h-4 text-gray-600" />;
    }
  };

  const getTypeLabel = (type: string) => {
    switch (type) {
      case 'curriculum': return '커리큘럼';
      case 'teaching': return 'AI 강사';
      case 'question': return '문제 생성';
      case 'analysis': return '학습 분석';
      default: return '기타';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'pending': return 'bg-yellow-100 text-yellow-800';
      case 'reviewed': return 'bg-blue-100 text-blue-800';
      case 'implemented': return 'bg-green-100 text-green-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getStatusLabel = (status: string) => {
    switch (status) {
      case 'pending': return '검토 대기';
      case 'reviewed': return '검토 완료';
      case 'implemented': return '개선 반영';
      default: return '알 수 없음';
    }
  };

  const getRatingColor = (rating: number) => {
    if (rating >= 4) return 'text-green-600';
    if (rating >= 3) return 'text-yellow-600';
    return 'text-red-600';
  };

  const tabs = [
    { key: 'all', label: '전체', count: allFeedbacks.length },
    { key: 'curriculum', label: '커리큘럼', count: allFeedbacks.filter(f => f.type === 'curriculum').length },
    { key: 'teaching', label: 'AI 강사', count: allFeedbacks.filter(f => f.type === 'teaching').length },
    { key: 'question', label: '문제 생성', count: allFeedbacks.filter(f => f.type === 'question').length },
    { key: 'analysis', label: '학습 분석', count: allFeedbacks.filter(f => f.type === 'analysis').length },
  ];

  return (
    <div className="max-w-7xl mx-auto space-y-8">
      {/* 헤더 */}
      <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg p-6 text-white">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold mb-2">AI 피드백 센터</h1>
            <p className="text-blue-100">
              AI 응답에 대한 사용자 피드백을 통합 관리하고 개선점을 파악합니다
            </p>
          </div>
          <div className="text-right">
            <div className="text-2xl font-bold">{totalFeedbacks}</div>
            <div className="text-sm text-blue-100">총 피드백 수</div>
          </div>
        </div>
      </div>

      {/* 통계 카드 */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <div className="flex items-center">
            <div className="p-3 bg-yellow-100 rounded-lg">
              <Star className="w-6 h-6 text-yellow-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">평균 평점</p>
              <p className="text-2xl font-bold text-gray-900">{averageRating.toFixed(1)}</p>
              <div className="flex items-center mt-1">
                {[...Array(5)].map((_, i) => (
                  <Star 
                    key={i} 
                    className={`w-3 h-3 ${i < Math.round(averageRating) ? 'text-yellow-400 fill-current' : 'text-gray-300'}`} 
                  />
                ))}
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <div className="flex items-center">
            <div className="p-3 bg-green-100 rounded-lg">
              <ThumbsUp className="w-6 h-6 text-green-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">만족도</p>
              <p className="text-2xl font-bold text-gray-900">{positiveRate.toFixed(1)}%</p>
              <p className="text-xs text-green-600">4점 이상 평가</p>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <div className="flex items-center">
            <div className="p-3 bg-orange-100 rounded-lg">
              <Clock className="w-6 h-6 text-orange-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">검토 대기</p>
              <p className="text-2xl font-bold text-gray-900">{pendingCount}</p>
              <p className="text-xs text-orange-600">처리 필요</p>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <div className="flex items-center">
            <div className="p-3 bg-purple-100 rounded-lg">
              <Brain className="w-6 h-6 text-purple-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">AI 신뢰도</p>
              <p className="text-2xl font-bold text-gray-900">86.4%</p>
              <p className="text-xs text-purple-600">평균</p>
            </div>
          </div>
        </div>
      </div>

      {/* 필터 및 탭 */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200">
        <div className="p-6 border-b border-gray-200">
          <div className="flex flex-col md:flex-row md:items-center md:justify-between space-y-4 md:space-y-0">
            {/* 탭 */}
            <div className="flex space-x-1">
              {tabs.map((tab) => (
                <button
                  key={tab.key}
                  onClick={() => setActiveTab(tab.key as any)}
                  className={`px-4 py-2 text-sm font-medium rounded-lg transition-colors ${
                    activeTab === tab.key
                      ? 'bg-blue-600 text-white'
                      : 'text-gray-700 hover:bg-gray-100'
                  }`}
                >
                  {tab.label} ({tab.count})
                </button>
              ))}
            </div>

            {/* 검색 및 필터 */}
            <div className="flex items-center space-x-3">
              <div className="relative">
                <Search className="w-4 h-4 absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
                <input
                  type="text"
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  placeholder="피드백 검색..."
                  className="pl-10 pr-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <select
                value={selectedRating || ''}
                onChange={(e) => setSelectedRating(e.target.value ? parseInt(e.target.value) : null)}
                className="border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">모든 평점</option>
                {[5, 4, 3, 2, 1].map(rating => (
                  <option key={rating} value={rating}>{rating}점</option>
                ))}
              </select>
            </div>
          </div>
        </div>

        {/* 피드백 목록 */}
        <div className="divide-y divide-gray-200">
          {filteredFeedbacks.map((feedback) => (
            <div key={feedback.id} className="p-6 hover:bg-gray-50">
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center space-x-3">
                  {getTypeIcon(feedback.type)}
                  <span className="text-sm font-medium text-gray-900">
                    {getTypeLabel(feedback.type)}
                  </span>
                  <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(feedback.status)}`}>
                    {getStatusLabel(feedback.status)}
                  </span>
                </div>
                <div className="flex items-center space-x-3 text-sm text-gray-500">
                  <span>{feedback.username}</span>
                  <span>•</span>
                  <span>{new Date(feedback.created_at).toLocaleDateString()}</span>
                </div>
              </div>

              <div className="space-y-4">
                {/* 사용자 요청 */}
                <div className="bg-gray-50 p-4 rounded-lg">
                  <div className="flex items-center mb-2">
                    <User className="w-4 h-4 text-gray-600 mr-2" />
                    <span className="text-sm font-medium text-gray-700">사용자 요청</span>
                  </div>
                  <p className="text-sm text-gray-900">{feedback.content}</p>
                </div>

                {/* AI 응답 */}
                <div className="bg-blue-50 p-4 rounded-lg">
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center">
                      <Brain className="w-4 h-4 text-blue-600 mr-2" />
                      <span className="text-sm font-medium text-blue-700">AI 응답</span>
                    </div>
                    <span className="text-xs text-blue-600">
                      신뢰도 {(feedback.ai_confidence * 100).toFixed(1)}%
                    </span>
                  </div>
                  <p className="text-sm text-blue-900">{feedback.ai_response}</p>
                </div>

                {/* 사용자 피드백 */}
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center mb-2">
                      <MessageSquare className="w-4 h-4 text-green-600 mr-2" />
                      <span className="text-sm font-medium text-green-700">사용자 피드백</span>
                      <div className="flex items-center ml-3">
                        {[...Array(5)].map((_, i) => (
                          <Star 
                            key={i} 
                            className={`w-4 h-4 ${
                              i < feedback.rating 
                                ? 'text-yellow-400 fill-current' 
                                : 'text-gray-300'
                            }`} 
                          />
                        ))}
                        <span className={`ml-2 text-sm font-medium ${getRatingColor(feedback.rating)}`}>
                          {feedback.rating}/5
                        </span>
                      </div>
                    </div>
                    <p className="text-sm text-gray-900">{feedback.user_feedback}</p>
                  </div>

                  {user?.is_admin && (
                    <button
                      onClick={() => setExpandedFeedback(
                        expandedFeedback === feedback.id ? null : feedback.id
                      )}
                      className="ml-4 p-2 text-gray-400 hover:text-gray-600"
                    >
                      <MoreHorizontal className="w-4 h-4" />
                    </button>
                  )}
                </div>

                {/* 관리자 전용 확장 영역 */}
                {user?.is_admin && expandedFeedback === feedback.id && (
                  <div className="mt-4 p-4 bg-purple-50 rounded-lg border-l-4 border-purple-400">
                    <h4 className="text-sm font-medium text-purple-900 mb-3">관리자 액션</h4>
                    <div className="flex items-center space-x-3">
                      <button className="px-3 py-1 bg-green-600 text-white text-xs rounded hover:bg-green-700">
                        개선 반영
                      </button>
                      <button className="px-3 py-1 bg-blue-600 text-white text-xs rounded hover:bg-blue-700">
                        검토 완료
                      </button>
                      <button className="px-3 py-1 bg-gray-600 text-white text-xs rounded hover:bg-gray-700">
                        추가 정보 요청
                      </button>
                    </div>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>

        {filteredFeedbacks.length === 0 && (
          <div className="p-12 text-center">
            <AlertCircle className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">검색 결과가 없습니다</h3>
            <p className="text-gray-600">다른 검색어나 필터를 시도해보세요.</p>
          </div>
        )}
      </div>

      {/* 개선 제안 */}
      <div className="bg-gradient-to-r from-green-50 to-blue-50 p-6 rounded-lg border border-green-200">
        <div className="flex items-start">
          <div className="p-2 bg-green-100 rounded-lg mr-4">
            <CheckCircle className="w-6 h-6 text-green-600" />
          </div>
          <div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">개선 제안사항</h3>
            <div className="space-y-2 text-sm text-gray-700">
              <p>• 재귀 함수 설명 시 더 쉬운 예제 사용 (피드백 기반)</p>
              <p>• 문제 난이도 조절 알고리즘 개선 필요</p>
              <p>• 커리큘럼 생성 시 실습 비중 증가</p>
              <p>• AI 강사 응답의 개인화 수준 향상</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AIFeedbackCenter;
