import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
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
  Star,
  PartyPopper
} from 'lucide-react';

// --- UI Components ---
// shadcn/ui의 컴포넌트를 기반으로 간단하게 재구성했습니다.
// 실제 프로젝트에서는 shadcn/ui를 직접 설치하여 사용하시는 것을 권장합니다.
const Card = ({ children, className = '' }) => (
  <div className={`bg-white rounded-2xl shadow-2xl shadow-blue-500/10 overflow-hidden ${className}`}>
    {children}
  </div>
);
const CardHeader = ({ children, className = '' }) => <div className={`p-8 ${className}`}>{children}</div>;
const CardContent = ({ children, className = '' }) => <div className={`p-8 pt-0 ${className}`}>{children}</div>;
const CardTitle = ({ children, className = '' }) => <h2 className={`text-3xl font-bold text-gray-800 ${className}`}>{children}</h2>;
const CardDescription = ({ children, className = '' }) => <p className={`text-gray-500 mt-2 ${className}`}>{children}</p>;

const Button = ({ children, onClick, variant = 'default', size = 'default', disabled = false, className = '' }) => {
  const baseClasses = 'inline-flex items-center justify-center rounded-lg font-semibold transition-all duration-300 focus:outline-none focus:ring-2 focus:ring-offset-2';
  const sizeClasses = {
    default: 'px-6 py-3 text-base',
    lg: 'px-8 py-4 text-lg',
  };
  const variantClasses = {
    default: 'bg-blue-600 text-white hover:bg-blue-700 focus:ring-blue-500 disabled:bg-blue-300',
    outline: 'border border-gray-300 bg-transparent text-gray-700 hover:bg-gray-100 focus:ring-gray-400',
  };
  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className={`${baseClasses} ${sizeClasses[size]} ${variantClasses[variant]} ${className}`}
    >
      {children}
    </button>
  );
};

const Input = ({ id, value, onChange, placeholder, type = 'text', className = '' }) => (
  <input
    id={id}
    type={type}
    value={value}
    onChange={onChange}
    placeholder={placeholder}
    className={`w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors ${className}`}
  />
);
const Label = ({ htmlFor, children, className = '' }) => <label htmlFor={htmlFor} className={`block text-sm font-medium text-gray-700 mb-2 ${className}`}>{children}</label>;
const Badge = ({ children, variant = 'default', className = '' }) => {
    const variantClasses = {
        default: 'bg-blue-100 text-blue-800',
        secondary: 'bg-gray-100 text-gray-800'
    }
    return <span className={`px-2.5 py-0.5 rounded-full text-xs font-semibold ${variantClasses[variant]} ${className}`}>{children}</span>
};
const Progress = ({ value, className = '' }) => (
  <div className={`w-full bg-gray-200 rounded-full h-2.5 overflow-hidden ${className}`}>
    <motion.div
      className="bg-blue-600 h-2.5 rounded-full"
      initial={{ width: 0 }}
      animate={{ width: `${value}%` }}
      transition={{ duration: 0.5, ease: 'easeInOut' }}
    />
  </div>
);

// --- Onboarding Steps ---
const steps = [
  { id: 'welcome', title: '베타 테스터 환영', description: 'AI 기반 개인화 학습 플랫폼에 오신 것을 환영합니다!' },
  { id: 'profile', title: '프로필 설정', description: '개인화된 학습 경험을 위한 기본 정보를 입력해주세요' },
  { id: 'interests', title: '학습 관심사', description: '관심 있는 학습 영역을 선택해주세요' },
  { id: 'ai-features', title: 'AI 기능 소개', description: '사용할 수 있는 AI 기능들을 확인해보세요' },
  { id: 'beta-agreement', title: '베타 테스트 동의', description: '베타 테스트 참여 조건을 확인해주세요' },
  { id: 'complete', title: '설정 완료', description: '이제 AI 기반 학습을 시작할 준비가 되었습니다!' }
];

const stepVariants = {
  hidden: { opacity: 0, x: 50 },
  visible: { opacity: 1, x: 0 },
  exit: { opacity: 0, x: -50 },
};

