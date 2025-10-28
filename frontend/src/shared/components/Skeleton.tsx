import React from 'react';

interface SkeletonProps {
  className?: string;
  variant?: 'text' | 'circular' | 'rectangular';
  width?: string;
  height?: string;
  count?: number;
}

export default function Skeleton({ 
  className = '',
  variant = 'text',
  width,
  height,
  count = 1
}: SkeletonProps) {
  const baseClasses = 'animate-pulse bg-gray-200';
  
  const variantClasses = {
    text: 'h-4 rounded',
    circular: 'rounded-full',
    rectangular: 'rounded-lg'
  };

  const style = {
    width: width || (variant === 'circular' ? '40px' : '100%'),
    height: height || (variant === 'circular' ? '40px' : variant === 'text' ? '16px' : '100px')
  };

  return (
    <>
      {Array.from({ length: count }).map((_, index) => (
        <div 
          key={index}
          className={`${baseClasses} ${variantClasses[variant]} ${className}`}
          style={style}
        />
      ))}
    </>
  );
}

// 커리큘럼 카드 스켈레톤
export function CurriculumCardSkeleton() {
  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      <div className="flex items-start justify-between mb-4">
        <div className="flex-1">
          <Skeleton width="60%" height="24px" className="mb-2" />
          <Skeleton width="40%" height="16px" />
        </div>
        <Skeleton variant="circular" width="48px" height="48px" />
      </div>
      <Skeleton count={3} className="mb-2" />
      <div className="flex items-center gap-4 mt-4">
        <Skeleton width="80px" height="20px" />
        <Skeleton width="80px" height="20px" />
        <Skeleton width="80px" height="20px" />
      </div>
    </div>
  );
}

// 통계 카드 스켈레톤
export function StatsCardSkeleton() {
  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      <div className="flex items-center justify-between">
        <div className="flex-1">
          <Skeleton width="50%" height="16px" className="mb-2" />
          <Skeleton width="30%" height="32px" />
        </div>
        <Skeleton variant="circular" width="48px" height="48px" />
      </div>
    </div>
  );
}

// 리스트 아이템 스켈레톤
export function ListItemSkeleton({ count = 3 }: { count?: number }) {
  return (
    <>
      {Array.from({ length: count }).map((_, index) => (
        <div key={index} className="flex items-center gap-4 p-4 border-b border-gray-200">
          <Skeleton variant="circular" width="40px" height="40px" />
          <div className="flex-1">
            <Skeleton width="60%" height="20px" className="mb-2" />
            <Skeleton width="40%" height="16px" />
          </div>
        </div>
      ))}
    </>
  );
}
