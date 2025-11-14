/**
 * 감성적 지원 페이지
 * 
 * Phase C: 불완전함을 포용하는 시스템
 */
import { useState, useEffect } from 'react';
import { Heart, MessageCircle, TrendingUp, Sparkles } from 'lucide-react';
import { MoodCheckInModal, MoodCheckInData } from './MoodCheckInModal';
import { SelfComparisonDashboard } from './SelfComparisonDashboard';
import apiClient from '../../shared/services/apiClient';

interface EncouragingMessage {
  id: number;
  message: string;
  message_tone: string;
  trigger_type: string;
  sent_at: string;
  read_at?: string;
}

export function EmotionalSupportPage() {
  const [showMoodModal, setShowMoodModal] = useState(false);
  const [checkInType, setCheckInType] = useState<'before_learning' | 'after_learning' | 'during_break'>('before_learning');
  const [encouragingMessages, setEncouragingMessages] = useState<EncouragingMessage[]>([]);
  const [unreadCount, setUnreadCount] = useState(0);

  useEffect(() => {
    fetchEncouragingMessages();
  }, []);

  const fetchEncouragingMessages = async () => {
    try {
      const response = await apiClient.get('/api/v1/emotional/encouragement', {
        params: { limit: 5 }
      });
      setEncouragingMessages(response.data);
      
      const unread = response.data.filter((m: EncouragingMessage) => !m.read_at).length;
      setUnreadCount(unread);
    } catch (error) {
      console.error('격려 메시지 로드 실패:', error);
    }
  };

  const handleMoodCheckIn = async (data: MoodCheckInData) => {
    try {
      await apiClient.post('/api/v1/emotional/mood/check-in', data);
      alert('기분 체크인이 완료되었습니다! 💙');
      
      // 격려 메시지 새로고침
      fetchEncouragingMessages();
    } catch (error) {
      console.error('기분 체크인 실패:', error);
      throw error;
    }
  };

  const handleMarkAsRead = async (messageId: number, wasHelpful?: boolean) => {
    try {
      await apiClient.put(`/api/v1/emotional/encouragement/${messageId}/read`, {
        was_helpful: wasHelpful
      });
      
      // 메시지 목록 새로고침
      fetchEncouragingMessages();
    } catch (error) {
      console.error('메시지 읽음 처리 실패:', error);
    }
  };

  const openMoodCheckIn = (type: 'before_learning' | 'after_learning' | 'during_break') => {
    setCheckInType(type);
    setShowMoodModal(true);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-purple-50 to-pink-50 py-8 px-4">
      <div className="max-w-6xl mx-auto space-y-8">
        {/* 헤더 */}
        <div className="text-center space-y-2">
          <h1 className="text-4xl font-bold text-gray-800">
            감성적 지원 센터 💙💛
          </h1>
          <p className="text-gray-600">
            "불완전함을 포용하는 학습" - 당신의 감정과 성장을 함께 추적합니다
          </p>
        </div>

        {/* 기분 체크인 액션 버튼들 */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <button
            onClick={() => openMoodCheckIn('before_learning')}
            className="bg-white hover:bg-blue-50 border-2 border-blue-200 rounded-lg p-6 transition shadow-sm hover:shadow-md"
          >
            <div className="flex flex-col items-center space-y-2">
              <Sparkles className="w-8 h-8 text-blue-500" />
              <h3 className="font-semibold text-gray-800">학습 시작 ✨</h3>
              <p className="text-xs text-gray-600 text-center">
                학습 전 기분 체크인
              </p>
            </div>
          </button>

          <button
            onClick={() => openMoodCheckIn('during_break')}
            className="bg-white hover:bg-purple-50 border-2 border-purple-200 rounded-lg p-6 transition shadow-sm hover:shadow-md"
          >
            <div className="flex flex-col items-center space-y-2">
              <Heart className="w-8 h-8 text-purple-500" />
              <h3 className="font-semibold text-gray-800">휴식 중 ☕</h3>
              <p className="text-xs text-gray-600 text-center">
                현재 상태 체크인
              </p>
            </div>
          </button>

          <button
            onClick={() => openMoodCheckIn('after_learning')}
            className="bg-white hover:bg-pink-50 border-2 border-pink-200 rounded-lg p-6 transition shadow-sm hover:shadow-md"
          >
            <div className="flex flex-col items-center space-y-2">
              <TrendingUp className="w-8 h-8 text-pink-500" />
              <h3 className="font-semibold text-gray-800">학습 완료 🎉</h3>
              <p className="text-xs text-gray-600 text-center">
                학습 후 회고 체크인
              </p>
            </div>
          </button>
        </div>

        {/* 자기 대비 대시보드 */}
        <SelfComparisonDashboard compareDays={30} />

        {/* 격려 메시지 */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center space-x-2">
              <MessageCircle className="w-6 h-6 text-blue-500" />
              <h2 className="text-xl font-bold text-gray-800">격려 메시지</h2>
            </div>
            {unreadCount > 0 && (
              <span className="bg-blue-500 text-white text-xs font-bold px-2 py-1 rounded-full">
                {unreadCount}개 새 메시지
              </span>
            )}
          </div>

          {encouragingMessages.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              <p>아직 격려 메시지가 없습니다.</p>
              <p className="text-sm mt-2">학습을 시작하면 맞춤형 격려 메시지를 받을 수 있어요! 💙</p>
            </div>
          ) : (
            <div className="space-y-3">
              {encouragingMessages.map((message) => (
                <div
                  key={message.id}
                  className={`border rounded-lg p-4 transition ${
                    message.read_at
                      ? 'border-gray-200 bg-gray-50'
                      : 'border-blue-300 bg-blue-50'
                  }`}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <p className="text-gray-800 mb-2">{message.message}</p>
                      <div className="flex items-center space-x-2 text-xs text-gray-500">
                        <span className="bg-gray-200 px-2 py-1 rounded">
                          {message.message_tone}
                        </span>
                        <span>•</span>
                        <span>{new Date(message.sent_at).toLocaleDateString('ko-KR')}</span>
                      </div>
                    </div>
                    
                    {!message.read_at && (
                      <div className="flex flex-col space-y-1 ml-4">
                        <button
                          onClick={() => handleMarkAsRead(message.id, true)}
                          className="text-xs bg-green-100 text-green-700 px-2 py-1 rounded hover:bg-green-200"
                        >
                          도움됨 👍
                        </button>
                        <button
                          onClick={() => handleMarkAsRead(message.id, false)}
                          className="text-xs bg-gray-100 text-gray-700 px-2 py-1 rounded hover:bg-gray-200"
                        >
                          읽음
                        </button>
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* 감성적 지원 안내 */}
        <div className="bg-gradient-to-r from-blue-100 to-purple-100 border border-blue-300 rounded-lg p-6">
          <h3 className="text-lg font-bold text-gray-800 mb-3">
            💡 감성적 지원 시스템이란?
          </h3>
          <div className="space-y-2 text-sm text-gray-700">
            <p>
              <strong>기분 체크인:</strong> 학습 전후의 감정을 기록하여 패턴을 파악합니다.
            </p>
            <p>
              <strong>자기 대비 성장:</strong> 다른 사람이 아닌, 과거의 나와 비교합니다.
            </p>
            <p>
              <strong>격려 메시지:</strong> 당신의 상태에 맞는 맞춤형 격려를 제공합니다.
            </p>
            <p className="mt-3 text-xs text-gray-600 italic">
              "완벽할 필요 없어요. 어제보다 조금 나아지면 충분합니다." 💙💛
            </p>
          </div>
        </div>
      </div>

      {/* 기분 체크인 모달 */}
      <MoodCheckInModal
        isOpen={showMoodModal}
        onClose={() => setShowMoodModal(false)}
        checkInType={checkInType}
        onSubmit={handleMoodCheckIn}
      />
    </div>
  );
}

