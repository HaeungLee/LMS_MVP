/**
 * 플로팅 AI 멘토 - 모든 페이지에서 접근 가능
 * 우측 하단 고정 버튼
 */

import { useState } from 'react';
import { X, Send, Sparkles, Minimize2, Maximize2 } from 'lucide-react';

interface Message {
  role: 'user' | 'ai';
  text: string;
  timestamp: Date;
}

export default function FloatingAIMentor() {
  const [isOpen, setIsOpen] = useState(false);
  const [isMinimized, setIsMinimized] = useState(false);
  const [message, setMessage] = useState('');
  const [messages, setMessages] = useState<Message[]>([]);

  const handleSend = () => {
    if (!message.trim()) return;

    // 사용자 메시지 추가
    const userMessage: Message = {
      role: 'user',
      text: message,
      timestamp: new Date()
    };
    setMessages(prev => [...prev, userMessage]);

    // AI 응답 (임시)
    setTimeout(() => {
      const aiMessage: Message = {
        role: 'ai',
        text: `안녕하세요! "${message}"에 대해 도움을 드리겠습니다.\n\n(실제로는 AI 멘토가 맥락을 파악하여 답변합니다)`,
        timestamp: new Date()
      };
      setMessages(prev => [...prev, aiMessage]);
    }, 800);

    setMessage('');
  };

  if (!isOpen) {
    return (
      <button
        onClick={() => setIsOpen(true)}
        className="fixed bottom-8 right-8 w-16 h-16 bg-gradient-to-br from-purple-500 to-pink-500 rounded-full shadow-2xl hover:scale-110 transition-transform duration-200 flex items-center justify-center z-50 animate-pulse"
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
                        className={`max-w-xs px-4 py-2 rounded-2xl ${
                          msg.role === 'user'
                            ? 'bg-gradient-to-r from-purple-600 to-pink-600 text-white'
                            : 'bg-white text-gray-900 border border-gray-200'
                        }`}
                      >
                        <p className="text-sm whitespace-pre-wrap">{msg.text}</p>
                      </div>
                    </div>
                  ))}
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
                  onKeyPress={(e) => e.key === 'Enter' && handleSend()}
                  placeholder="궁금한 점을 물어보세요..."
                  className="flex-1 px-4 py-2 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-purple-500 text-sm"
                />
                <button
                  onClick={handleSend}
                  className="px-4 py-2 bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-xl hover:shadow-lg transition-all duration-200"
                >
                  <Send className="w-4 h-4" />
                </button>
              </div>
              
              {/* 추천 질문 */}
              {messages.length === 0 && (
                <div className="mt-3 flex flex-wrap gap-2">
                  {[
                    "이 개념 설명해줘",
                    "예제 보여줘",
                    "왜 이렇게 하나요?"
                  ].map((q, idx) => (
                    <button
                      key={idx}
                      onClick={() => setMessage(q)}
                      className="text-xs px-3 py-1 bg-purple-50 text-purple-700 rounded-full border border-purple-200 hover:bg-purple-100 transition-colors"
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
