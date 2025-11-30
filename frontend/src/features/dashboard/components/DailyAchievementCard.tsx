import React, { memo, useMemo } from 'react';

interface DailyAchievementCardProps {
  streak: number; // 연속 학습일
  todayCompleted: boolean; // 오늘 학습 완료 여부
  weeklyProgress: number; // 주간 목표 달성률 (0-100)
  totalDaysLearned: number; // 총 학습일
}

const DailyAchievementCard: React.FC<DailyAchievementCardProps> = memo(({
  streak,
  todayCompleted,
  weeklyProgress,
  totalDaysLearned
}) => {
  // useMemo로 계산값 캐싱
  const encouragementMessage = useMemo((): string => {
    if (streak === 0 && !todayCompleted) {
      return "오늘 학습을 시작해보세요! 🚀";
    }
    if (streak === 1) {
      return "좋아요! 내일도 계속 해봐요! 💪";
    }
    if (streak >= 2 && streak < 7) {
      return "연속 학습 중! 이 기세를 이어가세요! 🔥";
    }
    if (streak >= 7 && streak < 14) {
      return "일주일 연속! 정말 대단해요! 🎉";
    }
    if (streak >= 14 && streak < 30) {
      return "2주 연속! 학습이 습관이 되고 있어요! ✨";
    }
    if (streak >= 30 && streak < 100) {
      return "한 달 연속! 당신은 전설이에요! 🏆";
    }
    if (streak >= 100) {
      return "100일 연속! 불가능을 가능으로! 👑";
    }
    return "오늘도 화이팅! 💪";
  }, [streak, todayCompleted]);

  const streakEmoji = useMemo((): string => {
    if (streak === 0) return "🌱";
    if (streak < 7) return "🔥";
    if (streak < 14) return "🔥🔥";
    if (streak < 30) return "🔥🔥🔥";
    if (streak < 100) return "💎";
    return "👑";
  }, [streak]);

  const progressColor = useMemo((): string => {
    if (weeklyProgress >= 80) return "bg-green-500";
    if (weeklyProgress >= 50) return "bg-yellow-500";
    return "bg-gray-400";
  }, [weeklyProgress]);

  const milestoneMessage = useMemo((): string => {
    if (streak <= 0) return "";
    if (streak < 7) return `일주일 연속까지 ${7 - streak}일 남았어요!`;
    if (streak < 30) return `한 달 연속까지 ${30 - streak}일 남았어요!`;
    if (streak < 100) return `100일 연속까지 ${100 - streak}일 남았어요!`;
    return "당신은 이미 전설입니다! 🎉";
  }, [streak]);

  const learningWeeks = useMemo(() => Math.floor(totalDaysLearned / 7), [totalDaysLearned]);

  return (
    <div className="bg-white rounded-xl shadow-lg p-6 hover:shadow-xl transition-all duration-300 border-2 border-transparent hover:border-indigo-200">
      {/* 헤더 */}
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-xl font-bold text-gray-800">
          오늘의 성취 🎯
        </h3>
        {todayCompleted && (
          <span className="bg-green-100 text-green-700 px-3 py-1 rounded-full text-sm font-semibold">
            ✅ 완료
          </span>
        )}
      </div>

      {/* 연속 학습일 */}
      <div className="bg-gradient-to-br from-orange-50 to-red-50 rounded-lg p-6 mb-4">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-gray-600 text-sm mb-1">연속 학습일</p>
            <div className="flex items-baseline gap-2">
              <span className="text-5xl font-black text-transparent bg-clip-text bg-gradient-to-r from-orange-500 to-red-500">
                {streak}
              </span>
              <span className="text-2xl text-gray-600">일</span>
            </div>
          </div>
          <div className="text-6xl">
            {streakEmoji}
          </div>
        </div>
        
        {/* 격려 메시지 */}
        <div className="mt-4 bg-white/80 rounded-lg p-3">
          <p className="text-sm font-medium text-gray-700 text-center">
            {encouragementMessage}
          </p>
        </div>
      </div>

      {/* 주간 목표 달성률 */}
      <div className="mb-4">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm font-medium text-gray-600">주간 목표</span>
          <span className="text-sm font-bold text-gray-800">{weeklyProgress}%</span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
          <div 
            className={`h-full ${progressColor} transition-all duration-500 ease-out rounded-full`}
            style={{ width: `${weeklyProgress}%` }}
          />
        </div>
      </div>

      {/* 통계 요약 */}
      <div className="grid grid-cols-2 gap-4">
        <div className="bg-indigo-50 rounded-lg p-3 text-center">
          <p className="text-2xl font-bold text-indigo-600">{totalDaysLearned}</p>
          <p className="text-xs text-gray-600 mt-1">총 학습일</p>
        </div>
        <div className="bg-purple-50 rounded-lg p-3 text-center">
          <p className="text-2xl font-bold text-purple-600">
            {learningWeeks}
          </p>
          <p className="text-xs text-gray-600 mt-1">학습 주차</p>
        </div>
      </div>

      {/* 다음 마일스톤 */}
      {streak > 0 && milestoneMessage && (
        <div className="mt-4 pt-4 border-t border-gray-200">
          <p className="text-xs text-gray-500 text-center">
            {milestoneMessage}
          </p>
        </div>
      )}
    </div>
  );
});

DailyAchievementCard.displayName = 'DailyAchievementCard';

export default DailyAchievementCard;
