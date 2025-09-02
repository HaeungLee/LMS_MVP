import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import useAuthStore from '../../stores/authStore';
import { 
  CheckCircle, 
  ArrowRight, 
  ArrowLeft,
  Sparkles,
  Brain,
  Target,
  Code,
  User,
  Mail,
  Lock,
  BookOpen,
  Zap,
  Star
} from 'lucide-react';

const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || '') + '/api/v1';

// 간단한 UI 컴포넌트들
const Card = ({ children, className = '' }) => (
  <div className={`bg-white rounded-2xl shadow-xl shadow-blue-500/10 overflow-hidden ${className}`}>
    {children}
  </div>
);

const CardHeader = ({ children, className = '' }) => (
  <div className={`p-8 ${className}`}>{children}</div>
);

const CardContent = ({ children, className = '' }) => (
  <div className={`p-8 pt-0 ${className}`}>{children}</div>
);

const CardTitle = ({ children, className = '' }) => (
  <h2 className={`text-3xl font-bold text-gray-800 ${className}`}>{children}</h2>
);

const CardDescription = ({ children, className = '' }) => (
  <p className={`text-gray-500 mt-2 ${className}`}>{children}</p>
);

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
      className={`${baseClasses} ${sizeClasses[size]} ${variantClasses[variant]} ${disabled ? 'opacity-50 cursor-not-allowed' : ''} ${className}`}
    >
      {children}
    </button>
  );
};

const Input = ({ id, value, onChange, placeholder, type = 'text', className = '', required = false }) => (
  <input
    id={id}
    type={type}
    value={value}
    onChange={onChange}
    placeholder={placeholder}
    required={required}
    className={`w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors ${className}`}
  />
);

const Label = ({ htmlFor, children, className = '' }) => (
  <label htmlFor={htmlFor} className={`block text-sm font-medium text-gray-700 mb-2 ${className}`}>
    {children}
  </label>
);

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

// 단계 정의 (베타 용어 제거, 간소화)
const steps = [
  { 
    id: 'welcome', 
    title: 'AI 학습 플랫폼에 오신 것을 환영합니다!', 
    description: '개인화된 AI 학습 경험을 시작해보세요' 
  },
  { 
    id: 'basic-info', 
    title: '기본 정보를 알려주세요', 
    description: '계정 생성을 위한 필수 정보입니다' 
  },
  { 
    id: 'learning-profile', 
    title: '학습 프로필을 설정해주세요', 
    description: '더 나은 학습 경험을 위한 맞춤 설정입니다' 
  },
  { 
    id: 'interests', 
    title: '관심 분야를 선택해주세요', 
    description: '관심 있는 학습 영역을 알려주시면 맞춤 콘텐츠를 추천해드려요' 
  },
  { 
    id: 'complete', 
    title: '준비 완료!', 
    description: '이제 AI 맞춤 학습을 시작할 수 있습니다' 
  }
];

const stepVariants = {
  hidden: { opacity: 0, x: 50 },
  visible: { opacity: 1, x: 0 },
  exit: { opacity: 0, x: -50 },
};

