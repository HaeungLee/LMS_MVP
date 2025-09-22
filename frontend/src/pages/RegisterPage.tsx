import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Bot, Mail, Lock, User, RefreshCw, AlertCircle, CheckCircle, Info } from 'lucide-react';
import useAuthStore from '../shared/hooks/useAuthStore';

export default function RegisterPage() {
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    confirmPassword: '',
    displayName: '',
  });
  const [agreedToTerms, setAgreedToTerms] = useState(false);
  const [customError, setCustomError] = useState<string | null>(null);
  const navigate = useNavigate();
  const { register, loading, error } = useAuthStore();

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
    // 사용자가 입력하면 에러 메시지 제거
    if (customError) setCustomError(null);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setCustomError(null);
    
    // 비밀번호 확인
    if (formData.password !== formData.confirmPassword) {
      setCustomError('비밀번호가 일치하지 않습니다.');
      return;
    }

    // 약관 동의 확인
    if (!agreedToTerms) {
      setCustomError('이용약관에 동의해주세요.');
      return;
    }

    // 이메일 형식 검증
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(formData.email)) {
      setCustomError('올바른 이메일 형식을 입력해주세요.');
      return;
    }

    // 비밀번호 강도 검증
    if (formData.password.length < 6) {
      setCustomError('비밀번호는 최소 6자리 이상이어야 합니다.');
      return;
    }

    try {
      await register(formData.email, formData.password, formData.displayName || undefined);
      navigate('/'); // 회원가입 성공 시 대시보드로 이동
    } catch (err) {
      // 추가적인 에러 처리는 useAuthStore에서 이미 처리됨
      console.error('회원가입 실패:', err);
    }
  };

  const isPasswordMatch = formData.password && formData.confirmPassword && formData.password === formData.confirmPassword;
  const isPasswordMismatch = formData.password && formData.confirmPassword && formData.password !== formData.confirmPassword;
  const displayError = customError || error;

  // 일반적인 회원가입 오류에 대한 사용자 친화적 메시지
  const getFriendlyErrorMessage = (errorMsg: string) => {
    if (errorMsg.includes('Email already registered') || errorMsg.includes('이미 등록된')) {
      return '이미 등록된 이메일 주소입니다. 다른 이메일을 사용하거나 로그인해주세요.';
    }
    if (errorMsg.includes('password') && errorMsg.includes('too short')) {
      return '비밀번호가 너무 짧습니다. 최소 6자리 이상 입력해주세요.';
    }
    if (errorMsg.includes('invalid email')) {
      return '올바른 이메일 형식을 입력해주세요.';
    }
    return errorMsg;
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 flex items-center justify-center p-4">
      <div className="max-w-md w-full space-y-8">
        {/* 로고 */}
        <div className="text-center">
          <div className="flex items-center justify-center mb-4">
            <div className="w-12 h-12 bg-blue-600 rounded-xl flex items-center justify-center">
              <Bot className="w-7 h-7 text-white" />
            </div>
          </div>
          <h2 className="text-3xl font-bold text-gray-900">계정 만들기</h2>
          <p className="mt-2 text-gray-600">AI 중심 학습 플랫폼에 가입하세요</p>
        </div>

        {/* 회원가입 폼 */}
        <div className="bg-white rounded-xl shadow-lg p-8">
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* 이메일 */}
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-2">
                이메일 주소 *
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <Mail className="h-5 w-5 text-gray-400" />
                </div>
                <input
                  id="email"
                  name="email"
                  type="email"
                  value={formData.email}
                  onChange={handleChange}
                  required
                  className="w-full pl-10 pr-3 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  placeholder="your@email.com"
                />
              </div>
            </div>

            {/* 표시 이름 */}
            <div>
              <label htmlFor="displayName" className="block text-sm font-medium text-gray-700 mb-2">
                표시 이름 (선택)
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <User className="h-5 w-5 text-gray-400" />
                </div>
                <input
                  id="displayName"
                  name="displayName"
                  type="text"
                  value={formData.displayName}
                  onChange={handleChange}
                  className="w-full pl-10 pr-3 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  placeholder="홍길동"
                />
              </div>
            </div>

            {/* 비밀번호 */}
            <div>
              <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-2">
                비밀번호 *
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <Lock className="h-5 w-5 text-gray-400" />
                </div>
                <input
                  id="password"
                  name="password"
                  type="password"
                  value={formData.password}
                  onChange={handleChange}
                  required
                  className="w-full pl-10 pr-3 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  placeholder="••••••••"
                />
              </div>
              <p className="text-xs text-gray-500 mt-1">
                최소 6자리 이상 권장합니다
              </p>
            </div>

            {/* 비밀번호 확인 */}
            <div>
              <label htmlFor="confirmPassword" className="block text-sm font-medium text-gray-700 mb-2">
                비밀번호 확인 *
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <Lock className="h-5 w-5 text-gray-400" />
                </div>
                <input
                  id="confirmPassword"
                  name="confirmPassword"
                  type="password"
                  value={formData.confirmPassword}
                  onChange={handleChange}
                  required
                  className={`w-full pl-10 pr-10 py-3 border rounded-lg focus:ring-2 focus:ring-blue-500 ${
                    isPasswordMismatch ? 'border-red-300' : 
                    isPasswordMatch ? 'border-green-300' : 'border-gray-300'
                  }`}
                  placeholder="••••••••"
                />
                {isPasswordMatch && (
                  <div className="absolute inset-y-0 right-0 pr-3 flex items-center">
                    <CheckCircle className="h-5 w-5 text-green-500" />
                  </div>
                )}
                {isPasswordMismatch && (
                  <div className="absolute inset-y-0 right-0 pr-3 flex items-center">
                    <AlertCircle className="h-5 w-5 text-red-500" />
                  </div>
                )}
              </div>
              {isPasswordMismatch && (
                <p className="text-xs text-red-600 mt-1">비밀번호가 일치하지 않습니다</p>
              )}
            </div>

            {/* 약관 동의 */}
            <div className="flex items-start">
              <input
                id="agreedToTerms"
                type="checkbox"
                checked={agreedToTerms}
                onChange={(e) => setAgreedToTerms(e.target.checked)}
                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded mt-1"
              />
              <label htmlFor="agreedToTerms" className="ml-3 block text-sm text-gray-700">
                <span className="text-blue-600 hover:text-blue-500 cursor-pointer">이용약관</span> 및{' '}
                <span className="text-blue-600 hover:text-blue-500 cursor-pointer">개인정보처리방침</span>에 동의합니다 *
              </label>
            </div>

            {/* 에러 메시지 */}
            {displayError && (
              <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                <div className="flex items-center">
                  <AlertCircle className="w-5 h-5 text-red-600 mr-2 flex-shrink-0" />
                  <div>
                    <span className="text-red-800 text-sm font-medium">회원가입 실패</span>
                    <p className="text-red-700 text-sm mt-1">
                      {getFriendlyErrorMessage(displayError)}
                    </p>
                  </div>
                </div>
              </div>
            )}

            {/* 이미 등록된 이메일 안내 */}
            {displayError && displayError.includes('already registered') && (
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <div className="flex items-center">
                  <Info className="w-5 h-5 text-blue-600 mr-2" />
                  <div>
                    <span className="text-blue-800 text-sm">기존 계정이 있으신가요?</span>
                    <Link to="/login" className="text-blue-600 hover:text-blue-500 ml-2 font-medium">
                      로그인하러 가기 →
                    </Link>
                  </div>
                </div>
              </div>
            )}

            {/* 회원가입 버튼 */}
            <button
              type="submit"
              disabled={loading || !formData.email || !formData.password || !formData.confirmPassword || isPasswordMismatch || !agreedToTerms}
              className="w-full bg-blue-600 text-white py-3 px-4 rounded-lg hover:bg-blue-700 focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors flex items-center justify-center"
            >
              {loading ? (
                <>
                  <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                  계정 생성 중...
                </>
              ) : (
                '계정 만들기'
              )}
            </button>

            {/* 로그인 링크 */}
            <div className="text-center">
              <p className="text-sm text-gray-600">
                이미 계정이 있으시나요?{' '}
                <Link to="/login" className="text-blue-600 hover:text-blue-500 font-medium">
                  로그인
                </Link>
              </p>
            </div>
          </form>
        </div>

        {/* 백엔드 연결 상태 */}
        <div className="text-center">
          <div className="inline-flex items-center bg-green-50 border border-green-200 rounded-lg px-3 py-2">
            <div className="w-2 h-2 bg-green-500 rounded-full mr-2"></div>
            <span className="text-green-800 text-xs font-medium">백엔드 서버 연결됨</span>
          </div>
        </div>
      </div>
    </div>
  );
}