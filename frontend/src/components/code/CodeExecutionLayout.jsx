import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { 
  Play, 
  Square, 
  Settings, 
  Code, 
  Terminal,
  Clock,
  HardDrive,
  CheckCircle,
  XCircle,
  List
} from 'lucide-react';

const CodeExecutionLayout = ({ 
  problem, 
  onCodeRun, 
  onCodeSubmit,
  isRunning = false 
}) => {
  const [selectedLanguage, setSelectedLanguage] = useState('python');
  const [code, setCode] = useState(problem?.template || '');
  const [executionResult, setExecutionResult] = useState(null);

  const languages = [
    { id: 'python', name: 'Python', version: '3.11' },
    { id: 'javascript', name: 'JavaScript', version: 'ES2022' },
    { id: 'sql', name: 'SQL', version: 'PostgreSQL' }
  ];

  const handleRunCode = async () => {
    if (onCodeRun) {
      const result = await onCodeRun(code, selectedLanguage);
      setExecutionResult(result);
    }
  };

  const handleSubmitCode = async () => {
    if (onCodeSubmit) {
      await onCodeSubmit(code, selectedLanguage);
    }
  };

  return (
    <div className="min-h-screen flex bg-gray-50">
      {/* 좌측 패널 - 문제 설명 */}
      <div className="w-1/2 border-r border-gray-200 bg-white overflow-y-auto">
        <div className="p-6">
          {/* 문제 헤더 */}
          <div className="mb-6">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center space-x-4">
                <h1 className="text-xl font-bold text-gray-900">
                  {problem?.title || '문제 제목'}
                </h1>
                <Link to="/code/problems">
                  <Button variant="outline" size="sm" className="flex items-center space-x-2">
                    <List className="w-4 h-4" />
                    <span>문제 목록</span>
                  </Button>
                </Link>
              </div>
              <div className="flex items-center space-x-2">
                <Badge 
                  variant={problem?.difficulty === 'easy' ? 'default' : 
                          problem?.difficulty === 'medium' ? 'secondary' : 'destructive'}
                >
                  {problem?.difficulty || 'medium'}
                </Badge>
                <Badge variant="outline">
                  {problem?.category || 'Python 기초'}
                </Badge>
              </div>
            </div>
            
            {/* 문제 메타정보 */}
            <div className="flex items-center space-x-4 text-sm text-gray-600 pb-4 border-b border-gray-200">
              <span className="flex items-center">
                <Clock className="w-4 h-4 mr-1" />
                시간 제한: {problem?.timeLimit || '10초'}
              </span>
              <span className="flex items-center">
                <HardDrive className="w-4 h-4 mr-1" />
                메모리 제한: {problem?.memoryLimit || '128MB'}
              </span>
            </div>
          </div>

          {/* 문제 내용 */}
          <div className="space-y-6">
            {/* 문제 설명 */}
            <section>
              <h3 className="text-lg font-semibold mb-3">문제 설명</h3>
              <div className="prose prose-sm max-w-none text-gray-700">
                {problem?.description || '문제 설명이 여기에 표시됩니다.'}
              </div>
            </section>

            {/* 입출력 예제 */}
            {problem?.examples && problem.examples.length > 0 && (
              <section>
                <h3 className="text-lg font-semibold mb-3">입출력 예제</h3>
                <div className="space-y-4">
                  {problem.examples.map((example, index) => (
                    <div key={index} className="bg-gray-50 rounded-lg p-4">
                      <div className="grid grid-cols-2 gap-4">
                        <div>
                          <h4 className="font-medium text-gray-900 mb-2">입력</h4>
                          <pre className="bg-white p-3 rounded border text-sm overflow-x-auto">
                            {example.input}
                          </pre>
                        </div>
                        <div>
                          <h4 className="font-medium text-gray-900 mb-2">출력</h4>
                          <pre className="bg-white p-3 rounded border text-sm overflow-x-auto">
                            {example.output}
                          </pre>
                        </div>
                      </div>
                      {example.explanation && (
                        <div className="mt-3">
                          <h4 className="font-medium text-gray-900 mb-2">설명</h4>
                          <p className="text-gray-600 text-sm">{example.explanation}</p>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </section>
            )}

            {/* 제약 조건 */}
            {problem?.constraints && (
              <section>
                <h3 className="text-lg font-semibold mb-3">제약 조건</h3>
                <ul className="space-y-1 text-gray-700 text-sm">
                  {problem.constraints.map((constraint, index) => (
                    <li key={index} className="flex items-start">
                      <span className="text-gray-400 mr-2">•</span>
                      <span>{constraint}</span>
                    </li>
                  ))}
                </ul>
              </section>
            )}

            {/* 힌트 */}
            {problem?.hints && problem.hints.length > 0 && (
              <section>
                <h3 className="text-lg font-semibold mb-3">힌트</h3>
                <div className="space-y-2">
                  {problem.hints.map((hint, index) => (
                    <div key={index} className="bg-blue-50 border border-blue-200 rounded-lg p-3">
                      <p className="text-blue-800 text-sm">{hint}</p>
                    </div>
                  ))}
                </div>
              </section>
            )}
          </div>
        </div>
      </div>

      {/* 우측 패널 - 코드 에디터 및 실행 */}
      <div className="w-1/2 flex flex-col bg-white">
        {/* 상단 툴바 */}
        <div className="p-4 border-b border-gray-200 bg-gray-50">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              {/* 언어 선택 */}
              <div className="flex items-center space-x-2">
                <label className="text-sm font-medium text-gray-700">언어:</label>
                <select
                  value={selectedLanguage}
                  onChange={(e) => setSelectedLanguage(e.target.value)}
                  className="px-3 py-1 border border-gray-300 rounded text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  {languages.map((lang) => (
                    <option key={lang.id} value={lang.id}>
                      {lang.name} ({lang.version})
                    </option>
                  ))}
                </select>
              </div>
            </div>

            {/* 실행/제출 버튼 */}
            <div className="flex items-center space-x-2">
              <Button
                onClick={handleRunCode}
                disabled={isRunning}
                size="sm"
                className="flex items-center space-x-2"
              >
                {isRunning ? (
                  <Square className="w-4 h-4" />
                ) : (
                  <Play className="w-4 h-4" />
                )}
                <span>{isRunning ? '실행 중...' : '실행'}</span>
              </Button>
              
              <Button
                onClick={handleSubmitCode}
                disabled={isRunning}
                size="sm"
                variant="outline"
                className="flex items-center space-x-2"
              >
                <Code className="w-4 h-4" />
                <span>제출</span>
              </Button>
            </div>
          </div>
        </div>

        {/* 코드 에디터 영역 */}
        <div className="flex-1 p-4">
          <Card className="h-full">
            <CardHeader className="py-3">
              <CardTitle className="text-sm">코드 작성</CardTitle>
            </CardHeader>
            <CardContent className="h-full p-0">
              <textarea
                value={code}
                onChange={(e) => setCode(e.target.value)}
                placeholder={`${selectedLanguage === 'python' ? '# 여기에 Python 코드를 작성하세요' : 
                             selectedLanguage === 'javascript' ? '// 여기에 JavaScript 코드를 작성하세요' :
                             '-- 여기에 SQL 쿼리를 작성하세요'}`}
                className="w-full h-full p-4 font-mono text-sm border-0 resize-none focus:outline-none"
                style={{ minHeight: '300px' }}
              />
            </CardContent>
          </Card>
        </div>

        {/* 실행 결과 영역 */}
        <div className="h-1/3 border-t border-gray-200 p-4">
          <Card className="h-full">
            <CardHeader className="py-3">
              <CardTitle className="text-sm flex items-center">
                <Terminal className="w-4 h-4 mr-2" />
                실행 결과
              </CardTitle>
            </CardHeader>
            <CardContent className="h-full overflow-y-auto">
              {executionResult ? (
                <div className="space-y-3">
                  {/* 실행 상태 */}
                  <div className="flex items-center space-x-2">
                    {executionResult.success ? (
                      <CheckCircle className="w-5 h-5 text-green-500" />
                    ) : (
                      <XCircle className="w-5 h-5 text-red-500" />
                    )}
                    <span className={`font-medium ${executionResult.success ? 'text-green-700' : 'text-red-700'}`}>
                      {executionResult.success ? '실행 성공' : '실행 실패'}
                    </span>
                  </div>

                  {/* 출력 결과 */}
                  {executionResult.output && (
                    <div>
                      <h4 className="font-medium text-gray-900 mb-2">출력:</h4>
                      <pre className="bg-gray-50 p-3 rounded text-sm overflow-x-auto border">
                        {executionResult.output}
                      </pre>
                    </div>
                  )}

                  {/* 에러 메시지 */}
                  {executionResult.error && (
                    <div>
                      <h4 className="font-medium text-red-700 mb-2">오류:</h4>
                      <pre className="bg-red-50 border border-red-200 p-3 rounded text-sm overflow-x-auto text-red-700">
                        {executionResult.error}
                      </pre>
                    </div>
                  )}

                  {/* 실행 통계 */}
                  {executionResult.stats && (
                    <div className="flex items-center space-x-4 text-sm text-gray-600 pt-2 border-t">
                      <span className="flex items-center">
                        <Clock className="w-3 h-3 mr-1" />
                        실행 시간: {executionResult.stats.executionTime}ms
                      </span>
                      <span className="flex items-center">
                        <HardDrive className="w-3 h-3 mr-1" />
                        메모리: {executionResult.stats.memoryUsage}MB
                      </span>
                    </div>
                  )}
                </div>
              ) : (
                <div className="flex items-center justify-center h-full text-gray-500">
                  <div className="text-center">
                    <Terminal className="w-8 h-8 mx-auto mb-2 text-gray-400" />
                    <p className="text-sm">코드를 실행하면 결과가 여기에 표시됩니다</p>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default CodeExecutionLayout;