const WelcomeStep = ({ onNext, stepInfo }) => (
  <motion.div variants={stepVariants} initial="hidden" animate="visible" exit="exit">
    <Card className="text-center">
      <CardHeader>
        <div className="flex justify-center mb-6">
          <div className="w-20 h-20 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center shadow-lg shadow-blue-500/30">
            <Sparkles className="w-10 h-10 text-white" />
          </div>
        </div>
        <CardTitle>{stepInfo.title}</CardTitle>
        <CardDescription className="text-lg max-w-md mx-auto">{stepInfo.description}</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-6">
          <div className="bg-blue-50/50 border border-blue-200 p-6 rounded-xl">
            <h3 className="font-bold text-blue-900 mb-3 text-lg flex items-center justify-center"><Target className="w-5 h-5 mr-2"/> 베타 테스트 특전</h3>
            <ul className="text-sm text-blue-800 space-y-2 text-left">
              {['최신 AI 기능 우선 체험', '개인화된 학습 분석 무료 제공', '24/7 AI 멘토링 시스템 이용', '피드백 제공 시 정식 버전 할인 혜택'].map(item => (
                <li key={item} className="flex items-start"><CheckCircle className="w-4 h-4 mr-2 mt-0.5 text-blue-500 flex-shrink-0"/><span>{item}</span></li>
              ))}
            </ul>
          </div>
          <Button onClick={onNext} size="lg" className="w-full shadow-lg shadow-blue-500/30">
            시작하기 <ArrowRight className="w-5 h-5 ml-2" />
          </Button>
        </div>
      </CardContent>
    </Card>
  </motion.div>
);

const ProfileStep = ({ data, onUpdate, onNext, onPrev, stepInfo }) => {
  const [errors, setErrors] = useState({});
  const handleSubmit = () => {
    const newErrors = {};
    if (!data.name.trim()) newErrors.name = '이름을 입력해주세요';
    if (!/^\S+@\S+\.\S+$/.test(data.email)) newErrors.email = '유효한 이메일 주소를 입력해주세요';
    if (!data.experience_level) newErrors.experience_level = '경험 수준을 선택해주세요';
    setErrors(newErrors);
    if (Object.keys(newErrors).length === 0) onNext();
  };

  const experienceLevels = [
    { value: 'beginner', label: '초급', description: '프로그래밍을 처음 배웁니다' },
    { value: 'intermediate', label: '중급', description: '기본 개념을 알고 있습니다' },
    { value: 'advanced', label: '고급', description: '실무 경험이 있습니다' },
    { value: 'expert', label: '전문가', description: '다른 사람을 가르칠 수 있습니다' }
  ];

  return (
    <motion.div variants={stepVariants} initial="hidden" animate="visible" exit="exit">
      <Card>
        <CardHeader>
          <CardTitle>{stepInfo.title}</CardTitle>
          <CardDescription>{stepInfo.description}</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-6">
            <div>
              <Label htmlFor="name">이름 *</Label>
              <Input id="name" value={data.name} onChange={(e) => onUpdate({ ...data, name: e.target.value })} placeholder="김학습" className={errors.name ? 'border-red-500' : ''} />
              {errors.name && <p className="text-red-500 text-sm mt-1">{errors.name}</p>}
            </div>
            <div>
              <Label htmlFor="email">이메일 *</Label>
              <Input id="email" type="email" value={data.email} onChange={(e) => onUpdate({ ...data, email: e.target.value })} placeholder="example@email.com" className={errors.email ? 'border-red-500' : ''} />
              {errors.email && <p className="text-red-500 text-sm mt-1">{errors.email}</p>}
            </div>
            <div>
              <Label>프로그래밍 경험 수준 *</Label>
              <div className="space-y-3 mt-2">
                {experienceLevels.map((level) => (
                  <label key={level.value} className={`flex items-center p-4 border rounded-lg cursor-pointer transition-all duration-300 ${data.experience_level === level.value ? 'border-blue-500 bg-blue-50 shadow-md' : 'border-gray-200 hover:border-gray-400'}`}>
                    <input type="radio" value={level.value} checked={data.experience_level === level.value} onChange={(e) => onUpdate({ ...data, experience_level: e.target.value })} className="sr-only" />
                    <div className={`w-5 h-5 rounded-full border-2 flex items-center justify-center mr-4 ${data.experience_level === level.value ? 'border-blue-500 bg-blue-500' : 'border-gray-300'}`}>
                      {data.experience_level === level.value && <div className="w-2 h-2 bg-white rounded-full"></div>}
                    </div>
                    <div>
                      <span className="font-semibold text-gray-800">{level.label}</span>
                      <p className="text-sm text-gray-500">{level.description}</p>
                    </div>
                  </label>
                ))}
              </div>
              {errors.experience_level && <p className="text-red-500 text-sm mt-1">{errors.experience_level}</p>}
            </div>
          </div>
          <div className="flex justify-between mt-8">
            <Button variant="outline" onClick={onPrev}><ArrowLeft className="w-4 h-4 mr-2" /> 이전</Button>
            <Button onClick={handleSubmit}>다음 <ArrowRight className="w-4 h-4 ml-2" /></Button>
          </div>
        </CardContent>
      </Card>
    </motion.div>
  );
};

