import React, { useState, useEffect, useRef } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';

const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000') + '/api/v1';
import { 
  MessageCircle, 
  Send, 
  Bot, 
  User, 
  Heart,
  HelpCircle,
  BookOpen,
  Target,
  Lightbulb,
  RefreshCw,
  Settings
} from 'lucide-react';

// Bold체 자동 적용 함수 - 중요한 키워드만 강조
const formatBoldText = (text) => {
  if (!text) return '';
  
  // 중요한 프로그래밍 키워드나 짧은 단어에만 bold 적용
  // **단어** 또는 **짧은 구문** (20자 이하)만 bold로 변환
  return text.replace(/\*\*([^*]{1,20}?)\*\*/g, '<strong class="font-semibold text-blue-700">$1</strong>');
};

// 메시지 컨텐츠 컴포넌트
const MessageContent = ({ content, isBot, textSize = 'base' }) => {
  const sizeClasses = {
    'sm': 'text-sm',
    'base': 'text-base', 
    'lg': 'text-lg'
  };

  return (
    <div className={`${sizeClasses[textSize]} leading-relaxed space-y-2`}>
      <div 
        dangerouslySetInnerHTML={{
          __html: formatBoldText(content)
        }} 
        className="prose prose-sm max-w-none"
      />
    </div>
  );
};

