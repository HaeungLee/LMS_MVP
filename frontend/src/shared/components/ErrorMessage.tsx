import React from 'react';
import { AlertCircle, RefreshCw } from 'lucide-react';

interface ErrorMessageProps {
  title?: string;
  message: string;
  onRetry?: () => void;
  fullScreen?: boolean;
}

export default function ErrorMessage({ 
  title = '오류가 발생했습니다',
  message,
  onRetry,
  fullScreen = false 
}: ErrorMessageProps) {
  const containerClasses = fullScreen
    ? 'fixed inset-0 bg-white flex items-center justify-center z-50 p-4'
    : 'py-12';

  return (
    <div className={containerClasses}>
      <div className="max-w-md w-full bg-red-50 border border-red-200 rounded-lg p-6">
        <div className="flex items-center mb-4">
          <AlertCircle className="w-6 h-6 text-red-600 mr-3 flex-shrink-0" />
          <h3 className="text-red-800 font-medium">{title}</h3>
        </div>
        <p className="text-red-600 mb-4 whitespace-pre-line">
          {message}
        </p>
        {onRetry && (
          <button 
            onClick={onRetry}
            className="w-full bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700 transition-colors flex items-center justify-center"
          >
            <RefreshCw className="w-4 h-4 mr-2" />
            다시 시도
          </button>
        )}
        {!onRetry && (
          <button 
            onClick={() => window.location.reload()}
            className="w-full bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700 transition-colors flex items-center justify-center"
          >
            <RefreshCw className="w-4 h-4 mr-2" />
            새로고침
          </button>
        )}
      </div>
    </div>
  );
}
