"""
Native Thinking Mode 통합 - 기존 콘텐츠 생성기와의 통합
"""

from typing import Dict, List, Any, Optional
import asyncio
from datetime import datetime

from ..content_generators.base_generator import BaseContentGenerator, GeneratedContent
from ..content_generators.shorts_generator import ShortsScriptGenerator
from ..content_generators.article_generator import ArticleGenerator
from ..content_generators.report_generator import ReportGenerator
from .native_thinking_engine import NativeThinkingEngine, ThinkingResult
from .prompt_engineering import ThinkingPromptEngineer, ContentType
from .thinking_analyzer import ThinkingAnalyzer, ThinkingAnalysis

class ThinkingEnabledContentGenerator:
    """Native Thinking Mode가 통합된 콘텐츠 생성기"""
    
    def __init__(self):
        self.thinking_engine = NativeThinkingEngine()
        self.prompt_engineer = ThinkingPromptEngineer()
        self.thinking_analyzer = ThinkingAnalyzer()
        
        # 콘텐츠 생성기들
        self.generators = {
            ContentType.SHORTS: ShortsScriptGenerator(),
            ContentType.ARTICLE: ArticleGenerator(),
            ContentType.REPORT: ReportGenerator()
        }
        
    async def generate_with_thinking(self,
                                   content_type: ContentType,
                                   topic: str,
                                   papers: List[Any],
                                   target_audience: str = "general",
                                   **kwargs) -> Dict[str, Any]:
        """사고 과정을 포함한 콘텐츠 생성"""
        
        # 1. 사고 유도 프롬프트 생성
        context = {
            'papers': papers,
            'target_audience': target_audience,
            'category': kwargs.get('category', '')
        }
        
        thinking_prompt = self.prompt_engineer.create_thinking_prompt(
            content_type, topic, context
        )
        
        # 2. Native Thinking 실행
        thinking_result = self.thinking_engine.generate_with_thinking(
            thinking_prompt, require_thinking=True
        )
        
        # 3. 사고 과정 분석
        thinking_analysis = self.thinking_analyzer.analyze(
            thinking_result.thinking_process
        )
        
        # 4. 사고 품질이 낮으면 재시도
        if thinking_analysis.quality_score < 60:
            enhanced_prompt = self.prompt_engineer.enhance_with_step_by_step_thinking(
                thinking_prompt
            )
            thinking_result = self.thinking_engine.generate_with_thinking(
                enhanced_prompt, require_thinking=True
            )
            thinking_analysis = self.thinking_analyzer.analyze(
                thinking_result.thinking_process
            )
        
        # 5. 콘텐츠 생성기 실행
        generator = self.generators.get(content_type)
        if not generator:
            raise ValueError(f"Unknown content type: {content_type}")
            
        # 사고 과정을 바탕으로 생성
        generated_content = await self._generate_content_with_insights(
            generator, topic, papers, target_audience, 
            thinking_result, thinking_analysis, **kwargs
        )
        
        # 6. 결과 통합
        return {
            'content': generated_content,
            'thinking': {
                'process': thinking_result.thinking_process,
                'quality_score': thinking_analysis.quality_score,
                'depth_level': thinking_analysis.depth_level,
                'key_insights': thinking_result.key_insights,
                'patterns': thinking_analysis.thinking_patterns,
                'analysis': thinking_analysis
            },
            'metadata': {
                'generated_at': datetime.now().isoformat(),
                'content_type': content_type.value,
                'thinking_enabled': True
            }
        }
    
    async def _generate_content_with_insights(self,
                                            generator: BaseContentGenerator,
                                            topic: str,
                                            papers: List[Any],
                                            target_audience: str,
                                            thinking_result: ThinkingResult,
                                            thinking_analysis: ThinkingAnalysis,
                                            **kwargs) -> GeneratedContent:
        """사고 인사이트를 활용한 콘텐츠 생성"""
        
        # 사고 과정에서 도출된 인사이트를 kwargs에 추가
        enhanced_kwargs = kwargs.copy()
        enhanced_kwargs['thinking_insights'] = thinking_result.key_insights
        enhanced_kwargs['thinking_quality'] = thinking_analysis.quality_score
        enhanced_kwargs['thinking_patterns'] = thinking_analysis.thinking_patterns
        
        # 생성기 실행
        content = generator.generate(
            topic, papers, target_audience=target_audience, **enhanced_kwargs
        )
        
        # 사고 과정 정보 추가
        content.thinking_process = thinking_result.thinking_process
        
        return content


