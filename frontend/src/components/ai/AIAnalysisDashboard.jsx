import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';

const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000') + '/api/v1';

import { 
  Brain, 
  TrendingUp, 
  Target, 
  Clock, 
  Award,
  RefreshCw,
  Lightbulb,
  BarChart3
} from 'lucide-react';

const AIAnalysisDashboard = ({ userId }) => {
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchAnalysis = async (useAI = false) => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch(`${API_BASE_URL}/ai-features/analysis/deep-learning/${userId}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          use_ai: useAI,
          analysis_type: "comprehensive"
        })
      });
      
      if (!response.ok) {
        throw new Error('분석 요청 실패');
      }
      
      const data = await response.json();
      if (data.success) {
        setAnalysis(data.analysis);
      } else {
        setError(data.message || '분석 실패');
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAnalysis(false); // 초기 로드는 AI 없이
  }, [userId]);

  const getLearnerTypeColor = (type) => {
    const colors = {
      'fast_learner': 'bg-green-100 text-green-800',
      'deep_thinker': 'bg-blue-100 text-blue-800',
      'practical_learner': 'bg-purple-100 text-purple-800',
      'steady_learner': 'bg-yellow-100 text-yellow-800',
      'struggling_learner': 'bg-red-100 text-red-800'
    };
    return colors[type] || 'bg-gray-100 text-gray-800';
  };

  const getLearnerTypeLabel = (type) => {
    const labels = {
      'fast_learner': '빠른 학습자',
      'deep_thinker': '심층 사고자',
      'practical_learner': '실무형 학습자',
      'steady_learner': '꾸준한 학습자',
      'struggling_learner': '도움 필요 학습자'
    };
    return labels[type] || type;
  };

  const getPhaseLabel = (phase) => {
    const labels = {
      'beginner': '초급',
      'intermediate': '중급',
      'advanced': '고급',
      'expert': '전문가'
    };
    return labels[phase] || phase;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <RefreshCw className="w-8 h-8 animate-spin mx-auto mb-4" />
          <p>AI가 당신의 학습 패턴을 분석하고 있습니다...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <Card className="border-red-200">
        <CardContent className="pt-6">
          <div className="text-center">
            <p className="text-red-600 mb-4">{error}</p>
            <Button onClick={() => fetchAnalysis(false)} variant="outline">
              다시 시도
            </Button>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (!analysis || !analysis.learner_profile) {
    return (
      <Card>
        <CardContent className="pt-6">
          <div className="text-center">
            <Brain className="w-12 h-12 mx-auto mb-4 text-gray-400" />
            <h3 className="text-lg font-semibold mb-2">학습 분석 준비 중</h3>
            <p className="text-gray-600 mb-4">
              더 정확한 분석을 위해 몇 개의 문제를 더 풀어주세요.
            </p>
            <Badge variant="secondary">
              최소 5개 문제 필요
            </Badge>
          </div>
        </CardContent>
      </Card>
    );
  }

  const { learner_profile, learning_metrics, recommendations, next_actions } = analysis;

  return (
    <div className="space-y-6">
      {/* 헤더 */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold">AI 학습 분석</h2>
          <p className="text-gray-600">당신만의 맞춤형 학습 인사이트</p>
        </div>
        <div className="space-x-2">
          <Button 
            onClick={() => fetchAnalysis(false)} 
            variant="outline"
            disabled={loading}
          >
            <RefreshCw className="w-4 h-4 mr-2" />
            새로고침
          </Button>
          <Button 
            onClick={() => fetchAnalysis(true)} 
            disabled={loading}
          >
            <Brain className="w-4 h-4 mr-2" />
            AI 심층 분석
          </Button>
        </div>
      </div>

      {/* 학습자 프로필 */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center space-x-2">
              <Target className="w-5 h-5 text-blue-500" />
              <div>
                <p className="text-sm text-gray-600">학습자 유형</p>
                <Badge className={getLearnerTypeColor(learner_profile.type)}>
                  {getLearnerTypeLabel(learner_profile.type)}
                </Badge>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center space-x-2">
              <Award className="w-5 h-5 text-green-500" />
              <div>
                <p className="text-sm text-gray-600">학습 단계</p>
                <p className="text-lg font-semibold">
                  {getPhaseLabel(learner_profile.phase)}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center space-x-2">
              <Clock className="w-5 h-5 text-purple-500" />
              <div>
                <p className="text-sm text-gray-600">최적 세션</p>
                <p className="text-lg font-semibold">
                  {learner_profile.optimal_session_length}분
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center space-x-2">
              <TrendingUp className="w-5 h-5 text-orange-500" />
              <div>
                <p className="text-sm text-gray-600">추천 난이도</p>
                <p className="text-lg font-semibold">
                  레벨 {learner_profile.preferred_difficulty}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* 학습 메트릭 */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <BarChart3 className="w-5 h-5 mr-2" />
            학습 성과 분석
          </CardTitle>
          <CardDescription>
            최근 학습 활동을 바탕으로 한 성과 지표
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <div>
              <p className="text-sm text-gray-600 mb-2">전체 정확도</p>
              <Progress 
                value={learning_metrics.overall_accuracy * 100} 
                className="mb-1"
              />
              <p className="text-sm font-medium">
                {(learning_metrics.overall_accuracy * 100).toFixed(1)}%
              </p>
            </div>
            
            <div>
              <p className="text-sm text-gray-600 mb-2">일관성 점수</p>
              <Progress 
                value={learning_metrics.consistency_score * 100} 
                className="mb-1"
              />
              <p className="text-sm font-medium">
                {(learning_metrics.consistency_score * 100).toFixed(1)}%
              </p>
            </div>
            
            <div>
              <p className="text-sm text-gray-600 mb-2">개선율</p>
              <Progress 
                value={Math.max(0, learning_metrics.improvement_rate * 100 + 50)} 
                className="mb-1"
              />
              <p className="text-sm font-medium">
                {learning_metrics.improvement_rate > 0 ? '+' : ''}
                {(learning_metrics.improvement_rate * 100).toFixed(1)}%
              </p>
            </div>
            
            <div>
              <p className="text-sm text-gray-600 mb-2">참여도</p>
              <Progress 
                value={learning_metrics.engagement_level * 100} 
                className="mb-1"
              />
              <p className="text-sm font-medium">
                {(learning_metrics.engagement_level * 100).toFixed(1)}%
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* 강점과 약점 */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="text-green-600">🎯 당신의 강점</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {learner_profile.strengths?.map((strength, index) => (
                <Badge key={index} variant="secondary" className="mr-2 mb-2">
                  {strength}
                </Badge>
              ))}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-orange-600">🔧 개선할 점</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {learner_profile.weaknesses?.map((weakness, index) => (
                <Badge key={index} variant="outline" className="mr-2 mb-2">
                  {weakness}
                </Badge>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* AI 추천사항 */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <Lightbulb className="w-5 h-5 mr-2" />
            AI 맞춤 추천
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {recommendations?.map((rec, index) => (
              <div key={index} className="p-4 bg-blue-50 rounded-lg">
                <div className="flex items-start justify-between">
                  <div>
                    <h4 className="font-semibold text-blue-900">{rec.title}</h4>
                    <p className="text-blue-700 text-sm mt-1">{rec.description}</p>
                  </div>
                  <Badge 
                    variant={rec.priority === 'high' ? 'default' : 'secondary'}
                  >
                    {rec.priority === 'high' ? '우선순위' : '권장'}
                  </Badge>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* 다음 액션 */}
      <Card>
        <CardHeader>
          <CardTitle>📋 다음 학습 액션</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {next_actions?.map((action, index) => (
              <div key={index} className="flex items-center justify-between p-3 border rounded-lg">
                <div>
                  <h4 className="font-medium">{action.title}</h4>
                  <p className="text-sm text-gray-600">{action.description}</p>
                </div>
                <Badge variant="outline">
                  {action.timeframe === 'today' ? '오늘' : 
                   action.timeframe === 'this_week' ? '이번 주' : '계획'}
                </Badge>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default AIAnalysisDashboard;
