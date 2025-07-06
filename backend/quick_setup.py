#!/usr/bin/env python3
"""
빠른 설정 스크립트
"""

import os
from pathlib import Path


def create_directories():
    """필요한 디렉토리 생성"""
    print("📁 디렉토리 생성 중...")
    
    directories = [
        "logs",
        "cache",
        "cache/advanced",
        "exports",
        "exports/analytics",
        "exports/monitoring",
        "data"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
    
    print("✅ 모든 디렉토리 생성 완료")


def create_env_file():
    """환경 변수 파일 생성"""
    print("\n🔐 환경 변수 파일 확인...")
    
    env_path = Path(".env")
    
    if env_path.exists():
        print("✅ .env 파일이 이미 존재합니다.")
        return
    
    # .env 파일 생성
    with open(env_path, 'w') as f:
        f.write("# 환경 변수 설정\n")
        f.write("# GEMINI_API_KEY를 실제 API 키로 변경해주세요!\n")
        f.write("GEMINI_API_KEY=your-gemini-api-key-here\n")
        f.write("DATABASE_URL=sqlite:///./data/app.db\n")
        f.write("ENVIRONMENT=development\n")
        f.write("LOG_LEVEL=INFO\n")
        f.write("SECRET_KEY=development-secret-key-change-in-production\n")
    
    print("📝 .env 파일 생성됨")
    print("⚠️  .env 파일의 GEMINI_API_KEY를 실제 API 키로 변경해주세요!")


def main():
    """메인 설정 함수"""
    print("🚀 빠른 설정 시작\n")
    
    try:
        # 1. 디렉토리 생성
        create_directories()
        
        # 2. 환경 변수 파일 생성
        create_env_file()
        
        print("\n✨ 설정 완료!")
        print("\n다음 단계:")
        print("1. .env 파일에서 GEMINI_API_KEY를 실제 API 키로 변경하세요.")
        print("2. 서버 실행: python run_server.py")
        print("\n서버가 시작되면 http://localhost:8000/docs 에서 API 문서를 확인할 수 있습니다.")
        
    except Exception as e:
        print(f"\n❌ 설정 중 오류 발생: {e}")


if __name__ == "__main__":
    main()