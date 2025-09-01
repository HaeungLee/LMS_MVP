import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  SUBJECTS, 
  SUBJECT_ICONS, 
  SUBJECT_COLORS, 
  SUBJECT_DESCRIPTIONS,
  getSubjectName,
  getSubjectIcon
} from '../constants/subjects';

const QuizModeSelectionPage = () => {
  const navigate = useNavigate();
  const [selectedMode, setSelectedMode] = useState('single');

  const handleSubjectSelect = (subjectKey) => {
    navigate(`/quiz/${subjectKey}`);
  };

  const handleMixedModeStart = () => {
    // Python 기초 + 웹 크롤링 혼합 모드로 시작
    navigate('/quiz/mixed?subjects=python_basics,web_crawling');
  };

  return (
    <div style={{ 
      maxWidth: '1200px', 
      margin: '0 auto', 
      padding: '40px 20px',
      minHeight: '100vh'
    }}>
      {/* 헤더 */}
      <div style={{ textAlign: 'center', marginBottom: '40px' }}>
        <h1 style={{ 
          fontSize: '32px', 
          color: '#1976d2', 
          marginBottom: '16px',
          fontWeight: 'bold'
        }}>
          퀴즈 시작하기
        </h1>
        <p style={{ 
          fontSize: '18px', 
          color: '#6b7280',
          maxWidth: '600px',
          margin: '0 auto'
        }}>
          학습할 과목을 선택하거나 여러 과목을 조합해서 실무형 퀴즈를 시작하세요
        </p>
      </div>

      {/* 모드 선택 탭 */}
      <div style={{ 
        display: 'flex', 
        justifyContent: 'center', 
        marginBottom: '40px',
        borderBottom: '2px solid #e5e7eb'
      }}>
        <button
          onClick={() => setSelectedMode('single')}
          style={{
            padding: '12px 24px',
            backgroundColor: selectedMode === 'single' ? '#1976d2' : 'transparent',
            color: selectedMode === 'single' ? 'white' : '#6b7280',
            border: 'none',
            borderBottom: selectedMode === 'single' ? '3px solid #1976d2' : '3px solid transparent',
            fontSize: '16px',
            fontWeight: '600',
            cursor: 'pointer',
            transition: 'all 0.2s ease'
          }}
        >
          단일 과목
        </button>
        <button
          onClick={() => setSelectedMode('mixed')}
          style={{
            padding: '12px 24px',
            backgroundColor: selectedMode === 'mixed' ? '#1976d2' : 'transparent',
            color: selectedMode === 'mixed' ? 'white' : '#6b7280',
            border: 'none',
            borderBottom: selectedMode === 'mixed' ? '3px solid #1976d2' : '3px solid transparent',
            fontSize: '16px',
            fontWeight: '600',
            cursor: 'pointer',
            transition: 'all 0.2s ease'
          }}
        >
          혼합 모드
        </button>
      </div>

      {/* 단일 과목 모드 */}
      {selectedMode === 'single' && (
        <div>
          <h2 style={{ 
            fontSize: '24px', 
            marginBottom: '24px',
            textAlign: 'center',
            color: '#374151'
          }}>
            과목을 선택하세요
          </h2>
          <div style={{ 
            display: 'grid', 
            gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
            gap: '24px',
            marginBottom: '40px'
          }}>
            {Object.entries(SUBJECTS).map(([subjectKey, subjectName]) => {
              const colors = SUBJECT_COLORS[subjectKey];
              const icon = SUBJECT_ICONS[subjectKey];
              
              return (
                <div
                  key={subjectKey}
                  onClick={() => handleSubjectSelect(subjectKey)}
                  style={{
                    backgroundColor: 'white',
                    borderRadius: '16px',
                    padding: '32px',
                    boxShadow: '0 4px 6px rgba(0,0,0,0.1)',
                    border: '2px solid #e5e7eb',
                    cursor: 'pointer',
                    transition: 'all 0.3s ease',
                    textAlign: 'center'
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.transform = 'translateY(-4px)';
                    e.currentTarget.style.boxShadow = '0 8px 16px rgba(0,0,0,0.15)';
                    e.currentTarget.style.borderColor = colors.primary;
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.transform = 'translateY(0)';
                    e.currentTarget.style.boxShadow = '0 4px 6px rgba(0,0,0,0.1)';
                    e.currentTarget.style.borderColor = '#e5e7eb';
                  }}
                >
                  <div style={{
                    width: '80px',
                    height: '80px',
                    borderRadius: '16px',
                    backgroundColor: colors.background,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    fontSize: '40px',
                    margin: '0 auto 20px'
                  }}>
                    {icon}
                  </div>
                  <h3 style={{ 
                    fontSize: '20px', 
                    fontWeight: 'bold',
                    marginBottom: '12px',
                    color: '#374151'
                  }}>
                    {subjectName}
                  </h3>
                  <p style={{ 
                    color: '#6b7280', 
                    fontSize: '14px',
                    lineHeight: '1.5',
                    marginBottom: '20px'
                  }}>
                    {SUBJECT_DESCRIPTIONS[subjectKey]}
                  </p>
                  <div style={{
                    padding: '8px 16px',
                    backgroundColor: colors.primary,
                    color: 'white',
                    borderRadius: '20px',
                    fontSize: '14px',
                    fontWeight: '600',
                    display: 'inline-block'
                  }}>
                    퀴즈 시작하기 →
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* 혼합 모드 */}
      {selectedMode === 'mixed' && (
        <div>
          <h2 style={{ 
            fontSize: '24px', 
            marginBottom: '16px',
            textAlign: 'center',
            color: '#374151'
          }}>
            실무형 혼합 학습 (Beta)
          </h2>
          <p style={{ 
            textAlign: 'center', 
            color: '#6b7280', 
            marginBottom: '32px',
            fontSize: '16px'
          }}>
            여러 과목을 조합해서 실제 프로젝트와 같은 통합적 학습 경험을 제공합니다
          </p>

          <div style={{ 
            display: 'grid', 
            gridTemplateColumns: 'repeat(auto-fit, minmax(350px, 1fr))',
            gap: '24px'
          }}>
            {/* 인기 조합 1: 웹 크롤링 시작하기 */}
            <div
              onClick={handleMixedModeStart}
              style={{
                backgroundColor: 'white',
                borderRadius: '16px',
                padding: '24px',
                boxShadow: '0 4px 6px rgba(0,0,0,0.1)',
                border: '2px solid #e5e7eb',
                cursor: 'pointer',
                transition: 'all 0.3s ease'
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.transform = 'translateY(-4px)';
                e.currentTarget.style.boxShadow = '0 8px 16px rgba(0,0,0,0.15)';
                e.currentTarget.style.borderColor = '#3b82f6';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.transform = 'translateY(0)';
                e.currentTarget.style.boxShadow = '0 4px 6px rgba(0,0,0,0.1)';
                e.currentTarget.style.borderColor = '#e5e7eb';
              }}
            >
              <div style={{ marginBottom: '16px' }}>
                <span style={{ fontSize: '24px', marginRight: '8px' }}>🐍</span>
                <span style={{ fontSize: '20px', marginRight: '8px' }}>+</span>
                <span style={{ fontSize: '24px' }}>🕷️</span>
              </div>
              <h3 style={{ 
                fontSize: '18px', 
                fontWeight: 'bold',
                marginBottom: '8px',
                color: '#374151'
              }}>
                웹 크롤링 시작하기
              </h3>
              <p style={{ 
                color: '#6b7280', 
                fontSize: '14px',
                marginBottom: '16px',
                lineHeight: '1.5'
              }}>
                Python 기초 (30%) + 웹 크롤링 (70%)<br/>
                변수, 함수와 함께 requests, BeautifulSoup 학습
              </p>
              <div style={{
                padding: '6px 12px',
                backgroundColor: '#3b82f6',
                color: 'white',
                borderRadius: '16px',
                fontSize: '12px',
                fontWeight: '600',
                display: 'inline-block'
              }}>
                인기 조합
              </div>
            </div>

            {/* 곧 출시 예정 */}
            <div style={{
              backgroundColor: '#f9fafb',
              borderRadius: '16px',
              padding: '24px',
              border: '2px dashed #d1d5db',
              textAlign: 'center',
              opacity: 0.7
            }}>
              <div style={{ fontSize: '48px', marginBottom: '16px' }}>🚧</div>
              <h3 style={{ 
                fontSize: '18px', 
                fontWeight: 'bold',
                marginBottom: '8px',
                color: '#6b7280'
              }}>
                더 많은 조합 곧 출시
              </h3>
              <p style={{ 
                color: '#9ca3af', 
                fontSize: '14px'
              }}>
                데이터 파이프라인 구축<br/>
                풀스택 데이터 사이언티스트
              </p>
            </div>
          </div>
        </div>
      )}

      {/* 하단 정보 */}
      <div style={{ 
        textAlign: 'center', 
        marginTop: '60px',
        padding: '24px',
        backgroundColor: '#f8fafc',
        borderRadius: '12px'
      }}>
        <p style={{ color: '#6b7280', fontSize: '14px' }}>
          💡 <strong>팁:</strong> 혼합 모드는 실제 업무와 같은 통합적 사고를 기를 수 있도록 설계되었습니다.<br/>
          각 과목을 개별로 학습한 후 혼합 모드로 실력을 검증해보세요!
        </p>
      </div>
    </div>
  );
};

export default QuizModeSelectionPage;
