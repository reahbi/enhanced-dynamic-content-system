"""
성능 최적화 모듈 - 시스템 전반의 성능 개선
"""

from typing import Dict, List, Any, Optional, Callable
import asyncio
import time
from functools import wraps, lru_cache
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import threading
import psutil
import gc

@dataclass
class PerformanceMetrics:
    """성능 메트릭"""
    operation: str
    start_time: float
    end_time: float
    duration: float
    memory_before: float
    memory_after: float
    memory_delta: float
    cpu_percent: float
    success: bool
    error: Optional[str] = None

class PerformanceOptimizer:
    """성능 최적화기"""
    
    def __init__(self):
        self.metrics_history = []
        self.thread_pool = ThreadPoolExecutor(max_workers=4)
        self.process_pool = ProcessPoolExecutor(max_workers=2)
        self._lock = threading.Lock()
        
    def measure_performance(self, operation_name: str):
        """성능 측정 데코레이터"""
        def decorator(func):
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                return await self._measure_async(operation_name, func, *args, **kwargs)
                
            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                return self._measure_sync(operation_name, func, *args, **kwargs)
                
            if asyncio.iscoroutinefunction(func):
                return async_wrapper
            else:
                return sync_wrapper
                
        return decorator
    
    async def _measure_async(self, operation_name: str, func: Callable, *args, **kwargs):
        """비동기 함수 성능 측정"""
        process = psutil.Process()
        
        # 시작 메트릭
        start_time = time.time()
        memory_before = process.memory_info().rss / 1024 / 1024  # MB
        cpu_before = process.cpu_percent(interval=0.1)
        
        try:
            # 함수 실행
            result = await func(*args, **kwargs)
            success = True
            error = None
        except Exception as e:
            result = None
            success = False
            error = str(e)
            
        # 종료 메트릭
        end_time = time.time()
        memory_after = process.memory_info().rss / 1024 / 1024  # MB
        cpu_percent = process.cpu_percent(interval=0.1)
        
        # 메트릭 기록
        metrics = PerformanceMetrics(
            operation=operation_name,
            start_time=start_time,
            end_time=end_time,
            duration=end_time - start_time,
            memory_before=memory_before,
            memory_after=memory_after,
            memory_delta=memory_after - memory_before,
            cpu_percent=cpu_percent,
            success=success,
            error=error
        )
        
        with self._lock:
            self.metrics_history.append(metrics)
            
        if not success:
            raise Exception(error)
            
        return result
    
    def _measure_sync(self, operation_name: str, func: Callable, *args, **kwargs):
        """동기 함수 성능 측정"""
        process = psutil.Process()
        
        # 시작 메트릭
        start_time = time.time()
        memory_before = process.memory_info().rss / 1024 / 1024  # MB
        
        try:
            # 함수 실행
            result = func(*args, **kwargs)
            success = True
            error = None
        except Exception as e:
            result = None
            success = False
            error = str(e)
            
        # 종료 메트릭
        end_time = time.time()
        memory_after = process.memory_info().rss / 1024 / 1024  # MB
        cpu_percent = process.cpu_percent(interval=0.1)
        
        # 메트릭 기록
        metrics = PerformanceMetrics(
            operation=operation_name,
            start_time=start_time,
            end_time=end_time,
            duration=end_time - start_time,
            memory_before=memory_before,
            memory_after=memory_after,
            memory_delta=memory_after - memory_before,
            cpu_percent=cpu_percent,
            success=success,
            error=error
        )
        
        with self._lock:
            self.metrics_history.append(metrics)
            
        if not success:
            raise Exception(error)
            
        return result
    
    def get_performance_report(self, operation_name: Optional[str] = None) -> Dict[str, Any]:
        """성능 리포트 생성"""
        filtered_metrics = self.metrics_history
        if operation_name:
            filtered_metrics = [m for m in self.metrics_history if m.operation == operation_name]
            
        if not filtered_metrics:
            return {'error': 'No metrics found'}
            
        # 성공/실패 통계
        successful = [m for m in filtered_metrics if m.success]
        failed = [m for m in filtered_metrics if not m.success]
        
        # 성능 통계
        durations = [m.duration for m in successful]
        memory_deltas = [m.memory_delta for m in successful]
        cpu_percents = [m.cpu_percent for m in successful]
        
        report = {
            'operation': operation_name or 'all',
            'total_calls': len(filtered_metrics),
            'successful_calls': len(successful),
            'failed_calls': len(failed),
            'success_rate': len(successful) / len(filtered_metrics) * 100,
            'performance': {
                'avg_duration': sum(durations) / len(durations) if durations else 0,
                'min_duration': min(durations) if durations else 0,
                'max_duration': max(durations) if durations else 0,
                'avg_memory_delta': sum(memory_deltas) / len(memory_deltas) if memory_deltas else 0,
                'avg_cpu_percent': sum(cpu_percents) / len(cpu_percents) if cpu_percents else 0
            },
            'errors': [{'operation': m.operation, 'error': m.error} for m in failed]
        }
        
        return report
    
    async def optimize_parallel_operations(self, operations: List[Callable]) -> List[Any]:
        """병렬 작업 최적화"""
        tasks = []
        for operation in operations:
            if asyncio.iscoroutinefunction(operation):
                tasks.append(operation())
            else:
                # 동기 함수를 비동기로 실행
                tasks.append(asyncio.get_event_loop().run_in_executor(
                    self.thread_pool, operation
                ))
                
        return await asyncio.gather(*tasks)
    
    def cleanup_resources(self):
        """리소스 정리"""
        # 가비지 컬렉션 강제 실행
        gc.collect()
        
        # 오래된 메트릭 정리 (최근 1000개만 유지)
        if len(self.metrics_history) > 1000:
            with self._lock:
                self.metrics_history = self.metrics_history[-1000:]
                
        return {
            'gc_collected': gc.get_count(),
            'metrics_cleaned': len(self.metrics_history)
        }


