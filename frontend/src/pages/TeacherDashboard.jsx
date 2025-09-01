import React from 'react';
import { useNavigate } from 'react-router-dom';
import useAuthStore from '../stores/authStore';
import { getTeacherDashboardStats } from '../services/apiClient';
import { listTeacherGroups, createTeacherGroup, addGroupMember } from '../services/teacherClient';
import { fetchTaxonomyTopics } from '../services/taxonomyClient';
import ChartAdapter from '../components/common/charts/ChartAdapter';
import { SUBJECTS, getSubjectName, getSubjectIcon } from '../constants/subjects';

export default function TeacherDashboard() {
  const { user } = useAuthStore();
  const navigate = useNavigate();
  const [subject, setSubject] = React.useState('python_basics');
  const [data, setData] = React.useState(null);
  const [loading, setLoading] = React.useState(true);
  const [error, setError] = React.useState('');
  const [topics, setTopics] = React.useState([]);
  const [selectedTopic, setSelectedTopic] = React.useState('');
  const [groups, setGroups] = React.useState([]);
  const [groupId, setGroupId] = React.useState('');
  const [newGroupName, setNewGroupName] = React.useState('');
  const [addUserId, setAddUserId] = React.useState('');

  React.useEffect(() => {
    if (!user || (user.role !== 'teacher' && user.role !== 'admin')) {
      navigate('/login');
    }
  }, [user]);

  React.useEffect(() => {
    (async () => {
      try {
        setLoading(true);
        const res = await getTeacherDashboardStats(subject, groupId || undefined);
        setData(res);
        setError('');
      } catch (e) {
        setError('대시보드 데이터를 불러오지 못했습니다.');
      } finally {
        setLoading(false);
      }
    })();
  }, [subject, groupId]);

  // 그룹 목록 로드
  React.useEffect(() => {
    (async () => {
      try {
        const res = await listTeacherGroups();
        setGroups(res.items || []);
      } catch {}
    })();
  }, []);

  // 토픽 목록 로드
  React.useEffect(() => {
    (async () => {
      try {
        const res = await fetchTaxonomyTopics(subject);
        setTopics(res.items || []);
        setSelectedTopic('');
      } catch {}
    })();
  }, [subject]);

  if (loading) return <div style={{ padding:24 }}>불러오는 중...</div>;
  if (error) return <div style={{ padding:24, color:'#dc2626' }}>{error}</div>;
  if (!data) return <div style={{ padding:24 }}>데이터 없음</div>;

  const allTopicBar = Object.entries(data.topics || {}).map(([label, value]) => ({ label, value }));
  const allAccBar = Object.entries(data.topic_accuracy || {}).map(([label, v]) => ({ label, value: v.percentage }));
  const topicBar = selectedTopic ? allTopicBar.filter(d => d.label === selectedTopic) : allTopicBar;
  const accBar = selectedTopic ? allAccBar.filter(d => d.label === selectedTopic) : allAccBar;

  return (
    <div style={{ padding:24, maxWidth:1200, margin:'0 auto' }}>
      <div style={{ display:'flex', justifyContent:'space-between', alignItems:'center', marginBottom:16 }}>
        <h1 style={{ fontSize:24 }}>교사용 대시보드</h1>
        <div>
          <label style={{ marginRight:8 }}>과목</label>
          <select value={subject} onChange={(e)=>setSubject(e.target.value)} style={{ padding:'6px 10px', border:'1px solid #d1d5db', borderRadius:6 }}>
            {Object.entries(SUBJECTS).map(([key, name]) => (
              <option key={key} value={key}>
                {getSubjectIcon(key)} {name}
              </option>
            ))}
          </select>
          <label style={{ margin: '0 8px 0 16px' }}>그룹</label>
          <select value={groupId} onChange={(e)=>setGroupId(e.target.value)} style={{ padding:'6px 10px', border:'1px solid #d1d5db', borderRadius:6 }}>
            <option value="">전체</option>
            {groups.map(g => (
              <option key={g.id} value={g.id}>{g.name}</option>
            ))}
          </select>
          <button onClick={async ()=>{ if(!newGroupName.trim()) return; const res = await createTeacherGroup(newGroupName.trim()); setGroups(g=>[{ id: res.id, name: res.name }, ...g]); setNewGroupName(''); }} style={{ marginLeft:8, padding:'6px 10px', border:'1px solid #d1d5db', borderRadius:6, background:'#fff' }}>그룹 추가</button>
          <input value={newGroupName} onChange={(e)=>setNewGroupName(e.target.value)} placeholder="새 그룹명" style={{ marginLeft:8, padding:'6px 10px', border:'1px solid #d1d5db', borderRadius:6 }} />
          <input value={addUserId} onChange={(e)=>setAddUserId(e.target.value)} placeholder="학생ID 추가" style={{ marginLeft:8, padding:'6px 10px', border:'1px solid #d1d5db', borderRadius:6, width:120 }} />
          <button onClick={async ()=>{ if(!groupId || !addUserId) return; await addGroupMember(Number(groupId), Number(addUserId)); alert('추가 완료'); setAddUserId(''); }} style={{ marginLeft:8, padding:'6px 10px', border:'1px solid #d1d5db', borderRadius:6, background:'#fff' }}>멤버 추가</button>
          <label style={{ margin: '0 8px 0 16px' }}>토픽</label>
          <select value={selectedTopic} onChange={(e)=>setSelectedTopic(e.target.value)} style={{ padding:'6px 10px', border:'1px solid #d1d5db', borderRadius:6 }}>
            <option value="">전체</option>
            {topics.map(t => (
              <option key={t.topic_key} value={t.topic_key}>{t.topic_key}{t.is_core ? '' : ' (ext)'}</option>
            ))}
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


