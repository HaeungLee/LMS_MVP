import React, { useState, useRef } from 'react';
import Editor from '@monaco-editor/react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Play, Square, Settings, Code } from 'lucide-react';

const MonacoCodeEditor = ({
  value = '',
  onChange,
  language = 'python',
  onRun,
  onSubmit,
  isRunning = false,
  height = '400px',
  showRunButton = true,
  showSubmitButton = true,
  className = ''
}) => {
  const [editorTheme, setEditorTheme] = useState('light');
  const [settingsOpen, setSettingsOpen] = useState(false);
  const editorRef = useRef(null);

  // Monaco Editor 설정
  const editorOptions = {
    selectOnLineNumbers: true,
    roundedSelection: false,
    readOnly: false,
    cursorStyle: 'line',
    automaticLayout: true,
    wordWrap: 'on',
    fontSize: 14,
    lineHeight: 18,
    minimap: {
      enabled: false
    },
    scrollBeyondLastLine: false,
    folding: true,
    foldingHighlight: true,
    showFoldingControls: 'always',
    bracketPairColorization: {
      enabled: true
    },
    suggestOnTriggerCharacters: true,
    acceptSuggestionOnEnter: 'on',
    tabCompletion: 'on',
    mouseWheelZoom: true,
    smoothScrolling: true,
    cursorBlinking: 'smooth'
  };

  // 에디터 마운트 시 콜백
  const handleEditorDidMount = (editor, monaco) => {
    editorRef.current = editor;
    
    // Ctrl+Enter로 실행
    editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.Enter, () => {
      if (onRun && !isRunning) {
        onRun();
      }
    });

    editor.focus();
  };

  return (
    <Card className={`h-full ${className}`}>
      <CardHeader className="py-3 px-4">
        <div className="flex items-center justify-between">
          <CardTitle className="text-sm flex items-center gap-2">
            <span className="w-3 h-3 rounded-full bg-green-500"></span>
            코드 에디터 ({language.toUpperCase()})
          </CardTitle>
          
          <div className="flex items-center gap-2">
            {/* 실행 버튼 */}
            {showRunButton && onRun && (
              <button
                onClick={onRun}
                disabled={isRunning}
                className={`flex items-center gap-1 px-3 py-1.5 rounded text-sm font-medium transition-colors ${
                  isRunning 
                    ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                    : 'bg-green-600 hover:bg-green-700 text-white'
                }`}
                title="실행 (Ctrl+Enter)"
              >
                {isRunning ? (
                  <>
                    <Square className="w-4 h-4" />
                    실행 중...
                  </>
                ) : (
                  <>
                    <Play className="w-4 h-4" />
                    실행
                  </>
                )}
              </button>
            )}

            {/* 제출 버튼 */}
            {showSubmitButton && onSubmit && (
              <button
                onClick={onSubmit}
                disabled={isRunning}
                className={`flex items-center gap-1 px-3 py-1.5 rounded text-sm font-medium transition-colors ${
                  isRunning 
                    ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                    : 'bg-blue-600 hover:bg-blue-700 text-white'
                }`}
                title="제출"
              >
                <Code className="w-4 h-4" />
                제출
              </button>
            )}

            {/* 설정 버튼 */}
            <button
              onClick={() => setSettingsOpen(!settingsOpen)}
              className="p-1.5 text-gray-600 hover:text-gray-800 hover:bg-gray-100 rounded"
              title="에디터 설정"
            >
              <Settings className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* 설정 패널 */}
        {settingsOpen && (
          <div className="mt-3 p-3 bg-gray-50 rounded-lg border">
            <div className="flex items-center gap-4">
              <div>
                <label className="block text-gray-700 mb-1 text-sm">테마</label>
                <select
                  value={editorTheme}
                  onChange={(e) => setEditorTheme(e.target.value)}
                  className="p-1 border rounded text-sm"
                >
                  <option value="light">라이트</option>
                  <option value="vs-dark">다크</option>
                  <option value="hc-black">고대비</option>
                </select>
              </div>
            </div>
          </div>
        )}
      </CardHeader>

      <CardContent className="p-0 h-full">
        <div className="h-full">
          <Editor
            height={height}
            language={language}
            value={value}
            theme={editorTheme}
            onChange={onChange}
            onMount={handleEditorDidMount}
            options={editorOptions}
            loading={
              <div className="flex items-center justify-center h-full">
                <div className="text-gray-500">에디터 로딩 중...</div>
              </div>
            }
          />
        </div>
      </CardContent>
    </Card>
  );
};

export default MonacoCodeEditor;
