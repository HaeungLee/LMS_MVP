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
      // 실제 API 호출 시뮬레이션 - 지연 제거됨
      // await new Promise(resolve => setTimeout(resolve, 2000));
      
      // 모킹 분석 결과
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
            message: '일부 함수가 너무 길어질 수 있습니다',
            line: 15,
            severity: 'medium'
          },
          {
            type: 'suggestion',
            message: '타입 힌트를 추가하면 코드 안정성이 향상됩니다',
            line: 8,
            severity: 'low'
          },
          {
            type: 'error',
            message: '잠재적인 null 참조 오류가 있습니다',
            line: 22,
            severity: 'high'
          }
        ],
        suggestions: [
          "함수를 더 작은 단위로 분리하세요",
          "타입 힌트를 추가하세요",
          "예외 처리를 강화하세요",
          "코드 주석을 추가하세요"
        ],
        improved_code: `# 개선된 코드 예시
def process_data(data: list) -> dict:
    """데이터를 처리하는 함수"""
    if not data:
        raise ValueError("데이터가 비어있습니다")
    
    result = {}
    for item in data:
        if item is not None:
            result[item.id] = item.value
    
    return result`
      };
      
      return mockResult;
    },
    onSuccess: (result) => {
      setAnalysisResult(result);
      toast.success(`코드 분석 완료! 점수: ${result.overall_score}/100`);
    },
    onError: (error) => {
      toast.error('코드 분석 중 오류가 발생했습니다');
      console.error('Analysis error:', error);
    }
  });

  const handleAnalyze = () => {
    if (!code.trim()) {
      toast.error('분석할 코드를 입력해주세요');
      return;
    }
    
    analysisMutation.mutate({
      code,
      language,
      analysis_type: analysisType
    });
  };

  return (
    <div className="space-y-6">
      {/* 헤더 */}
      <div className="text-center">
        <div className="flex items-center justify-center mb-4">
          <div className="w-12 h-12 bg-purple-600 rounded-xl flex items-center justify-center">
            <Code className="w-7 h-7 text-white" />
          </div>
        </div>
        <h2 className="text-2xl font-bold text-gray-900 mb-2">AI 코드 분석기</h2>
        <p className="text-gray-600">코드의 품질을 분석하고 개선점을 제안받으세요</p>
      </div>

      {/* 코드 입력 영역 */}
      <div className="bg-white rounded-xl shadow-lg p-6">
        <div className="space-y-4">
          {/* 언어 및 분석 타입 선택 */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                프로그래밍 언어
              </label>
              <select
                value={language}
                onChange={(e) => setLanguage(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              >
                <option value="python">Python</option>
                <option value="javascript">JavaScript</option>
                <option value="typescript">TypeScript</option>
                <option value="java">Java</option>
                <option value="cpp">C++</option>
                <option value="csharp">C#</option>
                <option value="go">Go</option>
                <option value="rust">Rust</option>
              </select>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                분석 타입
              </label>
              <select
                value={analysisType}
                onChange={(e) => setAnalysisType(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              >
                <option value="general">일반 분석</option>
                <option value="performance">성능 분석</option>
                <option value="security">보안 분석</option>
                <option value="style">코드 스타일</option>
                <option value="complexity">복잡도 분석</option>
              </select>
            </div>
          </div>

          {/* 코드 입력 */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              분석할 코드
            </label>
            <textarea
              value={code}
              onChange={(e) => setCode(e.target.value)}
              placeholder="분석하고 싶은 코드를 입력하세요..."
              className="w-full h-64 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent font-mono text-sm"
            />
          </div>

          {/* 분석 버튼 */}
          <button
            onClick={handleAnalyze}
            disabled={analysisMutation.isPending || !code.trim()}
            className="w-full bg-purple-600 text-white py-3 px-4 rounded-lg hover:bg-purple-700 focus:ring-2 focus:ring-purple-500 focus:ring-offset-2 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors flex items-center justify-center"
          >
            {analysisMutation.isPending ? (
              <>
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2"></div>
                분석 중...
              </>
            ) : (
              <>
                <Play className="w-4 h-4 mr-2" />
                코드 분석하기
              </>
            )}
          </button>
        </div>
      </div>

      {/* 분석 결과 */}
      {analysisResult && (
        <div className="bg-white rounded-xl shadow-lg p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
            <Target className="w-5 h-5 mr-2 text-purple-600" />
            분석 결과
          </h3>

          {/* 전체 점수 */}
          <div className="mb-6">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium text-gray-700">전체 점수</span>
              <span className="text-2xl font-bold text-purple-600">{analysisResult.overall_score}/100</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div
                className="bg-purple-600 h-2 rounded-full transition-all duration-500"
                style={{ width: `${analysisResult.overall_score}%` }}
              ></div>
            </div>
          </div>

          {/* 강점 */}
          <div className="mb-6">
            <h4 className="text-md font-semibold text-green-700 mb-3 flex items-center">
              <CheckCircle className="w-4 h-4 mr-2" />
              강점 ({analysisResult.strengths.length})
            </h4>
            <div className="space-y-2">
              {analysisResult.strengths.map((strength, index) => (
                <div key={index} className="flex items-start">
                  <CheckCircle className="w-4 h-4 text-green-500 mr-2 mt-0.5 flex-shrink-0" />
                  <span className="text-sm text-gray-700">{strength}</span>
                </div>
              ))}
            </div>
          </div>

          {/* 문제점 */}
          <div className="mb-6">
            <h4 className="text-md font-semibold text-red-700 mb-3 flex items-center">
              <Bug className="w-4 h-4 mr-2" />
              발견된 문제 ({analysisResult.issues.length})
            </h4>
            <div className="space-y-3">
              {analysisResult.issues.map((issue, index) => (
                <div key={index} className="border border-gray-200 rounded-lg p-3">
                  <div className="flex items-start justify-between mb-1">
                    <div className="flex items-center">
                      {issue.type === 'error' && <AlertCircle className="w-4 h-4 text-red-500 mr-2" />}
                      {issue.type === 'warning' && <AlertCircle className="w-4 h-4 text-yellow-500 mr-2" />}
                      {issue.type === 'suggestion' && <Lightbulb className="w-4 h-4 text-blue-500 mr-2" />}
                      <span className={`text-sm font-medium capitalize ${
                        issue.type === 'error' ? 'text-red-700' :
                        issue.type === 'warning' ? 'text-yellow-700' : 'text-blue-700'
                      }`}>
                        {issue.type}
                      </span>
                    </div>
                    <span className={`text-xs px-2 py-1 rounded-full ${
                      issue.severity === 'high' ? 'bg-red-100 text-red-700' :
                      issue.severity === 'medium' ? 'bg-yellow-100 text-yellow-700' : 'bg-blue-100 text-blue-700'
                    }`}>
                      {issue.severity}
                    </span>
                  </div>
                  <p className="text-sm text-gray-700">{issue.message}</p>
                  {issue.line && (
                    <p className="text-xs text-gray-500 mt-1">라인 {issue.line}</p>
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* 개선 제안 */}
          <div className="mb-6">
            <h4 className="text-md font-semibold text-blue-700 mb-3 flex items-center">
              <Lightbulb className="w-4 h-4 mr-2" />
              개선 제안 ({analysisResult.suggestions.length})
            </h4>
            <div className="space-y-2">
              {analysisResult.suggestions.map((suggestion, index) => (
                <div key={index} className="flex items-start">
                  <Zap className="w-4 h-4 text-blue-500 mr-2 mt-0.5 flex-shrink-0" />
                  <span className="text-sm text-gray-700">{suggestion}</span>
                </div>
              ))}
            </div>
          </div>

          {/* 개선된 코드 */}
          {analysisResult.improved_code && (
            <div>
              <h4 className="text-md font-semibold text-purple-700 mb-3 flex items-center">
                <Code className="w-4 h-4 mr-2" />
                개선된 코드
              </h4>
              <div className="bg-gray-50 rounded-lg p-4">
                <pre className="text-sm text-gray-700 overflow-x-auto">
                  <code>{analysisResult.improved_code}</code>
                </pre>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}