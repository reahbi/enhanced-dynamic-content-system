#!/bin/bash
# 개발 서버 시작 스크립트

echo "🚀 하이브리드 Paper-Based Content System 개발 서버 시작..."

# 가상 환경 활성화 (있을 경우)
if [ -d "venv" ]; then
    echo "📦 가상 환경 활성화..."
    source venv/bin/activate
elif [ -d ".venv" ]; then
    echo "📦 가상 환경 활성화..."
    source .venv/bin/activate
fi

# 환경 변수 로드 (있을 경우)
if [ -f ".env" ]; then
    echo "🔐 환경 변수 로드..."
    export $(cat .env | grep -v '^#' | xargs)
fi

# 의존성 설치 확인
echo "📚 의존성 확인..."
pip install -q -r requirements.txt 2>/dev/null || echo "⚠️  requirements.txt 파일이 없거나 일부 패키지 설치 실패"

# 서버 실행
echo "🎯 서버 시작 중..."
python run_server.py --reload --log-level info