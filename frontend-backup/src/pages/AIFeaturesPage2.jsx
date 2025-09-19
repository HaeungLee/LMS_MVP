import React, { useState, useEffect } from 'react';
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
  BarChart3,
  RefreshCw,
  AlertCircle
} from 'lucide-react';
import apiClient from '../services/apiClient';
import AIAnalysisDashboard from '../components/ai/AIAnalysisDashboard';
import AdaptiveDifficultyWidget from '../components/ai/AdaptiveDifficultyWidget';
import AIMentorChatImproved from '../components/ai/AIMentorChatImproved';
import LearningStatsWidget from '../components/dashboard/LearningStatsWidget';

// --- Mock Components ---
const Card = ({ children, className = '' }) => (
  <div className={`bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl ${className}`}>
    {children}
  </div>
);

const CardHeader = ({ children, className = '' }) => (
  <div className={`p-6 border-b border-slate-200 dark:border-slate-800 ${className}`}>
    {children}
  </div>
);

const CardTitle = ({ children, className = '' }) => (
  <h3 className={`text-lg font-semibold text-slate-900 dark:text-white ${className}`}>
    {children}
  </h3>
);

const CardDescription = ({ children, className = '' }) => (
  <p className={`text-sm text-slate-500 dark:text-slate-400 ${className}`}>
    {children}
  </p>
);

const CardContent = ({ children, className = '' }) => (
  <div className={`p-6 ${className}`}>
    {children}
  </div>
);

const Badge = ({ children, className = '' }) => (
  <span className={`inline-block px-2.5 py-0.5 text-xs font-semibold rounded-full ${className}`}>
    {children}
  </span>
);

// AIMentorChatImproved 컴포넌트는 상단에서 import됨

const AIFeaturesPage = () => {
  const [activeFeatureId, setActiveFeatureId] = useState('analysis');
  const [userId] = useState(1); // 실제로는 인증된 사용자 ID를 사용

  const features = [
    {
      id: 'analysis',
      title: 'AI 심층 분석',
      description: '학습 데이터를 분석하고 개인별 맞춤 인사이트를 제공합니다.',
      icon: BarChart3,
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
    }
  ];

  const activeFeature = features.find(feature => feature.id === activeFeatureId);
  const ActiveComponent = activeFeature?.component || AIAnalysisDashboard;

  return (
    <div className="bg-slate-50 dark:bg-slate-950 min-h-screen font-sans text-slate-800 dark:text-slate-200">
      <div className="container mx-auto px-4 py-8">
        <div className="flex flex-col lg:flex-row gap-8">

          {/* --- Left Sidebar --- */}
          <div className="lg:w-80">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Sparkles className="w-5 h-5 text-blue-500" />
                  AI 학습 도우미
                </CardTitle>
                <CardDescription>
                  최신 AI 기술로 개인 맞춤 학습을 지원합니다.
                </CardDescription>
              </CardHeader>

              <CardContent className="p-0">
                <nav className="space-y-1">
                  {features.map((feature) => {
                    const Icon = feature.icon;
                    const isActive = activeFeatureId === feature.id;

                    return (
                      <button
                        key={feature.id}
                        onClick={() => setActiveFeatureId(feature.id)}
                        className={`w-full flex items-center text-left p-3 rounded-lg transition-all duration-200 ${
                          isActive
                            ? 'bg-blue-50 dark:bg-blue-900/20 border-r-2 border-blue-500 text-blue-700 dark:text-blue-300'
                            : 'hover:bg-slate-50 dark:hover:bg-slate-800/50 text-slate-600 dark:text-slate-400'
                        }`}
                      >
                        <Icon className={`w-5 h-5 mr-3 ${isActive ? 'text-blue-500' : 'text-slate-400'}`} />
                        <div className="flex-1 min-w-0">
                          <div className={`font-medium ${isActive ? 'text-blue-700 dark:text-blue-300' : ''}`}>
                            {feature.title}
                          </div>
                          <div className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
                            {feature.description}
                          </div>
                        </div>
                        <ChevronRight className={`w-4 h-4 transition-transform ${isActive ? 'rotate-90 text-blue-500' : 'text-slate-400'}`} />
                      </button>
                    );
                  })}
                </nav>
              </CardContent>
            </Card>

            {/* Quick Stats */}
            <Card className="mt-6">
              <CardHeader>
                <CardTitle className="text-base">학습 통계</CardTitle>
              </CardHeader>
              <CardContent>
                <LearningStatsWidget userId={userId} />
              </CardContent>
            </Card>
          </div>

          {/* --- Main Content --- */}
          <div className="flex-1">
            <ActiveComponent userId={userId} />
          </div>
        </div>
      </div>
    </div>
  );
};

export default AIFeaturesPage;
