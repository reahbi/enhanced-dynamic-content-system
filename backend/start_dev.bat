@echo off
REM 개발 서버 시작 스크립트 (Windows)

echo 🚀 하이브리드 Paper-Based Content System 개발 서버 시작...

REM 가상 환경 활성화 (있을 경우)
if exist venv\Scripts\activate.bat (
    echo 📦 가상 환경 활성화...
    call venv\Scripts\activate.bat
) else if exist .venv\Scripts\activate.bat (
    echo 📦 가상 환경 활성화...
    call .venv\Scripts\activate.bat
)

REM 환경 변수 로드
if exist .env (
    echo 🔐 환경 변수 로드...
    for /f "tokens=*" %%a in (.env) do (
        set %%a
    )
)

REM 의존성 설치 확인
echo 📚 의존성 확인...
pip install -q -r requirements.txt 2>nul || echo ⚠️  requirements.txt 파일이 없거나 일부 패키지 설치 실패

REM 서버 실행
echo 🎯 서버 시작 중...
python run_server.py --reload --log-level info