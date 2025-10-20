// AI 커리큘럼 요청 상세 디버깅
// F12 → Console에서 실행

console.log('🍪 현재 쿠키:', document.cookie);

// 1. /auth/me 재확인
fetch('http://localhost:8000/api/v1/auth/me', {
  method: 'GET',
  credentials: 'include'
})
.then(response => {
  console.log('👤 /auth/me 상태:', response.status);
  return response.json();
})
.then(data => {
  console.log('👤 사용자 정보:', data);
  
  // 2. AI 커리큘럼 요청 (헤더 상세 확인)
  return fetch('http://localhost:8000/api/v1/ai-curriculum/generate-curriculum-stream', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    credentials: 'include',
    body: JSON.stringify({
      subject_key: 'python',
      learning_goals: ['Python 기초'],
      difficulty_level: 3
    })
  });
})
.then(response => {
  console.log('🤖 AI 커리큘럼 상태:', response.status);
  
  // 응답 헤더 확인
  console.log('📋 AI 커리큘럼 Response Headers:');
  for (let [key, value] of response.headers.entries()) {
    console.log(`   ${key}: ${value}`);
  }
  
  return response.text();
})
.then(text => {
  console.log('🤖 AI 커리큘럼 응답:', text);
})
.catch(err => console.error('❌ 테스트 실패:', err));