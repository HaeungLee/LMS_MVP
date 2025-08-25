import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { 
  CheckCircle, 
  Circle, 
  ArrowRight, 
  ArrowLeft,
  Sparkles,
  Brain,
  MessageCircle,
  Target,
  Code,
  Gift,
  Star
} from 'lucide-react';

const BetaOnboarding = ({ onComplete }) => {
  const [currentStep, setCurrentStep] = useState(0);
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    experience_level: '',
    interests: [],
    goals: [],
    beta_feedback_consent: false,
    ai_features_interest: []
  });

  const steps = [
    {
      id: 'welcome',
      title: '베타 테스터 환영',
      description: 'AI 기반 개인화 학습 플랫폼에 오신 것을 환영합니다!',
      component: WelcomeStep
    },
    {
      id: 'profile',
      title: '프로필 설정',
      description: '개인화된 학습 경험을 위한 기본 정보를 입력해주세요',
      component: ProfileStep
    },
    {
      id: 'interests',
      title: '학습 관심사',
      description: '관심 있는 학습 영역을 선택해주세요',
      component: InterestsStep
    },
    {
      id: 'ai-features',
      title: 'AI 기능 소개',
      description: '사용할 수 있는 AI 기능들을 확인해보세요',
      component: AIFeaturesStep
    },
    {
      id: 'beta-agreement',
      title: '베타 테스트 동의',
      description: '베타 테스트 참여 조건을 확인해주세요',
      component: BetaAgreementStep
    },
    {
      id: 'complete',
      title: '설정 완료',
      description: '이제 AI 기반 학습을 시작할 준비가 되었습니다!',
      component: CompleteStep
    }
  ];

  const handleNext = () => {
    if (currentStep < steps.length - 1) {
      setCurrentStep(currentStep + 1);
    }
  };

  const handlePrev = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
    }
  };

  const handleComplete = () => {
    // 온보딩 데이터 저장
    localStorage.setItem('beta_onboarding_complete', 'true');
    localStorage.setItem('beta_user_profile', JSON.stringify(formData));
    
    if (onComplete) {
      onComplete(formData);
    }
  };

  const CurrentStepComponent = steps[currentStep].component;
  const progress = ((currentStep + 1) / steps.length) * 100;

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-purple-50 flex items-center justify-center p-4">
      <div className="w-full max-w-2xl">
        {/* 진행률 */}
        <div className="mb-6">
          <div className="flex justify-between items-center mb-2">
            <span className="text-sm font-medium">온보딩 진행률</span>
            <span className="text-sm text-gray-600">{currentStep + 1} / {steps.length}</span>
          </div>
          <Progress value={progress} className="h-2" />
        </div>

        {/* 단계 표시 */}
        <div className="flex justify-center mb-6">
          <div className="flex items-center space-x-2">
            {steps.map((step, index) => (
              <div key={step.id} className="flex items-center">
                <div className={`w-8 h-8 rounded-full flex items-center justify-center text-xs font-medium ${
                  index < currentStep 
                    ? 'bg-green-500 text-white' 
                    : index === currentStep 
                      ? 'bg-blue-500 text-white' 
                      : 'bg-gray-200 text-gray-600'
                }`}>
                  {index < currentStep ? (
                    <CheckCircle className="w-4 h-4" />
                  ) : (
                    index + 1
                  )}
                </div>
                {index < steps.length - 1 && (
                  <div className={`w-12 h-0.5 ${
                    index < currentStep ? 'bg-green-500' : 'bg-gray-200'
                  }`} />
                )}
              </div>
            ))}
          </div>
        </div>

        {/* 현재 단계 컴포넌트 */}
        <CurrentStepComponent
          data={formData}
          onUpdate={setFormData}
          onNext={handleNext}
          onPrev={handlePrev}
          onComplete={handleComplete}
          isFirst={currentStep === 0}
          isLast={currentStep === steps.length - 1}
          stepInfo={steps[currentStep]}
        />
      </div>
    </div>
  );
};

