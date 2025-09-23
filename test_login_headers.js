// 네트워크 헤더 확인 테스트
// F12 → Console에서 실행

fetch('http://localhost:8000/api/v1/auth/logout', {
  method: 'POST',
  credentials: 'include'
})
.then(() => {
  console.log('🚪 로그아웃 완료');
  
  // 상세 로그인 테스트
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
  console.log('🔑 로그인 응답 상태:', response.status);
  console.log('📋 Response Headers:');
  
  // 모든 응답 헤더 출력
  for (let [key, value] of response.headers.entries()) {
    console.log(`   ${key}: ${value}`);
  }
  
  // Set-Cookie 헤더 특별히 확인
  const setCookie = response.headers.get('set-cookie');
  console.log('🍪 Set-Cookie 헤더:', setCookie);
  
  return response.json();
})
.then(data => {
  console.log('🔑 로그인 응답 데이터:', data);
  console.log('🍪 로그인 후 쿠키:', document.cookie);
})
.catch(err => console.error('❌ 로그인 테스트 실패:', err));