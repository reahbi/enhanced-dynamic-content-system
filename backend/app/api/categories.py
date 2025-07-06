"""
카테고리 관련 API 엔드포인트
"""

from fastapi import APIRouter, HTTPException, Query, Depends, BackgroundTasks
from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional
from sqlalchemy.orm import Session
import json

from ..models.database import get_db, Category as CategoryModel, Subcategory as SubcategoryModel
from ..services.category_optimizer import CategoryOptimizer
from ..services.advanced_cache_manager import advanced_cache
from ..services.performance_optimizer import performance_optimizer
from ..utils.logging_config import app_logger, audit_logger
from ..utils.bug_fixes import bug_fix_utils
from ..utils.token_tracker import token_tracker

router = APIRouter()

# Pydantic 모델
class CategoryRequest(BaseModel):
    """카테고리 생성 요청"""
    keyword: str = Field(..., min_length=1, max_length=100, description="검색 키워드")
    count: int = Field(default=10, ge=1, le=20, description="생성할 카테고리 수")
    force_new: bool = Field(default=False, description="캐시 무시하고 새로 생성")
    
class CategoryResponse(BaseModel):
    """카테고리 응답"""
    id: str
    name: str
    emoji: str
    description: str
    practicality_score: float
    interest_score: float
    created_at: str
    content_count: Optional[int] = Field(default=0, description="연결된 콘텐츠 수")

class CategoryListResponse(BaseModel):
    """카테고리 목록 응답"""
    categories: List[CategoryResponse]
    total: int
    keyword: str
    generated_at: str

# 의존성
async def get_category_optimizer():
    """카테고리 최적화기 인스턴스"""
    return CategoryOptimizer()

async def get_gemini_client():
    """Gemini 클라이언트 인스턴스"""
    from ..services.gemini_client import GeminiClient
    return GeminiClient()

