"""
로깅 설정 - 시스템 전반의 로깅 구성
"""

import logging
import logging.handlers
from pathlib import Path
from datetime import datetime
import json
import sys
from typing import Dict, Any, Optional

class CustomFormatter(logging.Formatter):
    """커스텀 로그 포맷터"""
    
    # 로그 레벨별 색상 (터미널용)
    COLORS = {
        'DEBUG': '\033[36m',    # Cyan
        'INFO': '\033[32m',     # Green
        'WARNING': '\033[33m',  # Yellow
        'ERROR': '\033[31m',    # Red
        'CRITICAL': '\033[35m', # Magenta
    }
    RESET = '\033[0m'
    
    def __init__(self, use_colors: bool = True):
        super().__init__()
        self.use_colors = use_colors and sys.stdout.isatty()
        
    def format(self, record):
        # 기본 포맷
        log_fmt = '[%(asctime)s] %(levelname)-8s | %(name)s | %(message)s'
        
        # 에러인 경우 추가 정보
        if record.levelno >= logging.ERROR:
            log_fmt += ' | File: %(pathname)s:%(lineno)d'
            
        # 색상 적용
        if self.use_colors:
            levelname = record.levelname
            if levelname in self.COLORS:
                log_fmt = log_fmt.replace(
                    '%(levelname)-8s',
                    f'{self.COLORS[levelname]}%(levelname)-8s{self.RESET}'
                )
                
        formatter = logging.Formatter(log_fmt, datefmt='%Y-%m-%d %H:%M:%S')
        return formatter.format(record)


class JSONFormatter(logging.Formatter):
    """JSON 포맷 로거 (구조화된 로깅용)"""
    
    def format(self, record):
        log_obj = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        # 추가 컨텍스트 정보
        if hasattr(record, 'user_id'):
            log_obj['user_id'] = record.user_id
        if hasattr(record, 'request_id'):
            log_obj['request_id'] = record.request_id
        if hasattr(record, 'content_type'):
            log_obj['content_type'] = record.content_type
            
        # 에러 정보
        if record.exc_info:
            log_obj['exception'] = self.formatException(record.exc_info)
            
        return json.dumps(log_obj, ensure_ascii=False)


class LoggingConfig:
    """로깅 설정 관리"""
    
    def __init__(self, 
                 log_dir: str = "./logs",
                 app_name: str = "hybrid_content_system",
                 log_level: str = "INFO",
                 enable_file_logging: bool = True,
                 enable_console_logging: bool = True):
        
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        self.app_name = app_name
        self.log_level = getattr(logging, log_level.upper())
        self.enable_file_logging = enable_file_logging
        self.enable_console_logging = enable_console_logging
        
        self.loggers = {}
        
    def setup_logging(self):
        """전체 로깅 설정"""
        # 루트 로거 설정
        root_logger = logging.getLogger()
        root_logger.setLevel(self.log_level)
        
        # 기존 핸들러 제거
        root_logger.handlers = []
        
        # 콘솔 핸들러
        if self.enable_console_logging:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setFormatter(CustomFormatter(use_colors=True))
            console_handler.setLevel(self.log_level)
            root_logger.addHandler(console_handler)
            
        # 파일 핸들러들
        if self.enable_file_logging:
            # 일반 로그 파일
            file_handler = self._create_file_handler(
                'app.log',
                formatter=CustomFormatter(use_colors=False)
            )
            root_logger.addHandler(file_handler)
            
            # JSON 로그 파일 (분석용)
            json_handler = self._create_file_handler(
                'app.json.log',
                formatter=JSONFormatter()
            )
            root_logger.addHandler(json_handler)
            
            # 에러 전용 로그
            error_handler = self._create_file_handler(
                'errors.log',
                formatter=CustomFormatter(use_colors=False),
                level=logging.ERROR
            )
            root_logger.addHandler(error_handler)
            
    def _create_file_handler(self, 
                           filename: str,
                           formatter: logging.Formatter,
                           level: Optional[int] = None) -> logging.Handler:
        """파일 핸들러 생성"""
        log_file = self.log_dir / filename
        
        # 로테이팅 파일 핸들러 (최대 10MB, 5개 백업)
        handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        
        handler.setFormatter(formatter)
        if level:
            handler.setLevel(level)
        else:
            handler.setLevel(self.log_level)
            
        return handler
        
    def get_logger(self, name: str) -> logging.Logger:
        """모듈별 로거 생성"""
        if name in self.loggers:
            return self.loggers[name]
            
        logger = logging.getLogger(name)
        self.loggers[name] = logger
        
        return logger
        
    def setup_module_loggers(self):
        """모듈별 로거 설정"""
        # 특정 모듈에 대한 커스텀 설정
        module_configs = {
            'content_generator': logging.INFO,
            'paper_evaluator': logging.INFO,
            'cache_manager': logging.WARNING,
            'thinking_engine': logging.DEBUG,
            'performance': logging.INFO,
            'security': logging.WARNING
        }
        
        for module_name, level in module_configs.items():
            logger = self.get_logger(f"{self.app_name}.{module_name}")
            logger.setLevel(level)
            
    def add_context_to_logs(self, **context):
        """로그에 컨텍스트 정보 추가"""
        class ContextFilter(logging.Filter):
            def filter(self, record):
                for key, value in context.items():
                    setattr(record, key, value)
                return True
                
        # 모든 핸들러에 필터 추가
        root_logger = logging.getLogger()
        context_filter = ContextFilter()
        
        for handler in root_logger.handlers:
            handler.addFilter(context_filter)


