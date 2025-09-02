import React, { useState, useEffect, useRef } from 'react';
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

// Simple UI Components
const Card = ({ children, className = '' }) => (
  <div className={`bg-white border border-gray-200 rounded-lg shadow ${className}`}>
    {children}
  </div>
);

const CardHeader = ({ children }) => (
  <div className="px-6 py-4 border-b border-gray-200">
    {children}
  </div>
);

const CardTitle = ({ children, className = '' }) => (
  <h3 className={`text-lg font-semibold ${className}`}>
    {children}
  </h3>
);

const CardContent = ({ children, className = '' }) => (
  <div className={`p-6 ${className}`}>
    {children}
  </div>
);

const Button = ({ children, onClick, disabled, size = 'default', className = '', ...props }) => (
  <button
    onClick={onClick}
    disabled={disabled}
    className={`px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 disabled:opacity-50 ${className}`}
    {...props}
  >
    {children}
  </button>
);

const Input = ({ className = '', ...props }) => (
  <input
    className={`w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500 ${className}`}
    {...props}
  />
);

const Badge = ({ children, variant = 'default', className = '' }) => (
  <span className={`px-2 py-1 text-xs font-medium rounded ${variant === 'secondary' ? 'bg-gray-100 text-gray-800' : 'bg-blue-100 text-blue-800'} ${className}`}>
    {children}
  </span>
);

const ScrollArea = React.forwardRef(({ children, className = '', ...props }, ref) => (
  <div ref={ref} className={`overflow-auto ${className}`} {...props}>
    {children}
  </div>
));

const Select = ({ children, value, onValueChange }) => (
  <div className="relative">
    {React.Children.map(children, child => 
      React.cloneElement(child, { value, onValueChange })
    )}
  </div>
);

const SelectTrigger = ({ children, className = '' }) => (
  <div className={`w-full px-3 py-2 border border-gray-300 rounded cursor-pointer ${className}`}>
    {children}
  </div>
);

const SelectValue = ({ placeholder }) => (
  <span className="text-gray-500">{placeholder}</span>
);

const SelectContent = ({ children }) => (
  <div className="absolute top-full left-0 w-full bg-white border border-gray-300 rounded mt-1 shadow-lg z-50">
    {children}
  </div>
);

const SelectItem = ({ children, value, onValueChange }) => (
  <div
    className="px-3 py-2 hover:bg-gray-100 cursor-pointer"
    onClick={() => onValueChange && onValueChange(value)}
  >
    {children}
  </div>
);

const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || '') + '/api/v1';

