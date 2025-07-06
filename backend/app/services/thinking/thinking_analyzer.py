"""
사고 과정 분석기 - 사고의 품질과 깊이를 측정하고 개선점 제시
"""

from typing import Dict, List, Any, Optional, Tuple
import re
import json
from dataclasses import dataclass
from datetime import datetime
from collections import Counter

@dataclass
class ThinkingAnalysis:
    """사고 과정 분석 결과"""
    quality_score: float
    depth_level: int
    thinking_patterns: List[str]
    strengths: List[str]
    weaknesses: List[str]
    improvement_suggestions: List[str]
    metrics: Dict[str, Any]

@dataclass
class ThinkingMetrics:
    """사고 과정 측정 지표"""
    word_count: int
    sentence_count: int
    avg_sentence_length: float
    complexity_score: float
    logical_connectors: int
    analytical_terms: int
    decision_points: int
    evidence_references: int

class ThinkingAnalyzer:
    """사고 과정 분석기"""
    
    def __init__(self):
        self.pattern_detector = ThinkingPatternDetector()
        self.quality_assessor = QualityAssessor()
        self.depth_analyzer = DepthAnalyzer()
        
    def analyze(self, thinking_process: str) -> ThinkingAnalysis:
        """사고 과정 종합 분석"""
        if not thinking_process:
            return self._empty_analysis()
            
        # 기본 메트릭 계산
        metrics = self._calculate_metrics(thinking_process)
        
        # 패턴 감지
        patterns = self.pattern_detector.detect_patterns(thinking_process)
        
        # 품질 평가
        quality_score = self.quality_assessor.assess(thinking_process, metrics)
        
        # 깊이 분석
        depth_level = self.depth_analyzer.analyze_depth(thinking_process, metrics)
        
        # 강점과 약점 분석
        strengths, weaknesses = self._analyze_strengths_weaknesses(
            thinking_process, metrics, patterns
        )
        
        # 개선 제안
        suggestions = self._generate_suggestions(weaknesses, metrics)
        
        return ThinkingAnalysis(
            quality_score=quality_score,
            depth_level=depth_level,
            thinking_patterns=patterns,
            strengths=strengths,
            weaknesses=weaknesses,
            improvement_suggestions=suggestions,
            metrics=vars(metrics)
        )
    
    def _calculate_metrics(self, thinking: str) -> ThinkingMetrics:
        """사고 과정의 기본 메트릭 계산"""
        words = thinking.split()
        sentences = [s.strip() for s in re.split(r'[.!?]', thinking) if s.strip()]
        
        word_count = len(words)
        sentence_count = len(sentences)
        avg_sentence_length = word_count / max(sentence_count, 1)
        
        # 복잡도 점수 계산
        complexity_score = self._calculate_complexity(thinking)
        
        # 논리적 연결어 계수
        logical_connectors = self._count_logical_connectors(thinking)
        
        # 분석적 용어 계수
        analytical_terms = self._count_analytical_terms(thinking)
        
        # 의사결정 포인트 계수
        decision_points = self._count_decision_points(thinking)
        
        # 근거 참조 계수
        evidence_references = self._count_evidence_references(thinking)
        
        return ThinkingMetrics(
            word_count=word_count,
            sentence_count=sentence_count,
            avg_sentence_length=avg_sentence_length,
            complexity_score=complexity_score,
            logical_connectors=logical_connectors,
            analytical_terms=analytical_terms,
            decision_points=decision_points,
            evidence_references=evidence_references
        )
    
    def _calculate_complexity(self, thinking: str) -> float:
        """텍스트 복잡도 계산"""
        # 문장 길이 다양성
        sentences = [s.strip() for s in re.split(r'[.!?]', thinking) if s.strip()]
        if not sentences:
            return 0.0
            
        sentence_lengths = [len(s.split()) for s in sentences]
        length_variance = self._variance(sentence_lengths)
        
        # 어휘 다양성 (Type-Token Ratio)
        words = thinking.lower().split()
        unique_words = set(words)
        ttr = len(unique_words) / max(len(words), 1)
        
        # 복잡도 점수 (0-100)
        complexity = (length_variance * 0.3 + ttr * 100 * 0.7)
        return min(complexity, 100)
    
    def _variance(self, numbers: List[float]) -> float:
        """분산 계산"""
        if not numbers:
            return 0.0
        mean = sum(numbers) / len(numbers)
        return sum((x - mean) ** 2 for x in numbers) / len(numbers)
    
    def _count_logical_connectors(self, thinking: str) -> int:
        """논리적 연결어 계수"""
        connectors = [
            '따라서', '그러므로', '왜냐하면', '때문에', '그래서',
            '하지만', '그러나', '반면', '또한', '게다가',
            '즉', '다시 말해', '예를 들어', '구체적으로', '특히'
        ]
        count = sum(1 for connector in connectors if connector in thinking)
        return count
    
    def _count_analytical_terms(self, thinking: str) -> int:
        """분석적 용어 계수"""
        analytical_terms = [
            '분석', '평가', '검토', '비교', '대조', '검증',
            '추론', '판단', '해석', '종합', '통합', '도출',
            '고려', '탐색', '조사', '확인', '파악', '이해'
        ]
        count = sum(1 for term in analytical_terms if term in thinking)
        return count
    
    def _count_decision_points(self, thinking: str) -> int:
        """의사결정 포인트 계수"""
        decision_patterns = [
            r'선택했다', r'결정했다', r'판단했다',
            r'하기로 했다', r'것이 좋겠다', r'것이 적절하다'
        ]
        count = 0
        for pattern in decision_patterns:
            count += len(re.findall(pattern, thinking))
        return count
    
    def _count_evidence_references(self, thinking: str) -> int:
        """근거 참조 계수"""
        evidence_patterns = [
            r'연구에 따르면', r'논문에서', r'데이터를 보면',
            r'통계상', r'결과적으로', r'실험 결과'
        ]
        count = 0
        for pattern in evidence_patterns:
            count += len(re.findall(pattern, thinking))
        return count
    
    def _analyze_strengths_weaknesses(self, 
                                    thinking: str, 
                                    metrics: ThinkingMetrics,
                                    patterns: List[str]) -> Tuple[List[str], List[str]]:
        """강점과 약점 분석"""
        strengths = []
        weaknesses = []
        
        # 강점 분석
        if metrics.word_count > 100:
            strengths.append("충분한 사고 과정 전개")
        if metrics.logical_connectors > 5:
            strengths.append("논리적 연결성 우수")
        if metrics.analytical_terms > 5:
            strengths.append("분석적 접근 활용")
        if metrics.evidence_references > 2:
            strengths.append("근거 기반 사고")
        if len(patterns) > 2:
            strengths.append("다양한 사고 패턴 활용")
            
        # 약점 분석
        if metrics.word_count < 50:
            weaknesses.append("사고 과정이 너무 간략함")
        if metrics.logical_connectors < 2:
            weaknesses.append("논리적 연결 부족")
        if metrics.analytical_terms < 2:
            weaknesses.append("분석적 깊이 부족")
        if metrics.evidence_references == 0:
            weaknesses.append("근거 제시 부재")
        if metrics.avg_sentence_length > 30:
            weaknesses.append("문장이 너무 길고 복잡함")
            
        return strengths, weaknesses
    
    def _generate_suggestions(self, weaknesses: List[str], metrics: ThinkingMetrics) -> List[str]:
        """개선 제안 생성"""
        suggestions = []
        
        weakness_to_suggestion = {
            "사고 과정이 너무 간략함": "각 단계별로 더 구체적인 설명을 추가하세요",
            "논리적 연결 부족": "'따라서', '왜냐하면' 등의 연결어를 활용하세요",
            "분석적 깊이 부족": "원인, 영향, 대안 등을 체계적으로 분석하세요",
            "근거 제시 부재": "논문이나 데이터를 인용하여 주장을 뒷받침하세요",
            "문장이 너무 길고 복잡함": "한 문장에 하나의 아이디어만 담도록 분리하세요"
        }
        
        for weakness in weaknesses:
            if weakness in weakness_to_suggestion:
                suggestions.append(weakness_to_suggestion[weakness])
                
        # 추가 제안
        if metrics.decision_points < 2:
            suggestions.append("의사결정 과정을 더 명확히 표현하세요")
        if metrics.complexity_score < 30:
            suggestions.append("더 다양한 어휘와 문장 구조를 사용하세요")
            
        return suggestions
    
    def _empty_analysis(self) -> ThinkingAnalysis:
        """빈 분석 결과"""
        return ThinkingAnalysis(
            quality_score=0.0,
            depth_level=0,
            thinking_patterns=[],
            strengths=[],
            weaknesses=["사고 과정이 없음"],
            improvement_suggestions=["사고 과정을 추가하세요"],
            metrics={}
        )


