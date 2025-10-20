/**
 * Pricing Page - 가격 안내 및 결제 시작
 * 
 * - ₩9,900/월
 * - 7일 무료 체험
 * - 혜택 나열
 */

import { useState } from 'react';
import { 
  Check, 
  Sparkles, 
  Zap,
  Shield,
  TrendingUp,
  Brain,
  Target,
  Award
} from 'lucide-react';
import PaymentModal from '../payment/PaymentModal';

export default function PricingPage() {
  const [isAnnual, setIsAnnual] = useState(false);
  const [showPaymentModal, setShowPaymentModal] = useState(false);
  const [selectedPlan, setSelectedPlan] = useState<'monthly' | 'annual'>('monthly');

  const handleStartTrial = (plan: 'monthly' | 'annual') => {
    setSelectedPlan(plan);
    setShowPaymentModal(true);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-purple-50 to-pink-50">
      <div className="max-w-7xl mx-auto px-4 py-16">
        {/* 헤더 */}
        <div className="text-center mb-16">
          <div className="inline-flex items-center gap-2 px-4 py-2 bg-purple-100 text-purple-700 rounded-full text-sm font-semibold mb-6">
            <Sparkles className="w-4 h-4" />
            4주 만에 첫 유료 고객 확보 프로젝트
          </div>
          
          <h1 className="text-5xl font-black text-gray-900 mb-4">
            AI가 만드는<br />
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-purple-600 to-pink-600">
              나만의 학습 로드맵
            </span>
          </h1>
          
          <p className="text-xl text-gray-600 mb-8">
            망각 곡선 기반 복습 시스템으로 학습 효과 200% 향상
          </p>
          
          {/* 가격 토글 */}
          <div className="flex items-center justify-center gap-4 mb-8">
            <button
              onClick={() => setIsAnnual(false)}
              className={`px-6 py-3 rounded-xl font-semibold transition-all ${
                !isAnnual
                  ? 'bg-purple-600 text-white shadow-lg'
                  : 'bg-white text-gray-600 hover:bg-gray-50'
              }`}
            >
              월간 결제
            </button>
            <button
              onClick={() => setIsAnnual(true)}
              className={`px-6 py-3 rounded-xl font-semibold transition-all ${
                isAnnual
                  ? 'bg-purple-600 text-white shadow-lg'
                  : 'bg-white text-gray-600 hover:bg-gray-50'
              }`}
            >
              연간 결제
              <span className="ml-2 px-2 py-1 bg-green-100 text-green-700 text-xs rounded-full">
                20% 할인
              </span>
            </button>
          </div>
        </div>

        {/* 가격 카드 */}
        <div className="max-w-2xl mx-auto mb-16">
          <div className="bg-white rounded-3xl shadow-2xl overflow-hidden border-4 border-purple-200">
            {/* 베스트 배지 */}
            <div className="bg-gradient-to-r from-purple-600 to-pink-600 text-white text-center py-3 font-semibold">
              🎉 런칭 특가 - 선착순 100명
            </div>
            
            <div className="p-12">
              {/* 가격 */}
              <div className="text-center mb-8">
                <div className="flex items-baseline justify-center gap-2 mb-2">
                  <span className="text-6xl font-black text-gray-900">
                    {isAnnual ? '₩95,000' : '₩9,900'}
                  </span>
                  <span className="text-2xl text-gray-500">
                    {isAnnual ? '/년' : '/월'}
                  </span>
                </div>
                {isAnnual && (
                  <p className="text-green-600 font-semibold">
                    월 ₩7,900으로 20% 절약!
                  </p>
                )}
                <p className="text-gray-500 mt-2">
                  7일 무료 체험 • 언제든지 취소 가능
                </p>
              </div>

              {/* CTA 버튼 */}
              <button
                onClick={() => handleStartTrial(isAnnual ? 'annual' : 'monthly')}
                className="w-full py-4 bg-gradient-to-r from-purple-600 to-pink-600 text-white text-xl font-bold rounded-xl shadow-xl hover:shadow-2xl transform hover:scale-105 transition-all mb-8"
              >
                <span className="flex items-center justify-center gap-2">
                  <Zap className="w-6 h-6" />
                  7일 무료로 시작하기
                </span>
              </button>

              {/* 혜택 목록 */}
              <div className="space-y-4">
                <BenefitItem
                  icon={<Brain className="w-5 h-5" />}
                  text="AI 맞춤 12주 커리큘럼 생성"
                />
                <BenefitItem
                  icon={<Target className="w-5 h-5" />}
                  text="망각 곡선 기반 복습 시스템"
                />
                <BenefitItem
                  icon={<TrendingUp className="w-5 h-5" />}
                  text="일일 학습 가이드 & 진도 관리"
                />
                <BenefitItem
                  icon={<Award className="w-5 h-5" />}
                  text="연속 학습일 추적 & 동기부여"
                />
                <BenefitItem
                  icon={<Shield className="w-5 h-5" />}
                  text="무제한 AI 멘토링"
                />
              </div>
            </div>
          </div>
        </div>

        {/* 비교표 */}
        <div className="max-w-4xl mx-auto mb-16">
          <h2 className="text-3xl font-bold text-center text-gray-900 mb-8">
            왜 우리를 선택해야 할까요?
          </h2>
          
          <div className="bg-white rounded-2xl shadow-xl overflow-hidden">
            <table className="w-full">
              <thead className="bg-gradient-to-r from-purple-600 to-pink-600 text-white">
                <tr>
                  <th className="py-4 px-6 text-left">기능</th>
                  <th className="py-4 px-6 text-center">우리 서비스</th>
                  <th className="py-4 px-6 text-center">일반 LMS</th>
                </tr>
              </thead>
              <tbody>
                <ComparisonRow
                  feature="AI 맞춤 커리큘럼"
                  us={true}
                  them={false}
                />
                <ComparisonRow
                  feature="복습 시스템"
                  us={true}
                  them={false}
                  bgGray={true}
                />
                <ComparisonRow
                  feature="가격"
                  us="₩9,900/월"
                  them="₩29,000/월"
                />
                <ComparisonRow
                  feature="무료 체험"
                  us="7일"
                  them="없음"
                  bgGray={true}
                />
                <ComparisonRow
                  feature="AI 멘토링"
                  us={true}
                  them={false}
                />
              </tbody>
            </table>
          </div>
        </div>

        {/* FAQ */}
        <div className="max-w-3xl mx-auto">
          <h2 className="text-3xl font-bold text-center text-gray-900 mb-8">
            자주 묻는 질문
          </h2>
          
          <div className="space-y-4">
            <FAQItem
              question="7일 무료 체험은 어떻게 작동하나요?"
              answer="가입 후 7일간 모든 기능을 무료로 사용할 수 있습니다. 체험 기간 중 언제든 취소 가능하며, 취소하지 않으면 자동으로 유료 구독이 시작됩니다."
            />
            <FAQItem
              question="언제든지 구독을 취소할 수 있나요?"
              answer="네! 설정 페이지에서 언제든 구독을 취소할 수 있습니다. 취소 후에도 결제한 기간까지는 서비스를 계속 이용할 수 있습니다."
            />
            <FAQItem
              question="환불이 가능한가요?"
              answer="서비스 이용 후 7일 이내라면 100% 환불이 가능합니다. 단, 무료 체험 기간은 환불 대상이 아닙니다."
            />
            <FAQItem
              question="결제 방법은 무엇이 있나요?"
              answer="신용카드, 체크카드, 계좌이체, 간편결제(토스, 카카오페이) 등 다양한 결제 수단을 지원합니다."
            />
          </div>
        </div>

        {/* 최종 CTA */}
        <div className="text-center mt-16">
          <div className="inline-block bg-white rounded-3xl shadow-2xl p-12">
            <h3 className="text-3xl font-bold text-gray-900 mb-4">
              지금 시작하세요!
            </h3>
            <p className="text-gray-600 mb-6">
              선착순 100명 한정 특가<br />
              나중에 후회하지 말고 지금 바로!
            </p>
            <button
              onClick={() => handleStartTrial('monthly')}
              className="px-12 py-4 bg-gradient-to-r from-purple-600 to-pink-600 text-white text-xl font-bold rounded-xl shadow-xl hover:shadow-2xl transform hover:scale-105 transition-all"
            >
              7일 무료로 시작하기 →
            </button>
          </div>
        </div>
      </div>

      {/* 결제 모달 */}
      <PaymentModal
        isOpen={showPaymentModal}
        onClose={() => setShowPaymentModal(false)}
        plan={selectedPlan}
      />
    </div>
  );
}

