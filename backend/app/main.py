from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from datetime import datetime
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from app.api import categories, papers, contents, health, cache, analytics
from app.models.database import init_db

# Lifespan context manager for startup/shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Initializing application...")
    # Initialize database
    init_db()
    print("Database initialized successfully")
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
    allow_origins=[
        "http://localhost:3000", 
        "http://localhost:3001", 
        "http://localhost:3002", 
        "http://localhost:3003", 
        "http://localhost:5173"
    ],  # React dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(categories.router, prefix="/api/v1/categories", tags=["categories"])
app.include_router(papers.router, prefix="/api/v1/papers", tags=["papers"])
app.include_router(contents.router, prefix="/api/v1/contents", tags=["contents"])
app.include_router(health.router, prefix="/api/v1/health", tags=["health"])
app.include_router(cache.router, prefix="/api/v1/cache", tags=["cache"])
app.include_router(analytics.router, prefix="/api/v1/analytics", tags=["analytics"])

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