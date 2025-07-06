"""
캐시 관리 API 엔드포인트
"""

from fastapi import APIRouter, HTTPException, Query, BackgroundTasks
from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field

from ..services.advanced_cache_manager import advanced_cache
from ..services.cache_strategies import (
    CacheWarmer, CacheInvalidator,
    content_cache_strategy, time_cache_strategy, user_cache_strategy
)
from ..services.performance_optimizer import performance_optimizer
from ..utils.logging_config import app_logger, audit_logger

router = APIRouter()

# Pydantic 모델
class CacheStatsResponse(BaseModel):
    """캐시 통계 응답"""
    total_entries: int
    total_size_mb: float
    hit_count: int
    miss_count: int
    eviction_count: int
    hit_rate: float
    compression_ratio: float
    avg_access_time_ms: float
    most_accessed_keys: List[Dict[str, Any]]

class CacheEntryResponse(BaseModel):
    """캐시 엔트리 응답"""
    key: str
    size_bytes: int
    created_at: str
    expires_at: Optional[str]
    access_count: int
    last_accessed: str
    compression: bool
    metadata: Optional[Dict[str, Any]]

class CacheClearRequest(BaseModel):
    """캐시 삭제 요청"""
    pattern: Optional[str] = Field(None, description="키 패턴")
    content_type: Optional[str] = Field(None, description="콘텐츠 타입")
    older_than_hours: Optional[int] = Field(None, ge=1, description="특정 시간 이전 항목")

class CacheWarmRequest(BaseModel):
    """캐시 워밍 요청"""
    topics: List[str] = Field(..., max_items=20, description="워밍할 주제 목록")
    content_types: List[str] = Field(default=["shorts", "article"], description="콘텐츠 타입")

class CacheConfigUpdate(BaseModel):
    """캐시 설정 업데이트"""
    max_size_mb: Optional[float] = Field(None, ge=100, le=10240, description="최대 크기 (MB)")
    default_ttl: Optional[int] = Field(None, ge=60, le=86400*30, description="기본 TTL (초)")
    enable_compression: Optional[bool] = Field(None, description="압축 활성화")

