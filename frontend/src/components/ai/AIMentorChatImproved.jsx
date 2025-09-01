import React, { useState, useEffect, useRef } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';

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
  Settings,
  Type,
  Eye
} from 'lucide-react';

const AIMentorChatImproved = ({ userId }) => {
  const [session, setSession] = useState(null);
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [conversationMode, setConversationMode] = useState('help_seeking');

  // 새로운 UX 개선 상태들
  const [textStyle, setTextStyle] = useState('default'); // default, concise, casual, friendly
  const [lineHeight, setLineHeight] = useState('comfortable'); // compact, comfortable, relaxed
  const [showSettings, setShowSettings] = useState(false);

  const [dailyMotivation, setDailyMotivation] = useState('');
  const scrollAreaRef = useRef(null);

  const conversationModes = [
    { id: 'help_seeking', label: '도움 요청', icon: HelpCircle, color: 'blue' },
    { id: 'motivation', label: '동기 부여', icon: Heart, color: 'red' },
    { id: 'explanation', label: '설명 요청', icon: BookOpen, color: 'green' },
    { id: 'guidance', label: '학습 가이드', icon: Target, color: 'purple' },
    { id: 'reflection', label: '학습 성찰', icon: Lightbulb, color: 'yellow' }
  ];

  const textStyleOptions = [
    {
      id: 'default',
      label: '기본 스타일',
      description: '일반적인 설명 스타일',
      preview: '안녕하세요! 이 개념을 설명해 드리겠습니다.'
    },
    {
      id: 'concise',
      label: '핵심만',
      description: '중요한 내용만 간단히',
      preview: '**핵심:** 변수는 데이터를 저장하는 컨테이너입니다.'
    },
    {
      id: 'casual',
      label: '반말로',
      description: '친근한 반말 스타일',
      preview: '야, 이거 쉽지? 그냥 이렇게 하면 돼!'
    },
    {
      id: 'friendly',
      label: '친절하게',
      description: '상세하고 친절한 설명',
      preview: '좋은 질문이네요! 천천히 함께 살펴보겠습니다. 😊'
    }
  ];

  const lineHeightOptions = [
    { id: 'compact', label: '좁게', value: '1.2' },
    { id: 'comfortable', label: '적당히', value: '1.5' },
    { id: 'relaxed', label: '넓게', value: '1.8' }
  ];

  // 텍스트 스타일링 함수
  const applyTextStyle = (content, style) => {
    switch (style) {
      case 'concise':
        return content.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
                      .replace(/^(.*?):/gm, '<strong>$1:</strong>');
      case 'casual':
        return content.replace(/합니다/g, '해')
                      .replace(/입니다/g, '야')
                      .replace(/하세요/g, '해');
      case 'friendly':
        return content.replace(/!/g, '! 😊')
                      .replace(/\?/g, '? 💡');
      default:
        return content;
    }
  };

  // 행간 스타일 함수
  const getLineHeightStyle = (height) => {
    const heights = {
      compact: '1.2',
      comfortable: '1.5',
      relaxed: '1.8'
    };
    return { lineHeight: heights[height] || '1.5' };
  };

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
          initial_question: initialQuestion,
          text_style: textStyle,
          line_height: lineHeight
        })
      });

      if (!response.ok) {
        throw new Error('세션 시작 실패');
      }

      const data = await response.json();
      setSession(data.session);

      // 초기 메시지 추가
      const welcomeMessage = {
        id: Date.now(),
        type: 'mentor',
        content: applyTextStyle(
          `안녕하세요! ${data.session.user_name || '학습자'}님. AI 학습 멘토입니다. 무엇을 도와드릴까요?`,
          textStyle
        ),
        timestamp: new Date(),
        suggestions: data.session.suggested_topics || []
      };

      setMessages([welcomeMessage]);
    } catch (error) {
      console.error('세션 시작 오류:', error);
    } finally {
      setLoading(false);
    }
  };

  // 메시지 전송
  const sendMessage = async () => {
    if (!inputMessage.trim() || !session) return;

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
      const response = await fetch(`${API_BASE_URL}/ai-features/mentoring/chat/${session.id}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: inputMessage,
          mode: conversationMode,
          text_style: textStyle,
          line_height: lineHeight
        })
      });

      if (!response.ok) {
        throw new Error('메시지 전송 실패');
      }

      const data = await response.json();

      const mentorMessage = {
        id: Date.now() + 1,
        type: 'mentor',
        content: applyTextStyle(data.response, textStyle),
        timestamp: new Date(),
        suggestions: data.suggestions || [],
        follow_up_questions: data.follow_up_questions || []
      };

      setMessages(prev => [...prev, mentorMessage]);
    } catch (error) {
      console.error('메시지 전송 오류:', error);
      const errorMessage = {
        id: Date.now() + 1,
        type: 'mentor',
        content: '죄송합니다. 일시적인 오류가 발생했습니다. 다시 시도해주세요.',
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (scrollAreaRef.current) {
      scrollAreaRef.current.scrollTop = scrollAreaRef.current.scrollHeight;
    }
  }, [messages]);

  return (
    <div className="w-full max-w-4xl mx-auto space-y-4">
      {/* 헤더 - 개선된 설정 옵션들 */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            <div className="flex items-center">
              <Settings className="w-5 h-5 mr-2" />
              AI 멘토링 설정
            </div>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setShowSettings(!showSettings)}
            >
              {showSettings ? '설정 닫기' : '설정 열기'}
            </Button>
          </CardTitle>
        </CardHeader>

        {showSettings && (
          <CardContent className="space-y-4">
            {/* 텍스트 스타일 설정 */}
            <div>
              <label className="text-sm font-medium flex items-center mb-2">
                <Type className="w-4 h-4 mr-1" />
                텍스트 스타일
              </label>
              <Select value={textStyle} onValueChange={setTextStyle}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {textStyleOptions.map((style) => (
                    <SelectItem key={style.id} value={style.id}>
                      <div>
                        <div className="font-medium">{style.label}</div>
                        <div className="text-xs text-gray-500">{style.description}</div>
                        <div className="text-xs text-gray-400 mt-1 italic">
                          {style.preview}
                        </div>
                      </div>
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {/* 행간 설정 */}
            <div>
              <label className="text-sm font-medium flex items-center mb-2">
                <Eye className="w-4 h-4 mr-1" />
                행간 설정
              </label>
              <Select value={lineHeight} onValueChange={setLineHeight}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {lineHeightOptions.map((option) => (
                    <SelectItem key={option.id} value={option.id}>
                      {option.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </CardContent>
        )}
      </Card>

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
            <Badge variant="secondary" className="ml-2">
              {textStyleOptions.find(s => s.id === textStyle)?.label}
            </Badge>
          </CardTitle>
        </CardHeader>
        <CardContent className="h-full flex flex-col">
          {!session ? (
            <div className="flex-1 flex items-center justify-center">
              <div className="text-center">
                <Bot className="w-12 h-12 mx-auto mb-4 text-gray-400" />
                <h3 className="text-lg font-semibold mb-2">AI 멘토와 대화 시작</h3>
                <p className="text-gray-600 mb-4" style={getLineHeightStyle(lineHeight)}>
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
              {/* 메시지 목록 - 개선된 스타일링 */}
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
                      } rounded-lg p-3`} style={getLineHeightStyle(lineHeight)}>
                        <div className="flex items-start space-x-2">
                          {message.type === 'mentor' ? (
                            <Bot className="w-4 h-4 mt-1 text-blue-500" />
                          ) : (
                            <User className="w-4 h-4 mt-1" />
                          )}
                          <div className="flex-1">
                            <div
                              className="text-sm"
                              dangerouslySetInnerHTML={{
                                __html: applyTextStyle(message.content, textStyle)
                              }}
                            />
                            <p className="text-xs opacity-70 mt-1">
                              {message.timestamp.toLocaleTimeString()}
                            </p>
                          </div>
                        </div>

                        {/* 멘토 추가 정보 - 개선된 스타일링 */}
                        {message.type === 'mentor' && (
                          <div className="mt-3 space-y-2" style={getLineHeightStyle(lineHeight)}>
                            {message.suggestions && message.suggestions.length > 0 && (
                              <div>
                                <p className="text-xs font-medium mb-1">💡 제안사항:</p>
                                <div className="space-y-1">
                                  {message.suggestions.map((suggestion, index) => (
                                    <div key={index} className="text-xs bg-blue-50 text-blue-800 p-2 rounded">
                                      <span dangerouslySetInnerHTML={{
                                        __html: applyTextStyle(suggestion, textStyle)
                                      }} />
                                    </div>
                                  ))}
                                </div>
                              </div>
                            )}

                            {message.follow_up_questions && message.follow_up_questions.length > 0 && (
                              <div>
                                <p className="text-xs font-medium mb-1">❓ 후속 질문:</p>
                                <div className="space-y-1">
                                  {message.follow_up_questions.map((question, index) => (
                                    <div key={index} className="text-xs bg-yellow-50 text-yellow-800 p-2 rounded">
                                      <span dangerouslySetInnerHTML={{
                                        __html: applyTextStyle(question, textStyle)
                                      }} />
                                    </div>
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
                      <div className="bg-gray-100 text-gray-900 rounded-lg p-3">
                        <div className="flex items-center space-x-2">
                          <Bot className="w-4 h-4 text-blue-500" />
                          <div className="flex space-x-1">
                            <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce"></div>
                            <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{animationDelay: '0.1s'}}></div>
                            <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></div>
                          </div>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              </ScrollArea>

              {/* 입력 영역 */}
              <div className="flex space-x-2 mt-4">
                <Input
                  value={inputMessage}
                  onChange={(e) => setInputMessage(e.target.value)}
                  placeholder="메시지를 입력하세요..."
                  onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
                  disabled={loading}
                  className="flex-1"
                />
                <Button
                  onClick={sendMessage}
                  disabled={loading || !inputMessage.trim()}
                  size="sm"
                >
                  <Send className="w-4 h-4" />
                </Button>
              </div>
            </>
          )}
        </CardContent>
      </Card>

      {/* 세션 정보 */}
      {session && (
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-4">
                <Badge variant="outline">
                  세션 #{session.id}
                </Badge>
                {session.session_goals && session.session_goals.length > 0 && (
                  <Badge variant="secondary">
                    목표: {session.session_goals[0]}
                  </Badge>
                )}
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

export default AIMentorChatImproved;
