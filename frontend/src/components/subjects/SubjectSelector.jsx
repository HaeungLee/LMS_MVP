import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { 
  SUBJECTS, 
  SUBJECT_ICONS, 
  SUBJECT_COLORS, 
  SUBJECT_DESCRIPTIONS,
  SUBJECT_TOPICS,
  RECOMMENDED_LEARNING_PATH
} from '../constants/subjects';
import { 
  BookOpen, 
  Play, 
  Star, 
  Clock, 
  Users,
  ChevronRight,
  Trophy,
  Target
} from 'lucide-react';

const SubjectCard = ({ subjectKey, subjectData, onSelect, userProgress = {} }) => {
  const navigate = useNavigate();
  const icon = SUBJECT_ICONS[subjectKey];
  const colors = SUBJECT_COLORS[subjectKey];
  const topics = SUBJECT_TOPICS[subjectKey] || {};
  const topicCount = Object.keys(topics).length;
  
  // 가상의 진행률 (실제로는 API에서 가져와야 함)
  const completedTopics = userProgress[subjectKey]?.completed || 0;
  const progressPercentage = topicCount > 0 ? (completedTopics / topicCount) * 100 : 0;
  
  const handleStartLearning = () => {
    navigate(`/quiz?subject=${subjectKey}`);
  };
  
  const handleViewDetails = () => {
    onSelect(subjectKey);
  };

  return (
    <Card className="hover:shadow-lg transition-all duration-300 border-2 hover:border-blue-200">
      <CardHeader className="pb-4">
        <div className="flex items-start justify-between">
          <div className="flex items-center space-x-3">
            <div 
              className="w-12 h-12 rounded-lg flex items-center justify-center text-2xl"
              style={{ backgroundColor: colors.background }}
            >
              {icon}
            </div>
            <div>
              <CardTitle className="text-lg">{SUBJECTS[subjectKey]}</CardTitle>
              <CardDescription className="text-sm">
                {SUBJECT_DESCRIPTIONS[subjectKey]}
              </CardDescription>
            </div>
          </div>
          <Badge variant="secondary">
            {topicCount}개 토픽
          </Badge>
        </div>
      </CardHeader>
      
      <CardContent className="space-y-4">
        {/* 진행률 */}
        <div>
          <div className="flex justify-between items-center mb-2">
            <span className="text-sm text-gray-600">학습 진행률</span>
            <span className="text-sm font-medium">{progressPercentage.toFixed(0)}%</span>
          </div>
          <Progress value={progressPercentage} className="h-2" />
          <div className="flex justify-between text-xs text-gray-500 mt-1">
            <span>{completedTopics}/{topicCount} 토픽 완료</span>
            {progressPercentage > 0 && (
              <span className="flex items-center">
                <Trophy className="w-3 h-3 mr-1" />
                진행 중
              </span>
            )}
          </div>
        </div>
        
        {/* 주요 토픽 미리보기 */}
        <div>
          <h4 className="text-sm font-medium mb-2">주요 학습 내용</h4>
          <div className="grid grid-cols-1 gap-1">
            {RECOMMENDED_LEARNING_PATH[subjectKey]?.slice(0, 3).map((topicKey, index) => (
              <div key={topicKey} className="flex items-center text-xs text-gray-600">
                <div className="w-1.5 h-1.5 rounded-full bg-blue-400 mr-2"></div>
                {topics[topicKey] || topicKey}
              </div>
            ))}
            {RECOMMENDED_LEARNING_PATH[subjectKey]?.length > 3 && (
              <div className="text-xs text-gray-500 ml-3.5">
                +{RECOMMENDED_LEARNING_PATH[subjectKey].length - 3}개 더
              </div>
            )}
          </div>
        </div>
        
        {/* 액션 버튼들 */}
        <div className="flex space-x-2 pt-2">
          <Button 
            onClick={handleStartLearning}
            className="flex-1"
            style={{ backgroundColor: colors.primary }}
          >
            <Play className="w-4 h-4 mr-2" />
            시작하기
          </Button>
          <Button 
            onClick={handleViewDetails}
            variant="outline"
            size="sm"
          >
            <ChevronRight className="w-4 h-4" />
          </Button>
        </div>
      </CardContent>
    </Card>
  );
};

