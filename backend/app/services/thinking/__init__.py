"""
Native Thinking Mode Package
깊이 있는 사고 과정을 통한 콘텐츠 품질 향상
"""

from .native_thinking_engine import (
    NativeThinkingEngine,
    ThinkingResult,
    ThinkingQualityEvaluator,
    InsightExtractor
)

from .prompt_engineering import (
    ThinkingPromptEngineer,
    ContentType,
    ThinkingPatternLibrary
)

from .thinking_analyzer import (
    ThinkingAnalyzer,
    ThinkingAnalysis,
    ThinkingMetrics,
    ThinkingPatternDetector,
    QualityAssessor,
    DepthAnalyzer
)

from .thinking_integration import (
    ThinkingEnabledContentGenerator,
    ThinkingPerformanceMonitor,
    ThinkingOptimizer
)

from .thinking_config import (
    ThinkingConfig,
    ThinkingConfigManager,
    ThinkingPromptTemplates,
    thinking_config_manager
)

__all__ = [
    # Engine
    'NativeThinkingEngine',
    'ThinkingResult',
    'ThinkingQualityEvaluator',
    'InsightExtractor',
    
    # Prompt Engineering
    'ThinkingPromptEngineer',
    'ContentType',
    'ThinkingPatternLibrary',
    
    # Analysis
    'ThinkingAnalyzer',
    'ThinkingAnalysis',
    'ThinkingMetrics',
    'ThinkingPatternDetector',
    'QualityAssessor',
    'DepthAnalyzer',
    
    # Integration
    'ThinkingEnabledContentGenerator',
    'ThinkingPerformanceMonitor',
    'ThinkingOptimizer',
    
    # Configuration
    'ThinkingConfig',
    'ThinkingConfigManager',
    'ThinkingPromptTemplates',
    'thinking_config_manager'
]

# 버전 정보
__version__ = '1.0.0'