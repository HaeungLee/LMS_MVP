// 브라우저 콘솔에서 실행 - 로그아웃 후 재로그인 테스트

// 1. 로그아웃
fetch('http://localhost:8000/api/v1/auth/logout', {
  method: 'POST',
  credentials: 'include'
})
.then(response => {
  console.log('🚪 로그아웃 상태:', response.status);
  console.log('🍪 로그아웃 후 쿠키:', document.cookie);
  
  // 2. 재로그인
  return fetch('http://localhost:8000/api/v1/auth/login', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    credentials: 'include',
    body: JSON.stringify({
      email: 'test@test.com',
      password: 'test123'
    })
  });
})
.then(response => {
  console.log('🔑 재로그인 상태:', response.status);
  console.log('🍪 재로그인 후 쿠키:', document.cookie);
  
  // 3. 즉시 인증 확인
  return fetch('http://localhost:8000/api/v1/auth/me', {
    method: 'GET',
    credentials: 'include'
  });
})
.then(response => {
  console.log('👤 즉시 인증 확인:', response.status);
  return response.json();
})
.then(data => console.log('👤 즉시 사용자 정보:', data))
.catch(err => console.error('❌ 전체 테스트 실패:', err));