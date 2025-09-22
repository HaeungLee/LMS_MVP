import React, { useState, useEffect } from 'react';
import { useMutation, useQuery } from '@tanstack/react-query';
import { Heart, MessageCircle, Target, TrendingUp, Calendar, CheckCircle, AlertCircle, Lightbulb, Star, BookOpen } from 'lucide-react';
import { toast } from 'react-hot-toast';
import useAuthStore from '../../../shared/hooks/useAuthStore';
import { counselingApi } from '../../../shared/services/apiClient';

interface CounselingSession {
  id: string;
  type: 'motivation' | 'guidance' | 'goal_setting' | 'habit_building';
  message: string;
  ai_response: string;
  timestamp: Date;
  mood_score?: number;
  tags: string[];
}

interface MotivationalInsight {
  type: 'achievement' | 'progress' | 'challenge' | 'encouragement';
  title: string;
  message: string;
  icon: string;
}

interface LearningGoal {
  id: string;
  title: string;
  description: string;
  target_date: string;
  progress: number;
  status: 'active' | 'completed' | 'paused';
}

export default function LearningCounselor() {
  const { user } = useAuthStore();
  const [message, setMessage] = useState('');
  const [selectedType, setSelectedType] = useState<'motivation' | 'guidance' | 'goal_setting' | 'habit_building'>('motivation');
  const [moodScore, setMoodScore] = useState(5);
  const [sessions, setSessions] = useState<CounselingSession[]>([]);
  const [currentSessionId, setCurrentSessionId] = useState<string | null>(null);

  // 사용자 인사이트 조회 (실제 API)
  const { data: userInsights, isLoading: isInsightsLoading } = useQuery({
    queryKey: ['user-insights'],
    queryFn: () => counselingApi.getUserInsights(),
    enabled: !!user,
  });

  // 일일 동기부여 메시지 조회 (실제 API)
  const { data: dailyMotivation } = useQuery({
    queryKey: ['daily-motivation'],
    queryFn: () => counselingApi.getDailyMotivation(),
    enabled: !!user,
  });

  // 폴백용 모킹 데이터
  const fallbackInsights: MotivationalInsight[] = [
    {
      type: 'achievement',
      title: '이번 주 학습 목표 달성!',
      message: '설정한 주간 학습 시간 20시간을 초과 달성했습니다. 정말 대단해요!',
      icon: '🎉'
    },
    {
      type: 'progress',
      title: '꾸준한 성장을 보이고 있어요',
      message: '지난 달 대비 문제 해결 속도가 25% 향상되었습니다.',
      icon: '📈'
    },
    {
      type: 'challenge',
      title: '새로운 도전을 시작해보세요',
      message: '현재 실력으로 중급 레벨 과정에 도전해볼 준비가 되었습니다.',
      icon: '🚀'
    },
    {
      type: 'encouragement',
      title: '지금까지 정말 잘해왔어요',
      message: '어려운 시기에도 포기하지 않고 꾸준히 학습을 이어가고 있습니다.',
      icon: '💪'
    }
  ];

  // 실제 데이터 또는 폴백 데이터 사용
  const insights = userInsights?.insights || fallbackInsights;

  const mockGoals: LearningGoal[] = [
    {
      id: '1',
      title: 'Python 기초 완주하기',
      description: '파이썬 기초 문법과 자료구조를 모두 학습',
      target_date: '2024-10-15',
      progress: 78,
      status: 'active'
    },
    {
      id: '2',
      title: '알고리즘 100문제 풀기',
      description: '코딩테스트 대비 알고리즘 문제 100개 해결',
      target_date: '2024-11-30',
      progress: 45,
      status: 'active'
    },
    {
      id: '3',
      title: '데이터베이스 이해하기',
      description: 'SQL과 NoSQL 데이터베이스 기본 개념 습득',
      target_date: '2024-12-20',
      progress: 12,
      status: 'active'
    }
  ];

  // 상담 세션 전송 (실제 API 사용)
  const counselingMutation = useMutation({
    mutationFn: async (data: {
      message: string;
      type: 'motivation' | 'guidance' | 'goal_setting' | 'habit_building';
      mood_score?: number;
    }) => {
      return counselingApi.sendMessage({
        message: data.message,
        type: data.type,
        mood_score: data.mood_score,
        session_id: currentSessionId || undefined,
      });
    },
    onSuccess: (response) => {
      const newSession: CounselingSession = {
        id: `session-${Date.now()}`,
        type: selectedType,
        message: message,
        ai_response: response.ai_response,
        timestamp: new Date(),
        mood_score: selectedType === 'motivation' ? moodScore : undefined,
        tags: [selectedType, 'ai-counseling']
      };
      
      setSessions(prev => [newSession, ...prev]);
      setCurrentSessionId(response.session_id);
      setMessage('');
      toast.success('AI 상담사가 응답했습니다!');
    },
    onError: (error: any) => {
      console.error('상담 API 오류:', error);
      toast.error(`상담 요청 실패: ${error.response?.data?.detail || error.message}`);
    },
  });

  const handleSubmit = () => {
    if (!message.trim()) {
      toast.error('상담 내용을 입력해주세요');
      return;
    }

    counselingMutation.mutate({
      message: message.trim(),
      type: selectedType,
      mood_score: selectedType === 'motivation' ? moodScore : undefined
    });
  };

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'motivation': return <Heart className="w-5 h-5" />;
      case 'guidance': return <Lightbulb className="w-5 h-5" />;
      case 'goal_setting': return <Target className="w-5 h-5" />;
      case 'habit_building': return <Calendar className="w-5 h-5" />;
      default: return <MessageCircle className="w-5 h-5" />;
    }
  };

  const getTypeColor = (type: string) => {
    switch (type) {
      case 'motivation': return 'text-pink-600 bg-pink-50 border-pink-200';
      case 'guidance': return 'text-blue-600 bg-blue-50 border-blue-200';
      case 'goal_setting': return 'text-green-600 bg-green-50 border-green-200';
      case 'habit_building': return 'text-purple-600 bg-purple-50 border-purple-200';
      default: return 'text-gray-600 bg-gray-50 border-gray-200';
    }
  };

  const getMoodEmoji = (score: number) => {
    if (score <= 2) return '😢';
    if (score <= 4) return '😕';
    if (score <= 6) return '😐';
    if (score <= 8) return '😊';
    return '😄';
  };

  return (
    <div className="max-w-6xl mx-auto space-y-8">
      {/* 헤더 */}
      <div className="bg-gradient-to-r from-pink-500 to-purple-600 rounded-lg p-6 text-white">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold mb-2">💝 AI 학습 상담사</h1>
            <p className="text-pink-100">
              학습 고민 상담부터 목표 설정, 동기부여까지 AI 상담사가 도와드립니다
            </p>
          </div>
          <Heart className="w-16 h-16 text-pink-200" />
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* 상담 요청 영역 */}
        <div className="lg:col-span-2 space-y-6">
          {/* 상담 유형 선택 */}
          <div className="bg-white rounded-lg p-6 shadow-sm border border-gray-200">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">상담 유형 선택</h3>
            <div className="grid grid-cols-2 gap-3">
              {[
                { type: 'motivation', label: '동기부여 & 격려', desc: '학습 의욕이 떨어질 때' },
                { type: 'guidance', label: '학습 방향 가이드', desc: '어떻게 공부해야 할지 모를 때' },
                { type: 'goal_setting', label: '목표 설정 도움', desc: '구체적인 목표를 세우고 싶을 때' },
                { type: 'habit_building', label: '습관 형성 조언', desc: '꾸준한 학습 습관을 만들고 싶을 때' }
              ].map((option) => (
                <button
                  key={option.type}
                  onClick={() => setSelectedType(option.type as any)}
                  className={`p-4 rounded-lg border-2 text-left transition-all ${
                    selectedType === option.type
                      ? getTypeColor(option.type)
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                >
                  <div className="flex items-center mb-2">
                    {getTypeIcon(option.type)}
                    <span className="ml-2 font-medium">{option.label}</span>
                  </div>
                  <p className="text-sm text-gray-600">{option.desc}</p>
                </button>
              ))}
            </div>
          </div>

          {/* 기분 점수 (동기부여 상담시에만) */}
          {selectedType === 'motivation' && (
            <div className="bg-white rounded-lg p-6 shadow-sm border border-gray-200">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">현재 기분 상태</h3>
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">매우 우울</span>
                  <span className="text-2xl">{getMoodEmoji(moodScore)}</span>
                  <span className="text-sm text-gray-600">매우 좋음</span>
                </div>
                <input
                  type="range"
                  min="1"
                  max="10"
                  value={moodScore}
                  onChange={(e) => setMoodScore(Number(e.target.value))}
                  className="w-full"
                />
                <p className="text-center text-sm text-gray-600">
                  현재 기분: {moodScore}/10
                </p>
              </div>
            </div>
          )}

          {/* 상담 메시지 입력 */}
          <div className="bg-white rounded-lg p-6 shadow-sm border border-gray-200">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">상담 내용</h3>
            <textarea
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              rows={6}
              placeholder={`${selectedType === 'motivation' ? '학습에 대한 고민이나 어려움' : 
                selectedType === 'guidance' ? '어떤 방향으로 학습해야 할지 궁금한 점' :
                selectedType === 'goal_setting' ? '설정하고 싶은 학습 목표' :
                '만들고 싶은 학습 습관이나 어려움'}을 자유롭게 적어주세요...

예시:
- 요즘 공부에 집중이 안 되고 의욕이 떨어져요
- 프로그래밍을 배우고 싶은데 어디서부터 시작해야 할까요?
- 취업을 위한 구체적인 학습 계획을 세우고 싶어요
- 매일 공부하는 습관을 만들고 싶은데 자꾸 포기하게 돼요`}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-pink-500"
            />
            
            <button
              onClick={handleSubmit}
              disabled={counselingMutation.isPending || !message.trim()}
              className="w-full mt-4 bg-pink-600 text-white py-3 px-4 rounded-lg hover:bg-pink-700 disabled:bg-gray-300 disabled:cursor-not-allowed flex items-center justify-center"
            >
              {counselingMutation.isPending ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                  상담 중...
                </>
              ) : (
                <>
                  <MessageCircle className="w-4 h-4 mr-2" />
                  AI 상담사에게 전송
                </>
              )}
            </button>
          </div>

          {/* 상담 기록 */}
          {sessions.length > 0 && (
            <div className="bg-white rounded-lg p-6 shadow-sm border border-gray-200">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">상담 기록</h3>
              <div className="space-y-4 max-h-96 overflow-y-auto">
                {sessions.map((session) => (
                  <div key={session.id} className="border border-gray-200 rounded-lg p-4">
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center">
                        {getTypeIcon(session.type)}
                        <span className="ml-2 text-sm font-medium capitalize">
                          {session.type.replace('_', ' ')}
                        </span>
                        {session.mood_score && (
                          <span className="ml-2 text-sm text-gray-500">
                            기분: {getMoodEmoji(session.mood_score)} {session.mood_score}/10
                          </span>
                        )}
                      </div>
                      <span className="text-xs text-gray-500">
                        {session.timestamp.toLocaleString()}
                      </span>
                    </div>
                    
                    <div className="bg-blue-50 rounded-lg p-3 mb-3">
                      <p className="text-sm text-blue-900">
                        <strong>내 질문:</strong> {session.message}
                      </p>
                    </div>
                    
                    <div className="bg-pink-50 rounded-lg p-3">
                      <p className="text-sm text-pink-900">
                        <strong>AI 상담사:</strong> {session.ai_response}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* 사이드바 - 동기부여 인사이트 & 목표 */}
        <div className="space-y-6">
          {/* 개인화 인사이트 */}
          <div className="bg-white rounded-lg p-6 shadow-sm border border-gray-200">
            <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
              <Star className="w-5 h-5 text-yellow-500 mr-2" />
              오늘의 격려 메시지
            </h3>
            {isInsightsLoading ? (
              <div className="space-y-3">
                {[...Array(3)].map((_, index) => (
                  <div key={index} className="bg-gray-100 rounded-lg p-4 animate-pulse">
                    <div className="h-4 bg-gray-300 rounded w-3/4 mb-2"></div>
                    <div className="h-3 bg-gray-300 rounded"></div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="space-y-3">
                {insights.map((insight, index) => (
                  <div key={index} className="bg-gradient-to-r from-pink-50 to-purple-50 rounded-lg p-4 border border-pink-200">
                    <div className="flex items-center mb-2">
                      <span className="text-lg mr-2">{insight.icon}</span>
                      <h4 className="text-sm font-semibold text-gray-900">{insight.title}</h4>
                    </div>
                    <p className="text-sm text-gray-700">{insight.message}</p>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* 학습 목표 현황 */}
          <div className="bg-white rounded-lg p-6 shadow-sm border border-gray-200">
            <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
              <Target className="w-5 h-5 text-green-500 mr-2" />
              나의 학습 목표
            </h3>
            <div className="space-y-4">
              {mockGoals.map((goal) => (
                <div key={goal.id} className="border border-gray-200 rounded-lg p-4">
                  <div className="flex items-center justify-between mb-2">
                    <h4 className="text-sm font-semibold text-gray-900">{goal.title}</h4>
                    <span className={`text-xs px-2 py-1 rounded-full ${
                      goal.status === 'active' ? 'bg-green-100 text-green-800' :
                      goal.status === 'completed' ? 'bg-blue-100 text-blue-800' :
                      'bg-gray-100 text-gray-800'
                    }`}>
                      {goal.status}
                    </span>
                  </div>
                  <p className="text-xs text-gray-600 mb-2">{goal.description}</p>
                  <div className="w-full bg-gray-200 rounded-full h-2 mb-2">
                    <div 
                      className="bg-green-600 h-2 rounded-full transition-all duration-300"
                      style={{ width: `${goal.progress}%` }}
                    ></div>
                  </div>
                  <div className="flex items-center justify-between text-xs text-gray-500">
                    <span>{goal.progress}% 완료</span>
                    <span>목표일: {goal.target_date}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* 상담 통계 */}
          <div className="bg-gradient-to-br from-purple-50 to-pink-50 rounded-lg p-6 border border-purple-200">
            <h3 className="text-lg font-semibold text-purple-900 mb-4">이번 달 상담 현황</h3>
            <div className="grid grid-cols-2 gap-4 text-center">
              <div className="bg-white rounded-lg p-3">
                <div className="text-2xl font-bold text-purple-600">{sessions.length}</div>
                <div className="text-xs text-gray-600">총 상담 횟수</div>
              </div>
              <div className="bg-white rounded-lg p-3">
                <div className="text-2xl font-bold text-pink-600">
                  {sessions.length > 0 ? Math.round(sessions.reduce((acc, s) => acc + (s.mood_score || 5), 0) / sessions.length * 10) / 10 : '-'}
                </div>
                <div className="text-xs text-gray-600">평균 기분 점수</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* 기능 안내 */}
      <div className="bg-pink-50 border border-pink-200 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-pink-900 mb-4">🌟 AI 학습 상담사 기능</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="flex items-start">
            <Heart className="w-5 h-5 text-pink-600 mr-2 mt-0.5" />
            <div>
              <h4 className="text-sm font-semibold text-pink-900">동기부여 & 격려</h4>
              <p className="text-xs text-pink-700">학습 의욕 저하시 맞춤형 격려와 동기부여</p>
            </div>
          </div>
          <div className="flex items-start">
            <Lightbulb className="w-5 h-5 text-pink-600 mr-2 mt-0.5" />
            <div>
              <h4 className="text-sm font-semibold text-pink-900">학습 방향 가이드</h4>
              <p className="text-xs text-pink-700">개인 수준에 맞는 최적 학습 경로 제안</p>
            </div>
          </div>
          <div className="flex items-start">
            <Target className="w-5 h-5 text-pink-600 mr-2 mt-0.5" />
            <div>
              <h4 className="text-sm font-semibold text-pink-900">목표 설정 도움</h4>
              <p className="text-xs text-pink-700">SMART 원칙 기반 현실적 목표 수립 지원</p>
            </div>
          </div>
          <div className="flex items-start">
            <Calendar className="w-5 h-5 text-pink-600 mr-2 mt-0.5" />
            <div>
              <h4 className="text-sm font-semibold text-pink-900">습관 형성 조언</h4>
              <p className="text-xs text-pink-700">지속 가능한 학습 습관 개발 전략 제공</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
