"""
캐싱 전략 - 다양한 캐싱 패턴과 전략 구현
"""

from typing import Dict, List, Any, Optional, Callable, Union
import hashlib
import json
from datetime import datetime, timedelta
from abc import ABC, abstractmethod
import asyncio
from functools import wraps

from .advanced_cache_manager import AdvancedCacheManager

class CacheStrategy(ABC):
    """캐시 전략 기본 클래스"""
    
    @abstractmethod
    def should_cache(self, key: str, value: Any, metadata: Dict[str, Any]) -> bool:
        """캐싱 여부 결정"""
        pass
    
    @abstractmethod
    def get_ttl(self, key: str, value: Any, metadata: Dict[str, Any]) -> int:
        """TTL 결정"""
        pass
    
    @abstractmethod
    def get_cache_key(self, *args, **kwargs) -> str:
        """캐시 키 생성"""
        pass

class ContentTypeCacheStrategy(CacheStrategy):
    """콘텐츠 타입별 캐싱 전략"""
    
    def __init__(self):
        self.ttl_config = {
            'shorts': 3600 * 24,      # 24시간
            'article': 3600 * 24 * 3,  # 3일
            'report': 3600 * 24 * 7,   # 7일
            'category': 3600 * 12,     # 12시간
            'paper_quality': 3600 * 24 * 30  # 30일
        }
        
        self.size_limits = {
            'shorts': 1024 * 100,      # 100KB
            'article': 1024 * 500,     # 500KB
            'report': 1024 * 1024 * 2  # 2MB
        }
        
    def should_cache(self, key: str, value: Any, metadata: Dict[str, Any]) -> bool:
        """캐싱 여부 결정"""
        content_type = metadata.get('content_type', 'unknown')
        
        # 콘텐츠 타입이 설정에 없으면 캐싱하지 않음
        if content_type not in self.ttl_config:
            return False
            
        # 크기 제한 확인
        if content_type in self.size_limits:
            value_size = len(str(value).encode('utf-8'))
            if value_size > self.size_limits[content_type]:
                return False
                
        # 품질 점수가 낮으면 캐싱하지 않음
        quality_score = metadata.get('quality_score', 100)
        if quality_score < 60:
            return False
            
        return True
    
    def get_ttl(self, key: str, value: Any, metadata: Dict[str, Any]) -> int:
        """TTL 결정"""
        content_type = metadata.get('content_type', 'unknown')
        base_ttl = self.ttl_config.get(content_type, 3600)
        
        # 품질 점수에 따른 TTL 조정
        quality_score = metadata.get('quality_score', 70)
        if quality_score >= 90:
            return int(base_ttl * 1.5)  # 50% 증가
        elif quality_score < 70:
            return int(base_ttl * 0.5)  # 50% 감소
            
        return base_ttl
    
    def get_cache_key(self, *args, **kwargs) -> str:
        """캐시 키 생성"""
        # 콘텐츠 타입, 주제, 타겟 청중, 논문 ID 등을 조합
        content_type = kwargs.get('content_type', 'unknown')
        topic = kwargs.get('topic', '')
        target_audience = kwargs.get('target_audience', 'general')
        
        # 논문 ID들을 정렬하여 일관된 키 생성
        papers = kwargs.get('papers', [])
        paper_ids = sorted([str(p.id) if hasattr(p, 'id') else str(p) for p in papers])
        
        key_parts = [
            content_type,
            topic,
            target_audience,
            ','.join(paper_ids)
        ]
        
        key_string = '|'.join(key_parts)
        return hashlib.md5(key_string.encode()).hexdigest()