// Step 1: 환영 페이지 (베타 강조 제거)
const WelcomeStep = ({ onNext, stepInfo }) => (
  <motion.div variants={stepVariants} initial="hidden" animate="visible" exit="exit">
    <Card className="text-center max-w-lg mx-auto">
      <CardHeader>
        <div className="flex justify-center mb-6">
          <div className="w-20 h-20 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center shadow-lg shadow-blue-500/30">
            <Sparkles className="w-10 h-10 text-white" />
          </div>
        </div>
        <CardTitle className="text-center">{stepInfo.title}</CardTitle>
        <CardDescription className="text-lg max-w-md mx-auto text-center">
          {stepInfo.description}
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-6">
          {/* AI 기능 강조 (베타 특전 대신) */}
          <div className="bg-blue-50/50 border border-blue-200 p-6 rounded-xl">
            <h3 className="font-bold text-blue-900 mb-3 text-lg flex items-center justify-center">
              <Target className="w-5 h-5 mr-2"/> AI 학습 기능
            </h3>
            <ul className="text-sm text-blue-800 space-y-2 text-left">
              {[
                'AI 멘토가 실시간으로 도움을 제공',
                '개인화된 학습 경로 자동 생성', 
                '코딩 실습과 즉시 피드백',
                '진도에 맞는 맞춤형 문제 추천'
              ].map(item => (
                <li key={item} className="flex items-start">
                  <CheckCircle className="w-4 h-4 mr-2 mt-0.5 text-blue-500 flex-shrink-0"/>
                  <span>{item}</span>
                </li>
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

// Step 2: 기본 정보 (기존 AuthRegister 내용 + 개선)
const BasicInfoStep = ({ data, onUpdate, onNext, onPrev, stepInfo, errors, setErrors }) => {
  const handleSubmit = () => {
    const newErrors = {};
    if (!data.email.trim()) newErrors.email = '이메일을 입력해주세요';
    else if (!/^\S+@\S+\.\S+$/.test(data.email)) newErrors.email = '유효한 이메일 주소를 입력해주세요';
    if (!data.password.trim()) newErrors.password = '비밀번호를 입력해주세요';
    else if (data.password.length < 6) newErrors.password = '비밀번호는 6자 이상이어야 합니다';
    if (!data.displayName.trim()) newErrors.displayName = '이름을 입력해주세요';
    
    setErrors(newErrors);
    if (Object.keys(newErrors).length === 0) onNext();
  };

  return (
    <motion.div variants={stepVariants} initial="hidden" animate="visible" exit="exit">
      <Card className="max-w-lg mx-auto">
        <CardHeader>
          <CardTitle>{stepInfo.title}</CardTitle>
          <CardDescription>{stepInfo.description}</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-6">
            <div>
              <Label htmlFor="email">이메일 주소 *</Label>
              <Input 
                id="email" 
                type="email"
                value={data.email} 
                onChange={(e) => onUpdate({ ...data, email: e.target.value })} 
                placeholder="example@email.com" 
                className={errors.email ? 'border-red-500' : ''}
                required
              />
              {errors.email && <p className="text-red-500 text-sm mt-1">{errors.email}</p>}
            </div>

            <div>
              <Label htmlFor="password">비밀번호 *</Label>
              <Input 
                id="password" 
                type="password"
                value={data.password} 
                onChange={(e) => onUpdate({ ...data, password: e.target.value })} 
                placeholder="6자 이상 입력하세요" 
                className={errors.password ? 'border-red-500' : ''}
                required
              />
              {errors.password && <p className="text-red-500 text-sm mt-1">{errors.password}</p>}
            </div>

            <div>
              <Label htmlFor="displayName">이름 *</Label>
              <Input 
                id="displayName" 
                value={data.displayName} 
                onChange={(e) => onUpdate({ ...data, displayName: e.target.value })} 
                placeholder="김학습" 
                className={errors.displayName ? 'border-red-500' : ''}
                required
              />
              {errors.displayName && <p className="text-red-500 text-sm mt-1">{errors.displayName}</p>}
            </div>
          </div>
          
          <div className="flex justify-between mt-8">
            <Button variant="outline" onClick={onPrev}>
              <ArrowLeft className="w-4 h-4 mr-2" /> 이전
            </Button>
            <Button onClick={handleSubmit}>
              다음 <ArrowRight className="w-4 h-4 ml-2" />
            </Button>
          </div>
        </CardContent>
      </Card>
    </motion.div>
  );
};

// Step 3: 학습 프로필 (간소화된 프로필 설정)
const LearningProfileStep = ({ data, onUpdate, onNext, onPrev, stepInfo }) => {
  const experienceLevels = [
    { value: 'beginner', label: '입문자', description: '프로그래밍을 처음 배웁니다', icon: <BookOpen className="w-5 h-5" /> },
    { value: 'intermediate', label: '초급자', description: '기본 문법을 알고 있습니다', icon: <Code className="w-5 h-5" /> },
    { value: 'advanced', label: '중급자', description: '프로젝트 경험이 있습니다', icon: <Zap className="w-5 h-5" /> },
    { value: 'expert', label: '고급자', description: '실무 경험이 풍부합니다', icon: <Star className="w-5 h-5" /> }
  ];

  const learningGoals = [
    { value: 'job-preparation', label: '취업 준비', icon: '💼' },
    { value: 'skill-improvement', label: '실력 향상', icon: '📈' },
    { value: 'hobby', label: '취미/흥미', icon: '🎯' },
    { value: 'career-change', label: '전직 준비', icon: '🔄' }
  ];

  return (
    <motion.div variants={stepVariants} initial="hidden" animate="visible" exit="exit">
      <Card className="max-w-2xl mx-auto">
        <CardHeader>
          <CardTitle>{stepInfo.title}</CardTitle>
          <CardDescription>{stepInfo.description}</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-8">
            {/* 프로그래밍 경험 수준 */}
            <div>
              <Label>프로그래밍 경험 수준</Label>
              <div className="grid grid-cols-2 gap-4 mt-3">
                {experienceLevels.map((level) => (
                  <label 
                    key={level.value} 
                    className={`flex items-center p-4 border rounded-lg cursor-pointer transition-all duration-300 ${
                      data.experienceLevel === level.value 
                        ? 'border-blue-500 bg-blue-50 shadow-md' 
                        : 'border-gray-200 hover:border-gray-400'
                    }`}
                  >
                    <input 
                      type="radio" 
                      value={level.value} 
                      checked={data.experienceLevel === level.value} 
                      onChange={(e) => onUpdate({ ...data, experienceLevel: e.target.value })} 
                      className="sr-only" 
                    />
                    <div className="mr-3 text-blue-600">
                      {level.icon}
                    </div>
                    <div>
                      <span className="font-semibold text-gray-800">{level.label}</span>
                      <p className="text-sm text-gray-500">{level.description}</p>
                    </div>
                  </label>
                ))}
              </div>
            </div>

            {/* 학습 목표 */}
            <div>
              <Label>학습 목표 (복수 선택 가능)</Label>
              <div className="grid grid-cols-2 gap-3 mt-3">
                {learningGoals.map((goal) => (
                  <label 
                    key={goal.value} 
                    className={`flex items-center p-3 border rounded-lg cursor-pointer transition-all duration-300 ${
                      data.learningGoals.includes(goal.value)
                        ? 'border-blue-500 bg-blue-50' 
                        : 'border-gray-200 hover:border-gray-400'
                    }`}
                  >
                    <input 
                      type="checkbox" 
                      value={goal.value} 
                      checked={data.learningGoals.includes(goal.value)} 
                      onChange={(e) => {
                        const goals = data.learningGoals.includes(goal.value)
                          ? data.learningGoals.filter(g => g !== goal.value)
                          : [...data.learningGoals, goal.value];
                        onUpdate({ ...data, learningGoals: goals });
                      }} 
                      className="sr-only" 
                    />
                    <span className="mr-2">{goal.icon}</span>
                    <span className="text-sm font-medium">{goal.label}</span>
                  </label>
                ))}
              </div>
            </div>
          </div>
          
          <div className="flex justify-between mt-8">
            <Button variant="outline" onClick={onPrev}>
              <ArrowLeft className="w-4 h-4 mr-2" /> 이전
            </Button>
            <Button onClick={onNext}>
              다음 <ArrowRight className="w-4 h-4 ml-2" />
            </Button>
          </div>
        </CardContent>
      </Card>
    </motion.div>
  );
};

// Step 4: 관심 분야 (간소화)
const InterestsStep = ({ data, onUpdate, onNext, onPrev, stepInfo }) => {
  const interests = [
    { id: 'python_basics', label: 'Python 기초', icon: '🐍' },
    { id: 'web_crawling', label: '웹 크롤링', icon: '🕷️' },
    { id: 'data_analysis', label: '데이터 분석', icon: '📊' },
    { id: 'web_development', label: '웹 개발', icon: '🌐' },
    { id: 'mobile_app', label: '모바일 앱', icon: '📱' },
    { id: 'ai_ml', label: '인공지능/머신러닝', icon: '🤖' },
    { id: 'game_development', label: '게임 개발', icon: '🎮' },
    { id: 'devops', label: 'DevOps', icon: '🚀' }
  ];

  return (
    <motion.div variants={stepVariants} initial="hidden" animate="visible" exit="exit">
      <Card className="max-w-2xl mx-auto">
        <CardHeader>
          <CardTitle>{stepInfo.title}</CardTitle>
          <CardDescription>{stepInfo.description}</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
            {interests.map((interest) => (
              <label 
                key={interest.id} 
                className={`flex flex-col items-center p-4 border rounded-lg cursor-pointer transition-all duration-300 ${
                  data.interests.includes(interest.id)
                    ? 'border-blue-500 bg-blue-50 shadow-md' 
                    : 'border-gray-200 hover:border-gray-400'
                }`}
              >
                <input 
                  type="checkbox" 
                  value={interest.id} 
                  checked={data.interests.includes(interest.id)} 
                  onChange={(e) => {
                    const updatedInterests = data.interests.includes(interest.id)
                      ? data.interests.filter(i => i !== interest.id)
                      : [...data.interests, interest.id];
                    onUpdate({ ...data, interests: updatedInterests });
                  }} 
                  className="sr-only" 
                />
                <span className="text-2xl mb-2">{interest.icon}</span>
                <span className="text-sm font-medium text-center">{interest.label}</span>
              </label>
            ))}
          </div>
          
          <div className="flex justify-between mt-8">
            <Button variant="outline" onClick={onPrev}>
              <ArrowLeft className="w-4 h-4 mr-2" /> 이전
            </Button>
            <Button onClick={onNext}>
              다음 <ArrowRight className="w-4 h-4 ml-2" />
            </Button>
          </div>
        </CardContent>
      </Card>
    </motion.div>
  );
};

// Step 5: 완료 및 계정 생성
const CompleteStep = ({ data, onSubmit, onPrev, stepInfo, loading, error }) => (
  <motion.div variants={stepVariants} initial="hidden" animate="visible" exit="exit">
    <Card className="text-center max-w-lg mx-auto">
      <CardHeader>
        <div className="flex justify-center mb-6">
          <div className="w-20 h-20 bg-gradient-to-br from-green-500 to-blue-600 rounded-full flex items-center justify-center shadow-lg shadow-green-500/30">
            <CheckCircle className="w-10 h-10 text-white" />
          </div>
        </div>
        <CardTitle>{stepInfo.title}</CardTitle>
        <CardDescription className="text-lg">{stepInfo.description}</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-6">
          {error && (
            <div className="bg-red-50 border border-red-200 p-4 rounded-lg">
              <p className="text-red-800 text-sm">{error}</p>
            </div>
          )}
          
          {/* 설정 요약 */}
          <div className="bg-gray-50 border border-gray-200 p-6 rounded-xl text-left">
            <h3 className="font-bold text-gray-800 mb-3">설정 요약</h3>
            <div className="space-y-2 text-sm text-gray-600">
              <p><strong>이름:</strong> {data.displayName}</p>
              <p><strong>이메일:</strong> {data.email}</p>
              <p><strong>경험 수준:</strong> {data.experienceLevel}</p>
              <p><strong>관심 분야:</strong> {data.interests.length}개 선택</p>
            </div>
          </div>

          <div className="flex gap-4">
            <Button variant="outline" onClick={onPrev} className="flex-1">
              <ArrowLeft className="w-4 h-4 mr-2" /> 수정
            </Button>
            <Button 
              onClick={onSubmit} 
              disabled={loading} 
              className="flex-1 shadow-lg shadow-green-500/30"
            >
              {loading ? '계정 생성 중...' : '계정 생성'}
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  </motion.div>
);

// 메인 컴포넌트
const UnifiedRegistration = () => {
  const navigate = useNavigate();
  const { fetchMe } = useAuthStore();
  
  const [currentStep, setCurrentStep] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [errors, setErrors] = useState({});
  
  const [userData, setUserData] = useState({
    // 기본 정보
    email: '',
    password: '',
    displayName: '',
    
    // 학습 프로필
    experienceLevel: 'beginner',
    learningGoals: [],
    
    // 관심 분야
    interests: [],
    
    // 동의 사항 (기존 베타 동의를 선택사항으로)
    feedbackConsent: false,
    analyticsConsent: true
  });

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

  const handleSubmit = async () => {
    setLoading(true);
    setError('');
    
    try {
      // 1. 기본 회원가입
      const registerRes = await fetch(`${API_BASE_URL}/auth/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({
          email: userData.email,
          password: userData.password,
          display_name: userData.displayName,
        }),
      });

      if (!registerRes.ok) {
        throw new Error('이미 사용 중인 이메일일 수 있습니다.');
      }

      // 2. 사용자 프로필 업데이트 (추가 정보 저장)
      // TODO: 나중에 프로필 API가 준비되면 학습 프로필 정보 저장

      // 3. 로그인 상태 확인
      await fetchMe();
      
      // 4. 메인 페이지로 리다이렉트
      navigate('/');
      
    } catch (err) {
      setError(err.message || '회원가입 중 오류가 발생했습니다.');
    } finally {
      setLoading(false);
    }
  };

  const currentStepData = steps[currentStep];
  const progress = ((currentStep + 1) / steps.length) * 100;

  const renderStep = () => {
    switch (currentStepData.id) {
      case 'welcome':
        return <WelcomeStep onNext={handleNext} stepInfo={currentStepData} />;
      
      case 'basic-info':
        return (
          <BasicInfoStep 
            data={userData} 
            onUpdate={setUserData} 
            onNext={handleNext} 
            onPrev={handlePrev} 
            stepInfo={currentStepData}
            errors={errors}
            setErrors={setErrors}
          />
        );
      
      case 'learning-profile':
        return (
          <LearningProfileStep 
            data={userData} 
            onUpdate={setUserData} 
            onNext={handleNext} 
            onPrev={handlePrev} 
            stepInfo={currentStepData} 
          />
        );
      
      case 'interests':
        return (
          <InterestsStep 
            data={userData} 
            onUpdate={setUserData} 
            onNext={handleNext} 
            onPrev={handlePrev} 
            stepInfo={currentStepData} 
          />
        );
      
      case 'complete':
        return (
          <CompleteStep 
            data={userData} 
            onSubmit={handleSubmit} 
            onPrev={handlePrev} 
            stepInfo={currentStepData}
            loading={loading}
            error={error}
          />
        );
      
      default:
        return null;
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 flex items-center justify-center p-4">
      <div className="w-full max-w-4xl">
        {/* 진행률 표시 */}
        <div className="mb-8">
          <div className="flex justify-between items-center mb-2">
            <span className="text-sm font-medium text-gray-600">
              단계 {currentStep + 1} / {steps.length}
            </span>
            <span className="text-sm font-medium text-gray-600">
              {Math.round(progress)}% 완료
            </span>
          </div>
          <Progress value={progress} />
        </div>

        {/* 단계별 컨텐츠 */}
        <AnimatePresence mode="wait">
          <motion.div key={currentStep}>
            {renderStep()}
          </motion.div>
        </AnimatePresence>
      </div>
    </div>
  );
};

export default UnifiedRegistration;