const InterestsStep = ({ data, onUpdate, onNext, onPrev, stepInfo }) => {
  const interests = [
    { id: 'web', label: '웹 개발', icon: '🌐' }, { id: 'mobile', label: '모바일 앱', icon: '📱' },
    { id: 'ai', label: '인공지능', icon: '🤖' }, { id: 'data', label: '데이터 사이언스', icon: '📊' },
    { id: 'game', label: '게임 개발', icon: '🎮' }, { id: 'backend', label: '백엔드', icon: '⚙️' },
    { id: 'frontend', label: '프론트엔드', icon: '🎨' }, { id: 'devops', label: 'DevOps', icon: '🚀' }
  ];
  const goals = [
    { id: 'job', label: '취업 준비' }, { id: 'skill', label: '기술 향상' },
    { id: 'project', label: '프로젝트 완성' }, { id: 'hobby', label: '취미 학습' }
  ];

  const toggleSelection = (key, value) => {
    const currentValues = data[key] || [];
    const newValues = currentValues.includes(value)
      ? currentValues.filter(v => v !== value)
      : [...currentValues, value];
    onUpdate({ ...data, [key]: newValues });
  };

  return (
    <motion.div variants={stepVariants} initial="hidden" animate="visible" exit="exit">
      <Card>
        <CardHeader>
          <CardTitle>{stepInfo.title}</CardTitle>
          <CardDescription>{stepInfo.description}</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-8">
            <div>
              <Label className="text-lg font-semibold">관심 있는 개발 분야 (복수 선택 가능)</Label>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-4">
                {interests.map((interest) => (
                  <button key={interest.id} onClick={() => toggleSelection('interests', interest.id)} className={`p-4 text-center border rounded-xl transition-all duration-300 transform hover:-translate-y-1 ${data.interests.includes(interest.id) ? 'border-blue-500 bg-blue-50 text-blue-900 shadow-lg' : 'border-gray-200 hover:border-gray-400 hover:shadow-md'}`}>
                    <div className="text-4xl mb-2">{interest.icon}</div>
                    <div className="text-sm font-bold">{interest.label}</div>
                  </button>
                ))}
              </div>
            </div>
            <div>
              <Label className="text-lg font-semibold">학습 목표 (복수 선택 가능)</Label>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3 mt-4">
                {goals.map((goal) => (
                  <button key={goal.id} onClick={() => toggleSelection('goals', goal.id)} className={`p-4 text-left border rounded-lg transition-colors flex items-center ${data.goals.includes(goal.id) ? 'border-blue-500 bg-blue-50' : 'border-gray-200 hover:border-gray-300'}`}>
                    {data.goals.includes(goal.id) ? <CheckCircle className="w-6 h-6 mr-3 text-blue-600" /> : <Circle className="w-6 h-6 mr-3 text-gray-300" />}
                    <span className="font-semibold text-gray-800">{goal.label}</span>
                  </button>
                ))}
              </div>
            </div>
          </div>
          <div className="flex justify-between mt-8">
            <Button variant="outline" onClick={onPrev}><ArrowLeft className="w-4 h-4 mr-2" /> 이전</Button>
            <Button onClick={onNext}>다음 <ArrowRight className="w-4 h-4 ml-2" /></Button>
          </div>
        </CardContent>
      </Card>
    </motion.div>
  );
};

