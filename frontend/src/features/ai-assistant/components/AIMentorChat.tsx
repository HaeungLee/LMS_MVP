import React, { useState, useEffect, useRef } from 'react';
import {
  MessageCircle,
  Send,
  Bot,
  User,
  HelpCircle,
  Heart,
  BookOpen,
  Target,
  Lightbulb,
  RefreshCw
} from 'lucide-react';

interface Message {
  id: string;
  type: 'user' | 'mentor';
  content: string;
  timestamp: Date;
  teachingGuidance?: string;
  suggestedActions?: string[];
}

interface TeachingSession {
  id: number | string;
  session_title: string;
  current_step: number;
  total_steps: number;
  completion_percentage: number;
  session_status: string;
}

interface AIMentorChatProps {
  userId?: number;
}

const AIMentorChat: React.FC<AIMentorChatProps> = ({ userId }) => {
  const [session, setSession] = useState<TeachingSession | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [conversationMode, setConversationMode] = useState('help_seeking');
  const scrollAreaRef = useRef<HTMLDivElement>(null);

  // 대화 모드 옵션
  const conversationModes = [
    { id: 'help_seeking', label: '도움 요청', icon: HelpCircle, color: 'blue' },
    { id: 'motivation', label: '동기 부여', icon: Heart, color: 'red' },
    { id: 'explanation', label: '설명 요청', icon: BookOpen, color: 'green' },
    { id: 'guidance', label: '학습 가이드', icon: Target, color: 'purple' },
    { id: 'reflection', label: '학습 성찰', icon: Lightbulb, color: 'yellow' }
  ];

  // 텍스트 포맷팅 - 구분선 제거 및 가독성 향상
  const formatText = (text: string) => {
    if (!text) return '';
    
    // 구분선 패턴들 제거 (가독성 저해 요소)
    let formatted = text
      // 연속된 대시나 하이픈 구분선 제거
      .replace(/^[-─=_*~]{3,}$/gm, '')
      // 양쪽에 공백이 있는 구분선 제거  
      .replace(/^\s*[-─=_*~]{3,}\s*$/gm, '')
      // 중간에 텍스트가 있는 구분선도 정리
      .replace(/^[-─=_*~]{2,}\s*.+\s*[-─=_*~]{2,}$/gm, (match) => {
        // 구분선 사이의 텍스트만 추출
        const textMatch = match.match(/[-─=_*~]{2,}\s*(.+?)\s*[-─=_*~]{2,}/);
        return textMatch ? `**${textMatch[1].trim()}**` : '';
      });
    
    // 모든 형태의 취소선 제거
    formatted = formatted
      // 마크다운 취소선 (~~텍스트~~)
      .replace(/~~([^~]+?)~~/g, '$1')
      // 대괄호 안 취소선 제거
      .replace(/\[~~([^\]]+?)~~\]/g, '$1')
      // HTML 취소선 태그들 제거
      .replace(/<del[^>]*>([^<]+?)<\/del>/gi, '$1')
      .replace(/<s[^>]*>([^<]+?)<\/s>/gi, '$1')
      .replace(/<strike[^>]*>([^<]+?)<\/strike>/gi, '$1')
      // 유니코드 취소선 문자 제거 (U+0336)
      .replace(/([^\u0336]+)\u0336+/g, '$1')
      // CSS style로 적용된 취소선도 제거
      .replace(/<span[^>]*text-decoration[^>]*line-through[^>]*>([^<]+?)<\/span>/gi, '$1')
      // 기타 스타일 속성에서 취소선 제거
      .replace(/style="[^"]*text-decoration:[^;]*line-through[^"]*"/gi, '');
    
    // Bold 텍스트 처리
    formatted = formatted.replace(/\*\*([^*]+?)\*\*/g, '<strong class="font-semibold text-blue-700">$1</strong>');
    
    // 연속된 빈 줄 정리 (3개 이상의 연속 줄바꿈을 2개로)
    formatted = formatted.replace(/\n{3,}/g, '\n\n');
    
    // 줄바꿈 처리
    formatted = formatted.replace(/\n/g, '<br>');
    
    // 연속된 br 태그 정리
    formatted = formatted.replace(/(<br>){3,}/g, '<br><br>');
    
    // 특수 문자와 이모지 보존
    return formatted;
  };

  // 메시지 내용 렌더링 - 취소선 완전 제거
  const renderMessageContent = (content: string) => {
    return (
      <div 
        className="max-w-none leading-relaxed word-break-words text-sm antialiased"
        style={{ 
          whiteSpace: 'pre-wrap',
          wordWrap: 'break-word',
          overflowWrap: 'break-word',
          textDecoration: 'none',
          textDecorationLine: 'none',
          lineHeight: '1.6',
          fontSize: '14px',
          color: 'inherit'
        }}
      >
        <div
          style={{
            textDecoration: 'none',
            textDecorationLine: 'none'
          }}
          className="strikethrough-none"
          dangerouslySetInnerHTML={{ __html: formatText(content) }}
        />
        <style dangerouslySetInnerHTML={{
          __html: `
            .strikethrough-none, 
            .strikethrough-none *, 
            .strikethrough-none del, 
            .strikethrough-none s, 
            .strikethrough-none strike {
              text-decoration: none !important;
              text-decoration-line: none !important;
            }
          `
        }} />
      </div>
    );
  };

  // 세션 시작 - 실제 LLM 연결된 엔드포인트 사용
  const startMentorSession = async (initialQuestion?: string) => {
    try {
      setLoading(true);
      
      // 기존의 실제 LLM 연결된 엔드포인트 사용
      const response = await fetch(`/api/v1/ai-features/mentoring/start-session/${userId || 1}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include', // 쿠키 포함
        body: JSON.stringify({
          initial_question: initialQuestion,
          text_style: 'default',
          line_height: 'comfortable'
        })
      });
      
      const data = await response.json();
      console.log('멘토링 세션 시작 성공:', data); // 디버깅용
      
      if (data.success) {
        const sessionData = {
          id: data.session.session_id,
          session_title: '멘토링 세션',
          current_step: 1,
          total_steps: 1,
          completion_percentage: 0,
          session_status: 'active'
        };
        
        setSession(sessionData);
        
        // 환영 메시지 추가
        const welcomeMessage: Message = {
          id: `mentor-${Date.now()}`,
          type: 'mentor',
          content: data.session.greeting || `안녕하세요! 저는 AI 멘토입니다. 

${conversationModes.find(m => m.id === conversationMode)?.label} 모드로 대화를 시작하겠습니다. 

학습에 대한 어떤 도움이 필요하신가요? 궁금한 것이 있거나, 동기부여가 필요하시거나, 개념 설명을 원하시면 언제든 말씀해주세요! 😊`,
          timestamp: new Date(),
        };
        setMessages([welcomeMessage]);
      } else {
        throw new Error('세션 시작 실패');
      }
    } catch (error) {
      console.error('멘토링 세션 시작 오류:', error);
    } finally {
      setLoading(false);
    }
  };

  // 메시지 전송 - 실제 LLM 연결된 엔드포인트 사용
  const sendMessage = async () => {
    if (!inputMessage.trim() || !session || loading) return;

    const userMessage: Message = {
      id: `user-${Date.now()}`,
      type: 'user',
      content: inputMessage,
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setLoading(true);
    
    const messageToSend = inputMessage;
    setInputMessage('');

    try {
      // 실제 LLM 연결된 엔드포인트 사용
      const response = await fetch(`/api/v1/ai-features/mentoring/chat/${session.id}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({
          message: messageToSend,
          conversation_mode: conversationMode,
          text_style: 'default',
          line_height: 'comfortable'
        })
      });
      
      const data = await response.json();
      console.log('멘토링 대화 응답:', data); // 디버깅용
      
      if (data.success) {
        const mentorMessage: Message = {
          id: `mentor-${Date.now()}`,
          type: 'mentor',
          content: data.response || '응답을 받았지만 내용이 비어있습니다.',
          timestamp: new Date(),
          suggestedActions: data.follow_up_questions || [],
        };

        setMessages(prev => [...prev, mentorMessage]);
      } else {
        throw new Error('응답 생성 실패');
      }
    } catch (error) {
      console.error('메시지 전송 실패:', error);
      
      // 에러 시 기본 응답
      const errorMessage: Message = {
        id: `mentor-error-${Date.now()}`,
        type: 'mentor',
        content: '죄송합니다. 일시적인 문제가 발생했습니다. 잠시 후 다시 시도해주세요.',
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  // 메시지 스크롤
  useEffect(() => {
    if (scrollAreaRef.current) {
      scrollAreaRef.current.scrollTop = scrollAreaRef.current.scrollHeight;
    }
  }, [messages]);

  const getModeColor = (mode: string) => {
    const modeData = conversationModes.find(m => m.id === mode);
    return modeData?.color || 'blue';
  };

  const handleKeyPress = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className="w-full max-w-4xl mx-auto">
      <div className="bg-white border border-gray-200 rounded-lg shadow-sm">
        {/* 헤더 */}
        <div className="px-6 py-4 border-b border-gray-200">
          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <MessageCircle className="w-5 h-5 mr-2 text-blue-500" />
              <h3 className="text-lg font-semibold text-gray-900">AI 멘토링 채팅</h3>
            </div>
            {session && (
              <div className="flex items-center space-x-2">
                <span className={`px-2 py-1 text-xs font-medium rounded-full bg-${getModeColor(conversationMode)}-100 text-${getModeColor(conversationMode)}-800`}>
                  {conversationModes.find(m => m.id === conversationMode)?.label}
                </span>
                <button
                  onClick={() => startMentorSession()}
                  className="p-1 hover:bg-gray-100 rounded"
                  disabled={loading}
                >
                  <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
                </button>
              </div>
            )}
          </div>
        </div>

        <div className="h-[600px] flex flex-col">
          {!session ? (
            /* 세션 시작 화면 */
            <div className="flex-1 flex items-center justify-center p-6">
              <div className="text-center max-w-md">
                <Bot className="w-16 h-16 mx-auto mb-4 text-blue-400" />
                <h3 className="text-xl font-semibold text-gray-900 mb-2">
                  AI 멘토와 대화를 시작해보세요
                </h3>
                <p className="text-gray-600 mb-6">
                  학습에 대한 궁금함이나 도움이 필요한 부분을 자유롭게 질문해주세요.
                  AI 멘토가 친절하게 도움을 드릴게요!
                </p>

                {/* 대화 모드 선택 */}
                <div className="mb-6">
                  <p className="text-sm font-medium text-gray-700 mb-3">대화 모드 선택:</p>
                  <div className="grid grid-cols-2 gap-2">
                    {conversationModes.slice(0, 4).map((mode) => {
                      const IconComponent = mode.icon;
                      return (
                        <button
                          key={mode.id}
                          onClick={() => setConversationMode(mode.id)}
                          className={`p-2 text-sm rounded-lg border transition-colors ${
                            conversationMode === mode.id
                              ? `bg-${mode.color}-50 border-${mode.color}-200 text-${mode.color}-700`
                              : 'bg-gray-50 border-gray-200 text-gray-600 hover:bg-gray-100'
                          }`}
                        >
                          <IconComponent className="w-4 h-4 mx-auto mb-1" />
                          {mode.label}
                        </button>
                      );
                    })}
                  </div>
                </div>

                <button 
                  onClick={() => startMentorSession()}
                  disabled={loading}
                  className="px-6 py-3 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {loading ? (
                    <div className="flex items-center">
                      <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                      세션 시작 중...
                    </div>
                  ) : (
                    '새 멘토링 세션 시작'
                  )}
                </button>
              </div>
            </div>
          ) : (
            /* 채팅 화면 */
            <>
              {/* 메시지 영역 */}
              <div 
                ref={scrollAreaRef}
                className="flex-1 overflow-y-auto p-4 space-y-4 min-h-0"
                style={{ scrollBehavior: 'smooth' }}
              >
                {messages.map((message) => (
                  <div
                    key={message.id}
                    className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'} mb-4`}
                  >
                    <div className={`w-full max-w-[90%] ${
                      message.type === 'user'
                        ? 'bg-blue-500 text-white'
                        : 'bg-gray-50 text-gray-900 border border-gray-200'
                    } rounded-lg p-4 shadow-sm overflow-hidden`}>
                      <div className="flex items-start space-x-3">
                        {message.type === 'mentor' && (
                          <Bot className="w-5 h-5 mt-1 text-blue-500 flex-shrink-0" />
                        )}
                        {message.type === 'user' && (
                          <User className="w-5 h-5 mt-1 flex-shrink-0 text-white" />
                        )}
                        <div className="flex-1">
                          {renderMessageContent(message.content)}
                          
                          {/* 학습 팁이나 가이드 표시 */}
                          {message.suggestedActions && message.suggestedActions.length > 0 && (
                            <div className="mt-3 p-3 bg-blue-50 rounded-lg border-l-4 border-blue-400">
                              <div className="text-sm text-blue-800">
                                <strong className="flex items-center mb-2">
                                  💡 후속 질문:
                                </strong>
                                <ul className="space-y-1">
                                  {message.suggestedActions.map((action, index) => (
                                    <li key={index} className="flex items-start">
                                      <button
                                        onClick={() => setInputMessage(action)}
                                        className="text-left text-blue-600 hover:text-blue-800 hover:underline"
                                      >
                                        • {action}
                                      </button>
                                    </li>
                                  ))}
                                </ul>
                              </div>
                            </div>
                          )}

                          {/* 이해도 체크 질문 표시 */}
                          {message.teachingGuidance && (
                            <div className="mt-3 p-3 bg-green-50 rounded-lg border-l-4 border-green-400">
                              <div className="text-sm text-green-800">
                                <strong className="flex items-center mb-1">
                                  🤔 이해도 체크:
                                </strong>
                                <p>{message.teachingGuidance}</p>
                              </div>
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>
                ))}

                {loading && (
                  <div className="flex justify-start mb-4">
                    <div className="bg-gray-50 border border-gray-200 rounded-lg p-4 shadow-sm">
                      <div className="flex items-center space-x-3">
                        <Bot className="w-5 h-5 text-blue-500" />
                        <div className="flex items-center space-x-2">
                          <span className="text-gray-600 text-sm">AI 멘토가 답변하고 있습니다</span>
                          <div className="flex space-x-1">
                            <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce"></div>
                            <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{animationDelay: '0.1s'}}></div>
                            <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                )}
              </div>

              {/* 입력 영역 */}
              <div className="p-4 border-t border-gray-200 bg-gray-50">
                <div className="flex space-x-3">
                  <textarea
                    value={inputMessage}
                    onChange={(e) => setInputMessage(e.target.value)}
                    placeholder={`${conversationModes.find(m => m.id === conversationMode)?.label} 메시지를 입력하세요...`}
                    onKeyPress={handleKeyPress}
                    disabled={loading}
                    rows={2}
                    className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 disabled:opacity-50 resize-none"
                  />
                  <button
                    onClick={sendMessage}
                    disabled={loading || !inputMessage.trim()}
                    className="px-6 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center space-x-2"
                  >
                    <Send className="w-4 h-4" />
                    <span>{loading ? '전송 중...' : '전송'}</span>
                  </button>
                </div>
                <div className="mt-2 text-xs text-gray-500">
                  Enter로 전송 • Shift+Enter로 줄바꿈
                </div>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
};

export default AIMentorChat;