/**
 * 완료 요약 - 오늘의 학습 완료 축하
 */

import { Trophy, ArrowRight, Calendar } from 'lucide-react';

interface CompletionSummaryProps {
  week: number;
  day: number;
  theme: string;
  onContinue: () => void;
  onNextDay?: () => void;
}

export default function CompletionSummary({ week, day, theme, onContinue, onNextDay }: CompletionSummaryProps) {
  return (
    <div className="bg-gradient-to-br from-purple-500 to-pink-500 rounded-2xl shadow-2xl p-8 text-white text-center">
      {/* 트로피 아이콘 */}
      <div className="w-24 h-24 bg-white/20 backdrop-blur-sm rounded-full flex items-center justify-center mx-auto mb-6">
        <Trophy className="w-12 h-12 text-yellow-300" />
      </div>

      {/* 축하 메시지 */}
      <h2 className="text-3xl font-bold mb-4">
        🎉 오늘의 학습 완료!
      </h2>
      <p className="text-lg opacity-90 mb-8">
        Week {week} Day {day}의 모든 학습을 마쳤습니다.<br />
        "{theme}"를 완벽하게 이해하셨네요!
      </p>

      {/* 성취 */}
      <div className="bg-white/10 backdrop-blur-sm rounded-xl p-6 mb-8">
        <div className="grid grid-cols-3 gap-4 text-center">
          <div>
            <div className="text-3xl font-bold mb-1">✅</div>
            <div className="text-sm opacity-80">교재 학습</div>
          </div>
          <div>
            <div className="text-3xl font-bold mb-1">💻</div>
            <div className="text-sm opacity-80">실습 완료</div>
          </div>
          <div>
            <div className="text-3xl font-bold mb-1">✍️</div>
            <div className="text-sm opacity-80">퀴즈 통과</div>
          </div>
        </div>
      </div>

      {/* 다음 학습 안내 */}
      <div className="bg-white/10 backdrop-blur-sm rounded-xl p-4 mb-6">
        <div className="flex items-center gap-3 text-left">
          <Calendar className="w-8 h-8" />
          <div>
            <p className="text-sm opacity-80">다음 학습</p>
            <p className="font-semibold">Day {day + 1}로 계속 학습하세요!</p>
          </div>
        </div>
      </div>

      {/* 버튼 그룹 */}
      <div className="space-y-3">
        {/* 다음 Day로 버튼 */}
        {onNextDay && (
          <button
            onClick={onNextDay}
            className="w-full bg-white text-purple-600 py-4 px-6 rounded-xl hover:shadow-xl transition-all duration-200 font-bold flex items-center justify-center gap-2"
          >
            다음 Day {day + 1} 시작하기 🚀
            <ArrowRight className="w-5 h-5" />
          </button>
        )}
        
        {/* 대시보드 버튼 */}
        <button
          onClick={onContinue}
          className="w-full bg-white/20 text-white border-2 border-white py-3 px-6 rounded-xl hover:bg-white/30 transition-all duration-200 font-semibold flex items-center justify-center gap-2"
        >
          대시보드로 돌아가기
        </button>
      </div>

      {/* 격려 메시지 */}
      <p className="mt-6 text-sm opacity-80">
        💪 꾸준히 학습하면 목표를 이룰 수 있어요!
      </p>
    </div>
  );
}