const AIFeaturesStep = ({ data, onUpdate, onNext, onPrev, stepInfo }) => {
  const aiFeatures = [
    { id: 'analysis', title: '심층 학습 분석', description: 'AI가 학습 패턴을 분석하여 개인화된 인사이트 제공', icon: Brain },
    { id: 'mentor', title: 'AI 멘토링', description: '24/7 개인 학습 코치와 실시간 대화', icon: MessageCircle },
    { id: 'difficulty', title: '적응형 난이도', description: '실시간 성과 분석을 통한 난이도 자동 조절', icon: Target },
    { id: 'code_review', title: 'AI 코드 리뷰', description: '전문적인 코드 검토와 개선 방안 제시', icon: Code }
  ];

  const toggleFeature = (featureId) => {
    const newFeatures = data.ai_features_interest.includes(featureId)
      ? data.ai_features_interest.filter(id => id !== featureId)
      : [...data.ai_features_interest, featureId];
    onUpdate({ ...data, ai_features_interest: newFeatures });
  };

  return (
    <motion.div variants={stepVariants} initial="hidden" animate="visible" exit="exit">
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
                <div key={feature.id} onClick={() => toggleFeature(feature.id)} className={`p-5 border rounded-xl cursor-pointer transition-all duration-300 ${isSelected ? 'border-blue-500 bg-blue-50 shadow-lg' : 'border-gray-200 hover:border-gray-400 hover:shadow-md'}`}>
                  <div className="flex items-start space-x-4">
                    <div className={`p-3 rounded-lg flex-shrink-0 ${isSelected ? 'bg-blue-200' : 'bg-gray-100'}`}>
                      <Icon className={`w-6 h-6 ${isSelected ? 'text-blue-600' : 'text-gray-600'}`} />
                    </div>
                    <div className="flex-1">
                      <h3 className="font-bold text-lg text-gray-800">{feature.title}</h3>
                      <p className="text-gray-600 text-sm mt-1">{feature.description}</p>
                    </div>
                    {isSelected && <CheckCircle className="w-6 h-6 text-blue-600 flex-shrink-0" />}
                  </div>
                </div>
              );
            })}
          </div>
          <div className="flex justify-between mt-8">
            <Button variant="outline" onClick={onPrev}><ArrowLeft className="w-4 h-4 mr-2" /> 이전</Button>
            <Button onClick={onNext}>다음 <ArrowRight className="w-4 h-4 ml-2" /></Button>
          </div>
        </CardContent>
      </Card>
    </motion.div>
  );
};

const BetaAgreementStep = ({ data, onUpdate, onNext, onPrev, stepInfo }) => (
  <motion.div variants={stepVariants} initial="hidden" animate="visible" exit="exit">
    <Card>
      <CardHeader>
        <CardTitle>{stepInfo.title}</CardTitle>
        <CardDescription>{stepInfo.description}</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-6">
          <div className="border p-6 rounded-lg bg-gray-50">
            <h3 className="font-bold text-lg mb-3">📋 베타 테스트 약관</h3>
            <div className="text-sm text-gray-600 space-y-2 max-h-32 overflow-y-auto pr-2">
              <p>1. 베타 버전은 개발 중인 소프트웨어로 예상치 못한 오류가 발생할 수 있습니다.</p>
              <p>2. 피드백 제공은 의무가 아니지만, 서비스 개선을 위해 적극적인 참여를 권장합니다.</p>
              <p>3. 수집된 학습 데이터는 개인을 식별할 수 없는 형태로 서비스 개선 및 연구 목적으로만 사용됩니다.</p>
              <p>4. 개인정보는 관련 법령에 따라 안전하게 보호되며, 동의 없이 제3자에게 제공되지 않습니다.</p>
              <p>5. 베타 테스트 기간은 별도 공지 시까지이며, 사전 안내 후 종료될 수 있습니다.</p>
            </div>
          </div>
          <label className="flex items-start space-x-3 cursor-pointer p-4 rounded-lg hover:bg-gray-50 transition-colors">
            <input type="checkbox" checked={data.beta_feedback_consent} onChange={(e) => onUpdate({ ...data, beta_feedback_consent: e.target.checked })} className="mt-1 h-5 w-5 text-blue-600 border-gray-300 rounded focus:ring-blue-500" />
            <span className="text-sm text-gray-700">
              베타 테스트 약관에 동의하며, 서비스 개선을 위한 학습 데이터 수집 및 피드백 요청에 협조하겠습니다.
            </span>
          </label>
        </div>
        <div className="flex justify-between mt-8">
          <Button variant="outline" onClick={onPrev}><ArrowLeft className="w-4 h-4 mr-2" /> 이전</Button>
          <Button onClick={onNext} disabled={!data.beta_feedback_consent}>동의하고 계속 <ArrowRight className="w-4 h-4 ml-2" /></Button>
        </div>
      </CardContent>
    </Card>
  </motion.div>
);

