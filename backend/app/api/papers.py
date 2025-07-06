"""
논문 관련 API 엔드포인트
"""

from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum

from ..services.paper_quality_evaluator import PaperQualityEvaluator, QualityGrade
from ..services.advanced_cache_manager import advanced_cache
from ..services.performance_optimizer import performance_optimizer
from ..utils.logging_config import app_logger, audit_logger
from ..utils.bug_fixes import bug_fix_utils, data_validator

router = APIRouter()

# Enums
class PaperType(str, Enum):
    SYSTEMATIC_REVIEW = "Systematic Review"
    META_ANALYSIS = "Meta-analysis"
    RCT = "RCT"
    COHORT_STUDY = "Cohort Study"
    CASE_CONTROL = "Case-control Study"
    CROSS_SECTIONAL = "Cross-sectional Study"
    CASE_REPORT = "Case Report"
    ORIGINAL_RESEARCH = "Original Research"

class SortField(str, Enum):
    QUALITY_SCORE = "quality_score"
    IMPACT_FACTOR = "impact_factor"
    CITATIONS = "citations"
    YEAR = "year"
    TITLE = "title"

# Pydantic 모델
class PaperSearchRequest(BaseModel):
    """논문 검색 요청"""
    query: str = Field(..., min_length=1, max_length=200, description="검색 쿼리")
    paper_types: Optional[List[PaperType]] = Field(None, description="논문 유형 필터")
    min_impact_factor: Optional[float] = Field(None, ge=0, description="최소 Impact Factor")
    min_year: Optional[int] = Field(None, ge=1900, le=2030, description="최소 출판년도")
    max_results: int = Field(default=20, ge=1, le=100, description="최대 결과 수")

class PaperQualityInfo(BaseModel):
    """논문 품질 정보"""
    quality_score: float
    grade: str
    details: Dict[str, float]
    strengths: List[str]
    weaknesses: List[str]

class PaperResponse(BaseModel):
    """논문 응답"""
    id: str
    title: str
    authors: str
    journal: str
    year: int
    doi: Optional[str]
    abstract: Optional[str]
    paper_type: str
    impact_factor: float
    citations: int
    quality_info: PaperQualityInfo
    created_at: str

class PaperListResponse(BaseModel):
    """논문 목록 응답"""
    papers: List[PaperResponse]
    total: int
    query: str
    filters_applied: Dict[str, Any]

class PaperEvaluationRequest(BaseModel):
    """논문 평가 요청"""
    title: str = Field(..., description="논문 제목")
    authors: str = Field(..., description="저자")
    journal: str = Field(..., description="저널명")
    year: int = Field(..., ge=1900, le=2030, description="출판년도")
    paper_type: PaperType = Field(..., description="논문 유형")
    impact_factor: float = Field(..., ge=0, description="Impact Factor")
    citations: int = Field(default=0, ge=0, description="인용 수")
    doi: Optional[str] = Field(None, description="DOI")

class PaperDiscoveryRequest(BaseModel):
    """논문 기반 서브카테고리 발견 요청"""
    category: str = Field(..., min_length=1, max_length=200, description="카테고리")
    topic: str = Field(..., min_length=1, max_length=200, description="세부 주제")

class SubcategoryResponse(BaseModel):
    """서브카테고리 응답"""
    name: str
    description: str
    papers: List[Dict[str, Any]]
    expected_effect: str
    quality_score: float
    quality_grade: str

# 의존성
async def get_paper_evaluator():
    """논문 평가기 인스턴스"""
    return PaperQualityEvaluator()

