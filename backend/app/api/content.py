from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel, Field
import uuid
import time
from datetime import datetime

from app.models.database import get_db, Content, Category, Paper
from app.services.gemini_client import GeminiClient, SubcategoryResult, PaperInfo

router = APIRouter()

# Pydantic models
class ContentGenerateRequest(BaseModel):
    category_id: str
    subcategory_name: str
    subcategory_description: str
    papers: List[dict]  # Paper information
    expected_effect: str
    quality_score: float
    quality_grade: str
    content_types: List[str] = Field(default=["shorts", "article", "report"])

class ContentResponse(BaseModel):
    id: str
    category_id: str
    paper_id: Optional[str]
    content_type: str
    title: str
    content: str
    quality_score: float
    generation_time: float
    created_at: datetime
    
    class Config:
        from_attributes = True

# Initialize Gemini client
gemini_client = GeminiClient()

@router.post("/generate", response_model=List[ContentResponse])
async def generate_content(
    request: ContentGenerateRequest,
    db: Session = Depends(get_db)
):
    """Generate multiple content formats based on papers"""
    try:
        # Verify category exists
        category = db.query(Category).filter(Category.id == request.category_id).first()
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")
        
        # Create SubcategoryResult from request
        papers = []
        paper_ids = []
        
        for p in request.papers:
            papers.append(PaperInfo(
                title=p["title"],
                authors=p["authors"],
                journal=p["journal"],
                year=p["publication_year"],
                doi=p["doi"],
                impact_factor=p.get("impact_factor", 3.0),
                citations=p.get("citations", 50),
                paper_type=p.get("paper_type", "Research Article")
            ))
            
            # Find paper in database
            db_paper = db.query(Paper).filter(Paper.doi == p["doi"]).first()
            if db_paper:
                paper_ids.append(db_paper.id)
        
        subcategory = SubcategoryResult(
            name=request.subcategory_name,
            description=request.subcategory_description,
            papers=papers,
            expected_effect=request.expected_effect,
            quality_score=request.quality_score,
            quality_grade=request.quality_grade
        )
        
        # Generate content for each type
        generated_contents = []
        
        for content_type in request.content_types:
            start_time = time.time()
            
            # Generate content using Gemini
            result = gemini_client.generate_content(subcategory, content_type)
            
            generation_time = time.time() - start_time
            
            # Save to database
            db_content = Content(
                id=str(uuid.uuid4()),
                category_id=request.category_id,
                paper_id=paper_ids[0] if paper_ids else None,  # Link to first paper
                content_type=content_type,
                title=f"{request.subcategory_name} - {content_type.upper()}",
                content=result["content"],
                thinking_process=f"Generated from {len(papers)} papers",
                quality_score=result["quality_score"],
                generation_time=generation_time
            )
            db.add(db_content)
            generated_contents.append(db_content)
        
        db.commit()
        
        return generated_contents
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_model=List[ContentResponse])
async def list_contents(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    content_type: Optional[str] = None,
    category_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """List all generated contents"""
    query = db.query(Content)
    
    if content_type:
        query = query.filter(Content.content_type == content_type)
    
    if category_id:
        query = query.filter(Content.category_id == category_id)
    
    contents = query.offset(skip).limit(limit).all()
    return contents

@router.get("/{content_id}", response_model=ContentResponse)
async def get_content(
    content_id: str,
    db: Session = Depends(get_db)
):
    """Get a specific content"""
    content = db.query(Content).filter(Content.id == content_id).first()
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")
    return content

@router.delete("/{content_id}")
async def delete_content(
    content_id: str,
    db: Session = Depends(get_db)
):
    """Delete a content"""
    content = db.query(Content).filter(Content.id == content_id).first()
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")
    
    db.delete(content)
    db.commit()
    
    return {"message": "Content deleted successfully"}

@router.get("/statistics/summary")
async def get_content_statistics(
    db: Session = Depends(get_db)
):
    """Get content generation statistics"""
    total_contents = db.query(Content).count()
    
    # Count by type
    shorts_count = db.query(Content).filter(Content.content_type == "shorts").count()
    article_count = db.query(Content).filter(Content.content_type == "article").count()
    report_count = db.query(Content).filter(Content.content_type == "report").count()
    
    # Average generation time
    contents = db.query(Content).all()
    avg_generation_time = sum(c.generation_time for c in contents) / len(contents) if contents else 0
    
    # Average quality score
    avg_quality_score = sum(c.quality_score for c in contents) / len(contents) if contents else 0
    
    return {
        "total_contents": total_contents,
        "by_type": {
            "shorts": shorts_count,
            "article": article_count,
            "report": report_count
        },
        "average_generation_time": round(avg_generation_time, 2),
        "average_quality_score": round(avg_quality_score, 1)
    }