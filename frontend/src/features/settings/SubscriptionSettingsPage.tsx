/**
 * Subscription Settings Page
 * 구독 관리 페이지
 * 
 * - 구독 정보 상세
 * - 플랜 변경
 * - 구독 취소
 * - 결제 내역
 */

import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  CreditCard, 
  Crown, 
  Calendar,
  AlertTriangle,
  CheckCircle,
  ArrowLeft
} from 'lucide-react';
import { api } from '../../shared/services/apiClient';

interface SubscriptionData {
  status: string;
  plan: string;
  trial_end_date: string | null;
  next_billing_date: string | null;
  amount: number;
  is_trial: boolean;
  days_remaining: number;
}

export default function SubscriptionSettingsPage() {
  const navigate = useNavigate();
  const [subscription, setSubscription] = useState<SubscriptionData | null>(null);
  const [loading, setLoading] = useState(true);
  const [showCancelModal, setShowCancelModal] = useState(false);
  const [cancelling, setCancelling] = useState(false);

  useEffect(() => {
    fetchSubscription();
  }, []);

  const fetchSubscription = async () => {
    try {
      const response: any = await api.get('/payment/subscription');
      setSubscription(response.data);
    } catch (error) {
      console.error('Failed to fetch subscription:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCancelSubscription = async () => {
    setCancelling(true);
    try {
      await api.post('/payment/cancel');
      alert('구독이 취소되었습니다. 결제한 기간까지는 계속 이용 가능합니다.');
      fetchSubscription();
      setShowCancelModal(false);
    } catch (error) {
      console.error('Failed to cancel subscription:', error);
      alert('구독 취소에 실패했습니다. 다시 시도해주세요.');
    } finally {
      setCancelling(false);
    }
  };

  if (loading) {
    return (
      <div className="max-w-4xl mx-auto p-6">
        <div className="animate-pulse space-y-6">
          <div className="h-32 bg-gray-200 rounded-xl"></div>
          <div className="h-64 bg-gray-200 rounded-xl"></div>
        </div>
      </div>
    );
  }

  if (!subscription) {
    return (
      <div className="max-w-4xl mx-auto p-6">
        <button
          onClick={() => navigate('/dashboard')}
          className="flex items-center gap-2 text-gray-600 hover:text-gray-900 mb-6"
        >
          <ArrowLeft className="w-5 h-5" />
          대시보드로 돌아가기
        </button>

        <div className="bg-gradient-to-br from-purple-50 to-pink-50 rounded-2xl p-12 text-center">
          <div className="inline-block p-4 bg-purple-100 rounded-full mb-6">
            <CreditCard className="w-12 h-12 text-purple-600" />
          </div>
          <h2 className="text-3xl font-bold text-gray-900 mb-4">
            구독 중인 플랜이 없습니다
          </h2>
          <p className="text-gray-600 mb-8">
            프리미엄 기능으로 학습 효과를 200% 높이세요!
          </p>
          <button
            onClick={() => navigate('/pricing')}
            className="px-8 py-4 bg-gradient-to-r from-purple-600 to-pink-600 text-white text-lg font-bold rounded-xl shadow-xl hover:shadow-2xl transform hover:scale-105 transition-all"
          >
            7일 무료로 시작하기
          </button>
        </div>
      </div>
    );
  }

  const { status, plan, is_trial, days_remaining, next_billing_date, amount } = subscription;

  return (
    <div className="max-w-4xl mx-auto p-6 space-y-6">
      {/* 헤더 */}
      <div className="flex items-center justify-between">
        <button
          onClick={() => navigate('/dashboard')}
          className="flex items-center gap-2 text-gray-600 hover:text-gray-900"
        >
          <ArrowLeft className="w-5 h-5" />
          대시보드로 돌아가기
        </button>
      </div>

      <h1 className="text-3xl font-bold text-gray-900">구독 관리</h1>

      {/* 현재 구독 상태 */}
      <div className="bg-gradient-to-br from-purple-50 to-pink-50 rounded-2xl p-8 border-2 border-purple-200">
        <div className="flex items-start justify-between mb-6">
          <div className="flex items-center gap-4">
            <div className="w-16 h-16 bg-purple-100 rounded-full flex items-center justify-center">
              {status === 'trial' ? (
                <Calendar className="w-8 h-8 text-yellow-600" />
              ) : (
                <Crown className="w-8 h-8 text-purple-600" />
              )}
            </div>
            <div>
              <h2 className="text-2xl font-bold text-gray-900">
                {status === 'trial' ? '무료 체험 중' : '프리미엄 회원'}
              </h2>
              <p className="text-gray-600">
                {plan === 'monthly' ? '월간 구독' : '연간 구독'}
              </p>
            </div>
          </div>
          
          {status === 'active' && (
            <div className="px-4 py-2 bg-green-100 text-green-700 rounded-full font-semibold">
              ✅ 활성
            </div>
          )}
          {status === 'trial' && (
            <div className="px-4 py-2 bg-yellow-100 text-yellow-700 rounded-full font-semibold">
              🎉 체험
            </div>
          )}
          {status === 'cancelled' && (
            <div className="px-4 py-2 bg-gray-100 text-gray-700 rounded-full font-semibold">
              ⏸️ 해지 예정
            </div>
          )}
        </div>

        <div className="grid grid-cols-3 gap-4">
          <InfoBox
            label="플랜"
            value={plan === 'monthly' ? '월간 구독' : '연간 구독'}
          />
          <InfoBox
            label={is_trial ? '체험 종료일' : '다음 결제일'}
            value={next_billing_date ? new Date(next_billing_date).toLocaleDateString('ko-KR') : '-'}
          />
          <InfoBox
            label="금액"
            value={`₩${amount.toLocaleString()}`}
          />
        </div>

        {is_trial && (
          <div className="mt-6 bg-yellow-50 border-2 border-yellow-200 rounded-xl p-4">
            <div className="flex items-start gap-3">
              <AlertTriangle className="w-5 h-5 text-yellow-600 flex-shrink-0 mt-0.5" />
              <div className="text-sm">
                <p className="font-semibold text-yellow-900 mb-1">
                  체험 종료까지 {days_remaining}일 남았습니다
                </p>
                <p className="text-yellow-800">
                  체험 종료 후 자동으로 {plan === 'monthly' ? '월간' : '연간'} 구독이 시작됩니다.
                  원하지 않으시면 아래에서 구독을 취소해주세요.
                </p>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* 구독 혜택 */}
      <div className="bg-white rounded-2xl shadow-lg p-8">
        <h3 className="text-xl font-bold text-gray-900 mb-6">현재 이용 중인 혜택</h3>
        
        <div className="space-y-4">
          <BenefitItem text="AI 맞춤 12주 커리큘럼 생성" />
          <BenefitItem text="망각 곡선 기반 복습 시스템" />
          <BenefitItem text="일일 학습 가이드 & 진도 관리" />
          <BenefitItem text="무제한 AI 멘토링" />
          <BenefitItem text="연속 학습일 추적 & 동기부여" />
        </div>
      </div>

      {/* 플랜 변경 */}
      <div className="bg-white rounded-2xl shadow-lg p-8">
        <h3 className="text-xl font-bold text-gray-900 mb-4">플랜 변경</h3>
        <p className="text-gray-600 mb-6">
          다른 플랜으로 변경하고 싶으신가요?
        </p>
        
        <button
          onClick={() => navigate('/pricing')}
          className="px-6 py-3 bg-purple-600 text-white font-semibold rounded-xl hover:bg-purple-700 transition-colors"
        >
          플랜 둘러보기
        </button>
      </div>

      {/* 구독 취소 */}
      {status !== 'cancelled' && (
        <div className="bg-white rounded-2xl shadow-lg p-8 border-2 border-red-100">
          <h3 className="text-xl font-bold text-gray-900 mb-4">구독 취소</h3>
          <p className="text-gray-600 mb-6">
            구독을 취소하시면 {next_billing_date ? new Date(next_billing_date).toLocaleDateString('ko-KR') : '현재 기간'}까지는
            계속 프리미엄 기능을 이용할 수 있습니다.
          </p>
          
          <button
            onClick={() => setShowCancelModal(true)}
            className="px-6 py-3 bg-red-50 text-red-600 font-semibold rounded-xl hover:bg-red-100 transition-colors"
          >
            구독 취소하기
          </button>
        </div>
      )}

      {/* 취소 확인 모달 */}
      {showCancelModal && (
        <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-2xl shadow-2xl max-w-md w-full p-8">
            <div className="text-center mb-6">
              <div className="inline-block p-4 bg-red-100 rounded-full mb-4">
                <AlertTriangle className="w-8 h-8 text-red-600" />
              </div>
              <h3 className="text-2xl font-bold text-gray-900 mb-2">
                정말 취소하시겠습니까?
              </h3>
              <p className="text-gray-600">
                다음과 같은 혜택을 더 이상 이용할 수 없게 됩니다.
              </p>
            </div>

            <div className="bg-gray-50 rounded-lg p-4 mb-6 text-sm text-gray-700 space-y-2">
              <p>• AI 맞춤 커리큘럼</p>
              <p>• 복습 시스템</p>
              <p>• 무제한 AI 멘토링</p>
            </div>

            <div className="flex gap-3">
              <button
                onClick={() => setShowCancelModal(false)}
                className="flex-1 px-6 py-3 bg-gray-100 text-gray-700 font-semibold rounded-xl hover:bg-gray-200"
              >
                계속 이용하기
              </button>
              <button
                onClick={handleCancelSubscription}
                disabled={cancelling}
                className="flex-1 px-6 py-3 bg-red-600 text-white font-semibold rounded-xl hover:bg-red-700 disabled:opacity-50"
              >
                {cancelling ? '처리 중...' : '취소하기'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

// ============= Sub Components =============

function InfoBox({ label, value }: { label: string; value: string }) {
  return (
    <div className="bg-white/80 rounded-lg p-4">
      <p className="text-xs text-gray-600 mb-1">{label}</p>
      <p className="text-lg font-bold text-gray-900">{value}</p>
    </div>
  );
}

function BenefitItem({ text }: { text: string }) {
  return (
    <div className="flex items-center gap-3">
      <div className="w-6 h-6 bg-green-100 rounded-full flex items-center justify-center flex-shrink-0">
        <CheckCircle className="w-4 h-4 text-green-600" />
      </div>
      <span className="text-gray-700">{text}</span>
    </div>
  );
}