# 모의 논문 데이터베이스
MOCK_PAPERS = [
    {
        "id": "paper_001",
        "title": "Effects of High-Intensity Interval Training on Cardiovascular Function",
        "authors": "Smith J, Johnson K, Williams R",
        "journal": "Sports Medicine",
        "year": 2024,
        "doi": "10.1234/sportmed.2024.001",
        "abstract": "This systematic review examines the effects of HIIT on cardiovascular health...",
        "paper_type": "Systematic Review",
        "impact_factor": 11.2,
        "citations": 45
    },
    {
        "id": "paper_002",
        "title": "Protein Timing and Muscle Recovery: A Meta-Analysis",
        "authors": "Lee S, Park H, Kim J",
        "journal": "Journal of Sports Science",
        "year": 2023,
        "doi": "10.5678/jss.2023.112",
        "abstract": "We conducted a meta-analysis to determine optimal protein timing...",
        "paper_type": "Meta-analysis",
        "impact_factor": 7.8,
        "citations": 89
    },
    {
        "id": "paper_003",
        "title": "Core Training Methods: A Randomized Controlled Trial",
        "authors": "Wilson R, Davis M",
        "journal": "Exercise Science Review",
        "year": 2023,
        "doi": "10.9012/esr.2023.045",
        "abstract": "This RCT compared different core training methods...",
        "paper_type": "RCT",
        "impact_factor": 5.8,
        "citations": 67
    }
]

