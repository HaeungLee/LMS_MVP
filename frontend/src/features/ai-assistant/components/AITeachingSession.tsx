import React, { useState, useRef, useEffect } from 'react';
import { useMutation } from '@tanstack/react-query';
import { MessageCircle, ArrowLeft, Send, Bot, User, RefreshCw, AlertCircle } from 'lucide-react';
import { aiApi } from '../../../shared/services/apiClient';

interface Subject {
  id: number;
  key: string;
  title: string;
}

interface AITeachingSessionProps {
  subjects?: Subject[];
  onBack?: () => void;
}

interface Message {
  id: string;
  type: 'user' | 'ai';
  content: string;
  timestamp: Date;
  teachingGuidance?: string;
  suggestedActions?: string[];
}

export default function AITeachingSession({ subjects = [], onBack }: AITeachingSessionProps) {
  const [selectedSubject, setSelectedSubject] = useState('');
  const [customSubject, setCustomSubject] = useState('');
  const [sessionId, setSessionId] = useState<number | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isSessionStarted, setIsSessionStarted] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // 세션 시작 mutation
  const startSessionMutation = useMutation({
    mutationFn: aiApi.startTeachingSession,
    onSuccess: (data) => {
      setSessionId(data.session_id);
      setIsSessionStarted(true);
      
      // 환영 메시지 추가
      const finalSubject = customSubject.trim() || selectedSubject;
      const subjectTitle = subjects.find(s => s.key === selectedSubject)?.title || finalSubject;
      const welcomeMessage: Message = {
        id: `ai-${Date.now()}`,
        type: 'ai',
        content: `안녕하세요! 저는 ${subjectTitle} 전문 AI 강사입니다. 무엇을 배우고 싶으신가요?`,
        timestamp: new Date(),
      };
      setMessages([welcomeMessage]);
    },
  });

  // 메시지 전송 mutation
  const sendMessageMutation = useMutation({
    mutationFn: aiApi.sendTeachingMessage,
    onSuccess: (data, variables) => {
      // AI 응답 메시지 추가
      const aiMessage: Message = {
        id: `ai-${Date.now()}`,
        type: 'ai',
        content: data.response,
        timestamp: new Date(),
        teachingGuidance: data.teaching_guidance,
        suggestedActions: data.suggested_actions,
      };

      setMessages(prev => [...prev, aiMessage]);
    },
  });

  // 메시지 스크롤
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleStartSession = () => {
    const finalSubject = customSubject.trim() || selectedSubject;
    if (!finalSubject) {
      alert('학습할 과목을 선택하거나 입력해주세요');
      return;
    }

    startSessionMutation.mutate({
      subject_key: finalSubject,
      session_preferences: {
        learning_style: 'interactive',
        pace: 'adaptive',
      },
    });
  };

  const handleSendMessage = () => {
    if (!inputMessage.trim() || !sessionId || sendMessageMutation.isPending) {
      return;
    }

    // 사용자 메시지 추가
    const userMessage: Message = {
      id: `user-${Date.now()}`,
      type: 'user',
      content: inputMessage,
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);

    // AI에게 메시지 전송
    sendMessageMutation.mutate({
      session_id: sessionId,
      message: inputMessage,
      message_type: 'question',
    });

    setInputMessage('');
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const formatTime = (date: Date) => {
    return date.toLocaleTimeString('ko-KR', { 
      hour: '2-digit', 
      minute: '2-digit' 
    });
  };

  return (
    <div className="max-w-4xl mx-auto">
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 h-[600px] flex flex-col">
        {/* 헤더 */}
        <div className="flex items-center p-4 border-b border-gray-200">
          <button 
            onClick={onBack}
            className="mr-4 p-2 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <ArrowLeft className="w-5 h-5" />
          </button>
          <div className="flex-1">
            <h2 className="text-xl font-semibold text-gray-900">1:1 AI 강사 세션</h2>
            <p className="text-gray-600 text-sm">
              {isSessionStarted 
                ? `${subjects.find(s => s.key === selectedSubject)?.title || customSubject || selectedSubject} 학습 중` 
                : 'Phase 9 실시간 AI 교육 시스템'
              }
            </p>
          </div>
          {isSessionStarted && (
            <div className="flex items-center text-green-600">
              <div className="w-2 h-2 bg-green-500 rounded-full mr-2 animate-pulse"></div>
              <span className="text-sm">세션 활성</span>
            </div>
          )}
        </div>

        {!isSessionStarted ? (
          /* 세션 시작 화면 */
          <div className="flex-1 flex items-center justify-center p-6">
            <div className="text-center max-w-md">
              <Bot className="w-16 h-16 text-blue-600 mx-auto mb-4" />
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                AI 강사와 1:1 학습을 시작하세요
              </h3>
              <p className="text-gray-600 mb-6">
                선택한 과목의 전문 AI 강사가 개인 맞춤형 교육을 제공합니다.
              </p>

              <div className="mb-6">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  학습할 과목
                </label>
                
                {/* 기존 과목 선택 (있는 경우) */}
                {subjects.length > 0 && (
                  <div className="mb-3">
                    <select
                      value={selectedSubject}
                      onChange={(e) => {
                        setSelectedSubject(e.target.value);
                        if (e.target.value) setCustomSubject('');
                      }}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    >
                      <option value="">기존 과목에서 선택</option>
                      {subjects.map((subject) => (
                        <option key={subject.id} value={subject.key}>
                          {subject.title}
                        </option>
                      ))}
                    </select>
                  </div>
                )}
                
                {/* 직접 입력 */}
                <div>
                  <input
                    type="text"
                    value={customSubject}
                    onChange={(e) => {
                      setCustomSubject(e.target.value);
                      if (e.target.value) setSelectedSubject('');
                    }}
                    placeholder="또는 학습하고 싶은 과목을 직접 입력하세요"
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
              </div>

              {startSessionMutation.error && (
                <div className="bg-red-50 border border-red-200 rounded-lg p-3 mb-4">
                  <div className="flex items-center">
                    <AlertCircle className="w-4 h-4 text-red-600 mr-2" />
                    <span className="text-red-800 text-sm">
                      {startSessionMutation.error instanceof Error 
                        ? startSessionMutation.error.message 
                        : '세션 시작에 실패했습니다.'
                      }
                    </span>
                  </div>
                </div>
              )}

              <button
                onClick={handleStartSession}
                disabled={(!selectedSubject && !customSubject.trim()) || startSessionMutation.isPending}
                className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed flex items-center mx-auto"
              >
                {startSessionMutation.isPending ? (
                  <>
                    <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                    세션 시작 중...
                  </>
                ) : (
                  <>
                    <MessageCircle className="w-4 h-4 mr-2" />
                    세션 시작하기
                  </>
                )}
              </button>
            </div>
          </div>
        ) : (
          /* 채팅 화면 */
          <>
            {/* 메시지 영역 */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4">
              {messages.map((message) => (
                <div 
                  key={message.id}
                  className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div className={`max-w-xs lg:max-w-md ${
                    message.type === 'user' 
                      ? 'bg-blue-600 text-white' 
                      : 'bg-gray-100 text-gray-900'
                  } rounded-lg p-3`}>
                    <div className="flex items-center mb-1">
                      {message.type === 'ai' ? (
                        <Bot className="w-4 h-4 mr-2" />
                      ) : (
                        <User className="w-4 h-4 mr-2" />
                      )}
                      <span className="text-xs opacity-75">
                        {formatTime(message.timestamp)}
                      </span>
                    </div>
                    
                    <p className="text-sm">{message.content}</p>
                    
                    {message.teachingGuidance && (
                      <div className="mt-2 p-2 bg-blue-50 rounded text-blue-800 text-xs">
                        <strong>학습 가이드:</strong> {message.teachingGuidance}
                      </div>
                    )}
                    
                    {message.suggestedActions && message.suggestedActions.length > 0 && (
                      <div className="mt-2">
                        <p className="text-xs opacity-75 mb-1">추천 액션:</p>
                        {message.suggestedActions.map((action, index) => (
                          <button
                            key={index}
                            onClick={() => setInputMessage(action)}
                            className="block w-full text-left text-xs bg-white bg-opacity-20 hover:bg-opacity-30 rounded p-1 mb-1 transition-colors"
                          >
                            {action}
                          </button>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              ))}
              
              {sendMessageMutation.isPending && (
                <div className="flex justify-start">
                  <div className="bg-gray-100 rounded-lg p-3">
                    <div className="flex items-center">
                      <Bot className="w-4 h-4 mr-2" />
                      <RefreshCw className="w-4 h-4 animate-spin mr-2" />
                      <span className="text-sm text-gray-600">AI가 생각 중...</span>
                    </div>
                  </div>
                </div>
              )}
              
              <div ref={messagesEndRef} />
            </div>

            {/* 입력 영역 */}
            <div className="border-t border-gray-200 p-4">
              {sendMessageMutation.error && (
                <div className="bg-red-50 border border-red-200 rounded-lg p-2 mb-3">
                  <div className="flex items-center">
                    <AlertCircle className="w-4 h-4 text-red-600 mr-2" />
                    <span className="text-red-800 text-sm">
                      메시지 전송에 실패했습니다.
                    </span>
                  </div>
                </div>
              )}
              
              <div className="flex space-x-3">
                <textarea
                  value={inputMessage}
                  onChange={(e) => setInputMessage(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="AI 강사에게 질문하거나 학습하고 싶은 내용을 입력하세요..."
                  className="flex-1 px-3 py-2 border border-gray-300 rounded-lg resize-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  rows={2}
                />
                <button
                  onClick={handleSendMessage}
                  disabled={!inputMessage.trim() || sendMessageMutation.isPending}
                  className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed flex items-center"
                >
                  <Send className="w-4 h-4" />
                </button>
              </div>
              
              <p className="text-xs text-gray-500 mt-2">
                Enter로 전송, Shift+Enter로 줄바꿈
              </p>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
