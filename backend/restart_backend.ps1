# 백엔드 재시작 스크립트 - 좀비 연결 정리

Write-Host "🛑 기존 백엔드 프로세스 종료 중..." -ForegroundColor Yellow

# 8000번 포트를 사용하는 프로세스 찾기
$processes = netstat -ano | findstr :8000 | ForEach-Object {
    if ($_ -match '\s+(\d+)$') {
        $matches[1]
    }
} | Select-Object -Unique

if ($processes) {
    foreach ($pid in $processes) {
        try {
            Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue
            Write-Host "✅ PID $pid 종료됨" -ForegroundColor Green
        } catch {
            Write-Host "⚠️ PID $pid 종료 실패" -ForegroundColor Red
        }
    }
    
    # 프로세스가 완전히 종료될 때까지 대기
    Start-Sleep -Seconds 2
} else {
    Write-Host "ℹ️ 실행 중인 백엔드 없음" -ForegroundColor Cyan
}

# 가상환경 활성화 확인
if (-not $env:VIRTUAL_ENV) {
    Write-Host "🔧 가상환경 활성화 중..." -ForegroundColor Yellow
    & .\venv\Scripts\Activate.ps1
}

Write-Host ""
Write-Host "🚀 백엔드 서버 시작 중..." -ForegroundColor Green
Write-Host "📍 http://127.0.0.1:8000" -ForegroundColor Cyan
Write-Host "📖 API Docs: http://127.0.0.1:8000/docs" -ForegroundColor Cyan
Write-Host ""

# uvicorn 실행 with keep-alive timeout 설정
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000 --timeout-keep-alive 30
