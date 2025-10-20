/**
 * 교재 섹션 - 콘텐츠 렌더링
 */

import { useState } from 'react';
import { BookOpen, CheckCircle } from 'lucide-react';

interface TextbookSectionProps {
  content?: any;
  onComplete: () => void;
}

export default function TextbookSection({ content, onComplete }: TextbookSectionProps) {
  const [isCompleted, setIsCompleted] = useState(false);

  const handleComplete = () => {
    setIsCompleted(true);
    onComplete();
  };

  // 임시 콘텐츠 (content가 없을 때)
  const defaultContent = `
# FastAPI 라우팅 기초

## 라우팅이란?

라우팅은 클라이언트의 요청을 적절한 핸들러 함수로 연결하는 과정입니다.

## 기본 라우트 정의

\`\`\`python
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello World"}
\`\`\`

## 경로 매개변수

URL에서 동적인 값을 받을 수 있습니다:

\`\`\`python
@app.get("/items/{item_id}")
def read_item(item_id: int):
    return {"item_id": item_id}
\`\`\`

## 쿼리 매개변수

선택적 매개변수를 받을 수 있습니다:

\`\`\`python
@app.get("/items/")
def read_items(skip: int = 0, limit: int = 10):
    return {"skip": skip, "limit": limit}
\`\`\`

## 핵심 개념

- **경로 매개변수**: URL의 일부로 필수 값
- **쿼리 매개변수**: ?key=value 형태로 선택적 값
- **타입 힌트**: Python 타입 힌트로 자동 검증
  `;

  const displayContent = content?.text || content || defaultContent;

  return (
    <div className="bg-white rounded-2xl shadow-lg p-8">
      {/* 헤더 */}
      <div className="flex items-center gap-3 mb-6 pb-4 border-b border-gray-200">
        <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-cyan-500 rounded-xl flex items-center justify-center">
          <BookOpen className="w-6 h-6 text-white" />
        </div>
        <div>
          <h2 className="text-2xl font-bold text-gray-900">📖 교재 학습</h2>
          <p className="text-sm text-gray-600">차근차근 읽어보세요</p>
        </div>
      </div>

      {/* 콘텐츠 */}
      <div className="prose prose-indigo max-w-none">
        <div 
          className="whitespace-pre-wrap text-gray-800 leading-relaxed"
          dangerouslySetInnerHTML={{ 
            __html: displayContent
              .replace(/#{1,6}\s+(.*)/g, '<h2 class="text-2xl font-bold mt-6 mb-3 text-gray-900">$1</h2>')
              .replace(/```(\w+)?\n([\s\S]*?)```/g, '<pre class="bg-gray-900 text-gray-100 p-4 rounded-lg overflow-x-auto my-4"><code>$2</code></pre>')
              .replace(/`([^`]+)`/g, '<code class="bg-gray-100 text-red-600 px-2 py-1 rounded">$1</code>')
              .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
              .replace(/\n\n/g, '<br/><br/>')
          }}
        />
      </div>

      {/* 완료 버튼 */}
      <div className="mt-8 pt-6 border-t border-gray-200">
        {!isCompleted ? (
          <button
            onClick={handleComplete}
            className="w-full bg-gradient-to-r from-blue-600 to-cyan-600 text-white py-4 px-6 rounded-xl hover:shadow-lg transition-all duration-200 flex items-center justify-center gap-2"
          >
            <CheckCircle className="w-5 h-5" />
            <span className="font-semibold">이해했습니다! 다음으로</span>
          </button>
        ) : (
          <div className="w-full bg-green-50 text-green-700 py-4 px-6 rounded-xl flex items-center justify-center gap-2">
            <CheckCircle className="w-5 h-5" />
            <span className="font-semibold">✅ 완료했습니다!</span>
          </div>
        )}
      </div>
    </div>
  );
}