class ThinkingPerformanceMonitor:
    """사고 과정 성능 모니터"""
    
    def __init__(self):
        self.metrics_history = []
        
    def record_generation(self, 
                         content_type: str,
                         thinking_quality: float,
                         thinking_depth: int,
                         generation_time: float):
        """생성 메트릭 기록"""
        metric = {
            'timestamp': datetime.now().isoformat(),
            'content_type': content_type,
            'thinking_quality': thinking_quality,
            'thinking_depth': thinking_depth,
            'generation_time': generation_time
        }
        self.metrics_history.append(metric)
        
    def get_average_metrics(self, content_type: Optional[str] = None) -> Dict[str, float]:
        """평균 메트릭 계산"""
        filtered_metrics = self.metrics_history
        if content_type:
            filtered_metrics = [m for m in self.metrics_history 
                              if m['content_type'] == content_type]
            
        if not filtered_metrics:
            return {
                'avg_quality': 0.0,
                'avg_depth': 0.0,
                'avg_time': 0.0,
                'count': 0
            }
            
        avg_quality = sum(m['thinking_quality'] for m in filtered_metrics) / len(filtered_metrics)
        avg_depth = sum(m['thinking_depth'] for m in filtered_metrics) / len(filtered_metrics)
        avg_time = sum(m['generation_time'] for m in filtered_metrics) / len(filtered_metrics)
        
        return {
            'avg_quality': avg_quality,
            'avg_depth': avg_depth,
            'avg_time': avg_time,
            'count': len(filtered_metrics)
        }
    
    def get_improvement_trends(self) -> Dict[str, Any]:
        """개선 추세 분석"""
        if len(self.metrics_history) < 10:
            return {'trend': 'insufficient_data'}
            
        # 최근 10개와 이전 10개 비교
        recent = self.metrics_history[-10:]
        previous = self.metrics_history[-20:-10] if len(self.metrics_history) >= 20 else self.metrics_history[:10]
        
        recent_avg_quality = sum(m['thinking_quality'] for m in recent) / len(recent)
        previous_avg_quality = sum(m['thinking_quality'] for m in previous) / len(previous)
        
        quality_improvement = ((recent_avg_quality - previous_avg_quality) / previous_avg_quality) * 100
        
        return {
            'trend': 'improving' if quality_improvement > 0 else 'declining',
            'quality_improvement_percent': quality_improvement,
            'recent_avg_quality': recent_avg_quality,
            'previous_avg_quality': previous_avg_quality
        }


class ThinkingOptimizer:
    """사고 과정 최적화기"""
    
    def __init__(self):
        self.optimization_rules = self._initialize_rules()
        
    def _initialize_rules(self) -> Dict[str, Dict[str, Any]]:
        """최적화 규칙 초기화"""
        return {
            'shorts': {
                'min_quality': 70,
                'preferred_patterns': ['실용적', '창의적'],
                'max_thinking_time': 5.0
            },
            'article': {
                'min_quality': 75,
                'preferred_patterns': ['분석적', '종합적'],
                'max_thinking_time': 10.0
            },
            'report': {
                'min_quality': 80,
                'preferred_patterns': ['분석적', '비판적', '종합적'],
                'max_thinking_time': 15.0
            }
        }
    
    def optimize_prompt(self, 
                       content_type: str,
                       base_prompt: str,
                       previous_analysis: Optional[ThinkingAnalysis] = None) -> str:
        """사고 과정 최적화를 위한 프롬프트 개선"""
        
        rules = self.optimization_rules.get(content_type, {})
        optimized_prompt = base_prompt
        
        # 이전 분석 결과가 있으면 활용
        if previous_analysis:
            # 품질이 낮으면 강화
            if previous_analysis.quality_score < rules.get('min_quality', 70):
                optimized_prompt = self._add_quality_enhancement(optimized_prompt)
                
            # 선호 패턴이 부족하면 추가
            preferred = rules.get('preferred_patterns', [])
            missing_patterns = [p for p in preferred if p not in previous_analysis.thinking_patterns]
            if missing_patterns:
                optimized_prompt = self._add_pattern_guidance(optimized_prompt, missing_patterns)
                
            # 약점 보완
            if previous_analysis.weaknesses:
                optimized_prompt = self._add_weakness_correction(
                    optimized_prompt, previous_analysis.weaknesses
                )
                
        return optimized_prompt
    
    def _add_quality_enhancement(self, prompt: str) -> str:
        """품질 향상을 위한 가이드 추가"""
        enhancement = """
<quality_enhancement>
더 깊이 있는 사고를 위해:
- 각 아이디어의 근거를 명확히 제시하세요
- 여러 관점에서 문제를 바라보세요
- 구체적인 예시와 데이터를 활용하세요
- 논리적 연결고리를 강화하세요
</quality_enhancement>

"""
        return enhancement + prompt
    
    def _add_pattern_guidance(self, prompt: str, patterns: List[str]) -> str:
        """특정 사고 패턴 유도"""
        pattern_guides = {
            '분석적': "원인과 결과를 체계적으로 분석하세요",
            '창의적': "기존 방식과 다른 새로운 접근을 시도하세요",
            '비판적': "가정과 한계점을 명확히 지적하세요",
            '실용적': "즉시 실행 가능한 구체적 방안을 제시하세요",
            '종합적': "개별 요소들을 통합하여 전체 그림을 그리세요"
        }
        
        guidance = "\n<pattern_guidance>\n"
        for pattern in patterns:
            if pattern in pattern_guides:
                guidance += f"- {pattern_guides[pattern]}\n"
        guidance += "</pattern_guidance>\n\n"
        
        return guidance + prompt
    
    def _add_weakness_correction(self, prompt: str, weaknesses: List[str]) -> str:
        """약점 보완 가이드 추가"""
        correction = "\n<improvement_focus>\n이전 사고 과정의 개선점:\n"
        for weakness in weaknesses:
            correction += f"- {weakness}\n"
        correction += "</improvement_focus>\n\n"
        
        return correction + prompt