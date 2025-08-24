import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { getDashboardStats, getLearningStatus } from '../services/apiClient';
import useDashboardStore from '../stores/dashboardStore';
import useQuizStore from '../stores/quizStore';
import ChartAdapter from '../components/common/charts/ChartAdapter';
import AILearningDashboard from '../components/dashboard/AILearningDashboard';
import QuestionTypeGenerator from '../components/dashboard/QuestionTypeGenerator';
import EnhancedFeedbackTester from '../components/dashboard/EnhancedFeedbackTester';

const DashboardPage = () => {
  const navigate = useNavigate();
  const { 
    dashboardData, 
    loading, 
    error, 
    setDashboardData, 
    setLoading, 
    setError 
  } = useDashboardStore();
  const [subject, setSubject] = React.useState('python_basics');
  // 차트 모드 상태는 모든 렌더에서 동일 순서로 훅이 호출되도록 최상단에 선언
  const [chartMode, setChartMode] = React.useState('bar'); // 'bar' | 'donut'
  const [activeTab, setActiveTab] = React.useState('overview'); // 'overview' | 'ai-learning' | 'question-generator' | 'feedback-tester'
  
  // 퀴즈 스토어에서 최근 활동 가져오기
  const { recentActivities } = useQuizStore();

  useEffect(() => {
    let cancelled = false;
    const fetchDashboardData = async () => {
      setLoading(true);
      try {
        const [dashRes, learnRes] = await Promise.allSettled([
          getDashboardStats(subject),
          getLearningStatus(subject)
        ]);

        if (cancelled) return;

        const data = dashRes.status === 'fulfilled' ? dashRes.value : null;
        const learning = learnRes.status === 'fulfilled' ? learnRes.value : null;

        if (!data && !learning) {
          setError('대시보드 데이터를 불러오는데 실패했습니다.');
          return;
        }

        const enrichedData = {
          ...(data || {}),
          recent_activity: recentActivities.length > 0 ? recentActivities : (data?.recent_activity || []),
          learning: learning || null,
        };
        setDashboardData(enrichedData);
        setError(null);
      } catch (err) {
        if (cancelled) return;
        console.error('Dashboard data fetch error:', err);
        setError('대시보드 데이터를 불러오는데 실패했습니다.');
      } finally {
        if (!cancelled) setLoading(false);
      }
    };

    fetchDashboardData();
    return () => { cancelled = true; };
  }, [setDashboardData, setLoading, setError, recentActivities, subject]);

  if (loading) {
    return (
      <div style={{ minHeight: '100vh', backgroundColor: '#f9fafb', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <div style={{ textAlign: 'center' }}>
          <div style={{ 
            border: '3px solid #f3f4f6', 
            borderTop: '3px solid #3b82f6', 
            borderRadius: '50%', 
            width: '50px', 
            height: '50px', 
            animation: 'spin 1s linear infinite',
            margin: '0 auto'
          }}></div>
          <p style={{ marginTop: '16px', color: '#6b7280' }}>대시보드를 불러오는 중...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ minHeight: '100vh', backgroundColor: '#f9fafb', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <div style={{ textAlign: 'center' }}>
          <p style={{ color: '#dc2626', fontSize: '18px' }}>{error}</p>
          <button 
            onClick={() => window.location.reload()}
            style={{
              marginTop: '16px',
              padding: '8px 16px',
              backgroundColor: '#3b82f6',
              color: 'white',
              border: 'none',
              borderRadius: '6px',
              cursor: 'pointer'
            }}
          >
            다시 시도
          </button>
        </div>
      </div>
    );
  }

  if (!dashboardData) {
    return (
      <div style={{ minHeight: '100vh', backgroundColor: '#f9fafb', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <p>데이터가 없습니다.</p>
      </div>
    );
  }

  const { progress, topics, recent_activity, total_questions, topic_accuracy, learning } = dashboardData;
  const coveragePct = learning ? Math.round((learning.coverage.value || 0) * 100) : 0;
  const avgSessionMin = learning?.avgSessionMin ?? null;
  const recentScores = learning?.recentScores ?? [];
  const strengthBuckets = learning?.strengthBuckets ?? null;
  const weaknesses = learning?.weaknesses || [];
  const username = (progress && progress.username) ? progress.username : '학습자';

  return (
    <div style={{ backgroundColor: '#f9fafb', padding: '24px', minHeight: 'calc(100vh - 80px)' }}>
      <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
        {/* 헤더 */}
        <div style={{ marginBottom: '32px' }}>
          <h1 style={{ fontSize: '32px', fontWeight: 'bold', color: '#111827', marginBottom: '8px' }}>
            안녕하세요! {username}님
          </h1>
          <p style={{ color: '#6b7280' }}>
            파이썬 마스터까지 {coveragePct}% 진행되었습니다!
          </p>
          <div style={{ marginTop: '12px' }}>
            <label style={{ marginRight: 8, color: '#6b7280' }}>과목</label>
            <select value={subject} onChange={(e) => setSubject(e.target.value)} style={{ padding: '6px 10px', borderRadius: 6, border: '1px solid #d1d5db' }}>
              <option value="python_basics">Python 기초</option>
              {/* 향후 data_analysis, ml_dl 등 확장 */}
            </select>
          </div>
        </div>

        {/* 탭 네비게이션 */}
        <div style={{ marginBottom: '32px' }}>
          <div style={{ borderBottom: '1px solid #e5e7eb' }}>
            <nav style={{ display: 'flex', gap: '32px' }}>
              <button
                onClick={() => setActiveTab('overview')}
                style={{
                  padding: '12px 0',
                  fontSize: '16px',
                  fontWeight: '500',
                  color: activeTab === 'overview' ? '#3b82f6' : '#6b7280',
                  backgroundColor: 'transparent',
                  border: 'none',
                  borderBottom: activeTab === 'overview' ? '2px solid #3b82f6' : '2px solid transparent',
                  cursor: 'pointer',
                  transition: 'all 0.2s'
                }}
              >
                📊 학습 현황
              </button>
              <button
                onClick={() => setActiveTab('ai-learning')}
                style={{
                  padding: '12px 0',
                  fontSize: '16px',
                  fontWeight: '500',
                  color: activeTab === 'ai-learning' ? '#3b82f6' : '#6b7280',
                  backgroundColor: 'transparent',
                  border: 'none',
                  borderBottom: activeTab === 'ai-learning' ? '2px solid #3b82f6' : '2px solid transparent',
                  cursor: 'pointer',
                  transition: 'all 0.2s'
                }}
              >
                🤖 AI 맞춤학습
              </button>
              <button
                onClick={() => setActiveTab('question-generator')}
                style={{
                  padding: '12px 0',
                  fontSize: '16px',
                  fontWeight: '500',
                  color: activeTab === 'question-generator' ? '#3b82f6' : '#6b7280',
                  backgroundColor: 'transparent',
                  border: 'none',
                  borderBottom: activeTab === 'question-generator' ? '2px solid #3b82f6' : '2px solid transparent',
                  cursor: 'pointer',
                  transition: 'all 0.2s'
                }}
              >
                🔧 문제 생성기
              </button>
              <button
                onClick={() => setActiveTab('feedback-tester')}
                style={{
                  padding: '12px 0',
                  fontSize: '16px',
                  fontWeight: '500',
                  color: activeTab === 'feedback-tester' ? '#3b82f6' : '#6b7280',
                  backgroundColor: 'transparent',
                  border: 'none',
                  borderBottom: activeTab === 'feedback-tester' ? '2px solid #3b82f6' : '2px solid transparent',
                  cursor: 'pointer',
                  transition: 'all 0.2s'
                }}
              >
                🧠 AI 피드백
              </button>
            </nav>
          </div>
        </div>

        {/* 탭 콘텐츠 */}
        {activeTab === 'overview' && (
          <>
            {/* 진행률 바 */}
            <div style={{ backgroundColor: 'white', borderRadius: '8px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)', padding: '24px', marginBottom: '32px' }}>
          <h2 style={{ fontSize: '20px', fontWeight: '600', marginBottom: '16px' }}>전체 진행률</h2>
          <div style={{ width: '100%', backgroundColor: '#e5e7eb', borderRadius: '9999px', height: '16px' }}>
            <div 
              style={{ 
                backgroundColor: '#3b82f6', 
                height: '16px', 
                borderRadius: '9999px',
                width: `${coveragePct}%`,
                transition: 'width 0.5s'
              }}
            ></div>
          </div>
          <p style={{ marginTop: '8px', fontSize: '14px', color: '#6b7280' }}>
            {coveragePct}% 완료 (코어 토픽 가중치 기준)
          </p>
        </div>

        {/* 메인 액션 */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '24px', marginBottom: '32px' }}>
          {/* 오늘의 학습 */}
          <div style={{ backgroundColor: 'white', borderRadius: '8px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)', padding: '24px' }}>
            <h2 style={{ fontSize: '20px', fontWeight: '600', marginBottom: '16px' }}>오늘의 학습</h2>
            <div style={{ backgroundColor: '#eff6ff', border: '1px solid #bfdbfe', borderRadius: '8px', padding: '16px', marginBottom: '16px' }}>
              <h3 style={{ fontWeight: '500', color: '#1e3a8a' }}>{progress?.today_goal || 'Python 기초'}</h3>
              <p style={{ color: '#1d4ed8', fontSize: '14px' }}>총 {total_questions}개의 문제가 준비되어 있습니다</p>
            </div>
            <button
              onClick={() => navigate('/quiz')}
              style={{
                width: '100%',
                backgroundColor: '#3b82f6',
                color: 'white',
                padding: '12px 16px',
                borderRadius: '8px',
                border: 'none',
                cursor: 'pointer',
                fontWeight: '500',
                fontSize: '16px'
              }}
            >
              정기 퀴즈 시작하기
            </button>
          </div>

          {/* 나의 약점 */}
          <div style={{ backgroundColor: 'white', borderRadius: '8px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)', padding: '24px' }}>
            <h2 style={{ fontSize: '20px', fontWeight: '600', marginBottom: '16px' }}>나의 약점 📊</h2>
            <div style={{ marginBottom: '16px' }}>
              {weaknesses.length === 0 && (
                <div style={{ color: '#6b7280', fontSize: '14px' }}>충분한 데이터가 없어 약점이 없습니다.</div>
              )}
              {weaknesses.map((w, index) => (
                <div key={index} style={{ backgroundColor: '#fef2f2', border: '1px solid #fecaca', borderRadius: '4px', padding: '8px', marginBottom: '8px', display:'flex', justifyContent:'space-between' }}>
                  <span style={{ color: '#b91c1c', fontSize: '14px' }}>{w.title}</span>
                  <span style={{ color: '#b91c1c', fontSize: '14px' }}>{Math.round(w.accuracy*100)}%</span>
                </div>
              ))}
            </div>
            <button
              onClick={() => navigate('/quiz')}
              style={{
                width: '100%',
                backgroundColor: '#f97316',
                color: 'white',
                padding: '8px 16px',
                borderRadius: '6px',
                border: 'none',
                cursor: 'pointer'
              }}
            >
              약점 보완 퀴즈
            </button>
          </div>
        </div>

        {/* 개인화 KPI + 최근 성과(또는 도넛) */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '24px', marginBottom: '32px' }}>
          {/* KPI 카드 */}
          <div style={{ backgroundColor: 'white', borderRadius: '8px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)', padding: '24px', minHeight: 220 }}>
            <h2 style={{ fontSize: '20px', fontWeight: '600', marginBottom: '16px' }}>나의 학습 지표</h2>
            <div style={{ display:'flex', alignItems:'center', gap:16 }}>
              {/* 간단 링 게이지 */}
              <div style={{ position:'relative', width:120, height:120 }}>
                <svg width="120" height="120">
                  <circle cx="60" cy="60" r="54" stroke="#e5e7eb" strokeWidth="12" fill="none" />
                  <circle cx="60" cy="60" r="54" stroke="#3b82f6" strokeWidth="12" fill="none" strokeDasharray={`${Math.max(0, Math.min(100, coveragePct)) * 3.39} ${339 - Math.max(0, Math.min(100, coveragePct)) * 3.39}`} strokeLinecap="round" transform="rotate(-90 60 60)" />
                </svg>
                <div style={{ position:'absolute', inset:0, display:'flex', alignItems:'center', justifyContent:'center', fontWeight:600 }}>{coveragePct}%</div>
              </div>
              {/* KPI 배지 */}
              <div style={{ display:'grid', gridTemplateColumns:'1fr 1fr', gap:8, flex:1 }}>
                <div style={{ background:'#f3f4f6', borderRadius:6, padding:'8px 10px' }}>
                  <div style={{ fontSize:12, color:'#6b7280' }}>연속 출석</div>
                  <div style={{ fontSize:18, fontWeight:600 }}>{learning?.streak ?? 0}일</div>
                </div>
                <div style={{ background:'#f3f4f6', borderRadius:6, padding:'8px 10px' }}>
                  <div style={{ fontSize:12, color:'#6b7280' }}>최근 7일 시도</div>
                  <div style={{ fontSize:18, fontWeight:600 }}>{learning?.recent7dAttempts ?? 0}회</div>
                </div>
                <div style={{ background:'#f3f4f6', borderRadius:6, padding:'8px 10px' }}>
                  <div style={{ fontSize:12, color:'#6b7280' }}>평균 학습시간</div>
                  <div style={{ fontSize:18, fontWeight:600 }}>{avgSessionMin !== null ? `${avgSessionMin}분` : '-'} </div>
                </div>
              </div>
            </div>
          </div>

          {/* 성과 카드 */}
          <div style={{ backgroundColor: 'white', borderRadius: '8px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)', padding: '24px', minHeight: 220 }}>
            <div style={{ display:'flex', justifyContent:'space-between', alignItems:'center', marginBottom: '8px' }}>
              <h2 style={{ fontSize: '20px', fontWeight: '600' }}>최근 성과</h2>
              <div style={{ display:'flex', gap:8 }}>
                <button onClick={()=>setChartMode('bar')} style={{ padding:'6px 10px', borderRadius:6, border:'1px solid #d1d5db', background: chartMode==='bar' ? '#e5e7eb' : '#fff' }}>막대</button>
                <button onClick={()=>setChartMode('donut')} style={{ padding:'6px 10px', borderRadius:6, border:'1px solid #d1d5db', background: chartMode==='donut' ? '#e5e7eb' : '#fff' }}>도넛</button>
              </div>
            </div>
            {chartMode === 'bar' ? (
              <ChartAdapter
                type="bar"
                data={(recentScores || []).map(s => ({ label: (s.date ? new Date(s.date).toLocaleDateString('ko-KR') : '-'), value: s.score_pct }))}
                height={220}
                options={{ horizontal: true, tickMaxChars: 6, barWidth: 14 }}
              />
            ) : (
              <ChartAdapter
                type="donut"
                data={strengthBuckets || {}}
                height={220}
                options={{}}
              />
            )}
          </div>
        </div>

        {/* 최근 활동 */}
        <div style={{ backgroundColor: 'white', borderRadius: '8px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)', padding: '24px' }}>
          <h2 style={{ fontSize: '20px', fontWeight: '600', marginBottom: '16px' }}>최근 활동</h2>
          <div>
            {recent_activity.map((activity, index) => (
              <div key={index} onClick={() => activity.submission_id && navigate(`/results/${activity.submission_id}`)} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '12px', backgroundColor: '#f9fafb', borderRadius: '6px', marginBottom: '12px', cursor: activity.submission_id ? 'pointer' : 'default' }}>
                <div>
                  <p style={{ fontWeight: '500', margin: '0' }}>{activity.activity}</p>
                  <p style={{ fontSize: '14px', color: '#6b7280', margin: '0' }}>{activity.date}</p>
                </div>
                <div style={{ textAlign: 'right' }}>
                  <span style={{ fontSize: '18px', fontWeight: 'bold', color: '#059669' }}>{activity.score}점</span>
                </div>
              </div>
            ))}
          </div>
        </div>
          </>
        )}

        {activeTab === 'ai-learning' && (
          <AILearningDashboard />
        )}

        {activeTab === 'question-generator' && (
          <QuestionTypeGenerator />
        )}

        {activeTab === 'feedback-tester' && (
          <EnhancedFeedbackTester />
        )}
      </div>
      
      <style>
        {`
          @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
          }
        `}
      </style>
    </div>
  );
};

export default DashboardPage;