// 환영 단계
const WelcomeStep = ({ onNext, stepInfo }) => {
  return (
    <Card className="text-center">
      <CardHeader>
        <div className="flex justify-center mb-4">
          <div className="w-16 h-16 bg-gradient-to-r from-blue-500 to-purple-500 rounded-full flex items-center justify-center">
            <Sparkles className="w-8 h-8 text-white" />
          </div>
        </div>
        <CardTitle className="text-2xl">{stepInfo.title}</CardTitle>
        <CardDescription className="text-lg">{stepInfo.description}</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          <div className="bg-blue-50 p-4 rounded-lg">
            <h3 className="font-semibold text-blue-900 mb-2">🎯 베타 테스트 특전</h3>
            <ul className="text-sm text-blue-800 space-y-1">
              <li>• 최신 AI 기능 우선 체험</li>
              <li>• 개인화된 학습 분석 무료 제공</li>
              <li>• 24/7 AI 멘토링 시스템 이용</li>
              <li>• 피드백 제공 시 정식 버전 할인 혜택</li>
            </ul>
          </div>
          
          <div className="bg-green-50 p-4 rounded-lg">
            <h3 className="font-semibold text-green-900 mb-2">🚀 AI 기능 미리보기</h3>
            <div className="grid grid-cols-2 gap-2 text-sm">
              <div className="flex items-center space-x-2 text-green-800">
                <Brain className="w-4 h-4" />
                <span>심층 학습 분석</span>
              </div>
              <div className="flex items-center space-x-2 text-green-800">
                <MessageCircle className="w-4 h-4" />
                <span>AI 멘토링</span>
              </div>
              <div className="flex items-center space-x-2 text-green-800">
                <Target className="w-4 h-4" />
                <span>적응형 난이도</span>
              </div>
              <div className="flex items-center space-x-2 text-green-800">
                <Code className="w-4 h-4" />
                <span>AI 코드 리뷰</span>
              </div>
            </div>
          </div>

          <Button onClick={onNext} className="w-full" size="lg">
            시작하기
            <ArrowRight className="w-4 h-4 ml-2" />
          </Button>
        </div>
      </CardContent>
    </Card>
  );
};

