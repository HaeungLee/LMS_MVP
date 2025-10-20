/**
 * 플로팅 AI 멘토 - 모든 페이지에서 접근 가능
 * 우측 하단 고정 버튼
 * OpenRouter API 연동
 */

import { useState, useRef, useEffect } from 'react';
import { X, Send, Sparkles, Minimize2, Maximize2 } from 'lucide-react';
import useAuthStore from '../hooks/useAuthStore';

interface Message {
  role: 'user' | 'ai';
  text: string;
  timestamp: Date;
}

export default function FloatingAIMentor() {
  const { user } = useAuthStore();
  const [isOpen, setIsOpen] = useState(false);
  const [isMinimized, setIsMinimized] = useState(false);
  const [message, setMessage] = useState('');
  const [messages, setMessages] = useState<Message[]>([]);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // 채팅창이 열릴 때 세션 시작
  useEffect(() => {
    if (isOpen && !isMinimized && !sessionId && messages.length === 0) {
      startSession();
    }
  }, [isOpen, isMinimized]);

  // 세션 시작
  const startSession = async (): Promise<string | null> => {
    try {
      const response = await fetch(`/api/v1/ai-features/mentoring/start-session/${user?.id || 1}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({
          initial_question: null,
          text_style: 'default',
          line_height: 'comfortable'
        })
      });
      
      const data = await response.json();
      
      if (data.success && data.session) {
        const newSessionId = data.session.session_id;
        setSessionId(newSessionId);
        
        // 환영 메시지 추가 (기존 메시지가 없을 때만)
        if (data.session.greeting && messages.length === 0) {
          const welcomeMessage: Message = {
            role: 'ai',
            text: data.session.greeting,
            timestamp: new Date()
          };
          setMessages([welcomeMessage]);
        }
        
        return newSessionId;
      }
      return null;
    } catch (error) {
      console.error('세션 시작 실패:', error);
      return null;
    }
  };

  // 메시지 전송
  const handleSend = async () => {
    if (!message.trim() || loading) return;

    const messageToSend = message;
    setMessage('');
    setLoading(true);

    // 사용자 메시지 추가
    const userMessage: Message = {
      role: 'user',
      text: messageToSend,
      timestamp: new Date()
    };
    setMessages(prev => [...prev, userMessage]);

    try {
      // 세션이 없으면 먼저 생성
      let currentSessionId = sessionId;
      if (!currentSessionId) {
        currentSessionId = await startSession();
        
        // 여전히 세션이 없으면 에러
        if (!currentSessionId) {
          throw new Error('세션 생성 실패');
        }
      }

      const response = await fetch(`/api/v1/ai-features/mentoring/chat/${currentSessionId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({
          message: messageToSend,
          conversation_mode: 'help_seeking',
          text_style: 'default',
          line_height: 'comfortable'
        })
      });
      
      const data = await response.json();
      
      console.log('API 응답:', data); // 디버깅용
      
      if (data.success && data.response !== undefined && data.response !== null) {
        const aiMessage: Message = {
          role: 'ai',
          text: data.response || '(응답 없음)',
          timestamp: new Date()
        };
        setMessages(prev => [...prev, aiMessage]);
      } else {
        console.error('API 응답 오류:', data);
        throw new Error(data.error || '응답 생성 실패');
      }
    } catch (error) {
      console.error('메시지 전송 실패:', error);
      const errorMessage: Message = {
        role: 'ai',
        text: '죄송합니다. 일시적인 오류가 발생했습니다. 잠시 후 다시 시도해주세요.',
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) {
    return (
      <button
        onClick={() => setIsOpen(true)}
        className="fixed bottom-8 right-8 w-16 h-16 bg-gradient-to-br from-purple-500 to-pink-500 rounded-full shadow-2xl hover:scale-110 transition-transform duration-200 flex items-center justify-center z-50"
        aria-label="AI 멘토 열기"
      >
        <Sparkles className="w-8 h-8 text-white" />
      </button>
    );
  }

  return (
    <div className={`fixed bottom-8 right-8 z-50 transition-all duration-300 ${
      isMinimized ? 'w-80' : 'w-96'
    }`}>
      <div className="bg-white rounded-2xl shadow-2xl overflow-hidden border-2 border-purple-200">
        {/* 헤더 */}
        <div className="bg-gradient-to-r from-purple-600 to-pink-600 p-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-white/20 rounded-full flex items-center justify-center">
              <Sparkles className="w-5 h-5 text-white" />
            </div>
            <div className="text-white">
              <h3 className="font-bold">AI 멘토</h3>
              <p className="text-xs opacity-90">24/7 학습 도우미</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={() => setIsMinimized(!isMinimized)}
              className="p-2 hover:bg-white/20 rounded-lg transition-colors"
            >
              {isMinimized ? (
                <Maximize2 className="w-4 h-4 text-white" />
              ) : (
                <Minimize2 className="w-4 h-4 text-white" />
              )}
            </button>
            <button
              onClick={() => setIsOpen(false)}
              className="p-2 hover:bg-white/20 rounded-lg transition-colors"
            >
              <X className="w-5 h-5 text-white" />
            </button>
          </div>
        </div>

        {/* 채팅 영역 */}
        {!isMinimized && (
          <>
            <div className="h-96 overflow-y-auto p-4 bg-gray-50">
              {messages.length === 0 ? (
                <div className="h-full flex items-center justify-center">
                  <div className="text-center">
                    <div className="w-16 h-16 bg-gradient-to-br from-purple-100 to-pink-100 rounded-full flex items-center justify-center mx-auto mb-4">
                      <Sparkles className="w-8 h-8 text-purple-600" />
                    </div>
                    <p className="text-gray-600 mb-2">안녕하세요! 👋</p>
                    <p className="text-sm text-gray-500">
                      학습 중 궁금한 점을<br />
                      언제든 물어보세요!
                    </p>
                  </div>
                </div>
              ) : (
                <div className="space-y-4">
                  {messages.map((msg, idx) => (
                    <div
                      key={idx}
                      className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                    >
                      <div
                        className={`max-w-xs px-4 py-3 rounded-2xl ${
                          msg.role === 'user'
                            ? 'bg-gradient-to-r from-purple-600 to-pink-600 text-white'
                            : 'bg-white text-gray-900 border border-gray-200 shadow-sm'
                        }`}
                      >
                        <p className="text-sm whitespace-pre-wrap leading-relaxed">{msg.text}</p>
                        <p className="text-xs opacity-60 mt-1">
                          {msg.timestamp.toLocaleTimeString('ko-KR', { 
                            hour: '2-digit', 
                            minute: '2-digit' 
                          })}
                        </p>
                      </div>
                    </div>
                  ))}
                  {loading && (
                    <div className="flex justify-start">
                      <div className="bg-white text-gray-900 border border-gray-200 shadow-sm px-4 py-3 rounded-2xl">
                        <div className="flex gap-1">
                          <div className="w-2 h-2 bg-purple-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                          <div className="w-2 h-2 bg-purple-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                          <div className="w-2 h-2 bg-purple-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
                        </div>
                      </div>
                    </div>
                  )}
                  <div ref={messagesEndRef} />
                </div>
              )}
            </div>

            {/* 입력 영역 */}
            <div className="p-4 bg-white border-t border-gray-200">
              <div className="flex gap-2">
                <input
                  type="text"
                  value={message}
                  onChange={(e) => setMessage(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && !loading && handleSend()}
                  placeholder="궁금한 점을 물어보세요..."
                  disabled={loading}
                  className="flex-1 px-4 py-2 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-purple-500 text-sm disabled:bg-gray-100"
                />
                <button
                  onClick={handleSend}
                  disabled={loading || !message.trim()}
                  className="px-4 py-2 bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-xl hover:shadow-lg transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <Send className="w-4 h-4" />
                </button>
              </div>
              
              {/* 추천 질문 */}
              {messages.length === 0 && (
                <div className="mt-3 flex flex-wrap gap-2">
                  {[
                    "개념 설명해줘",
                    "예제 보여줘",
                    "학습 방법 알려줘"
                  ].map((q, idx) => (
                    <button
                      key={idx}
                      onClick={() => setMessage(q)}
                      disabled={loading}
                      className="text-xs px-3 py-1 bg-purple-50 text-purple-700 rounded-full border border-purple-200 hover:bg-purple-100 transition-colors disabled:opacity-50"
                    >
                      {q}
                    </button>
                  ))}
                </div>
              )}
            </div>
          </>
        )}

        {/* 최소화 상태 */}
        {isMinimized && (
          <div className="p-4 bg-white">
            <p className="text-sm text-gray-600 text-center">
              AI 멘토가 대기 중입니다
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
