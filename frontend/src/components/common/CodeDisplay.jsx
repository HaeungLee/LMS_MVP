import React, { useState } from 'react';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { oneDark, oneLight } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { Copy, Check, Sun, Moon } from 'lucide-react';

const CodeDisplay = ({
  code,
  language = 'python',
  title = null,
  showLineNumbers = true,
  showCopyButton = true,
  theme = 'dark',
  className = ''
}) => {
  const [copied, setCopied] = useState(false);
  const [currentTheme, setCurrentTheme] = useState(theme);

  // 코드 복사 기능
  const copyToClipboard = async () => {
    try {
      await navigator.clipboard.writeText(code);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy code:', err);
    }
  };

  // 테마 토글
  const toggleTheme = () => {
    setCurrentTheme(currentTheme === 'dark' ? 'light' : 'dark');
  };

  // 언어 감지 (단순화된 버전)
  const detectLanguage = (code) => {
    if (!code) return language;

    const lowerCode = code.toLowerCase();

    if (lowerCode.includes('def ') || lowerCode.includes('import ') || lowerCode.includes('print(')) {
      return 'python';
    }
    if (lowerCode.includes('function') || lowerCode.includes('const ') || lowerCode.includes('let ')) {
      return 'javascript';
    }
    if (lowerCode.includes('public class') || lowerCode.includes('system.out')) {
      return 'java';
    }
    if (lowerCode.includes('#include') || lowerCode.includes('int main')) {
      return 'cpp';
    }
    if (lowerCode.includes('select ') || lowerCode.includes('from ') || lowerCode.includes('where ')) {
      return 'sql';
    }

    return language;
  };

  const detectedLanguage = detectLanguage(code);
  const style = currentTheme === 'dark' ? oneDark : oneLight;

  return (
    <div className={`relative ${className}`}>
      {/* 헤더 */}
      {(title || showCopyButton) && (
        <div className="flex items-center justify-between mb-2 px-4 py-2 bg-gray-50 dark:bg-gray-800 rounded-t-lg border-b">
          <div className="flex items-center space-x-3">
            {title && (
              <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300">
                {title}
              </h4>
            )}
            <span className="text-xs text-gray-500 bg-gray-200 dark:bg-gray-700 px-2 py-1 rounded">
              {detectedLanguage}
            </span>
          </div>

          <div className="flex items-center space-x-2">
            {/* 테마 토글 버튼 */}
            <button
              onClick={toggleTheme}
              onKeyDown={(e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                  e.preventDefault();
                  toggleTheme();
                }
              }}
              className="p-1 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 rounded"
              title={`테마 변경: ${currentTheme === 'dark' ? '밝은 테마로 전환' : '어두운 테마로 전환'}`}
              aria-label={`테마 변경: ${currentTheme === 'dark' ? '밝은 테마로 전환' : '어두운 테마로 전환'}`}
              tabIndex={0}
            >
              {currentTheme === 'dark' ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}
              <span className="sr-only">테마 변경</span>
            </button>

            {/* 복사 버튼 */}
            {showCopyButton && (
              <button
                onClick={copyToClipboard}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    copyToClipboard();
                  }
                }}
                className="p-1 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 flex items-center space-x-1 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 rounded"
                title="코드 복사 (Enter 또는 Space 키)"
                aria-label="코드 복사"
                tabIndex={0}
              >
                {copied ? <Check className="w-4 h-4 text-green-500" /> : <Copy className="w-4 h-4" />}
                <span className="sr-only">{copied ? '복사됨' : '복사'}</span>
              </button>
            )}
          </div>
        </div>
      )}

      {/* 코드 표시 영역 */}
      <div className="relative">
        <SyntaxHighlighter
          language={detectedLanguage}
          style={style}
          showLineNumbers={showLineNumbers}
          lineNumberStyle={{
            minWidth: '3em',
            paddingRight: '1em',
            color: currentTheme === 'dark' ? '#6b7280' : '#9ca3af',
            borderRight: `1px solid ${currentTheme === 'dark' ? '#374151' : '#e5e7eb'}`,
            marginRight: '1em',
            textAlign: 'right',
            userSelect: 'none'
          }}
          customStyle={{
            margin: 0,
            padding: '1rem',
            fontSize: '14px',
            lineHeight: '1.5',
            borderRadius: title || showCopyButton ? '0 0 8px 8px' : '8px',
            fontFamily: '"JetBrains Mono", "Fira Code", "Source Code Pro", Monaco, Consolas, "Courier New", monospace'
          }}
          wrapLines={true}
          wrapLongLines={true}
        >
          {code}
        </SyntaxHighlighter>
      </div>

      {/* 복사 성공 메시지 */}
      {copied && (
        <div className="absolute top-2 right-2 bg-green-500 text-white px-2 py-1 rounded text-xs">
          복사되었습니다!
        </div>
      )}
    </div>
  );
};

export default CodeDisplay;