// 프로필 설정 단계
const ProfileStep = ({ data, onUpdate, onNext, onPrev, stepInfo }) => {
  const [errors, setErrors] = useState({});

  const handleSubmit = () => {
    const newErrors = {};
    
    if (!data.name.trim()) newErrors.name = '이름을 입력해주세요';
    if (!data.email.trim()) newErrors.email = '이메일을 입력해주세요';
    if (!data.experience_level) newErrors.experience_level = '경험 수준을 선택해주세요';

    setErrors(newErrors);
    
    if (Object.keys(newErrors).length === 0) {
      onNext();
    }
  };

  const experienceLevels = [
    { value: 'beginner', label: '초급 - 프로그래밍을 처음 배웁니다' },
    { value: 'intermediate', label: '중급 - 기본 개념을 알고 있습니다' },
    { value: 'advanced', label: '고급 - 실무 경험이 있습니다' },
    { value: 'expert', label: '전문가 - 다른 사람을 가르칠 수 있습니다' }
  ];

  return (
    <Card>
      <CardHeader>
        <CardTitle>{stepInfo.title}</CardTitle>
        <CardDescription>{stepInfo.description}</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          <div>
            <Label htmlFor="name">이름 *</Label>
            <Input
              id="name"
              value={data.name}
              onChange={(e) => onUpdate({ ...data, name: e.target.value })}
              placeholder="김학습"
              className={errors.name ? 'border-red-500' : ''}
            />
            {errors.name && <p className="text-red-500 text-sm mt-1">{errors.name}</p>}
          </div>

          <div>
            <Label htmlFor="email">이메일 *</Label>
            <Input
              id="email"
              type="email"
              value={data.email}
              onChange={(e) => onUpdate({ ...data, email: e.target.value })}
              placeholder="example@email.com"
              className={errors.email ? 'border-red-500' : ''}
            />
            {errors.email && <p className="text-red-500 text-sm mt-1">{errors.email}</p>}
          </div>

          <div>
            <Label>프로그래밍 경험 수준 *</Label>
            <div className="grid grid-cols-1 gap-2 mt-2">
              {experienceLevels.map((level) => (
                <label
                  key={level.value}
                  className={`flex items-center p-3 border rounded-lg cursor-pointer transition-colors ${
                    data.experience_level === level.value
                      ? 'border-blue-500 bg-blue-50'
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                >
                  <input
                    type="radio"
                    value={level.value}
                    checked={data.experience_level === level.value}
                    onChange={(e) => onUpdate({ ...data, experience_level: e.target.value })}
                    className="mr-3"
                  />
                  <span className="text-sm">{level.label}</span>
                </label>
              ))}
            </div>
            {errors.experience_level && (
              <p className="text-red-500 text-sm mt-1">{errors.experience_level}</p>
            )}
          </div>
        </div>

        <div className="flex justify-between mt-6">
          <Button variant="outline" onClick={onPrev}>
            <ArrowLeft className="w-4 h-4 mr-2" />
            이전
          </Button>
          <Button onClick={handleSubmit}>
            다음
            <ArrowRight className="w-4 h-4 ml-2" />
          </Button>
        </div>
      </CardContent>
    </Card>
  );
};

// 관심사 선택 단계
const InterestsStep = ({ data, onUpdate, onNext, onPrev, stepInfo }) => {
  const interests = [
    { id: 'web', label: '웹 개발', icon: '🌐' },
    { id: 'mobile', label: '모바일 앱', icon: '📱' },
    { id: 'ai', label: '인공지능', icon: '🤖' },
    { id: 'data', label: '데이터 사이언스', icon: '📊' },
    { id: 'game', label: '게임 개발', icon: '🎮' },
    { id: 'backend', label: '백엔드 개발', icon: '⚙️' },
    { id: 'frontend', label: '프론트엔드', icon: '🎨' },
    { id: 'devops', label: 'DevOps', icon: '🚀' }
  ];

  const goals = [
    { id: 'job', label: '취업 준비' },
    { id: 'skill', label: '기술 향상' },
    { id: 'project', label: '프로젝트 완성' },
    { id: 'certification', label: '자격증 취득' },
    { id: 'hobby', label: '취미 학습' }
  ];

  const toggleInterest = (interestId) => {
    const newInterests = data.interests.includes(interestId)
      ? data.interests.filter(id => id !== interestId)
      : [...data.interests, interestId];
    
    onUpdate({ ...data, interests: newInterests });
  };

  const toggleGoal = (goalId) => {
    const newGoals = data.goals.includes(goalId)
      ? data.goals.filter(id => id !== goalId)
      : [...data.goals, goalId];
    
    onUpdate({ ...data, goals: newGoals });
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>{stepInfo.title}</CardTitle>
        <CardDescription>{stepInfo.description}</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-6">
          <div>
            <Label className="text-base font-medium">관심 있는 개발 분야 (복수 선택 가능)</Label>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mt-3">
              {interests.map((interest) => (
                <button
                  key={interest.id}
                  onClick={() => toggleInterest(interest.id)}
                  className={`p-3 text-center border rounded-lg transition-colors ${
                    data.interests.includes(interest.id)
                      ? 'border-blue-500 bg-blue-50 text-blue-900'
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                >
                  <div className="text-2xl mb-1">{interest.icon}</div>
                  <div className="text-sm font-medium">{interest.label}</div>
                </button>
              ))}
            </div>
          </div>

          <div>
            <Label className="text-base font-medium">학습 목표 (복수 선택 가능)</Label>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-2 mt-3">
              {goals.map((goal) => (
                <button
                  key={goal.id}
                  onClick={() => toggleGoal(goal.id)}
                  className={`p-3 text-left border rounded-lg transition-colors ${
                    data.goals.includes(goal.id)
                      ? 'border-green-500 bg-green-50 text-green-900'
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                >
                  <div className="flex items-center">
                    {data.goals.includes(goal.id) ? (
                      <CheckCircle className="w-5 h-5 mr-2 text-green-600" />
                    ) : (
                      <Circle className="w-5 h-5 mr-2 text-gray-400" />
                    )}
                    <span className="font-medium">{goal.label}</span>
                  </div>
                </button>
              ))}
            </div>
          </div>
        </div>

        <div className="flex justify-between mt-6">
          <Button variant="outline" onClick={onPrev}>
            <ArrowLeft className="w-4 h-4 mr-2" />
            이전
          </Button>
          <Button onClick={onNext}>
            다음
            <ArrowRight className="w-4 h-4 ml-2" />
          </Button>
        </div>
      </CardContent>
    </Card>
  );
};

// AI 기능 소개 단계
const AIFeaturesStep = ({ data, onUpdate, onNext, onPrev, stepInfo }) => {
  const aiFeatures = [
    {
      id: 'analysis',
      title: '심층 학습 분석',
      description: 'AI가 학습 패턴을 분석하여 개인화된 인사이트 제공',
      icon: Brain,
      benefits: ['학습자 유형 분류', '강점/약점 분석', '개선 방안 제시']
    },
    {
      id: 'mentor',
      title: 'AI 멘토링',
      description: '24/7 개인 학습 코치와 실시간 대화',
      icon: MessageCircle,
      benefits: ['실시간 질문 답변', '동기 부여', '학습 가이드']
    },
    {
      id: 'difficulty',
      title: '적응형 난이도',
      description: '실시간 성과 분석을 통한 난이도 자동 조절',
      icon: Target,
      benefits: ['개인 맞춤 난이도', '학습 효율 극대화', '최적 도전 수준']
    },
    {
      id: 'code_review',
      title: 'AI 코드 리뷰',
      description: '전문적인 코드 검토와 개선 방안 제시',
      icon: Code,
      benefits: ['코드 품질 평가', '보안 취약점 검사', '개선 권장사항']
    }
  ];

  const toggleFeature = (featureId) => {
    const newFeatures = data.ai_features_interest.includes(featureId)
      ? data.ai_features_interest.filter(id => id !== featureId)
      : [...data.ai_features_interest, featureId];
    
    onUpdate({ ...data, ai_features_interest: newFeatures });
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>{stepInfo.title}</CardTitle>
        <CardDescription>{stepInfo.description}</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {aiFeatures.map((feature) => {
            const Icon = feature.icon;
            const isSelected = data.ai_features_interest.includes(feature.id);
            
            return (
              <div
                key={feature.id}
                className={`p-4 border rounded-lg cursor-pointer transition-all ${
                  isSelected
                    ? 'border-blue-500 bg-blue-50'
                    : 'border-gray-200 hover:border-gray-300'
                }`}
                onClick={() => toggleFeature(feature.id)}
              >
                <div className="flex items-start space-x-3">
                  <div className={`p-2 rounded-lg ${
                    isSelected ? 'bg-blue-200' : 'bg-gray-100'
                  }`}>
                    <Icon className={`w-5 h-5 ${
                      isSelected ? 'text-blue-600' : 'text-gray-600'
                    }`} />
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center justify-between">
                      <h3 className="font-semibold">{feature.title}</h3>
                      {isSelected && (
                        <CheckCircle className="w-5 h-5 text-blue-600" />
                      )}
                    </div>
                    <p className="text-gray-600 text-sm mt-1">{feature.description}</p>
                    <div className="flex flex-wrap gap-1 mt-2">
                      {feature.benefits.map((benefit, index) => (
                        <Badge key={index} variant="secondary" className="text-xs">
                          {benefit}
                        </Badge>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            );
          })}
        </div>

        <div className="bg-yellow-50 p-4 rounded-lg mt-4">
          <p className="text-sm text-yellow-800">
            💡 <strong>팁:</strong> 관심 있는 기능을 선택하시면 우선적으로 소개해드립니다.
            모든 기능은 언제든 사용하실 수 있습니다.
          </p>
        </div>

        <div className="flex justify-between mt-6">
          <Button variant="outline" onClick={onPrev}>
            <ArrowLeft className="w-4 h-4 mr-2" />
            이전
          </Button>
          <Button onClick={onNext}>
            다음
            <ArrowRight className="w-4 h-4 ml-2" />
          </Button>
        </div>
      </CardContent>
    </Card>
  );
};

// 베타 동의 단계
const BetaAgreementStep = ({ data, onUpdate, onNext, onPrev, stepInfo }) => {
  return (
    <Card>
      <CardHeader>
        <CardTitle>{stepInfo.title}</CardTitle>
        <CardDescription>{stepInfo.description}</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          <div className="bg-blue-50 p-4 rounded-lg">
            <h3 className="font-semibold text-blue-900 mb-2">🎯 베타 테스터 역할</h3>
            <ul className="text-sm text-blue-800 space-y-1">
              <li>• AI 기능을 사용하며 피드백 제공</li>
              <li>• 버그나 개선사항 발견 시 신고</li>
              <li>• 학습 경험에 대한 솔직한 의견 공유</li>
              <li>• 새로운 기능에 대한 제안 환영</li>
            </ul>
          </div>

          <div className="bg-green-50 p-4 rounded-lg">
            <h3 className="font-semibold text-green-900 mb-2">🎁 베타 테스터 혜택</h3>
            <ul className="text-sm text-green-800 space-y-1">
              <li>• 정식 출시 시 50% 할인 혜택</li>
              <li>• 프리미엄 AI 기능 무료 이용</li>
              <li>• 새 기능 우선 체험 기회</li>
              <li>• 개발진과 직접 소통 채널</li>
            </ul>
          </div>

          <div className="border p-4 rounded-lg">
            <h3 className="font-semibold mb-2">📋 베타 테스트 약관</h3>
            <div className="text-sm text-gray-700 space-y-2 max-h-32 overflow-y-auto">
              <p>1. 베타 버전은 개발 중인 소프트웨어로 예상치 못한 오류가 발생할 수 있습니다.</p>
              <p>2. 피드백 제공은 의무가 아니지만 권장됩니다.</p>
              <p>3. 학습 데이터는 서비스 개선 목적으로만 사용됩니다.</p>
              <p>4. 개인정보는 관련 법령에 따라 안전하게 보호됩니다.</p>
              <p>5. 베타 테스트 기간은 약 4주입니다.</p>
            </div>
          </div>

          <label className="flex items-start space-x-3 cursor-pointer">
            <input
              type="checkbox"
              checked={data.beta_feedback_consent}
              onChange={(e) => onUpdate({ ...data, beta_feedback_consent: e.target.checked })}
              className="mt-1"
            />
            <span className="text-sm">
              베타 테스트 약관에 동의하며, 학습 데이터 수집 및 피드백 요청에 협조하겠습니다.
            </span>
          </label>
        </div>

        <div className="flex justify-between mt-6">
          <Button variant="outline" onClick={onPrev}>
            <ArrowLeft className="w-4 h-4 mr-2" />
            이전
          </Button>
          <Button 
            onClick={onNext} 
            disabled={!data.beta_feedback_consent}
          >
            동의하고 계속
            <ArrowRight className="w-4 h-4 ml-2" />
          </Button>
        </div>
      </CardContent>
    </Card>
  );
};

// 완료 단계
const CompleteStep = ({ data, onComplete, stepInfo }) => {
  return (
    <Card className="text-center">
      <CardHeader>
        <div className="flex justify-center mb-4">
          <div className="w-16 h-16 bg-gradient-to-r from-green-500 to-blue-500 rounded-full flex items-center justify-center">
            <CheckCircle className="w-8 h-8 text-white" />
          </div>
        </div>
        <CardTitle className="text-2xl">{stepInfo.title}</CardTitle>
        <CardDescription className="text-lg">{stepInfo.description}</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          <div className="bg-gradient-to-r from-blue-50 to-purple-50 p-6 rounded-lg">
            <h3 className="font-semibold text-blue-900 mb-3">🎉 온보딩 완료!</h3>
            <div className="text-sm text-blue-800 space-y-2">
              <p><strong>이름:</strong> {data.name}</p>
              <p><strong>경험 수준:</strong> {data.experience_level}</p>
              <p><strong>관심 분야:</strong> {data.interests.length}개 선택</p>
              <p><strong>AI 기능 관심:</strong> {data.ai_features_interest.length}개 선택</p>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4 text-sm">
            <div className="bg-green-50 p-3 rounded-lg">
              <Gift className="w-6 h-6 text-green-600 mx-auto mb-2" />
              <p className="font-medium text-green-900">베타 혜택 활성화</p>
            </div>
            <div className="bg-blue-50 p-3 rounded-lg">
              <Star className="w-6 h-6 text-blue-600 mx-auto mb-2" />
              <p className="font-medium text-blue-900">AI 기능 접근 권한</p>
            </div>
          </div>

          <Button onClick={onComplete} className="w-full" size="lg">
            <Sparkles className="w-4 h-4 mr-2" />
            AI 학습 시작하기
          </Button>

          <p className="text-xs text-gray-600">
            궁금한 점이 있으시면 언제든 AI 멘토에게 물어보세요!
          </p>
        </div>
      </CardContent>
    </Card>
  );
};

export default BetaOnboarding;
