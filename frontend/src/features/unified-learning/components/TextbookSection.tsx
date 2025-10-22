/**
 * 교재 섹션 - 콘텐츠 렌더링 (IntersectionObserver 자동 추적)
 */

import { useState, useEffect, useRef } from 'react';
import { BookOpen, CheckCircle } from 'lucide-react';
import { api } from '../../../shared/services/apiClient';

interface TextbookSectionProps {
  content?: any;
  curriculumId?: number;
  onComplete: () => void;
}

export default function TextbookSection({ content, curriculumId, onComplete }: TextbookSectionProps) {
  const [isCompleted, setIsCompleted] = useState(false);
  const endMarkerRef = useRef<HTMLDivElement>(null);
  const hasTrackedRef = useRef(false);

  // IntersectionObserver로 교재 끝 지점 감지
  useEffect(() => {
    const endMarker = endMarkerRef.current;
    if (!endMarker || hasTrackedRef.current || isCompleted) return;

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          // 교재 끝이 뷰포트에 보이면 자동 완료
          if (entry.isIntersecting && !hasTrackedRef.current && !isCompleted) {
            hasTrackedRef.current = true;
            handleComplete();
          }
        });
      },
      {
        threshold: 0.5, // 50% 이상 보이면 트리거
        rootMargin: '0px',
      }
    );

    observer.observe(endMarker);

    return () => {
      observer.disconnect();
    };
  }, [curriculumId, isCompleted]);

  const handleComplete = () => {
    // 서버에 읽음 상태 전송
    (async () => {
      try {
        if (curriculumId) {
          await api.post('/mvp/textbook/track', { curriculum_id: curriculumId }, { timeoutMs: 15000 });
        }
      } catch (e) {
        // 실패해도 UX는 진행
        console.warn('Textbook track failed', e);
      }
      setIsCompleted(true);
      onComplete();
    })();
  };

  // 교재 콘텐츠가 없을 때 안내
  const defaultContent = `
# 📚 교재를 불러오는 중입니다

커리큘럼에서 오늘의 학습 교재를 준비하고 있습니다.

잠시만 기다려주세요... ⏳

## 교재가 곧 제공됩니다

- 커리큘럼 기반 맞춤 교재
- 단계별 학습 가이드
- 실습 예제 포함
- 핵심 개념 정리

*교재가 표시되지 않으면 페이지를 새로고침해주세요.*
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
          <h2 className="text-2xl font-bold text-gray-900">교재 학습</h2>
          <p className="text-sm text-gray-600">차근차근 읽어보세요</p>
        </div>
      </div>

      {/* 콘텐츠 */}
      <div className="prose prose-indigo max-w-none">
        <div 
          className="text-gray-800 leading-relaxed"
          dangerouslySetInnerHTML={{ 
            __html: displayContent
              // 제목 처리
              .replace(/#{1,6}\s+(.*)/g, '<h2 class="text-2xl font-bold mt-6 mb-3 text-grey-100">$1</h2>')
              // 코드 블록 처리 - 흰색 글씨, 검은 배경
              .replace(/```(\w+)?\n([\s\S]*?)```/g, '<pre class="bg-gray-900 text-white p-4 rounded-lg overflow-x-auto my-4 border-2 border-gray-700"><code class="text-white font-mono">$2</code></pre>')
              // 인라인 코드 처리 - 빨간색
              .replace(/`([^`]+)`/g, '<code class="bg-gray-100 text-red-600 px-2 py-1 rounded font-mono text-sm">$1</code>')
              // 볼드 처리
              .replace(/\*\*(.*?)\*\*/g, '<strong class="font-semibold text-gray-900">$1</strong>')
              // 일반 줄바꿈을 <p> 태그로 감싸기 (가독성 향상)
              .split('\n\n')
              .map((para: string) => para.trim() ? `<p class="text-gray-800 mb-4">${para.replace(/\n/g, '<br/>')}</p>` : '')
              .join('')
          }}
        />
        
        {/* IntersectionObserver 감지용 마커 - 교재 끝 지점 */}
        <div ref={endMarkerRef} className="h-1 w-full" aria-hidden="true" />
      </div>

      {/* 완료 버튼 (수동 완료도 가능) */}
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
        
        {/* 자동 추적 안내 */}
        {!isCompleted && (
          <p className="text-center text-sm text-gray-500 mt-3">
            교재를 끝까지 스크롤하면 자동으로 완료됩니다
          </p>
        )}
      </div>
    </div>
  );
}
