/**
 * Subscription Card - 대시보드용 구독 상태 카드
 * 
 * - 현재 구독 플랜 표시
 * - 7일 무료 체험 상태
 * - 다음 결제일
 * - 구독 관리 버튼
 */

import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { CreditCard, Crown, Calendar, Zap, Settings } from 'lucide-react';
import { api } from '../../../shared/services/apiClient';

interface SubscriptionData {
  status: string;
  plan: string;
  trial_end_date: string | null;
  next_billing_date: string | null;
  amount: number;
  is_trial: boolean;
  days_remaining: number;
}

export default function SubscriptionCard() {
  const navigate = useNavigate();
  const [subscription, setSubscription] = useState<SubscriptionData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let isMounted = true;
    
    const fetchSubscription = async () => {
      try {
        console.log('🔍 구독 정보 조회 시작...');
        const response: any = await api.get('/payment/subscription');
        console.log('✅ 구독 정보 응답:', response);
        
        if (isMounted) {
          setSubscription(response.data || response);
          setLoading(false);
        }
      } catch (error: any) {
        console.error('❌ 구독 정보 조회 실패:', error);
        console.error('에러 타입:', error.name);
        console.error('에러 메시지:', error.message);
        
        if (isMounted) {
          // AbortError가 아닌 경우에만 에러 처리
          if (error.name !== 'AbortError') {
            setSubscription(null);
          }
          setLoading(false);
        }
      }
    };
    
    fetchSubscription();
    
    return () => {
      isMounted = false;
    };
  }, []);

  if (loading) {
    return (
      <div className="bg-white rounded-xl shadow-lg p-6 animate-pulse">
        <div className="h-24 bg-gray-200 rounded"></div>
      </div>
    );
  }

  // 무료 사용자
  if (!subscription) {
    return (
      <div className="bg-gradient-to-br from-purple-50 to-pink-50 rounded-xl shadow-lg p-6 border-2 border-purple-200">
        <div className="flex items-start justify-between mb-4">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 bg-purple-100 rounded-full flex items-center justify-center">
              <CreditCard className="w-6 h-6 text-purple-600" />
            </div>
            <div>
              <h3 className="text-lg font-bold text-gray-900">무료 체험</h3>
              <p className="text-sm text-gray-600">제한된 기능 이용 중</p>
            </div>
          </div>
        </div>

        <div className="bg-white/80 rounded-lg p-4 mb-4">
          <p className="text-sm text-gray-700 mb-2">
            🎯 <strong>프리미엄 기능</strong>을 사용하고 싶으신가요?
          </p>
          <ul className="text-xs text-gray-600 space-y-1 ml-4">
            <li>• AI 맞춤 커리큘럼</li>
            <li>• 망각 곡선 복습 시스템</li>
            <li>• 무제한 AI 멘토링</li>
          </ul>
        </div>

        <button
          onClick={() => navigate('/pricing')}
          className="w-full py-3 bg-gradient-to-r from-purple-600 to-pink-600 text-white font-bold rounded-lg hover:shadow-xl transform hover:scale-105 transition-all"
        >
          <span className="flex items-center justify-center gap-2">
            <Zap className="w-5 h-5" />
            7일 무료로 시작하기
          </span>
        </button>
      </div>
    );
  }

  // 유료 구독자
  const { status, plan, is_trial, days_remaining, next_billing_date, amount } = subscription;

  const statusConfig = {
    trial: {
      icon: <Zap className="w-6 h-6 text-yellow-600" />,
      bgColor: 'bg-yellow-100',
      title: '무료 체험 중',
      badge: '🎉 TRIAL'
    },
    active: {
      icon: <Crown className="w-6 h-6 text-purple-600" />,
      bgColor: 'bg-purple-100',
      title: '프리미엄 회원',
      badge: '👑 PREMIUM'
    },
    cancelled: {
      icon: <Calendar className="w-6 h-6 text-gray-600" />,
      bgColor: 'bg-gray-100',
      title: '해지 예정',
      badge: '⏸️ CANCELLED'
    }
  };

  const config = statusConfig[status as keyof typeof statusConfig] || statusConfig.active;

  return (
    <div className="bg-gradient-to-br from-purple-50 to-pink-50 rounded-xl shadow-lg p-6 border-2 border-purple-200">
      {/* 헤더 */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center gap-3">
          <div className={`w-12 h-12 ${config.bgColor} rounded-full flex items-center justify-center`}>
            {config.icon}
          </div>
          <div>
            <h3 className="text-lg font-bold text-gray-900">{config.title}</h3>
            <span className="text-xs font-semibold text-purple-600">
              {config.badge}
            </span>
          </div>
        </div>
        
        <button
          onClick={() => navigate('/settings/subscription')}
          className="text-gray-400 hover:text-gray-600"
        >
          <Settings className="w-5 h-5" />
        </button>
      </div>

      {/* 플랜 정보 */}
      <div className="bg-white/80 rounded-lg p-4 mb-4 space-y-2">
        <div className="flex justify-between items-center">
          <span className="text-sm text-gray-600">플랜</span>
          <span className="text-sm font-semibold text-gray-900">
            {plan === 'monthly' ? '월간 구독' : '연간 구독'}
          </span>
        </div>
        
        {is_trial && (
          <div className="flex justify-between items-center">
            <span className="text-sm text-gray-600">체험 종료</span>
            <span className="text-sm font-semibold text-yellow-600">
              {days_remaining}일 남음
            </span>
          </div>
        )}
        
        {!is_trial && next_billing_date && (
          <div className="flex justify-between items-center">
            <span className="text-sm text-gray-600">다음 결제일</span>
            <span className="text-sm font-semibold text-gray-900">
              {new Date(next_billing_date).toLocaleDateString('ko-KR')}
            </span>
          </div>
        )}
        
        <div className="flex justify-between items-center">
          <span className="text-sm text-gray-600">금액</span>
          <span className="text-sm font-semibold text-gray-900">
            ₩{amount.toLocaleString()}/{plan === 'monthly' ? '월' : '년'}
          </span>
        </div>
      </div>

      {/* CTA */}
      {is_trial && (
        <div className="bg-yellow-50 border-2 border-yellow-200 rounded-lg p-3 mb-3">
          <p className="text-xs text-yellow-800">
            💡 체험 종료 후 자동으로 유료 구독이 시작됩니다.
          </p>
        </div>
      )}

      <button
        onClick={() => navigate('/settings/subscription')}
        className="w-full py-2.5 bg-white text-gray-700 font-semibold rounded-lg border-2 border-gray-200 hover:border-purple-300 hover:bg-purple-50 transition-all"
      >
        구독 관리
      </button>
    </div>
  );
}
