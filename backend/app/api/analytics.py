"""
분석 및 통계 API 엔드포인트
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel, Field
from collections import Counter, defaultdict

from ..services.advanced_cache_manager import advanced_cache
from ..services.performance_optimizer import performance_optimizer
from ..services.system_monitor import system_monitor
from ..utils.logging_config import app_logger

router = APIRouter()

# Pydantic 모델
class TimeRange(BaseModel):
    """시간 범위"""
    start_date: Optional[datetime] = Field(None, description="시작 날짜")
    end_date: Optional[datetime] = Field(None, description="종료 날짜")
    last_hours: Optional[int] = Field(None, ge=1, le=168, description="최근 N시간")

class ContentAnalytics(BaseModel):
    """콘텐츠 생성 분석"""
    total_generated: int
    by_type: Dict[str, int]
    by_quality: Dict[str, int]
    avg_quality_score: float
    avg_generation_time: float
    popular_topics: List[Dict[str, Any]]

class CategoryAnalytics(BaseModel):
    """카테고리 분석"""
    total_categories: int
    avg_practicality_score: float
    avg_interest_score: float
    by_practicality_range: Dict[str, int]
    most_popular: List[Dict[str, Any]]

class PaperAnalytics(BaseModel):
    """논문 분석"""
    total_papers: int
    quality_distribution: Dict[str, int]
    avg_impact_factor: float
    avg_citations: int
    by_type: Dict[str, int]
    by_year: Dict[int, int]

class SystemAnalytics(BaseModel):
    """시스템 사용 분석"""
    api_calls: Dict[str, int]
    cache_performance: Dict[str, Any]
    error_rate: float
    avg_response_time: float
    peak_usage_hours: List[int]

@router.get("/overview")
async def get_analytics_overview(
    time_range: TimeRange = None
):
    """전체 분석 개요"""
    try:
        # 시간 범위 설정
        if time_range and time_range.last_hours:
            start_time = datetime.now() - timedelta(hours=time_range.last_hours)
            end_time = datetime.now()
        elif time_range and time_range.start_date and time_range.end_date:
            start_time = time_range.start_date
            end_time = time_range.end_date
        else:
            # 기본값: 최근 24시간
            start_time = datetime.now() - timedelta(hours=24)
            end_time = datetime.now()
        
        # 각 부분 분석 수집
        content_analytics = await _get_content_analytics(start_time, end_time)
        category_analytics = await _get_category_analytics(start_time, end_time)
        paper_analytics = await _get_paper_analytics(start_time, end_time)
        system_analytics = await _get_system_analytics(start_time, end_time)
        
        return {
            "time_range": {
                "start": start_time.isoformat(),
                "end": end_time.isoformat()
            },
            "content": content_analytics,
            "categories": category_analytics,
            "papers": paper_analytics,
            "system": system_analytics,
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        app_logger.error(f"분석 개요 조회 실패: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="분석 개요 조회 중 오류가 발생했습니다")

@router.get("/content/metrics")
async def get_content_metrics(
    content_type: Optional[str] = Query(None, description="콘텐츠 타입 필터"),
    min_quality: Optional[float] = Query(None, ge=0, le=100, description="최소 품질 점수")
):
    """콘텐츠 생성 메트릭"""
    try:
        # 캐시에서 콘텐츠 관련 항목 수집
        content_entries = []
        
        for key, entry in advanced_cache.index.items():
            if entry.metadata and entry.metadata.get('content_type'):
                if content_type and entry.metadata['content_type'] != content_type:
                    continue
                if min_quality and entry.metadata.get('quality_score', 0) < min_quality:
                    continue
                    
                content_entries.append(entry)
        
        # 통계 계산
        total_count = len(content_entries)
        type_counts = Counter(e.metadata['content_type'] for e in content_entries)
        quality_scores = [e.metadata.get('quality_score', 0) for e in content_entries]
        
        # 품질 범위별 분포
        quality_ranges = {
            '0-60': 0,
            '60-70': 0,
            '70-80': 0,
            '80-90': 0,
            '90-100': 0
        }
        
        for score in quality_scores:
            if score < 60:
                quality_ranges['0-60'] += 1
            elif score < 70:
                quality_ranges['60-70'] += 1
            elif score < 80:
                quality_ranges['70-80'] += 1
            elif score < 90:
                quality_ranges['80-90'] += 1
            else:
                quality_ranges['90-100'] += 1
        
        # 인기 주제 (캐시 접근 횟수 기반)
        topic_access = defaultdict(int)
        for entry in content_entries:
            topic = entry.metadata.get('topic', 'Unknown')
            topic_access[topic] += entry.access_count
            
        popular_topics = sorted(
            topic_access.items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]
        
        return {
            "total_content": total_count,
            "by_type": dict(type_counts),
            "quality_distribution": quality_ranges,
            "avg_quality_score": sum(quality_scores) / len(quality_scores) if quality_scores else 0,
            "popular_topics": [
                {"topic": topic, "access_count": count}
                for topic, count in popular_topics
            ],
            "filters_applied": {
                "content_type": content_type,
                "min_quality": min_quality
            }
        }
        
    except Exception as e:
        app_logger.error(f"콘텐츠 메트릭 조회 실패: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="콘텐츠 메트릭 조회 중 오류가 발생했습니다")

@router.get("/categories/performance")
async def get_category_performance():
    """카테고리 성능 분석"""
    try:
        # 모의 데이터 (실제로는 DB에서 조회)
        categories_data = [
            {"name": "💪 홈트레이닝", "practicality": 9.0, "interest": 8.5, "content_count": 45},
            {"name": "🥗 건강식단", "practicality": 8.5, "interest": 9.0, "content_count": 38},
            {"name": "🔥 HIIT 운동", "practicality": 9.5, "interest": 9.8, "content_count": 52},
            {"name": "🧘 요가/명상", "practicality": 7.5, "interest": 8.0, "content_count": 25},
            {"name": "💊 보충제 가이드", "practicality": 8.0, "interest": 7.5, "content_count": 30}
        ]
        
        # 실용성별 분포
        practicality_ranges = {
            '6-7': 0,
            '7-8': 0,
            '8-9': 0,
            '9-10': 0
        }
        
        for cat in categories_data:
            score = cat['practicality']
            if score < 7:
                practicality_ranges['6-7'] += 1
            elif score < 8:
                practicality_ranges['7-8'] += 1
            elif score < 9:
                practicality_ranges['8-9'] += 1
            else:
                practicality_ranges['9-10'] += 1
        
        # 콘텐츠 생성량 기준 정렬
        top_categories = sorted(
            categories_data,
            key=lambda x: x['content_count'],
            reverse=True
        )[:5]
        
        return {
            "total_categories": len(categories_data),
            "avg_practicality_score": sum(c['practicality'] for c in categories_data) / len(categories_data),
            "avg_interest_score": sum(c['interest'] for c in categories_data) / len(categories_data),
            "practicality_distribution": practicality_ranges,
            "top_categories_by_content": top_categories,
            "correlation": {
                "practicality_vs_content": 0.82,  # 모의 상관계수
                "interest_vs_content": 0.75
            }
        }
        
    except Exception as e:
        app_logger.error(f"카테고리 성능 분석 실패: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="카테고리 성능 분석 중 오류가 발생했습니다")

@router.get("/papers/quality")
async def get_paper_quality_analytics():
    """논문 품질 분석"""
    try:
        # 모의 데이터
        papers_data = {
            "total_papers": 150,
            "quality_distribution": {
                "A+": 12,
                "A": 28,
                "B+": 45,
                "B": 35,
                "C": 20,
                "D": 10
            },
            "by_type": {
                "Systematic Review": 15,
                "Meta-analysis": 18,
                "RCT": 42,
                "Cohort Study": 30,
                "Cross-sectional": 25,
                "Case Report": 20
            },
            "impact_factor_ranges": {
                "0-2": 30,
                "2-5": 45,
                "5-10": 50,
                "10+": 25
            },
            "citation_ranges": {
                "0-10": 40,
                "10-50": 55,
                "50-100": 35,
                "100+": 20
            }
        }
        
        # 고품질 논문 비율
        high_quality = (
            papers_data["quality_distribution"]["A+"] +
            papers_data["quality_distribution"]["A"] +
            papers_data["quality_distribution"]["B+"]
        )
        high_quality_ratio = high_quality / papers_data["total_papers"] * 100
        
        return {
            **papers_data,
            "high_quality_ratio": high_quality_ratio,
            "avg_quality_score": 72.5,  # 모의 평균
            "trends": {
                "quality_improving": True,
                "avg_if_trend": "+2.3% monthly",
                "citation_trend": "+5.1% monthly"
            }
        }
        
    except Exception as e:
        app_logger.error(f"논문 품질 분석 실패: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="논문 품질 분석 중 오류가 발생했습니다")

@router.get("/system/usage")
async def get_system_usage():
    """시스템 사용 통계"""
    try:
        # 성능 리포트
        perf_report = performance_optimizer.get_performance_report()
        
        # 캐시 통계
        cache_stats = advanced_cache.get_stats()
        
        # API 호출 통계 (모의)
        api_calls = {
            "categories": 1250,
            "papers": 890,
            "contents": 2100,
            "cache": 450,
            "health": 3200
        }
        
        # 시간대별 사용량 (모의)
        hourly_usage = {}
        for hour in range(24):
            if 7 <= hour <= 10 or 18 <= hour <= 21:  # 피크 시간
                hourly_usage[hour] = 150 + (hour % 3) * 20
            else:
                hourly_usage[hour] = 50 + (hour % 5) * 10
        
        # 피크 시간 찾기
        peak_hours = sorted(
            hourly_usage.items(),
            key=lambda x: x[1],
            reverse=True
        )[:3]
        
        return {
            "api_calls": {
                "total": sum(api_calls.values()),
                "by_endpoint": api_calls,
                "avg_per_hour": sum(api_calls.values()) / 24
            },
            "performance": {
                "avg_response_time_ms": perf_report.get('performance', {}).get('avg_duration', 0),
                "success_rate": perf_report.get('success_rate', 0),
                "error_rate": 100 - perf_report.get('success_rate', 100)
            },
            "cache": {
                "hit_rate": (cache_stats.hit_count / (cache_stats.hit_count + cache_stats.miss_count) * 100) 
                           if (cache_stats.hit_count + cache_stats.miss_count) > 0 else 0,
                "total_entries": cache_stats.total_entries,
                "size_mb": cache_stats.total_size_mb
            },
            "usage_patterns": {
                "hourly_distribution": hourly_usage,
                "peak_hours": [hour for hour, _ in peak_hours],
                "busiest_day": "Wednesday",  # 모의
                "avg_daily_requests": sum(api_calls.values()) / 7
            }
        }
        
    except Exception as e:
        app_logger.error(f"시스템 사용 통계 조회 실패: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="시스템 사용 통계 조회 중 오류가 발생했습니다")

@router.get("/trends")
async def get_analytics_trends(
    metric: str = Query(..., description="분석할 메트릭 (content_quality, category_popularity, paper_quality, api_usage)"),
    period: str = Query("week", regex="^(day|week|month)$", description="기간")
):
    """트렌드 분석"""
    try:
        # 기간별 데이터 포인트 수
        data_points = {
            "day": 24,     # 시간별
            "week": 7,     # 일별
            "month": 30    # 일별
        }
        
        points = data_points[period]
        
        # 모의 트렌드 데이터 생성
        if metric == "content_quality":
            trend_data = [
                {"time": i, "value": 70 + (i % 5) * 2 + (i / points) * 5}
                for i in range(points)
            ]
        elif metric == "category_popularity":
            trend_data = [
                {"time": i, "value": 100 + (i % 7) * 10 - (i % 3) * 5}
                for i in range(points)
            ]
        elif metric == "paper_quality":
            trend_data = [
                {"time": i, "value": 65 + (i % 4) * 3 + (i / points) * 3}
                for i in range(points)
            ]
        elif metric == "api_usage":
            trend_data = [
                {"time": i, "value": 200 + (i % 6) * 30 + (i % 2) * 50}
                for i in range(points)
            ]
        else:
            raise HTTPException(status_code=400, detail="지원하지 않는 메트릭입니다")
        
        # 트렌드 계산
        values = [d["value"] for d in trend_data]
        avg_value = sum(values) / len(values)
        trend_direction = "increasing" if values[-1] > values[0] else "decreasing"
        change_percent = ((values[-1] - values[0]) / values[0]) * 100
        
        return {
            "metric": metric,
            "period": period,
            "data": trend_data,
            "summary": {
                "current_value": values[-1],
                "avg_value": avg_value,
                "min_value": min(values),
                "max_value": max(values),
                "trend": trend_direction,
                "change_percent": change_percent
            },
            "generated_at": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        app_logger.error(f"트렌드 분석 실패: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="트렌드 분석 중 오류가 발생했습니다")

@router.post("/export")
async def export_analytics(
    format: str = Query("json", regex="^(json|csv)$", description="내보내기 형식"),
    include_raw_data: bool = Query(False, description="원시 데이터 포함 여부")
):
    """분석 데이터 내보내기"""
    try:
        # 전체 분석 데이터 수집
        analytics_data = {
            "export_info": {
                "timestamp": datetime.now().isoformat(),
                "format": format,
                "include_raw_data": include_raw_data
            },
            "overview": await get_analytics_overview(),
            "content_metrics": await get_content_metrics(),
            "category_performance": await get_category_performance(),
            "paper_quality": await get_paper_quality_analytics(),
            "system_usage": await get_system_usage()
        }
        
        # 파일 저장
        export_dir = "./exports/analytics"
        os.makedirs(export_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if format == "json":
            import json
            export_path = f"{export_dir}/analytics_{timestamp}.json"
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(analytics_data, f, indent=2, ensure_ascii=False)
        else:  # csv
            import csv
            export_path = f"{export_dir}/analytics_{timestamp}.csv"
            # CSV는 플랫 구조만 지원하므로 요약 정보만 내보내기
            with open(export_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(["Metric", "Value"])
                writer.writerow(["Export Time", analytics_data["export_info"]["timestamp"]])
                writer.writerow(["Total Content", analytics_data["content_metrics"]["total_content"]])
                writer.writerow(["Avg Quality Score", analytics_data["content_metrics"]["avg_quality_score"]])
                writer.writerow(["Total Categories", analytics_data["category_performance"]["total_categories"]])
                writer.writerow(["Cache Hit Rate", analytics_data["system_usage"]["cache"]["hit_rate"]])
        
        return {
            "status": "success",
            "export_path": export_path,
            "format": format,
            "file_size_kb": os.path.getsize(export_path) / 1024,
            "message": "분석 데이터가 성공적으로 내보내졌습니다"
        }
        
    except Exception as e:
        app_logger.error(f"분석 데이터 내보내기 실패: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="분석 데이터 내보내기 중 오류가 발생했습니다")

# 내부 헬퍼 함수들
async def _get_content_analytics(start_time: datetime, end_time: datetime) -> Dict[str, Any]:
    """콘텐츠 분석 데이터 수집"""
    # 실제로는 DB에서 시간 범위에 맞는 데이터 조회
    return {
        "total_generated": 125,
        "by_type": {"shorts": 45, "article": 50, "report": 30},
        "by_quality": {"excellent": 35, "good": 60, "average": 30},
        "avg_quality_score": 78.5,
        "avg_generation_time": 2.3,
        "popular_topics": [
            {"topic": "HIIT 운동", "count": 15},
            {"topic": "단백질 섭취", "count": 12},
            {"topic": "홈트레이닝", "count": 10}
        ]
    }

async def _get_category_analytics(start_time: datetime, end_time: datetime) -> Dict[str, Any]:
    """카테고리 분석 데이터 수집"""
    return {
        "total_categories": 45,
        "avg_practicality_score": 8.2,
        "avg_interest_score": 8.5,
        "by_practicality_range": {"6-7": 5, "7-8": 10, "8-9": 20, "9-10": 10},
        "most_popular": [
            {"name": "홈트레이닝", "usage_count": 250},
            {"name": "다이어트", "usage_count": 180}
        ]
    }

async def _get_paper_analytics(start_time: datetime, end_time: datetime) -> Dict[str, Any]:
    """논문 분석 데이터 수집"""
    return {
        "total_papers": 89,
        "quality_distribution": {"A+": 10, "A": 20, "B+": 30, "B": 20, "C": 9},
        "avg_impact_factor": 6.8,
        "avg_citations": 45,
        "by_type": {"Systematic Review": 10, "RCT": 25, "Meta-analysis": 15, "Other": 39},
        "by_year": {2024: 25, 2023: 35, 2022: 20, 2021: 9}
    }

async def _get_system_analytics(start_time: datetime, end_time: datetime) -> Dict[str, Any]:
    """시스템 분석 데이터 수집"""
    return {
        "api_calls": {"total": 5800, "by_endpoint": {"contents": 2100, "categories": 1500, "papers": 1200, "other": 1000}},
        "cache_performance": {"hit_rate": 85.5, "total_size_mb": 450},
        "error_rate": 0.5,
        "avg_response_time": 125,
        "peak_usage_hours": [9, 14, 20]
    }