const AIMentorChat = ({ userId }) => {
  const [session, setSession] = useState(null);
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [conversationMode, setConversationMode] = useState('help_seeking');
  const [dailyMotivation, setDailyMotivation] = useState('');
  const scrollAreaRef = useRef(null);

  // 사용자 설정 상태
  const [settings, setSettings] = useState({
    textSize: 'base',
    showFollowUps: false,   // 기본적으로 비활성화
    showSessionInfo: false  // 기본적으로 비활성화
  });
  const [showSettings, setShowSettings] = useState(false);

  const conversationModes = [
    { id: 'help_seeking', label: '도움 요청', icon: HelpCircle, color: 'blue' },
    { id: 'motivation', label: '동기 부여', icon: Heart, color: 'red' },
    { id: 'explanation', label: '설명 요청', icon: BookOpen, color: 'green' },
    { id: 'guidance', label: '학습 가이드', icon: Target, color: 'purple' },
    { id: 'reflection', label: '학습 성찰', icon: Lightbulb, color: 'yellow' }
  ];

  // 세션 시작
  const startMentorSession = async (initialQuestion = null) => {
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/ai-features/mentoring/start-session/${userId}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          initial_question: initialQuestion
        })
      });
      
      const data = await response.json();
      if (data.success) {
        setSession(data.session);
        setMessages([{
          id: Date.now(),
          type: 'mentor',
          content: data.session.greeting,
          timestamp: new Date(),
          mentor_personality: data.session.mentor_personality
        }]);
      }
    } catch (error) {
      console.error('멘토링 세션 시작 실패:', error);
    } finally {
      setLoading(false);
    }
  };

  // 메시지 전송
  const sendMessage = async () => {
    if (!inputMessage.trim() || !session || loading) return;

    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: inputMessage,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setLoading(true);

    try {
      const response = await fetch(`${API_BASE_URL}/ai-features/mentoring/chat/${session.session_id}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: inputMessage,
          conversation_mode: conversationMode
        })
      });
      
      const data = await response.json();
      if (data.success) {
        const mentorMessage = {
          id: Date.now() + 1,
          type: 'mentor',
          content: data.response, // 직접 response 사용
          timestamp: new Date(),
          follow_up_questions: data.follow_up_questions || [],
          tone: data.tone
        };
        
        setMessages(prev => [...prev, mentorMessage]);
      }
    } catch (error) {
      console.error('메시지 전송 실패:', error);
    } finally {
      setLoading(false);
    }
  };

  // 일일 동기부여 가져오기
  const fetchDailyMotivation = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/ai-features/mentoring/daily-motivation/${userId}`);
      const data = await response.json();
      if (data.success) {
        setDailyMotivation(data.motivation);
      }
    } catch (error) {
      console.error('일일 동기부여 가져오기 실패:', error);
    }
  };

  // 컴포넌트 마운트 시 초기화
  useEffect(() => {
    fetchDailyMotivation();
  }, [userId]);

  // 메시지 스크롤
  useEffect(() => {
    if (scrollAreaRef.current) {
      scrollAreaRef.current.scrollTop = scrollAreaRef.current.scrollHeight;
    }
  }, [messages]);

  const getModeColor = (mode) => {
    const modeInfo = conversationModes.find(m => m.id === mode);
    return modeInfo ? modeInfo.color : 'blue';
  };

  const getMentorPersonalityLabel = (personality) => {
    const labels = {
      'encouraging': '격려형 멘토',
      'analytical': '분석형 멘토',
      'practical': '실무형 멘토',
      'patient': '인내형 멘토',
      'challenging': '도전형 멘토'
    };
    return labels[personality] || personality;
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className="space-y-6">
      {/* 헤더 */}
      <div className="flex justify-between items-center mb-6">
        <div>
          <h2 className="text-2xl font-bold">AI 멘토링</h2>
          <p className="text-gray-600">24/7 개인 학습 코치와 대화하세요</p>
        </div>
        
        <div className="flex items-center space-x-2">
          {/* 설정 버튼 */}
          <Button 
            variant="outline" 
            size="sm" 
            onClick={() => setShowSettings(!showSettings)}
            className="flex items-center space-x-1"
          >
            <Settings className="w-4 h-4" />
            <span>설정</span>
          </Button>
          
          {/* 새 세션 버튼 */}
          {session && (
            <Button 
              variant="outline" 
              size="sm" 
              onClick={() => startMentorSession()}
              className="flex items-center space-x-1"
            >
              <RefreshCw className="w-4 h-4" />
              <span>새 세션</span>
            </Button>
          )}
          
          {/* 멘토 성격 배지 */}
          {session && settings.showSessionInfo && (
            <Badge variant="secondary">
              {getMentorPersonalityLabel(session.mentor_personality)}
            </Badge>
          )}
        </div>
      </div>

      {/* 설정 패널 */}
      {showSettings && (
        <Card className="bg-gray-50 border-gray-200">
          <CardHeader>
            <CardTitle className="text-lg">멘토링 설정</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {/* 텍스트 크기 설정 */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                텍스트 크기
              </label>
              <select 
                value={settings.textSize}
                onChange={(e) => setSettings(prev => ({ ...prev, textSize: e.target.value }))}
                className="w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="sm">작게</option>
                <option value="base">보통</option>
                <option value="lg">크게</option>
              </select>
            </div>
            
            {/* 표시 옵션 */}
            <div className="space-y-3">
              <label className="block text-sm font-medium text-gray-700">표시 옵션</label>
              
              <div className="space-y-2">
                <label className="flex items-center space-x-2">
                  <input 
                    type="checkbox" 
                    checked={settings.showFollowUps}
                    onChange={(e) => setSettings(prev => ({ ...prev, showFollowUps: e.target.checked }))}
                    className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                  />
                  <span className="text-sm">❓ 후속 질문 표시</span>
                </label>
                
                <label className="flex items-center space-x-2">
                  <input 
                    type="checkbox" 
                    checked={settings.showSessionInfo}
                    onChange={(e) => setSettings(prev => ({ ...prev, showSessionInfo: e.target.checked }))}
                    className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                  />
                  <span className="text-sm">📊 세션 정보 표시</span>
                </label>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* 일일 동기부여 */}
      {dailyMotivation && (
        <Card className="bg-gradient-to-r from-blue-50 to-purple-50 border-blue-200">
          <CardContent className="pt-6">
            <div className="flex items-start space-x-3">
              <Heart className="w-5 h-5 text-red-500 mt-1" />
              <div>
                <h3 className="font-semibold text-blue-900 mb-1">오늘의 동기부여</h3>
                <p className="text-blue-800">{dailyMotivation}</p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* 대화 모드 선택 - 설정에서 활성화된 경우만 표시 */}
      {settings.showSessionInfo && (
        <Card>
          <CardHeader>
            <CardTitle className="text-sm">대화 모드</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex flex-wrap gap-2">
              {conversationModes.map((mode) => {
                const Icon = mode.icon;
                return (
                  <Button
                    key={mode.id}
                    variant={conversationMode === mode.id ? "default" : "outline"}
                    size="sm"
                    onClick={() => setConversationMode(mode.id)}
                    className="flex items-center space-x-1"
                  >
                    <Icon className="w-4 h-4" />
                    <span>{mode.label}</span>
                  </Button>
                );
              })}
            </div>
          </CardContent>
        </Card>
      )}

      {/* 채팅 영역 */}
      <Card className="h-[600px]"> {/* 높이 확장 */}
        <CardHeader>
          <CardTitle className="flex items-center">
            <MessageCircle className="w-5 h-5 mr-2" />
            멘토링 채팅
          </CardTitle>
        </CardHeader>
        <CardContent className="h-full flex flex-col p-6"> {/* 패딩 증가 */}
          {!session ? (
            <div className="flex-1 flex items-center justify-center">
              <div className="text-center">
                <Bot className="w-12 h-12 mx-auto mb-4 text-gray-400" />
                <h3 className="text-lg font-semibold mb-2">AI 멘토와 대화 시작</h3>
                <p className="text-gray-600 mb-4">
                  궁금한 것이 있거나 학습 도움이 필요하신가요?
                </p>
                <div className="space-y-2">
                  <Button onClick={() => startMentorSession()}>
                    새 멘토링 세션 시작
                  </Button>
                  <div className="text-sm text-gray-500">
                    또는 바로 질문을 입력해보세요
                  </div>
                </div>
              </div>
            </div>
          ) : (
            <>
              {/* 메시지 목록 */}
              <ScrollArea className="flex-1 pr-4" ref={scrollAreaRef}>
                <div className="space-y-4">
                  {messages.map((message) => (
                    <div
                      key={message.id}
                      className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
                    >
                      <div className={`max-w-[80%] ${
                        message.type === 'user'
                          ? 'bg-blue-500 text-white'
                          : 'bg-gray-100 text-gray-900'
                      } rounded-lg p-3`}>
                        <div className="flex items-start space-x-2">
                          {message.type === 'mentor' ? (
                            <Bot className="w-4 h-4 mt-1 text-blue-500" />
                          ) : (
                            <User className="w-4 h-4 mt-1" />
                          )}
                          <div className="flex-1">
                            {/* 새로운 메시지 컨텐츠 컴포넌트 사용 */}
                            <MessageContent 
                              content={message.content} 
                              isBot={message.type === 'mentor'} 
                              textSize={settings.textSize}
                            />
                            <p className="text-xs opacity-70 mt-2">
                              {message.timestamp.toLocaleTimeString()}
                            </p>
                          </div>
                        </div>
                        
                        {/* 멘토 추가 정보 - 설정에 따라 표시 */}
                        {message.type === 'mentor' && (
                          <div className="mt-4 space-y-3">
                            {/* 후속 질문 - 설정에서 활성화된 경우만 표시 */}
                            {settings.showFollowUps && message.follow_up_questions && message.follow_up_questions.length > 0 && (
                              <div>
                                <p className="text-xs font-medium mb-2 text-gray-600">❓ 후속 질문:</p>
                                <div className="space-y-2">
                                  {message.follow_up_questions.map((question, index) => (
                                    <Button
                                      key={index}
                                      variant="ghost"
                                      size="sm"
                                      className="text-sm h-auto p-2 text-blue-600 hover:text-blue-800 border border-blue-200 hover:bg-blue-50"
                                      onClick={() => setInputMessage(question)}
                                    >
                                      {question}
                                    </Button>
                                  ))}
                                </div>
                              </div>
                            )}
                          </div>
                        )}
                      </div>
                    </div>
                  ))}
                  
                  {loading && (
                    <div className="flex justify-start">
                      <div className="bg-gray-100 rounded-lg p-3">
                        <div className="flex items-center space-x-2">
                          <Bot className="w-4 h-4 text-blue-500" />
                          <RefreshCw className="w-4 h-4 animate-spin" />
                          <span className="text-sm text-gray-600">멘토가 답변을 준비하고 있습니다...</span>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              </ScrollArea>

              {/* 입력 영역 */}
              <div className="flex space-x-2 pt-4 border-t">
                <Input
                  placeholder="질문이나 고민을 입력하세요..."
                  value={inputMessage}
                  onChange={(e) => setInputMessage(e.target.value)}
                  onKeyPress={handleKeyPress}
                  disabled={loading}
                  className="flex-1"
                />
                <Button 
                  onClick={sendMessage} 
                  disabled={!inputMessage.trim() || loading}
                  size="sm"
                >
                  <Send className="w-4 h-4" />
                </Button>
              </div>
            </>
          )}
          
          {/* 세션이 없을 때 바로 시작할 수 있는 입력 */}
          {!session && (
            <div className="flex space-x-2 pt-4 border-t">
              <Input
                placeholder="바로 질문을 입력하고 멘토링을 시작하세요..."
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                onKeyPress={(e) => {
                  if (e.key === 'Enter' && inputMessage.trim()) {
                    startMentorSession(inputMessage);
                    setInputMessage('');
                  }
                }}
                className="flex-1"
              />
              <Button 
                onClick={() => {
                  if (inputMessage.trim()) {
                    startMentorSession(inputMessage);
                    setInputMessage('');
                  } else {
                    startMentorSession();
                  }
                }}
                size="sm"
              >
                <Send className="w-4 h-4" />
              </Button>
            </div>
          )}
        </CardContent>
      </Card>

      {/* 세션 정보 */}
      {session && (
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">현재 세션</p>
                <p className="font-medium">{session.session_id}</p>
                <div className="flex items-center space-x-2 mt-1">
                  <Badge variant="outline">
                    {getModeColor(conversationMode)} 모드
                  </Badge>
                  {session.session_goals && session.session_goals.length > 0 && (
                    <Badge variant="secondary">
                      목표: {session.session_goals[0]}
                    </Badge>
                  )}
                </div>
              </div>
              <Button 
                variant="outline" 
                size="sm"
                onClick={() => {
                  setSession(null);
                  setMessages([]);
                }}
              >
                새 세션 시작
              </Button>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default AIMentorChat;
