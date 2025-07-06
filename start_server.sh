#!/bin/bash
# Enhanced Dynamic Content System v6.1 서버 시작 스크립트

# 스크립트 위치 확인
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
BACKEND_DIR="$SCRIPT_DIR/backend"

# 백엔드 디렉토리로 이동
cd "$BACKEND_DIR"

# 환경 변수 로드
if [ -f ".env" ]; then
    export $(cat .env | grep -v '^#' | xargs)
    echo "✅ 환경 변수 로드됨"
fi

# Python 스크립트 실행
echo "🚀 서버 시작 중..."
python3 run_server.py "$@"