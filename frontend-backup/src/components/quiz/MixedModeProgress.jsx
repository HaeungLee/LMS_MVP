import React from 'react';
import { 
  getSubjectName,
  getSubjectColor
} from '../../constants/subjects';const MixedModeProgress = ({ 
  subjectStats, 
  currentSubjects = [], 
  className = '' 
}) => {
  if (!subjectStats || Object.keys(subjectStats).length === 0) {
    return null;
  }

  return (
    <div className={`mixed-mode-progress ${className}`} style={{
      backgroundColor: 'white',
      borderRadius: '12px',
      padding: '16px',
      marginBottom: '20px',
      boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
      border: '1px solid #e5e7eb'
    }}>
      <div style={{
        display: 'flex',
        alignItems: 'center',
        marginBottom: '16px'
      }}>
        <div style={{
          fontSize: '16px',
          fontWeight: '600',
          color: '#374151',
          marginRight: '8px'
        }}>
          혼합 모드 진행률
        </div>
        {currentSubjects.length > 1 && (
          <div style={{
            fontSize: '12px',
            padding: '2px 8px',
            backgroundColor: '#fef3c7',
            color: '#d97706',
            borderRadius: '12px',
            fontWeight: '500'
          }}>
            통합 문제
          </div>
        )}
      </div>

      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
        gap: '12px'
      }}>
        {Object.entries(subjectStats).map(([subject, stats]) => {
          const colors = getSubjectColor(subject);
          const isActive = currentSubjects.includes(subject);
          
          return (
            <div
              key={subject}
              style={{
                padding: '12px',
                borderRadius: '8px',
                backgroundColor: isActive ? colors.background : '#f9fafb',
                border: `2px solid ${isActive ? colors.primary : '#e5e7eb'}`,
                transition: 'all 0.2s ease'
              }}
            >
              {/* 과목 헤더 */}
              <div style={{
                display: 'flex',
                alignItems: 'center',
                marginBottom: '8px'
              }}>
                <span style={{
                  fontSize: '14px',
                  fontWeight: '600',
                  color: isActive ? colors.primary : '#6b7280'
                }}>
                  {getSubjectName(subject)}
                </span>
                {isActive && (
                  <div style={{
                    width: '6px',
                    height: '6px',
                    borderRadius: '50%',
                    backgroundColor: colors.primary,
                    marginLeft: '6px'
                  }} />
                )}
              </div>

              {/* 진행률 바 */}
              <div style={{
                width: '100%',
                height: '6px',
                backgroundColor: '#e5e7eb',
                borderRadius: '3px',
                overflow: 'hidden',
                marginBottom: '6px'
              }}>
                <div
                  style={{
                    width: `${(stats.progress || 0) * 100}%`,
                    height: '100%',
                    backgroundColor: colors.primary,
                    borderRadius: '3px',
                    transition: 'width 0.3s ease'
                  }}
                />
              </div>

              {/* 통계 텍스트 */}
              <div style={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center'
              }}>
                <span style={{
                  fontSize: '12px',
                  color: '#6b7280'
                }}>
                  {stats.answered}/{stats.total} 완료
                </span>
                <span style={{
                  fontSize: '12px',
                  fontWeight: '600',
                  color: colors.primary
                }}>
                  {Math.round((stats.progress || 0) * 100)}%
                </span>
              </div>
            </div>
          );
        })}
      </div>

      {/* 전체 진행률 */}
      <div style={{
        marginTop: '16px',
        padding: '12px',
        backgroundColor: '#f8fafc',
        borderRadius: '8px',
        border: '1px solid #e2e8f0'
      }}>
        <div style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center'
        }}>
          <span style={{
            fontSize: '14px',
            fontWeight: '600',
            color: '#374151'
          }}>
            전체 진행률
          </span>
          <span style={{
            fontSize: '14px',
            fontWeight: '600',
            color: '#3b82f6'
          }}>
            {(() => {
              const totalAnswered = Object.values(subjectStats).reduce((sum, stats) => sum + stats.answered, 0);
              const totalQuestions = Object.values(subjectStats).reduce((sum, stats) => sum + stats.total, 0);
              const overallProgress = totalQuestions > 0 ? (totalAnswered / totalQuestions) * 100 : 0;
              return `${totalAnswered}/${totalQuestions} (${Math.round(overallProgress)}%)`;
            })()}
          </span>
        </div>
      </div>
    </div>
  );
};

export default MixedModeProgress;
