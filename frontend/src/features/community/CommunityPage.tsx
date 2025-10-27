import React from 'react';
import { MessageCircle, Heart, Users, Lightbulb, HelpCircle } from 'lucide-react';

export default function CommunityPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      <div className="max-w-6xl mx-auto px-4 py-8 sm:px-6 lg:px-8">
        
        {/* 헤더 배너 */}
        <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-2xl shadow-xl p-8 mb-8 text-white">
          <div className="flex items-center justify-center mb-4">
            <MessageCircle className="w-12 h-12 mr-4" />
            <h1 className="text-3xl sm:text-4xl font-bold">커뮤니티</h1>
          </div>
          <p className="text-center text-xl sm:text-2xl font-medium leading-relaxed">
            함께 만들어가는 학습 플랫폼
          </p>
          <p className="text-center text-lg sm:text-xl mt-2 opacity-90">
            당신의 피드백 하나가, 다음 학습자를 웃게 합니다
          </p>
        </div>

        {/* 피드백 폼 섹션 */}
        <div className="bg-white rounded-xl shadow-lg p-6 sm:p-8 mb-8">
          <div className="flex items-center mb-6">
            <Heart className="w-6 h-6 text-red-500 mr-3" />
            <h2 className="text-2xl font-bold text-gray-900">여러분의 목소리를 들려주세요</h2>
          </div>
          
          <p className="text-gray-600 mb-6 leading-relaxed">
            첫 학습을 완료하셨나요? 🎉 여러분의 솔직한 피드백이 이 플랫폼을 더 나은 곳으로 만듭니다.
            <br />
            좋았던 점, 불편했던 점, 바라는 점을 자유롭게 나눠주세요.
          </p>

          {/* Google Form Iframe */}
          <div className="w-full rounded-lg overflow-hidden shadow-inner bg-gray-50">
            <iframe
              src="https://docs.google.com/forms/d/e/1FAIpQLScEMnzYVQqiX_ndxTrWxqhZl5A8bfCid_Bie0H4gjnP-QyojA/viewform?embedded=true"
              width="100%"
              height="800"
              frameBorder="0"
              marginHeight={0}
              marginWidth={0}
              className="w-full"
              title="피드백 폼"
            >
              로딩 중…
            </iframe>
          </div>

          <div className="mt-6 p-4 bg-blue-50 rounded-lg border border-blue-200">
            <p className="text-sm text-blue-800 flex items-center">
              <Lightbulb className="w-4 h-4 mr-2" />
              <strong>Tip:</strong> 익명으로도 제출 가능합니다. 이메일은 선택사항이에요!
            </p>
          </div>
        </div>

        {/* FAQ 섹션 */}
        <div className="bg-white rounded-xl shadow-lg p-6 sm:p-8">
          <div className="flex items-center mb-6">
            <HelpCircle className="w-6 h-6 text-purple-600 mr-3" />
            <h2 className="text-2xl font-bold text-gray-900">자주 묻는 질문 (FAQ)</h2>
          </div>

          <div className="space-y-6">
            {/* FAQ 1 */}
            <div className="border-b border-gray-200 pb-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-2 flex items-center">
                <Users className="w-5 h-5 text-blue-600 mr-2" />
                피드백은 어떻게 활용되나요?
              </h3>
              <p className="text-gray-600 leading-relaxed pl-7">
                모든 피드백은 플랫폼 개선에 직접 반영됩니다. 교재 분량, UI/UX 개선, 새로운 기능 추가 등
                여러분의 의견이 다음 업데이트의 우선순위가 됩니다.
              </p>
            </div>

            {/* FAQ 2 */}
            <div className="border-b border-gray-200 pb-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-2 flex items-center">
                <MessageCircle className="w-5 h-5 text-green-600 mr-2" />
                익명으로 피드백을 남길 수 있나요?
              </h3>
              <p className="text-gray-600 leading-relaxed pl-7">
                네! 이메일 항목은 선택사항입니다. 익명으로도 충분히 소중한 의견을 전달할 수 있어요.
                다만 이메일을 남겨주시면 답변이 필요한 경우 연락드릴 수 있습니다.
              </p>
            </div>

            {/* FAQ 3 */}
            <div className="border-b border-gray-200 pb-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-2 flex items-center">
                <Heart className="w-5 h-5 text-red-500 mr-2" />
                어떤 피드백이 가장 도움이 되나요?
              </h3>
              <p className="text-gray-600 leading-relaxed pl-7">
                구체적일수록 좋아요! "불편했어요" 보다는 "AI 답변이 너무 길어서 핵심을 찾기 어려웠어요" 같은
                구체적인 상황 설명이 큰 도움이 됩니다. 좋았던 점도 함께 남겨주시면 더욱 감사하겠습니다!
              </p>
            </div>

            {/* FAQ 4 */}
            <div className="border-b border-gray-200 pb-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-2 flex items-center">
                <Lightbulb className="w-5 h-5 text-yellow-600 mr-2" />
                새로운 기능을 제안할 수 있나요?
              </h3>
              <p className="text-gray-600 leading-relaxed pl-7">
                물론입니다! "바라는 점" 항목에 원하시는 기능이나 개선사항을 자유롭게 적어주세요.
                기술적 구현 가능성과 사용자 수요를 고려하여 로드맵에 반영하겠습니다.
              </p>
            </div>

            {/* FAQ 5 */}
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2 flex items-center">
                <Users className="w-5 h-5 text-purple-600 mr-2" />
                다른 사용자들의 피드백도 볼 수 있나요?
              </h3>
              <p className="text-gray-600 leading-relaxed pl-7">
                현재는 개발팀에서만 확인하고 있지만, Phase 2에서 커뮤니티 게시판을 추가할 예정입니다.
                그곳에서 학습 팁, 질문, 후기 등을 자유롭게 공유하고 소통할 수 있게 될 거예요!
              </p>
            </div>
          </div>
        </div>

        {/* 하단 감사 메시지 */}
        <div className="mt-8 text-center">
          <p className="text-gray-600 text-lg">
            <Heart className="w-5 h-5 inline text-red-500 mx-1" />
            함께 성장하는 학습 플랫폼, 감사합니다
            <Heart className="w-5 h-5 inline text-red-500 mx-1" />
          </p>
        </div>
      </div>
    </div>
  );
}