@router.get("/stats", response_model=CacheStatsResponse)
async def get_cache_stats():
    """캐시 통계 조회"""
    try:
        stats = advanced_cache.get_stats()
        
        # hit rate 계산
        total_requests = stats.hit_count + stats.miss_count
        hit_rate = (stats.hit_count / total_requests * 100) if total_requests > 0 else 0
        
        return CacheStatsResponse(
            total_entries=stats.total_entries,
            total_size_mb=stats.total_size_mb,
            hit_count=stats.hit_count,
            miss_count=stats.miss_count,
            eviction_count=stats.eviction_count,
            hit_rate=hit_rate,
            compression_ratio=stats.compression_ratio,
            avg_access_time_ms=stats.avg_access_time_ms,
            most_accessed_keys=[
                {"key": key, "access_count": count}
                for key, count in stats.most_accessed_keys
            ]
        )
        
    except Exception as e:
        app_logger.error(f"캐시 통계 조회 실패: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="캐시 통계 조회 중 오류가 발생했습니다")

@router.get("/entries")
async def list_cache_entries(
    page: int = Query(1, ge=1, description="페이지 번호"),
    size: int = Query(20, ge=1, le=100, description="페이지 크기"),
    pattern: Optional[str] = Query(None, description="키 패턴 필터")
):
    """캐시 엔트리 목록 조회"""
    try:
        all_entries = []
        
        for key, entry in advanced_cache.index.items():
            # 패턴 필터
            if pattern and pattern not in key:
                continue
                
            entry_response = CacheEntryResponse(
                key=key,
                size_bytes=entry.size_bytes,
                created_at=datetime.fromtimestamp(entry.created_at).isoformat(),
                expires_at=datetime.fromtimestamp(entry.expires_at).isoformat() if entry.expires_at else None,
                access_count=entry.access_count,
                last_accessed=datetime.fromtimestamp(entry.last_accessed).isoformat(),
                compression=entry.compression,
                metadata=entry.metadata
            )
            all_entries.append(entry_response)
        
        # 최근 접근 순으로 정렬
        all_entries.sort(key=lambda x: x.last_accessed, reverse=True)
        
        # 페이지네이션
        start = (page - 1) * size
        end = start + size
        paginated_entries = all_entries[start:end]
        
        return {
            "entries": paginated_entries,
            "total": len(all_entries),
            "page": page,
            "size": size,
            "pages": (len(all_entries) + size - 1) // size
        }
        
    except Exception as e:
        app_logger.error(f"캐시 엔트리 목록 조회 실패: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="캐시 엔트리 목록 조회 중 오류가 발생했습니다")

@router.get("/entry/{key}")
async def get_cache_entry(key: str):
    """특정 캐시 엔트리 조회"""
    try:
        if key not in advanced_cache.index:
            raise HTTPException(status_code=404, detail="캐시 엔트리를 찾을 수 없습니다")
            
        entry = advanced_cache.index[key]
        value = advanced_cache.get(key)
        
        return {
            "key": key,
            "value": value,  # 주의: 큰 데이터일 수 있음
            "metadata": {
                "size_bytes": entry.size_bytes,
                "created_at": datetime.fromtimestamp(entry.created_at).isoformat(),
                "expires_at": datetime.fromtimestamp(entry.expires_at).isoformat() if entry.expires_at else None,
                "access_count": entry.access_count,
                "last_accessed": datetime.fromtimestamp(entry.last_accessed).isoformat(),
                "compression": entry.compression,
                "custom_metadata": entry.metadata
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        app_logger.error(f"캐시 엔트리 조회 실패: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="캐시 엔트리 조회 중 오류가 발생했습니다")

@router.delete("/entry/{key}")
async def delete_cache_entry(key: str):
    """특정 캐시 엔트리 삭제"""
    try:
        if key not in advanced_cache.index:
            raise HTTPException(status_code=404, detail="캐시 엔트리를 찾을 수 없습니다")
            
        success = advanced_cache.delete(key)
        
        if success:
            audit_logger.log_action(
                action="delete_cache_entry",
                entity_type="cache",
                entity_id=key
            )
            
            return {
                "status": "success",
                "message": f"캐시 엔트리 '{key}'가 삭제되었습니다"
            }
        else:
            raise HTTPException(status_code=500, detail="캐시 엔트리 삭제 실패")
            
    except HTTPException:
        raise
    except Exception as e:
        app_logger.error(f"캐시 엔트리 삭제 실패: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="캐시 엔트리 삭제 중 오류가 발생했습니다")

@router.post("/clear")
async def clear_cache(request: CacheClearRequest):
    """캐시 일괄 삭제"""
    try:
        deleted_count = 0
        
        if request.pattern or request.content_type or request.older_than_hours:
            # 조건부 삭제
            invalidator = CacheInvalidator(advanced_cache)
            
            if request.pattern:
                deleted_count += await invalidator.invalidate_by_pattern(request.pattern)
                
            if request.content_type:
                deleted_count += await invalidator.invalidate_by_metadata(
                    {"content_type": request.content_type}
                )
                
            if request.older_than_hours:
                current_time = datetime.now().timestamp()
                cutoff_time = current_time - (request.older_than_hours * 3600)
                
                for key, entry in list(advanced_cache.index.items()):
                    if entry.created_at < cutoff_time:
                        if advanced_cache.delete(key):
                            deleted_count += 1
        else:
            # 전체 삭제
            deleted_count = advanced_cache.clear()
            
        audit_logger.log_action(
            action="clear_cache",
            entity_type="cache",
            entity_id="all",
            changes={
                "deleted_count": deleted_count,
                "conditions": request.dict(exclude_none=True)
            }
        )
        
        return {
            "status": "success",
            "deleted_count": deleted_count,
            "message": f"{deleted_count}개의 캐시 엔트리가 삭제되었습니다"
        }
        
    except Exception as e:
        app_logger.error(f"캐시 삭제 실패: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="캐시 삭제 중 오류가 발생했습니다")

@router.post("/warm")
async def warm_cache(
    request: CacheWarmRequest,
    background_tasks: BackgroundTasks
):
    """캐시 워밍 (미리 채우기)"""
    try:
        warmer = CacheWarmer(advanced_cache)
        
        # 백그라운드로 워밍 작업 실행
        background_tasks.add_task(
            warm_cache_background,
            warmer,
            request.topics,
            request.content_types
        )
        
        return {
            "status": "processing",
            "message": f"{len(request.topics)}개 주제에 대한 캐시 워밍이 시작되었습니다",
            "topics": request.topics,
            "content_types": request.content_types
        }
        
    except Exception as e:
        app_logger.error(f"캐시 워밍 시작 실패: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="캐시 워밍 시작 중 오류가 발생했습니다")

async def warm_cache_background(warmer: CacheWarmer, topics: List[str], content_types: List[str]):
    """백그라운드 캐시 워밍"""
    try:
        popular_topics = [
            {"topic": topic, "content_types": content_types}
            for topic in topics
        ]
        
        await warmer.warm_popular_content(popular_topics)
        
        app_logger.info(f"캐시 워밍 완료: {len(topics)}개 주제")
        
    except Exception as e:
        app_logger.error(f"캐시 워밍 실패: {e}", exc_info=True)

@router.post("/optimize")
@performance_optimizer.measure_performance("cache_optimization")
async def optimize_cache():
    """캐시 최적화"""
    try:
        stats_before = advanced_cache.get_stats()
        
        # 오래된 항목 정리
        advanced_cache._ensure_cache_size()
        
        # 리소스 정리
        cleanup_result = performance_optimizer.cleanup_resources()
        
        # 인덱스 재구성
        advanced_cache._save_index()
        
        stats_after = advanced_cache.get_stats()
        
        return {
            "status": "success",
            "before": {
                "entries": stats_before.total_entries,
                "size_mb": stats_before.total_size_mb
            },
            "after": {
                "entries": stats_after.total_entries,
                "size_mb": stats_after.total_size_mb
            },
            "cleanup": cleanup_result,
            "message": "캐시 최적화가 완료되었습니다"
        }
        
    except Exception as e:
        app_logger.error(f"캐시 최적화 실패: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="캐시 최적화 중 오류가 발생했습니다")

@router.put("/config")
async def update_cache_config(config: CacheConfigUpdate):
    """캐시 설정 업데이트"""
    try:
        updated_fields = []
        
        if config.max_size_mb is not None:
            advanced_cache.max_size_mb = config.max_size_mb
            updated_fields.append("max_size_mb")
            
        if config.default_ttl is not None:
            advanced_cache.default_ttl = config.default_ttl
            updated_fields.append("default_ttl")
            
        if config.enable_compression is not None:
            advanced_cache.enable_compression = config.enable_compression
            updated_fields.append("enable_compression")
            
        audit_logger.log_action(
            action="update_cache_config",
            entity_type="cache_config",
            entity_id="main",
            changes=config.dict(exclude_none=True)
        )
        
        return {
            "status": "success",
            "updated_fields": updated_fields,
            "current_config": {
                "max_size_mb": advanced_cache.max_size_mb,
                "default_ttl": advanced_cache.default_ttl,
                "enable_compression": advanced_cache.enable_compression
            }
        }
        
    except Exception as e:
        app_logger.error(f"캐시 설정 업데이트 실패: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="캐시 설정 업데이트 중 오류가 발생했습니다")

@router.get("/strategies")
async def get_cache_strategies():
    """캐싱 전략 정보 조회"""
    return {
        "strategies": {
            "content_type": {
                "description": "콘텐츠 타입별 캐싱 전략",
                "ttl_config": content_cache_strategy.ttl_config,
                "size_limits": content_cache_strategy.size_limits
            },
            "time_sensitive": {
                "description": "시간대별 캐싱 전략",
                "peak_hours": time_cache_strategy.peak_hours
            },
            "user_segment": {
                "description": "사용자 세그먼트별 캐싱 전략",
                "segment_ttls": user_cache_strategy.segment_ttls
            }
        }
    }