#!/bin/bash

echo "🚀 Enhanced Dynamic Content System v6.1 시작 스크립트"
echo "================================================="

# 색상 정의
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 환경 확인
check_environment() {
    echo -e "\n${YELLOW}환경 확인 중...${NC}"
    
    # Python 확인
    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}❌ Python 3가 설치되어 있지 않습니다.${NC}"
        exit 1
    fi
    echo -e "${GREEN}✅ Python 3 설치됨${NC}"
    
    # Node.js 확인
    if ! command -v node &> /dev/null; then
        echo -e "${RED}❌ Node.js가 설치되어 있지 않습니다.${NC}"
        exit 1
    fi
    echo -e "${GREEN}✅ Node.js 설치됨${NC}"
    
    # .env 파일 확인
    if [ ! -f ".env" ]; then
        echo -e "${RED}❌ .env 파일이 없습니다.${NC}"
        echo "GEMINI_API_KEY를 설정해주세요."
        exit 1
    fi
    echo -e "${GREEN}✅ .env 파일 존재${NC}"
}

# Backend 시작
start_backend() {
    echo -e "\n${YELLOW}Backend 시작 중...${NC}"
    cd backend
    
    # 가상환경 확인
    if [ ! -d "venv" ]; then
        echo "가상환경 생성 중..."
        python3 -m venv venv
    fi
    
    # 가상환경 활성화 및 패키지 설치
    source venv/bin/activate
    pip install -q -r requirements.txt
    
    # Backend 시작
    echo -e "${GREEN}✅ Backend 시작 (http://localhost:8000)${NC}"
    uvicorn app.main:app --reload &
    BACKEND_PID=$!
    cd ..
}

# Frontend 시작
start_frontend() {
    echo -e "\n${YELLOW}Frontend 시작 중...${NC}"
    cd frontend
    
    # 패키지 설치
    if [ ! -d "node_modules" ]; then
        echo "패키지 설치 중..."
        npm install
    fi
    
    # Frontend 시작
    echo -e "${GREEN}✅ Frontend 시작 (http://localhost:3000)${NC}"
    npm run dev &
    FRONTEND_PID=$!
    cd ..
}

# 종료 처리
cleanup() {
    echo -e "\n${YELLOW}시스템 종료 중...${NC}"
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    echo -e "${GREEN}✅ 시스템이 종료되었습니다.${NC}"
    exit 0
}

# Ctrl+C 시그널 처리
trap cleanup INT

# 메인 실행
check_environment
start_backend
sleep 5  # Backend가 시작될 때까지 대기
start_frontend

echo -e "\n${GREEN}=================================================${NC}"
echo -e "${GREEN}✨ Enhanced Dynamic Content System v6.1 시작 완료!${NC}"
echo -e "${GREEN}=================================================${NC}"
echo ""
echo "📍 Backend API: http://localhost:8000/docs"
echo "📍 Frontend App: http://localhost:3000"
echo ""
echo "종료하려면 Ctrl+C를 누르세요."
echo ""

# 프로세스 유지
wait