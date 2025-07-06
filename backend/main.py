#!/usr/bin/env python3
"""
FastAPI 메인 애플리케이션
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from datetime import datetime
import os
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

# API 라우터 임포트
from app.api.categories import router as categories_router
from app.api.papers import router as papers_router
from app.api.contents import router as contents_router
from app.api.health import router as health_router
from app.api.cache import router as cache_router
from app.api.analytics import router as analytics_router

# Lifespan context manager for startup/shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Initializing application...")
    print(f"Gemini API Key loaded: {'Yes' if os.getenv('GEMINI_API_KEY') else 'No'}")
    yield
    # Shutdown
    print("Shutting down...")

# Create FastAPI app
app = FastAPI(
    title="Enhanced Dynamic Content System v6.1",
    description="AI-powered content generation system based on academic papers",
    version="6.1.0",
    lifespan=lifespan
)

# Configure CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 개발 환경에서는 모든 origin 허용
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(categories_router, prefix="/api/v1/categories", tags=["categories"])
app.include_router(papers_router, prefix="/api/v1/papers", tags=["papers"])
app.include_router(contents_router, prefix="/api/v1/contents", tags=["contents"])
app.include_router(health_router, prefix="/api/v1/health", tags=["health"])
app.include_router(cache_router, prefix="/api/v1/cache", tags=["cache"])
app.include_router(analytics_router, prefix="/api/v1/analytics", tags=["analytics"])

@app.get("/")
async def root():
    return {
        "message": "Enhanced Dynamic Content System v6.1 API",
        "version": "6.1.0",
        "docs": "/docs",
        "redoc": "/redoc",
        "endpoints": {
            "categories": "/api/v1/categories",
            "papers": "/api/v1/papers",
            "contents": "/api/v1/contents",
            "health": "/api/v1/health",
            "cache": "/api/v1/cache",
            "analytics": "/api/v1/analytics"
        }
    }

@app.get("/health")
async def health_check():
    """Quick health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)