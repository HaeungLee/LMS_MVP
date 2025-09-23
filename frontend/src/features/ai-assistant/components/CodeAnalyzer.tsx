import React, { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { Code, Play, CheckCircle, AlertCircle, Lightbulb, Bug, Target, Zap } from 'lucide-react';
import { toast } from 'react-hot-toast';

interface CodeAnalysisResult {
  overall_score: number;
  strengths: string[];
  issues: Array<{
    type: 'error' | 'warning' | 'suggestion';
    message: string;
    line?: number;
    severity: 'high' | 'medium' | 'low';
  }>;
  suggestions: string[];
  improved_code?: string;
}

export default function CodeAnalyzer() {
  const [code, setCode] = useState('');
  const [language, setLanguage] = useState('python');
  const [analysisType, setAnalysisType] = useState('general');
  const [analysisResult, setAnalysisResult] = useState<CodeAnalysisResult | null>(null);

  // 코드 분석 mutation
  const analysisMutation = useMutation({
    mutationFn: async (data: { code: string; language: string; analysis_type: string }) => {
      // 모킹 분석 결과 (실제 API 연결 시 이 부분을 교체)
      const mockResult: CodeAnalysisResult = {
        overall_score: 78,
        strengths: [
          "코드 구조가 명확하고 읽기 쉽습니다",
          "적절한 변수명을 사용했습니다",
          "함수 분리가 잘 되어 있습니다"
        ],
        issues: [
          {
            type: 'warning',
            message: '예외 처리가 누락되어 있습니다',
            line: 12,
            severity: 'medium'
          },
          {
            type: 'suggestion',
            message: '더 효율적인 알고리즘을 사용할 수 있습니다',
            severity: 'low'
          },
          {
            type: 'error',
            message: '변수가 사용되기 전에 선언되지 않았습니다',
            line: 8,
            severity: 'high'
          }
        ],
        suggestions: [
          "try-catch 문을 추가하여 예외 처리를 강화하세요",
          "코드에 주석을 추가하여 가독성을 높이세요",
          "함수의 복잡도를 줄이기 위해 더 작은 함수로 분리하세요",
          "타입 힌트를 추가하여 코드의 안정성을 높이세요"
        ],
        improved_code: data.code // 실제로는 개선된 코드가 반환됨
      };

      return mockResult;
    },
    onSuccess: (data) => {
      setAnalysisResult(data);
      toast.success('코드 분석이 완료되었습니다!');
    },
    onError: (error: any) => {
      toast.error(`분석 실패: ${error.message}`);
    },
  });

  const handleAnalyze = () => {
    if (!code.trim()) {
      toast.error('분석할 코드를 입력해주세요');
      return;
    }

    analysisMutation.mutate({
      code: code.trim(),
      language,
      analysis_type: analysisType
    });
  };

  const getIssueIcon = (type: string) => {
    switch (type) {
      case 'error': return <AlertCircle className="w-4 h-4 text-red-600" />;
      case 'warning': return <AlertCircle className="w-4 h-4 text-yellow-600" />;
      case 'suggestion': return <Lightbulb className="w-4 h-4 text-blue-600" />;
      default: return <AlertCircle className="w-4 h-4 text-gray-600" />;
    }
  };

  const getIssueColor = (type: string) => {
    switch (type) {
      case 'error': return 'bg-red-50 border-red-200';
      case 'warning': return 'bg-yellow-50 border-yellow-200';
      case 'suggestion': return 'bg-blue-50 border-blue-200';
      default: return 'bg-gray-50 border-gray-200';
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'high': return 'text-red-600';
      case 'medium': return 'text-yellow-600';
      case 'low': return 'text-green-600';
      default: return 'text-gray-600';
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 90) return 'text-green-600';
    if (score >= 70) return 'text-yellow-600';
    return 'text-red-600';
  };

  return (
    <div className="max-w-6xl mx-auto space-y-8">
      {/* 헤더 */}
      <div className="bg-gradient-to-r from-purple-600 to-blue-600 rounded-lg p-6 text-white">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold mb-2">AI 코드 분석기</h1>
            <p className="text-purple-100">
              코드를 분석하여 개선점과 최적화 방안을 제안해드립니다
            </p>
          </div>
          <Code className="w-16 h-16 text-purple-200" />
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* 코드 입력 영역 */}
        <div className="bg-white rounded-lg p-6 shadow-sm border border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">코드 입력</h3>
          
          {/* 언어 및 분석 타입 선택 */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                프로그래밍 언어
              </label>
              <select
                value={language}
                onChange={(e) => setLanguage(e.target.value)}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-purple-500"
              >
                <option value="python">Python</option>
                <option value="javascript">JavaScript</option>
                <option value="typescript">TypeScript</option>
                <option value="java">Java</option>
                <option value="cpp">C++</option>
                <option value="react">React</option>
              </select>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                분석 유형
              </label>
              <select
                value={analysisType}
                onChange={(e) => setAnalysisType(e.target.value)}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-purple-500"
              >
                <option value="general">종합 분석</option>
                <option value="performance">성능 최적화</option>
                <option value="security">보안 검사</option>
                <option value="style">코딩 스타일</option>
                <option value="bugs">버그 탐지</option>
              </select>
            </div>
          </div>

          {/* 코드 입력 */}
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              분석할 코드
            </label>
            <textarea
              value={code}
              onChange={(e) => setCode(e.target.value)}
              rows={12}
              placeholder={`${language} 코드를 입력하세요...

예시:
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

print(fibonacci(10))`}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 font-mono text-sm focus:outline-none focus:ring-2 focus:ring-purple-500"
            />
          </div>

          {/* 분석 버튼 */}
          <button
            onClick={handleAnalyze}
            disabled={analysisMutation.isPending || !code.trim()}
            className="w-full bg-purple-600 text-white py-3 px-4 rounded-lg hover:bg-purple-700 disabled:bg-gray-300 disabled:cursor-not-allowed flex items-center justify-center"
          >
            {analysisMutation.isPending ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                분석 중...
              </>
            ) : (
              <>
                <Play className="w-4 h-4 mr-2" />
                코드 분석 시작
              </>
            )}
          </button>
        </div>

        {/* 분석 결과 영역 */}
        <div className="bg-white rounded-lg p-6 shadow-sm border border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">분석 결과</h3>
          
          {!analysisResult ? (
            <div className="text-center py-12">
              <Code className="w-16 h-16 text-gray-300 mx-auto mb-4" />
              <h4 className="text-lg font-medium text-gray-500 mb-2">분석 결과 대기중</h4>
              <p className="text-gray-400">
                코드를 입력하고 분석을 시작해주세요
              </p>
            </div>
          ) : (
            <div className="space-y-6">
              {/* 전체 점수 */}
              <div className="bg-gray-50 rounded-lg p-4">
                <div className="flex items-center justify-between">
                  <h4 className="text-md font-semibold text-gray-900">전체 점수</h4>
                  <div className={`text-2xl font-bold ${getScoreColor(analysisResult.overall_score)}`}>
                    {analysisResult.overall_score}/100
                  </div>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2 mt-2">
                  <div 
                    className="bg-purple-600 h-2 rounded-full transition-all duration-300"
                    style={{ width: `${analysisResult.overall_score}%` }}
                  ></div>
                </div>
              </div>

              {/* 장점 */}
              {analysisResult.strengths.length > 0 && (
                <div>
                  <h4 className="text-md font-semibold text-gray-900 mb-3 flex items-center">
                    <CheckCircle className="w-5 h-5 text-green-600 mr-2" />
                    잘한 점
                  </h4>
                  <div className="space-y-2">
                    {analysisResult.strengths.map((strength, index) => (
                      <div key={index} className="bg-green-50 border border-green-200 rounded-lg p-3">
                        <p className="text-green-800 text-sm">{strength}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* 문제점 및 개선사항 */}
              {analysisResult.issues.length > 0 && (
                <div>
                  <h4 className="text-md font-semibold text-gray-900 mb-3 flex items-center">
                    <Bug className="w-5 h-5 text-red-600 mr-2" />
                    발견된 문제
                  </h4>
                  <div className="space-y-3">
                    {analysisResult.issues.map((issue, index) => (
                      <div key={index} className={`border rounded-lg p-3 ${getIssueColor(issue.type)}`}>
                        <div className="flex items-start">
                          {getIssueIcon(issue.type)}
                          <div className="ml-2 flex-1">
                            <div className="flex items-center justify-between">
                              <span className="text-sm font-medium capitalize">{issue.type}</span>
                              <span className={`text-xs font-medium ${getSeverityColor(issue.severity)}`}>
                                {issue.severity} 우선순위
                              </span>
                            </div>
                            <p className="text-sm text-gray-700 mt-1">{issue.message}</p>
                            {issue.line && (
                              <p className="text-xs text-gray-500 mt-1">라인 {issue.line}</p>
                            )}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* 개선 제안 */}
              {analysisResult.suggestions.length > 0 && (
                <div>
                  <h4 className="text-md font-semibold text-gray-900 mb-3 flex items-center">
                    <Target className="w-5 h-5 text-blue-600 mr-2" />
                    개선 제안
                  </h4>
                  <div className="space-y-2">
                    {analysisResult.suggestions.map((suggestion, index) => (
                      <div key={index} className="bg-blue-50 border border-blue-200 rounded-lg p-3 flex items-start">
                        <Lightbulb className="w-4 h-4 text-blue-600 mr-2 mt-0.5 flex-shrink-0" />
                        <p className="text-blue-800 text-sm">{suggestion}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      {/* 기능 설명 */}
      <div className="bg-purple-50 border border-purple-200 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-purple-900 mb-4">AI 코드 분석 기능</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="flex items-start">
            <Zap className="w-5 h-5 text-purple-600 mr-2 mt-0.5" />
            <div>
              <h4 className="text-sm font-semibold text-purple-900">성능 최적화</h4>
              <p className="text-xs text-purple-700">느린 알고리즘과 비효율적인 코드를 찾아 개선방안 제시</p>
            </div>
          </div>
          <div className="flex items-start">
            <Bug className="w-5 h-5 text-purple-600 mr-2 mt-0.5" />
            <div>
              <h4 className="text-sm font-semibold text-purple-900">버그 탐지</h4>
              <p className="text-xs text-purple-700">잠재적인 런타임 에러와 로직 오류 사전 발견</p>
            </div>
          </div>
          <div className="flex items-start">
            <CheckCircle className="w-5 h-5 text-purple-600 mr-2 mt-0.5" />
            <div>
              <h4 className="text-sm font-semibold text-purple-900">코딩 스타일</h4>
              <p className="text-xs text-purple-700">일관된 코딩 스타일과 베스트 프랙티스 준수 확인</p>
            </div>
          </div>
          <div className="flex items-start">
            <Target className="w-5 h-5 text-purple-600 mr-2 mt-0.5" />
            <div>
              <h4 className="text-sm font-semibold text-purple-900">보안 검사</h4>
              <p className="text-xs text-purple-700">보안 취약점과 위험한 코드 패턴 식별</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}