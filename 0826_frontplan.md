# 0826 Frontend Plan

목표: 베타 테스트 전 프론트의 P0/P1/P2 작업을 정의하고 우선순위대로 하나씩 구현합니다.

## 체크리스트 요약
- P0: 사용자에게 즉각적인 영향을 주는 문제들(로딩, 폼 검증, 인증 흐름)
- P1: 접근성, 상태 관리 최적화, 로깅·에러 중앙화
- P2: 성능 개선, 코드 스플리팅, 테스트 보강

---

## P0 (즉시, 우선순위 높음)
1. BetaOnboarding2: 클라이언트 폼 검증, 제출중 로더/disabled, 서버 에러 표시, 성공 토스트/리다이렉션
2. apiClient: 전역 에러 인터셉터(401 처리) 및 토큰 첨부 일관화
3. authStore: 토큰 만료 처리(로그아웃/리프레시)와 로딩/error 상태 플래그 정리
4. 전역 로더/토스트 컴포넌트 확보(`ui/alert.jsx` 활용 또는 간단 구현)

---

## P1 (중요)
1. 접근성 개선: aria, focus, keyboard navigation, 색 대비 점검
2. 로깅/오류 수집: Sentry(또는 유사) 연동 기초 코드 삽입, 에러 포맷 표준화
3. 상태관리 최적화: stores에서 selector/모듈화로 리렌더 최소화
4. 스모크 자동화 스크립트 작성(온보딩 → 퀴즈 흐름)

---

## P2 (권장)
1. 코드 스플리팅: 무거운 AI 컴포넌트 lazy 로드
2. UI 일관성: Tailwind 토큰화 및 `ui/*` 표준 컴포넌트로 통합
3. E2E 테스트: Playwright 또는 Cypress로 핵심 흐름 검증
4. 번들 분석 및 Lighthouse 개선 작업

---

## 시행 계획
- Step 0: 레포에서 현재 구현 확인(BetaOnboarding2, apiClient, authStore) — 완료
- Step 1: P0-1 (BetaOnboarding2) 구현 및 테스트
- Step 2: P0-2 (apiClient) 변경 및 통합 테스트
- Step 3: P0-3 (authStore) 보완
- Step 4: P1 항목 순차적으로 적용

---

준비가 되었으면 Step 1 구현을 시작합니다: `BetaOnboarding2.jsx`에 폼 검증(yup 또는 간단한 검사), 제출 로더, 서버 에러 표시를 추가하고, `apiClient`에 에러 포맷을 확인해 통합하겠습니다.
