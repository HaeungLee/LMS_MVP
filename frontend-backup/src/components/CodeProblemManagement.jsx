import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  PlusIcon, 
  PencilIcon, 
  TrashIcon, 
  PlayIcon, 
  ClockIcon, 
  ChartBarIcon,
  TagIcon,
  AdjustmentsHorizontalIcon
} from '@heroicons/react/24/outline';
import { toast } from 'react-hot-toast';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

const CodeProblemManagement = () => {
  const [problems, setProblems] = useState([]);
  const [tags, setTags] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [editingProblem, setEditingProblem] = useState(null);
  const [selectedDifficulty, setSelectedDifficulty] = useState('all');
  const [selectedCategory, setSelectedCategory] = useState('all');

  // 문제 목록 로드
  const fetchProblems = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/code/admin/problems`);
      if (response.ok) {
        const data = await response.json();
        setProblems(data);
      }
    } catch (error) {
      console.error('Failed to fetch problems:', error);
      toast.error('문제 목록을 불러오지 못했습니다.');
    }
  };

  // 태그 목록 로드
  const fetchTags = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/code/admin/tags`);
      if (response.ok) {
        const data = await response.json();
        setTags(data);
      }
    } catch (error) {
      console.error('Failed to fetch tags:', error);
    }
  };

  useEffect(() => {
    const loadData = async () => {
      setLoading(true);
      await Promise.all([fetchProblems(), fetchTags()]);
      setLoading(false);
    };
    loadData();
  }, []);

  // 문제 삭제
  const handleDeleteProblem = async (problemId) => {
    if (!confirm('정말로 이 문제를 삭제하시겠습니까?')) return;

    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/code/admin/problems/${problemId}`, {
        method: 'DELETE'
      });
      
      if (response.ok) {
        setProblems(problems.filter(p => p.id !== problemId));
        toast.success('문제가 삭제되었습니다.');
      } else {
        toast.error('문제 삭제에 실패했습니다.');
      }
    } catch (error) {
      console.error('Failed to delete problem:', error);
      toast.error('문제 삭제 중 오류가 발생했습니다.');
    }
  };

  // 난이도별 색상
  const getDifficultyColor = (difficulty) => {
    switch (difficulty) {
      case 'easy': return 'text-green-600 bg-green-100';
      case 'medium': return 'text-yellow-600 bg-yellow-100';
      case 'hard': return 'text-red-600 bg-red-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  // 필터링된 문제들
  const filteredProblems = problems.filter(problem => {
    if (selectedDifficulty !== 'all' && problem.difficulty !== selectedDifficulty) {
      return false;
    }
    if (selectedCategory !== 'all' && problem.category !== selectedCategory) {
      return false;
    }
    return true;
  });

  // 카테고리 목록 추출
  const categories = [...new Set(problems.map(p => p.category))];

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* 헤더 */}
        <div className="mb-8">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">코딩테스트 문제 관리</h1>
              <p className="mt-2 text-gray-600">
                코딩테스트 문제를 생성, 수정, 삭제할 수 있습니다.
              </p>
            </div>
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => setShowCreateModal(true)}
              className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              <PlusIcon className="h-5 w-5 mr-2" />
              새 문제 추가
            </motion.button>
          </div>
        </div>

        {/* 필터링 */}
        <div className="mb-6 bg-white rounded-lg shadow p-4">
          <div className="flex flex-wrap gap-4 items-center">
            <div className="flex items-center space-x-2">
              <AdjustmentsHorizontalIcon className="h-5 w-5 text-gray-500" />
              <span className="text-sm font-medium text-gray-700">필터:</span>
            </div>
            
            <select
              value={selectedDifficulty}
              onChange={(e) => setSelectedDifficulty(e.target.value)}
              className="block w-32 px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
            >
              <option value="all">모든 난이도</option>
              <option value="easy">쉬움</option>
              <option value="medium">보통</option>
              <option value="hard">어려움</option>
            </select>

            <select
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              className="block w-40 px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
            >
              <option value="all">모든 카테고리</option>
              {categories.map(category => (
                <option key={category} value={category}>{category}</option>
              ))}
            </select>

            <div className="text-sm text-gray-500">
              총 {filteredProblems.length}개 문제
            </div>
          </div>
        </div>

        {/* 문제 목록 */}
        <div className="bg-white shadow rounded-lg overflow-hidden">
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    문제 정보
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    난이도
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    통계
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    제한사항
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    생성일
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                    작업
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {filteredProblems.map((problem) => (
                  <motion.tr
                    key={problem.id}
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    className="hover:bg-gray-50"
                  >
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div>
                        <div className="text-sm font-medium text-gray-900">
                          {problem.title}
                        </div>
                        <div className="text-sm text-gray-500">
                          {problem.category}
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getDifficultyColor(problem.difficulty)}`}>
                        {problem.difficulty === 'easy' ? '쉬움' : problem.difficulty === 'medium' ? '보통' : '어려움'}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      <div className="flex items-center space-x-4">
                        <div className="flex items-center">
                          <ChartBarIcon className="h-4 w-4 mr-1" />
                          {problem.acceptance_rate?.toFixed(1) || 0}%
                        </div>
                        <div>
                          제출: {problem.total_submissions || 0}
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      <div className="flex items-center space-x-2">
                        <ClockIcon className="h-4 w-4" />
                        <span>{problem.time_limit_ms}ms</span>
                        <span>/</span>
                        <span>{problem.memory_limit_mb}MB</span>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {new Date(problem.created_at).toLocaleDateString('ko-KR')}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                      <div className="flex justify-end space-x-2">
                        <motion.button
                          whileHover={{ scale: 1.1 }}
                          whileTap={{ scale: 0.9 }}
                          onClick={() => window.open(`/code/problems/${problem.id}`, '_blank')}
                          className="text-green-600 hover:text-green-900 p-1"
                          title="문제 풀기"
                        >
                          <PlayIcon className="h-4 w-4" />
                        </motion.button>
                        <motion.button
                          whileHover={{ scale: 1.1 }}
                          whileTap={{ scale: 0.9 }}
                          onClick={() => setEditingProblem(problem)}
                          className="text-blue-600 hover:text-blue-900 p-1"
                          title="수정"
                        >
                          <PencilIcon className="h-4 w-4" />
                        </motion.button>
                        <motion.button
                          whileHover={{ scale: 1.1 }}
                          whileTap={{ scale: 0.9 }}
                          onClick={() => handleDeleteProblem(problem.id)}
                          className="text-red-600 hover:text-red-900 p-1"
                          title="삭제"
                        >
                          <TrashIcon className="h-4 w-4" />
                        </motion.button>
                      </div>
                    </td>
                  </motion.tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* 빈 상태 */}
        {filteredProblems.length === 0 && (
          <div className="text-center py-12">
            <div className="text-gray-500">
              {problems.length === 0 ? '아직 생성된 문제가 없습니다.' : '필터 조건에 맞는 문제가 없습니다.'}
            </div>
            {problems.length === 0 && (
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => setShowCreateModal(true)}
                className="mt-4 inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700"
              >
                <PlusIcon className="h-5 w-5 mr-2" />
                첫 번째 문제 추가하기
              </motion.button>
            )}
          </div>
        )}
      </div>

      {/* 문제 생성/수정 모달 */}
      <AnimatePresence>
        {(showCreateModal || editingProblem) && (
          <ProblemFormModal
            problem={editingProblem}
            tags={tags}
            onClose={() => {
              setShowCreateModal(false);
              setEditingProblem(null);
            }}
            onSave={(problem) => {
              if (editingProblem) {
                setProblems(problems.map(p => p.id === problem.id ? problem : p));
              } else {
                setProblems([...problems, problem]);
              }
              setShowCreateModal(false);
              setEditingProblem(null);
            }}
          />
        )}
      </AnimatePresence>
    </div>
  );
};

