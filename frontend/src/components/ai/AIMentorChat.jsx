import React, { useState, useEffect, useRef } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';

const API_BASE_URL = 'http://localhost:8000/api/v1';
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
  RefreshCw
} from 'lucide-react';

const AIMentorChat = ({ userId }) => {
  const [session, setSession] = useState(null);
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [conversationMode, setConversationMode] = useState('help_seeking');
  const [dailyMotivation, setDailyMotivation] = useState('');
  const scrollAreaRef = useRef(null);

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
      const response = await fetch(`${API_BASE_URL}/ai-features/mentoring/continue`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          session_id: session.session_id,
          message: inputMessage,
          conversation_mode: conversationMode
        })
      });
      
      const data = await response.json();
      if (data.success) {
        const mentorMessage = {
          id: Date.now() + 1,
          type: 'mentor',
          content: data.mentor_response.content,
          timestamp: new Date(),
          suggestions: data.mentor_response.suggestions,
          follow_up_questions: data.mentor_response.follow_up_questions,
          tone: data.mentor_response.tone
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
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold">AI 멘토링</h2>
          <p className="text-gray-600">24/7 개인 학습 코치와 대화하세요</p>
        </div>
        {session && (
          <Badge variant="secondary">
            {getMentorPersonalityLabel(session.mentor_personality)}
          </Badge>
        )}
      </div>

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

      {/* 대화 모드 선택 */}
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

      {/* 채팅 영역 */}
      <Card className="h-96">
        <CardHeader>
          <CardTitle className="flex items-center">
            <MessageCircle className="w-5 h-5 mr-2" />
            멘토링 채팅
          </CardTitle>
        </CardHeader>
        <CardContent className="h-full flex flex-col">
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
                            <p className="text-sm">{message.content}</p>
                            <p className="text-xs opacity-70 mt-1">
                              {message.timestamp.toLocaleTimeString()}
                            </p>
                          </div>
                        </div>
                        
                        {/* 멘토 추가 정보 */}
                        {message.type === 'mentor' && (
                          <div className="mt-3 space-y-2">
                            {message.suggestions && message.suggestions.length > 0 && (
                              <div>
                                <p className="text-xs font-medium mb-1">💡 제안사항:</p>
                                <div className="space-y-1">
                                  {message.suggestions.map((suggestion, index) => (
                                    <p key={index} className="text-xs bg-blue-50 text-blue-800 p-1 rounded">
                                      {suggestion}
                                    </p>
                                  ))}
                                </div>
                              </div>
                            )}
                            
                            {message.follow_up_questions && message.follow_up_questions.length > 0 && (
                              <div>
                                <p className="text-xs font-medium mb-1">❓ 후속 질문:</p>
                                <div className="space-y-1">
                                  {message.follow_up_questions.map((question, index) => (
                                    <Button
                                      key={index}
                                      variant="ghost"
                                      size="sm"
                                      className="text-xs h-auto p-1 text-blue-600 hover:text-blue-800"
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
