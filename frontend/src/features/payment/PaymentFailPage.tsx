/**
 * Payment Fail Page
 * 결제 실패 페이지
 */

import { useNavigate, useSearchParams } from 'react-router-dom';
import { XCircle } from 'lucide-react';

export default function PaymentFailPage() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();

  const errorCode = searchParams.get('code') || '알 수 없는 오류';
  const errorMessage = searchParams.get('message') || '결제 중 문제가 발생했습니다.';

  return (
    <div className="min-h-screen bg-gradient-to-br from-red-50 to-pink-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-2xl p-12 max-w-md text-center">
        <div className="w-20 h-20 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-6">
          <XCircle className="w-12 h-12 text-red-600" />
        </div>
        
        <h1 className="text-3xl font-bold text-gray-900 mb-4">
          결제 실패
        </h1>
        
        <div className="mb-8">
          <p className="text-gray-600 mb-2">
            {errorMessage}
          </p>
          <p className="text-sm text-gray-400">
            오류 코드: {errorCode}
          </p>
        </div>

        <div className="space-y-3">
          <button
            onClick={() => navigate('/pricing')}
            className="w-full px-6 py-3 bg-purple-600 text-white rounded-xl hover:bg-purple-700 font-semibold"
          >
            다시 시도하기
          </button>
          
          <button
            onClick={() => navigate('/')}
            className="w-full px-6 py-3 bg-gray-100 text-gray-700 rounded-xl hover:bg-gray-200 font-semibold"
          >
            홈으로 돌아가기
          </button>
        </div>

        <p className="text-xs text-gray-500 mt-6">
          문제가 계속되면 고객센터로 문의해주세요.
        </p>
      </div>
    </div>
  );
}
