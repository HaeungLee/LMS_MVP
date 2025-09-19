import React, { useState, useEffect } from 'react';
import { useQuery, useMutation } from '@tanstack/react-query';
import { 
  TrendingUp, 
  Target, 
  Brain, 
  BarChart3, 
  Zap, 
  Clock, 
  Award, 
  AlertTriangle,
  CheckCircle,
  ArrowRight,
  Lightbulb,
  Settings
} from 'lucide-react';
import { toast } from 'react-hot-toast';
import useAuthStore from '../../../shared/hooks/useAuthStore';
import { adaptiveLearningApi } from '../../../shared/services/apiClient';

// Phase 10 적응형 학습 타입 정의
interface PerformanceMetrics {
  accuracy: number;
  response_time: number;
  consistency: number;
  improvement_rate: number;
  engagement_score: number;
  difficulty_comfort_zone: [number, number];
}

interface AdaptationRecommendation {
  current_difficulty: number;
  recommended_difficulty: number;
  adjustment_type: string;
  confidence: number;
  reasoning: string;
  suggested_actions: string[];
  estimated_mastery_time?: number;
}

interface LearningState {
  state: 'struggling' | 'learning' | 'mastering' | 'mastered';
  description: string;
  color: string;
  icon: React.ComponentType<any>;
}

