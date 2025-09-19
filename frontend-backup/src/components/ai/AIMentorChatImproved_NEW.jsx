import React, { useState, useEffect, useRef } from 'react';
import {
  MessageCircle,
  Send,
  Bot,
  User,
  Settings
} from 'lucide-react';

const AIMentorChatImproved = ({ userId }) => {
  const [session, setSession] = useState(null);
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [loading, setLoading] = useState(false);

  const startMentorSession = async () => {
    try {
      console.log('AI 멘토링 세션 시작');
      setSession({ id: 'temp-session' });
    } catch (error) {
      console.error('세션 시작 오류:', error);
    }
  };

  const sendMessage = () => {
    if (!inputMessage.trim()) return;
    
    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: inputMessage,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    
    // 간단한 응답
    setTimeout(() => {
      const mentorMessage = {
        id: Date.now() + 1,
        type: 'mentor',
        content: '안녕하세요! AI 멘토입니다. 무엇을 도와드릴까요?',
        timestamp: new Date()
      };
      setMessages(prev => [...prev, mentorMessage]);
    }, 1000);
  };

  return (
    <div className="w-full max-w-4xl mx-auto p-6">
      <div className="bg-white border border-gray-200 rounded-lg shadow">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-semibold flex items-center">
            <MessageCircle className="w-5 h-5 mr-2" />
            AI 멘토링 채팅
          </h3>
        </div>
        <div className="p-6 h-full flex flex-col">
          {!session ? (
            <div className="flex-1 flex items-center justify-center">
              <div className="text-center">
                <Bot className="w-12 h-12 mx-auto mb-4 text-gray-400" />
                <h3 className="text-lg font-semibold mb-2">AI 멘토와 대화 시작</h3>
                <p className="text-gray-600 mb-4">
                  궁금한 것이 있거나 학습 도움이 필요하신가요?
                </p>
                <button 
                  onClick={startMentorSession}
                  className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
                >
                  새 멘토링 세션 시작
                </button>
              </div>
            </div>
          ) : (
            <>
              <div className="flex-1 overflow-auto pr-4 mb-4">
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
                      } rounded-lg p-4`}>
                        <div className="flex items-start space-x-3">
                          {message.type === 'mentor' ? (
                            <Bot className="w-5 h-5 mt-1 text-blue-500 flex-shrink-0" />
                          ) : (
                            <User className="w-5 h-5 mt-1 flex-shrink-0" />
                          )}
                          <div className="flex-1">
                            <div dangerouslySetInnerHTML={{ __html: message.content }} />
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              <div className="flex space-x-2">
                <input
                  value={inputMessage}
                  onChange={(e) => setInputMessage(e.target.value)}
                  placeholder="메시지를 입력하세요..."
                  onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
                  disabled={loading}
                  className="flex-1 px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
                <button
                  onClick={sendMessage}
                  disabled={loading || !inputMessage.trim()}
                  className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 disabled:opacity-50"
                >
                  <Send className="w-4 h-4" />
                </button>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
};

export default AIMentorChatImproved;
