"""
고급 캐시 매니저 - 향상된 파일 기반 캐싱 시스템
"""

import os
import json
import pickle
import hashlib
import time
import asyncio
import aiofiles
from typing import Any, Optional, Dict, List, Tuple, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import threading
from pathlib import Path
import shutil
import gzip

@dataclass
class CacheEntry:
    """캐시 엔트리"""
    key: str
    value: Any
    created_at: float
    expires_at: Optional[float]
    access_count: int = 0
    last_accessed: float = None
    size_bytes: int = 0
    compression: bool = False
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.last_accessed is None:
            self.last_accessed = self.created_at

@dataclass
class CacheStats:
    """캐시 통계"""
    total_entries: int
    total_size_mb: float
    hit_count: int
    miss_count: int
    eviction_count: int
    compression_ratio: float
    avg_access_time_ms: float
    most_accessed_keys: List[Tuple[str, int]]

class AdvancedCacheManager:
    """고급 캐시 매니저"""
    
    def __init__(self, 
                 cache_dir: str = "./cache/advanced",
                 max_size_mb: float = 1024,  # 1GB
                 default_ttl: int = 3600,
                 enable_compression: bool = True,
                 enable_async: bool = True):
        
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        self.max_size_mb = max_size_mb
        self.default_ttl = default_ttl
        self.enable_compression = enable_compression
        self.enable_async = enable_async
        
        # 인덱스 파일
        self.index_file = self.cache_dir / "cache_index.json"
        self.stats_file = self.cache_dir / "cache_stats.json"
        
        # 메모리 인덱스
        self.index: Dict[str, CacheEntry] = {}
        self.stats = {
            'hit_count': 0,
            'miss_count': 0,
            'eviction_count': 0,
            'total_access_time': 0,
            'access_count': 0
        }
        
        # 스레드 안전성
        self._lock = threading.Lock()
        self._async_lock = asyncio.Lock()
        
        # 초기화
        self._load_index()
        self._start_maintenance_tasks()
        
    def _load_index(self):
        """인덱스 로드"""
        if self.index_file.exists():
            try:
                with open(self.index_file, 'r') as f:
                    index_data = json.load(f)
                    
                for key, entry_data in index_data.items():
                    self.index[key] = CacheEntry(**entry_data)
                    
            except Exception as e:
                print(f"인덱스 로드 실패: {e}")
                
    def _save_index(self):
        """인덱스 저장"""
        try:
            index_data = {}
            for key, entry in self.index.items():
                entry_dict = asdict(entry)
                # 직렬화 불가능한 값 제거
                entry_dict['value'] = None
                index_data[key] = entry_dict
                
            with open(self.index_file, 'w') as f:
                json.dump(index_data, f)
                
        except Exception as e:
            print(f"인덱스 저장 실패: {e}")
            
    def _get_cache_path(self, key: str) -> Path:
        """캐시 파일 경로 생성"""
        # 키를 해시하여 파일명 생성
        key_hash = hashlib.md5(key.encode()).hexdigest()
        
        # 디렉토리 분산 (첫 2글자로 서브디렉토리)
        subdir = self.cache_dir / key_hash[:2]
        subdir.mkdir(exist_ok=True)
        
        return subdir / f"{key_hash}.cache"
        
    def _serialize(self, value: Any, compress: bool = False) -> bytes:
        """값 직렬화"""
        data = pickle.dumps(value)
        
        if compress and self.enable_compression:
            data = gzip.compress(data)
            
        return data
        
    def _deserialize(self, data: bytes, compressed: bool = False) -> Any:
        """값 역직렬화"""
        if compressed and self.enable_compression:
            data = gzip.decompress(data)
            
        return pickle.loads(data)
        
    def set(self, key: str, value: Any, ttl: Optional[int] = None, 
            metadata: Optional[Dict[str, Any]] = None) -> bool:
        """캐시 설정"""
        start_time = time.time()
        
        try:
            with self._lock:
                # TTL 설정
                if ttl is None:
                    ttl = self.default_ttl
                    
                expires_at = time.time() + ttl if ttl > 0 else None
                
                # 압축 여부 결정 (큰 데이터만 압축)
                data = self._serialize(value)
                compress = len(data) > 1024 * 10  # 10KB 이상
                
                if compress:
                    compressed_data = self._serialize(value, compress=True)
                    compression_ratio = len(compressed_data) / len(data)
                    
                    # 압축 효율이 좋을 때만 사용
                    if compression_ratio < 0.9:
                        data = compressed_data
                    else:
                        compress = False
                        
                # 캐시 엔트리 생성
                entry = CacheEntry(
                    key=key,
                    value=None,  # 파일에 저장
                    created_at=time.time(),
                    expires_at=expires_at,
                    size_bytes=len(data),
                    compression=compress,
                    metadata=metadata
                )
                
                # 크기 확인 및 정리
                self._ensure_cache_size()
                
                # 파일 저장
                cache_path = self._get_cache_path(key)
                with open(cache_path, 'wb') as f:
                    f.write(data)
                    
                # 인덱스 업데이트
                self.index[key] = entry
                self._save_index()
                
                # 통계 업데이트
                access_time = (time.time() - start_time) * 1000
                self._update_stats('set', access_time)
                
                return True
                
        except Exception as e:
            print(f"캐시 설정 실패: {e}")
            return False
            
    def get(self, key: str, default: Any = None) -> Any:
        """캐시 조회"""
        start_time = time.time()
        
        try:
            with self._lock:
                # 인덱스 확인
                if key not in self.index:
                    self.stats['miss_count'] += 1
                    return default
                    
                entry = self.index[key]
                
                # 만료 확인
                if entry.expires_at and time.time() > entry.expires_at:
                    self._remove_entry(key)
                    self.stats['miss_count'] += 1
                    return default
                    
                # 파일 읽기
                cache_path = self._get_cache_path(key)
                if not cache_path.exists():
                    self._remove_entry(key)
                    self.stats['miss_count'] += 1
                    return default
                    
                with open(cache_path, 'rb') as f:
                    data = f.read()
                    
                # 역직렬화
                value = self._deserialize(data, compressed=entry.compression)
                
                # 접근 정보 업데이트
                entry.access_count += 1
                entry.last_accessed = time.time()
                
                # 통계 업데이트
                self.stats['hit_count'] += 1
                access_time = (time.time() - start_time) * 1000
                self._update_stats('get', access_time)
                
                return value
                
        except Exception as e:
            print(f"캐시 조회 실패: {e}")
            self.stats['miss_count'] += 1
            return default
            
    async def aset(self, key: str, value: Any, ttl: Optional[int] = None,
                   metadata: Optional[Dict[str, Any]] = None) -> bool:
        """비동기 캐시 설정"""
        if not self.enable_async:
            return self.set(key, value, ttl, metadata)
            
        start_time = time.time()
        
        try:
            async with self._async_lock:
                # TTL 설정
                if ttl is None:
                    ttl = self.default_ttl
                    
                expires_at = time.time() + ttl if ttl > 0 else None
                
                # 직렬화 (CPU 집약적이므로 스레드 풀에서 실행)
                loop = asyncio.get_event_loop()
                data = await loop.run_in_executor(None, self._serialize, value)
                
                compress = len(data) > 1024 * 10
                if compress:
                    compressed_data = await loop.run_in_executor(
                        None, self._serialize, value, True
                    )
                    if len(compressed_data) < len(data) * 0.9:
                        data = compressed_data
                    else:
                        compress = False
                        
                # 캐시 엔트리 생성
                entry = CacheEntry(
                    key=key,
                    value=None,
                    created_at=time.time(),
                    expires_at=expires_at,
                    size_bytes=len(data),
                    compression=compress,
                    metadata=metadata
                )
                
                # 크기 확인
                await loop.run_in_executor(None, self._ensure_cache_size)
                
                # 파일 저장
                cache_path = self._get_cache_path(key)
                async with aiofiles.open(cache_path, 'wb') as f:
                    await f.write(data)
                    
                # 인덱스 업데이트
                self.index[key] = entry
                await loop.run_in_executor(None, self._save_index)
                
                # 통계 업데이트
                access_time = (time.time() - start_time) * 1000
                self._update_stats('aset', access_time)
                
                return True
                
        except Exception as e:
            print(f"비동기 캐시 설정 실패: {e}")
            return False
            
    async def aget(self, key: str, default: Any = None) -> Any:
        """비동기 캐시 조회"""
        if not self.enable_async:
            return self.get(key, default)
            
        start_time = time.time()
        
        try:
            async with self._async_lock:
                # 인덱스 확인
                if key not in self.index:
                    self.stats['miss_count'] += 1
                    return default
                    
                entry = self.index[key]
                
                # 만료 확인
                if entry.expires_at and time.time() > entry.expires_at:
                    await self._aremove_entry(key)
                    self.stats['miss_count'] += 1
                    return default
                    
                # 파일 읽기
                cache_path = self._get_cache_path(key)
                if not cache_path.exists():
                    await self._aremove_entry(key)
                    self.stats['miss_count'] += 1
                    return default
                    
                async with aiofiles.open(cache_path, 'rb') as f:
                    data = await f.read()
                    
                # 역직렬화
                loop = asyncio.get_event_loop()
                value = await loop.run_in_executor(
                    None, self._deserialize, data, entry.compression
                )
                
                # 접근 정보 업데이트
                entry.access_count += 1
                entry.last_accessed = time.time()
                
                # 통계 업데이트
                self.stats['hit_count'] += 1
                access_time = (time.time() - start_time) * 1000
                self._update_stats('aget', access_time)
                
                return value
                
        except Exception as e:
            print(f"비동기 캐시 조회 실패: {e}")
            self.stats['miss_count'] += 1
            return default
            
    def delete(self, key: str) -> bool:
        """캐시 삭제"""
        with self._lock:
            return self._remove_entry(key)
            
    def clear(self) -> int:
        """전체 캐시 삭제"""
        with self._lock:
            count = len(self.index)
            
            # 캐시 디렉토리 삭제 및 재생성
            shutil.rmtree(self.cache_dir, ignore_errors=True)
            self.cache_dir.mkdir(parents=True, exist_ok=True)
            
            # 인덱스 초기화
            self.index.clear()
            self._save_index()
            
            return count
            
    def _remove_entry(self, key: str) -> bool:
        """캐시 엔트리 제거"""
        if key not in self.index:
            return False
            
        try:
            # 파일 삭제
            cache_path = self._get_cache_path(key)
            if cache_path.exists():
                cache_path.unlink()
                
            # 인덱스에서 제거
            del self.index[key]
            
            return True
            
        except Exception as e:
            print(f"캐시 엔트리 제거 실패: {e}")
            return False
            
    async def _aremove_entry(self, key: str) -> bool:
        """비동기 캐시 엔트리 제거"""
        if key not in self.index:
            return False
            
        try:
            cache_path = self._get_cache_path(key)
            if cache_path.exists():
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(None, cache_path.unlink)
                
            del self.index[key]
            return True
            
        except Exception as e:
            print(f"비동기 캐시 엔트리 제거 실패: {e}")
            return False
            
    def _ensure_cache_size(self):
        """캐시 크기 관리"""
        total_size = sum(entry.size_bytes for entry in self.index.values())
        max_size_bytes = self.max_size_mb * 1024 * 1024
        
        if total_size <= max_size_bytes:
            return
            
        # LRU 방식으로 정리
        entries = sorted(
            self.index.items(),
            key=lambda x: x[1].last_accessed
        )
        
        while total_size > max_size_bytes * 0.9:  # 90%까지 정리
            if not entries:
                break
                
            key, entry = entries.pop(0)
            if self._remove_entry(key):
                total_size -= entry.size_bytes
                self.stats['eviction_count'] += 1
                
    def _update_stats(self, operation: str, access_time_ms: float):
        """통계 업데이트"""
        self.stats['total_access_time'] += access_time_ms
        self.stats['access_count'] += 1
        
    def get_stats(self) -> CacheStats:
        """캐시 통계 조회"""
        with self._lock:
            # 전체 크기 계산
            total_size_bytes = sum(entry.size_bytes for entry in self.index.values())
            total_size_mb = total_size_bytes / 1024 / 1024
            
            # 압축률 계산
            compressed_entries = [e for e in self.index.values() if e.compression]
            compression_ratio = len(compressed_entries) / max(len(self.index), 1)
            
            # 평균 접근 시간
            avg_access_time = (
                self.stats['total_access_time'] / max(self.stats['access_count'], 1)
            )
            
            # 가장 많이 접근된 키
            most_accessed = sorted(
                [(k, e.access_count) for k, e in self.index.items()],
                key=lambda x: x[1],
                reverse=True
            )[:10]
            
            return CacheStats(
                total_entries=len(self.index),
                total_size_mb=total_size_mb,
                hit_count=self.stats['hit_count'],
                miss_count=self.stats['miss_count'],
                eviction_count=self.stats['eviction_count'],
                compression_ratio=compression_ratio,
                avg_access_time_ms=avg_access_time,
                most_accessed_keys=most_accessed
            )
            
    def _start_maintenance_tasks(self):
        """유지보수 작업 시작"""
        # 만료된 엔트리 정리 작업
        def cleanup_expired():
            while True:
                time.sleep(300)  # 5분마다
                with self._lock:
                    expired_keys = []
                    for key, entry in self.index.items():
                        if entry.expires_at and time.time() > entry.expires_at:
                            expired_keys.append(key)
                            
                    for key in expired_keys:
                        self._remove_entry(key)
                        
                    if expired_keys:
                        self._save_index()
                        
        # 백그라운드 스레드로 실행
        cleanup_thread = threading.Thread(target=cleanup_expired, daemon=True)
        cleanup_thread.start()
        
    def export_stats(self, filepath: str):
        """통계 내보내기"""
        stats = self.get_stats()
        stats_dict = asdict(stats)
        stats_dict['export_time'] = datetime.now().isoformat()
        
        with open(filepath, 'w') as f:
            json.dump(stats_dict, f, indent=2)
            
        print(f"📊 캐시 통계 내보내기 완료: {filepath}")


# 전역 고급 캐시 인스턴스
advanced_cache = AdvancedCacheManager()