import React from 'react';
import { useNavigate } from 'react-router-dom';
import useAuthStore from '../stores/authStore';
import { adminListQuestions, adminCreateQuestion, adminUpdateQuestion, adminDeleteQuestion } from '../services/apiClient';
import { fetchTaxonomyTopics } from '../services/taxonomyClient';

export default function AdminQuestions() {
  const { user } = useAuthStore();
  const navigate = useNavigate();
  const [items, setItems] = React.useState([]);
  const [loading, setLoading] = React.useState(false);
  const [error, setError] = React.useState('');
  const [search, setSearch] = React.useState('');
  const [page, setPage] = React.useState(0);
  const [total, setTotal] = React.useState(0);
  const PAGE_SIZE = 20;
  const [form, setForm] = React.useState({
    subject: 'python_basics',
    topic: '',
    question_type: 'fill_in_the_blank',
    code_snippet: '',
    correct_answer: '',
    difficulty: 'easy',
  });
  const [topics, setTopics] = React.useState([]);

  const canAccess = user && (user.role === 'teacher' || user.role === 'admin');
  React.useEffect(() => {
    if (!canAccess) {
      navigate('/login');
    }
  }, [canAccess]);

  const fetchList = async () => {
    try {
      setLoading(true);
      const res = await adminListQuestions({ subject: form.subject, q: search, limit: PAGE_SIZE, offset: page * PAGE_SIZE });
      setItems(res.items || []);
      setTotal(res.total || 0);
      setError('');
    } catch (e) {
      setError('목록을 불러오지 못했습니다.');
    } finally {
      setLoading(false);
    }
  };

  React.useEffect(() => { fetchList(); }, [search, page, form.subject]);
  React.useEffect(() => {
    (async () => {
      try {
        const res = await fetchTaxonomyTopics(form.subject);
        setTopics(res.items || []);
      } catch {}
    })();
  }, [form.subject]);

  const onChange = (e) => setForm({ ...form, [e.target.name]: e.target.value });

  const onSubmit = async (e) => {
    e.preventDefault();
    try {
      setLoading(true);
      await adminCreateQuestion(form);
      await fetchList();
      setForm({ ...form, topic: '', code_snippet: '', correct_answer: '' });
    } catch (e) {
      setError('등록에 실패했습니다.');
    } finally {
      setLoading(false);
    }
  };

  const onDelete = async (id) => {
    if (!confirm('삭제하시겠습니까?')) return;
    try {
      setLoading(true);
      await adminDeleteQuestion(id);
      await fetchList();
    } catch {
      setError('삭제에 실패했습니다.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: 960, margin: '24px auto', padding: 24, background: '#fff', borderRadius: 8 }}>
      <h1 style={{ fontSize: 24, marginBottom: 16 }}>문항 출제(교사/관리자)</h1>
      {error && <div style={{ color: '#dc2626', marginBottom: 12 }}>{error}</div>}

      <form onSubmit={onSubmit} style={{ display:'grid', gridTemplateColumns:'1fr 1fr', gap: 12, marginBottom: 24 }}>
        <div>
          <label>과목</label>
          <select name="subject" value={form.subject} onChange={onChange} style={{ width:'100%', padding:8, border:'1px solid #d1d5db', borderRadius:6 }}>
            <option value="python_basics">Python 기초</option>
          </select>
        </div>
        <div>
          <label>토픽</label>
          <select name="topic" value={form.topic} onChange={onChange} required style={{ width:'100%', padding:8, border:'1px solid #d1d5db', borderRadius:6 }}>
            <option value="">선택...</option>
            {topics.map(t => (
              <option key={t.topic_key} value={t.topic_key}>{t.topic_key}{t.is_core ? '' : ' (ext)'}</option>
            ))}
          </select>
        </div>
        <div>
          <label>문항 유형</label>
          <select name="question_type" value={form.question_type} onChange={onChange} style={{ width:'100%', padding:8, border:'1px solid #d1d5db', borderRadius:6 }}>
            <option value="fill_in_the_blank">빈칸</option>
            <option value="multiple_choice" disabled>객관식(후속)</option>
            <option value="short_answer">단답</option>
          </select>
        </div>
        <div>
          <label>난이도</label>
          <select name="difficulty" value={form.difficulty} onChange={onChange} style={{ width:'100%', padding:8, border:'1px solid #d1d5db', borderRadius:6 }}>
            <option value="easy">easy</option>
            <option value="medium">medium</option>
            <option value="hard">hard</option>
          </select>
        </div>
        <div style={{ gridColumn:'1 / -1' }}>
          <label>문항 텍스트/코드</label>
          <textarea name="code_snippet" value={form.code_snippet} onChange={onChange} required rows={5} style={{ width:'100%', padding:8, border:'1px solid #d1d5db', borderRadius:6 }} />
        </div>
        <div style={{ gridColumn:'1 / -1' }}>
          <label>정답</label>
          <input name="correct_answer" value={form.correct_answer} onChange={onChange} required style={{ width:'100%', padding:8, border:'1px solid #d1d5db', borderRadius:6 }} />
        </div>
        <div style={{ gridColumn:'1 / -1', textAlign:'right' }}>
          <button disabled={loading} type="submit" style={{ padding:'10px 16px', background:'#3b82f6', color:'#fff', border:'none', borderRadius:6 }}>등록</button>
        </div>
      </form>

      <h2 style={{ fontSize: 18, margin:'8px 0 12px' }}>문항 목록</h2>
      <div style={{ display:'flex', gap:8, marginBottom:12 }}>
        <input placeholder="검색(토픽/정답/본문)" value={search} onChange={(e)=>{ setSearch(e.target.value); setPage(0); }} style={{ flex:1, padding:8, border:'1px solid #d1d5db', borderRadius:6 }} />
        <button onClick={()=>{ setPage(0); fetchList(); }} style={{ padding:'8px 12px', border:'1px solid #d1d5db', borderRadius:6, background:'#fff' }}>검색</button>
      </div>
      {loading && <div>로딩 중...</div>}
      <div>
        {items.map((it) => (
          <div key={it.id} style={{ border:'1px solid #e5e7eb', borderRadius:6, padding:12, marginBottom:8 }}>
            <div style={{ display:'flex', justifyContent:'space-between', alignItems:'center' }}>
              <div>
                <div style={{ fontWeight:600 }}>{it.topic} <span style={{ color:'#6b7280' }}>[{it.difficulty}]</span></div>
                <div style={{ color:'#374151', whiteSpace:'pre-wrap' }}>{it.code_snippet}</div>
                <div style={{ color:'#6b7280', fontSize:12 }}>정답: {it.correct_answer}</div>
              </div>
              <div style={{ display:'flex', gap:8 }}>
                {/* 간단 수정: 정답만 수정 예시 */}
                <button onClick={async ()=>{ const nv = prompt('정답 수정', it.correct_answer); if (nv!=null){ setLoading(true); try{ await adminUpdateQuestion(it.id, { correct_answer: nv }); await fetchList(); } finally { setLoading(false);} } }} style={{ padding:'6px 10px', background:'#f59e0b', color:'#fff', border:'none', borderRadius:6 }}>수정</button>
                <button onClick={() => onDelete(it.id)} style={{ padding:'6px 10px', background:'#ef4444', color:'#fff', border:'none', borderRadius:6 }}>삭제</button>
              </div>
            </div>
          </div>
        ))}
      </div>
      <div style={{ display:'flex', justifyContent:'space-between', marginTop:12 }}>
        <button disabled={page===0} onClick={()=>setPage((p)=>Math.max(0,p-1))} style={{ padding:'6px 10px', border:'1px solid #d1d5db', borderRadius:6, background:'#fff' }}>이전</button>
        <div style={{ color:'#6b7280' }}>{items.length ? page*PAGE_SIZE+1 : 0} - {Math.min((page+1)*PAGE_SIZE, total)} / {total}</div>
        <button disabled={(page+1)*PAGE_SIZE >= total} onClick={()=>setPage((p)=>p+1)} style={{ padding:'6px 10px', border:'1px solid #d1d5db', borderRadius:6, background:'#fff' }}>다음</button>
      </div>
    </div>
  );
}


