"""
콘텐츠 생성 API 엔드포인트
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks, Query
from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum
import json
from sqlalchemy.orm import Session

from ..models.database import get_db, Content as ContentModel, Category as CategoryModel, Paper as PaperModel

from ..services.advanced_cache_manager import advanced_cache
from ..services.performance_optimizer import performance_optimizer
from ..services.thinking.native_thinking_engine import NativeThinkingEngine
from ..services.content_generators.shorts_generator import ShortsScriptGenerator
from ..services.content_generators.article_generator import ArticleGenerator
from ..services.content_generators.report_generator import ReportGenerator
from ..utils.logging_config import app_logger, audit_logger
from ..utils.token_tracker import token_tracker

router = APIRouter()

# Enums
class ContentType(str, Enum):
    SHORTS = "shorts"
    ARTICLE = "article"
    REPORT = "report"

class ThinkingMode(str, Enum):
    NONE = "none"
    BASIC = "basic"
    ENHANCED = "enhanced"

# Pydantic 모델
class ContentRequest(BaseModel):
    """콘텐츠 생성 요청"""
    topic: str = Field(..., min_length=1, max_length=200, description="콘텐츠 주제")
    category_id: str = Field(..., description="카테고리 ID")
    content_type: ContentType = Field(..., description="콘텐츠 타입")
    paper_ids: List[str] = Field(..., min_items=1, max_items=10, description="논문 ID 목록")
    thinking_mode: ThinkingMode = Field(default=ThinkingMode.ENHANCED, description="사고 모드")
    additional_context: Optional[str] = Field(None, description="추가 컨텍스트")

class GeneratedContent(BaseModel):
    """생성된 콘텐츠"""
    id: str
    topic: str
    category_id: str
    content_type: ContentType
    content: str
    metadata: Dict[str, Any]
    quality_score: float
    thinking_process: Optional[str]
    created_at: str

class ContentResponse(BaseModel):
    """콘텐츠 응답"""
    content: GeneratedContent
    generation_time: float
    cache_hit: bool

class ContentListResponse(BaseModel):
    """콘텐츠 목록 응답"""
    contents: List[GeneratedContent]
    total: int
    filters_applied: Dict[str, Any]

class TransformationType(str, Enum):
    """콘텐츠 변환 타입"""
    HUMANIZE = "humanize"  # 사람이 쓴 것처럼
    SIMPLIFY = "simplify"  # 쉽게 설명
    PRACTICAL = "practical"  # 실용적으로

class ContentTransformRequest(BaseModel):
    """콘텐츠 변환 요청"""
    content_id: str = Field(..., description="변환할 콘텐츠 ID")
    transformation_type: TransformationType = Field(..., description="변환 타입")

class BatchContentRequest(BaseModel):
    """배치 콘텐츠 생성 요청"""
    requests: List[ContentRequest] = Field(..., min_items=1, max_items=10)

# 의존성
def get_thinking_engine():
    """Native Thinking Engine 인스턴스"""
    return NativeThinkingEngine()

def get_content_generators():
    """콘텐츠 생성기 인스턴스들"""
    return {
        ContentType.SHORTS: ShortsScriptGenerator(),
        ContentType.ARTICLE: ArticleGenerator(),
        ContentType.REPORT: ReportGenerator()
    }

@router.post("/generate", response_model=ContentResponse)
@performance_optimizer.measure_performance("content_generation")
async def generate_content(
    request: ContentRequest,
    thinking_engine: NativeThinkingEngine = Depends(get_thinking_engine),
    generators: Dict[ContentType, Any] = Depends(get_content_generators),
    db: Session = Depends(get_db)
):
    """콘텐츠 생성"""
    try:
        start_time = datetime.now()
        
        # 토큰 추적기 초기화 (새 콘텐츠 생성 워크플로우)
        token_tracker.reset()
        
        # 캐시 확인
        cache_key = f"content_{hash(str(request.dict()))}"
        cached_content = advanced_cache.get(cache_key)
        
        if cached_content:
            app_logger.info(f"캐시에서 콘텐츠 반환: {request.topic}")
            return ContentResponse(
                content=cached_content,
                generation_time=0.0,
                cache_hit=True
            )
        
        # 논문 정보 가져오기 (additional_context에서 추출)
        papers = []
        try:
            if request.additional_context:
                context_data = json.loads(request.additional_context)
                if 'papers' in context_data:
                    papers = context_data['papers']
                else:
                    raise HTTPException(
                        status_code=400,
                        detail="논문 정보가 제공되지 않았습니다. 먼저 논문을 검색해주세요."
                    )
            else:
                raise HTTPException(
                    status_code=400,
                    detail="논문 정보가 제공되지 않았습니다. 먼저 논문을 검색해주세요."
                )
        except json.JSONDecodeError:
            app_logger.error("additional_context JSON 파싱 실패")
            raise HTTPException(
                status_code=400,
                detail="잘못된 논문 정보 형식입니다."
            )
        
        # 생성기 선택
        generator = generators.get(request.content_type)
        if not generator:
            raise HTTPException(status_code=400, detail="지원하지 않는 콘텐츠 타입입니다")
        
        # 콘텐츠 생성
        generated_content = generator.generate(
            topic=request.topic,
            papers=papers,
            category_id=request.category_id,
            additional_context=request.additional_context
        )
        
        # 품질 평가
        quality_score = generated_content.quality_score
        
        # Thinking Mode 적용
        thinking_process = None
        if request.thinking_mode != ThinkingMode.NONE:
            thinking_result = thinking_engine.generate_with_thinking(
                prompt=f"Analyze the quality and impact of this {request.content_type} content about {request.topic}",
                require_thinking=(request.thinking_mode == ThinkingMode.ENHANCED)
            )
            thinking_process = thinking_result.thinking_process
            
            # 사고 과정 기반 품질 점수 조정
            if thinking_result.thinking_quality_score > 0.8:
                quality_score = min(100, quality_score * 1.1)
        
        # 결과 생성
        content_id = f"cnt_{datetime.now().strftime('%Y%m%d%H%M%S')}_{hash(request.topic) % 10000}"
        
        # 메타데이터 준비
        metadata = {
            "tone": generated_content.tone,
            "word_count": len(generated_content.content.split()),
            "paper_count": len(papers),
            "generation_method": generator.__class__.__name__,
            "papers": papers  # 논문 정보 추가
        }
        
        # 데이터베이스에 저장
        db_content = ContentModel(
            id=content_id,
            topic=request.topic,
            category_id=request.category_id,
            paper_id=request.paper_ids[0] if request.paper_ids else None,  # 첫 번째 논문 ID 사용
            content_type=request.content_type.value,
            content=generated_content.content,
            content_metadata=json.dumps(metadata),  # JSON으로 직렬화
            thinking_process=thinking_process,
            quality_score=quality_score
        )
        
        db.add(db_content)
        db.commit()
        db.refresh(db_content)
        
        app_logger.info(f"콘텐츠 데이터베이스 저장 완료: {content_id}")
        
        # API 응답용 객체 생성
        result = GeneratedContent(
            id=content_id,
            topic=request.topic,
            category_id=request.category_id,
            content_type=request.content_type,
            content=generated_content.content,
            metadata=metadata,
            quality_score=quality_score,
            thinking_process=thinking_process,
            created_at=db_content.created_at.isoformat()
        )
        
        # 캐시 저장
        advanced_cache.set(
            cache_key, 
            result,
            ttl=3600*24,  # 24시간
            metadata={
                "content_type": request.content_type.value,
                "quality_score": quality_score,
                "topic": request.topic
            }
        )
        
        # 개별 콘텐츠 타입별 워크플로우 완료 시 토큰 사용량 로깅
        # 카테고리 정보 가져오기
        category = db.query(CategoryModel).filter(CategoryModel.id == request.category_id).first()
        category_name = category.name if category else "Unknown Category"
        
        # 각 콘텐츠 타입별로 요약
        token_tracker.log_workflow_summary(
            f"Content Generation Workflow - {category_name} / {request.topic} ({request.content_type.value})"
        )
        
        # report 생성 후 전체 워크플로우 토큰 사용량 총합 로깅
        if request.content_type == ContentType.REPORT:
            # 약간의 지연을 두고 전체 요약 (모든 개별 요약이 끝난 후)
            import asyncio
            await asyncio.sleep(0.1)
            
            app_logger.info("\n" + "="*80)
            app_logger.info("[TOTAL WORKFLOW SUMMARY] 전체 워크플로우 토큰 사용량 총합")
            app_logger.info("="*80)
            
            # 현재 세션의 전체 토큰 사용량 계산
            total_prompt_tokens = 0
            total_response_tokens = 0
            total_tokens = 0
            total_cost = 0.0
            
            for operation, usage in token_tracker.usage_by_operation.items():
                total_prompt_tokens += usage['prompt_tokens']
                total_response_tokens += usage['response_tokens']
                total_tokens += usage['total_tokens']
            
            # 비용 계산
            total_cost_krw = token_tracker._calculate_cost_krw(total_prompt_tokens, total_response_tokens)
            total_cost_usd = token_tracker._calculate_cost_usd(total_prompt_tokens, total_response_tokens)
            
            app_logger.info(f"전체 프로세스: 카테고리 생성 → 서브카테고리 생성 → 콘텐츠 생성 (shorts/article/report)")
            app_logger.info(f"총 작업 수: {sum(usage['count'] for usage in token_tracker.usage_by_operation.values())}")
            app_logger.info(f"총 토큰 사용량: {total_tokens:,}")
            app_logger.info(f"  - 입력 토큰: {total_prompt_tokens:,}")
            app_logger.info(f"  - 출력 토큰: {total_response_tokens:,}")
            app_logger.info(f"예상 총 비용: ${total_cost_usd:,.4f} USD (₩{total_cost_krw:,.2f} KRW)")
            app_logger.info("="*80 + "\n")
        
        # 감사 로깅
        audit_logger.log_action(
            action="generate_content",
            entity_type="content",
            entity_id=content_id,
            changes={
                "topic": request.topic,
                "type": request.content_type.value,
                "quality_score": quality_score
            }
        )
        
        generation_time = (datetime.now() - start_time).total_seconds()
        
        return ContentResponse(
            content=result,
            generation_time=generation_time,
            cache_hit=False
        )
        
    except HTTPException:
        raise
    except Exception as e:
        app_logger.error(f"콘텐츠 생성 실패: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="콘텐츠 생성 중 오류가 발생했습니다")

@router.get("/list", response_model=ContentListResponse)
async def list_contents(
    content_type: Optional[ContentType] = None,
    category_id: Optional[str] = None,
    min_quality: Optional[float] = None,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """생성된 콘텐츠 목록 조회"""
    try:
        # 데이터베이스에서 콘텐츠 조회
        query = db.query(ContentModel)
        
        # 필터링
        if content_type:
            query = query.filter(ContentModel.content_type == content_type.value)
        if category_id:
            query = query.filter(ContentModel.category_id == category_id)
        if min_quality:
            query = query.filter(ContentModel.quality_score >= min_quality)
        
        # 최신순 정렬 및 제한
        db_contents = query.order_by(ContentModel.created_at.desc()).limit(limit).all()
        
        # GeneratedContent 객체로 변환
        contents = []
        for db_content in db_contents:
            metadata = json.loads(db_content.content_metadata) if db_content.content_metadata else {}
            
            content = GeneratedContent(
                id=db_content.id,
                topic=db_content.topic,
                category_id=db_content.category_id,
                content_type=db_content.content_type,
                content=db_content.content,
                metadata=metadata,
                quality_score=db_content.quality_score,
                thinking_process=db_content.thinking_process,
                created_at=db_content.created_at.isoformat()
            )
            contents.append(content)
        
        # 전체 개수 조회
        total_query = db.query(ContentModel)
        if content_type:
            total_query = total_query.filter(ContentModel.content_type == content_type.value)
        if category_id:
            total_query = total_query.filter(ContentModel.category_id == category_id)
        if min_quality:
            total_query = total_query.filter(ContentModel.quality_score >= min_quality)
        
        total = total_query.count()
        
        return ContentListResponse(
            contents=contents,
            total=total,
            filters_applied={
                "content_type": content_type.value if content_type else None,
                "category_id": category_id,
                "min_quality": min_quality
            }
        )
        
    except Exception as e:
        app_logger.error(f"콘텐츠 목록 조회 실패: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="콘텐츠 목록 조회 중 오류가 발생했습니다")

@router.get("/{content_id}", response_model=GeneratedContent)
async def get_content(content_id: str, db: Session = Depends(get_db)):
    """특정 콘텐츠 조회"""
    try:
        # 데이터베이스에서 콘텐츠 조회
        db_content = db.query(ContentModel).filter(ContentModel.id == content_id).first()
        
        if not db_content:
            raise HTTPException(status_code=404, detail="콘텐츠를 찾을 수 없습니다")
        
        # GeneratedContent 객체로 변환
        metadata = json.loads(db_content.content_metadata) if db_content.content_metadata else {}
        
        return GeneratedContent(
            id=db_content.id,
            topic=db_content.topic,
            category_id=db_content.category_id,
            content_type=db_content.content_type,
            content=db_content.content,
            metadata=metadata,
            quality_score=db_content.quality_score,
            thinking_process=db_content.thinking_process,
            created_at=db_content.created_at.isoformat()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        app_logger.error(f"콘텐츠 조회 실패: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="콘텐츠 조회 중 오류가 발생했습니다")

@router.post("/batch/generate")
async def batch_generate_content(
    request: BatchContentRequest,
    background_tasks: BackgroundTasks,
    thinking_engine: NativeThinkingEngine = Depends(get_thinking_engine),
    generators: Dict[ContentType, Any] = Depends(get_content_generators),
    db: Session = Depends(get_db)
):
    """배치 콘텐츠 생성"""
    try:
        batch_id = f"batch_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # 백그라운드 작업으로 처리
        background_tasks.add_task(
            process_batch_generation,
            batch_id,
            request.requests,
            thinking_engine,
            generators,
            db
        )
        
        return {
            "batch_id": batch_id,
            "status": "processing",
            "request_count": len(request.requests),
            "message": "배치 콘텐츠 생성이 시작되었습니다"
        }
        
    except Exception as e:
        app_logger.error(f"배치 콘텐츠 생성 시작 실패: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="배치 콘텐츠 생성 시작 중 오류가 발생했습니다")

async def process_batch_generation(
    batch_id: str,
    requests: List[ContentRequest],
    thinking_engine: NativeThinkingEngine,
    generators: Dict[ContentType, Any],
    db: Session = None
):
    """배치 생성 처리 (백그라운드)"""
    try:
        results = []
        
        for req in requests:
            try:
                # 각 요청 처리
                result = await generate_content(
                    req,
                    thinking_engine,
                    generators
                )
                results.append({
                    "status": "success",
                    "content_id": result.content.id,
                    "topic": req.topic
                })
            except Exception as e:
                results.append({
                    "status": "failed",
                    "topic": req.topic,
                    "error": str(e)
                })
        
        # 결과 캐시에 저장
        advanced_cache.set(
            f"batch_{batch_id}",
            {
                "batch_id": batch_id,
                "status": "completed",
                "results": results,
                "completed_at": datetime.now().isoformat()
            },
            ttl=3600*24  # 24시간
        )
        
        app_logger.info(f"배치 생성 완료: {batch_id}")
        
    except Exception as e:
        app_logger.error(f"배치 생성 실패: {e}", exc_info=True)
        
        # 실패 상태 저장
        advanced_cache.set(
            f"batch_{batch_id}",
            {
                "batch_id": batch_id,
                "status": "failed",
                "error": str(e),
                "failed_at": datetime.now().isoformat()
            },
            ttl=3600*24
        )

@router.get("/batch/{batch_id}")
async def get_batch_status(batch_id: str):
    """배치 생성 상태 조회"""
    try:
        result = advanced_cache.get(f"batch_{batch_id}")
        
        if not result:
            raise HTTPException(status_code=404, detail="배치 작업을 찾을 수 없습니다")
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        app_logger.error(f"배치 상태 조회 실패: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="배치 상태 조회 중 오류가 발생했습니다")

@router.post("/regenerate/{content_id}")
async def regenerate_content(
    content_id: str,
    thinking_mode: ThinkingMode = ThinkingMode.ENHANCED,
    thinking_engine: NativeThinkingEngine = Depends(get_thinking_engine),
    generators: Dict[ContentType, Any] = Depends(get_content_generators),
    db: Session = Depends(get_db)
):
    """콘텐츠 재생성"""
    try:
        # 데이터베이스에서 기존 콘텐츠 조회
        db_content = db.query(ContentModel).filter(ContentModel.id == content_id).first()
        
        if not db_content:
            raise HTTPException(status_code=404, detail="원본 콘텐츠를 찾을 수 없습니다")
        
        # GeneratedContent 객체로 변환
        metadata = json.loads(db_content.content_metadata) if db_content.content_metadata else {}
        existing_content = GeneratedContent(
            id=db_content.id,
            topic=db_content.topic,
            category_id=db_content.category_id,
            content_type=db_content.content_type,
            content=db_content.content,
            metadata=metadata,
            quality_score=db_content.quality_score,
            thinking_process=db_content.thinking_process,
            created_at=db_content.created_at.isoformat()
        )
        
        # 재생성 요청 생성
        paper_ids = [db_content.paper_id] if db_content.paper_id else ["paper_001"]
        request = ContentRequest(
            topic=existing_content.topic,
            category_id=existing_content.category_id,
            content_type=existing_content.content_type,
            paper_ids=paper_ids,
            thinking_mode=thinking_mode
        )
        
        # 콘텐츠 재생성
        result = await generate_content(request, thinking_engine, generators, db)
        
        return {
            "status": "success",
            "original_id": content_id,
            "new_id": result.content.id,
            "message": "콘텐츠가 성공적으로 재생성되었습니다"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        app_logger.error(f"콘텐츠 재생성 실패: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="콘텐츠 재생성 중 오류가 발생했습니다")

@router.post("/transform", response_model=ContentResponse)
async def transform_content(
    request: ContentTransformRequest,
    db: Session = Depends(get_db)
):
    """기존 콘텐츠를 다른 스타일로 변환"""
    try:
        # 기존 콘텐츠 조회
        db_content = db.query(ContentModel).filter(ContentModel.id == request.content_id).first()
        if not db_content:
            raise HTTPException(status_code=404, detail="콘텐츠를 찾을 수 없습니다")
        
        # Gemini 클라이언트 초기화
        from ..services.gemini_client import GeminiClient
        gemini_client = GeminiClient()
        
        # 변환 프롬프트 설정
        transformation_prompts = {
            TransformationType.HUMANIZE: """
