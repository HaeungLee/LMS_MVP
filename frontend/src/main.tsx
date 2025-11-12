import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.tsx'

// Week 4: Strict Mode 재활성화 완료 ✅
// TanStack Query 설정 개선으로 중복 요청 문제 해결
createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
  </StrictMode>
)
