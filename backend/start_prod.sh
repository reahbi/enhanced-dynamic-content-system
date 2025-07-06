#!/bin/bash
# 프로덕션 서버 시작 스크립트

echo "🚀 하이브리드 Paper-Based Content System 프로덕션 서버 시작..."

# 가상 환경 활성화 (있을 경우)
if [ -d "venv" ]; then
    echo "📦 가상 환경 활성화..."
    source venv/bin/activate
elif [ -d ".venv" ]; then
    echo "📦 가상 환경 활성화..."
    source .venv/bin/activate
fi

# 환경 변수 로드 (있을 경우)
if [ -f ".env.production" ]; then
    echo "🔐 프로덕션 환경 변수 로드..."
    export $(cat .env.production | grep -v '^#' | xargs)
elif [ -f ".env" ]; then
    echo "🔐 환경 변수 로드..."
    export $(cat .env | grep -v '^#' | xargs)
fi

# 의존성 설치 확인
echo "📚 의존성 확인..."
pip install -q -r requirements.txt

# 워커 수 계산 (CPU 코어 * 2 + 1)
WORKERS=$(python -c "import multiprocessing; print(multiprocessing.cpu_count() * 2 + 1)")
echo "💪 워커 프로세스: $WORKERS"

# 서버 실행
echo "🎯 프로덕션 서버 시작 중..."
python run_server.py --no-reload --workers $WORKERS --host 0.0.0.0 --log-level warning