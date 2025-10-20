import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.tsx'

// Week 3: Strict Mode 임시 비활성화 (중복 요청 취소 이슈)
// TODO Week 4: 중복 요청 처리 로직 개선 후 Strict Mode 재활성화
createRoot(document.getElementById('root')!).render(
  <App />
)