const AIMentorChatImproved = ({ userId }) => {
  const [session, setSession] = useState(null);
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [conversationMode, setConversationMode] = useState('help_seeking');

  // 새로운 UX 개선 상태들
  const [textStyle, setTextStyle] = useState('default');
  const [lineHeight, setLineHeight] = useState('comfortable');
  const [showSettings, setShowSettings] = useState(false);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [showFollowUps, setShowFollowUps] = useState(false);

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

  // 텍스트 스타일링 함수 - Bold체 적용 개선
  const applyTextStyle = (content, style) => {
    let formattedContent = content;
    
    // 연속된 줄바꿈을 하나로 줄임 (\n\n -> \n)
    formattedContent = formattedContent.replace(/\n\n+/g, '\n');
    
    // 줄바꿈 처리
    formattedContent = formattedContent.replace(/\n/g, '<br>');
    
    // Bold체 마크다운 적용 (** ** 형태)
    formattedContent = formattedContent.replace(
      /\*\*(.*?)\*\*/g, 
      '<strong class="font-bold text-gray-900 dark:text-white">$1</strong>'
    );
    
    // 콜론으로 끝나는 라벨들 Bold 처리
    formattedContent = formattedContent.replace(
      /^([^:]+):/gm, 
      '<strong class="font-bold text-gray-900 dark:text-white">$1:</strong>'
    );
    
    // 번호 리스트 Bold 처리 (줄바꿈 포함)
    formattedContent = formattedContent.replace(
      /(\d+\.\s)/g, 
      '<br><strong class="font-bold text-blue-600">$1</strong>'
    );
    
    // 중요한 키워드들 Bold 처리 (빨간색 대신 Bold체)
    const importantKeywords = [
      '중요', '핵심', '주의', '기억', '꼭', '반드시', '필수',
      '정답', '오답', '실수', '주의사항', '팁', 'TIP'
    ];
    
    importantKeywords.forEach(keyword => {
      const regex = new RegExp(`(${keyword})`, 'gi');
      formattedContent = formattedContent.replace(
        regex, 
        '<strong class="font-bold text-gray-900 dark:text-white">$1</strong>'
      );
    });

    switch (style) {
      case 'concise':
        formattedContent = formattedContent.replace(
          /(핵심|요약|결론|포인트)/gi,
          '<strong class="font-bold text-blue-700 dark:text-blue-300">$1</strong>'
        );
        return formattedContent;
      case 'casual':
        return formattedContent
          .replace(/합니다/g, '해')
          .replace(/입니다/g, '야')
          .replace(/하세요/g, '해')
          .replace(/됩니다/g, '돼');
      case 'friendly':
        return formattedContent
          .replace(/!/g, '! 😊')
          .replace(/\?/g, '? 💡')
          .replace(/(좋다|훌륭하다|잘했다)/gi, '<strong class="text-green-600">$1</strong> 👍');
      default:
        return formattedContent;
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

      // 초기 메시지 추가 - Bold체 적용 개선
      const welcomeMessage = {
        id: Date.now(),
        type: 'mentor',
        content: applyTextStyle(
          `**안녕하세요!** ${data.session.user_name || '학습자'}님. AI 학습 멘토입니다. 무엇을 도와드릴까요?\n**주요 기능:**\n• 프로그래밍 질문 답변\n• 학습 방향 가이드\n• 코드 리뷰 및 개선 제안`,
          textStyle
        ),
        timestamp: new Date()
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
      {/* 헤더 - 개선된 설정 및 새 세션 버튼 */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold">AI 멘토링</h2>
          <p className="text-gray-600">24/7 개인 학습 코치와 대화하세요</p>
        </div>
        
        <div className="flex items-center space-x-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => setShowSettings(!showSettings)}
          >
            <Settings className="w-4 h-4 mr-2" />
            설정
          </Button>
          
          {session && (
            <Button 
              variant="outline" 
              size="sm" 
              onClick={() => {
                setSession(null);
                setMessages([]);
              }}
            >
              <RefreshCw className="w-4 h-4 mr-2" />
              새 세션
            </Button>
          )}
        </div>
      </div>

      {/* 설정 패널 - 간소화 */}
      {showSettings && (
        <Card>
          <CardHeader>
            <CardTitle className="text-base">멘토링 설정</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {/* 텍스트 스타일 설정 */}
            <div>
              <label className="text-sm font-medium flex items-center mb-2">
                <Type className="w-4 h-4 mr-1" />
                텍스트 스타일
              </label>
              <select 
                value={textStyle} 
                onChange={(e) => setTextStyle(e.target.value)}
                className="w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
              >
                {textStyleOptions.map((style) => (
                  <option key={style.id} value={style.id}>
                    {style.label} - {style.description}
                  </option>
                ))}
              </select>
            </div>

            {/* 행간 설정 */}
            <div>
              <label className="text-sm font-medium flex items-center mb-2">
                <Eye className="w-4 h-4 mr-1" />
                행간 설정
              </label>
              <select 
                value={lineHeight} 
                onChange={(e) => setLineHeight(e.target.value)}
                className="w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
              >
                {lineHeightOptions.map((option) => (
                  <option key={option.id} value={option.id}>
                    {option.label}
                  </option>
                ))}
              </select>
            </div>
          </CardContent>
        </Card>
      )}

      {/* 채팅 영역 - 확장된 크기 */}
      <Card className="h-[600px]">
        <CardHeader>
          <CardTitle className="flex items-center">
            <MessageCircle className="w-5 h-5 mr-2" />
            멘토링 채팅
            <Badge variant="secondary" className="ml-2">
              {textStyleOptions.find(s => s.id === textStyle)?.label}
            </Badge>
          </CardTitle>
        </CardHeader>
        <CardContent className="h-full flex flex-col p-6">
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
                      } rounded-lg p-4`} style={getLineHeightStyle(lineHeight)}>
                        <div className="flex items-start space-x-3">
                          {message.type === 'mentor' ? (
                            <Bot className="w-5 h-5 mt-1 text-blue-500 flex-shrink-0" />
                          ) : (
                            <User className="w-5 h-5 mt-1 flex-shrink-0" />
                          )}
                          <div className="flex-1">
                            <div
                              className="text-base"
                              dangerouslySetInnerHTML={{
                                __html: applyTextStyle(message.content, textStyle)
                              }}
                            />
                            <p className="text-xs opacity-70 mt-2">
                              {message.timestamp.toLocaleTimeString()}
                            </p>
                          </div>
                        </div>

                        {/* 멘토 추가 정보 - 설정 기반 표시 */}
                        {message.type === 'mentor' && (
                          <div className="mt-4 space-y-3" style={getLineHeightStyle(lineHeight)}>
                            {showSuggestions && message.suggestions && message.suggestions.length > 0 && (
                              <div>
                                <p className="text-sm font-medium mb-2">💡 제안사항:</p>
                                <div className="space-y-2">
                                  {message.suggestions.map((suggestion, index) => (
                                    <div key={index} className="text-sm bg-blue-50 text-blue-800 p-3 rounded">
                                      <span dangerouslySetInnerHTML={{
                                        __html: applyTextStyle(suggestion, textStyle)
                                      }} />
                                    </div>
                                  ))}
                                </div>
                              </div>
                            )}

                            {showFollowUps && message.follow_up_questions && message.follow_up_questions.length > 0 && (
                              <div>
                                <p className="text-sm font-medium mb-2">❓ 후속 질문:</p>
                                <div className="space-y-2">
                                  {message.follow_up_questions.map((question, index) => (
                                    <button
                                      key={index} 
                                      className="text-sm bg-yellow-50 text-yellow-800 p-3 rounded w-full text-left hover:bg-yellow-100 transition-colors"
                                      onClick={() => setInputMessage(question)}
                                    >
                                      <span dangerouslySetInnerHTML={{
                                        __html: applyTextStyle(question, textStyle)
                                      }} />
                                    </button>
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
                      <div className="bg-gray-100 text-gray-900 rounded-lg p-4">
                        <div className="flex items-center space-x-3">
                          <Bot className="w-5 h-5 text-blue-500" />
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
                  className="flex-1 text-base"
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
    </div>
  );
};

export default AIMentorChatImproved;
