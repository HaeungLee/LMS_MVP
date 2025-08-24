import React, { useState } from 'react';
import { Loader2, Code, Search, CheckCircle, XCircle, HelpCircle } from 'lucide-react';
import apiClient from '../../services/apiClient';

const QuestionTypeGenerator = () => {
  const [loading, setLoading] = useState(false);
  const [selectedType, setSelectedType] = useState('');
  const [selectedTopic, setSelectedTopic] = useState('');
  const [selectedDifficulty, setSelectedDifficulty] = useState('');
  const [generatedQuestion, setGeneratedQuestion] = useState(null);
  const [mixedQuestions, setMixedQuestions] = useState([]);
  const [error, setError] = useState('');

  // 문제 유형 정의
  const questionTypes = [
    { value: 'multiple_choice', label: '객관식', icon: CheckCircle, color: '#3b82f6' },
    { value: 'short_answer', label: '단답형', icon: HelpCircle, color: '#10b981' },
    { value: 'code_completion', label: '코드 완성', icon: Code, color: '#8b5cf6' },
    { value: 'debug_code', label: '디버깅', icon: Search, color: '#ef4444' },
    { value: 'true_false', label: 'OX 퀴즈', icon: XCircle, color: '#f59e0b' }
  ];

  const topics = [
    { value: 'python_basics', label: '파이썬 기초' },
    { value: 'variables', label: '변수와 자료형' },
    { value: 'strings', label: '문자열' },
    { value: 'lists', label: '리스트' },
    { value: 'dictionaries', label: '딕셔너리' },
    { value: 'conditions', label: '조건문' },
    { value: 'loops', label: '반복문' },
    { value: 'functions', label: '함수' }
  ];

  const difficulties = [
    { value: 'easy', label: '쉬움', color: '#10b981' },
    { value: 'medium', label: '보통', color: '#f59e0b' },
    { value: 'hard', label: '어려움', color: '#ef4444' }
  ];

  // 단일 문제 생성
  const generateSingleQuestion = async () => {
    if (!selectedType || !selectedTopic || !selectedDifficulty) {
      setError('모든 옵션을 선택해주세요');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const response = await apiClient.post('/ai-learning/generate-single-question', {
        question_type: selectedType,
        topic: selectedTopic,
        difficulty: selectedDifficulty
      });

      setGeneratedQuestion(response.question);
      console.log('✅ 단일 문제 생성 성공:', response);
    } catch (err) {
      setError('문제 생성에 실패했습니다: ' + (err.response?.data?.detail || err.message));
      console.error('❌ 단일 문제 생성 실패:', err);
    } finally {
      setLoading(false);
    }
  };

  // 혼합 문제셋 생성
  const generateMixedQuestions = async () => {
    if (!selectedTopic || !selectedDifficulty) {
      setError('주제와 난이도를 선택해주세요');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const response = await apiClient.post('/ai-learning/generate-mixed-questions', {
        topic: selectedTopic,
        difficulty: selectedDifficulty,
        count: 4 // 4가지 다른 유형
      });

      setMixedQuestions(response.questions);
      console.log('✅ 혼합 문제셋 생성 성공:', response);
    } catch (err) {
      setError('혼합 문제셋 생성에 실패했습니다: ' + (err.response?.data?.detail || err.message));
      console.error('❌ 혼합 문제셋 생성 실패:', err);
    } finally {
      setLoading(false);
    }
  };

  // 문제 유형별 렌더링
  const renderQuestion = (question, index = null) => {
    const typeInfo = questionTypes.find(t => t.value === question.question_type);
    const TypeIcon = typeInfo?.icon || HelpCircle;

    return (
      <div key={index || 0} style={{ 
        backgroundColor: 'white',
        border: '1px solid #e5e7eb',
        borderRadius: '8px',
        padding: '20px',
        marginTop: '16px'
      }}>
        <div style={{ 
          display: 'flex', 
          alignItems: 'center', 
          justifyContent: 'space-between',
          borderBottom: '1px solid #f3f4f6',
          paddingBottom: '12px',
          marginBottom: '16px'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <div style={{ 
              padding: '8px', 
              borderRadius: '50%', 
              backgroundColor: typeInfo?.color || '#6b7280',
              color: 'white',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center'
            }}>
              <TypeIcon size={16} />
            </div>
            <span style={{ fontWeight: '600', fontSize: '16px' }}>
              {typeInfo?.label || question.question_type}
            </span>
          </div>
          <span style={{ 
            padding: '4px 8px',
            backgroundColor: '#f3f4f6',
            border: '1px solid #d1d5db',
            borderRadius: '4px',
            fontSize: '12px',
            fontWeight: '500'
          }}>
            {question.difficulty}
          </span>
        </div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          <div>
            <h4 style={{ fontWeight: '600', marginBottom: '8px', fontSize: '14px' }}>문제</h4>
            <p style={{ color: '#374151', lineHeight: '1.5' }}>{question.question}</p>
          </div>

          {question.code_snippet && (
            <div>
              <h4 style={{ fontWeight: '600', marginBottom: '8px', fontSize: '14px' }}>코드</h4>
              <pre style={{ 
                backgroundColor: '#f3f4f6', 
                padding: '12px', 
                borderRadius: '6px', 
                fontSize: '14px', 
                overflowX: 'auto',
                margin: 0,
                fontFamily: 'monospace'
              }}>
                <code>{question.code_snippet}</code>
              </pre>
            </div>
          )}

          {question.choices && question.choices.length > 0 && (
            <div>
              <h4 style={{ fontWeight: '600', marginBottom: '8px', fontSize: '14px' }}>선택지</h4>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
                {question.choices.map((choice, idx) => (
                  <div key={idx} style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <span style={{ 
                      fontFamily: 'monospace', 
                      fontSize: '12px', 
                      backgroundColor: '#e5e7eb', 
                      padding: '4px 8px', 
                      borderRadius: '4px',
                      fontWeight: '600'
                    }}>
                      {String.fromCharCode(65 + idx)}
                    </span>
                    <span style={{ fontSize: '14px' }}>{choice}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          <div>
            <h4 style={{ fontWeight: '600', marginBottom: '8px', fontSize: '14px' }}>정답</h4>
            <p style={{ 
              color: '#059669', 
              fontFamily: 'monospace',
              fontSize: '14px',
              fontWeight: '500'
            }}>{question.correct_answer}</p>
          </div>

          {question.explanation && (
            <div>
              <h4 style={{ fontWeight: '600', marginBottom: '8px', fontSize: '14px' }}>해설</h4>
              <p style={{ color: '#6b7280', fontSize: '14px', lineHeight: '1.5' }}>{question.explanation}</p>
            </div>
          )}

          <div style={{ display: 'flex', gap: '8px', fontSize: '12px', color: '#6b7280' }}>
            <span style={{ 
              padding: '2px 6px',
              backgroundColor: '#f3f4f6',
              borderRadius: '4px'
            }}>
              AI 생성: {question.ai_generated ? '✅' : '❌'}
            </span>
            <span style={{ 
              padding: '2px 6px',
              backgroundColor: '#f3f4f6',
              borderRadius: '4px'
            }}>
              생성 시간: {new Date(question.created_at).toLocaleTimeString()}
            </span>
          </div>
        </div>
      </div>
    );
  };

  return (
    <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '24px' }}>
      <div style={{ 
        backgroundColor: 'white', 
        borderRadius: '8px', 
        boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
        padding: '24px'
      }}>
        <div style={{ 
          borderBottom: '2px solid #e5e7eb', 
          paddingBottom: '16px', 
          marginBottom: '24px' 
        }}>
          <h2 style={{ 
            fontSize: '24px', 
            fontWeight: 'bold', 
            display: 'flex', 
            alignItems: 'center', 
            gap: '8px',
            margin: 0
          }}>
            <Code style={{ color: '#3b82f6' }} />
            5가지 문제 유형 AI 생성기
          </h2>
        </div>
        <div style={{ marginBottom: '24px' }}>
          <div style={{ 
            display: 'grid', 
            gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', 
            gap: '16px',
            marginBottom: '24px'
          }}>
            <div>
              <label style={{ 
                display: 'block', 
                fontSize: '14px', 
                fontWeight: '500', 
                marginBottom: '8px' 
              }}>문제 유형</label>
              <select 
                value={selectedType} 
                onChange={(e) => setSelectedType(e.target.value)}
                style={{
                  width: '100%',
                  padding: '8px 12px',
                  border: '1px solid #d1d5db',
                  borderRadius: '6px',
                  fontSize: '14px'
                }}
              >
                <option value="">문제 유형 선택</option>
                {questionTypes.map((type) => (
                  <option key={type.value} value={type.value}>
                    {type.label}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label style={{ 
                display: 'block', 
                fontSize: '14px', 
                fontWeight: '500', 
                marginBottom: '8px' 
              }}>주제</label>
              <select 
                value={selectedTopic} 
                onChange={(e) => setSelectedTopic(e.target.value)}
                style={{
                  width: '100%',
                  padding: '8px 12px',
                  border: '1px solid #d1d5db',
                  borderRadius: '6px',
                  fontSize: '14px'
                }}
              >
                <option value="">주제 선택</option>
                {topics.map((topic) => (
                  <option key={topic.value} value={topic.value}>
                    {topic.label}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label style={{ 
                display: 'block', 
                fontSize: '14px', 
                fontWeight: '500', 
                marginBottom: '8px' 
              }}>난이도</label>
              <select 
                value={selectedDifficulty} 
                onChange={(e) => setSelectedDifficulty(e.target.value)}
                style={{
                  width: '100%',
                  padding: '8px 12px',
                  border: '1px solid #d1d5db',
                  borderRadius: '6px',
                  fontSize: '14px'
                }}
              >
                <option value="">난이도 선택</option>
                {difficulties.map((difficulty) => (
                  <option key={difficulty.value} value={difficulty.value}>
                    {difficulty.label}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {/* 에러 메시지 */}
          {error && (
            <div style={{ 
              backgroundColor: '#fef2f2', 
              border: '1px solid #fecaca', 
              color: '#dc2626',
              padding: '12px',
              borderRadius: '6px',
              marginBottom: '16px'
            }}>
              {error}
            </div>
          )}

          {/* 생성 버튼들 */}
          <div style={{ display: 'flex', gap: '16px', marginBottom: '24px' }}>
            <button 
              onClick={generateSingleQuestion} 
              disabled={loading}
              style={{
                flex: 1,
                padding: '12px 24px',
                backgroundColor: loading ? '#9ca3af' : '#3b82f6',
                color: 'white',
                border: 'none',
                borderRadius: '6px',
                fontSize: '16px',
                fontWeight: '500',
                cursor: loading ? 'not-allowed' : 'pointer',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '8px'
              }}
            >
              {loading ? (
                <>
                  <Loader2 size={16} style={{ animation: 'spin 1s linear infinite' }} />
                  생성 중...
                </>
              ) : (
                '단일 문제 생성'
              )}
            </button>

            <button 
              onClick={generateMixedQuestions} 
              disabled={loading}
              style={{
                flex: 1,
                padding: '12px 24px',
                backgroundColor: loading ? '#9ca3af' : 'white',
                color: loading ? 'white' : '#374151',
                border: '1px solid #d1d5db',
                borderRadius: '6px',
                fontSize: '16px',
                fontWeight: '500',
                cursor: loading ? 'not-allowed' : 'pointer',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '8px'
              }}
            >
              {loading ? (
                <>
                  <Loader2 size={16} style={{ animation: 'spin 1s linear infinite' }} />
                  생성 중...
                </>
              ) : (
                '혼합 문제셋 생성 (4개)'
              )}
            </button>
          </div>

          {/* 단일 문제 결과 */}
          {generatedQuestion && (
            <div style={{ marginBottom: '24px' }}>
              <h3 style={{ fontSize: '18px', fontWeight: '600', marginBottom: '16px' }}>생성된 문제</h3>
              {renderQuestion(generatedQuestion)}
            </div>
          )}

          {/* 혼합 문제셋 결과 */}
          {mixedQuestions.length > 0 && (
            <div>
              <h3 style={{ fontSize: '18px', fontWeight: '600', marginBottom: '16px' }}>혼합 문제셋 ({mixedQuestions.length}개)</h3>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                {mixedQuestions.map((question, index) => renderQuestion(question, index))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default QuestionTypeGenerator;
