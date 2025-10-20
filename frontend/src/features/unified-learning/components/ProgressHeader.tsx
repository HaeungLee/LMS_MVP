/**
 * 진행 헤더 - 상단 고정 진행 상황 표시
 */

import { Calendar, TrendingUp } from 'lucide-react';

interface ProgressHeaderProps {
  week: number;
  day: number;
  theme: string;
  progress: number;
}

export default function ProgressHeader({ week, day, theme, progress }: ProgressHeaderProps) {
  return (
    <div className="sticky top-0 z-40 bg-white border-b border-gray-200 shadow-sm">
      <div className="max-w-7xl mx-auto px-4 py-3">
        <div className="flex items-center justify-between">
          {/* 왼쪽: Week/Day 정보 */}
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2 text-sm">
              <Calendar className="w-4 h-4 text-indigo-600" />
              <span className="font-semibold text-gray-900">Week {week}</span>
              <span className="text-gray-400">·</span>
              <span className="text-gray-600">Day {day}</span>
            </div>
            <div className="hidden md:block text-sm text-gray-500">
              {theme}
            </div>
          </div>

          {/* 오른쪽: 진행률 */}
          <div className="flex items-center gap-3">
            <div className="hidden sm:block w-32 h-2 bg-gray-100 rounded-full overflow-hidden">
              <div 
                className="h-full bg-gradient-to-r from-indigo-500 to-purple-600 rounded-full transition-all duration-500"
                style={{ width: `${progress}%` }}
              />
            </div>
            <div className="flex items-center gap-1 text-sm font-semibold text-indigo-600">
              <TrendingUp className="w-4 h-4" />
              <span>{Math.round(progress)}%</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
