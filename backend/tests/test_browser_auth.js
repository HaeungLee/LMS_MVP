// 브라우저 콘솔에서 실행할 테스트 코드
// F12 → Console 탭에서 실행하세요

console.log('🍪 현재 쿠키:', document.cookie);

// 현재 로그인 상태 확인
fetch('http://localhost:8000/api/v1/auth/me', {
  method: 'GET',
  credentials: 'include'
})
.then(response => {
  console.log('👤 로그인 상태:', response.status);
  return response.json();
})
.then(data => console.log('👤 사용자 정보:', data))
.catch(err => console.error('❌ 로그인 확인 실패:', err));

// AI 커리큘럼 API 테스트
fetch('http://localhost:8000/api/v1/ai-curriculum/generate-curriculum-stream', {
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
})
.then(response => {
  console.log('🤖 AI 커리큘럼 상태:', response.status);
  if (!response.ok) {
    return response.text().then(text => {
      console.error('🤖 AI 커리큘럼 에러:', text);
    });
  }
})
.catch(err => console.error('❌ AI 커리큘럼 실패:', err));