const AdaptiveLearningSystem: React.FC = () => {
  const { user } = useAuthStore();
  const [selectedSubject, setSelectedSubject] = useState<string>('python_basics');
  const [currentPerformance, setCurrentPerformance] = useState<PerformanceMetrics>({
    accuracy: 0.75,
    response_time: 85,
    consistency: 0.82,
    improvement_rate: 0.15,
    engagement_score: 0.88,
    difficulty_comfort_zone: [0.6, 0.8]
  });
  const [adaptationHistory, setAdaptationHistory] = useState<AdaptationRecommendation[]>([]);

  // 현재 성과 지표 조회
  const { data: performanceData, isLoading: isPerformanceLoading } = useQuery({
    queryKey: ['adaptive-performance', user?.id, selectedSubject],
    queryFn: () => adaptiveLearningApi.getCurrentPerformance(user?.id || 1, selectedSubject),
    enabled: !!user?.id,
    refetchInterval: 30000, // 30초마다 업데이트
  });

  // 성과 데이터가 있으면 업데이트
  useEffect(() => {
    if (performanceData) {
      setCurrentPerformance(performanceData);
    }
  }, [performanceData]);

  // 적응형 추천 뮤테이션
  const { mutate: getRecommendation, isPending: isAnalyzing } = useMutation({
    mutationFn: adaptiveLearningApi.getAdaptiveRecommendation,
    onSuccess: (recommendation) => {
      setAdaptationHistory(prev => [recommendation, ...prev.slice(0, 4)]); // 최근 5개 유지
      toast.success('적응형 분석이 완료되었습니다!');
    },
    onError: (error: any) => {
      toast.error(`분석 실패: ${error.message}`);
    },
  });

  const handleAnalyzePerformance = () => {
    getRecommendation({
      subject_key: selectedSubject,
      current_performance: currentPerformance,
      focus_areas: ['기본 문법', '문제 해결']
    });
  };

  // 학습 상태 결정
  const getLearningState = (accuracy: number): LearningState => {
    if (accuracy < 0.6) {
      return {
        state: 'struggling',
        description: '어려움을 겪고 있어요',
        color: 'text-red-600 bg-red-50 border-red-200',
        icon: AlertTriangle
      };
    } else if (accuracy < 0.8) {
      return {
        state: 'learning',
        description: '꾸준히 학습 중이에요',
        color: 'text-yellow-600 bg-yellow-50 border-yellow-200',
        icon: Brain
      };
    } else if (accuracy < 0.95) {
      return {
        state: 'mastering',
        description: '숙달 과정에 있어요',
        color: 'text-blue-600 bg-blue-50 border-blue-200',
        icon: TrendingUp
      };
    } else {
      return {
        state: 'mastered',
        description: '완전히 숙달했어요',
        color: 'text-green-600 bg-green-50 border-green-200',
        icon: Award
      };
    }
  };

  const learningState = getLearningState(currentPerformance.accuracy);
  const StateIcon = learningState.icon;

  const getDifficultyColor = (difficulty: number) => {
    if (difficulty < 0.3) return 'bg-green-500';
    if (difficulty < 0.6) return 'bg-yellow-500';
    if (difficulty < 0.8) return 'bg-orange-500';
    return 'bg-red-500';
  };

  const getAdjustmentIcon = (adjustmentType: string) => {
    switch (adjustmentType) {
      case 'decrease_major':
      case 'decrease_minor':
        return '📉';
      case 'increase_major':
      case 'increase_minor':
        return '📈';
      default:
        return '📊';
    }
  };

  // 시뮬레이션을 위한 성과 업데이트 (실제로는 학습 활동 후 자동 업데이트)
  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentPerformance(prev => ({
        ...prev,
        accuracy: Math.max(0.1, Math.min(1.0, prev.accuracy + (Math.random() - 0.5) * 0.05)),
        response_time: Math.max(20, prev.response_time + (Math.random() - 0.5) * 10),
        consistency: Math.max(0.1, Math.min(1.0, prev.consistency + (Math.random() - 0.5) * 0.03)),
        improvement_rate: Math.max(-0.5, Math.min(0.5, prev.improvement_rate + (Math.random() - 0.5) * 0.02)),
        engagement_score: Math.max(0.1, Math.min(1.0, prev.engagement_score + (Math.random() - 0.5) * 0.02))
      }));
    }, 5000); // 5초마다 업데이트

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      {/* 헤더 */}
      <div className="bg-gradient-to-r from-blue-50 to-purple-50 border border-blue-200 rounded-lg p-6">
        <div className="flex items-center mb-4">
          <TrendingUp className="w-8 h-8 text-blue-600 mr-3" />
          <div>
            <h2 className="text-2xl font-bold text-blue-900">📊 적응형 학습 시스템</h2>
            <p className="text-blue-700">실시간 성과 분석으로 최적의 학습 경로를 제안합니다</p>
          </div>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
          <div className="bg-white rounded p-3">
            <span className="font-medium text-blue-700">🎯 실시간 분석</span>
            <p className="text-gray-600">성과 기반 즉시 피드백</p>
          </div>
          <div className="bg-white rounded p-3">
            <span className="font-medium text-blue-700">⚡ 자동 조정</span>
            <p className="text-gray-600">난이도 스마트 조절</p>
          </div>
          <div className="bg-white rounded p-3">
            <span className="font-medium text-blue-700">📈 예측 모델</span>
            <p className="text-gray-600">숙달 시간 예측</p>
          </div>
        </div>
      </div>

      {/* 현재 학습 상태 */}
      <div className="bg-white rounded-lg p-6 shadow-sm border border-gray-200">
        <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
          <BarChart3 className="w-5 h-5 mr-2 text-green-600" />
          현재 학습 상태
        </h3>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* 학습 상태 카드 */}
          <div className={`border rounded-lg p-4 ${learningState.color}`}>
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center">
                <StateIcon className="w-6 h-6 mr-2" />
                <span className="font-medium">학습 상태</span>
              </div>
              <span className="text-2xl font-bold">
                {(currentPerformance.accuracy * 100).toFixed(0)}%
              </span>
            </div>
            <p className="text-sm font-medium">{learningState.description}</p>
            <p className="text-xs mt-1">정답률 기준</p>
          </div>

          {/* 성과 지표들 */}
          <div className="grid grid-cols-2 gap-4">
            <div className="bg-gray-50 rounded p-3">
              <div className="flex items-center justify-between">
                <Clock className="w-4 h-4 text-gray-600" />
                <span className="text-lg font-bold text-gray-900">
                  {currentPerformance.response_time.toFixed(0)}초
                </span>
              </div>
              <p className="text-xs text-gray-600 mt-1">평균 응답시간</p>
            </div>
            
            <div className="bg-gray-50 rounded p-3">
              <div className="flex items-center justify-between">
                <Target className="w-4 h-4 text-gray-600" />
                <span className="text-lg font-bold text-gray-900">
                  {(currentPerformance.consistency * 100).toFixed(0)}%
                </span>
              </div>
              <p className="text-xs text-gray-600 mt-1">일관성</p>
            </div>
            
            <div className="bg-gray-50 rounded p-3">
              <div className="flex items-center justify-between">
                <TrendingUp className="w-4 h-4 text-gray-600" />
                <span className={`text-lg font-bold ${
                  currentPerformance.improvement_rate > 0 ? 'text-green-600' : 'text-red-600'
                }`}>
                  {currentPerformance.improvement_rate > 0 ? '+' : ''}
                  {(currentPerformance.improvement_rate * 100).toFixed(1)}%
                </span>
              </div>
              <p className="text-xs text-gray-600 mt-1">향상률</p>
            </div>
            
            <div className="bg-gray-50 rounded p-3">
              <div className="flex items-center justify-between">
                <Zap className="w-4 h-4 text-gray-600" />
                <span className="text-lg font-bold text-gray-900">
                  {(currentPerformance.engagement_score * 100).toFixed(0)}%
                </span>
              </div>
              <p className="text-xs text-gray-600 mt-1">참여도</p>
            </div>
          </div>
        </div>

        {/* 적정 난이도 구간 */}
        <div className="mt-6 p-4 bg-blue-50 rounded-lg">
          <h4 className="font-medium text-blue-900 mb-3">🎯 적정 난이도 구간</h4>
          <div className="flex items-center space-x-4">
            <div className="flex-1">
              <div className="w-full bg-gray-200 rounded-full h-3 relative">
                <div 
                  className="bg-blue-500 h-3 rounded-full absolute"
                  style={{
                    left: `${currentPerformance.difficulty_comfort_zone[0] * 100}%`,
                    width: `${(currentPerformance.difficulty_comfort_zone[1] - currentPerformance.difficulty_comfort_zone[0]) * 100}%`
                  }}
                ></div>
                <div 
                  className="w-2 h-5 bg-green-500 rounded absolute -top-1 transform -translate-x-1"
                  style={{ left: '60%' }} // 현재 난이도 위치
                ></div>
              </div>
              <div className="flex justify-between text-xs text-gray-600 mt-1">
                <span>쉬움</span>
                <span>적정</span>
                <span>어려움</span>
              </div>
            </div>
          </div>
          <p className="text-sm text-blue-700 mt-2">
            현재는 <strong>적정 구간</strong>에서 학습하고 있습니다.
          </p>
        </div>

        {/* 분석 버튼 */}
        <div className="mt-6 pt-4 border-t border-gray-200">
          <button
            onClick={handleAnalyzePerformance}
            disabled={isAnalyzing}
            className={`w-full md:w-auto px-6 py-3 rounded-lg font-medium flex items-center justify-center ${
              isAnalyzing
                ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                : 'bg-gradient-to-r from-blue-600 to-purple-600 text-white hover:from-blue-700 hover:to-purple-700'
            }`}
          >
            {isAnalyzing ? (
              <>
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                AI 분석 중...
              </>
            ) : (
              <>
                <Brain className="w-5 h-5 mr-2" />
                적응형 분석 실행
              </>
            )}
          </button>
        </div>
      </div>

      {/* 적응형 추천 결과 */}
      {adaptationHistory.length > 0 && (
        <div className="bg-white rounded-lg p-6 shadow-sm border border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
            <Lightbulb className="w-5 h-5 mr-2 text-yellow-600" />
            AI 적응형 추천
          </h3>

          <div className="space-y-4">
            {adaptationHistory.map((recommendation, index) => (
              <div 
                key={index} 
                className={`border rounded-lg p-4 ${index === 0 ? 'border-blue-500 bg-blue-50' : 'border-gray-200'}`}
              >
                <div className="flex items-start justify-between mb-3">
                  <div className="flex items-center">
                    <span className="text-2xl mr-3">
                      {getAdjustmentIcon(recommendation.adjustment_type)}
                    </span>
                    <div>
                      <h4 className="font-medium text-gray-900">
                        {recommendation.adjustment_type.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                      </h4>
                      <p className="text-sm text-gray-600">
                        신뢰도: {(recommendation.confidence * 100).toFixed(0)}%
                      </p>
                    </div>
                  </div>
                  {index === 0 && (
                    <span className="bg-blue-600 text-white text-xs px-2 py-1 rounded">
                      최신
                    </span>
                  )}
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                  <div>
                    <p className="text-sm font-medium text-gray-700 mb-2">난이도 변화</p>
                    <div className="flex items-center space-x-3">
                      <div className="flex items-center">
                        <div className={`w-3 h-3 rounded-full ${getDifficultyColor(recommendation.current_difficulty)} mr-1`}></div>
                        <span className="text-sm">{(recommendation.current_difficulty * 100).toFixed(0)}%</span>
                      </div>
                      <ArrowRight className="w-4 h-4 text-gray-400" />
                      <div className="flex items-center">
                        <div className={`w-3 h-3 rounded-full ${getDifficultyColor(recommendation.recommended_difficulty)} mr-1`}></div>
                        <span className="text-sm">{(recommendation.recommended_difficulty * 100).toFixed(0)}%</span>
                      </div>
                    </div>
                  </div>
                  
                  {recommendation.estimated_mastery_time && (
                    <div>
                      <p className="text-sm font-medium text-gray-700 mb-2">예상 숙달 시간</p>
                      <div className="flex items-center">
                        <Clock className="w-4 h-4 text-gray-500 mr-1" />
                        <span className="text-sm">{recommendation.estimated_mastery_time}분</span>
                      </div>
                    </div>
                  )}
                </div>

                <div className="bg-white rounded p-3 mb-3">
                  <p className="text-sm text-gray-700">
                    <strong>추천 이유:</strong> {recommendation.reasoning}
                  </p>
                </div>

                <div>
                  <p className="text-sm font-medium text-gray-700 mb-2">추천 액션:</p>
                  <div className="space-y-1">
                    {recommendation.suggested_actions.map((action, actionIndex) => (
                      <div key={actionIndex} className="flex items-center text-sm text-gray-600">
                        <CheckCircle className="w-4 h-4 text-green-500 mr-2" />
                        <span>{action}</span>
                      </div>
                    ))}
                  </div>
                </div>

                {index === 0 && (
                  <div className="mt-4 pt-3 border-t border-gray-200">
                    <div className="flex space-x-3">
                      <button className="flex-1 bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700">
                        추천 적용하기
                      </button>
                      <button className="flex-1 bg-gray-200 text-gray-700 py-2 px-4 rounded-lg hover:bg-gray-300">
                        추천 거부하기
                      </button>
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* 적응형 학습 설정 */}
      <div className="bg-white rounded-lg p-6 shadow-sm border border-gray-200">
        <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
          <Settings className="w-5 h-5 mr-2 text-gray-600" />
          적응형 학습 설정
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              목표 정답률
            </label>
            <input
              type="range"
              min="60"
              max="95"
              defaultValue="75"
              className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
            />
            <div className="flex justify-between text-xs text-gray-500 mt-1">
              <span>60%</span>
              <span>75%</span>
              <span>95%</span>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              조정 민감도
            </label>
            <select className="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500">
              <option value="low">낮음 (안정적)</option>
              <option value="medium" selected>보통 (권장)</option>
              <option value="high">높음 (적극적)</option>
            </select>
          </div>
        </div>

        <div className="mt-4 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
          <p className="text-sm text-yellow-800">
            💡 <strong>팁:</strong> 적응형 학습은 여러분의 학습 패턴을 분석하여 최적의 난이도를 자동으로 조절합니다. 
            꾸준한 학습을 통해 더 정확한 추천을 받을 수 있습니다.
          </p>
        </div>
      </div>

      {/* Phase 10 기능 안내 */}
      <div className="bg-gradient-to-r from-purple-50 to-pink-50 border border-purple-200 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-purple-900 mb-3">
          🤖 Phase 10 - 적응형 학습 시스템
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
          <div>
            <h4 className="font-medium text-purple-800 mb-2">🎯 핵심 기능</h4>
            <ul className="text-purple-700 space-y-1">
              <li>• 실시간 성과 분석 및 피드백</li>
              <li>• AI 기반 난이도 자동 조절</li>
              <li>• 개인별 학습 상태 진단</li>
              <li>• 예측적 숙달 시간 계산</li>
            </ul>
          </div>
          <div>
            <h4 className="font-medium text-purple-800 mb-2">📊 분석 지표</h4>
            <ul className="text-purple-700 space-y-1">
              <li>• 정답률, 응답시간, 일관성</li>
              <li>• 향상률, 참여도 종합 분석</li>
              <li>• 적정 난이도 구간 설정</li>
              <li>• 학습 효과 추적 및 최적화</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AdaptiveLearningSystem;