class PerformanceLogger:
    """성능 전용 로거"""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.timings = {}
        
    def start_timing(self, operation: str):
        """타이밍 시작"""
        self.timings[operation] = datetime.now()
        
    def end_timing(self, operation: str, metadata: Optional[Dict[str, Any]] = None):
        """타이밍 종료 및 로깅"""
        if operation not in self.timings:
            return
            
        start_time = self.timings.pop(operation)
        duration = (datetime.now() - start_time).total_seconds()
        
        log_data = {
            'operation': operation,
            'duration_seconds': duration,
            'timestamp': datetime.now().isoformat()
        }
        
        if metadata:
            log_data.update(metadata)
            
        self.logger.info(f"Performance: {operation} took {duration:.3f}s", 
                        extra=log_data)
        
        # 느린 작업 경고
        if duration > 5.0:
            self.logger.warning(f"Slow operation: {operation} took {duration:.3f}s")


class SecurityLogger:
    """보안 전용 로거"""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
        
    def log_suspicious_activity(self, 
                              activity_type: str,
                              details: Dict[str, Any],
                              severity: str = 'WARNING'):
        """의심스러운 활동 로깅"""
        log_data = {
            'security_event': True,
            'activity_type': activity_type,
            'severity': severity,
            'timestamp': datetime.now().isoformat(),
            **details
        }
        
        log_method = getattr(self.logger, severity.lower(), self.logger.warning)
        log_method(f"Security Alert: {activity_type}", extra=log_data)
        
    def log_access_attempt(self,
                         resource: str,
                         user_id: Optional[str],
                         success: bool,
                         reason: Optional[str] = None):
        """접근 시도 로깅"""
        log_data = {
            'access_log': True,
            'resource': resource,
            'user_id': user_id or 'anonymous',
            'success': success,
            'timestamp': datetime.now().isoformat()
        }
        
        if reason:
            log_data['reason'] = reason
            
        if success:
            self.logger.info(f"Access granted: {resource}", extra=log_data)
        else:
            self.logger.warning(f"Access denied: {resource}", extra=log_data)


class AuditLogger:
    """감사 로그"""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
        
    def log_action(self,
                  action: str,
                  entity_type: str,
                  entity_id: str,
                  user_id: Optional[str] = None,
                  changes: Optional[Dict[str, Any]] = None):
        """사용자 액션 로깅"""
        audit_data = {
            'audit_log': True,
            'action': action,
            'entity_type': entity_type,
            'entity_id': entity_id,
            'user_id': user_id or 'system',
            'timestamp': datetime.now().isoformat()
        }
        
        if changes:
            audit_data['changes'] = changes
            
        self.logger.info(f"Audit: {action} on {entity_type}:{entity_id}", 
                        extra=audit_data)


# 전역 로깅 설정
logging_config = LoggingConfig()
logging_config.setup_logging()
logging_config.setup_module_loggers()

# 전문 로거들
app_logger = logging_config.get_logger('hybrid_content_system')
performance_logger = PerformanceLogger(logging_config.get_logger('performance'))
security_logger = SecurityLogger(logging_config.get_logger('security'))
audit_logger = AuditLogger(logging_config.get_logger('audit'))