class TimeSensitiveCacheStrategy(CacheStrategy):
    """시간대별 캐싱 전략"""
    
    def __init__(self):
        self.peak_hours = [(7, 10), (18, 21)]  # 오전 7-10시, 저녁 6-9시
        
    def should_cache(self, key: str, value: Any, metadata: Dict[str, Any]) -> bool:
        """피크 시간대에만 적극적으로 캐싱"""
        current_hour = datetime.now().hour
        
        # 피크 시간대 확인
        in_peak_time = any(
            start <= current_hour < end 
            for start, end in self.peak_hours
        )
        
        # 피크 시간대가 아니면 중요한 콘텐츠만 캐싱
        if not in_peak_time:
            importance = metadata.get('importance', 'normal')
            return importance in ['high', 'critical']
            
        return True
    
    def get_ttl(self, key: str, value: Any, metadata: Dict[str, Any]) -> int:
        """시간대에 따른 TTL 조정"""
        current_hour = datetime.now().hour
        
        # 피크 시간대면 짧은 TTL
        in_peak_time = any(
            start <= current_hour < end 
            for start, end in self.peak_hours
        )
        
        if in_peak_time:
            return 1800  # 30분
        else:
            return 7200  # 2시간
    
    def get_cache_key(self, *args, **kwargs) -> str:
        """시간대를 포함한 캐시 키"""
        base_key = str(args) + str(sorted(kwargs.items()))
        time_slot = datetime.now().hour // 6  # 6시간 단위
        
        return f"{base_key}_{time_slot}"

class UserSegmentCacheStrategy(CacheStrategy):
    """사용자 세그먼트별 캐싱 전략"""
    
    def __init__(self):
        self.segment_ttls = {
            'premium': 3600 * 24 * 7,   # 7일
            'regular': 3600 * 24,       # 1일
            'guest': 3600 * 6          # 6시간
        }
        
    def should_cache(self, key: str, value: Any, metadata: Dict[str, Any]) -> bool:
        """사용자 세그먼트별 캐싱 결정"""
        user_segment = metadata.get('user_segment', 'guest')
        
        # 게스트는 인기 콘텐츠만 캐싱
        if user_segment == 'guest':
            popularity = metadata.get('popularity_score', 0)
            return popularity > 70
            
        return True
    
    def get_ttl(self, key: str, value: Any, metadata: Dict[str, Any]) -> int:
        """사용자 세그먼트별 TTL"""
        user_segment = metadata.get('user_segment', 'guest')
        return self.segment_ttls.get(user_segment, 3600)
    
    def get_cache_key(self, *args, **kwargs) -> str:
        """사용자 세그먼트를 포함한 캐시 키"""
        user_segment = kwargs.get('user_segment', 'guest')
        base_key = str(args) + str(sorted(kwargs.items()))
        
        return f"{user_segment}_{base_key}"

class CacheDecorator:
    """캐싱 데코레이터"""
    
    def __init__(self, 
                 cache_manager: AdvancedCacheManager,
                 strategy: CacheStrategy):
        self.cache_manager = cache_manager
        self.strategy = strategy
        
    def cached(self, 
               content_type: str = None,
               importance: str = 'normal',
               user_segment_getter: Callable = None):
        """캐싱 데코레이터"""
        
        def decorator(func):
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                # 메타데이터 수집
                metadata = {
                    'content_type': content_type or kwargs.get('content_type', 'unknown'),
                    'importance': importance,
                    'function': func.__name__,
                    'timestamp': datetime.now().isoformat()
                }
                
                # 사용자 세그먼트 추가
                if user_segment_getter:
                    metadata['user_segment'] = user_segment_getter(*args, **kwargs)
                    
                # 캐시 키 생성
                cache_key = self.strategy.get_cache_key(*args, **kwargs)
                
                # 캐시 확인
                cached_value = await self.cache_manager.aget(cache_key)
                if cached_value is not None:
                    return cached_value
                    
                # 함수 실행
                result = await func(*args, **kwargs)
                
                # 품질 점수 추가 (있는 경우)
                if hasattr(result, 'quality_score'):
                    metadata['quality_score'] = result.quality_score
                    
                # 캐싱 여부 결정
                if self.strategy.should_cache(cache_key, result, metadata):
                    ttl = self.strategy.get_ttl(cache_key, result, metadata)
                    await self.cache_manager.aset(cache_key, result, ttl, metadata)
                    
                return result
                
            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                # 동기 버전
                metadata = {
                    'content_type': content_type or kwargs.get('content_type', 'unknown'),
                    'importance': importance,
                    'function': func.__name__,
                    'timestamp': datetime.now().isoformat()
                }
                
                if user_segment_getter:
                    metadata['user_segment'] = user_segment_getter(*args, **kwargs)
                    
                cache_key = self.strategy.get_cache_key(*args, **kwargs)
                
                cached_value = self.cache_manager.get(cache_key)
                if cached_value is not None:
                    return cached_value
                    
                result = func(*args, **kwargs)
                
                if hasattr(result, 'quality_score'):
                    metadata['quality_score'] = result.quality_score
                    
                if self.strategy.should_cache(cache_key, result, metadata):
                    ttl = self.strategy.get_ttl(cache_key, result, metadata)
                    self.cache_manager.set(cache_key, result, ttl, metadata)
                    
                return result
                
            if asyncio.iscoroutinefunction(func):
                return async_wrapper
            else:
                return sync_wrapper
                
        return decorator