class CachingOptimizer:
    """캐싱 최적화"""
    
    def __init__(self, max_size: int = 128):
        self.max_size = max_size
        
    def cached(self, ttl: int = 3600):
        """TTL 기반 캐싱 데코레이터"""
        def decorator(func):
            cache = {}
            cache_times = {}
            
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                # 캐시 키 생성
                cache_key = self._make_cache_key(args, kwargs)
                
                # 캐시 확인
                if cache_key in cache:
                    if time.time() - cache_times[cache_key] < ttl:
                        return cache[cache_key]
                    else:
                        # 만료된 캐시 삭제
                        del cache[cache_key]
                        del cache_times[cache_key]
                        
                # 캐시 미스 - 함수 실행
                result = await func(*args, **kwargs)
                
                # 캐시 저장
                if len(cache) >= self.max_size:
                    # LRU 방식으로 가장 오래된 항목 제거
                    oldest_key = min(cache_times, key=cache_times.get)
                    del cache[oldest_key]
                    del cache_times[oldest_key]
                    
                cache[cache_key] = result
                cache_times[cache_key] = time.time()
                
                return result
                
            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                # 동기 함수용 캐싱
                cache_key = self._make_cache_key(args, kwargs)
                
                if cache_key in cache:
                    if time.time() - cache_times[cache_key] < ttl:
                        return cache[cache_key]
                    else:
                        del cache[cache_key]
                        del cache_times[cache_key]
                        
                result = func(*args, **kwargs)
                
                if len(cache) >= self.max_size:
                    oldest_key = min(cache_times, key=cache_times.get)
                    del cache[oldest_key]
                    del cache_times[oldest_key]
                    
                cache[cache_key] = result
                cache_times[cache_key] = time.time()
                
                return result
                
            if asyncio.iscoroutinefunction(func):
                return async_wrapper
            else:
                return sync_wrapper
                
        return decorator
    
    def _make_cache_key(self, args, kwargs):
        """캐시 키 생성"""
        # 간단한 키 생성 (실제로는 더 복잡한 로직 필요)
        return str(args) + str(sorted(kwargs.items()))


class BatchProcessor:
    """배치 처리 최적화"""
    
    def __init__(self, batch_size: int = 10, timeout: float = 1.0):
        self.batch_size = batch_size
        self.timeout = timeout
        self.queue = asyncio.Queue()
        self.processing = False
        
    async def add_item(self, item: Any):
        """아이템 추가"""
        await self.queue.put(item)
        
        if not self.processing:
            asyncio.create_task(self._process_batch())
            
    async def _process_batch(self):
        """배치 처리"""
        self.processing = True
        batch = []
        
        try:
            while True:
                try:
                    # 타임아웃이나 배치 크기까지 아이템 수집
                    while len(batch) < self.batch_size:
                        item = await asyncio.wait_for(
                            self.queue.get(), 
                            timeout=self.timeout
                        )
                        batch.append(item)
                        
                except asyncio.TimeoutError:
                    # 타임아웃 발생 - 현재 배치 처리
                    if batch:
                        await self._process_items(batch)
                        batch = []
                    else:
                        # 더 이상 처리할 아이템이 없음
                        break
                        
                # 배치가 가득 참 - 처리
                if len(batch) >= self.batch_size:
                    await self._process_items(batch)
                    batch = []
                    
        finally:
            self.processing = False
            
    async def _process_items(self, items: List[Any]):
        """실제 배치 처리 로직"""
        # 여기에 실제 배치 처리 로직 구현
        print(f"Processing batch of {len(items)} items")
        # 예: 데이터베이스 일괄 삽입, API 일괄 호출 등


class MemoryOptimizer:
    """메모리 최적화"""
    
    @staticmethod
    def get_memory_usage() -> Dict[str, float]:
        """현재 메모리 사용량"""
        process = psutil.Process()
        memory_info = process.memory_info()
        
        return {
            'rss_mb': memory_info.rss / 1024 / 1024,
            'vms_mb': memory_info.vms / 1024 / 1024,
            'percent': process.memory_percent(),
            'available_mb': psutil.virtual_memory().available / 1024 / 1024
        }
    
    @staticmethod
    def optimize_memory():
        """메모리 최적화 실행"""
        before = MemoryOptimizer.get_memory_usage()
        
        # 가비지 컬렉션
        gc.collect()
        
        # 메모리 압축 (Python 3.8+)
        if hasattr(gc, 'freeze'):
            gc.freeze()
            gc.collect()
            gc.unfreeze()
            
        after = MemoryOptimizer.get_memory_usage()
        
        return {
            'before': before,
            'after': after,
            'saved_mb': before['rss_mb'] - after['rss_mb']
        }


# 전역 성능 최적화 인스턴스
performance_optimizer = PerformanceOptimizer()
caching_optimizer = CachingOptimizer()
memory_optimizer = MemoryOptimizer()