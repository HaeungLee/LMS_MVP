import React from 'react';
import { useNavigate } from 'react-router-dom';
import useAuthStore from '../stores/authStore';
import { getTeacherDashboardStats } from '../services/apiClient';
import ChartAdapter from '../components/common/charts/ChartAdapter';

export default function TeacherDashboard() {
  const { user } = useAuthStore();
  const navigate = useNavigate();
  const [subject, setSubject] = React.useState('python_basics');
  const [data, setData] = React.useState(null);
  const [loading, setLoading] = React.useState(true);
  const [error, setError] = React.useState('');

  React.useEffect(() => {
    if (!user || (user.role !== 'teacher' && user.role !== 'admin')) {
      navigate('/login');
    }
  }, [user]);

  React.useEffect(() => {
    (async () => {
      try {
        setLoading(true);
        const res = await getTeacherDashboardStats(subject);
        setData(res);
        setError('');
      } catch (e) {
        setError('대시보드 데이터를 불러오지 못했습니다.');
      } finally {
        setLoading(false);
      }
    })();
  }, [subject]);

  if (loading) return <div style={{ padding:24 }}>불러오는 중...</div>;
  if (error) return <div style={{ padding:24, color:'#dc2626' }}>{error}</div>;
  if (!data) return <div style={{ padding:24 }}>데이터 없음</div>;

  const topicBar = Object.entries(data.topics || {}).map(([label, value]) => ({ label, value }));
  const accBar = Object.entries(data.topic_accuracy || {}).map(([label, v]) => ({ label, value: v.percentage }));

  return (
    <div style={{ padding:24, maxWidth:1200, margin:'0 auto' }}>
      <div style={{ display:'flex', justifyContent:'space-between', alignItems:'center', marginBottom:16 }}>
        <h1 style={{ fontSize:24 }}>교사용 대시보드</h1>
        <div>
          <label style={{ marginRight:8 }}>과목</label>
          <select value={subject} onChange={(e)=>setSubject(e.target.value)} style={{ padding:'6px 10px', border:'1px solid #d1d5db', borderRadius:6 }}>
            <option value="python_basics">Python 기초</option>
          </select>
        </div>
      </div>

      <div style={{ display:'grid', gridTemplateColumns:'1fr 1fr', gap:24 }}>
        <div style={{ background:'#fff', borderRadius:8, padding:16 }}>
          <h2 style={{ fontSize:18, marginBottom:12 }}>주제별 문제 수</h2>
          <ChartAdapter type="bar" data={topicBar} height={300} options={{ horizontal:true, tickMaxChars:10, barWidth:14 }} />
        </div>
        <div style={{ background:'#fff', borderRadius:8, padding:16 }}>
          <h2 style={{ fontSize:18, marginBottom:12 }}>주제별 정답률(%)</h2>
          <ChartAdapter type="bar" data={accBar} height={300} options={{ horizontal:true, tickMaxChars:10, barWidth:14 }} />
        </div>
      </div>

      <div style={{ background:'#fff', borderRadius:8, padding:16, marginTop:24 }}>
        <h2 style={{ fontSize:18, marginBottom:12 }}>최근 제출</h2>
        <div style={{ overflow:'auto' }}>
          <table style={{ width:'100%', borderCollapse:'collapse' }}>
            <thead>
              <tr style={{ background:'#f9fafb' }}>
                <th style={{ padding:8, textAlign:'left', borderBottom:'1px solid #e5e7eb' }}>제출ID</th>
                <th style={{ padding:8, textAlign:'left', borderBottom:'1px solid #e5e7eb' }}>학생ID</th>
                <th style={{ padding:8, textAlign:'left', borderBottom:'1px solid #e5e7eb' }}>과목</th>
                <th style={{ padding:8, textAlign:'left', borderBottom:'1px solid #e5e7eb' }}>시간</th>
                <th style={{ padding:8, textAlign:'left', borderBottom:'1px solid #e5e7eb' }}>점수(%)</th>
              </tr>
            </thead>
            <tbody>
              {(data.recent_submissions || []).map((s, idx) => (
                <tr key={idx}>
                  <td style={{ padding:8, borderBottom:'1px solid #f3f4f6' }}>{s.submission_id}</td>
                  <td style={{ padding:8, borderBottom:'1px solid #f3f4f6' }}>{s.user_id}</td>
                  <td style={{ padding:8, borderBottom:'1px solid #f3f4f6' }}>{s.subject}</td>
                  <td style={{ padding:8, borderBottom:'1px solid #f3f4f6' }}>{s.submitted_at ? new Date(s.submitted_at).toLocaleString() : ''}</td>
                  <td style={{ padding:8, borderBottom:'1px solid #f3f4f6' }}>{s.score_pct}%</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}


