import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';

const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || '') + '/api/v1';
import { 
  TrendingUp, 
  TrendingDown, 
  Minus,
  Target,
  Brain,
  Clock,
  BarChart3,
  RefreshCw,
  AlertTriangle,
  CheckCircle
} from 'lucide-react';

const AdaptiveDifficultyWidget = ({ userId, topic = "general", currentDifficulty = 2 }) => {
  const [recommendation, setRecommendation] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [nextDifficulty, setNextDifficulty] = useState(null);

  const fetchOptimalDifficulty = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch(`${API_BASE_URL}/ai-features/difficulty/optimal/${userId}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          topic: topic,
          current_difficulty: currentDifficulty
        })
      });
      
      if (!response.ok) {
        throw new Error('난이도 분석 실패');
      }
      
      const data = await response.json();
      if (data.success) {
        setRecommendation(data.recommendation);
      } else {
        setError('난이도 분석에 실패했습니다.');
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const fetchNextQuestionDifficulty = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/ai-features/difficulty/next-question/${userId}?topic=${encodeURIComponent(topic)}`);
      const data = await response.json();
      if (data.success) {
        setNextDifficulty(data.next_difficulty);
      }
    } catch (err) {
      console.error('다음 문제 난이도 조회 실패:', err);
    }
  };

  useEffect(() => {
    fetchOptimalDifficulty();
    fetchNextQuestionDifficulty();
  }, [userId, topic, currentDifficulty]);

  const getDifficultyTrend = () => {
    if (!recommendation) return { icon: Minus, color: 'gray', text: '분석 중' };
    
    const diff = recommendation.recommended_difficulty - currentDifficulty;
    
    if (diff > 0) {
      return { icon: TrendingUp, color: 'green', text: '난이도 상승 권장' };
    } else if (diff < 0) {
      return { icon: TrendingDown, color: 'red', text: '난이도 하락 권장' };
    } else {
      return { icon: Minus, color: 'blue', text: '현재 난이도 유지' };
    }
  };

  const getDifficultyLabel = (level) => {
    const labels = {
      1: '입문',
      2: '초급',
      3: '중급',
      4: '고급',
      5: '전문가'
    };
    return labels[level] || `레벨 ${level}`;
  };

  const getConfidenceColor = (confidence) => {
    if (confidence >= 0.8) return 'text-green-600';
    if (confidence >= 0.6) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getExpectedAccuracyColor = (accuracy) => {
    if (accuracy >= 0.8) return 'bg-green-100 text-green-800';
    if (accuracy >= 0.7) return 'bg-yellow-100 text-yellow-800';
    if (accuracy >= 0.6) return 'bg-orange-100 text-orange-800';
    return 'bg-red-100 text-red-800';
  };

  if (loading) {
    return (
      <Card>
        <CardContent className="pt-6">
          <div className="flex items-center justify-center space-x-2">
            <RefreshCw className="w-5 h-5 animate-spin" />
            <span>AI가 최적 난이도를 분석하고 있습니다...</span>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card className="border-red-200">
        <CardContent className="pt-6">
          <div className="flex items-center space-x-2 text-red-600">
            <AlertTriangle className="w-5 h-5" />
            <span>{error}</span>
          </div>
          <Button 
            onClick={fetchOptimalDifficulty} 
            variant="outline" 
            size="sm" 
            className="mt-2"
          >
            다시 시도
          </Button>
        </CardContent>
      </Card>
    );
  }

  if (!recommendation) {
    return (
      <Card>
        <CardContent className="pt-6">
          <div className="text-center text-gray-500">
            난이도 분석을 위한 데이터가 부족합니다.
          </div>
        </CardContent>
      </Card>
    );
  }

  const trend = getDifficultyTrend();
  const TrendIcon = trend.icon;

  return (
    <div className="space-y-4">
      {/* 메인 난이도 추천 카드 */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <Brain className="w-5 h-5 mr-2" />
            AI 난이도 조절
            <Badge variant="secondary" className="ml-2">
              {topic === "general" ? "전체" : topic}
            </Badge>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* 현재 난이도 */}
            <div className="text-center">
              <p className="text-sm text-gray-600 mb-2">현재 난이도</p>
              <div className="text-2xl font-bold text-gray-700">
                {getDifficultyLabel(currentDifficulty)}
              </div>
              <p className="text-xs text-gray-500 mt-1">레벨 {currentDifficulty}</p>
            </div>

            {/* 트렌드 표시 */}
            <div className="text-center">
              <p className="text-sm text-gray-600 mb-2">추천 변경</p>
              <div className={`text-${trend.color}-600 flex items-center justify-center`}>
                <TrendIcon className="w-6 h-6 mr-1" />
                <span className="text-sm font-medium">{trend.text}</span>
              </div>
            </div>

            {/* 추천 난이도 */}
            <div className="text-center">
              <p className="text-sm text-gray-600 mb-2">추천 난이도</p>
              <div className="text-2xl font-bold text-blue-600">
                {getDifficultyLabel(recommendation.recommended_difficulty)}
              </div>
              <p className="text-xs text-gray-500 mt-1">레벨 {recommendation.recommended_difficulty}</p>
            </div>
          </div>

          {/* 추천 근거 */}
          <div className="mt-4 p-3 bg-blue-50 rounded-lg">
            <div className="flex items-start space-x-2">
              <Target className="w-4 h-4 text-blue-600 mt-0.5" />
              <div>
                <p className="text-sm text-blue-900 font-medium">AI 분석 결과</p>
                <p className="text-sm text-blue-700">{recommendation.reasoning}</p>
              </div>
            </div>
          </div>

          {/* 추가 정보 */}
          <div className="mt-4 grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
            <div className="text-center">
              <p className="text-gray-600">신뢰도</p>
              <p className={`font-semibold ${getConfidenceColor(recommendation.confidence)}`}>
                {(recommendation.confidence * 100).toFixed(1)}%
              </p>
            </div>
            
            <div className="text-center">
              <p className="text-gray-600">예상 정답률</p>
              <Badge className={getExpectedAccuracyColor(recommendation.expected_accuracy)}>
                {(recommendation.expected_accuracy * 100).toFixed(1)}%
              </Badge>
            </div>
            
            <div className="text-center">
              <p className="text-gray-600">재평가 시점</p>
              <p className="font-medium text-gray-700">
                {recommendation.adjustment_timeline}
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* 다음 문제 난이도 미리보기 */}
      {nextDifficulty && (
        <Card className="bg-gradient-to-r from-green-50 to-blue-50 border-green-200">
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <CheckCircle className="w-5 h-5 text-green-600" />
                <div>
                  <p className="font-medium text-green-900">다음 문제 준비됨</p>
                  <p className="text-sm text-green-700">
                    {getDifficultyLabel(nextDifficulty)} 수준의 문제가 준비되어 있습니다
                  </p>
                </div>
              </div>
              <Badge variant="secondary">
                레벨 {nextDifficulty}
              </Badge>
            </div>
          </CardContent>
        </Card>
      )}

      {/* 난이도 조절 가이드 */}
      <Card>
        <CardHeader>
          <CardTitle className="text-sm">난이도 가이드</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-2 text-sm">
            <div className="flex justify-between items-center p-2 bg-gray-50 rounded">
              <span>레벨 1 (입문)</span>
              <span className="text-gray-600">기본 개념 학습</span>
            </div>
            <div className="flex justify-between items-center p-2 bg-gray-50 rounded">
              <span>레벨 2 (초급)</span>
              <span className="text-gray-600">기초 응용 문제</span>
            </div>
            <div className="flex justify-between items-center p-2 bg-gray-50 rounded">
              <span>레벨 3 (중급)</span>
              <span className="text-gray-600">복합 개념 적용</span>
            </div>
            <div className="flex justify-between items-center p-2 bg-gray-50 rounded">
              <span>레벨 4 (고급)</span>
              <span className="text-gray-600">심화 문제 해결</span>
            </div>
            <div className="flex justify-between items-center p-2 bg-gray-50 rounded">
              <span>레벨 5 (전문가)</span>
              <span className="text-gray-600">창의적 응용</span>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* 새로고침 버튼 */}
      <div className="text-center">
        <Button 
          onClick={() => {
            fetchOptimalDifficulty();
            fetchNextQuestionDifficulty();
          }} 
          variant="outline" 
          size="sm"
          disabled={loading}
        >
          <RefreshCw className={`w-4 h-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
          난이도 분석 새로고침
        </Button>
      </div>
    </div>
  );
};

export default AdaptiveDifficultyWidget;