const CompleteStep = ({ data, onComplete, stepInfo }) => {
    const getExperienceLabel = (value) => {
        const levels = {
            beginner: '초급', intermediate: '중급', advanced: '고급', expert: '전문가'
        };
        return levels[value] || 'N/A';
    }
    return (
      <motion.div variants={stepVariants} initial="hidden" animate="visible" exit="exit">
        <Card className="text-center">
          <CardHeader>
            <div className="flex justify-center mb-6">
              <div className="w-20 h-20 bg-gradient-to-br from-green-400 to-blue-500 rounded-full flex items-center justify-center shadow-lg shadow-green-500/30">
                <PartyPopper className="w-10 h-10 text-white" />
              </div>
            </div>
            <CardTitle>{stepInfo.title}</CardTitle>
            <CardDescription className="text-lg">{stepInfo.description}</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-6">
              <div className="bg-gradient-to-r from-blue-50 to-green-50 p-6 rounded-xl border border-gray-200">
                <h3 className="font-bold text-gray-800 mb-4">"{data.name}"님을 위한 맞춤 설정 요약</h3>
                <div className="text-sm text-gray-700 space-y-2 text-left">
                  <p><strong>경험 수준:</strong> <Badge>{getExperienceLabel(data.experience_level)}</Badge></p>
                  <p><strong>관심 분야:</strong> {data.interests.length > 0 ? data.interests.map(i => <Badge key={i} className="mr-1">{i}</Badge>) : '선택 안함'}</p>
                  <p><strong>학습 목표:</strong> {data.goals.length > 0 ? data.goals.map(g => <Badge key={g} className="mr-1">{g}</Badge>) : '선택 안함'}</p>
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div className="bg-green-100/70 p-4 rounded-lg text-green-900"><Gift className="w-6 h-6 mx-auto mb-2" /><p className="font-semibold">베타 혜택 활성화</p></div>
                <div className="bg-blue-100/70 p-4 rounded-lg text-blue-900"><Star className="w-6 h-6 mx-auto mb-2" /><p className="font-semibold">AI 기능 접근 권한</p></div>
              </div>
              <Button onClick={onComplete} size="lg" className="w-full bg-green-500 hover:bg-green-600 focus:ring-green-400 shadow-lg shadow-green-500/30">
                <Sparkles className="w-5 h-5 mr-2" /> AI 학습 시작하기
              </Button>
            </div>
          </CardContent>
        </Card>
      </motion.div>
    );
};

const BetaOnboarding = ({ onComplete }) => {
  const [currentStep, setCurrentStep] = useState(0);
  const [formData, setFormData] = useState({
    name: '', email: '', experience_level: '',
    interests: [], goals: [],
    beta_feedback_consent: false, ai_features_interest: []
  });

  const handleNext = () => currentStep < steps.length - 1 && setCurrentStep(currentStep + 1);
  const handlePrev = () => currentStep > 0 && setCurrentStep(currentStep - 1);
  const [submitting, setSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState(null);

  const handleComplete = async () => {
    setSubmitError(null);
    setSubmitting(true);
    const payload = {
      name: formData.name,
      email: formData.email,
      experience_level: formData.experience_level,
      interests: formData.interests,
      goals: formData.goals,
      beta_feedback_consent: formData.beta_feedback_consent,
      ai_features_interest: formData.ai_features_interest,
    };
    try {
      // lazy import to avoid circular deps
      const api = (await import('../../services/apiClient')).default;
      const res = await api.registerBetaTester(payload);
      setSubmitting(false);
      if (onComplete) onComplete(res);
    } catch (err) {
      console.error('Onboarding submit error', err);
      setSubmitError(err.message || 'Failed to register');
      setSubmitting(false);
    }
  };

  const stepComponents = {
      welcome: WelcomeStep,
      profile: ProfileStep,
      interests: InterestsStep,
      'ai-features': AIFeaturesStep, // Corrected Key
      'beta-agreement': BetaAgreementStep,
      complete: CompleteStep,
  }

  const CurrentStepComponent = stepComponents[steps[currentStep].id];
  const progress = ((currentStep) / (steps.length - 1)) * 100;

  return (
    <div className="min-h-screen bg-gray-50 font-sans flex items-center justify-center p-4">
      <div className="w-full max-w-2xl mx-auto">
        <div className="mb-8">
            <div className="flex justify-between items-center mb-2">
                <span className="text-sm font-semibold text-gray-600">온보딩 진행률</span>
                <span className="text-sm font-bold text-blue-600">{currentStep + 1} / {steps.length}</span>
            </div>
            <Progress value={progress} />
        </div>
        
        <AnimatePresence mode="wait">
          <CurrentStepComponent
            key={steps[currentStep].id}
            data={formData}
            onUpdate={setFormData}
            onNext={handleNext}
            onPrev={handlePrev}
            onComplete={handleComplete}
            stepInfo={steps[currentStep]}
          />
        </AnimatePresence>
      </div>
    </div>
  );
};


// App component to render the onboarding flow
export default function App() {
  const handleOnboardingComplete = (formData) => {
    // In a real app, you'd likely navigate to the main dashboard
    // For this example, we'll just show an alert.
    // Note: alert() is not ideal for production apps. Consider a modal.
    alert("온보딩이 완료되었습니다! 데이터를 확인해보세요: " + JSON.stringify(formData, null, 2));
  };

  return <BetaOnboarding onComplete={handleOnboardingComplete} />;
}