class CacheWarmer:
    """캐시 워밍 - 미리 캐시 채우기"""
    
    def __init__(self, cache_manager: AdvancedCacheManager):
        self.cache_manager = cache_manager
        self.warming_tasks = []
        
    async def warm_popular_content(self, popular_topics: List[Dict[str, Any]]):
        """인기 콘텐츠 미리 캐싱"""
        tasks = []
        
        for topic_info in popular_topics:
            topic = topic_info['topic']
            content_types = topic_info.get('content_types', ['shorts', 'article'])
            
            for content_type in content_types:
                task = asyncio.create_task(
                    self._generate_and_cache(topic, content_type)
                )
                tasks.append(task)
                
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        success_count = sum(1 for r in results if not isinstance(r, Exception))
        print(f"✅ 캐시 워밍 완료: {success_count}/{len(tasks)} 성공")
        
    async def _generate_and_cache(self, topic: str, content_type: str):
        """콘텐츠 생성 및 캐싱"""
        # 실제로는 콘텐츠 생성기를 호출
        # 여기서는 시뮬레이션
        cache_key = f"warmed_{content_type}_{topic}"
        value = f"Pre-generated {content_type} for {topic}"
        
        metadata = {
            'content_type': content_type,
            'warmed': True,
            'quality_score': 85
        }
        
        return await self.cache_manager.aset(
            cache_key, value, ttl=3600*24, metadata=metadata
        )

class CacheInvalidator:
    """캐시 무효화 관리"""
    
    def __init__(self, cache_manager: AdvancedCacheManager):
        self.cache_manager = cache_manager
        self.invalidation_rules = []
        
    def add_rule(self, rule: Dict[str, Any]):
        """무효화 규칙 추가"""
        self.invalidation_rules.append(rule)
        
    async def invalidate_by_pattern(self, pattern: str):
        """패턴에 맞는 캐시 무효화"""
        invalidated = 0
        
        for key in list(self.cache_manager.index.keys()):
            if pattern in key:
                if self.cache_manager.delete(key):
                    invalidated += 1
                    
        print(f"🗑️ 패턴 '{pattern}'에 맞는 {invalidated}개 캐시 무효화")
        return invalidated
        
    async def invalidate_by_metadata(self, conditions: Dict[str, Any]):
        """메타데이터 조건에 맞는 캐시 무효화"""
        invalidated = 0
        
        for key, entry in list(self.cache_manager.index.items()):
            if entry.metadata:
                match = all(
                    entry.metadata.get(k) == v 
                    for k, v in conditions.items()
                )
                if match and self.cache_manager.delete(key):
                    invalidated += 1
                    
        print(f"🗑️ 조건에 맞는 {invalidated}개 캐시 무효화")
        return invalidated

# 전역 인스턴스
content_cache_strategy = ContentTypeCacheStrategy()
time_cache_strategy = TimeSensitiveCacheStrategy()
user_cache_strategy = UserSegmentCacheStrategy()