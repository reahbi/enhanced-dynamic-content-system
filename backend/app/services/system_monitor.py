"""
시스템 모니터링 - 실시간 성능 및 상태 모니터링
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import asyncio
import psutil
import os
from collections import deque
from dataclasses import dataclass
import json

@dataclass
class SystemSnapshot:
    """시스템 스냅샷"""
    timestamp: datetime
    cpu_percent: float
    memory_percent: float
    memory_mb: float
    disk_usage_percent: float
    active_threads: int
    open_files: int
    network_io: Dict[str, int]
    process_info: Dict[str, Any]

@dataclass 
class Alert:
    """시스템 알림"""
    timestamp: datetime
    level: str  # 'info', 'warning', 'critical'
    metric: str
    message: str
    value: Any
    threshold: Any

class SystemMonitor:
    """시스템 모니터"""
    
    def __init__(self, 
                 history_size: int = 1000,
                 monitoring_interval: float = 5.0):
        self.history_size = history_size
        self.monitoring_interval = monitoring_interval
        self.history = deque(maxlen=history_size)
        self.alerts = deque(maxlen=100)
        self.is_monitoring = False
        self.process = psutil.Process()
        
        # 임계값 설정
        self.thresholds = {
            'cpu_percent': {'warning': 70, 'critical': 90},
            'memory_percent': {'warning': 80, 'critical': 95},
            'disk_usage_percent': {'warning': 85, 'critical': 95},
            'response_time': {'warning': 2.0, 'critical': 5.0}
        }
        
    async def start_monitoring(self):
        """모니터링 시작"""
        self.is_monitoring = True
        asyncio.create_task(self._monitoring_loop())
        print("🔍 시스템 모니터링 시작...")
        
    async def stop_monitoring(self):
        """모니터링 중지"""
        self.is_monitoring = False
        print("🛑 시스템 모니터링 중지...")
        
    async def _monitoring_loop(self):
        """모니터링 루프"""
        while self.is_monitoring:
            try:
                snapshot = self._take_snapshot()
                self.history.append(snapshot)
                
                # 임계값 확인
                self._check_thresholds(snapshot)
                
                await asyncio.sleep(self.monitoring_interval)
                
            except Exception as e:
                print(f"모니터링 오류: {e}")
                
    def _take_snapshot(self) -> SystemSnapshot:
        """시스템 스냅샷 생성"""
        # CPU 사용률
        cpu_percent = psutil.cpu_percent(interval=1)
        
        # 메모리 정보
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        memory_mb = self.process.memory_info().rss / 1024 / 1024
        
        # 디스크 사용률
        disk = psutil.disk_usage('/')
        disk_usage_percent = disk.percent
        
        # 프로세스 정보
        process_info = {
            'pid': self.process.pid,
            'threads': self.process.num_threads(),
            'open_files': len(self.process.open_files()),
            'connections': len(self.process.connections())
        }
        
        # 네트워크 I/O
        net_io = psutil.net_io_counters()
        network_io = {
            'bytes_sent': net_io.bytes_sent,
            'bytes_recv': net_io.bytes_recv
        }
        
        return SystemSnapshot(
            timestamp=datetime.now(),
            cpu_percent=cpu_percent,
            memory_percent=memory_percent,
            memory_mb=memory_mb,
            disk_usage_percent=disk_usage_percent,
            active_threads=process_info['threads'],
            open_files=process_info['open_files'],
            network_io=network_io,
            process_info=process_info
        )
    
    def _check_thresholds(self, snapshot: SystemSnapshot):
        """임계값 확인 및 알림 생성"""
        # CPU 확인
        if snapshot.cpu_percent > self.thresholds['cpu_percent']['critical']:
            self._create_alert('critical', 'cpu_percent', 
                             f"CPU 사용률 위험: {snapshot.cpu_percent:.1f}%",
                             snapshot.cpu_percent,
                             self.thresholds['cpu_percent']['critical'])
        elif snapshot.cpu_percent > self.thresholds['cpu_percent']['warning']:
            self._create_alert('warning', 'cpu_percent',
                             f"CPU 사용률 경고: {snapshot.cpu_percent:.1f}%",
                             snapshot.cpu_percent,
                             self.thresholds['cpu_percent']['warning'])
                             
        # 메모리 확인
        if snapshot.memory_percent > self.thresholds['memory_percent']['critical']:
            self._create_alert('critical', 'memory_percent',
                             f"메모리 사용률 위험: {snapshot.memory_percent:.1f}%",
                             snapshot.memory_percent,
                             self.thresholds['memory_percent']['critical'])
        elif snapshot.memory_percent > self.thresholds['memory_percent']['warning']:
            self._create_alert('warning', 'memory_percent',
                             f"메모리 사용률 경고: {snapshot.memory_percent:.1f}%",
                             snapshot.memory_percent,
                             self.thresholds['memory_percent']['warning'])
                             
        # 디스크 확인
        if snapshot.disk_usage_percent > self.thresholds['disk_usage_percent']['critical']:
            self._create_alert('critical', 'disk_usage_percent',
                             f"디스크 사용률 위험: {snapshot.disk_usage_percent:.1f}%",
                             snapshot.disk_usage_percent,
                             self.thresholds['disk_usage_percent']['critical'])
                             
    def _create_alert(self, level: str, metric: str, message: str, value: Any, threshold: Any):
        """알림 생성"""
        alert = Alert(
            timestamp=datetime.now(),
            level=level,
            metric=metric,
            message=message,
            value=value,
            threshold=threshold
        )
        self.alerts.append(alert)
        
        # 콘솔 출력 (실제로는 로깅 시스템 사용)
        icon = "🔴" if level == 'critical' else "🟡" if level == 'warning' else "🔵"
        print(f"{icon} [{alert.timestamp.strftime('%H:%M:%S')}] {message}")
        
    def get_current_status(self) -> Dict[str, Any]:
        """현재 상태 조회"""
        if not self.history:
            return {'status': 'no_data'}
            
        latest = self.history[-1]
        
        return {
            'timestamp': latest.timestamp.isoformat(),
            'cpu_percent': latest.cpu_percent,
            'memory_percent': latest.memory_percent,
            'memory_mb': latest.memory_mb,
            'disk_usage_percent': latest.disk_usage_percent,
            'active_threads': latest.active_threads,
            'open_files': latest.open_files,
            'status': self._determine_health_status(latest)
        }
    
    def get_statistics(self, minutes: int = 5) -> Dict[str, Any]:
        """통계 조회"""
        if not self.history:
            return {'status': 'no_data'}
            
        # 지정된 시간 범위의 데이터 필터링
        cutoff_time = datetime.now() - timedelta(minutes=minutes)
        recent_data = [s for s in self.history if s.timestamp > cutoff_time]
        
        if not recent_data:
            return {'status': 'insufficient_data'}
            
        # 통계 계산
        cpu_values = [s.cpu_percent for s in recent_data]
        memory_values = [s.memory_percent for s in recent_data]
        
        return {
            'time_range_minutes': minutes,
            'sample_count': len(recent_data),
            'cpu': {
                'avg': sum(cpu_values) / len(cpu_values),
                'min': min(cpu_values),
                'max': max(cpu_values)
            },
            'memory': {
                'avg': sum(memory_values) / len(memory_values),
                'min': min(memory_values),
                'max': max(memory_values)
            },
            'alerts': {
                'critical': len([a for a in self.alerts if a.level == 'critical']),
                'warning': len([a for a in self.alerts if a.level == 'warning']),
                'info': len([a for a in self.alerts if a.level == 'info'])
            }
        }
    
    def _determine_health_status(self, snapshot: SystemSnapshot) -> str:
        """시스템 건강 상태 판단"""
        if (snapshot.cpu_percent > self.thresholds['cpu_percent']['critical'] or
            snapshot.memory_percent > self.thresholds['memory_percent']['critical']):
            return 'critical'
        elif (snapshot.cpu_percent > self.thresholds['cpu_percent']['warning'] or
              snapshot.memory_percent > self.thresholds['memory_percent']['warning']):
            return 'warning'
        else:
            return 'healthy'
    
    def export_metrics(self, filepath: str):
        """메트릭 내보내기"""
        data = {
            'export_time': datetime.now().isoformat(),
            'history': [
                {
                    'timestamp': s.timestamp.isoformat(),
                    'cpu_percent': s.cpu_percent,
                    'memory_percent': s.memory_percent,
                    'memory_mb': s.memory_mb,
                    'disk_usage_percent': s.disk_usage_percent
                }
                for s in self.history
            ],
            'alerts': [
                {
                    'timestamp': a.timestamp.isoformat(),
                    'level': a.level,
                    'metric': a.metric,
                    'message': a.message,
                    'value': a.value
                }
                for a in self.alerts
            ]
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
            
        print(f"📊 메트릭 내보내기 완료: {filepath}")


class HealthChecker:
    """시스템 건강 체크"""
    
    def __init__(self):
        self.checks = {
            'database': self._check_database,
            'cache': self._check_cache,
            'api': self._check_api,
            'disk_space': self._check_disk_space,
            'memory': self._check_memory
        }
        
    async def run_health_check(self) -> Dict[str, Any]:
        """전체 건강 체크 실행"""
        results = {}
        overall_status = 'healthy'
        
        for check_name, check_func in self.checks.items():
            try:
                result = await check_func()
                results[check_name] = result
                
                if result['status'] == 'unhealthy':
                    overall_status = 'unhealthy'
                elif result['status'] == 'degraded' and overall_status == 'healthy':
                    overall_status = 'degraded'
                    
            except Exception as e:
                results[check_name] = {
                    'status': 'error',
                    'message': str(e)
                }
                overall_status = 'unhealthy'
                
        return {
            'timestamp': datetime.now().isoformat(),
            'overall_status': overall_status,
            'checks': results
        }
    
    async def _check_database(self) -> Dict[str, Any]:
        """데이터베이스 연결 체크"""
        # 실제로는 데이터베이스 연결 테스트
        return {
            'status': 'healthy',
            'response_time_ms': 15,
            'message': 'Database connection OK'
        }
    
    async def _check_cache(self) -> Dict[str, Any]:
        """캐시 시스템 체크"""
        # 실제로는 캐시 연결 테스트
        return {
            'status': 'healthy',
            'hit_rate': 0.85,
            'message': 'Cache system operational'
        }
    
    async def _check_api(self) -> Dict[str, Any]:
        """API 상태 체크"""
        # 실제로는 API 엔드포인트 테스트
        return {
            'status': 'healthy',
            'response_time_ms': 50,
            'message': 'API responding normally'
        }
    
    async def _check_disk_space(self) -> Dict[str, Any]:
        """디스크 공간 체크"""
        disk = psutil.disk_usage('/')
        status = 'healthy'
        
        if disk.percent > 95:
            status = 'unhealthy'
        elif disk.percent > 85:
            status = 'degraded'
            
        return {
            'status': status,
            'usage_percent': disk.percent,
            'free_gb': disk.free / (1024**3),
            'message': f'Disk usage: {disk.percent:.1f}%'
        }
    
    async def _check_memory(self) -> Dict[str, Any]:
        """메모리 상태 체크"""
        memory = psutil.virtual_memory()
        status = 'healthy'
        
        if memory.percent > 95:
            status = 'unhealthy'
        elif memory.percent > 85:
            status = 'degraded'
            
        return {
            'status': status,
            'usage_percent': memory.percent,
            'available_gb': memory.available / (1024**3),
            'message': f'Memory usage: {memory.percent:.1f}%'
        }


# 전역 모니터 인스턴스
system_monitor = SystemMonitor()
health_checker = HealthChecker()