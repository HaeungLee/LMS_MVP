/**
 * 실습 섹션 - 코딩 문제 풀이 (Monaco Editor 사용)
 */

import { useState, useRef } from 'react';
import Editor from '@monaco-editor/react';
import { Code, CheckCircle, Play, AlertCircle, Settings } from 'lucide-react';
import { api } from '../../../shared/services/apiClient';

interface PracticeSectionProps {
  problems: any[];
  curriculumId?: number;
  onComplete: () => void;
}

export default function PracticeSection({ problems, curriculumId, onComplete }: PracticeSectionProps) {
  const [code, setCode] = useState('');
  const [result, setResult] = useState<any>(null);
  const [isCompleted, setIsCompleted] = useState(false);
  const [isRunning, setIsRunning] = useState(false);
  const [editorTheme, setEditorTheme] = useState<'light' | 'vs-dark'>('vs-dark');
  const [showSettings, setShowSettings] = useState(false);
  const editorRef = useRef<any>(null);

  const handleRun = async () => {
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
    
    try {
      setIsRunning(true);
      setResult(null);

      const payload = {
        curriculum_id: curriculumId || 0,
        problem_id: problem.id ?? null,
        code: code || problem.starter_code || ''
      };

      const res: any = await api.post('/mvp/practice/submit', payload, { timeoutMs: 60000 });

      const isSuccess = !!res.success;
      setResult({
        success: isSuccess,
        output: res.output || '',
        error: res.error || null,
        feedback: res.feedback || '',
        passed: res.passed ?? 0,
        total: res.total ?? 0,
      });

      // 성공 시 자동 완료 처리 (3초 후)
      if (isSuccess && !isCompleted) {
        setTimeout(() => {
          handleComplete();
        }, 3000);
      }
    } catch (err: any) {
      setResult({
        success: false,
        output: err?.message || '서버 오류가 발생했습니다.',
        passed: 0,
        total: 0,
      });
    } finally {
      setIsRunning(false);
    }
  };

  const handleComplete = () => {
    setIsCompleted(true);
    onComplete();
  };

  // Monaco Editor 마운트 시
  const handleEditorDidMount = (editor: any, monaco: any) => {
    editorRef.current = editor;
    
    // Ctrl+Enter로 실행
    editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.Enter, () => {
      if (!isRunning) {
        handleRun();
      }
    });

    editor.focus();
  };

  // Monaco Editor 옵션
  const editorOptions = {
    selectOnLineNumbers: true,
    roundedSelection: false,
    readOnly: false,
    cursorStyle: 'line' as const,
    automaticLayout: true,
    wordWrap: 'on' as const,
    fontSize: 14,
    lineHeight: 20,
    minimap: {
      enabled: false
    },
    scrollBeyondLastLine: false,
    folding: true,
    foldingHighlight: true,
    showFoldingControls: 'always' as const,
    bracketPairColorization: {
      enabled: true
    },
    suggestOnTriggerCharacters: true,
    acceptSuggestionOnEnter: 'on' as const,
    tabCompletion: 'on' as const,
    mouseWheelZoom: true,
    smoothScrolling: true,
    cursorBlinking: 'smooth' as const,
    tabSize: 4,
    insertSpaces: true
  };

  // 문제가 없으면 안내 메시지
  const defaultProblem = {
    title: "실습 문제 준비 중",
    description: "커리큘럼에서 실습 문제를 불러오고 있습니다. 잠시만 기다려주세요.",
    starter_code: `# 실습 문제를 불러오는 중입니다...\n`
  };

  const problem = problems?.[0] || defaultProblem;

  // 에디터 초기값 설정
  if (!code && problem.starter_code) {
    setCode(problem.starter_code);
  }

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
        <p className="text-gray-600 whitespace-pre-wrap">{problem.description}</p>
        
        {/* 요구사항 */}
        {problem.requirements && problem.requirements.length > 0 && (
          <div className="mt-4 p-4 bg-blue-50 rounded-lg">
            <h4 className="font-semibold text-blue-900 mb-2">📋 구현 요구사항</h4>
            <ul className="space-y-1 text-sm text-blue-800">
              {problem.requirements.map((req: string, idx: number) => (
                <li key={idx} className="flex items-start gap-2">
                  <span className="text-blue-600">•</span>
                  <span>{req}</span>
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>

      {/* Monaco Editor */}
      <div className="mb-4">
        <div className="rounded-xl overflow-hidden border-2 border-gray-200">
          {/* 에디터 헤더 */}
          <div className="bg-gray-800 px-4 py-2 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className="w-3 h-3 rounded-full bg-green-500"></span>
              <span className="text-sm text-gray-300">Python</span>
            </div>
            <div className="flex items-center gap-2">
              <button
                onClick={handleRun}
                disabled={isRunning}
                className={`px-4 py-1.5 rounded-lg text-sm font-medium flex items-center gap-2 transition-colors ${
                  isRunning
                    ? 'bg-gray-600 text-gray-400 cursor-not-allowed'
                    : 'bg-green-600 hover:bg-green-700 text-white'
                }`}
                title="실행 (Ctrl+Enter)"
              >
                {!isRunning && <Play className="w-4 h-4" />}
                {isRunning ? '실행 중...' : '실행'}
              </button>
              <button
                onClick={() => setShowSettings(!showSettings)}
                className="p-1.5 text-gray-400 hover:text-white hover:bg-gray-700 rounded"
                title="에디터 설정"
              >
                <Settings className="w-4 h-4" />
              </button>
            </div>
          </div>

          {/* 설정 패널 */}
          {showSettings && (
            <div className="bg-gray-100 px-4 py-3 border-b border-gray-300">
              <div className="flex items-center gap-4">
                <label className="flex items-center gap-2 text-sm text-gray-700">
                  <span>테마:</span>
                  <select
                    value={editorTheme}
                    onChange={(e) => setEditorTheme(e.target.value as 'light' | 'vs-dark')}
                    className="px-2 py-1 border rounded text-sm"
                  >
                    <option value="light">라이트</option>
                    <option value="vs-dark">다크</option>
                  </select>
                </label>
              </div>
            </div>
          )}

          {/* Monaco Editor */}
          <Editor
            height="400px"
            language="python"
            value={code}
            theme={editorTheme}
            onChange={(value: string | undefined) => setCode(value || '')}
            onMount={handleEditorDidMount}
            options={editorOptions}
            loading={
              <div className="flex items-center justify-center h-full bg-gray-900">
                <div className="text-gray-400">에디터 로딩 중...</div>
              </div>
            }
          />
        </div>
      </div>

      {/* 실행 결과 */}
      {result && (
        <div className={`mb-6 rounded-xl ${result.success ? 'bg-green-50 border-2 border-green-200' : 'bg-red-50 border-2 border-red-200'}`}>
          {/* 실행 출력 */}
          {result.output && (
            <div className="p-4 border-b border-gray-200">
              <div className="flex items-center gap-2 mb-2">
                <h4 className="font-semibold text-gray-900">📤 출력 결과</h4>
              </div>
              <pre className="text-sm font-mono text-gray-700 whitespace-pre-wrap bg-gray-900 text-green-400 p-3 rounded">
                {result.output}
              </pre>
            </div>
          )}
          
          {/* AI 피드백 */}
          {result.feedback && (
            <div className="p-4">
              <div className="flex items-center gap-2 mb-3">
                {result.success ? (
                  <CheckCircle className="w-5 h-5 text-green-600" />
                ) : (
                  <AlertCircle className="w-5 h-5 text-red-600" />
                )}
                <h4 className={`font-bold ${result.success ? 'text-green-900' : 'text-red-900'}`}>
                  {result.success ? '✅ AI 튜터 피드백' : '❌ AI 튜터 피드백'}
                </h4>
              </div>
              <div className="prose prose-sm max-w-none">
                {result.feedback.split('\n').map((line: string, idx: number) => {
                  const trimmedLine = line.trim();
                  
                  // 빈 줄은 공백으로
                  if (!trimmedLine) {
                    return <div key={idx} className="h-2"></div>;
                  }
                  
                  // 코드 블록 마커는 숨김
                  if (trimmedLine.startsWith('```')) {
                    return null;
                  }
                  
                  // 섹션 제목 (** 로 시작하고 끝나는 경우)
                  if (trimmedLine.startsWith('**') && trimmedLine.endsWith('**')) {
                    const title = trimmedLine.replace(/\*\*/g, '');
                    return (
                      <h5 key={idx} className="font-bold text-gray-900 mt-3 mb-1">
                        {title}
                      </h5>
                    );
                  }
                  
                  // 볼드 텍스트 포함 (**text**)
                  if (trimmedLine.includes('**')) {
                    const parts = trimmedLine.split('**');
                    return (
                      <p key={idx} className="text-gray-700 mb-2 leading-relaxed">
                        {parts.map((part, i) => 
                          i % 2 === 1 ? <strong key={i} className="font-semibold text-gray-900">{part}</strong> : part
                        )}
                      </p>
                    );
                  }
                  
                  // 리스트 항목 (- 로 시작)
                  if (trimmedLine.startsWith('-') || trimmedLine.startsWith('•')) {
                    const text = trimmedLine.replace(/^[-•]\s*/, '');
                    return (
                      <li key={idx} className="text-gray-700 mb-1 ml-4">
                        {text}
                      </li>
                    );
                  }
                  
                  // 일반 텍스트
                  return (
                    <p key={idx} className="text-gray-700 mb-2 leading-relaxed">
                      {trimmedLine}
                    </p>
                  );
                })}
              </div>
            </div>
          )}
          
          {/* 에러 메시지 */}
          {result.error && (
            <div className="p-4 bg-red-100 border-t border-red-200">
              <h4 className="font-semibold text-red-900 mb-2">⚠️ 에러 메시지</h4>
              <pre className="text-sm font-mono text-red-700 whitespace-pre-wrap">
                {result.error}
              </pre>
            </div>
          )}
        </div>
      )}

      {/* 힌트 (있는 경우) */}
      {problem.hints && problem.hints.length > 0 && !result?.success && (
        <div className="mb-6 p-4 bg-yellow-50 border border-yellow-200 rounded-xl">
          <h4 className="font-semibold text-yellow-900 mb-2">💡 힌트</h4>
          <ul className="space-y-1 text-sm text-yellow-800">
            {problem.hints.map((hint: string, idx: number) => (
              <li key={idx} className="flex items-start gap-2">
                <span className="text-yellow-600">•</span>
                <span>{hint}</span>
              </li>
            ))}
          </ul>
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
