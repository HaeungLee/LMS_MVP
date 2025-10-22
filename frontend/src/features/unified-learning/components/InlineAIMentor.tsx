/**
 * 인라인 AI 멘토 - 학습 중 즉시 질문 가능
 * RAG로 현재 교재 내용 기반 답변
 */

import { useState } from 'react';
import { Send, Sparkles, Loader2 } from 'lucide-react';
import useAuthStore from '../../../shared/hooks/useAuthStore';

interface InlineAIMentorProps {
  context: 'textbook' | 'practice' | 'quiz';
  topic: string;
  currentContent?: string; // 현재 보고 있는 교재 내용
}

export default function InlineAIMentor({ topic, currentContent }: InlineAIMentorProps) {
  const { user } = useAuthStore();
  const [isExpanded, setIsExpanded] = useState(false);
  const [message, setMessage] = useState('');
  const [messages, setMessages] = useState<Array<{ role: 'user' | 'ai', text: string }>>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(null);

  const handleSend = async () => {
    if (!message.trim() || isLoading) return;

    // 사용자 메시지 추가
    const userMessage = message;
    setMessages(prev => [...prev, { role: 'user', text: userMessage }]);
    setMessage('');
    setIsLoading(true);

    try {
      // 세션이 없으면 새로 시작
      if (!sessionId) {
        const startRes = await fetch(`/api/v1/ai-features/mentoring/start-session/${user?.id || 1}`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          credentials: 'include',
          body: JSON.stringify({
            initial_question: `현재 학습 주제: ${topic}\n\n교재 내용:\n${currentContent?.substring(0, 500) || ''}...\n\n질문: ${userMessage}`,
            text_style: 'default',
            line_height: 'comfortable'
          })
        });

        if (!startRes.ok) throw new Error('세션 시작 실패');
        
        const startData = await startRes.json();
        if (startData.success && startData.session) {
          setSessionId(startData.session.session_id);
          
          // 인사말이 있으면 AI 응답으로 추가
          if (startData.session.greeting) {
            setMessages(prev => [...prev, { 
              role: 'ai', 
              text: startData.session.greeting 
            }]);
          }
        }
      } else {
        // 기존 세션으로 대화 계속
        const chatRes = await fetch(`/api/v1/ai-features/mentoring/chat/${sessionId}`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          credentials: 'include',
          body: JSON.stringify({
            message: `${userMessage}\n\n(참고: 현재 "${topic}" 학습 중)`,
            conversation_mode: 'explanation',
            text_style: 'default',
            line_height: 'comfortable'
          })
        });

        if (!chatRes.ok) throw new Error('응답 생성 실패');
        
        const chatData = await chatRes.json();
        if (chatData.success && chatData.response) {
          setMessages(prev => [...prev, { 
            role: 'ai', 
            text: chatData.response 
          }]);
        }
      }
    } catch (error) {
      console.error('AI 멘토 오류:', error);
      setMessages(prev => [...prev, {
        role: 'ai',
        text: `죄송합니다. 일시적인 문제가 발생했습니다.\n\n**오류:** ${error instanceof Error ? error.message : '알 수 없는 오류'}\n\n잠시 후 다시 시도해주세요.`
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="bg-gradient-to-br from-purple-50 to-pink-50 rounded-2xl shadow-lg p-6 border-2 border-purple-200">
      {/* 헤더 */}
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full flex items-center justify-between"
      >
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-gradient-to-br from-purple-500 to-pink-500 rounded-full flex items-center justify-center">
            <Sparkles className="w-5 h-5 text-white" />
          </div>
          <div className="text-left">
            <h3 className="font-bold text-gray-900">💬 이해 안 가는 부분이 있나요?</h3>
            <p className="text-sm text-gray-600">AI 멘토에게 바로 물어보세요</p>
          </div>
        </div>
        <div className="text-purple-600">
          {isExpanded ? '접기' : '펼치기'}
        </div>
      </button>

      {/* 채팅 영역 */}
      {isExpanded && (
        <div className="mt-4 space-y-4">
          {/* 메시지 목록 */}
          {messages.length > 0 && (
            <div className="bg-white rounded-xl p-4 max-h-64 overflow-y-auto space-y-3">
              {messages.map((msg, idx) => (
                <div
                  key={idx}
                  className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div
                    className={`max-w-xs px-4 py-2 rounded-2xl ${
                      msg.role === 'user'
                        ? 'bg-indigo-600 text-white'
                        : 'bg-gray-100 text-gray-900'
                    }`}
                  >
                    <p className="text-sm whitespace-pre-wrap">{msg.text}</p>
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* 입력 영역 */}
          <div className="flex gap-2">
            <input
              type="text"
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && !isLoading && handleSend()}
              placeholder={`"${topic}"에 대해 궁금한 점을 물어보세요...`}
              disabled={isLoading}
              className="flex-1 px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-purple-500 disabled:bg-gray-100"
            />
            <button
              onClick={handleSend}
              disabled={isLoading || !message.trim()}
              className="px-6 py-3 bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-xl hover:shadow-lg transition-all duration-200 flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isLoading ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                <Send className="w-4 h-4" />
              )}
            </button>
          </div>

          {/* 추천 질문 */}
          {messages.length === 0 && (
            <div className="space-y-2">
              <p className="text-xs text-gray-500">💡 이런 걸 물어볼 수 있어요:</p>
              <div className="flex flex-wrap gap-2">
                {[
                  "이 개념을 쉽게 설명해줘",
                  "실무에서 어떻게 쓰이나요?",
                  "예제 하나 더 보여줘"
                ].map((q, idx) => (
                  <button
                    key={idx}
                    onClick={() => setMessage(q)}
                    className="text-xs px-3 py-1.5 bg-white text-purple-700 rounded-full border border-purple-200 hover:bg-purple-50 transition-colors"
                  >
                    {q}
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
