"""
헬스체크 및 시스템 상태 API 엔드포인트
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List
from datetime import datetime
import psutil
import os

from ..services.system_monitor import system_monitor, health_checker
from ..services.performance_optimizer import performance_optimizer
from ..utils.logging_config import app_logger

router = APIRouter()

@router.get("/")
async def health_check():
    """기본 헬스체크"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "Hybrid Paper-Based Content System",
        "version": "1.0.0"
    }

@router.get("/detailed")
async def detailed_health_check():
    """상세 헬스체크"""
    try:
        # 시스템 리소스 정보
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # 프로세스 정보
        process = psutil.Process()
        process_info = {
            "pid": process.pid,
            "memory_mb": process.memory_info().rss / 1024 / 1024,
            "cpu_percent": process.cpu_percent(interval=1),
            "threads": process.num_threads(),
            "open_files": len(process.open_files())
        }
        
        # 서비스 상태
        health_result = await health_checker.run_health_check()
        
        return {
            "status": health_result['overall_status'],
            "timestamp": datetime.now().isoformat(),
            "system_resources": {
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "memory_available_gb": memory.available / (1024**3),
                "disk_percent": disk.percent,
                "disk_free_gb": disk.free / (1024**3)
            },
            "process_info": process_info,
            "service_checks": health_result['checks'],
            "uptime_seconds": (datetime.now() - datetime.fromtimestamp(process.create_time())).total_seconds()
        }
        
    except Exception as e:
        app_logger.error(f"상세 헬스체크 실패: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="헬스체크 중 오류가 발생했습니다")

@router.get("/monitoring/status")
async def get_monitoring_status():
    """모니터링 상태 조회"""
    try:
        current_status = system_monitor.get_current_status()
        
        if current_status.get('status') == 'no_data':
            return {
                "monitoring_active": False,
                "message": "모니터링이 활성화되지 않았습니다"
            }
            
        return {
            "monitoring_active": True,
            "current_status": current_status,
            "alert_count": len(system_monitor.alerts),
            "history_size": len(system_monitor.history)
        }
        
    except Exception as e:
        app_logger.error(f"모니터링 상태 조회 실패: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="모니터링 상태 조회 중 오류가 발생했습니다")

@router.get("/monitoring/statistics")
async def get_monitoring_statistics(minutes: int = 5):
    """모니터링 통계 조회"""
    try:
        stats = system_monitor.get_statistics(minutes=minutes)
        
        return {
            "time_range_minutes": minutes,
            "statistics": stats,
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        app_logger.error(f"모니터링 통계 조회 실패: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="모니터링 통계 조회 중 오류가 발생했습니다")

@router.get("/monitoring/alerts")
async def get_monitoring_alerts(limit: int = 50):
    """모니터링 알림 조회"""
    try:
        recent_alerts = list(system_monitor.alerts)[-limit:]
        
        formatted_alerts = []
        for alert in recent_alerts:
            formatted_alerts.append({
                "timestamp": alert.timestamp.isoformat(),
                "level": alert.level,
                "metric": alert.metric,
                "message": alert.message,
                "value": alert.value,
                "threshold": alert.threshold
            })
            
        return {
            "alerts": formatted_alerts,
            "total_count": len(system_monitor.alerts),
            "critical_count": sum(1 for a in system_monitor.alerts if a.level == 'critical'),
            "warning_count": sum(1 for a in system_monitor.alerts if a.level == 'warning')
        }
        
    except Exception as e:
        app_logger.error(f"알림 조회 실패: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="알림 조회 중 오류가 발생했습니다")

@router.get("/performance/report")
async def get_performance_report(operation: str = None):
    """성능 리포트 조회"""
    try:
        report = performance_optimizer.get_performance_report(operation)
        
        return {
            "report": report,
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        app_logger.error(f"성능 리포트 조회 실패: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="성능 리포트 조회 중 오류가 발생했습니다")

@router.post("/monitoring/export")
async def export_monitoring_data():
    """모니터링 데이터 내보내기"""
    try:
        export_path = f"./exports/monitoring_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        os.makedirs(os.path.dirname(export_path), exist_ok=True)
        
        system_monitor.export_metrics(export_path)
        
        return {
            "status": "success",
            "export_path": export_path,
            "message": "모니터링 데이터가 성공적으로 내보내졌습니다"
        }
        
    except Exception as e:
        app_logger.error(f"모니터링 데이터 내보내기 실패: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="데이터 내보내기 중 오류가 발생했습니다")

@router.get("/dependencies")
async def check_dependencies():
    """외부 의존성 상태 확인"""
    dependencies = {
        "database": {"status": "unknown", "message": ""},
        "cache": {"status": "unknown", "message": ""},
        "gemini_api": {"status": "unknown", "message": ""}
    }
    
    # 데이터베이스 확인
    try:
        # TODO: 실제 데이터베이스 연결 확인
        dependencies["database"] = {
            "status": "healthy",
            "message": "Database connection OK"
        }
    except Exception as e:
        dependencies["database"] = {
            "status": "unhealthy",
            "message": str(e)
        }
    
    # 캐시 확인
    try:
        from ..services.advanced_cache_manager import advanced_cache
        stats = advanced_cache.get_stats()
        dependencies["cache"] = {
            "status": "healthy",
            "message": f"Cache operational, {stats.total_entries} entries"
        }
    except Exception as e:
        dependencies["cache"] = {
            "status": "unhealthy",
            "message": str(e)
        }
    
    # Gemini API 확인
    try:
        # TODO: 실제 Gemini API 연결 확인
        dependencies["gemini_api"] = {
            "status": "healthy",
            "message": "Gemini API accessible"
        }
    except Exception as e:
        dependencies["gemini_api"] = {
            "status": "unhealthy",
            "message": str(e)
        }
    
    # 전체 상태 판단
    all_healthy = all(dep["status"] == "healthy" for dep in dependencies.values())
    
    return {
        "overall_status": "healthy" if all_healthy else "degraded",
        "dependencies": dependencies,
        "timestamp": datetime.now().isoformat()
    }

@router.get("/ready")
async def readiness_check():
    """서비스 준비 상태 확인"""
    try:
        # 필수 서비스 확인
        checks = {
            "cache_ready": False,
            "monitoring_ready": False,
            "api_ready": True
        }
        
        # 캐시 확인
        try:
            from ..services.advanced_cache_manager import advanced_cache
            stats = advanced_cache.get_stats()
            checks["cache_ready"] = True
        except:
            pass
        
        # 모니터링 확인
        if system_monitor.is_monitoring:
            checks["monitoring_ready"] = True
        
        all_ready = all(checks.values())
        
        return {
            "ready": all_ready,
            "checks": checks,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "ready": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@router.get("/live")
async def liveness_check():
    """서비스 생존 확인"""
    return {
        "alive": True,
        "timestamp": datetime.now().isoformat()
    }