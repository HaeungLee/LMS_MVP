import React from 'react';
import { useNavigate, Link } from 'react-router-dom';
import useAuthStore from '../stores/authStore';

const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || '') + '/api/v1';

export default function AuthLogin() {
  const navigate = useNavigate();
  const { fetchMe } = useAuthStore();
  const [email, setEmail] = React.useState('');
  const [password, setPassword] = React.useState('');
  const [remember, setRemember] = React.useState(true);
  const [loading, setLoading] = React.useState(false);
  const [error, setError] = React.useState('');

  const onSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    try {
      const res = await fetch(`${API_BASE_URL}/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ email, password, remember }),
      });
      if (!res.ok) throw new Error('로그인 실패');
      await fetchMe();
      navigate('/');
    } catch (err) {
      setError('이메일 또는 비밀번호를 확인하세요.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ display:'flex', justifyContent:'center', alignItems:'center', minHeight:'100vh' }}>
      <form onSubmit={onSubmit} style={{ background:'#fff', padding:24, borderRadius:8, width:360, boxShadow:'0 1px 3px rgba(0,0,0,0.1)' }}>
        <h1 style={{ fontSize:24, marginBottom:16 }}>로그인</h1>
        {error && <div style={{ color:'#dc2626', marginBottom:12 }}>{error}</div>}
        <div style={{ marginBottom:12 }}>
          <label style={{ display:'block', marginBottom:6 }}>이메일</label>
          <input value={email} onChange={(e)=>setEmail(e.target.value)} type="email" required style={{ width:'90%', padding:10, border:'1px solid #d1d5db', borderRadius:6 }} />
        </div>
        <div style={{ marginBottom:12 }}>
          <label style={{ display:'block', marginBottom:6 }}>비밀번호</label>
          <input value={password} onChange={(e)=>setPassword(e.target.value)} type="password" required style={{ width:'90%', padding:10, border:'1px solid #d1d5db', borderRadius:6 }} />
        </div>
        <div style={{ display:'flex', alignItems:'center', justifyContent:'space-between', marginBottom:16 }}>
          <label style={{ display:'flex', alignItems:'center', gap:8 }}>
            <input type="checkbox" checked={remember} onChange={(e)=>setRemember(e.target.checked)} />
            <span>로그인 유지</span>
          </label>
          <Link to="/register" style={{ fontSize:14, color:'#3b82f6' }}>회원가입</Link>
        </div>
        <button disabled={loading} type="submit" style={{ width:'100%', padding:12, background:'#3b82f6', color:'#fff', border:'none', borderRadius:8, fontWeight:'600' }}>
          {loading ? '로그인 중...' : '로그인'}
        </button>
      </form>
    </div>
  );
}