class ThinkingPatternDetector:
    """사고 패턴 감지기"""
    
    def __init__(self):
        self.patterns = {
            "분석적": ["분석", "평가", "비교", "검토", "원인", "결과"],
            "창의적": ["만약", "새로운", "독특한", "혁신적", "아이디어"],
            "비판적": ["문제점", "한계", "단점", "개선", "보완"],
            "실용적": ["적용", "실천", "활용", "구체적", "방법"],
            "종합적": ["전체적", "통합", "종합", "연결", "관계"]
        }
        
    def detect_patterns(self, thinking: str) -> List[str]:
        """사고 패턴 감지"""
        detected_patterns = []
        
        for pattern_name, keywords in self.patterns.items():
            keyword_count = sum(1 for keyword in keywords if keyword in thinking)
            if keyword_count >= 2:  # 2개 이상의 키워드가 있으면 해당 패턴으로 판단
                detected_patterns.append(pattern_name)
                
        return detected_patterns


class QualityAssessor:
    """품질 평가기"""
    
    def assess(self, thinking: str, metrics: ThinkingMetrics) -> float:
        """사고 과정 품질 평가 (0-100점)"""
        score = 0.0
        
        # 1. 길이 평가 (20점)
        if metrics.word_count >= 150:
            score += 20
        elif metrics.word_count >= 100:
            score += 15
        elif metrics.word_count >= 50:
            score += 10
        else:
            score += 5
            
        # 2. 논리성 평가 (20점)
        logical_score = min(metrics.logical_connectors * 4, 20)
        score += logical_score
        
        # 3. 분석성 평가 (20점)
        analytical_score = min(metrics.analytical_terms * 3, 20)
        score += analytical_score
        
        # 4. 근거성 평가 (20점)
        evidence_score = min(metrics.evidence_references * 5, 20)
        score += evidence_score
        
        # 5. 복잡도 평가 (20점)
        if 40 <= metrics.complexity_score <= 70:
            score += 20
        elif 30 <= metrics.complexity_score < 40 or 70 < metrics.complexity_score <= 80:
            score += 15
        else:
            score += 10
            
        return score


class DepthAnalyzer:
    """사고 깊이 분석기"""
    
    def analyze_depth(self, thinking: str, metrics: ThinkingMetrics) -> int:
        """사고 깊이 분석 (1-5 레벨)"""
        depth_score = 1
        
        # 레벨 2: 기본적 구조화
        if metrics.sentence_count >= 5 and metrics.logical_connectors >= 2:
            depth_score = 2
            
        # 레벨 3: 분석적 사고
        if metrics.analytical_terms >= 3 and metrics.decision_points >= 2:
            depth_score = 3
            
        # 레벨 4: 근거 기반 심화 분석
        if metrics.evidence_references >= 2 and metrics.complexity_score >= 50:
            depth_score = 4
            
        # 레벨 5: 통합적 고차원 사고
        if (metrics.word_count >= 200 and 
            metrics.analytical_terms >= 5 and 
            metrics.evidence_references >= 3 and
            metrics.logical_connectors >= 5):
            depth_score = 5
            
        return depth_score