import React, { useState, useEffect } from 'react';
import { Badge } from '@/components/ui/badge';
import { Clock, CheckCircle, TrendingUp, AlertCircle } from 'lucide-react';
import apiClient from '../../services/apiClient';

const LearningStatsWidget = ({ userId }) => {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        setLoading(true);
        
        // 실제 API 호출로 사용자 통계 가져오기
        const response = await apiClient.get(`/stats/user/${userId}/daily`);
        setStats(response.data);
        setError(null);
      } catch (error) {
        console.error('학습 통계 로딩 실패:', error);
        // API 실패 시 폴백 데이터
        setStats({
          todayStudyTime: '2.5시간',
          completedQuestions: 45,
          currentLevel: '중급',
          todayAccuracy: 78
        });
        setError('실시간 데이터 로딩 실패');
      } finally {
        setLoading(false);
      }
    };

    if (userId) {
      fetchStats();
    }
  }, [userId]);

  if (loading) {
    return (
      <div className="space-y-3">
        {[1, 2, 3].map((i) => (
          <div key={i} className="flex justify-between items-center">
            <div className="h-4 bg-slate-200 rounded w-20 animate-pulse"></div>
            <div className="h-6 bg-slate-200 rounded w-16 animate-pulse"></div>
          </div>
        ))}
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {error && (
        <div className="flex items-center text-xs text-amber-600 mb-2">
          <AlertCircle className="w-3 h-3 mr-1" />
          {error}
        </div>
      )}
      
      <div className="flex justify-between items-center">
        <span className="text-sm text-slate-600 dark:text-slate-400 flex items-center">
          <Clock className="w-3 h-3 mr-1" />
          오늘 학습 시간
        </span>
        <Badge className="bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200">
          {stats?.todayStudyTime || '0분'}
        </Badge>
      </div>
      
      <div className="flex justify-between items-center">
        <span className="text-sm text-slate-600 dark:text-slate-400 flex items-center">
          <CheckCircle className="w-3 h-3 mr-1" />
          완료한 문제
        </span>
        <Badge className="bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200">
          {stats?.completedQuestions || 0}개
        </Badge>
      </div>
      
      <div className="flex justify-between items-center">
        <span className="text-sm text-slate-600 dark:text-slate-400 flex items-center">
          <TrendingUp className="w-3 h-3 mr-1" />
          현재 레벨
        </span>
        <Badge className="bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200">
          {stats?.currentLevel || '초급'}
        </Badge>
      </div>
      
      {stats?.todayAccuracy && (
        <div className="flex justify-between items-center">
          <span className="text-sm text-slate-600 dark:text-slate-400">오늘 정답률</span>
          <Badge className={`${
            stats.todayAccuracy >= 80 
              ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
              : stats.todayAccuracy >= 60 
              ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200'
              : 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
          }`}>
            {stats.todayAccuracy}%
          </Badge>
        </div>
      )}
    </div>
  );
};

export default LearningStatsWidget;
