import React, { useState, useEffect } from 'react';
import { getFeedback } from '../../services/apiClient';

function FeedbackModal({ question, userAnswer, score, isOpen, onClose, aiFeedback }) {
  const [feedback, setFeedback] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (isOpen && question) {
      if (aiFeedback) {
        // AI 피드백이 이미 있으면 사용
        setFeedback(aiFeedback.feedback);
        setLoading(false);
      } else if (score < 1) {
        // 기존 피드백 시스템 사용
        fetchFeedback();
      }
    }
  }, [isOpen, question, userAnswer, score, aiFeedback]);

  const fetchFeedback = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // 실제 피드백 요청 (시뮬레이션용 딜레이)
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      const feedbackData = await getFeedback(question.id, userAnswer);
      setFeedback(feedbackData.feedback);
    } catch (err) {
      console.error('Feedback fetch error:', err);
      setError('피드백을 불러오는데 실패했습니다.');
      // 기본 피드백 제공
      setFeedback(`문제: ${question.topic}\n답변이 정확하지 않습니다. 다시 한번 확인해보세요.`);
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  const overlayStyle = {
    position: 'fixed',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: 'rgba(0,0,0,0.5)',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    zIndex: 1000
  };

  const modalStyle = {
    backgroundColor: 'white',
    borderRadius: '12px',
    padding: '32px',
    maxWidth: '600px',
    maxHeight: '80vh',
    overflow: 'auto',
    boxShadow: '0 10px 25px rgba(0,0,0,0.2)'
  };

  const headerStyle = {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '24px',
    paddingBottom: '16px',
    borderBottom: '2px solid #e5e7eb'
  };

  const titleStyle = {
    fontSize: '20px',
    fontWeight: '600',
    color: '#374151'
  };

  const closeButtonStyle = {
    background: 'none',
    border: 'none',
    fontSize: '24px',
    cursor: 'pointer',
    color: '#6b7280'
  };

  const feedbackContentStyle = {
    backgroundColor: '#f8fafc',
    border: '1px solid #e2e8f0',
    borderRadius: '8px',
    padding: '20px',
    marginBottom: '20px',
    lineHeight: '1.6'
  };

  const buttonStyle = {
    backgroundColor: '#3b82f6',
    color: 'white',
    padding: '12px 24px',
    border: 'none',
    borderRadius: '8px',
    cursor: 'pointer',
    fontWeight: '500',
    width: '100%'
  };

  return (
    <div style={overlayStyle} onClick={onClose}>
      <div style={modalStyle} onClick={(e) => e.stopPropagation()}>
        <div style={headerStyle}>
          <h2 style={titleStyle}>AI 피드백</h2>
          <button style={closeButtonStyle} onClick={onClose}>×</button>
        </div>

        <div style={{ marginBottom: '20px' }}>
          <h3 style={{ fontSize: '16px', fontWeight: '600', marginBottom: '8px', color: '#374151' }}>
            문제: {question.topic}
          </h3>
          <div style={{ fontSize: '14px', color: '#6b7280', marginBottom: '12px' }}>
            내 답안: <code style={{ backgroundColor: '#f3f4f6', padding: '2px 6px', borderRadius: '4px' }}>
              {userAnswer || '(건너뜀)'}
            </code>
          </div>
          <div style={{ fontSize: '14px', color: '#6b7280' }}>
            정답: <code style={{ backgroundColor: '#dcfce7', padding: '2px 6px', borderRadius: '4px' }}>
              {question.answer}
            </code>
          </div>
        </div>

        {loading && (
          <div style={feedbackContentStyle}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
              <div style={{ 
                border: '2px solid #f3f4f6', 
                borderTop: '2px solid #3b82f6', 
                borderRadius: '50%', 
                width: '20px', 
                height: '20px', 
                animation: 'spin 1s linear infinite'
              }}></div>
              <span>AI가 피드백을 생성하고 있습니다...</span>
            </div>
          </div>
        )}

        {error && (
          <div style={feedbackContentStyle}>
            <p style={{ color: '#dc2626', margin: 0 }}>{error}</p>
          </div>
        )}

        {feedback && (
          <div style={feedbackContentStyle}>
            <div style={{ marginBottom: '16px' }}>
              <h4 style={{ fontSize: '14px', fontWeight: '600', marginBottom: '8px', color: '#374151' }}>
                AI 피드백
              </h4>
              <p style={{ margin: 0, color: '#374151', lineHeight: '1.6' }}>{feedback}</p>
            </div>
            
            {/* AI 피드백 추가 정보 표시 */}
            {aiFeedback && (
              <>
                {aiFeedback.score !== undefined && (
                  <div style={{ marginBottom: '12px' }}>
                    <h4 style={{ fontSize: '14px', fontWeight: '600', marginBottom: '6px', color: '#374151' }}>
                      점수
                    </h4>
                    <div style={{
                      padding: '8px 12px',
                      backgroundColor: aiFeedback.score >= 0.8 ? '#dcfce7' : aiFeedback.score >= 0.6 ? '#fef3c7' : '#fef2f2',
                      color: aiFeedback.score >= 0.8 ? '#166534' : aiFeedback.score >= 0.6 ? '#a16207' : '#dc2626',
                      borderRadius: '6px',
                      fontSize: '14px',
                      fontWeight: '600'
                    }}>
                      {(aiFeedback.score * 100).toFixed(0)}점 / 100점
                    </div>
                  </div>
                )}
                
                {aiFeedback.performance_analysis?.improvement_suggestions && (
                  <div style={{ marginBottom: '12px' }}>
                    <h4 style={{ fontSize: '14px', fontWeight: '600', marginBottom: '6px', color: '#374151' }}>
                      개선 제안
                    </h4>
                    <ul style={{ 
                      margin: 0, 
                      paddingLeft: '16px', 
                      color: '#6b7280',
                      fontSize: '14px',
                      lineHeight: '1.5'
                    }}>
                      {aiFeedback.performance_analysis.improvement_suggestions.map((suggestion, idx) => (
                        <li key={idx} style={{ marginBottom: '4px' }}>{suggestion}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </>
            )}
          </div>
        )}

        {feedback && (
          <button 
            style={buttonStyle}
            onClick={() => {
              // 이 주제로 추가 문제 풀기 기능 (향후 구현)
              alert('이 기능은 곧 구현될 예정입니다!');
            }}
          >
            이 주제로 추가 문제 풀기
          </button>
        )}

        <style>
          {`
            @keyframes spin {
              0% { transform: rotate(0deg); }
              100% { transform: rotate(360deg); }
            }
          `}
        </style>
      </div>
    </div>
  );
}

export default FeedbackModal;
