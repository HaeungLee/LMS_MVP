import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import { 
  Brain, 
  MessageCircle, 
  TrendingUp, 
  Code,
  Map,
  Sparkles,
  User,
  BarChart3,
  Settings
} from 'lucide-react';

// AI 컴포넌트들 import
import AIAnalysisDashboard from '../components/ai/AIAnalysisDashboard';
import AIMentorChat from '../components/ai/AIMentorChat';
import AdaptiveDifficultyWidget from '../components/ai/AdaptiveDifficultyWidget';

const AIFeaturesPage = () => {
  const [activeTab, setActiveTab] = useState('analysis');
  const [userId] = useState(1); // 실제로는 인증된 사용자 ID를 사용

  const aiFeatures = [
    {
      id: 'analysis',
      title: '심층 학습 분석',
      description: 'AI가 당신의 학습 패턴을 분석하고 개인화된 인사이트를 제공합니다',
      icon: Brain,
      color: 'blue',
      component: AIAnalysisDashboard
    },
    {
      id: 'mentor',
      title: 'AI 멘토링',
      description: '24/7 개인 학습 코치와 실시간 대화하며 학습 도움을 받으세요',
      icon: MessageCircle,
      color: 'green',
      component: AIMentorChat
    },
    {
      id: 'difficulty',
      title: '적응형 난이도',
      description: '실시간 성과 분석을 통해 최적의 난이도로 자동 조절됩니다',
      icon: TrendingUp,
      color: 'purple',
      component: AdaptiveDifficultyWidget
    },
    {
      id: 'code-review',
      title: 'AI 코드 리뷰',
      description: '작성한 코드를 AI가 전문적으로 검토하고 개선 방안을 제시합니다',
      icon: Code,
      color: 'orange',
      component: null // 추후 구현
    },
    {
      id: 'learning-path',
      title: '개인화 학습 경로',
      description: '목표와 현재 수준에 맞는 맞춤형 학습 로드맵을 생성합니다',
      icon: Map,
      color: 'red',
      component: null // 추후 구현
    }
  ];

  const renderFeatureContent = (feature) => {
    if (!feature.component) {
      return (
        <Card>
          <CardContent className="pt-6">
            <div className="text-center py-12">
              <feature.icon className="w-16 h-16 mx-auto mb-4 text-gray-400" />
              <h3 className="text-lg font-semibold mb-2">{feature.title}</h3>
              <p className="text-gray-600 mb-4">{feature.description}</p>
              <Badge variant="secondary">곧 출시 예정</Badge>
            </div>
          </CardContent>
        </Card>
      );
    }

    const Component = feature.component;
    return <Component userId={userId} />;
  };

  return (
    <div className="container mx-auto px-4 py-8 max-w-7xl">
      {/* 헤더 */}
      <div className="text-center mb-8">
        <div className="flex items-center justify-center mb-4">
          <Sparkles className="w-8 h-8 text-blue-500 mr-2" />
          <h1 className="text-3xl font-bold">AI 학습 기능</h1>
        </div>
        <p className="text-gray-600 text-lg max-w-2xl mx-auto">
          첨단 AI 기술로 당신만의 맞춤형 학습 경험을 만나보세요
        </p>
      </div>

      {/* AI 기능 개요 */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-4 mb-8">
        {aiFeatures.map((feature) => {
          const Icon = feature.icon;
          return (
            <Card 
              key={feature.id} 
              className={`cursor-pointer transition-all hover:shadow-lg ${
                activeTab === feature.id ? 'ring-2 ring-blue-500' : ''
              }`}
              onClick={() => setActiveTab(feature.id)}
            >
              <CardContent className="pt-6">
                <div className="text-center">
                  <Icon className={`w-8 h-8 mx-auto mb-2 text-${feature.color}-500`} />
                  <h3 className="font-semibold text-sm">{feature.title}</h3>
                  <p className="text-xs text-gray-600 mt-1 line-clamp-2">
                    {feature.description}
                  </p>
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>

      {/* AI 기능 탭 */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <TabsList className="grid w-full grid-cols-5">
          {aiFeatures.map((feature) => (
            <TabsTrigger key={feature.id} value={feature.id} className="text-xs">
              {feature.title.split(' ')[0]}
            </TabsTrigger>
          ))}
        </TabsList>

        {aiFeatures.map((feature) => (
          <TabsContent key={feature.id} value={feature.id} className="mt-6">
            {renderFeatureContent(feature)}
          </TabsContent>
        ))}
      </Tabs>

      {/* AI 시스템 상태 */}
      <Card className="mt-8">
        <CardHeader>
          <CardTitle className="flex items-center">
            <Settings className="w-5 h-5 mr-2" />
            AI 시스템 상태
          </CardTitle>
          <CardDescription>
            현재 AI 기능들의 동작 상태를 확인하세요
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center">
              <div className="w-3 h-3 bg-green-500 rounded-full mx-auto mb-2"></div>
              <p className="text-sm font-medium">심층 분석</p>
              <p className="text-xs text-gray-600">정상 동작</p>
            </div>
            <div className="text-center">
              <div className="w-3 h-3 bg-green-500 rounded-full mx-auto mb-2"></div>
              <p className="text-sm font-medium">AI 멘토링</p>
              <p className="text-xs text-gray-600">정상 동작</p>
            </div>
            <div className="text-center">
              <div className="w-3 h-3 bg-green-500 rounded-full mx-auto mb-2"></div>
              <p className="text-sm font-medium">난이도 조절</p>
              <p className="text-xs text-gray-600">정상 동작</p>
            </div>
            <div className="text-center">
              <div className="w-3 h-3 bg-yellow-500 rounded-full mx-auto mb-2"></div>
              <p className="text-sm font-medium">코드 리뷰</p>
              <p className="text-xs text-gray-600">준비 중</p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* 도움말 */}
      <Card className="mt-6 bg-gradient-to-r from-blue-50 to-purple-50 border-blue-200">
        <CardContent className="pt-6">
          <div className="text-center">
            <h3 className="font-semibold text-blue-900 mb-2">💡 AI 기능 활용 팁</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm text-blue-800">
              <div>
                <strong>심층 분석:</strong> 최소 5개 문제를 풀어야 정확한 분석이 가능합니다
              </div>
              <div>
                <strong>AI 멘토링:</strong> 구체적인 질문을 하면 더 도움이 되는 답변을 받을 수 있습니다
              </div>
              <div>
                <strong>난이도 조절:</strong> 시간을 두고 문제를 풀면 더 정확한 난이도 추천을 받습니다
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default AIFeaturesPage;
