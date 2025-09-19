import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { 
  Code2, 
  Play, 
  Filter, 
  Search, 
  Clock,
  CheckCircle,
  Circle,
  Star,
  TrendingUp
} from 'lucide-react';
import { getProblems, getSampleProblems } from '@/services/codeExecutionApi';

const CodeProblemsPage = () => {
  const navigate = useNavigate();
  const [problems, setProblems] = useState([]);
  const [filteredProblems, setFilteredProblems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedDifficulty, setSelectedDifficulty] = useState('all');
  const [selectedCategory, setSelectedCategory] = useState('all');

  const difficulties = [
    { id: 'all', name: '전체', color: 'default' },
    { id: 'easy', name: '쉬움', color: 'default' },
    { id: 'medium', name: '보통', color: 'secondary' },
    { id: 'hard', name: '어려움', color: 'destructive' }
  ];

  const categories = [
    { id: 'all', name: '전체 카테고리' },
    { id: 'Python 기초', name: 'Python 기초' },
    { id: '데이터 분석', name: '데이터 분석' },
    { id: '웹 크롤링', name: '웹 크롤링' },
    { id: '알고리즘', name: '알고리즘' }
  ];

  useEffect(() => {
    loadProblems();
  }, []);

  useEffect(() => {
    filterProblems();
  }, [problems, searchQuery, selectedDifficulty, selectedCategory]);

  const loadProblems = async () => {
    try {
      setLoading(true);
      
      // 실제 API 호출
      const data = await getProblems({
        limit: 50,
        offset: 0
      });
      setProblems(data);
    } catch (error) {
      console.error('Failed to load problems:', error);
      setProblems([]);
      // 에러 토스트나 다른 에러 처리 로직 추가 가능
    } finally {
      setLoading(false);
    }
  };

  const filterProblems = () => {
    let filtered = [...problems];

    // 검색어 필터링
    if (searchQuery) {
      filtered = filtered.filter(problem =>
        problem.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
        problem.category.toLowerCase().includes(searchQuery.toLowerCase())
      );
    }

    // 난이도 필터링
    if (selectedDifficulty !== 'all') {
      filtered = filtered.filter(problem => problem.difficulty === selectedDifficulty);
    }

    // 카테고리 필터링
    if (selectedCategory !== 'all') {
      filtered = filtered.filter(problem => problem.category === selectedCategory);
    }

    setFilteredProblems(filtered);
  };

  const handleProblemClick = (problemId) => {
    navigate(`/code/${problemId}`);
  };

  const getDifficultyBadge = (difficulty) => {
    const config = difficulties.find(d => d.id === difficulty);
    return config || { color: 'default', name: difficulty };
  };

  const getAcceptanceColor = (rate) => {
    if (rate >= 80) return 'text-green-600';
    if (rate >= 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 p-8">
        <div className="max-w-6xl mx-auto">
          <div className="flex items-center justify-center h-64">
            <div className="text-center">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
              <p className="text-gray-600">문제 목록을 불러오는 중...</p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-6xl mx-auto">
        {/* 헤더 */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 flex items-center">
                <Code2 className="w-8 h-8 mr-3 text-blue-600" />
                코딩 테스트 문제
              </h1>
              <p className="text-gray-600 mt-2">실제 코드를 작성하고 실행해볼 수 있는 문제들입니다.</p>
            </div>
            
            <Button
              onClick={() => navigate('/code')}
              className="flex items-center space-x-2"
            >
              <Play className="w-4 h-4" />
              <span>샘플 문제 체험하기</span>
            </Button>
          </div>

          {/* 통계 카드들 */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
            <Card>
              <CardContent className="pt-6">
                <div className="flex items-center">
                  <div className="p-2 bg-blue-100 rounded-lg">
                    <Code2 className="w-6 h-6 text-blue-600" />
                  </div>
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-600">전체 문제</p>
                    <p className="text-2xl font-bold text-gray-900">{problems.length}</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="pt-6">
                <div className="flex items-center">
                  <div className="p-2 bg-green-100 rounded-lg">
                    <CheckCircle className="w-6 h-6 text-green-600" />
                  </div>
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-600">해결한 문제</p>
                    <p className="text-2xl font-bold text-gray-900">
                      {problems.filter(p => p.solved).length}
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="pt-6">
                <div className="flex items-center">
                  <div className="p-2 bg-yellow-100 rounded-lg">
                    <TrendingUp className="w-6 h-6 text-yellow-600" />
                  </div>
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-600">평균 정답률</p>
                    <p className="text-2xl font-bold text-gray-900">
                      {problems.length > 0 
                        ? (problems.reduce((sum, p) => sum + p.acceptance_rate, 0) / problems.length).toFixed(1)
                        : '0.0'
                      }%
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="pt-6">
                <div className="flex items-center">
                  <div className="p-2 bg-purple-100 rounded-lg">
                    <Star className="w-6 h-6 text-purple-600" />
                  </div>
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-600">추천 문제</p>
                    <p className="text-2xl font-bold text-gray-900">5</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* 필터 및 검색 */}
          <Card>
            <CardContent className="pt-6">
              <div className="flex flex-col md:flex-row gap-4">
                {/* 검색 */}
                <div className="flex-1">
                  <div className="relative">
                    <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                    <Input
                      placeholder="문제 제목이나 카테고리로 검색..."
                      value={searchQuery}
                      onChange={(e) => setSearchQuery(e.target.value)}
                      className="pl-10"
                    />
                  </div>
                </div>

                {/* 난이도 필터 */}
                <div className="flex items-center space-x-2">
                  <Filter className="w-4 h-4 text-gray-500" />
                  <select
                    value={selectedDifficulty}
                    onChange={(e) => setSelectedDifficulty(e.target.value)}
                    className="px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    {difficulties.map((difficulty) => (
                      <option key={difficulty.id} value={difficulty.id}>
                        {difficulty.name}
                      </option>
                    ))}
                  </select>
                </div>

                {/* 카테고리 필터 */}
                <div>
                  <select
                    value={selectedCategory}
                    onChange={(e) => setSelectedCategory(e.target.value)}
                    className="px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    {categories.map((category) => (
                      <option key={category.id} value={category.id}>
                        {category.name}
                      </option>
                    ))}
                  </select>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* 문제 목록 */}
        <div className="grid gap-4">
          {filteredProblems.length === 0 ? (
            <Card>
              <CardContent className="pt-6">
                <div className="text-center py-8">
                  <Code2 className="w-16 h-16 mx-auto mb-4 text-gray-400" />
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">
                    {searchQuery || selectedDifficulty !== 'all' || selectedCategory !== 'all'
                      ? '검색 결과가 없습니다'
                      : '문제가 없습니다'
                    }
                  </h3>
                  <p className="text-gray-600">
                    {searchQuery || selectedDifficulty !== 'all' || selectedCategory !== 'all'
                      ? '다른 검색 조건을 시도해보세요.'
                      : '곧 새로운 문제들이 추가될 예정입니다.'
                    }
                  </p>
                </div>
              </CardContent>
            </Card>
          ) : (
            filteredProblems.map((problem) => (
              <Card 
                key={problem.id} 
                className="hover:shadow-lg transition-shadow cursor-pointer"
                onClick={() => handleProblemClick(problem.id)}
              >
                <CardContent className="pt-6">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-4">
                      {/* 문제 상태 아이콘 */}
                      <div className="flex-shrink-0">
                        {problem.solved ? (
                          <CheckCircle className="w-6 h-6 text-green-500" />
                        ) : (
                          <Circle className="w-6 h-6 text-gray-400" />
                        )}
                      </div>

                      {/* 문제 정보 */}
                      <div>
                        <div className="flex items-center space-x-3 mb-2">
                          <h3 className="text-lg font-semibold text-gray-900 hover:text-blue-600">
                            {problem.title}
                          </h3>
                          <Badge variant={getDifficultyBadge(problem.difficulty).color}>
                            {getDifficultyBadge(problem.difficulty).name}
                          </Badge>
                          <Badge variant="outline">
                            {problem.category}
                          </Badge>
                        </div>
                        
                        <div className="flex items-center space-x-4 text-sm text-gray-600">
                          <span className="flex items-center">
                            <TrendingUp className="w-4 h-4 mr-1" />
                            정답률: <span className={`ml-1 font-medium ${getAcceptanceColor(problem.acceptance_rate)}`}>
                              {problem.acceptance_rate}%
                            </span>
                          </span>
                          <span className="flex items-center">
                            <Clock className="w-4 h-4 mr-1" />
                            예상 소요시간: 15-30분
                          </span>
                        </div>
                      </div>
                    </div>

                    {/* 실행 버튼 */}
                    <Button
                      size="sm"
                      className="flex items-center space-x-2"
                      onClick={(e) => {
                        e.stopPropagation();
                        handleProblemClick(problem.id);
                      }}
                    >
                      <Play className="w-4 h-4" />
                      <span>문제 풀기</span>
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))
          )}
        </div>

        {/* 더 보기 버튼 (페이지네이션) */}
        {filteredProblems.length > 0 && problems.length > filteredProblems.length && (
          <div className="mt-8 text-center">
            <Button variant="outline" onClick={loadProblems}>
              더 많은 문제 보기
            </Button>
          </div>
        )}
      </div>
    </div>
  );
};

export default CodeProblemsPage;
