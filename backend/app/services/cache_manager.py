"""
파일 기반 캐싱 시스템 - API 응답 속도 향상
"""

import json
import hashlib
import os
from pathlib import Path
from datetime import datetime, timedelta
from typing import Any, Optional, Dict
import pickle

class CacheManager:
    """파일 기반 캐시 관리자"""
    
    def __init__(self, cache_dir: str = "cache", default_ttl: int = 3600):
        """
        Args:
            cache_dir: 캐시 디렉토리 경로
            default_ttl: 기본 TTL (초 단위, 기본값: 1시간)
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.default_ttl = default_ttl
        
        # 캐시 타입별 서브디렉토리
        self.subdirs = {
            "categories": self.cache_dir / "categories",
            "papers": self.cache_dir / "papers",
            "content": self.cache_dir / "content"
        }
        
        for subdir in self.subdirs.values():
            subdir.mkdir(exist_ok=True)
    
    def _generate_key(self, cache_type: str, params: Dict[str, Any]) -> str:
        """캐시 키 생성"""
        # 파라미터를 정렬하여 일관된 키 생성
        sorted_params = json.dumps(params, sort_keys=True, ensure_ascii=False)
        hash_obj = hashlib.md5(sorted_params.encode())
        return f"{cache_type}_{hash_obj.hexdigest()}"
    
    def _get_cache_path(self, cache_type: str, key: str) -> Path:
        """캐시 파일 경로 반환"""
        subdir = self.subdirs.get(cache_type, self.cache_dir)
        return subdir / f"{key}.cache"
    
    def get(self, cache_type: str, params: Dict[str, Any]) -> Optional[Any]:
        """캐시에서 데이터 조회"""
        key = self._generate_key(cache_type, params)
        cache_path = self._get_cache_path(cache_type, key)
        
        if not cache_path.exists():
            return None
        
        try:
            with open(cache_path, "rb") as f:
                cache_data = pickle.load(f)
            
            # TTL 확인
            if datetime.now() > cache_data["expires_at"]:
                # 만료된 캐시 삭제
                cache_path.unlink()
                return None
            
            return cache_data["data"]
            
        except Exception as e:
            print(f"캐시 읽기 오류: {e}")
            # 손상된 캐시 파일 삭제
            if cache_path.exists():
                cache_path.unlink()
            return None
    
    def set(self, cache_type: str, params: Dict[str, Any], 
            data: Any, ttl: Optional[int] = None) -> bool:
        """캐시에 데이터 저장"""
        key = self._generate_key(cache_type, params)
        cache_path = self._get_cache_path(cache_type, key)
        
        ttl = ttl or self.default_ttl
        expires_at = datetime.now() + timedelta(seconds=ttl)
        
        cache_data = {
            "data": data,
            "created_at": datetime.now(),
            "expires_at": expires_at,
            "params": params
        }
        
        try:
            with open(cache_path, "wb") as f:
                pickle.dump(cache_data, f)
            return True
            
        except Exception as e:
            print(f"캐시 저장 오류: {e}")
            return False
    
    def delete(self, cache_type: str, params: Dict[str, Any]) -> bool:
        """특정 캐시 삭제"""
        key = self._generate_key(cache_type, params)
        cache_path = self._get_cache_path(cache_type, key)
        
        if cache_path.exists():
            cache_path.unlink()
            return True
        return False
    
    def clear(self, cache_type: Optional[str] = None) -> int:
        """캐시 전체 또는 특정 타입 삭제"""
        count = 0
        
        if cache_type:
            # 특정 타입만 삭제
            subdir = self.subdirs.get(cache_type, self.cache_dir)
            for cache_file in subdir.glob("*.cache"):
                cache_file.unlink()
                count += 1
        else:
            # 전체 삭제
            for subdir in self.subdirs.values():
                for cache_file in subdir.glob("*.cache"):
                    cache_file.unlink()
                    count += 1
        
        return count
    
    def cleanup_expired(self) -> int:
        """만료된 캐시 정리"""
        count = 0
        now = datetime.now()
        
        for subdir in self.subdirs.values():
            for cache_file in subdir.glob("*.cache"):
                try:
                    with open(cache_file, "rb") as f:
                        cache_data = pickle.load(f)
                    
                    if now > cache_data["expires_at"]:
                        cache_file.unlink()
                        count += 1
                        
                except Exception:
                    # 읽을 수 없는 파일 삭제
                    cache_file.unlink()
                    count += 1
        
        return count
    
    def get_stats(self) -> Dict[str, Any]:
        """캐시 통계 정보"""
        stats = {
            "total_files": 0,
            "total_size": 0,
            "by_type": {}
        }
        
        for cache_type, subdir in self.subdirs.items():
            files = list(subdir.glob("*.cache"))
            size = sum(f.stat().st_size for f in files)
            
            stats["by_type"][cache_type] = {
                "count": len(files),
                "size": size
            }
            stats["total_files"] += len(files)
            stats["total_size"] += size
        
        # 사이즈를 읽기 쉬운 형태로 변환
        stats["total_size_readable"] = self._format_size(stats["total_size"])
        
        return stats
    
    def _format_size(self, size_bytes: int) -> str:
        """바이트를 읽기 쉬운 형태로 변환"""
        for unit in ["B", "KB", "MB", "GB"]:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} TB"

# 싱글톤 인스턴스
cache_manager = CacheManager()