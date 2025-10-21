/**
 * 실습 섹션 - 코딩 문제 풀이
 */

import { useState } from 'react';
import { Code, CheckCircle, Play, AlertCircle } from 'lucide-react';

interface PracticeSectionProps {
  problems: any[];
  onComplete: () => void;
}

export default function PracticeSection({ problems, onComplete }: PracticeSectionProps) {
  const [code, setCode] = useState('');
  const [result, setResult] = useState<any>(null);
  const [isCompleted, setIsCompleted] = useState(false);

  const handleRun = () => {
    // 실제 코드 실행은 백엔드 API 호출 필요
    if (!problem.title || problem.title === "실습 문제 준비 중") {
      setResult({
        success: false,
        output: "실습 문제를 먼저 불러와주세요.",
        passed: 0,
        total: 0
      });
      return;
    }
    
    // TODO: 백엔드 코드 실행 API 호출
    setResult({
      success: false,
      output: "코드 실행 기능은 개발 중입니다.\n현재는 교재를 통해 학습해주세요.",
      passed: 0,
      total: 0
    });
  };

  const handleComplete = () => {
    setIsCompleted(true);
    onComplete();
  };

  // 문제가 없으면 안내 메시지
  const defaultProblem = {
    title: "실습 문제 준비 중",
    description: "커리큘럼에서 실습 문제를 불러오고 있습니다. 잠시만 기다려주세요.",
    starter_code: `# 실습 문제를 불러오는 중입니다...\n`
  };

  const problem = problems?.[0] || defaultProblem;

  return (
    <div className="bg-white rounded-2xl shadow-lg p-8">
      {/* 헤더 */}
      <div className="flex items-center gap-3 mb-6 pb-4 border-b border-gray-200">
        <div className="w-12 h-12 bg-gradient-to-br from-purple-500 to-pink-500 rounded-xl flex items-center justify-center">
          <Code className="w-6 h-6 text-white" />
        </div>
        <div>
          <h2 className="text-2xl font-bold text-gray-900">💻 실습 코딩</h2>
          <p className="text-sm text-gray-600">직접 코드를 작성해보세요</p>
        </div>
      </div>

      {/* 문제 설명 */}
      <div className="mb-6">
        <h3 className="text-lg font-bold text-gray-900 mb-2">{problem.title}</h3>
        <p className="text-gray-600">{problem.description}</p>
      </div>

      {/* 코드 에디터 */}
      <div className="mb-4">
        <div className="bg-gray-900 rounded-xl overflow-hidden">
          <div className="bg-gray-800 px-4 py-2 flex items-center justify-between">
            <span className="text-sm text-gray-400">Python</span>
            <button
              onClick={handleRun}
              className="px-4 py-1 bg-green-600 text-white rounded-lg text-sm hover:bg-green-700 flex items-center gap-2"
            >
              <Play className="w-4 h-4" />
              실행
            </button>
          </div>
          <textarea
            value={code || problem.starter_code}
            onChange={(e) => setCode(e.target.value)}
            className="w-full h-64 p-4 bg-gray-900 text-gray-100 font-mono text-sm resize-none focus:outline-none"
            placeholder="여기에 코드를 작성하세요..."
          />
        </div>
      </div>

      {/* 실행 결과 */}
      {result && (
        <div className={`mb-6 p-4 rounded-xl ${result.success ? 'bg-green-50 border-2 border-green-200' : 'bg-red-50 border-2 border-red-200'}`}>
          <div className="flex items-center gap-2 mb-2">
            {result.success ? (
              <CheckCircle className="w-5 h-5 text-green-600" />
            ) : (
              <AlertCircle className="w-5 h-5 text-red-600" />
            )}
            <h4 className={`font-bold ${result.success ? 'text-green-900' : 'text-red-900'}`}>
              {result.success ? '✅ 성공!' : '❌ 실패'}
            </h4>
          </div>
          <pre className="text-sm font-mono text-gray-700 whitespace-pre-wrap">
            {result.output}
          </pre>
          {result.success && (
            <p className="text-sm text-green-700 mt-2">
              테스트 케이스: {result.passed}/{result.total} 통과
            </p>
          )}
        </div>
      )}

      {/* 완료 버튼 */}
      <div className="mt-8 pt-6 border-t border-gray-200">
        {!isCompleted ? (
          <button
            onClick={handleComplete}
            disabled={!result?.success}
            className="w-full bg-gradient-to-r from-purple-600 to-pink-600 text-white py-4 px-6 rounded-xl hover:shadow-lg transition-all duration-200 flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <CheckCircle className="w-5 h-5" />
            <span className="font-semibold">실습 완료! 다음으로</span>
          </button>
        ) : (
          <div className="w-full bg-green-50 text-green-700 py-4 px-6 rounded-xl flex items-center justify-center gap-2">
            <CheckCircle className="w-5 h-5" />
            <span className="font-semibold">✅ 완료했습니다!</span>
          </div>
        )}
      </div>
    </div>
  );
}
