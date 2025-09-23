import { useState } from 'react';
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
  
  // 스트리밍 관련 상태
  const [isStreaming, setIsStreaming] = useState(false);
  const [streamContent, setStreamContent] = useState('');
  const [streamStatus, setStreamStatus] = useState('');
  const [useStreaming, setUseStreaming] = useState(true);

  // 커리큘럼 생성 mutation
  const generateMutation = useMutation({
    mutationFn: aiApi.generateCurriculum,
    onSuccess: (data) => {
      console.log('커리큘럼 생성 성공:', data);
      setGeneratedCurriculumId(data.id);
    },
    onError: (error) => {
      console.error('커리큘럼 생성 실패:', error);
      alert(`커리큘럼 생성에 실패했습니다: ${error.message}`);
    },
  });

  // 생성된 커리큘럼 조회
  const { data: curriculumData } = useQuery({
    queryKey: ['curriculum', generatedCurriculumId],
    queryFn: () => aiApi.getCurriculum(generatedCurriculumId!),
    enabled: !!generatedCurriculumId,
    refetchInterval: (query) => {
      const data = query.state.data;
      return data?.status === 'generating' ? 3000 : false;
    },
    retry: 3,
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

  // 스트리밍 커리큘럼 생성
  const handleStreamingGenerate = async () => {
    const validGoals = learningGoals.filter(goal => goal.trim());
    const validRequirements = specialRequirements.filter(req => req.trim());
    const finalSubject = customSubject.trim() || selectedSubject;
    
    if (!finalSubject || validGoals.length === 0) {
      alert(!finalSubject ? '학습할 과목을 선택하거나 직접 입력해주세요' : '학습 목표를 최소 하나는 입력해주세요');
      return;
    }

    try {
      setIsStreaming(true);
      setStreamContent('');
      setStreamStatus('AI 커리큘럼 생성을 시작합니다...');

      const response = await aiApi.generateCurriculumStream({
        subject_key: finalSubject,
        learning_goals: validGoals,
        difficulty_level: difficultyLevel,
        duration_preference: durationPreference,
        special_requirements: validRequirements.length > 0 ? validRequirements : undefined,
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const reader = response.body?.getReader();
      const decoder = new TextDecoder();

      if (reader) {
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          const chunk = decoder.decode(value);
          const lines = chunk.split('\\n');

          for (const line of lines) {
            if (line.startsWith('data: ')) {
              try {
                const data = JSON.parse(line.slice(6));
                
                if (data.type === 'started') {
                  setGeneratedCurriculumId(data.curriculum_id);
                  setStreamStatus(data.message);
                } else if (data.type === 'token') {
                  setStreamContent(prev => prev + data.content);
                } else if (data.type === 'section_change') {
                  setStreamStatus(data.message);
                } else if (data.type === 'completed') {
                  setStreamStatus('커리큘럼 생성이 완료되었습니다!');
                  setIsStreaming(false);
                } else if (data.type === 'error') {
                  setStreamStatus(`오류: ${data.message}`);
                  setIsStreaming(false);
                }
              } catch (e) {
                console.warn('JSON 파싱 실패:', line);
              }
            }
          }
        }
      }
    } catch (error: any) {
      console.error('스트리밍 생성 실패:', error);
      setStreamStatus(`생성 실패: ${error.message}`);
      setIsStreaming(false);
    }
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

    console.log('커리큘럼 생성 요청:', {
      subject_key: finalSubject,
      learning_goals: validGoals,
      difficulty_level: difficultyLevel,
      duration_preference: durationPreference,
      special_requirements: validRequirements.length > 0 ? validRequirements : undefined,
    });

    generateMutation.mutate({
      subject_key: finalSubject,
      learning_goals: validGoals,
      difficulty_level: difficultyLevel,
      duration_preference: durationPreference,
      special_requirements: validRequirements.length > 0 ? validRequirements : undefined,
    });
  };

  // 상태 계산
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
          <h2 className="text-2xl font-bold text-gray-900">AI 커리큘럼 생성</h2>
        </div>

        {/* 메인 컨텐츠 */}
        {!generatedCurriculumId && !isStreaming && !streamContent ? (
          /* 커리큘럼 생성 폼 */
          <div className="space-y-6">
            {/* 과목 선택 */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                학습할 과목 *
              </label>
              
              {subjects.length > 0 && (
                <div className="mb-3">
                  <select
                    value={selectedSubject}
                    onChange={(e) => {
                      setSelectedSubject(e.target.value);
                      if (e.target.value) setCustomSubject('');
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
              
              <div>
                <input
                  type="text"
                  value={customSubject}
                  onChange={(e) => {
                    setCustomSubject(e.target.value);
                    if (e.target.value) setSelectedSubject('');
                  }}
                  placeholder="또는 학습하고 싶은 과목을 직접 입력하세요 (예: Python, React, 머신러닝, 영어회화 등)"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
            </div>

            {/* 학습 목표 */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                학습 목표 *
              </label>
              <div className="space-y-2">
                {learningGoals.map((goal, index) => (
                  <div key={index} className="flex items-center space-x-2">
                    <input
                      type="text"
                      value={goal}
                      onChange={(e) => updateLearningGoal(index, e.target.value)}
                      placeholder={`학습 목표 ${index + 1} (예: 기본 문법 이해, 실전 프로젝트 완성 등)`}
                      className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    />
                    {learningGoals.length > 1 && (
                      <button
                        onClick={() => removeLearningGoal(index)}
                        className="p-2 text-red-600 hover:text-red-700"
                      >
                        <X className="w-4 h-4" />
                      </button>
                    )}
                  </div>
                ))}
              </div>
              <button
                onClick={addLearningGoal}
                className="mt-2 flex items-center text-blue-600 hover:text-blue-700 text-sm"
              >
                <Plus className="w-4 h-4 mr-1" />
                학습 목표 추가
              </button>
            </div>

            {/* 난이도 설정 */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                난이도 수준: {difficultyLevel}/10
              </label>
              <input
                type="range"
                min="1"
                max="10"
                value={difficultyLevel}
                onChange={(e) => setDifficultyLevel(parseInt(e.target.value))}
                className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
              />
              <div className="flex justify-between text-sm text-gray-500 mt-1">
                <span>입문자</span>
                <span>중급자</span>
                <span>전문가</span>
              </div>
            </div>

            {/* 학습 기간 */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                선호 학습 기간
              </label>
              <select
                value={durationPreference}
                onChange={(e) => setDurationPreference(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="2주">2주 (집중 과정)</option>
                <option value="4주">4주 (표준 과정)</option>
                <option value="8주">8주 (체계적 과정)</option>
                <option value="12주">12주 (심화 과정)</option>
              </select>
            </div>

            {/* 생성 방식 선택 */}
            <div className="bg-gray-50 rounded-lg p-4">
              <label className="block text-sm font-medium text-gray-700 mb-3">
                생성 방식 선택
              </label>
              
              <div className="space-y-2">
                <label className="flex items-center">
                  <input
                    type="radio"
                    name="generationMode"
                    checked={useStreaming}
                    onChange={() => setUseStreaming(true)}
                    className="mr-2 text-blue-600"
                  />
                  <span className="text-sm">실시간 스트리밍 생성 (권장)</span>
                </label>
                <p className="text-xs text-gray-600 ml-6">
                  ChatGPT처럼 글자가 하나씩 나타나며 생성 과정을 실시간으로 볼 수 있습니다
                </p>
                
                <label className="flex items-center">
                  <input
                    type="radio"
                    name="generationMode"
                    checked={!useStreaming}
                    onChange={() => setUseStreaming(false)}
                    className="mr-2 text-blue-600"
                  />
                  <span className="text-sm">일반 생성 (완료 후 표시)</span>
                </label>
                <p className="text-xs text-gray-600 ml-6">
                  완성된 커리큘럼을 한 번에 표시합니다 (2-3분 소요)
                </p>
              </div>
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
              <button
                onClick={useStreaming ? handleStreamingGenerate : handleGenerate}
                disabled={(!selectedSubject && !customSubject.trim()) || learningGoals.filter(g => g.trim()).length === 0 || generateMutation.isPending || isStreaming}
                className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed flex items-center transition-all duration-200"
              >
                {generateMutation.isPending || isStreaming ? (
                  <>
                    <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                    {useStreaming ? 'AI 스트리밍 생성 중...' : 'AI 생성 중...'}
                  </>
                ) : (
                  <>
                    <BookOpen className="w-4 h-4 mr-2" />
                    {useStreaming ? '실시간 커리큘럼 생성' : '커리큘럼 생성하기'}
                  </>
                )}
              </button>
            </div>
          </div>
        ) : (
          /* 생성 결과 또는 스트리밍 표시 */
          <div>
            {/* 스트리밍 결과 표시 */}
            {(isStreaming || streamContent) && (
              <div className="bg-gray-50 rounded-lg p-4">
                <div className="flex items-center justify-between mb-3">
                  <h3 className="text-lg font-medium text-gray-900">AI 커리큘럼 생성</h3>
                  {isStreaming && (
                    <div className="flex items-center text-blue-600">
                      <RefreshCw className="w-4 h-4 mr-1 animate-spin" />
                      <span className="text-sm">실시간 생성</span>
                    </div>
                  )}
                </div>
                
                {streamStatus && (
                  <div className="mb-3 text-sm text-blue-600 font-medium">
                    {streamStatus}
                  </div>
                )}
                
                <div className="bg-white rounded-lg p-4 border max-h-96 overflow-y-auto">
                  <pre className="whitespace-pre-wrap text-sm text-gray-800">
                    {streamContent}
                    {isStreaming && <span className="animate-pulse">|</span>}
                  </pre>
                </div>

                {!isStreaming && streamContent && (
                  <div className="mt-3 flex space-x-2">
                    <button
                      onClick={() => {
                        setStreamContent('');
                        setStreamStatus('');
                        setGeneratedCurriculumId(null);
                      }}
                      className="px-4 py-2 bg-gray-500 text-white rounded-lg hover:bg-gray-600"
                    >
                      다시 생성
                    </button>
                  </div>
                )}
              </div>
            )}

            {/* 기존 방식 결과 표시 */}
            {generatedCurriculumId && !isStreaming && !streamContent && (
              <div>
                {isGenerating && (
                  <div className="text-center py-8">
                    <RefreshCw className="w-12 h-12 animate-spin mx-auto mb-4 text-blue-600" />
                    <h3 className="text-lg font-medium text-gray-900 mb-2">AI가 커리큘럼을 생성하고 있습니다</h3>
                    <p className="text-gray-600">
                      2-Agent 시스템이 당신만의 맞춤형 학습 계획을 만들고 있어요...
                    </p>
                  </div>
                )}
                
                {isCompleted && curriculumData && (
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
                )}
                
                {!isGenerating && !isCompleted && (
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
        )}
      </div>
    </div>
  );
}