@router.post("/generate", response_model=CategoryListResponse)
@performance_optimizer.measure_performance("category_generation")
async def generate_categories(
    request: CategoryRequest,
    gemini_client = Depends(get_gemini_client),
    db: Session = Depends(get_db)
):
    """키워드 기반 카테고리 생성"""
    try:
        # 입력 검증 및 정제
        keyword = bug_fix_utils.safe_string_processing(request.keyword)
        if not keyword:
            raise HTTPException(status_code=400, detail="유효한 키워드를 입력해주세요")
            
        # 항상 새로운 카테고리 생성 (캐시 사용 안함)
        app_logger.info(f"새로운 카테고리 생성 요청: {keyword}")
        
        # 토큰 추적기 초기화 (새 워크플로우 시작)
        token_tracker.reset()
            
        # 카테고리 생성 (Gemini AI 사용)
        app_logger.info(f"카테고리 생성 시작: {keyword}")
        categories = gemini_client.generate_categories(
            keyword=keyword,
            count=request.count
        )
        
        # 생성된 카테고리 로깅
        app_logger.info(f"생성된 카테고리 수: {len(categories)}")
        for cat in categories:
            app_logger.info(f"카테고리: {cat.name}")
        
        # 필터링 없이 모든 카테고리 사용
        filtered_categories = categories
        
        # 응답 생성 및 데이터베이스 저장
        response_categories = []
        for cat in filtered_categories:
            cat_id = f"cat_{hash(cat.name)}"
            
            # 데이터베이스에 존재하는지 확인
            existing_cat = db.query(CategoryModel).filter(CategoryModel.id == cat_id).first()
            if not existing_cat:
                # 새 카테고리 생성
                db_category = CategoryModel(
                    id=cat_id,
                    name=cat.name,
                    emoji=cat.emoji or '📌',
                    description=cat.description or '',
                    seed_keyword=keyword,
                    practicality_score=cat.research_activity,  # research_activity는 practicality_score를 담고 있음
                    interest_score=cat.trend_score  # trend_score는 interest_score를 담고 있음
                )
                db.add(db_category)
                db.commit()
                db.refresh(db_category)
                created_at = db_category.created_at.isoformat()
            else:
                created_at = existing_cat.created_at.isoformat()
            
            # 콘텐츠 수 계산
            from ..models.database import Content as ContentModel
            content_count = db.query(ContentModel).filter(ContentModel.category_id == cat_id).count()
            
            response_categories.append(CategoryResponse(
                id=cat_id,
                name=cat.name,
                emoji=cat.emoji or '📌',
                description=cat.description or '',
                practicality_score=cat.research_activity,  # research_activity는 practicality_score를 담고 있음
                interest_score=cat.trend_score,  # trend_score는 interest_score를 담고 있음
                created_at=created_at,
                content_count=content_count
            ))
            
        response = CategoryListResponse(
            categories=response_categories,
            total=len(response_categories),
            keyword=keyword,
            generated_at=datetime.now().isoformat()
        )
        
        # 캐시 저장하지 않음 - 항상 새로 생성
        
        # 감사 로깅
        audit_logger.log_action(
            action="generate_categories",
            entity_type="category",
            entity_id=keyword,
            changes={"count": len(response_categories)}
        )
        
        return response
        
    except Exception as e:
        app_logger.error(f"카테고리 생성 실패: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="카테고리 생성 중 오류가 발생했습니다")

@router.get("/", response_model=CategoryListResponse)
async def list_categories(
    page: int = Query(1, ge=1, description="페이지 번호"),
    size: int = Query(10, ge=1, le=50, description="페이지 크기"),
    sort_by: str = Query("practicality", regex="^(practicality|interest|name)$"),
    db: Session = Depends(get_db)
):
    """저장된 카테고리 목록 조회"""
    try:
        # 데이터베이스에서 카테고리 조회
        query = db.query(CategoryModel)
        
        # 정렬
        if sort_by == "practicality":
            query = query.order_by(CategoryModel.practicality_score.desc())
        elif sort_by == "interest":
            query = query.order_by(CategoryModel.interest_score.desc())
        else:
            query = query.order_by(CategoryModel.name)
        
        # 페이지네이션
        offset = (page - 1) * size
        db_categories = query.offset(offset).limit(size).all()
        total = query.count()
        
        # 응답 생성 및 콘텐츠 수 계산
        from ..models.database import Content as ContentModel
        response_categories = []
        for cat in db_categories:
            # 해당 카테고리의 콘텐츠 수 계산
            content_count = db.query(ContentModel).filter(ContentModel.category_id == cat.id).count()
            
            response_categories.append(CategoryResponse(
                id=cat.id,
                name=cat.name,
                emoji=cat.emoji or '📌',
                description=cat.description or '',
                practicality_score=cat.practicality_score or 0.0,
                interest_score=cat.interest_score or 0.0,
                created_at=cat.created_at.isoformat(),
                content_count=content_count
            ))
        
        return CategoryListResponse(
            categories=response_categories,
            total=total,
            keyword="all",
            generated_at=datetime.now().isoformat()
        )
        
    except Exception as e:
        app_logger.error(f"카테고리 목록 조회 실패: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="카테고리 목록 조회 중 오류가 발생했습니다")

@router.get("/{category_id}", response_model=CategoryResponse)
async def get_category(category_id: str, db: Session = Depends(get_db)):
    """특정 카테고리 상세 조회"""
    try:
        # 데이터베이스에서 카테고리 조회
        db_category = db.query(CategoryModel).filter(CategoryModel.id == category_id).first()
        
        if not db_category:
            raise HTTPException(status_code=404, detail="카테고리를 찾을 수 없습니다")
        
        return CategoryResponse(
            id=db_category.id,
            name=db_category.name,
            emoji=db_category.emoji or '📌',
            description=db_category.description or '',
            practicality_score=db_category.practicality_score or 0.0,
            interest_score=db_category.interest_score or 0.0,
            created_at=db_category.created_at.isoformat()
        )
            
    except HTTPException:
        raise
    except Exception as e:
        app_logger.error(f"카테고리 조회 실패: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="카테고리 조회 중 오류가 발생했습니다")

@router.delete("/{category_id}")
async def delete_category(category_id: str, db: Session = Depends(get_db)):
    """카테고리 삭제"""
    try:
        # 데이터베이스에서 카테고리 조회
        db_category = db.query(CategoryModel).filter(CategoryModel.id == category_id).first()
        
        if not db_category:
            raise HTTPException(status_code=404, detail="카테고리를 찾을 수 없습니다")
        
        # 해당 카테고리에 연결된 콘텐츠가 있는지 확인
        from ..models.database import Content as ContentModel
        content_count = db.query(ContentModel).filter(ContentModel.category_id == category_id).count()
        
        if content_count > 0:
            raise HTTPException(
                status_code=400, 
                detail=f"이 카테고리에 {content_count}개의 콘텐츠가 연결되어 있습니다. 콘텐츠를 먼저 삭제해주세요."
            )
        
        # 서브카테고리 확인 및 삭제
        subcategory_count = db.query(SubcategoryModel).filter(SubcategoryModel.category_id == category_id).count()
        if subcategory_count > 0:
            # 서브카테고리는 함께 삭제
            db.query(SubcategoryModel).filter(SubcategoryModel.category_id == category_id).delete()
        
        # 카테고리 삭제
        db.delete(db_category)
        db.commit()
        
        app_logger.info(f"카테고리 삭제 완료: {category_id}")
        
        return {"message": "카테고리가 성공적으로 삭제되었습니다", "id": category_id}
            
    except HTTPException:
        raise
    except Exception as e:
        app_logger.error(f"카테고리 삭제 실패: {e}", exc_info=True)
        db.rollback()
        raise HTTPException(status_code=500, detail="카테고리 삭제 중 오류가 발생했습니다")

@router.get("/popular/trending", response_model=CategoryListResponse)
async def get_trending_categories(
    period: str = Query("week", regex="^(day|week|month)$", description="기간")
):
    """인기 카테고리 조회"""
    try:
        # TODO: 실제 인기도 계산 로직 구현
        # 현재는 샘플 데이터 반환
        trending_categories = [
            CategoryResponse(
                id="trend_1",
                name="🔥 HIIT 운동법",
                emoji="🔥",
                description="고강도 인터벌 트레이닝으로 효율적인 운동",
                practicality_score=9.5,
                interest_score=9.8,
                created_at=datetime.now().isoformat()
            )
        ]
        
        return CategoryListResponse(
            categories=trending_categories,
            total=len(trending_categories),
            keyword=f"trending_{period}",
            generated_at=datetime.now().isoformat()
        )
        
    except Exception as e:
        app_logger.error(f"인기 카테고리 조회 실패: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="인기 카테고리 조회 중 오류가 발생했습니다")

@router.post("/{category_id}/subcategories", response_model=CategoryListResponse)
async def generate_subcategories(
    category_id: str,
    count: int = Query(5, ge=1, le=10, description="생성할 서브카테고리 수"),
    optimizer: CategoryOptimizer = Depends(get_category_optimizer)
):
    """카테고리의 서브카테고리 생성"""
    try:
        # TODO: 카테고리 정보 조회
        # 현재는 샘플로 진행
        
        # 서브카테고리 생성
        subcategories = await optimizer.generate_subcategories(
            category_name="홈트레이닝 루틴",
            count=count
        )
        
        response_categories = []
        for sub in subcategories:
            response_categories.append(CategoryResponse(
                id=f"sub_{hash(sub['name'])}",
                name=sub['name'],
                emoji=sub.get('emoji', '📌'),
                description=sub.get('description', ''),
                practicality_score=sub.get('practicality_score', 7.0),
                interest_score=sub.get('interest_score', 7.0),
                created_at=datetime.now().isoformat()
            ))
            
        return CategoryListResponse(
            categories=response_categories,
            total=len(response_categories),
            keyword=f"subcategories_of_{category_id}",
            generated_at=datetime.now().isoformat()
        )
        
    except Exception as e:
        app_logger.error(f"서브카테고리 생성 실패: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="서브카테고리 생성 중 오류가 발생했습니다")

class SubcategoryRequest(BaseModel):
    """서브카테고리 생성 요청"""
    category_name: str = Field(..., min_length=1, max_length=200, description="카테고리명")

@router.post("/generate-subcategories")
@performance_optimizer.measure_performance("subcategory_generation")
async def generate_subcategories_auto(
    request: SubcategoryRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """선택된 카테고리에 대한 서브카테고리 자동 생성"""
    try:
        # 입력 검증
        category_name = bug_fix_utils.safe_string_processing(request.category_name)
        
        if not category_name:
            raise HTTPException(status_code=400, detail="유효한 카테고리명을 입력해주세요")
        
        app_logger.info(f"서브카테고리 자동 생성 요청: {category_name}")
        
        # 토큰 추적기 초기화 (새 워크플로우 시작)
        token_tracker.reset()
        
        # Gemini 클라이언트 초기화
        from ..services.gemini_client import GeminiClient
        gemini_client = GeminiClient()
        
        # 서브카테고리 생성을 위한 주제 목록 생성
        topics = await gemini_client.generate_subcategory_topics(category_name, count=5)
        
        # 각 주제에 대해 논문 검색 및 서브카테고리 생성
        subcategories = []
        successful_count = 0
        
        for topic in topics:
            if successful_count >= 3:  # 최대 3개의 서브카테고리만 생성
                break
                
            # 논문 기반 서브카테고리 생성 시도
            result = gemini_client.discover_papers_for_topic(category_name, topic)
            
            if result:
                # 카테고리 ID 찾기
                db_category = db.query(CategoryModel).filter(CategoryModel.name == category_name).first()
                if not db_category:
                    # 카테고리가 없으면 생성
                    cat_id = f"cat_{hash(category_name)}"
                    db_category = CategoryModel(
                        id=cat_id,
                        name=category_name,
                        description="",
                        emoji="📌",
                        seed_keyword=category_name
                    )
                    db.add(db_category)
                    db.commit()
                
                # 서브카테고리 데이터베이스에 저장
                subcategory_id = f"sub_{hash(result.name)}"
                db_subcategory = SubcategoryModel(
                    id=subcategory_id,
                    category_id=db_category.id,
                    name=result.name,
                    description=result.description,
                    expected_effect=result.expected_effect,
                    quality_score=result.quality_score,
                    quality_grade=result.quality_grade
                )
                db.add(db_subcategory)
                db.commit()
                
                # 논문들도 데이터베이스에 저장
                from ..models.database import Paper as PaperModel
                for paper in result.papers:
                    paper_id = f"paper_{hash(paper.title)}"
                    existing_paper = db.query(PaperModel).filter(PaperModel.id == paper_id).first()
                    if not existing_paper:
                        db_paper = PaperModel(
                            id=paper_id,
                            title=paper.title,
                            authors=paper.authors,
                            journal=paper.journal,
                            publication_year=paper.year,
                            doi=paper.doi,
                            impact_factor=paper.impact_factor,
                            citations=paper.citations,
                            paper_type=paper.paper_type,
                            subcategory_id=subcategory_id
                        )
                        db.add(db_paper)
                
                db.commit()
                
                subcategories.append({
                    "id": subcategory_id,
                    "name": result.name,
                    "description": result.description,
                    "papers_count": len(result.papers),
                    "quality_score": result.quality_score,
                    "quality_grade": result.quality_grade,
                    "expected_effect": result.expected_effect,
                    "topic": topic
                })
                successful_count += 1
                
                # 감사 로깅
                audit_logger.log_action(
                    action="generate_subcategory",
                    entity_type="subcategory",
                    entity_id=result.name,
                    changes={
                        "category": category_name,
                        "topic": topic,
                        "papers_found": len(result.papers)
                    }
                )
            
            # 서브카테고리 생성 워크플로우 완료 시 토큰 사용량 로깅
            if successful_count >= 3:
                token_tracker.log_workflow_summary(
                    f"Subcategory Generation Workflow - {category_name}"
                )
        
        if not subcategories:
            raise HTTPException(
                status_code=404,
                detail="해당 카테고리에 대한 논문 기반 서브카테고리를 생성할 수 없습니다."
            )
        
        response = {
            "category": category_name,
            "subcategories": subcategories,
            "total_generated": len(subcategories),
            "generation_timestamp": datetime.now().isoformat()
        }
        
        # 백그라운드에서 추가 서브카테고리 생성 시도
        if len(subcategories) < 3:
            background_tasks.add_task(
                generate_additional_subcategories,
                category_name,
                topics[len(subcategories):],
                subcategories
            )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        app_logger.error(f"서브카테고리 자동 생성 실패: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="서브카테고리 생성 중 오류가 발생했습니다")

async def generate_additional_subcategories(category_name: str, remaining_topics: List[str], existing_subcategories: List[Dict]):
    """백그라운드에서 추가 서브카테고리 생성"""
    try:
        from ..services.gemini_client import GeminiClient
        gemini_client = GeminiClient()
        
        for topic in remaining_topics:
            if len(existing_subcategories) >= 3:
                break
            
            result = gemini_client.discover_papers_for_topic(category_name, topic)
            if result:
                # 결과를 캐시에 저장하거나 DB에 저장
                app_logger.info(f"추가 서브카테고리 생성 성공: {result.name}")
    except Exception as e:
        app_logger.error(f"백그라운드 서브카테고리 생성 실패: {e}")