@router.post("/search", response_model=PaperListResponse)
@performance_optimizer.measure_performance("paper_search")
async def search_papers(
    request: PaperSearchRequest,
    evaluator: PaperQualityEvaluator = Depends(get_paper_evaluator)
):
    """논문 검색"""
    try:
        # 입력 검증
        query = bug_fix_utils.safe_string_processing(request.query)
        if not query:
            raise HTTPException(status_code=400, detail="유효한 검색어를 입력해주세요")
        
        # 캐시 확인
        cache_key = f"paper_search_{hash(str(request.dict()))}"
        cached_result = advanced_cache.get(cache_key)
        
        if cached_result:
            app_logger.info(f"캐시에서 논문 검색 결과 반환: {query}")
            return cached_result
        
        # 논문 검색 (모의 구현)
        filtered_papers = []
        
        for paper_data in MOCK_PAPERS:
            # 검색어 매칭
            if query.lower() not in paper_data['title'].lower() and \
               query.lower() not in paper_data['abstract'].lower():
                continue
            
            # 필터 적용
            if request.paper_types and paper_data['paper_type'] not in [pt.value for pt in request.paper_types]:
                continue
            if request.min_impact_factor and paper_data['impact_factor'] < request.min_impact_factor:
                continue
            if request.min_year and paper_data['year'] < request.min_year:
                continue
            
            # 논문 평가
            class MockPaper:
                def __init__(self, **kwargs):
                    for k, v in kwargs.items():
                        setattr(self, k, v)
            
            paper = MockPaper(**paper_data)
            quality_info = evaluator.evaluate_paper(paper)
            
            # 응답 생성
            paper_response = PaperResponse(
                id=paper_data['id'],
                title=paper_data['title'],
                authors=paper_data['authors'],
                journal=paper_data['journal'],
                year=paper_data['year'],
                doi=paper_data.get('doi'),
                abstract=paper_data.get('abstract'),
                paper_type=paper_data['paper_type'],
                impact_factor=paper_data['impact_factor'],
                citations=paper_data['citations'],
                quality_info=PaperQualityInfo(
                    quality_score=quality_info.quality_score,
                    grade=quality_info.grade.value,
                    details=quality_info.details,
                    strengths=quality_info.strengths,
                    weaknesses=quality_info.weaknesses
                ),
                created_at=datetime.now().isoformat()
            )
            
            filtered_papers.append(paper_response)
            
            if len(filtered_papers) >= request.max_results:
                break
        
        response = PaperListResponse(
            papers=filtered_papers,
            total=len(filtered_papers),
            query=query,
            filters_applied={
                'paper_types': [pt.value for pt in request.paper_types] if request.paper_types else None,
                'min_impact_factor': request.min_impact_factor,
                'min_year': request.min_year
            }
        )
        
        # 캐시 저장
        advanced_cache.set(cache_key, response, ttl=3600*6)  # 6시간
        
        # 감사 로깅
        audit_logger.log_action(
            action="search_papers",
            entity_type="paper",
            entity_id=query,
            changes={"result_count": len(filtered_papers)}
        )
        
        return response
        
    except Exception as e:
        app_logger.error(f"논문 검색 실패: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="논문 검색 중 오류가 발생했습니다")

@router.get("/{paper_id}", response_model=PaperResponse)
async def get_paper(
    paper_id: str,
    evaluator: PaperQualityEvaluator = Depends(get_paper_evaluator)
):
    """논문 상세 조회"""
    try:
        # 논문 찾기
        paper_data = None
        for p in MOCK_PAPERS:
            if p['id'] == paper_id:
                paper_data = p
                break
        
        if not paper_data:
            raise HTTPException(status_code=404, detail="논문을 찾을 수 없습니다")
        
        # 논문 평가
        class MockPaper:
            def __init__(self, **kwargs):
                for k, v in kwargs.items():
                    setattr(self, k, v)
        
        paper = MockPaper(**paper_data)
        quality_info = evaluator.evaluate_paper(paper)
        
        return PaperResponse(
            id=paper_data['id'],
            title=paper_data['title'],
            authors=paper_data['authors'],
            journal=paper_data['journal'],
            year=paper_data['year'],
            doi=paper_data.get('doi'),
            abstract=paper_data.get('abstract'),
            paper_type=paper_data['paper_type'],
            impact_factor=paper_data['impact_factor'],
            citations=paper_data['citations'],
            quality_info=PaperQualityInfo(
                quality_score=quality_info.quality_score,
                grade=quality_info.grade.value,
                details=quality_info.details,
                strengths=quality_info.strengths,
                weaknesses=quality_info.weaknesses
            ),
            created_at=datetime.now().isoformat()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        app_logger.error(f"논문 조회 실패: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="논문 조회 중 오류가 발생했습니다")

@router.post("/evaluate", response_model=PaperQualityInfo)
async def evaluate_paper(
    request: PaperEvaluationRequest,
    evaluator: PaperQualityEvaluator = Depends(get_paper_evaluator)
):
    """논문 품질 평가"""
    try:
        # MockPaper 객체 생성
        class MockPaper:
            def __init__(self, **kwargs):
                for k, v in kwargs.items():
                    setattr(self, k, v)
        
        paper = MockPaper(**request.dict())
        
        # 논문 검증
        if not data_validator.validate_paper(paper):
            raise HTTPException(status_code=400, detail="유효하지 않은 논문 정보입니다")
        
        # 품질 평가
        quality_info = evaluator.evaluate_paper(paper)
        
        return PaperQualityInfo(
            quality_score=quality_info.quality_score,
            grade=quality_info.grade.value,
            details=quality_info.details,
            strengths=quality_info.strengths,
            weaknesses=quality_info.weaknesses
        )
        
    except HTTPException:
        raise
    except Exception as e:
        app_logger.error(f"논문 평가 실패: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="논문 평가 중 오류가 발생했습니다")

@router.get("/", response_model=PaperListResponse)
async def list_papers(
    page: int = Query(1, ge=1, description="페이지 번호"),
    size: int = Query(10, ge=1, le=50, description="페이지 크기"),
    sort_by: SortField = Query(SortField.QUALITY_SCORE, description="정렬 필드"),
    order: str = Query("desc", regex="^(asc|desc)$", description="정렬 순서"),
    min_grade: Optional[str] = Query(None, regex="^(A\\+|A|B\\+|B|C|D)$", description="최소 등급")
):
    """논문 목록 조회"""
    try:
        evaluator = PaperQualityEvaluator()
        
        # 모든 논문 평가
        evaluated_papers = []
        for paper_data in MOCK_PAPERS:
            class MockPaper:
                def __init__(self, **kwargs):
                    for k, v in kwargs.items():
                        setattr(self, k, v)
            
            paper = MockPaper(**paper_data)
            quality_info = evaluator.evaluate_paper(paper)
            
            # 등급 필터
            if min_grade:
                grade_order = ['D', 'C', 'B', 'B+', 'A', 'A+']
                if grade_order.index(quality_info.grade.value) < grade_order.index(min_grade):
                    continue
            
            paper_response = PaperResponse(
                id=paper_data['id'],
                title=paper_data['title'],
                authors=paper_data['authors'],
                journal=paper_data['journal'],
                year=paper_data['year'],
                doi=paper_data.get('doi'),
                abstract=paper_data.get('abstract'),
                paper_type=paper_data['paper_type'],
                impact_factor=paper_data['impact_factor'],
                citations=paper_data['citations'],
                quality_info=PaperQualityInfo(
                    quality_score=quality_info.quality_score,
                    grade=quality_info.grade.value,
                    details=quality_info.details,
                    strengths=quality_info.strengths,
                    weaknesses=quality_info.weaknesses
                ),
                created_at=datetime.now().isoformat()
            )
            
            evaluated_papers.append(paper_response)
        
        # 정렬
        if sort_by == SortField.QUALITY_SCORE:
            evaluated_papers.sort(key=lambda x: x.quality_info.quality_score, reverse=(order == "desc"))
        elif sort_by == SortField.IMPACT_FACTOR:
            evaluated_papers.sort(key=lambda x: x.impact_factor, reverse=(order == "desc"))
        elif sort_by == SortField.CITATIONS:
            evaluated_papers.sort(key=lambda x: x.citations, reverse=(order == "desc"))
        elif sort_by == SortField.YEAR:
            evaluated_papers.sort(key=lambda x: x.year, reverse=(order == "desc"))
        elif sort_by == SortField.TITLE:
            evaluated_papers.sort(key=lambda x: x.title, reverse=(order == "desc"))
        
        # 페이지네이션
        start = (page - 1) * size
        end = start + size
        paginated_papers = evaluated_papers[start:end]
        
        return PaperListResponse(
            papers=paginated_papers,
            total=len(evaluated_papers),
            query="all",
            filters_applied={'min_grade': min_grade}
        )
        
    except Exception as e:
        app_logger.error(f"논문 목록 조회 실패: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="논문 목록 조회 중 오류가 발생했습니다")

@router.get("/category/{category_id}/papers", response_model=PaperListResponse)
async def get_papers_by_category(
    category_id: str,
    limit: int = Query(10, ge=1, le=50, description="최대 결과 수")
):
    """카테고리별 관련 논문 조회"""
    try:
        # TODO: 실제 카테고리-논문 매핑 구현
        # 현재는 카테고리와 관련 있을 것 같은 논문 반환
        
        evaluator = PaperQualityEvaluator()
        related_papers = []
        
        # 샘플: 처음 몇 개 논문 반환
        for paper_data in MOCK_PAPERS[:limit]:
            class MockPaper:
                def __init__(self, **kwargs):
                    for k, v in kwargs.items():
                        setattr(self, k, v)
            
            paper = MockPaper(**paper_data)
            quality_info = evaluator.evaluate_paper(paper)
            
            paper_response = PaperResponse(
                id=paper_data['id'],
                title=paper_data['title'],
                authors=paper_data['authors'],
                journal=paper_data['journal'],
                year=paper_data['year'],
                doi=paper_data.get('doi'),
                abstract=paper_data.get('abstract'),
                paper_type=paper_data['paper_type'],
                impact_factor=paper_data['impact_factor'],
                citations=paper_data['citations'],
                quality_info=PaperQualityInfo(
                    quality_score=quality_info.quality_score,
                    grade=quality_info.grade.value,
                    details=quality_info.details,
                    strengths=quality_info.strengths,
                    weaknesses=quality_info.weaknesses
                ),
                created_at=datetime.now().isoformat()
            )
            
            related_papers.append(paper_response)
        
        return PaperListResponse(
            papers=related_papers,
            total=len(related_papers),
            query=f"category:{category_id}",
            filters_applied={'category_id': category_id}
        )
        
    except Exception as e:
        app_logger.error(f"카테고리별 논문 조회 실패: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="카테고리별 논문 조회 중 오류가 발생했습니다")

@router.get("/quality/distribution")
async def get_quality_distribution():
    """논문 품질 등급 분포"""
    try:
        evaluator = PaperQualityEvaluator()
        
        distribution = {
            'A+': 0, 'A': 0, 'B+': 0, 'B': 0, 'C': 0, 'D': 0
        }
        
        for paper_data in MOCK_PAPERS:
            class MockPaper:
                def __init__(self, **kwargs):
                    for k, v in kwargs.items():
                        setattr(self, k, v)
            
            paper = MockPaper(**paper_data)
            quality_info = evaluator.evaluate_paper(paper)
            distribution[quality_info.grade.value] += 1
        
        total = sum(distribution.values())
        
        return {
            "distribution": distribution,
            "percentages": {
                grade: (count / total * 100) if total > 0 else 0
                for grade, count in distribution.items()
            },
            "total_papers": total,
            "high_quality_count": distribution['A+'] + distribution['A'] + distribution['B+'],
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        app_logger.error(f"품질 분포 조회 실패: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="품질 분포 조회 중 오류가 발생했습니다")

@router.post("/discover", response_model=SubcategoryResponse)
@performance_optimizer.measure_performance("paper_discovery")
async def discover_papers(
    request: PaperDiscoveryRequest,
    evaluator: PaperQualityEvaluator = Depends(get_paper_evaluator)
):
    """카테고리와 주제를 기반으로 논문 검색 및 서브카테고리 생성"""
    try:
        # 입력 검증
        category = bug_fix_utils.safe_string_processing(request.category)
        topic = bug_fix_utils.safe_string_processing(request.topic)
        
        if not category or not topic:
            raise HTTPException(status_code=400, detail="유효한 카테고리와 주제를 입력해주세요")
        
        # 캐시 확인
        cache_key = f"paper_discover_{hash(category + topic)}"
        cached_result = advanced_cache.get(cache_key)
        
        if cached_result:
            app_logger.info(f"캐시에서 논문 발견 결과 반환: {category}/{topic}")
            return cached_result
        
        # Gemini 클라이언트 초기화
        from ..services.gemini_client import GeminiClient
        gemini_client = GeminiClient()
        
        # 논문 검색 및 서브카테고리 생성 (최대 15회 시도)
        max_attempts = 15
        for attempt in range(max_attempts):
            app_logger.info(f"논문 검색 시도 {attempt + 1}/{max_attempts}: {category}/{topic}")
            
            # 시도할 때마다 약간 다른 주제로 변형
            if attempt > 0:
                topic_variation = f"{topic} (변형 {attempt})"
            else:
                topic_variation = topic
            
            subcategory_result = gemini_client.discover_papers_for_topic(category, topic_variation)
            
            if subcategory_result:
                # 결과를 응답 형식으로 변환
                response = SubcategoryResponse(
                    name=subcategory_result.name,
                    description=subcategory_result.description,
                    papers=[{
                        "title": p.title,
                        "authors": p.authors,
                        "journal": p.journal,
                        "publication_year": p.year,
                        "doi": p.doi,
                        "impact_factor": p.impact_factor,
                        "citations": p.citations,
                        "paper_type": p.paper_type
                    } for p in subcategory_result.papers],
                    expected_effect=subcategory_result.expected_effect,
                    quality_score=subcategory_result.quality_score,
                    quality_grade=subcategory_result.quality_grade
                )
                
                # 캐시 저장 (12시간)
                advanced_cache.set(cache_key, response, ttl=3600*12)
                
                # 감사 로깅
                audit_logger.log_action(
                    action="discover_papers",
                    entity_type="subcategory",
                    entity_id=subcategory_result.name,
                    changes={
                        "category": category,
                        "topic": topic,
                        "papers_found": len(subcategory_result.papers),
                        "attempts": attempt + 1
                    }
                )
                
                return response
        
        # 모든 시도가 실패한 경우
        app_logger.warning(f"논문 발견 실패 (모든 시도 소진): {category}/{topic}")
        raise HTTPException(
            status_code=404, 
            detail="해당 주제에 대한 적절한 논문을 찾을 수 없습니다. 다른 주제를 시도해보세요."
        )
        
    except HTTPException:
        raise
    except Exception as e:
        app_logger.error(f"논문 발견 실패: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="논문 발견 중 오류가 발생했습니다")