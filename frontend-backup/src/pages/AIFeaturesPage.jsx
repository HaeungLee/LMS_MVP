import React, { useState } from 'react';
import { 
  Brain, 
  MessageCircle, 
  TrendingUp, 
  Code,
  Map,
  Sparkles,
  Settings,
  CheckCircle,
  Clock,
  ChevronRight,
  Lightbulb,
  BarChart3 // 오류 수정을 위해 추가
} from 'lucide-react';

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import AIAnalysisDashboard from '@/components/ai/AIAnalysisDashboard';
import AIMentorChatImproved from '@/components/ai/AIMentorChatImproved';
import AdaptiveDifficultyWidget from '@/components/ai/AdaptiveDifficultyWidget';

const AIFeaturesPage = () => {
  const [activeFeatureId, setActiveFeatureId] = useState('analysis');
  const [userId] = useState(1); // 실제로는 인증된 사용자 ID를 사용

  const aiFeatures = [
    {
      id: 'analysis',
      title: '심층 학습 분석',
      description: '학습 패턴을 분석하여 개인화된 인사이트를 제공합니다.',
      icon: Brain,
      component: AIAnalysisDashboard
    },
    {
      id: 'mentor',
      title: 'AI 멘토링',
      description: '24/7 개인 학습 코치와 실시간으로 대화하세요.',
      icon: MessageCircle,
      component: AIMentorChatImproved
    },
    {
      id: 'difficulty',
      title: '적응형 난이도',
      description: '성과에 따라 최적의 난이도를 자동으로 조절합니다.',
      icon: TrendingUp,
      component: AdaptiveDifficultyWidget
    },
    {
      id: 'code-review',
      title: 'AI 코드 리뷰',
      description: '작성한 코드를 AI가 검토하고 개선점을 제안합니다.',
      icon: Code,
      component: null // Coming Soon
    },
    {
      id: 'learning-path',
      title: '개인화 학습 경로',
      description: '목표에 맞는 맞춤형 학습 로드맵을 생성합니다.',
      icon: Map,
      component: null // Coming Soon
    }
  ];

  const activeFeature = aiFeatures.find(f => f.id === activeFeatureId);
  const ActiveComponent = activeFeature?.component;

  return (
    <div className="bg-slate-50 dark:bg-slate-950 min-h-screen font-sans text-slate-800 dark:text-slate-200">
      <div className="container mx-auto px-4 py-8">
        <div className="flex flex-col lg:flex-row gap-8">
          
          {/* --- Left Sidebar --- */}
          <aside className="w-full lg:w-1/4 lg:flex-shrink-0">
            <div className="p-4 bg-white dark:bg-slate-900/70 border border-slate-200 dark:border-slate-800 rounded-xl backdrop-blur-sm sticky top-8">
              <div className="flex items-center gap-3 mb-6 px-2">
                <Sparkles className="w-7 h-7 text-blue-500" />
                <h1 className="text-xl font-bold text-slate-900 dark:text-white">AI 학습 기능</h1>
              </div>
              <nav className="space-y-1">
                {aiFeatures.map((feature) => {
                  const Icon = feature.icon;
                  const isActive = activeFeatureId === feature.id;
                  return (
                    <button
                      key={feature.id}
                      onClick={() => setActiveFeatureId(feature.id)}
                      className={`w-full flex items-center text-left p-3 rounded-lg transition-all duration-200 ${
                        isActive 
                        ? 'bg-blue-50 dark:bg-blue-500/10 text-blue-600 dark:text-blue-400' 
                        : 'hover:bg-slate-100 dark:hover:bg-slate-800/50 text-slate-600 dark:text-slate-400'
                      }`}
                    >
                      <Icon className={`w-5 h-5 mr-3 flex-shrink-0 ${isActive ? 'text-blue-500' : ''}`} />
                      <div className="flex-grow">
                        <p className={`font-semibold text-sm ${isActive ? 'text-blue-600 dark:text-blue-300' : 'text-slate-700 dark:text-slate-300'}`}>
                          {feature.title}
                        </p>
                      </div>
                      {!feature.component && <Badge className="bg-slate-200 dark:bg-slate-700 text-slate-600 dark:text-slate-300">예정</Badge>}
                    </button>
                  );
                })}
              </nav>
            </div>
          </aside>

          {/* --- Main Content --- */}
          <main className="flex-1 min-w-0">
            <div className="space-y-8">
              {activeFeature && (
                <div className="mb-6">
                  <h2 className="text-3xl font-bold text-slate-900 dark:text-white">{activeFeature.title}</h2>
                  <p className="text-slate-500 dark:text-slate-400 mt-1">{activeFeature.description}</p>
                </div>
              )}

              <div className="min-h-[500px]">
                {ActiveComponent ? (
                  <ActiveComponent userId={userId} />
                ) : (
                  <Card className="h-full flex items-center justify-center bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-900 dark:to-slate-800/50">
                    <div className="text-center p-8">
                      <div className="w-20 h-20 bg-white dark:bg-slate-800 rounded-full mx-auto flex items-center justify-center shadow-md mb-6">
                        <activeFeature.icon className="w-10 h-10 text-slate-400 dark:text-slate-500" />
                      </div>
                      <h3 className="text-xl font-bold text-slate-800 dark:text-slate-200 mb-2">곧 출시될 기능입니다</h3>
                      <p className="text-slate-600 dark:text-slate-400 max-w-sm mx-auto">
                        {activeFeature.title} 기능은 현재 열심히 개발 중입니다. 더 나은 학습 경험을 위해 최선을 다하고 있으니 조금만 기다려주세요!
                      </p>
                      <Badge className="mt-6 bg-blue-100 text-blue-700 dark:bg-blue-500/20 dark:text-blue-300">Coming Soon</Badge>
                    </div>
                  </Card>
                )}
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* AI System Status */}
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Settings className="w-5 h-5 text-slate-500" />
                      AI 시스템 상태
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="grid grid-cols-2 gap-4">
                    <div className="flex items-center gap-3">
                      <CheckCircle className="w-5 h-5 text-green-500" />
                      <div>
                        <p className="font-semibold text-sm text-slate-800 dark:text-slate-200">학습 분석</p>
                        <p className="text-xs text-slate-500 dark:text-slate-400">정상</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-3">
                      <CheckCircle className="w-5 h-5 text-green-500" />
                      <div>
                        <p className="font-semibold text-sm text-slate-800 dark:text-slate-200">AI 멘토링</p>
                        <p className="text-xs text-slate-500 dark:text-slate-400">정상</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-3">
                      <CheckCircle className="w-5 h-5 text-green-500" />
                      <div>
                        <p className="font-semibold text-sm text-slate-800 dark:text-slate-200">난이도 조절</p>
                        <p className="text-xs text-slate-500 dark:text-slate-400">정상</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-3">
                      <Clock className="w-5 h-5 text-amber-500" />
                      <div>
                        <p className="font-semibold text-sm text-slate-800 dark:text-slate-200">코드 리뷰</p>
                        <p className="text-xs text-slate-500 dark:text-slate-400">준비 중</p>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                {/* Tips */}
                <Card className="bg-gradient-to-r from-blue-50 to-purple-50 dark:from-slate-800/50 dark:to-slate-900/50 border-blue-200 dark:border-slate-800">
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2 text-blue-900 dark:text-blue-300">
                      <Lightbulb className="w-5 h-5" />
                      AI 기능 활용 팁
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <ul className="space-y-2 text-sm text-blue-800 dark:text-blue-300/80">
                      <li className="flex items-start">
                        <ChevronRight className="w-4 h-4 mr-2 mt-0.5 flex-shrink-0" />
                        <span><strong>AI 멘토에게</strong> 구체적으로 질문하면 더 정확한 답변을 얻을 수 있어요.</span>
                      </li>
                      <li className="flex items-start">
                        <ChevronRight className="w-4 h-4 mr-2 mt-0.5 flex-shrink-0" />
                        <span><strong>학습 분석은</strong> 데이터가 많을수록 더 정확해져요. 꾸준히 학습해보세요!</span>
                      </li>
                    </ul>
                  </CardContent>
                </Card>
              </div>
            </div>
          </main>
        </div>
      </div>
    </div>
  );
};

export default AIFeaturesPage;
