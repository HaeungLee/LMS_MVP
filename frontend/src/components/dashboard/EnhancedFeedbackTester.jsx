import React, { useState, useEffect } from 'react';
import { 
  Brain, 
  CheckCircle, 
  AlertCircle, 
  XCircle, 
  Code, 
  Search, 
  HelpCircle,
  TrendingUp,
  Target,
  Lightbulb
} from 'lucide-react';
import apiClient from '../../services/apiClient';

const EnhancedFeedbackTester = () => {
  const [answers, setAnswers] = useState({});
  const [feedback, setFeedback] = useState({});
  const [loading, setLoading] = useState({});
  const [multipleResults, setMultipleResults] = useState(null);
  const [testQuestions, setTestQuestions] = useState([]);
  const [questionsLoading, setQuestionsLoading] = useState(true);

  // 컴포넌트 마운트 시 실제 문제 데이터 로드
  useEffect(() => {
    loadRealQuestions();
  }, []);

  const loadRealQuestions = async () => {
    try {
      setQuestionsLoading(true);
      
      // 백엔드에서 실제 문제들을 가져옴 (python_basics 과목에서 5개)
      const response = await apiClient.get('/questions/python_basics?easy_count=3&medium_count=2&hard_count=0');
      
      console.log('🔍 API 응답 객체:', response);
      console.log('🔍 응답 상태:', response.status, response.statusText);
      
      // 응답 상태 체크
      if (!response.ok) {
        const errorText = await response.text();
        console.error('❌ API 에러 응답:', errorText);
        throw new Error(`HTTP ${response.status}: ${errorText}`);
      }
      
      // Response 객체에서 JSON 데이터 추출
      const questions = await response.json();
      
      console.log('🔍 백엔드에서 가져온 실제 문제들:', questions);
      
      if (!Array.isArray(questions)) {
        throw new Error('Questions is not an array');
      }
      
      // 백엔드 문제 데이터를 프론트엔드 형식으로 변환
      const formattedQuestions = questions.map(q => {
        console.log('🔍 문제 타입 확인:', q.question_type, '전체 문제:', q);
        return {
          id: q.id,
          type: q.question_type || 'short_answer', // 기본값
          title: `${getTypeDisplayName(q.question_type)}: ${q.topic || '문제'}`,
          question: q.code_snippet || '', // code_snippet을 question으로 사용
          choices: q.choices || [],
          code_snippet: q.code_snippet || '',
          correct_answer: q.answer || q.correct_answer, // answer 필드 우선 사용
          topic: q.topic || '',
          difficulty: q.difficulty || 'medium',
          required_keywords: q.required_keywords || [],
          bugs: q.bugs || []
        };
      });
      
      setTestQuestions(formattedQuestions);
      console.log('✅ 변환된 문제 데이터:', formattedQuestions);
      
    } catch (error) {
      console.error('❌ 문제 데이터 로드 실패:', error);
      
      // 실패 시 기본 Mock 데이터 사용
      const fallbackQuestions = [
        {
          id: 1,
          type: 'short_answer',
          title: '단답형: 딕셔너리 메서드',
          question: 'my_dict.____("name") - 딕셔너리에서 "name" 키의 값을 안전하게 가져오는 메서드는?',
          correct_answer: 'get',
          topic: '딕셔너리',
          difficulty: 'medium',
          required_keywords: ['get']
        }
      ];
      setTestQuestions(fallbackQuestions);
    } finally {
      setQuestionsLoading(false);
    }
  };

  // 문제 유형 표시명 반환
  const getTypeDisplayName = (type) => {
    const typeNames = {
      'multiple_choice': '객관식',
      'short_answer': '단답형',
      'fill_in_the_blank': '빈칸 채우기',
      'code_completion': '코드 완성',
      'debug_code': '디버깅',
      'true_false': 'OX 문제'
    };
    return typeNames[type] || '문제';
  };

  // 문제 유형별 아이콘 및 색상
  const typeConfig = {
    multiple_choice: { icon: CheckCircle, color: '#3b82f6', name: '객관식' },
    short_answer: { icon: HelpCircle, color: '#10b981', name: '단답형' },
    fill_in_the_blank: { icon: HelpCircle, color: '#10b981', name: '빈칸 채우기' },
    code_completion: { icon: Code, color: '#8b5cf6', name: '코드 완성' },
    debug_code: { icon: Search, color: '#ef4444', name: '디버깅' },
    true_false: { icon: XCircle, color: '#f59e0b', name: 'OX 퀴즈' }
  };

  // 개별 답안 제출
  const submitAnswer = async (questionId) => {
    const question = testQuestions.find(q => q.id === questionId);
    const answer = answers[questionId];

    if (!answer?.trim()) {
      alert('답안을 입력해주세요');
      return;
    }

    setLoading({ ...loading, [questionId]: true });

    try {
      const response = await apiClient.submitAnswerForFeedback(
        questionId,
        question.type,
        answer,
        null // user_score는 null로 설정 (자동 채점)
      );

      console.log(`🔍 API 응답 전체:`, response);
      console.log(`🔍 API 응답 데이터:`, response);
      console.log(`🔍 API 응답 상태: 성공`);
      
      setFeedback({ ...feedback, [questionId]: response });
      console.log(`✅ 문제 ${questionId} 피드백:`, response);
    } catch (err) {
      console.error(`❌ 문제 ${questionId} 피드백 실패:`, err);
      alert('피드백 생성에 실패했습니다: ' + (err.response?.data?.detail || err.message));
    } finally {
      setLoading({ ...loading, [questionId]: false });
    }
  };

  // 전체 답안 일괄 제출
  const submitAllAnswers = async () => {
    const submissions = testQuestions
      .filter(q => answers[q.id]?.trim())
      .map(q => ({
        question_id: q.id,
        answer: answers[q.id],
        question_type: q.type,
        question_data: {
          correct_answer: q.correct_answer,
          topic: q.topic,
          difficulty: q.difficulty,
          code_snippet: q.code_snippet,
          choices: q.choices,
          required_keywords: q.required_keywords,
          bugs: q.bugs
        }
      }));

    if (submissions.length === 0) {
      alert('최소 하나 이상의 답안을 입력해주세요');
      return;
    }

    setLoading({ all: true });

    try {
      const response = await apiClient.post('/ai-learning/submit-multiple-answers', {
        submissions: submissions
      });

      setMultipleResults(response.data);
      console.log('✅ 전체 피드백 결과:', response.data);
    } catch (err) {
      console.error('❌ 전체 피드백 실패:', err);
      alert('전체 피드백 생성에 실패했습니다: ' + (err.response?.data?.detail || err.message));
    } finally {
      setLoading({ all: false });
    }
  };

  // 개별 문제 렌더링
  const renderQuestion = (question) => {
    const config = typeConfig[question.type] || typeConfig['short_answer']; // 기본값 설정
    const TypeIcon = config.icon;
    const questionFeedback = feedback[question.id];
    const isLoading = loading[question.id];

    return (
      <div key={question.id} style={{
        backgroundColor: 'white',
        borderRadius: '8px',
        boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
        padding: '24px',
        marginBottom: '24px'
      }}>
        <div style={{
          borderBottom: '1px solid #e5e7eb',
          paddingBottom: '16px',
          marginBottom: '16px'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <h3 style={{
              fontSize: '18px',
              fontWeight: 'bold',
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              margin: 0
            }}>
              <div style={{
                padding: '8px',
                borderRadius: '50%',
                backgroundColor: config.color,
                color: 'white',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center'
              }}>
                <TypeIcon size={16} />
              </div>
              {question.title}
            </h3>
            <div style={{ display: 'flex', gap: '8px' }}>
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
              <span style={{
                padding: '4px 8px',
                backgroundColor: '#e5e7eb',
                borderRadius: '4px',
                fontSize: '12px',
                fontWeight: '500'
              }}>
                {config.name}
              </span>
            </div>
          </div>
        </div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          {/* 문제 내용 */}
          <div>
            <p style={{ fontWeight: '500', marginBottom: '8px' }}>{question.question}</p>
            {question.code_snippet && (
              <pre style={{
                marginTop: '8px',
                backgroundColor: '#f3f4f6',
                padding: '12px',
                borderRadius: '6px',
                fontSize: '14px',
                overflow: 'auto'
              }}>
                <code>{question.code_snippet}</code>
              </pre>
            )}
            {question.choices && (
              <div style={{
                marginTop: '8px',
                display: 'flex',
                flexDirection: 'column',
                gap: '4px'
              }}>
                {question.choices.map((choice, idx) => (
                  <div key={idx} style={{ fontSize: '14px' }}>{choice}</div>
                ))}
              </div>
            )}
          </div>

          {/* 답안 입력 */}
          <div>
            <label style={{
              display: 'block',
              fontSize: '14px',
              fontWeight: '500',
              marginBottom: '8px'
            }}>
              답안
            </label>
            <textarea
              value={answers[question.id] || ''}
              onChange={(e) => setAnswers({ ...answers, [question.id]: e.target.value })}
              placeholder="답안을 입력하세요..."
              style={{
                width: '100%',
                minHeight: '60px',
                padding: '12px',
                border: '1px solid #d1d5db',
                borderRadius: '6px',
                fontSize: '14px',
                resize: 'vertical'
              }}
            />
          </div>

          {/* 제출 버튼 */}
          <button 
            onClick={() => submitAnswer(question.id)}
            disabled={isLoading || !answers[question.id]?.trim()}
            style={{
              width: '100%',
              padding: '12px',
              backgroundColor: (isLoading || !answers[question.id]?.trim()) ? '#9ca3af' : '#3b82f6',
              color: 'white',
              border: 'none',
              borderRadius: '6px',
              fontSize: '14px',
              fontWeight: '500',
              cursor: (isLoading || !answers[question.id]?.trim()) ? 'not-allowed' : 'pointer'
            }}
          >
            {isLoading ? '피드백 생성 중...' : 'AI 피드백 받기'}
          </button>

          {/* 피드백 결과 */}
          {questionFeedback && (
            <div style={{
              borderTop: '1px solid #e5e7eb',
              paddingTop: '16px'
            }}>
              <div style={{
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                marginBottom: '12px'
              }}>
                <Brain style={{ color: '#3b82f6' }} size={20} />
                <span style={{ fontWeight: '600' }}>AI 피드백</span>
                {questionFeedback.status && (
                  <span style={{
                    padding: '4px 8px',
                    backgroundColor: questionFeedback.status === 'success' ? '#dcfce7' : '#fef2f2',
                    color: questionFeedback.status === 'success' ? '#166534' : '#dc2626',
                    borderRadius: '4px',
                    fontSize: '12px',
                    fontWeight: '600'
                  }}>
                    {questionFeedback.status === 'success' ? '완료' : '실패'}
                  </span>
                )}
              </div>
              
              <div style={{
                backgroundColor: '#dbeafe',
                padding: '16px',
                borderRadius: '8px',
                marginBottom: '12px'
              }}>
                <p style={{
                  color: '#1f2937',
                  lineHeight: '1.6',
                  margin: 0
                }}>
                  {questionFeedback.feedback || 'AI 피드백을 불러오는 중...'}
                </p>
              </div>

              {questionFeedback.performance_analysis && (
                <div style={{
                  fontSize: '14px',
                  color: '#6b7280'
                }}>
                  <div style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '4px',
                    marginBottom: '8px'
                  }}>
                    <Target size={14} />
                    <span style={{ fontWeight: '500' }}>개선 제안:</span>
                  </div>
                  <ul style={{
                    listStyle: 'disc',
                    listStylePosition: 'inside',
                    display: 'flex',
                    flexDirection: 'column',
                    gap: '4px',
                    margin: 0,
                    paddingLeft: '0'
                  }}>
                    {questionFeedback.performance_analysis.improvement_suggestions.map((suggestion, idx) => (
                      <li key={idx}>{suggestion}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    );
  };

  return (
    <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '24px' }}>
      {/* 문제 로딩 상태 */}
      {questionsLoading ? (
        <div style={{ 
          backgroundColor: 'white', 
          borderRadius: '8px', 
          boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
          padding: '48px',
          textAlign: 'center'
        }}>
          <Brain style={{ color: '#3b82f6', marginBottom: '16px' }} size={48} />
          <h2 style={{ fontSize: '24px', fontWeight: 'bold', marginBottom: '8px' }}>
            실제 문제 데이터 로딩 중...
          </h2>
          <p style={{ color: '#6b7280', margin: 0 }}>
            백엔드에서 최신 문제들을 가져오고 있습니다.
          </p>
        </div>
      ) : (
        <>
      <div style={{ 
        backgroundColor: 'white', 
        borderRadius: '8px', 
        boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
        padding: '24px',
        marginBottom: '24px'
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
            <Brain style={{ color: '#3b82f6' }} />
            AI 피드백 시스템 테스트
          </h2>
        </div>
        <div style={{ textAlign: 'center' }}>
          <button 
            onClick={submitAllAnswers}
            disabled={loading.all}
            style={{
              padding: '12px 32px',
              backgroundColor: loading.all ? '#9ca3af' : '#3b82f6',
              color: 'white',
              border: 'none',
              borderRadius: '8px',
              fontSize: '18px',
              fontWeight: '600',
              cursor: loading.all ? 'not-allowed' : 'pointer',
              marginBottom: '16px'
            }}
          >
            {loading.all ? '전체 분석 중...' : '전체 답안 일괄 분석'}
          </button>
          <p style={{ fontSize: '14px', color: '#6b7280', margin: 0 }}>
            각 문제별로 개별 피드백을 받거나, 전체 답안을 한 번에 분석할 수 있습니다.
          </p>
        </div>
      </div>

      {/* 개별 문제들 */}
      {testQuestions.map(renderQuestion)}

      {/* 전체 분석 결과 */}
      {multipleResults && (
        <div style={{ 
          backgroundColor: 'white', 
          borderRadius: '8px', 
          boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
          padding: '24px',
          marginTop: '24px'
        }}>
          <div style={{ 
            borderBottom: '2px solid #e5e7eb', 
            paddingBottom: '16px', 
            marginBottom: '24px' 
          }}>
            <h2 style={{ 
              fontSize: '20px', 
              fontWeight: 'bold', 
              display: 'flex', 
              alignItems: 'center', 
              gap: '8px',
              margin: 0
            }}>
              <TrendingUp style={{ color: '#10b981' }} />
              전체 성과 분석
            </h2>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
            {/* 전체 요약 */}
            <div style={{ 
              background: 'linear-gradient(to right, #dbeafe, #d1fae5)', 
              padding: '16px', 
              borderRadius: '8px' 
            }}>
              <div style={{ 
                display: 'grid', 
                gridTemplateColumns: 'repeat(3, 1fr)', 
                gap: '16px', 
                textAlign: 'center' 
              }}>
                <div>
                  <div style={{ fontSize: '32px', fontWeight: 'bold', color: '#2563eb' }}>
                    {multipleResults.overall_analysis.total_questions}
                  </div>
                  <div style={{ fontSize: '14px', color: '#6b7280' }}>총 문제 수</div>
                </div>
                <div>
                  <div style={{ fontSize: '32px', fontWeight: 'bold', color: '#10b981' }}>
                    {(multipleResults.overall_analysis.average_score * 100).toFixed(0)}%
                  </div>
                  <div style={{ fontSize: '14px', color: '#6b7280' }}>평균 점수</div>
                </div>
                <div>
                  <div style={{ fontSize: '32px', fontWeight: 'bold', color: '#7c3aed' }}>
                    {multipleResults.summary.percentage.toFixed(0)}%
                  </div>
                  <div style={{ fontSize: '14px', color: '#6b7280' }}>전체 정답률</div>
                </div>
              </div>
            </div>

            {/* 문제 유형별 성과 */}
            <div>
              <h4 style={{ 
                fontWeight: '600', 
                marginBottom: '12px', 
                display: 'flex', 
                alignItems: 'center', 
                gap: '8px' 
              }}>
                <Target size={16} />
                문제 유형별 성과
              </h4>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                {Object.entries(multipleResults.overall_analysis.scores_by_type).map(([type, data]) => {
                  const config = typeConfig[type] || typeConfig['short_answer']; // 기본값 설정
                  const percentage = data.average * 100;
                  return (
                    <div key={type} style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                      <div style={{ 
                        padding: '8px', 
                        borderRadius: '6px', 
                        backgroundColor: config.color,
                        color: 'white',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center'
                      }}>
                        <config.icon size={14} />
                      </div>
                      <div style={{ flex: 1 }}>
                        <div style={{ 
                          display: 'flex', 
                          justifyContent: 'space-between', 
                          alignItems: 'center', 
                          marginBottom: '4px' 
                        }}>
                          <span style={{ fontWeight: '500' }}>{config.name}</span>
                          <span style={{ fontSize: '14px', fontFamily: 'monospace' }}>
                            {percentage.toFixed(0)}%
                          </span>
                        </div>
                        <div style={{ 
                          height: '8px', 
                          backgroundColor: '#e5e7eb', 
                          borderRadius: '4px',
                          overflow: 'hidden'
                        }}>
                          <div style={{
                            height: '100%',
                            backgroundColor: '#3b82f6',
                            width: `${percentage}%`,
                            transition: 'width 0.3s ease'
                          }} />
                        </div>
                      </div>
                      <span style={{ 
                        padding: '2px 8px',
                        backgroundColor: '#f3f4f6',
                        border: '1px solid #d1d5db',
                        borderRadius: '4px',
                        fontSize: '12px',
                        fontWeight: '500'
                      }}>
                        {data.count}문제
                      </span>
                    </div>
                  );
                })}
              </div>
            </div>

            {/* 강점과 약점 */}
            <div style={{ 
              display: 'grid', 
              gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', 
              gap: '16px' 
            }}>
              <div>
                <h4 style={{ 
                  fontWeight: '600', 
                  marginBottom: '12px', 
                  display: 'flex', 
                  alignItems: 'center', 
                  gap: '8px',
                  color: '#059669'
                }}>
                  <CheckCircle size={16} />
                  강점
                </h4>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                  {multipleResults.overall_analysis.strengths.map((strength, idx) => (
                    <div key={idx} style={{ 
                      backgroundColor: '#ecfdf5', 
                      padding: '8px', 
                      borderRadius: '6px',
                      fontSize: '14px'
                    }}>
                      {strength}
                    </div>
                  ))}
                </div>
              </div>

              <div>
                <h4 style={{ 
                  fontWeight: '600', 
                  marginBottom: '12px', 
                  display: 'flex', 
                  alignItems: 'center', 
                  gap: '8px',
                  color: '#dc2626'
                }}>
                  <AlertCircle size={16} />
                  개선 영역
                </h4>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                  {multipleResults.overall_analysis.weaknesses.map((weakness, idx) => (
                    <div key={idx} style={{ 
                      backgroundColor: '#fef2f2', 
                      padding: '8px', 
                      borderRadius: '6px',
                      fontSize: '14px'
                    }}>
                      {weakness}
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* 학습 추천사항 */}
            <div>
              <h4 style={{ 
                fontWeight: '600', 
                marginBottom: '12px', 
                display: 'flex', 
                alignItems: 'center', 
                gap: '8px',
                color: '#2563eb'
              }}>
                <Lightbulb size={16} />
                학습 추천사항
              </h4>
              <div style={{ 
                backgroundColor: '#dbeafe', 
                padding: '16px', 
                borderRadius: '8px' 
              }}>
                <ul style={{ margin: 0, padding: 0, listStyle: 'none', display: 'flex', flexDirection: 'column', gap: '8px' }}>
                  {multipleResults.overall_analysis.study_recommendations.map((recommendation, idx) => (
                    <li key={idx} style={{ display: 'flex', alignItems: 'flex-start', gap: '8px' }}>
                      <span style={{ color: '#2563eb', marginTop: '4px', fontWeight: 'bold' }}>•</span>
                      <span style={{ color: '#374151', lineHeight: '1.5' }}>{recommendation}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          </div>
        </div>
      )}
        </>
      )}
    </div>
  );
};

export default EnhancedFeedbackTester;
