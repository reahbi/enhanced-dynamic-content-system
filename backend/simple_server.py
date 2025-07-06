#!/usr/bin/env python3
"""
간단한 서버 실행기
"""

import os
import uvicorn
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

if __name__ == "__main__":
    print("🚀 서버 시작 중...")
    print(f"📍 Gemini API Key: {'설정됨' if os.getenv('GEMINI_API_KEY') else '미설정'}")
    
    try:
        uvicorn.run(
            "main:app",
            host="127.0.0.1",
            port=8000,
            reload=True,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n⏹️  서버가 중단되었습니다.")
    except Exception as e:
        print(f"❌ 서버 실행 오류: {e}")