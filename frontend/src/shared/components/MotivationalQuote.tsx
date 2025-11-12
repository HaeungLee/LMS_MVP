import React, { useState, useEffect } from 'react';
import { Sparkles } from 'lucide-react';

// API에서 명언을 가져오도록 변경 (DB 기반)
interface Quote {
  id: number;
  content: string;
  author: string | null;
  category: string;
  order_number: number;
}

export function MotivationalQuote() {
  const [quote, setQuote] = useState<Quote | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    // API에서 랜덤 명언 가져오기
    const fetchQuote = async () => {
      try {
        const response = await fetch('/api/v1/quotes/random');
        if (!response.ok) throw new Error('Failed to fetch quote');
        
        const data: Quote = await response.json();
        setQuote(data);
      } catch (err) {
        console.error('명언 로딩 실패:', err);
        // Fallback: 기본 명언 사용
        setQuote({
          id: 0,
          content: "완벽함보다 꾸준함으로 나아가자.",
          author: "명언 111",
          category: 'general',
          order_number: 111
        });
      } finally {
        setIsLoading(false);
      }
    };

    fetchQuote();

    // 페이드인 애니메이션
    const timer = setTimeout(() => {
      setIsVisible(true);
    }, 100);

    return () => clearTimeout(timer);
  }, []);

  if (isLoading) {
    return (
      <div className="mt-8 mb-4 p-6 bg-gradient-to-r from-purple-50 to-blue-50 dark:from-purple-900/20 dark:to-blue-900/20 rounded-xl border border-purple-200 dark:border-purple-800 animate-pulse">
        <div className="h-16 bg-purple-200 dark:bg-purple-800 rounded"></div>
      </div>
    );
  }

  if (!quote) {
    return null;
  }

  return (
    <div
      className={`mt-8 mb-4 p-6 bg-gradient-to-r from-purple-50 to-blue-50 dark:from-purple-900/20 dark:to-blue-900/20 rounded-xl border border-purple-200 dark:border-purple-800 transition-all duration-3000 ${
        isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4'
      }`}
    >
      <div className="flex items-start space-x-3">
        <Sparkles className="w-6 h-6 text-purple-600 dark:text-purple-400 flex-shrink-0 mt-1" />
        <div className="flex-1">
          <p className="text-gray-700 dark:text-gray-300 text-base leading-relaxed italic">
            "{quote.content}"
          </p>
          {quote.author && (
            <p className="text-gray-500 dark:text-gray-400 text-sm mt-2 text-right">
              - {quote.author}
            </p>
          )}
        </div>
      </div>
    </div>
  );
}
