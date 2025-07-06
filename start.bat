@echo off
echo ===================================================
echo Enhanced Dynamic Content System v6.1 시작 스크립트
echo ===================================================

:: 환경 확인
echo.
echo 환경 확인 중...

:: Python 확인
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python이 설치되어 있지 않습니다.
    pause
    exit /b 1
)
echo [OK] Python 설치됨

:: Node.js 확인
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Node.js가 설치되어 있지 않습니다.
    pause
    exit /b 1
)
echo [OK] Node.js 설치됨

:: .env 파일 확인
if not exist ".env" (
    echo [ERROR] .env 파일이 없습니다.
    echo GEMINI_API_KEY를 설정해주세요.
    pause
    exit /b 1
)
echo [OK] .env 파일 존재

:: Backend 시작
echo.
echo Backend 시작 중...
start "Backend Server" cmd /k "cd backend && python -m venv venv && venv\Scripts\activate && pip install -r requirements.txt && uvicorn app.main:app --reload"

:: 5초 대기
timeout /t 5 /nobreak >nul

:: Frontend 시작
echo.
echo Frontend 시작 중...
start "Frontend Server" cmd /k "cd frontend && npm install && npm run dev"

echo.
echo ===================================================
echo Enhanced Dynamic Content System v6.1 시작 완료!
echo ===================================================
echo.
echo Backend API: http://localhost:8000/docs
echo Frontend App: http://localhost:3000
echo.
echo 종료하려면 열린 창들을 닫으세요.
echo.
pause