const SubjectDetailModal = ({ subjectKey, onClose }) => {
  const navigate = useNavigate();
  
  if (!subjectKey) return null;
  
  const subjectName = SUBJECTS[subjectKey];
  const topics = SUBJECT_TOPICS[subjectKey] || {};
  const colors = SUBJECT_COLORS[subjectKey];
  const icon = SUBJECT_ICONS[subjectKey];
  const learningPath = RECOMMENDED_LEARNING_PATH[subjectKey] || [];
  
  const handleStartLearning = () => {
    navigate(`/quiz?subject=${subjectKey}`);
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-xl max-w-2xl w-full max-h-[80vh] overflow-y-auto">
        <div className="p-6">
          {/* 헤더 */}
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center space-x-3">
              <div 
                className="w-16 h-16 rounded-xl flex items-center justify-center text-3xl"
                style={{ backgroundColor: colors.background }}
              >
                {icon}
              </div>
              <div>
                <h2 className="text-2xl font-bold">{subjectName}</h2>
                <p className="text-gray-600">{SUBJECT_DESCRIPTIONS[subjectKey]}</p>
              </div>
            </div>
            <Button 
              onClick={onClose}
              variant="ghost" 
              size="sm"
            >
              ✕
            </Button>
          </div>
          
          {/* 학습 경로 */}
          <div className="mb-6">
            <h3 className="text-lg font-semibold mb-4 flex items-center">
              <Target className="w-5 h-5 mr-2" />
              추천 학습 경로
            </h3>
            <div className="space-y-3">
              {learningPath.map((topicKey, index) => (
                <div key={topicKey} className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg">
                  <div className="w-8 h-8 rounded-full bg-blue-100 text-blue-600 flex items-center justify-center text-sm font-medium">
                    {index + 1}
                  </div>
                  <div className="flex-1">
                    <h4 className="font-medium">{topics[topicKey] || topicKey}</h4>
                  </div>
                  <Badge variant="outline">
                    {index < 3 ? '기초' : index < 6 ? '중급' : '고급'}
                  </Badge>
                </div>
              ))}
            </div>
          </div>
          
          {/* 액션 버튼 */}
          <div className="flex space-x-3">
            <Button 
              onClick={handleStartLearning}
              className="flex-1"
              style={{ backgroundColor: colors.primary }}
            >
              <Play className="w-4 h-4 mr-2" />
              학습 시작하기
            </Button>
            <Button 
              onClick={onClose}
              variant="outline"
            >
              닫기
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
};

const SubjectSelector = ({ userProgress = {} }) => {
  const [selectedSubject, setSelectedSubject] = useState(null);
  
  return (
    <div className="container mx-auto px-4 py-8">
      {/* 헤더 */}
      <div className="text-center mb-8">
        <h1 className="text-3xl font-bold mb-4">학습할 과목을 선택하세요</h1>
        <p className="text-gray-600 max-w-2xl mx-auto">
          SaaS 개발자가 되기 위한 핵심 기술들을 단계별로 학습할 수 있습니다. 
          각 과목은 실무에 바로 적용할 수 있는 내용들로 구성되어 있습니다.
        </p>
      </div>
      
      {/* 과목 카드들 */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 max-w-6xl mx-auto">
        {Object.keys(SUBJECTS).map((subjectKey) => (
          <SubjectCard
            key={subjectKey}
            subjectKey={subjectKey}
            subjectData={SUBJECTS[subjectKey]}
            onSelect={setSelectedSubject}
            userProgress={userProgress}
          />
        ))}
      </div>
      
      {/* 통계 요약 */}
      <div className="mt-12 bg-gradient-to-r from-blue-50 to-purple-50 rounded-xl p-6 max-w-4xl mx-auto">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 text-center">
          <div className="flex flex-col items-center">
            <BookOpen className="w-8 h-8 text-blue-600 mb-2" />
            <div className="text-2xl font-bold text-gray-900">
              {Object.values(SUBJECT_TOPICS).reduce((total, topics) => total + Object.keys(topics).length, 0)}
            </div>
            <div className="text-sm text-gray-600">총 학습 토픽</div>
          </div>
          <div className="flex flex-col items-center">
            <Users className="w-8 h-8 text-green-600 mb-2" />
            <div className="text-2xl font-bold text-gray-900">1,000+</div>
            <div className="text-sm text-gray-600">수강생</div>
          </div>
          <div className="flex flex-col items-center">
            <Clock className="w-8 h-8 text-purple-600 mb-2" />
            <div className="text-2xl font-bold text-gray-900">50+</div>
            <div className="text-sm text-gray-600">평균 학습 시간</div>
          </div>
        </div>
      </div>
      
      {/* 상세 모달 */}
      {selectedSubject && (
        <SubjectDetailModal 
          subjectKey={selectedSubject}
          onClose={() => setSelectedSubject(null)}
        />
      )}
    </div>
  );
};

export default SubjectSelector;
