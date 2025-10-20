/**
 * Payment Checkout Modal
 * 
 * 토스페이먼츠 결제 위젯 통합
 * - 7일 무료 체험 시작
 * - 월간/연간 결제
 */

import { useState, useEffect } from 'react';
import { X, CreditCard, Shield, Zap } from 'lucide-react';
import { api } from '../../shared/services/apiClient';

// 토스페이먼츠 SDK 타입 정의
declare global {
  interface Window {
    TossPayments: any;
  }
}

interface PaymentModalProps {
  isOpen: boolean;
  onClose: () => void;
  plan: 'monthly' | 'annual';
}

export default function PaymentModal({ isOpen, onClose, plan }: PaymentModalProps) {
  const [isLoading, setIsLoading] = useState(false);
  const [clientKey, setClientKey] = useState('');

  useEffect(() => {
    // 토스 클라이언트 키 가져오기
    const fetchClientKey = async () => {
      try {
        const response: any = await api.get('/payment/client-key');
        setClientKey(response.data.client_key);
      } catch (error) {
        console.error('Failed to fetch client key:', error);
      }
    };

    if (isOpen) {
      fetchClientKey();
    }
  }, [isOpen]);

  const handlePayment = async () => {
    setIsLoading(true);

    try {
      // 1. 백엔드에서 결제 준비
      const checkoutResponse: any = await api.post('/payment/checkout', {
        plan
      });

      const { order_id, amount, customer_key } = checkoutResponse.data;

      // 2. 토스페이먼츠 SDK 로드 (CDN에서 로드됨)
      if (!window.TossPayments) {
        throw new Error('토스페이먼츠 SDK가 로드되지 않았습니다.');
      }
      
      const tossPayments = window.TossPayments(clientKey);

      // 3. 결제창 열기
      await tossPayments.requestPayment('카드', {
        amount,
        orderId: order_id,
        orderName: plan === 'monthly' ? 'LMS 월간 구독' : 'LMS 연간 구독',
        customerName: '사용자',
        successUrl: `${window.location.origin}/payment/success`,
        failUrl: `${window.location.origin}/payment/fail`,
        customerKey: customer_key,
      });

    } catch (error: any) {
      console.error('Payment error:', error);
      alert(error.message || '결제 중 오류가 발생했습니다.');
    } finally {
      setIsLoading(false);
    }
  };

  if (!isOpen) return null;

  const amount = plan === 'monthly' ? 9900 : 95000;
  const savings = plan === 'annual' ? '월 ₩7,900 (20% 절약!)' : null;

  return (
    <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl shadow-2xl max-w-md w-full overflow-hidden">
        {/* 헤더 */}
        <div className="bg-gradient-to-r from-purple-600 to-pink-600 text-white p-6 relative">
          <button
            onClick={onClose}
            className="absolute top-4 right-4 text-white/80 hover:text-white"
          >
            <X className="w-6 h-6" />
          </button>
          
          <h2 className="text-2xl font-bold mb-2">
            {plan === 'monthly' ? '월간 구독' : '연간 구독'}
          </h2>
          <p className="text-white/90">7일 무료 체험 후 자동 결제</p>
        </div>

        {/* 본문 */}
        <div className="p-6 space-y-6">
          {/* 가격 */}
          <div className="text-center py-4 bg-purple-50 rounded-xl">
            <div className="text-4xl font-black text-gray-900 mb-1">
              ₩{amount.toLocaleString()}
            </div>
            <div className="text-gray-600">
              {plan === 'monthly' ? '/ 월' : '/ 년'}
            </div>
            {savings && (
              <div className="text-green-600 font-semibold mt-2">
                {savings}
              </div>
            )}
          </div>

          {/* 체험 안내 */}
          <div className="bg-blue-50 border-2 border-blue-200 rounded-xl p-4">
            <div className="flex items-center gap-2 text-blue-900 font-semibold mb-2">
              <Zap className="w-5 h-5" />
              7일 무료 체험
            </div>
            <p className="text-blue-800 text-sm">
              지금 시작하면 <strong>7일간 무료</strong>로 모든 기능을 사용할 수 있습니다.
              체험 기간 중 언제든 취소 가능합니다.
            </p>
          </div>

          {/* 혜택 */}
          <div className="space-y-3">
            <BenefitItem text="AI 맞춤 12주 커리큘럼" />
            <BenefitItem text="망각 곡선 기반 복습 시스템" />
            <BenefitItem text="무제한 AI 멘토링" />
            <BenefitItem text="연속 학습일 추적" />
          </div>

          {/* 결제 버튼 */}
          <button
            onClick={handlePayment}
            disabled={isLoading || !clientKey}
            className="w-full py-4 bg-gradient-to-r from-purple-600 to-pink-600 text-white text-lg font-bold rounded-xl shadow-lg hover:shadow-xl transform hover:scale-105 transition-all disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none"
          >
            {isLoading ? (
              '결제 준비 중...'
            ) : (
              <span className="flex items-center justify-center gap-2">
                <CreditCard className="w-5 h-5" />
                7일 무료로 시작하기
              </span>
            )}
          </button>

          {/* 보안 안내 */}
          <div className="flex items-center justify-center gap-2 text-gray-500 text-sm">
            <Shield className="w-4 h-4" />
            <span>토스페이먼츠 안전 결제</span>
          </div>

          {/* 취소 안내 */}
          <p className="text-center text-xs text-gray-500">
            체험 기간 중 언제든 취소 가능하며,<br />
            취소 시 비용이 청구되지 않습니다.
          </p>
        </div>
      </div>
    </div>
  );
}

// ============= Sub Component =============

function BenefitItem({ text }: { text: string }) {
  return (
    <div className="flex items-center gap-3">
      <div className="w-6 h-6 bg-green-100 rounded-full flex items-center justify-center flex-shrink-0">
        <svg className="w-4 h-4 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
        </svg>
      </div>
      <span className="text-gray-700">{text}</span>
    </div>
  );
}
