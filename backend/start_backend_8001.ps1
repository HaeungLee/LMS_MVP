# 백엔드 시작 스크립트 (포트 8001 사용)

Write-Host "🚀 백엔드 서버 시작 중..." -ForegroundColor Green
Write-Host "📍 http://127.0.0.1:8001" -ForegroundColor Cyan
Write-Host "📖 API Docs: http://127.0.0.1:8001/docs" -ForegroundColor Cyan
Write-Host ""
Write-Host "💡 포트 8000이 점유되어 8001 포트 사용" -ForegroundColor Yellow
Write-Host "   프론트엔드 .env 파일에서 VITE_API_BASE_URL을 수정하세요:" -ForegroundColor Yellow
Write-Host "   VITE_API_BASE_URL=http://localhost:8001" -ForegroundColor Cyan
Write-Host ""

# uvicorn 실행
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8001 --timeout-keep-alive 30
