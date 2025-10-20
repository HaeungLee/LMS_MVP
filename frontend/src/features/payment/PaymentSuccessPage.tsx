/**
 * Payment Success Page
 * 결제 성공 후 리다이렉트 페이지
 */

import { useEffect, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { CheckCircle, Loader } from 'lucide-react';
import { api } from '../../shared/services/apiClient';

export default function PaymentSuccessPage() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const [isProcessing, setIsProcessing] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const processPayment = async () => {
      try {
        const paymentKey = searchParams.get('paymentKey');
        const orderId = searchParams.get('orderId');
        const amount = searchParams.get('amount');

        if (!paymentKey || !orderId || !amount) {
          throw new Error('결제 정보가 올바르지 않습니다.');
        }

        // 백엔드에 결제 승인 요청
        await api.post('/payment/success', {
          payment_key: paymentKey,
          order_id: orderId,
          amount: parseInt(amount)
        });

        setIsProcessing(false);

        // 3초 후 대시보드로 이동
        setTimeout(() => {
          navigate('/');
        }, 3000);

      } catch (err: any) {
        console.error('Payment processing error:', err);
        setError(err.message || '결제 처리 중 오류가 발생했습니다.');
        setIsProcessing(false);
      }
    };

    processPayment();
  }, [searchParams, navigate]);

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-red-50 to-pink-50 flex items-center justify-center p-4">
        <div className="bg-white rounded-2xl shadow-2xl p-12 max-w-md text-center">
          <div className="w-20 h-20 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-6">
            <span className="text-4xl">❌</span>
          </div>
          <h1 className="text-2xl font-bold text-gray-900 mb-4">
            결제 처리 실패
          </h1>
          <p className="text-gray-600 mb-6">
            {error}
          </p>
          <button
            onClick={() => navigate('/pricing')}
            className="px-6 py-3 bg-purple-600 text-white rounded-xl hover:bg-purple-700"
          >
            다시 시도하기
          </button>
        </div>
      </div>
    );
  }

  if (isProcessing) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-purple-50 to-pink-50 flex items-center justify-center p-4">
        <div className="bg-white rounded-2xl shadow-2xl p-12 max-w-md text-center">
          <Loader className="w-20 h-20 text-purple-600 animate-spin mx-auto mb-6" />
          <h1 className="text-2xl font-bold text-gray-900 mb-4">
            결제 처리 중...
          </h1>
          <p className="text-gray-600">
            잠시만 기다려주세요.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 to-pink-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-2xl p-12 max-w-md text-center">
        <div className="w-20 h-20 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-6">
          <CheckCircle className="w-12 h-12 text-green-600" />
        </div>
        
        <h1 className="text-3xl font-bold text-gray-900 mb-4">
          🎉 환영합니다!
        </h1>
        
        <p className="text-gray-600 mb-8">
          7일 무료 체험이 시작되었습니다!<br />
          이제 모든 기능을 사용할 수 있습니다.
        </p>

        <div className="bg-purple-50 border-2 border-purple-200 rounded-xl p-4 mb-6">
          <p className="text-purple-900 font-semibold">
            💡 팁: 지금 바로 학습을 시작해보세요!
          </p>
        </div>

        <p className="text-sm text-gray-500">
          3초 후 자동으로 이동합니다...
        </p>
      </div>
    </div>
  );
}
