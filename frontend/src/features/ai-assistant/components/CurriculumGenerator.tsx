import React, { useState } from 'react';
import { useMutation, useQuery } from '@tanstack/react-query';
import { BookOpen, ArrowLeft, RefreshCw, CheckCircle, AlertCircle, Plus, X } from 'lucide-react';
import { aiApi } from '../../../shared/services/apiClient';

interface Subject {
  id: number;
  key: string;
  title: string;
  description?: string;
  difficulty_level?: string;
}

interface CurriculumGeneratorProps {
  subjects?: Subject[];
  onBack?: () => void;
}

export default function CurriculumGenerator({ subjects = [], onBack }: CurriculumGeneratorProps) {
  const [selectedSubject, setSelectedSubject] = useState('');
  const [customSubject, setCustomSubject] = useState('');
  const [learningGoals, setLearningGoals] = useState<string[]>(['']);
  const [difficultyLevel, setDifficultyLevel] = useState(3);
  const [durationPreference, setDurationPreference] = useState('4주');
  const [specialRequirements, setSpecialRequirements] = useState<string[]>([]);
  const [generatedCurriculumId, setGeneratedCurriculumId] = useState<number | null>(null);

  // 커리큘럼 생성 mutation
  const generateMutation = useMutation({
    mutationFn: aiApi.generateCurriculum,
    onSuccess: (data) => {
      setGeneratedCurriculumId(data.id);
    },
  });

  // 생성된 커리큘럼 조회
  const { data: curriculumData, isLoading: isLoadingCurriculum } = useQuery({
    queryKey: ['curriculum', generatedCurriculumId],
    queryFn: () => aiApi.getCurriculum(generatedCurriculumId!),
    enabled: !!generatedCurriculumId,
    refetchInterval: (data) => {
      // 상태가 'generating'이면 3초마다 폴링
      return data?.status === 'generating' ? 3000 : false;
    },
  });

  const addLearningGoal = () => {
    setLearningGoals([...learningGoals, '']);
  };

  const updateLearningGoal = (index: number, value: string) => {
    const updated = [...learningGoals];
    updated[index] = value;
    setLearningGoals(updated);
  };

  const removeLearningGoal = (index: number) => {
    if (learningGoals.length > 1) {
      setLearningGoals(learningGoals.filter((_, i) => i !== index));
    }
  };

  const addSpecialRequirement = () => {
    setSpecialRequirements([...specialRequirements, '']);
  };

  const updateSpecialRequirement = (index: number, value: string) => {
    const updated = [...specialRequirements];
    updated[index] = value;
    setSpecialRequirements(updated);
  };

  const removeSpecialRequirement = (index: number) => {
    setSpecialRequirements(specialRequirements.filter((_, i) => i !== index));
  };

  const handleGenerate = () => {
    const validGoals = learningGoals.filter(goal => goal.trim());
    const validRequirements = specialRequirements.filter(req => req.trim());
    const finalSubject = customSubject.trim() || selectedSubject;
    
    if (!finalSubject || validGoals.length === 0) {
      if (!finalSubject) {
        alert('학습할 과목을 선택하거나 직접 입력해주세요');
      } else {
        alert('학습 목표를 최소 하나는 입력해주세요');
      }
      return;
    }

    generateMutation.mutate({
      subject_key: finalSubject,
      learning_goals: validGoals,
      difficulty_level: difficultyLevel,
      duration_preference: durationPreference,
      special_requirements: validRequirements.length > 0 ? validRequirements : undefined,
    });
  };

  // 커리큘럼이 생성 완료되었는지 확인
  const isCompleted = curriculumData?.status === 'completed';
  const isGenerating = curriculumData?.status === 'generating' || generateMutation.isPending;

  return (
    <div className="max-w-4xl mx-auto">
      <div className="bg-white rounded-lg p-6 shadow-sm border border-gray-200">
        {/* 헤더 */}
        <div className="flex items-center mb-6">
          <button 
            onClick={onBack}
            className="mr-4 p-2 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <ArrowLeft className="w-5 h-5" />
          </button>
          <div>
            <h2 className="text-xl font-semibold text-gray-900">AI 맞춤 커리큘럼 생성</h2>
            <p className="text-gray-600 text-sm mt-1">
              Phase 9 API를 사용하여 개인화된 학습 계획을 생성합니다
            </p>
          </div>
        </div>

        {!generatedCurriculumId ? (
          /* 커리큘럼 생성 폼 */
          <div className="space-y-6">
            {/* 과목 선택 */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                학습할 과목 *
              </label>
              
              {/* 기존 과목 선택 (있는 경우) */}
              {subjects.length > 0 && (
                <div className="mb-3">
                  <select
                    value={selectedSubject}
                    onChange={(e) => {
                      setSelectedSubject(e.target.value);
                      if (e.target.value) setCustomSubject(''); // 기존 과목 선택시 직접입력 초기화
                    }}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  >
                    <option value="">기존 과목에서 선택</option>
                    {subjects.map((subject) => (
                      <option key={subject.id} value={subject.key}>
                        {subject.title} ({subject.difficulty_level || '기본'})
                      </option>
                    ))}
                  </select>
                </div>
              )}
              
              {/* 직접 입력 */}
              <div>
                <input
                  type="text"
                  value={customSubject}
                  onChange={(e) => {
                    setCustomSubject(e.target.value);
                    if (e.target.value) setSelectedSubject(''); // 직접입력시 기존 선택 초기화
                  }}
                  placeholder="또는 학습하고 싶은 과목을 직접 입력하세요 (예: Python, React, 머신러닝, 영어회화 등)"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
                <p className="text-xs text-gray-500 mt-1">
                  프로그래밍, 언어, 디자인, 비즈니스 등 어떤 주제든 가능합니다
                </p>
              </div>
            </div>

            {/* 학습 목표 */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                학습 목표 *
              </label>
              {learningGoals.map((goal, index) => (
                <div key={index} className="flex mb-2">
                  <input
                    type="text"
                    value={goal}
                    onChange={(e) => updateLearningGoal(index, e.target.value)}
                    placeholder={`학습 목표 ${index + 1}`}
                    className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  />
                  {learningGoals.length > 1 && (
                    <button
                      onClick={() => removeLearningGoal(index)}
                      className="ml-2 p-2 text-red-500 hover:bg-red-50 rounded-lg"
                    >
                      <X className="w-4 h-4" />
                    </button>
                  )}
                </div>
              ))}
              <button
                onClick={addLearningGoal}
                className="flex items-center text-blue-600 hover:text-blue-700 text-sm"
              >
                <Plus className="w-4 h-4 mr-1" />
                목표 추가
              </button>
            </div>

            {/* 난이도 설정 */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                희망 난이도: {difficultyLevel}/10
              </label>
              <input
                type="range"
                min="1"
                max="10"
                value={difficultyLevel}
                onChange={(e) => setDifficultyLevel(Number(e.target.value))}
                className="w-full"
              />
              <div className="flex justify-between text-xs text-gray-500 mt-1">
                <span>쉬움</span>
                <span>보통</span>
                <span>어려움</span>
              </div>
            </div>

            {/* 학습 기간 */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                희망 학습 기간
              </label>
              <select
                value={durationPreference}
                onChange={(e) => setDurationPreference(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="2주">2주 (집중 과정)</option>
                <option value="4주">4주 (표준)</option>
                <option value="8주">8주 (여유있게)</option>
                <option value="12주">12주 (장기 계획)</option>
              </select>
            </div>

            {/* 특별 요구사항 */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                특별 요구사항 (선택)
              </label>
              {specialRequirements.map((req, index) => (
                <div key={index} className="flex mb-2">
                  <input
                    type="text"
                    value={req}
                    onChange={(e) => updateSpecialRequirement(index, e.target.value)}
                    placeholder="예: 실무 프로젝트 중심, 이론보다 실습 우선 등"
                    className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  />
                  <button
                    onClick={() => removeSpecialRequirement(index)}
                    className="ml-2 p-2 text-red-500 hover:bg-red-50 rounded-lg"
                  >
                    <X className="w-4 h-4" />
                  </button>
                </div>
              ))}
              <button
                onClick={addSpecialRequirement}
                className="flex items-center text-blue-600 hover:text-blue-700 text-sm"
              >
                <Plus className="w-4 h-4 mr-1" />
                요구사항 추가
              </button>
            </div>

            {/* 에러 표시 */}
            {generateMutation.error && (
              <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                <div className="flex items-center">
                  <AlertCircle className="w-5 h-5 text-red-600 mr-2" />
                  <span className="text-red-800">
                    {generateMutation.error instanceof Error 
                      ? generateMutation.error.message 
                      : '커리큘럼 생성에 실패했습니다.'
                    }
                  </span>
                </div>
              </div>
            )}

            {/* 생성 버튼 */}
            <div className="flex flex-col items-end">
              {/* 조건 체크 안내 */}
              {(!selectedSubject && !customSubject.trim()) || learningGoals.filter(g => g.trim()).length === 0 ? (
                <div className="text-sm text-gray-500 mb-2 text-right">
                  {(!selectedSubject && !customSubject.trim()) && learningGoals.filter(g => g.trim()).length === 0 
                    ? '⚠️ 과목과 학습 목표를 입력해주세요'
                    : (!selectedSubject && !customSubject.trim())
                      ? '⚠️ 학습할 과목을 선택하거나 입력해주세요'
                      : '⚠️ 학습 목표를 최소 하나는 입력해주세요'
                  }
                </div>
              ) : null}
              
              <button
                onClick={handleGenerate}
                disabled={(!selectedSubject && !customSubject.trim()) || learningGoals.filter(g => g.trim()).length === 0 || generateMutation.isPending}
                className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed flex items-center transition-all duration-200"
              >
                {generateMutation.isPending ? (
                  <>
                    <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                    AI 생성 중...
                  </>
                ) : (
                  <>
                    <BookOpen className="w-4 h-4 mr-2" />
                    커리큘럼 생성하기
                  </>
                )}
              </button>
            </div>
          </div>
        ) : (
          /* 생성 결과 표시 */
          <div>
            {isGenerating ? (
              <div className="text-center py-8">
                <RefreshCw className="w-12 h-12 animate-spin mx-auto mb-4 text-blue-600" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">AI가 커리큘럼을 생성하고 있습니다</h3>
                <p className="text-gray-600">
                  2-Agent 시스템이 당신만의 맞춤형 학습 계획을 만들고 있어요...
                </p>
              </div>
            ) : isCompleted && curriculumData ? (
              <div>
                <div className="flex items-center mb-4">
                  <CheckCircle className="w-6 h-6 text-green-600 mr-2" />
                  <h3 className="text-lg font-semibold text-gray-900">커리큘럼 생성 완료!</h3>
                </div>
                
                {curriculumData.generated_syllabus && (
                  <div className="bg-gray-50 rounded-lg p-4 mb-4">
                    <h4 className="font-medium text-gray-900 mb-2">생성된 커리큘럼</h4>
                    <pre className="whitespace-pre-wrap text-sm text-gray-700">
                      {JSON.stringify(curriculumData.generated_syllabus, null, 2)}
                    </pre>
                  </div>
                )}

                {curriculumData.agent_conversation_log && (
                  <div className="bg-blue-50 rounded-lg p-4 mb-4">
                    <h4 className="font-medium text-blue-900 mb-2">AI 분석 과정</h4>
                    <p className="text-sm text-blue-800">
                      {curriculumData.agent_conversation_log}
                    </p>
                  </div>
                )}

                <div className="flex space-x-3">
                  <button
                    onClick={() => setGeneratedCurriculumId(null)}
                    className="bg-gray-600 text-white px-4 py-2 rounded-lg hover:bg-gray-700"
                  >
                    새 커리큘럼 생성
                  </button>
                  <button className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700">
                    커리큘럼 저장하기
                  </button>
                </div>
              </div>
            ) : (
              <div className="text-center py-8">
                <AlertCircle className="w-12 h-12 mx-auto mb-4 text-red-500" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">생성 실패</h3>
                <p className="text-gray-600 mb-4">커리큘럼 생성 중 오류가 발생했습니다.</p>
                <button
                  onClick={() => setGeneratedCurriculumId(null)}
                  className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
                >
                  다시 시도
                </button>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
