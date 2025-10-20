import { Link } from 'react-router-dom';
import { 
  Sparkles, 
  Brain, 
  CheckCircle, 
  ArrowRight,
  Star,
  TrendingUp,
  MessageSquare
} from 'lucide-react';

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-white to-pink-50">
      {/* Navigation */}
      <nav className="fixed top-0 left-0 right-0 z-50 bg-white/80 backdrop-blur-md border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-6 py-4 flex justify-between items-center">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 bg-gradient-to-r from-purple-600 to-pink-600 rounded-lg flex items-center justify-center">
              <Brain className="w-5 h-5 text-white" />
            </div>
            <span className="text-xl font-bold bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent">
              EduAI
            </span>
          </div>
          
          <div className="flex items-center gap-6">
            <Link to="/login" className="text-gray-600 hover:text-gray-900 transition">
              로그인
            </Link>
            <Link 
              to="/register" 
              className="px-6 py-2 bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-lg hover:shadow-lg transition"
            >
              무료로 시작하기
            </Link>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="pt-32 pb-20 px-6">
        <div className="max-w-7xl mx-auto text-center">
          <div className="inline-flex items-center gap-2 px-4 py-2 bg-purple-100 text-purple-700 rounded-full text-sm font-medium mb-8">
            <Sparkles className="w-4 h-4" />
            AI 기반 개인화 학습 플랫폼
          </div>
          
          <h1 className="text-5xl md:text-7xl font-bold mb-6 leading-tight">
            <span className="bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent">
              AI가 만드는
            </span>
            <br />
            <span className="text-gray-900">
              당신만의 학습 여정
            </span>
          </h1>
          
          <p className="text-xl text-gray-600 mb-12 max-w-2xl mx-auto leading-relaxed">
            실시간 AI 분석으로 당신의 수준과 목표에 맞는 맞춤형 커리큘럼을 생성하고,
            학습 과정 전체를 지능적으로 관리합니다
          </p>
          
          <div className="flex flex-col sm:flex-row gap-4 justify-center mb-16">
            <Link 
              to="/register"
              className="px-8 py-4 bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-xl text-lg font-semibold hover:shadow-2xl hover:scale-105 transition-all flex items-center justify-center gap-2"
            >
              무료로 시작하기
              <ArrowRight className="w-5 h-5" />
            </Link>
            
            <Link 
              to="/demo"
              className="px-8 py-4 bg-white text-gray-900 rounded-xl text-lg font-semibold border-2 border-gray-200 hover:border-purple-300 hover:shadow-lg transition-all flex items-center justify-center gap-2"
            >
              <Sparkles className="w-5 h-5" />
              데모 체험하기
            </Link>
          </div>
          
          {/* Stats */}
          <div className="grid grid-cols-3 gap-8 max-w-3xl mx-auto">
            <div>
              <div className="text-4xl font-bold text-purple-600 mb-2">10,000+</div>
              <div className="text-gray-600">학습 문제</div>
            </div>
            <div>
              <div className="text-4xl font-bold text-purple-600 mb-2">95%</div>
              <div className="text-gray-600">학습 만족도</div>
            </div>
            <div>
              <div className="text-4xl font-bold text-purple-600 mb-2">24/7</div>
              <div className="text-gray-600">AI 멘토링</div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 px-6 bg-white">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-bold mb-4">
              <span className="bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent">
                왜 EduAI인가요?
              </span>
            </h2>
            <p className="text-xl text-gray-600">
              기존 학습 플랫폼과는 다른 3가지 핵심 차별점
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            {/* Feature 1 */}
            <div className="p-8 rounded-2xl bg-gradient-to-br from-purple-50 to-pink-50 border border-purple-100 hover:shadow-xl transition-all group">
              <div className="w-14 h-14 bg-gradient-to-r from-purple-600 to-pink-600 rounded-xl flex items-center justify-center mb-6 group-hover:scale-110 transition">
                <Brain className="w-7 h-7 text-white" />
              </div>
              <h3 className="text-2xl font-bold mb-4">AI 개인화 커리큘럼</h3>
              <p className="text-gray-600 leading-relaxed mb-6">
                실시간 학습 패턴 분석으로 당신의 이해도, 속도, 선호도를 파악하여 
                최적화된 학습 경로를 자동으로 생성합니다
              </p>
              <ul className="space-y-3">
                <li className="flex items-center gap-2 text-sm text-gray-700">
                  <CheckCircle className="w-4 h-4 text-purple-600" />
                  실시간 난이도 조절
                </li>
                <li className="flex items-center gap-2 text-sm text-gray-700">
                  <CheckCircle className="w-4 h-4 text-purple-600" />
                  약점 자동 분석 및 보완
                </li>
                <li className="flex items-center gap-2 text-sm text-gray-700">
                  <CheckCircle className="w-4 h-4 text-purple-600" />
                  학습 목표 기반 경로 설정
                </li>
              </ul>
            </div>

            {/* Feature 2 */}
            <div className="p-8 rounded-2xl bg-gradient-to-br from-blue-50 to-cyan-50 border border-blue-100 hover:shadow-xl transition-all group">
              <div className="w-14 h-14 bg-gradient-to-r from-blue-600 to-cyan-600 rounded-xl flex items-center justify-center mb-6 group-hover:scale-110 transition">
                <MessageSquare className="w-7 h-7 text-white" />
              </div>
              <h3 className="text-2xl font-bold mb-4">24/7 AI 멘토</h3>
              <p className="text-gray-600 leading-relaxed mb-6">
                언제든지 질문하고 즉시 답변을 받으세요. 
                단순 답변이 아닌 이해를 돕는 맞춤형 설명을 제공합니다
              </p>
              <ul className="space-y-3">
                <li className="flex items-center gap-2 text-sm text-gray-700">
                  <CheckCircle className="w-4 h-4 text-blue-600" />
                  즉시 응답 (평균 2초)
                </li>
                <li className="flex items-center gap-2 text-sm text-gray-700">
                  <CheckCircle className="w-4 h-4 text-blue-600" />
                  맥락 기반 설명
                </li>
                <li className="flex items-center gap-2 text-sm text-gray-700">
                  <CheckCircle className="w-4 h-4 text-blue-600" />
                  무제한 질문 가능
                </li>
              </ul>
            </div>

            {/* Feature 3 */}
            <div className="p-8 rounded-2xl bg-gradient-to-br from-orange-50 to-yellow-50 border border-orange-100 hover:shadow-xl transition-all group">
              <div className="w-14 h-14 bg-gradient-to-r from-orange-600 to-yellow-600 rounded-xl flex items-center justify-center mb-6 group-hover:scale-110 transition">
                <TrendingUp className="w-7 h-7 text-white" />
              </div>
              <h3 className="text-2xl font-bold mb-4">실시간 학습 분석</h3>
              <p className="text-gray-600 leading-relaxed mb-6">
                모든 학습 활동을 실시간으로 추적하고 분석하여
                구체적이고 실행 가능한 인사이트를 제공합니다
              </p>
              <ul className="space-y-3">
                <li className="flex items-center gap-2 text-sm text-gray-700">
                  <CheckCircle className="w-4 h-4 text-orange-600" />
                  학습 패턴 시각화
                </li>
                <li className="flex items-center gap-2 text-sm text-gray-700">
                  <CheckCircle className="w-4 h-4 text-orange-600" />
                  성과 예측 및 가이드
                </li>
                <li className="flex items-center gap-2 text-sm text-gray-700">
                  <CheckCircle className="w-4 h-4 text-orange-600" />
                  최적 학습 시간 추천
                </li>
              </ul>
            </div>
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section className="py-20 px-6 bg-gradient-to-br from-purple-50 to-pink-50">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-bold mb-4">
              시작하기 정말 쉬워요
            </h2>
            <p className="text-xl text-gray-600">
              3분이면 당신만의 AI 학습이 시작됩니다
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-12">
            <div className="text-center">
              <div className="w-20 h-20 bg-gradient-to-r from-purple-600 to-pink-600 rounded-full flex items-center justify-center mx-auto mb-6 text-white text-3xl font-bold">
                1
              </div>
              <h3 className="text-2xl font-bold mb-4">간단한 가입</h3>
              <p className="text-gray-600">
                이메일만 있으면 OK! <br />
                복잡한 절차 없이 30초면 가입 완료
              </p>
            </div>

            <div className="text-center">
              <div className="w-20 h-20 bg-gradient-to-r from-purple-600 to-pink-600 rounded-full flex items-center justify-center mx-auto mb-6 text-white text-3xl font-bold">
                2
              </div>
              <h3 className="text-2xl font-bold mb-4">목표 설정</h3>
              <p className="text-gray-600">
                배우고 싶은 것과 목표를 알려주세요<br />
                AI가 최적의 학습 경로를 생성합니다
              </p>
            </div>

            <div className="text-center">
              <div className="w-20 h-20 bg-gradient-to-r from-purple-600 to-pink-600 rounded-full flex items-center justify-center mx-auto mb-6 text-white text-3xl font-bold">
                3
              </div>
              <h3 className="text-2xl font-bold mb-4">학습 시작!</h3>
              <p className="text-gray-600">
                바로 첫 문제부터 시작하세요<br />
                AI가 실시간으로 함께합니다
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Social Proof */}
      <section className="py-20 px-6 bg-white">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-bold mb-4">
              실제 사용자들의 이야기
            </h2>
            <div className="flex items-center justify-center gap-2 text-yellow-500">
              {[...Array(5)].map((_, i) => (
                <Star key={i} className="w-6 h-6 fill-current" />
              ))}
              <span className="text-gray-600 ml-2">4.9/5.0 평점</span>
            </div>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            {/* Testimonial 1 */}
            <div className="p-6 rounded-xl bg-gray-50 border border-gray-200">
              <div className="flex items-center gap-2 text-yellow-500 mb-4">
                {[...Array(5)].map((_, i) => (
                  <Star key={i} className="w-4 h-4 fill-current" />
                ))}
              </div>
              <p className="text-gray-700 mb-4 leading-relaxed">
                "독학으로 프로그래밍을 시작했는데 어디서부터 해야 할지 막막했어요. 
                EduAI는 저의 수준을 정확히 파악하고 필요한 것만 배울 수 있게 해줬어요!"
              </p>
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-purple-200 rounded-full flex items-center justify-center text-purple-700 font-bold">
                  김
                </div>
                <div>
                  <div className="font-semibold">김민준</div>
                  <div className="text-sm text-gray-500">대학생, 프로그래밍 입문</div>
                </div>
              </div>
            </div>

            {/* Testimonial 2 */}
            <div className="p-6 rounded-xl bg-gray-50 border border-gray-200">
              <div className="flex items-center gap-2 text-yellow-500 mb-4">
                {[...Array(5)].map((_, i) => (
                  <Star key={i} className="w-4 h-4 fill-current" />
                ))}
              </div>
              <p className="text-gray-700 mb-4 leading-relaxed">
                "AI 멘토가 정말 똑똑해요. 단순히 답을 알려주는 게 아니라 
                왜 그런지를 이해할 수 있게 설명해줘서 실력이 빠르게 늘었어요."
              </p>
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-blue-200 rounded-full flex items-center justify-center text-blue-700 font-bold">
                  박
                </div>
                <div>
                  <div className="font-semibold">박서연</div>
                  <div className="text-sm text-gray-500">취준생, 알고리즘 준비</div>
                </div>
              </div>
            </div>

            {/* Testimonial 3 */}
            <div className="p-6 rounded-xl bg-gray-50 border border-gray-200">
              <div className="flex items-center gap-2 text-yellow-500 mb-4">
                {[...Array(5)].map((_, i) => (
                  <Star key={i} className="w-4 h-4 fill-current" />
                ))}
              </div>
              <p className="text-gray-700 mb-4 leading-relaxed">
                "시간이 많지 않은데 효율적으로 공부할 수 있어요. 
                제 약점을 정확히 짚어주고 그것만 집중적으로 학습할 수 있어 좋아요."
              </p>
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-pink-200 rounded-full flex items-center justify-center text-pink-700 font-bold">
                  이
                </div>
                <div>
                  <div className="font-semibold">이준호</div>
                  <div className="text-sm text-gray-500">직장인, 커리어 전환</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Pricing Section */}
      <section className="py-20 px-6 bg-gradient-to-br from-purple-50 to-pink-50">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-bold mb-4">
              간단하고 명확한 가격
            </h2>
            <p className="text-xl text-gray-600">
              7일 무료 체험으로 부담 없이 시작하세요
            </p>
          </div>

          <div className="grid md:grid-cols-2 gap-8 max-w-4xl mx-auto">
            {/* Free Plan */}
            <div className="p-8 rounded-2xl bg-white border-2 border-gray-200">
              <div className="text-center mb-6">
                <h3 className="text-2xl font-bold mb-2">무료 체험</h3>
                <div className="text-5xl font-bold mb-2">₩0</div>
                <div className="text-gray-500">7일간 프리미엄 기능 체험</div>
              </div>
              
              <ul className="space-y-4 mb-8">
                <li className="flex items-center gap-3">
                  <CheckCircle className="w-5 h-5 text-green-600 flex-shrink-0" />
                  <span>AI 개인화 커리큘럼</span>
                </li>
                <li className="flex items-center gap-3">
                  <CheckCircle className="w-5 h-5 text-green-600 flex-shrink-0" />
                  <span>무제한 AI 멘토링</span>
                </li>
                <li className="flex items-center gap-3">
                  <CheckCircle className="w-5 h-5 text-green-600 flex-shrink-0" />
                  <span>실시간 학습 분석</span>
                </li>
                <li className="flex items-center gap-3">
                  <CheckCircle className="w-5 h-5 text-green-600 flex-shrink-0" />
                  <span>10,000+ 학습 문제</span>
                </li>
              </ul>
              
              <Link 
                to="/register"
                className="w-full py-3 px-6 bg-gray-200 text-gray-900 rounded-xl font-semibold hover:bg-gray-300 transition flex items-center justify-center gap-2"
              >
                무료 체험 시작
              </Link>
            </div>

            {/* Premium Plan */}
            <div className="p-8 rounded-2xl bg-gradient-to-br from-purple-600 to-pink-600 text-white relative overflow-hidden">
              <div className="absolute top-4 right-4 bg-yellow-400 text-gray-900 px-3 py-1 rounded-full text-sm font-bold">
                인기 ⭐
              </div>
              
              <div className="text-center mb-6">
                <h3 className="text-2xl font-bold mb-2">프리미엄</h3>
                <div className="text-5xl font-bold mb-2">₩29,000</div>
                <div className="opacity-90">월 구독 (언제든 취소 가능)</div>
              </div>
              
              <ul className="space-y-4 mb-8">
                <li className="flex items-center gap-3">
                  <CheckCircle className="w-5 h-5 flex-shrink-0" />
                  <span>무료 체험의 모든 기능</span>
                </li>
                <li className="flex items-center gap-3">
                  <CheckCircle className="w-5 h-5 flex-shrink-0" />
                  <span>프리미엄 AI 모델 사용</span>
                </li>
                <li className="flex items-center gap-3">
                  <CheckCircle className="w-5 h-5 flex-shrink-0" />
                  <span>우선 고객 지원</span>
                </li>
                <li className="flex items-center gap-3">
                  <CheckCircle className="w-5 h-5 flex-shrink-0" />
                  <span>신규 기능 조기 액세스</span>
                </li>
                <li className="flex items-center gap-3">
                  <CheckCircle className="w-5 h-5 flex-shrink-0" />
                  <span>학습 데이터 무제한 저장</span>
                </li>
              </ul>
              
              <Link 
                to="/register"
                className="w-full py-3 px-6 bg-white text-purple-600 rounded-xl font-semibold hover:shadow-xl transition flex items-center justify-center gap-2"
              >
                프리미엄 시작하기
                <ArrowRight className="w-5 h-5" />
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Final CTA */}
      <section className="py-20 px-6 bg-gradient-to-r from-purple-600 to-pink-600 text-white">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-4xl md:text-5xl font-bold mb-6">
            오늘부터 더 스마트하게 학습하세요
          </h2>
          <p className="text-xl mb-8 opacity-90">
            7일 무료 체험으로 부담 없이 시작하세요. 신용카드 등록 필요 없음.
          </p>
          
          <div className="flex flex-col sm:flex-row gap-4 justify-center mb-12">
            <Link 
              to="/register"
              className="px-8 py-4 bg-white text-purple-600 rounded-xl text-lg font-semibold hover:shadow-2xl hover:scale-105 transition-all flex items-center justify-center gap-2"
            >
              무료로 시작하기
              <ArrowRight className="w-5 h-5" />
            </Link>
            
            <Link 
              to="/login"
              className="px-8 py-4 bg-transparent border-2 border-white text-white rounded-xl text-lg font-semibold hover:bg-white hover:text-purple-600 transition-all"
            >
              이미 계정이 있나요?
            </Link>
          </div>

          <div className="flex items-center justify-center gap-8 text-sm opacity-75">
            <div className="flex items-center gap-2">
              <CheckCircle className="w-5 h-5" />
              신용카드 불필요
            </div>
            <div className="flex items-center gap-2">
              <CheckCircle className="w-5 h-5" />
              언제든 취소 가능
            </div>
            <div className="flex items-center gap-2">
              <CheckCircle className="w-5 h-5" />
              7일 무료 체험
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-12 px-6 bg-gray-900 text-gray-400">
        <div className="max-w-7xl mx-auto">
          <div className="grid md:grid-cols-4 gap-8 mb-8">
            <div>
              <div className="flex items-center gap-2 mb-4">
                <div className="w-8 h-8 bg-gradient-to-r from-purple-600 to-pink-600 rounded-lg flex items-center justify-center">
                  <Brain className="w-5 h-5 text-white" />
                </div>
                <span className="text-xl font-bold text-white">EduAI</span>
              </div>
              <p className="text-sm">
                AI가 만드는 당신만의 학습 여정
              </p>
            </div>

            <div>
              <h4 className="text-white font-semibold mb-4">제품</h4>
              <ul className="space-y-2 text-sm">
                <li><a href="#" className="hover:text-white transition">기능</a></li>
                <li><a href="#" className="hover:text-white transition">가격</a></li>
                <li><a href="#" className="hover:text-white transition">데모</a></li>
              </ul>
            </div>

            <div>
              <h4 className="text-white font-semibold mb-4">회사</h4>
              <ul className="space-y-2 text-sm">
                <li><a href="#" className="hover:text-white transition">소개</a></li>
                <li><a href="#" className="hover:text-white transition">블로그</a></li>
                <li><a href="#" className="hover:text-white transition">채용</a></li>
              </ul>
            </div>

            <div>
              <h4 className="text-white font-semibold mb-4">지원</h4>
              <ul className="space-y-2 text-sm">
                <li><a href="#" className="hover:text-white transition">고객센터</a></li>
                <li><a href="#" className="hover:text-white transition">이용약관</a></li>
                <li><a href="#" className="hover:text-white transition">개인정보처리방침</a></li>
              </ul>
            </div>
          </div>

          <div className="border-t border-gray-800 pt-8 text-center text-sm">
            <p>&copy; 2025 EduAI. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  );
}
