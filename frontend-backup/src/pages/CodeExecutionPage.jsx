import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import CodeExecutionLayout from '@/components/code/CodeExecutionLayout';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { ArrowLeft, BookOpen, List } from 'lucide-react';
import { executeCode, getProblem, submitCode, getSampleProblems } from '@/services/codeExecutionApi';

const CodeExecutionPage = () => {
  const { problemId } = useParams();
  const navigate = useNavigate();
  const [problem, setProblem] = useState(null);
  const [loading, setLoading] = useState(true);
  const [isRunning, setIsRunning] = useState(false);

  // 샘플 문제 데이터 (나중에 API로 교체)
  const sampleProblem = {
    id: 1,
    title: "두 수의 합",
    difficulty: "easy",
    category: "Python 기초",
    timeLimit: "10초",
    memoryLimit: "128MB",
    description: `두 개의 정수 a와 b가 주어졌을 때, a와 b의 합을 출력하는 프로그램을 작성하세요.

이 문제는 Python의 기본적인 입출력과 산술 연산을 연습하는 문제입니다.`,
    examples: [
      {
        input: "3 5",
        output: "8",
        explanation: "3과 5를 더하면 8입니다."
      },
      {
        input: "10 -2",
        output: "8", 
        explanation: "10과 -2를 더하면 8입니다."
      }
    ],
    constraints: [
      "-1000 ≤ a, b ≤ 1000",
      "a와 b는 정수입니다."
    ],
    hints: [
      "input() 함수를 사용해서 입력을 받을 수 있습니다.",
      "split() 함수를 사용해서 공백으로 구분된 값을 나눌 수 있습니다.",
      "int() 함수를 사용해서 문자열을 정수로 변환할 수 있습니다."
    ],
    template: `# 두 수의 합 구하기
# 입력: 두 개의 정수가 공백으로 구분되어 주어집니다.
# 출력: 두 수의 합을 출력하세요.

# 여기에 코드를 작성하세요
a, b = map(int, input().split())
result = a + b
print(result)`
  };

  useEffect(() => {
    const loadProblem = async () => {
      try {
        setLoading(true);
        
        if (problemId) {
          // 실제 API 호출
          const problemData = await getProblem(problemId);
          setProblem(problemData);
        } else {
          // problemId가 없는 경우 오류 처리
          throw new Error('Problem ID is required');
        }
      } catch (error) {
        console.error('Failed to load problem:', error);
        // API 실패시 에러 상태 설정 (Mock 데이터 제거)
        setProblem(null);
        // 에러 토스트나 다른 에러 처리 로직 추가 가능
      } finally {
        setLoading(false);
      }
    };

    loadProblem();
  }, [problemId]);

  const handleCodeRun = async (code, language) => {
    setIsRunning(true);
    
    try {
      // 실제 API 호출
      const result = await executeCode(code, language, '', null);
      return result;
    } catch (error) {
      console.error('Code execution failed:', error);
      return {
        success: false,
        output: null,
        error: error.message,
        execution_time_ms: 0,
        memory_usage_mb: 0
      };
    } finally {
      setIsRunning(false);
    }
  };

  const handleCodeSubmit = async (code, language) => {
    setIsRunning(true);
    
    try {
      // 실제 API 호출
      const result = await submitCode(problemId || 1, code, language);
      
      if (result.success) {
        alert(`제출 완료!\n결과: ${result.result ? '성공' : '실패'}\n${result.message}`);
        // navigate('/results/' + result.submission_id);
      } else {
        alert('제출 실패: ' + result.message);
      }
    } catch (error) {
      console.error('Code submission failed:', error);
      alert('제출 중 오류가 발생했습니다: ' + error.message);
    } finally {
      setIsRunning(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <Card className="w-96">
          <CardContent className="pt-6">
            <div className="text-center">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
              <p className="text-gray-600">문제를 불러오는 중...</p>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (!problem) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <Card className="w-96">
          <CardContent className="pt-6">
            <div className="text-center">
              <BookOpen className="w-12 h-12 mx-auto mb-4 text-gray-400" />
              <h3 className="text-lg font-semibold mb-2">문제를 찾을 수 없습니다</h3>
              <p className="text-gray-600 mb-4">요청하신 문제가 존재하지 않습니다.</p>
              <div className="space-y-2">
                <Link to="/code/problems">
                  <Button className="w-full">
                    <List className="w-4 h-4 mr-2" />
                    문제 목록 보기
                  </Button>
                </Link>
                <Button variant="outline" onClick={() => navigate('/quiz')} className="w-full">
                  <ArrowLeft className="w-4 h-4 mr-2" />
                  대시보드로 돌아가기
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="relative">
      {/* 상단 네비게이션 바 */}
      <div className="absolute top-0 left-0 right-0 z-10 bg-white border-b border-gray-200 px-6 py-3">
        <div className="flex items-center justify-between">
          <Button 
            variant="ghost" 
            size="sm"
            onClick={() => navigate('/quiz')}
            className="flex items-center space-x-2"
          >
            <ArrowLeft className="w-4 h-4" />
            <span>문제 목록</span>
          </Button>
          
          <div className="text-sm text-gray-600">
            문제 ID: {problemId || 'sample'}
          </div>
        </div>
      </div>

      {/* 메인 코드 실행 레이아웃 */}
      <div className="pt-16">
        <CodeExecutionLayout
          problem={problem}
          onCodeRun={handleCodeRun}
          onCodeSubmit={handleCodeSubmit}
          isRunning={isRunning}
        />
      </div>
    </div>
  );
};

export default CodeExecutionPage;
