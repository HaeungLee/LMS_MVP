// 토큰 스트리밍 확인 (더 상세한 로그)
// F12 → Console에서 실행

let tokenCount = 0;
let chunkCount = 0;

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
  console.log('📡 스트리밍 시작');
  
  const reader = response.body?.getReader();
  const decoder = new TextDecoder();
  
  if (reader) {
    function pump() {
      return reader.read().then(({ done, value }) => {
        if (done) {
          console.log(`✅ 스트리밍 완료 - 총 ${chunkCount}개 청크, ${tokenCount}개 토큰`);
          return;
        }
        
        chunkCount++;
        const chunk = decoder.decode(value);
        const lines = chunk.split('\n');
        
        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6));
              
              if (data.type === 'started') {
                console.log('🚀 시작:', data.message);
              } else if (data.type === 'token') {
                tokenCount++;
                console.log(`🎯 토큰 #${tokenCount}:`, JSON.stringify(data.content));
              } else if (data.type === 'section_change') {
                console.log('📄 섹션 변경:', data.message);
              } else if (data.type === 'completed') {
                console.log('✅ 완료:', data.message);
              } else {
                console.log('📦 기타 데이터:', data);
              }
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
.catch(err => console.error('❌ 스트리밍 실패:', err));