아래 콘텐츠를 사람이 직접 쓴 것처럼 자연스럽게 변환해주세요.
- AI가 작성한 느낌을 없애고 개인적인 경험이나 감정이 담긴 것처럼 작성
- 딱딱한 문체를 피하고 친근한 대화체 사용
- 완벽한 문장 구조보다는 자연스러운 흐름 중시
- 적절한 감탄사나 의문문 활용
- HTML 형식은 유지하되 내용만 변환
""",
            TransformationType.SIMPLIFY: """
아래 콘텐츠를 누구나 쉽게 이해할 수 있도록 변환해주세요.
- 전문 용어를 일상적인 표현으로 바꾸기
- 복잡한 개념을 친숙한 예시로 설명
- 긴 문장을 짧고 명확하게 나누기
- 중학생도 이해할 수 있는 수준으로 작성
- HTML 형식은 유지하되 내용만 변환
""",
            TransformationType.PRACTICAL: """
아래 콘텐츠를 실용적이고 행동 중심적으로 변환해주세요.
- 이론보다는 실제 적용 방법 중심으로 설명
- 구체적인 실행 단계와 팁 제공
- "어떻게" 할 수 있는지에 초점
- 즉시 시도해볼 수 있는 실천 방안 포함
- HTML 형식은 유지하되 내용만 변환
"""
        }
        
        # 변환 실행
        prompt = f"{transformation_prompts[request.transformation_type]}\n\n원본 콘텐츠:\n{db_content.content}"
        
        transformed_content = gemini_client.transform_content(
            content=db_content.content,
            transformation_type=request.transformation_type,
            prompt=prompt
        )
        
        # 새로운 콘텐츠 ID 생성
        new_content_id = f"cnt_transformed_{datetime.now().strftime('%Y%m%d%H%M%S')}_{hash(request.content_id) % 10000}"
        
        # 메타데이터 업데이트
        metadata = json.loads(db_content.content_metadata) if db_content.content_metadata else {}
        metadata['transformation_type'] = request.transformation_type.value
        metadata['original_content_id'] = request.content_id
        metadata['transformed_at'] = datetime.now().isoformat()
        
        # 변환된 콘텐츠 저장
        db_transformed = ContentModel(
            id=new_content_id,
            topic=f"{db_content.topic} (변환됨)",
            category_id=db_content.category_id,
            paper_id=db_content.paper_id,
            content_type=db_content.content_type,
            content=transformed_content,
            content_metadata=json.dumps(metadata),
            thinking_process=db_content.thinking_process,
            quality_score=db_content.quality_score
        )
        
        db.add(db_transformed)
        db.commit()
        db.refresh(db_transformed)
        
        # 응답 생성
        return ContentResponse(
            content=GeneratedContent(
                id=db_transformed.id,
                topic=db_transformed.topic,
                category_id=db_transformed.category_id,
                content_type=db_transformed.content_type,
                content=db_transformed.content,
                metadata=metadata,
                quality_score=db_transformed.quality_score,
                thinking_process=db_transformed.thinking_process,
                created_at=db_transformed.created_at.isoformat()
            ),
            generation_time=0.0,
            cache_hit=False
        )
        
    except HTTPException:
        raise
    except Exception as e:
        app_logger.error(f"콘텐츠 변환 실패: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="콘텐츠 변환 중 오류가 발생했습니다")

@router.get("/workflow/summary")
async def get_workflow_summary():
    """현재 워크플로우의 토큰 사용량 및 비용 요약 조회"""
    try:
        summary = token_tracker.get_session_summary()
        
        # USD 계산
        cost_usd = token_tracker._calculate_cost_usd(
            summary['total_prompt_tokens'], 
            summary['total_response_tokens']
        )
        
        return {
            "total_operations": summary['operation_count'],
            "total_tokens": summary['total_tokens'],
            "prompt_tokens": summary['total_prompt_tokens'],
            "response_tokens": summary['total_response_tokens'],
            "estimated_cost_usd": round(cost_usd, 4),
            "estimated_cost_krw": round(summary['estimated_cost_krw'], 2),
            "session_duration": summary['session_duration'],
            "operations_breakdown": summary['operations']
        }
        
    except Exception as e:
        app_logger.error(f"워크플로우 요약 조회 실패: {e}")
        raise HTTPException(status_code=500, detail="워크플로우 요약 조회 중 오류가 발생했습니다")

@router.post("/workflow/complete")
async def complete_workflow(
    workflow_name: str = Query(..., description="워크플로우 이름"),
    reset_after: bool = Query(True, description="요약 후 토큰 추적기 리셋 여부")
):
    """전체 워크플로우 완료 시 토큰 사용량 총합 로깅"""
    try:
        # 전체 워크플로우 요약 로깅
        token_tracker.log_workflow_summary(f"Complete Workflow: {workflow_name}")
        
        # 토큰 추적기 리셋 (선택적)
        if reset_after:
            token_tracker.reset()
        
        return {"message": "워크플로우 토큰 사용량 요약이 로그에 기록되었습니다."}
    
    except Exception as e:
        app_logger.error(f"워크플로우 완료 처리 실패: {e}")
        raise HTTPException(status_code=500, detail="워크플로우 완료 처리 중 오류가 발생했습니다")

@router.delete("/{content_id}")
async def delete_content(content_id: str, db: Session = Depends(get_db)):
    """콘텐츠 삭제"""
    try:
        # 데이터베이스에서 콘텐츠 조회
        db_content = db.query(ContentModel).filter(ContentModel.id == content_id).first()
        
        if not db_content:
            raise HTTPException(status_code=404, detail="콘텐츠를 찾을 수 없습니다")
        
        # 콘텐츠 삭제
        db.delete(db_content)
        db.commit()
        
        # 캐시에서도 삭제
        cache_key = f"content_{hash(str({'topic': db_content.topic, 'category_id': db_content.category_id, 'content_type': db_content.content_type}))}"
        advanced_cache.delete(cache_key)
        
        app_logger.info(f"콘텐츠 삭제 완료: {content_id}")
        
        # 감사 로깅
        audit_logger.log_action(
            action="delete_content",
            entity_type="content",
            entity_id=content_id,
            changes={
                "topic": db_content.topic,
                "type": db_content.content_type
            }
        )
        
        return {"message": "콘텐츠가 성공적으로 삭제되었습니다", "id": content_id}
            
    except HTTPException:
        raise
    except Exception as e:
        app_logger.error(f"콘텐츠 삭제 실패: {e}", exc_info=True)
        db.rollback()
        raise HTTPException(status_code=500, detail="콘텐츠 삭제 중 오류가 발생했습니다")