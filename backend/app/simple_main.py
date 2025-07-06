from fastapi import FastAPI
from datetime import datetime

# Create FastAPI app
app = FastAPI(
    title="Enhanced Dynamic Content System v6.1",
    description="AI-powered content generation system based on academic papers",
    version="6.1.0"
)

@app.get("/")
async def root():
    return {
        "message": "Enhanced Dynamic Content System v6.1 API",
        "version": "6.1.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }

@app.get("/health")
async def health_check():
    """Quick health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}