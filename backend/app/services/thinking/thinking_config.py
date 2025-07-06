"""
Native Thinking Mode 설정 및 구성 관리
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass
import json
import os

@dataclass
class ThinkingConfig:
    """사고 과정 설정"""
    # 기본 설정
    enable_thinking: bool = True
    require_thinking_for_all: bool = True
    min_thinking_quality: float = 60.0
    max_retry_attempts: int = 3
    
    # 품질 기준
    quality_thresholds: Dict[str, float] = None
    depth_requirements: Dict[str, int] = None
    
    # 성능 설정
    thinking_timeout: float = 30.0
    cache_thinking_results: bool = True
    cache_duration_hours: int = 24
    
    # 분석 설정
    analyze_thinking: bool = True
    store_analysis_results: bool = True
    
    def __post_init__(self):
        if self.quality_thresholds is None:
            self.quality_thresholds = {
                'shorts': 70.0,
                'article': 75.0,
                'report': 80.0,
                'category': 65.0,
                'subcategory': 65.0
            }
            
        if self.depth_requirements is None:
            self.depth_requirements = {
                'shorts': 2,
                'article': 3,
                'report': 4,
                'category': 2,
                'subcategory': 2
            }


class ThinkingConfigManager:
    """사고 과정 설정 관리자"""
    
    def __init__(self, config_path: str = "./config/thinking_config.json"):
        self.config_path = config_path
        self.config = self._load_config()
        
    def _load_config(self) -> ThinkingConfig:
        """설정 파일 로드"""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                return ThinkingConfig(**data)
            except Exception as e:
                print(f"설정 로드 실패, 기본값 사용: {e}")
                
        return ThinkingConfig()
    
    def save_config(self):
        """설정 저장"""
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        
        config_dict = {
            'enable_thinking': self.config.enable_thinking,
            'require_thinking_for_all': self.config.require_thinking_for_all,
            'min_thinking_quality': self.config.min_thinking_quality,
            'max_retry_attempts': self.config.max_retry_attempts,
            'quality_thresholds': self.config.quality_thresholds,
            'depth_requirements': self.config.depth_requirements,
            'thinking_timeout': self.config.thinking_timeout,
            'cache_thinking_results': self.config.cache_thinking_results,
            'cache_duration_hours': self.config.cache_duration_hours,
            'analyze_thinking': self.config.analyze_thinking,
            'store_analysis_results': self.config.store_analysis_results
        }
        
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(config_dict, f, indent=2, ensure_ascii=False)
    
    def update_config(self, **kwargs):
        """설정 업데이트"""
        for key, value in kwargs.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)
        self.save_config()
    
    def get_content_config(self, content_type: str) -> Dict[str, Any]:
        """콘텐츠 타입별 설정 조회"""
        return {
            'quality_threshold': self.config.quality_thresholds.get(content_type, 70.0),
            'depth_requirement': self.config.depth_requirements.get(content_type, 2),
            'enable_thinking': self.config.enable_thinking,
            'max_retry': self.config.max_retry_attempts
        }
    
    def validate_thinking_result(self, content_type: str, quality_score: float, depth_level: int) -> bool:
        """사고 결과 검증"""
        config = self.get_content_config(content_type)
        
        return (quality_score >= config['quality_threshold'] and 
                depth_level >= config['depth_requirement'])
    
    def get_retry_strategy(self, attempt: int) -> Dict[str, Any]:
        """재시도 전략 조회"""
        if attempt >= self.config.max_retry_attempts:
            return {'retry': False, 'reason': 'max_attempts_reached'}
            
        # 시도 횟수에 따른 전략 변경
        strategies = [
            {
                'retry': True,
                'enhancement': 'basic',
                'message': '기본 품질 향상 시도'
            },
            {
                'retry': True,
                'enhancement': 'step_by_step',
                'message': '단계별 사고 과정 강화'
            },
            {
                'retry': True,
                'enhancement': 'full',
                'message': '전체 사고 과정 재구성'
            }
        ]
        
        return strategies[min(attempt, len(strategies) - 1)]


class ThinkingPromptTemplates:
    """사고 유도 프롬프트 템플릿 관리"""
    
    @staticmethod
    def get_enhancement_template(enhancement_type: str) -> str:
        """향상 템플릿 조회"""
        templates = {
            'basic': """
더 명확하고 구조화된 사고 과정을 전개해주세요.
각 단계를 논리적으로 연결하고, 근거를 제시해주세요.
""",
            
            'step_by_step': """
다음 단계를 따라 체계적으로 사고해주세요:
1. 문제/주제의 핵심 파악
2. 관련 정보와 데이터 분석
3. 다양한 관점에서의 검토
4. 논리적 결론 도출
5. 실행 가능한 방안 제시
""",
            
            'full': """
<deep_thinking>
이 주제에 대해 깊이 있는 사고가 필요합니다.

먼저, 문제의 본질을 파악하고:
- 핵심 이슈는 무엇인가?
- 왜 이것이 중요한가?
- 누가 영향을 받는가?

다음으로, 체계적 분석을 수행하고:
- 현재 상황과 원인
- 가능한 해결책들
- 각 방안의 장단점

마지막으로, 최적의 방안을 도출하고:
- 선택의 근거
- 예상되는 효과
- 실행 계획

이 모든 과정을 구체적이고 논리적으로 전개해주세요.
</deep_thinking>
"""
        }
        
        return templates.get(enhancement_type, templates['basic'])
    
    @staticmethod
    def get_quality_criteria() -> Dict[str, str]:
        """품질 평가 기준"""
        return {
            'structure': '명확한 구조와 논리적 흐름',
            'evidence': '근거와 데이터 기반 사고',
            'depth': '심층적이고 다각도의 분석',
            'practicality': '실용적이고 실행 가능한 결론',
            'creativity': '창의적이고 혁신적인 접근'
        }


# 전역 설정 인스턴스
thinking_config_manager = ThinkingConfigManager()