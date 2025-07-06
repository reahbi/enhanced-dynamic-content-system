"""
버그 수정 유틸리티 - 공통 버그 패턴 수정
"""

from typing import Any, Dict, List, Optional, Union
import re
import json
from datetime import datetime
import logging
from functools import wraps
import traceback

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BugFixUtils:
    """버그 수정 유틸리티"""
    
    @staticmethod
    def safe_string_processing(text: Any) -> str:
        """안전한 문자열 처리"""
        if text is None:
            return ""
            
        if not isinstance(text, str):
            try:
                text = str(text)
            except:
                return ""
                
        # 위험한 문자 제거
        dangerous_patterns = [
            r'<script[^>]*>.*?</script>',  # 스크립트 태그
            r'javascript:',  # 자바스크립트 프로토콜
            r'on\w+\s*=',  # 이벤트 핸들러
            r'--',  # SQL 주석
            r';.*DROP.*TABLE',  # SQL 인젝션
            r'\.\./\.\./',  # 디렉토리 순회
        ]
        
        for pattern in dangerous_patterns:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE)
            
        # 특수 문자 이스케이프
        text = text.replace('<', '&lt;').replace('>', '&gt;')
        
        return text.strip()
    
    @staticmethod
    def safe_json_loads(json_string: str, default: Any = None) -> Any:
        """안전한 JSON 파싱"""
        if not json_string:
            return default
            
        try:
            return json.loads(json_string)
        except json.JSONDecodeError as e:
            logger.warning(f"JSON 파싱 실패: {e}")
            
            # 일반적인 JSON 오류 수정 시도
            try:
                # 따옴표 수정
                fixed_json = json_string.replace("'", '"')
                # 마지막 쉼표 제거
                fixed_json = re.sub(r',\s*}', '}', fixed_json)
                fixed_json = re.sub(r',\s*]', ']', fixed_json)
                
                return json.loads(fixed_json)
            except:
                return default
    
    @staticmethod
    def safe_dict_access(dictionary: Dict[str, Any], 
                        key_path: str, 
                        default: Any = None) -> Any:
        """안전한 딕셔너리 접근"""
        if not dictionary or not isinstance(dictionary, dict):
            return default
            
        keys = key_path.split('.')
        value = dictionary
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
                
        return value
    
    @staticmethod
    def validate_and_fix_url(url: str) -> Optional[str]:
        """URL 검증 및 수정"""
        if not url:
            return None
            
        url = url.strip()
        
        # 프로토콜 추가
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
            
        # 기본 URL 검증
        url_pattern = re.compile(
            r'^https?://'  # 프로토콜
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # 도메인
            r'localhost|'  # 로컬호스트
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # IP
            r'(?::\d+)?'  # 포트
            r'(?:/?|[/?]\S+)$', re.IGNORECASE
        )
        
        if url_pattern.match(url):
            return url
        else:
            logger.warning(f"유효하지 않은 URL: {url}")
            return None
    
    @staticmethod
    def fix_encoding_issues(text: str) -> str:
        """인코딩 문제 수정"""
        if not text:
            return ""
            
        # 일반적인 인코딩 문제 패턴
        encoding_fixes = {
            'â€™': "'",
            'â€œ': '"',
            'â€': '"',
            'â€"': '-',
            'â€"': '-',
            'Ã©': 'é',
            'Ã¨': 'è',
            'Ã ': 'à',
            'Ã§': 'ç',
            'â‚¬': '€',
            'Â°': '°'
        }
        
        for wrong, correct in encoding_fixes.items():
            text = text.replace(wrong, correct)
            
        # 깨진 유니코드 제거
        try:
            text = text.encode('utf-8', errors='ignore').decode('utf-8')
        except:
            pass
            
        return text
    
    @staticmethod
    def handle_none_values(data: Any, default: Any = "") -> Any:
        """None 값 처리"""
        if data is None:
            return default
            
        if isinstance(data, dict):
            return {k: BugFixUtils.handle_none_values(v, default) 
                   for k, v in data.items()}
                   
        if isinstance(data, list):
            return [BugFixUtils.handle_none_values(item, default) 
                   for item in data]
                   
        return data
    
    @staticmethod
    def fix_date_format(date_string: str) -> Optional[str]:
        """날짜 형식 수정"""
        if not date_string:
            return None
            
        # 다양한 날짜 형식 시도
        date_formats = [
            '%Y-%m-%d',
            '%Y/%m/%d',
            '%d-%m-%Y',
            '%d/%m/%Y',
            '%Y-%m-%d %H:%M:%S',
            '%Y-%m-%dT%H:%M:%S',
            '%Y-%m-%dT%H:%M:%SZ',
            '%Y-%m-%dT%H:%M:%S.%fZ'
        ]
        
        for fmt in date_formats:
            try:
                date_obj = datetime.strptime(date_string, fmt)
                return date_obj.isoformat()
            except:
                continue
                
        logger.warning(f"날짜 형식 파싱 실패: {date_string}")
        return None
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """파일명 정제"""
        if not filename:
            return "untitled"
            
        # 위험한 문자 제거
        filename = re.sub(r'[<>:"/\\|?*\x00-\x1f]', '_', filename)
        
        # 공백 처리
        filename = filename.strip()
        filename = re.sub(r'\s+', '_', filename)
        
        # 길이 제한
        if len(filename) > 255:
            name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
            filename = name[:250] + ('.' + ext if ext else '')
            
        return filename or "untitled"
    
    @staticmethod
    def fix_memory_leak(func):
        """메모리 누수 방지 데코레이터"""
        @wraps(func)
        def wrapper(*args, **kwargs):
            import gc
            
            # 함수 실행 전 가비지 컬렉션
            gc.collect()
            
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                # 함수 실행 후 가비지 컬렉션
                gc.collect()
                
        return wrapper
    
    @staticmethod
    def retry_on_error(max_attempts: int = 3, delay: float = 1.0):
        """에러 시 재시도 데코레이터"""
        def decorator(func):
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                import asyncio
                
                for attempt in range(max_attempts):
                    try:
                        return await func(*args, **kwargs)
                    except Exception as e:
                        if attempt == max_attempts - 1:
                            raise
                            
                        logger.warning(f"시도 {attempt + 1} 실패: {e}")
                        await asyncio.sleep(delay * (attempt + 1))
                        
            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                import time
                
                for attempt in range(max_attempts):
                    try:
                        return func(*args, **kwargs)
                    except Exception as e:
                        if attempt == max_attempts - 1:
                            raise
                            
                        logger.warning(f"시도 {attempt + 1} 실패: {e}")
                        time.sleep(delay * (attempt + 1))
                        
            import asyncio
            if asyncio.iscoroutinefunction(func):
                return async_wrapper
            else:
                return sync_wrapper
                
        return decorator
    
    @staticmethod
    def log_errors(func):
        """에러 로깅 데코레이터"""
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                logger.error(f"함수 {func.__name__} 에러: {e}")
                logger.error(f"Traceback: {traceback.format_exc()}")
                raise
                
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.error(f"함수 {func.__name__} 에러: {e}")
                logger.error(f"Traceback: {traceback.format_exc()}")
                raise
                
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper


class DataValidator:
    """데이터 검증기"""
    
    @staticmethod
    def validate_paper(paper: Any) -> bool:
        """논문 객체 검증"""
        if not paper:
            return False
            
        required_fields = ['title', 'authors']
        
        for field in required_fields:
            if not hasattr(paper, field) or not getattr(paper, field):
                return False
                
        # 숫자 필드 검증
        numeric_fields = ['impact_factor', 'citations', 'year']
        for field in numeric_fields:
            if hasattr(paper, field):
                value = getattr(paper, field)
                if value is not None:
                    try:
                        float(value) if field != 'year' else int(value)
                    except:
                        return False
                        
        return True
    
    @staticmethod
    def validate_content_result(result: Any) -> bool:
        """콘텐츠 생성 결과 검증"""
        if not result:
            return False
            
        required_attrs = ['total_content', 'quality_score']
        
        for attr in required_attrs:
            if not hasattr(result, attr):
                return False
                
        # 콘텐츠 길이 검증
        if not result.total_content or len(result.total_content) < 10:
            return False
            
        # 품질 점수 검증
        if not isinstance(result.quality_score, (int, float)) or result.quality_score < 0:
            return False
            
        return True
    
    @staticmethod
    def validate_cache_key(key: str) -> bool:
        """캐시 키 검증"""
        if not key or not isinstance(key, str):
            return False
            
        # 길이 제한
        if len(key) > 250:
            return False
            
        # 허용된 문자만 사용
        if not re.match(r'^[a-zA-Z0-9_\-]+$', key):
            return False
            
        return True


class ErrorHandler:
    """에러 처리기"""
    
    @staticmethod
    def handle_api_error(error: Exception) -> Dict[str, Any]:
        """API 에러 처리"""
        error_type = type(error).__name__
        
        error_responses = {
            'ValueError': {
                'status': 400,
                'message': '잘못된 요청입니다.',
                'code': 'INVALID_REQUEST'
            },
            'KeyError': {
                'status': 400,
                'message': '필수 파라미터가 누락되었습니다.',
                'code': 'MISSING_PARAMETER'
            },
            'TimeoutError': {
                'status': 504,
                'message': '요청 처리 시간이 초과되었습니다.',
                'code': 'TIMEOUT'
            },
            'MemoryError': {
                'status': 507,
                'message': '메모리가 부족합니다.',
                'code': 'INSUFFICIENT_MEMORY'
            }
        }
        
        default_response = {
            'status': 500,
            'message': '서버 오류가 발생했습니다.',
            'code': 'INTERNAL_ERROR'
        }
        
        response = error_responses.get(error_type, default_response)
        response['error_type'] = error_type
        response['timestamp'] = datetime.now().isoformat()
        
        # 개발 환경에서만 상세 에러 포함
        if logger.level == logging.DEBUG:
            response['details'] = str(error)
            response['traceback'] = traceback.format_exc()
            
        return response
    
    @staticmethod
    def create_fallback_response(operation: str) -> Any:
        """폴백 응답 생성"""
        fallbacks = {
            'category_generation': [
                {
                    'name': '기본 카테고리',
                    'practicality_score': 5.0,
                    'interest_score': 5.0
                }
            ],
            'content_generation': {
                'total_content': '콘텐츠 생성 중 오류가 발생했습니다.',
                'quality_score': 0.0,
                'sections': {}
            },
            'paper_evaluation': {
                'quality_score': 50.0,
                'grade': 'C',
                'details': {}
            }
        }
        
        return fallbacks.get(operation, {})


# 전역 인스턴스
bug_fix_utils = BugFixUtils()
data_validator = DataValidator()
error_handler = ErrorHandler()