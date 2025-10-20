// 브라우저 콘솔에서 스트리밍 테스트
// F12 → Console에서 실행

console.log('🧪 스트리밍 테스트 시작');

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
  console.log('📡 응답 상태:', response.status);
  console.log('📋 응답 헤더:');
  for (let [key, value] of response.headers.entries()) {
    console.log(`   ${key}: ${value}`);
  }
  
  const reader = response.body?.getReader();
  const decoder = new TextDecoder();
  
  if (reader) {
    function pump() {
      return reader.read().then(({ done, value }) => {
        if (done) {
          console.log('✅ 스트리밍 완료');
          return;
        }
        
        const chunk = decoder.decode(value);
        console.log('📦 받은 청크:', JSON.stringify(chunk));
        
        const lines = chunk.split('\n');
        console.log('📄 분할된 라인들:', lines);
        
        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6));
              console.log('🎯 파싱된 데이터:', data);
            } catch (e) {
              console.warn('❌ JSON 파싱 실패:', line);
            }
          }
        }
        
        return pump();
      });
    }
    
    pump();
  }
})
.catch(err => console.error('❌ 스트리밍 테스트 실패:', err));