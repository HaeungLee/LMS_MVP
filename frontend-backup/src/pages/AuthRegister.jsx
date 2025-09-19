import React from 'react';
import { useNavigate, Link } from 'react-router-dom';
import useAuthStore from '../stores/authStore';

const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || '') + '/api/v1';

export default function AuthRegister() {
  const navigate = useNavigate();
  const { fetchMe } = useAuthStore();
  const [email, setEmail] = React.useState('');
  const [password, setPassword] = React.useState('');
  const [displayName, setDisplayName] = React.useState('');
  const [loading, setLoading] = React.useState(false);
  const [error, setError] = React.useState('');

  const onSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    try {
      const res = await fetch(`${API_BASE_URL}/auth/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ email, password, display_name: displayName }),
      });
      if (!res.ok) throw new Error('회원가입 실패');
      await fetchMe();
      navigate('/');
    } catch (err) {
      setError('이미 사용 중인 이메일일 수 있습니다.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ display:'flex', justifyContent:'center', alignItems:'center', minHeight:'100vh' }}>
      <form onSubmit={onSubmit} style={{ background:'#fff', padding:24, borderRadius:8, width:360, boxShadow:'0 1px 3px rgba(0,0,0,0.1)' }}>
        <h1 style={{ fontSize:24, marginBottom:16 }}>회원가입</h1>
        {error && <div style={{ color:'#dc2626', marginBottom:12 }}>{error}</div>}
        <div style={{ marginBottom:12 }}>
          <label style={{ display:'block', marginBottom:6 }}>이메일</label>
          <input value={email} onChange={(e)=>setEmail(e.target.value)} type="email" required style={{ width:'90%', padding:10, border:'1px solid #d1d5db', borderRadius:6 }} />
        </div>
        <div style={{ marginBottom:12 }}>
          <label style={{ display:'block', marginBottom:6 }}>비밀번호</label>
          <input value={password} onChange={(e)=>setPassword(e.target.value)} type="password" required style={{ width:'90%', padding:10, border:'1px solid #d1d5db', borderRadius:6 }} />
        </div>
        <div style={{ marginBottom:12 }}>
          <label style={{ display:'block', marginBottom:6 }}>표시 이름</label>
          <input value={displayName} onChange={(e)=>setDisplayName(e.target.value)} type="text" style={{ width:'90%', padding:10, border:'1px solid #d1d5db', borderRadius:6 }} />
        </div>
        <div style={{ display:'flex', alignItems:'center', justifyContent:'space-between', marginBottom:16 }}>
          <Link to="/login" style={{ fontSize:14, color:'#3b82f6' }}>로그인</Link>
        </div>
        <button disabled={loading} type="submit" style={{ width:'100%', padding:12, background:'#10b981', color:'#fff', border:'none', borderRadius:8, fontWeight:'600' }}>
          {loading ? '가입 중...' : '가입하기'}
        </button>
      </form>
    </div>
  );
}