// ============= Sub Components =============

interface BenefitItemProps {
  icon: React.ReactNode;
  text: string;
}

function BenefitItem({ icon, text }: BenefitItemProps) {
  return (
    <div className="flex items-center gap-3">
      <div className="flex-shrink-0 w-8 h-8 bg-green-100 rounded-full flex items-center justify-center text-green-600">
        <Check className="w-5 h-5" />
      </div>
      <div className="flex items-center gap-2 text-gray-700">
        <span className="text-purple-600">{icon}</span>
        <span className="font-medium">{text}</span>
      </div>
    </div>
  );
}

interface ComparisonRowProps {
  feature: string;
  us: boolean | string;
  them: boolean | string;
  bgGray?: boolean;
}

function ComparisonRow({ feature, us, them, bgGray }: ComparisonRowProps) {
  return (
    <tr className={bgGray ? 'bg-gray-50' : ''}>
      <td className="py-4 px-6 font-medium text-gray-900">{feature}</td>
      <td className="py-4 px-6 text-center">
        {typeof us === 'boolean' ? (
          us ? (
            <Check className="w-6 h-6 text-green-600 mx-auto" />
          ) : (
            <span className="text-gray-400">-</span>
          )
        ) : (
          <span className="font-semibold text-purple-600">{us}</span>
        )}
      </td>
      <td className="py-4 px-6 text-center">
        {typeof them === 'boolean' ? (
          them ? (
            <Check className="w-6 h-6 text-green-600 mx-auto" />
          ) : (
            <span className="text-gray-400">-</span>
          )
        ) : (
          <span className="text-gray-600">{them}</span>
        )}
      </td>
    </tr>
  );
}

interface FAQItemProps {
  question: string;
  answer: string;
}

function FAQItem({ question, answer }: FAQItemProps) {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <div className="bg-white rounded-xl shadow-lg overflow-hidden">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-full px-6 py-4 text-left flex items-center justify-between hover:bg-gray-50 transition-colors"
      >
        <span className="font-semibold text-gray-900">{question}</span>
        <span className="text-2xl text-gray-400">{isOpen ? '−' : '+'}</span>
      </button>
      {isOpen && (
        <div className="px-6 pb-4 text-gray-600">
          {answer}
        </div>
      )}
    </div>
  );
}