// 문제 생성/수정 모달 컴포넌트
const ProblemFormModal = ({ problem, tags, onClose, onSave }) => {
  const [formData, setFormData] = useState({
    title: problem?.title || '',
    description: problem?.description || '',
    difficulty: problem?.difficulty || 'easy',
    category: problem?.category || '',
    examples: problem?.examples || [{ input: '', output: '', explanation: '' }],
    constraints: problem?.constraints || [''],
    hints: problem?.hints || [''],
    template: problem?.template || '',
    time_limit_ms: problem?.time_limit_ms || 10000,
    memory_limit_mb: problem?.memory_limit_mb || 128,
    test_cases: problem?.test_cases || [
      { input_data: '', expected_output: '', description: '', is_sample: true, is_hidden: false, weight: 1.0 }
    ]
  });

  const [saving, setSaving] = useState(false);

  // 예제 추가/제거
  const addExample = () => {
    setFormData({
      ...formData,
      examples: [...formData.examples, { input: '', output: '', explanation: '' }]
    });
  };

  const removeExample = (index) => {
    setFormData({
      ...formData,
      examples: formData.examples.filter((_, i) => i !== index)
    });
  };

  // 제약조건 추가/제거
  const addConstraint = () => {
    setFormData({
      ...formData,
      constraints: [...formData.constraints, '']
    });
  };

  const removeConstraint = (index) => {
    setFormData({
      ...formData,
      constraints: formData.constraints.filter((_, i) => i !== index)
    });
  };

  // 힌트 추가/제거
  const addHint = () => {
    setFormData({
      ...formData,
      hints: [...formData.hints, '']
    });
  };

  const removeHint = (index) => {
    setFormData({
      ...formData,
      hints: formData.hints.filter((_, i) => i !== index)
    });
  };

  // 테스트 케이스 추가/제거
  const addTestCase = () => {
    setFormData({
      ...formData,
      test_cases: [...formData.test_cases, 
        { input_data: '', expected_output: '', description: '', is_sample: false, is_hidden: true, weight: 1.0 }
      ]
    });
  };

  const removeTestCase = (index) => {
    setFormData({
      ...formData,
      test_cases: formData.test_cases.filter((_, i) => i !== index)
    });
  };

  // 폼 제출
  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);

    try {
      const url = problem 
        ? `${API_BASE_URL}/api/v1/code/admin/problems/${problem.id}`
        : `${API_BASE_URL}/api/v1/code/admin/problems`;
      
      const method = problem ? 'PUT' : 'POST';

      const response = await fetch(url, {
        method,
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });

      if (response.ok) {
        const savedProblem = await response.json();
        onSave(savedProblem);
        toast.success(problem ? '문제가 수정되었습니다.' : '문제가 생성되었습니다.');
      } else {
        toast.error('문제 저장에 실패했습니다.');
      }
    } catch (error) {
      console.error('Failed to save problem:', error);
      toast.error('문제 저장 중 오류가 발생했습니다.');
    } finally {
      setSaving(false);
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50"
    >
      <div className="relative top-4 mx-auto p-5 border w-11/12 max-w-4xl shadow-lg rounded-md bg-white mb-4">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-medium text-gray-900">
            {problem ? '문제 수정' : '새 문제 생성'}
          </h3>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600"
          >
            <span className="sr-only">닫기</span>
            <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* 기본 정보 */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700">제목</label>
              <input
                type="text"
                value={formData.title}
                onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">카테고리</label>
              <input
                type="text"
                value={formData.category}
                onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                required
              />
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700">난이도</label>
              <select
                value={formData.difficulty}
                onChange={(e) => setFormData({ ...formData, difficulty: e.target.value })}
                className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="easy">쉬움</option>
                <option value="medium">보통</option>
                <option value="hard">어려움</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">시간 제한 (ms)</label>
              <input
                type="number"
                value={formData.time_limit_ms}
                onChange={(e) => setFormData({ ...formData, time_limit_ms: parseInt(e.target.value) })}
                className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                min="1000"
                step="1000"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">메모리 제한 (MB)</label>
              <input
                type="number"
                value={formData.memory_limit_mb}
                onChange={(e) => setFormData({ ...formData, memory_limit_mb: parseInt(e.target.value) })}
                className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                min="64"
                step="64"
              />
            </div>
          </div>

          {/* 문제 설명 */}
          <div>
            <label className="block text-sm font-medium text-gray-700">문제 설명</label>
            <textarea
              rows={4}
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
              required
            />
          </div>

          {/* 예제 */}
          <div>
            <div className="flex justify-between items-center">
              <label className="block text-sm font-medium text-gray-700">예제</label>
              <button
                type="button"
                onClick={addExample}
                className="text-blue-600 hover:text-blue-500 text-sm"
              >
                + 예제 추가
              </button>
            </div>
            {formData.examples.map((example, index) => (
              <div key={index} className="mt-2 p-4 border border-gray-200 rounded-md">
                <div className="flex justify-between items-center mb-2">
                  <span className="text-sm font-medium">예제 {index + 1}</span>
                  {formData.examples.length > 1 && (
                    <button
                      type="button"
                      onClick={() => removeExample(index)}
                      className="text-red-600 hover:text-red-500 text-sm"
                    >
                      삭제
                    </button>
                  )}
                </div>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div>
                    <label className="block text-xs text-gray-500">입력</label>
                    <textarea
                      rows={2}
                      value={example.input}
                      onChange={(e) => {
                        const newExamples = [...formData.examples];
                        newExamples[index].input = e.target.value;
                        setFormData({ ...formData, examples: newExamples });
                      }}
                      className="mt-1 block w-full border-gray-300 rounded-md shadow-sm text-sm"
                    />
                  </div>
                  <div>
                    <label className="block text-xs text-gray-500">출력</label>
                    <textarea
                      rows={2}
                      value={example.output}
                      onChange={(e) => {
                        const newExamples = [...formData.examples];
                        newExamples[index].output = e.target.value;
                        setFormData({ ...formData, examples: newExamples });
                      }}
                      className="mt-1 block w-full border-gray-300 rounded-md shadow-sm text-sm"
                    />
                  </div>
                  <div>
                    <label className="block text-xs text-gray-500">설명</label>
                    <textarea
                      rows={2}
                      value={example.explanation}
                      onChange={(e) => {
                        const newExamples = [...formData.examples];
                        newExamples[index].explanation = e.target.value;
                        setFormData({ ...formData, examples: newExamples });
                      }}
                      className="mt-1 block w-full border-gray-300 rounded-md shadow-sm text-sm"
                    />
                  </div>
                </div>
              </div>
            ))}
          </div>

          {/* 제약조건 */}
          <div>
            <div className="flex justify-between items-center">
              <label className="block text-sm font-medium text-gray-700">제약조건</label>
              <button
                type="button"
                onClick={addConstraint}
                className="text-blue-600 hover:text-blue-500 text-sm"
              >
                + 제약조건 추가
              </button>
            </div>
            {formData.constraints.map((constraint, index) => (
              <div key={index} className="mt-2 flex items-center space-x-2">
                <input
                  type="text"
                  value={constraint}
                  onChange={(e) => {
                    const newConstraints = [...formData.constraints];
                    newConstraints[index] = e.target.value;
                    setFormData({ ...formData, constraints: newConstraints });
                  }}
                  className="flex-1 border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 text-sm"
                  placeholder="제약조건을 입력하세요"
                />
                {formData.constraints.length > 1 && (
                  <button
                    type="button"
                    onClick={() => removeConstraint(index)}
                    className="text-red-600 hover:text-red-500"
                  >
                    <TrashIcon className="h-4 w-4" />
                  </button>
                )}
              </div>
            ))}
          </div>

          {/* 힌트 */}
          <div>
            <div className="flex justify-between items-center">
              <label className="block text-sm font-medium text-gray-700">힌트</label>
              <button
                type="button"
                onClick={addHint}
                className="text-blue-600 hover:text-blue-500 text-sm"
              >
                + 힌트 추가
              </button>
            </div>
            {formData.hints.map((hint, index) => (
              <div key={index} className="mt-2 flex items-center space-x-2">
                <input
                  type="text"
                  value={hint}
                  onChange={(e) => {
                    const newHints = [...formData.hints];
                    newHints[index] = e.target.value;
                    setFormData({ ...formData, hints: newHints });
                  }}
                  className="flex-1 border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 text-sm"
                  placeholder="힌트를 입력하세요"
                />
                {formData.hints.length > 1 && (
                  <button
                    type="button"
                    onClick={() => removeHint(index)}
                    className="text-red-600 hover:text-red-500"
                  >
                    <TrashIcon className="h-4 w-4" />
                  </button>
                )}
              </div>
            ))}
          </div>

          {/* 코드 템플릿 */}
          <div>
            <label className="block text-sm font-medium text-gray-700">코드 템플릿</label>
            <textarea
              rows={8}
              value={formData.template}
              onChange={(e) => setFormData({ ...formData, template: e.target.value })}
              className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 font-mono text-sm"
              placeholder="# 여기에 기본 코드 템플릿을 작성하세요"
            />
          </div>

          {/* 테스트 케이스 */}
          <div>
            <div className="flex justify-between items-center">
              <label className="block text-sm font-medium text-gray-700">테스트 케이스</label>
              <button
                type="button"
                onClick={addTestCase}
                className="text-blue-600 hover:text-blue-500 text-sm"
              >
                + 테스트 케이스 추가
              </button>
            </div>
            {formData.test_cases.map((testCase, index) => (
              <div key={index} className="mt-2 p-4 border border-gray-200 rounded-md">
                <div className="flex justify-between items-center mb-2">
                  <span className="text-sm font-medium">테스트 케이스 {index + 1}</span>
                  {formData.test_cases.length > 1 && (
                    <button
                      type="button"
                      onClick={() => removeTestCase(index)}
                      className="text-red-600 hover:text-red-500 text-sm"
                    >
                      삭제
                    </button>
                  )}
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-3">
                  <div>
                    <label className="block text-xs text-gray-500">입력 데이터</label>
                    <textarea
                      rows={2}
                      value={testCase.input_data}
                      onChange={(e) => {
                        const newTestCases = [...formData.test_cases];
                        newTestCases[index].input_data = e.target.value;
                        setFormData({ ...formData, test_cases: newTestCases });
                      }}
                      className="mt-1 block w-full border-gray-300 rounded-md shadow-sm text-sm font-mono"
                    />
                  </div>
                  <div>
                    <label className="block text-xs text-gray-500">예상 출력</label>
                    <textarea
                      rows={2}
                      value={testCase.expected_output}
                      onChange={(e) => {
                        const newTestCases = [...formData.test_cases];
                        newTestCases[index].expected_output = e.target.value;
                        setFormData({ ...formData, test_cases: newTestCases });
                      }}
                      className="mt-1 block w-full border-gray-300 rounded-md shadow-sm text-sm font-mono"
                    />
                  </div>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div>
                    <label className="block text-xs text-gray-500">설명</label>
                    <input
                      type="text"
                      value={testCase.description}
                      onChange={(e) => {
                        const newTestCases = [...formData.test_cases];
                        newTestCases[index].description = e.target.value;
                        setFormData({ ...formData, test_cases: newTestCases });
                      }}
                      className="mt-1 block w-full border-gray-300 rounded-md shadow-sm text-sm"
                    />
                  </div>
                  <div className="flex items-center space-x-4">
                    <label className="flex items-center">
                      <input
                        type="checkbox"
                        checked={testCase.is_sample}
                        onChange={(e) => {
                          const newTestCases = [...formData.test_cases];
                          newTestCases[index].is_sample = e.target.checked;
                          setFormData({ ...formData, test_cases: newTestCases });
                        }}
                        className="mr-2"
                      />
                      <span className="text-xs text-gray-500">샘플</span>
                    </label>
                    <label className="flex items-center">
                      <input
                        type="checkbox"
                        checked={testCase.is_hidden}
                        onChange={(e) => {
                          const newTestCases = [...formData.test_cases];
                          newTestCases[index].is_hidden = e.target.checked;
                          setFormData({ ...formData, test_cases: newTestCases });
                        }}
                        className="mr-2"
                      />
                      <span className="text-xs text-gray-500">숨김</span>
                    </label>
                  </div>
                  <div>
                    <label className="block text-xs text-gray-500">가중치</label>
                    <input
                      type="number"
                      step="0.1"
                      min="0"
                      value={testCase.weight}
                      onChange={(e) => {
                        const newTestCases = [...formData.test_cases];
                        newTestCases[index].weight = parseFloat(e.target.value);
                        setFormData({ ...formData, test_cases: newTestCases });
                      }}
                      className="mt-1 block w-full border-gray-300 rounded-md shadow-sm text-sm"
                    />
                  </div>
                </div>
              </div>
            ))}
          </div>

          {/* 버튼 */}
          <div className="flex justify-end space-x-3 pt-6 border-t">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
            >
              취소
            </button>
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              type="submit"
              disabled={saving}
              className="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 disabled:opacity-50"
            >
              {saving ? '저장 중...' : (problem ? '수정하기' : '생성하기')}
            </motion.button>
          </div>
        </form>
      </div>
    </motion.div>
  );
};

export default CodeProblemManagement;
