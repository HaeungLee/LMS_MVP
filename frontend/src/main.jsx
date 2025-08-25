import React from 'react'
import ReactDOM from 'react-dom/client'
import './index.css'
import App from './App.jsx'
import { getMe, refreshSession, hasRefreshCookie } from './services/apiClient.js'

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)

// 부팅 시 자동 로그인: me → (쿠키 있을 때만) refresh → me 재시도
;(async () => {
  try {
    await getMe()
    return
  } catch {}
  try {
    const status = await hasRefreshCookie()
    if (status?.has) {
      await refreshSession()
      await getMe()
    }
  } catch {
    // 무시: 비로그인 상태 유지
  }
})()
