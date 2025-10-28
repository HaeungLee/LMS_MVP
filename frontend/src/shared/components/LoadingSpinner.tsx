import React from 'react';
import { RefreshCw } from 'lucide-react';

interface LoadingSpinnerProps {
  message?: string;
  size?: 'sm' | 'md' | 'lg';
  fullScreen?: boolean;
}

export default function LoadingSpinner({ 
  message = '로딩 중...', 
  size = 'md',
  fullScreen = false 
}: LoadingSpinnerProps) {
  const sizeClasses = {
    sm: 'w-4 h-4',
    md: 'w-8 h-8',
    lg: 'w-12 h-12'
  };

  const containerClasses = fullScreen 
    ? 'fixed inset-0 bg-white bg-opacity-90 flex items-center justify-center z-50'
    : 'flex items-center justify-center py-12';

  return (
    <div className={containerClasses}>
      <div className="text-center">
        <RefreshCw className={`${sizeClasses[size]} animate-spin mx-auto mb-4 text-blue-600`} />
        <p className="text-gray-600">{message}</p>
        {fullScreen && (
          <p className="text-sm text-gray-500 mt-2">
            첫 접속 시 서버 준비에 약 30초 소요될 수 있습니다
          </p>
        )}
      </div>
    </div>
  );
}
