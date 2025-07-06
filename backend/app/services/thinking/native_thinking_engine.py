"""
Native Thinking Engine - 깊이 있는 사고 과정을 통한 콘텐츠 품질 향상
"""

from typing import Dict, List, Any, Optional, Tuple
import re
import time
from dataclasses import dataclass
from abc import ABC, abstractmethod

@dataclass
class ThinkingResult:
    """사고 과정 결과"""
    original_response: str
    thinking_process: str
    clean_content: str
    thinking_quality_score: float
    thinking_depth: int
    key_insights: List[str]
    decision_points: List[str]
    
class NativeThinkingEngine:
    """Native Thinking 엔진 - Gemini의 <thinking> 태그 활용"""
    
    def __init__(self):
        self.thinking_pattern = r'<thinking>(.*?)</thinking>'
        self.quality_evaluator = ThinkingQualityEvaluator()
        self.insight_extractor = InsightExtractor()
        
    def generate_with_thinking(self, prompt: str, require_thinking: bool = True) -> ThinkingResult:
        """사고 과정을 포함한 응답 생성"""
        # 프롬프트에 thinking 요구사항 추가
        enhanced_prompt = self._enhance_prompt_with_thinking(prompt, require_thinking)
        
        # API 호출 (시뮬레이션)
        response = self._call_gemini_api(enhanced_prompt)
        
        # 사고 과정 추출
        thinking_process, clean_content = self.extract_thinking_process(response)
        
        # 사고 과정이 없으면 재시도
        if require_thinking and not thinking_process:
            response = self._retry_with_explicit_thinking(prompt)
            thinking_process, clean_content = self.extract_thinking_process(response)
        
        # 사고 품질 평가
        quality_score = self.validate_thinking_quality(thinking_process)
        
        # 사고 깊이 측정
        thinking_depth = self._measure_thinking_depth(thinking_process)
        
        # 핵심 인사이트 추출
        key_insights = self.insight_extractor.extract_insights(thinking_process)
        
        # 의사결정 포인트 추출
        decision_points = self._extract_decision_points(thinking_process)
        
        return ThinkingResult(
            original_response=response,
            thinking_process=thinking_process,
            clean_content=clean_content,
            thinking_quality_score=quality_score,
            thinking_depth=thinking_depth,
            key_insights=key_insights,
            decision_points=decision_points
        )
    
    def extract_thinking_process(self, response: str) -> Tuple[str, str]:
        """응답에서 사고 과정 추출"""
        thinking_matches = re.findall(self.thinking_pattern, response, re.DOTALL)
        
        if thinking_matches:
            # 모든 thinking 태그 내용 결합
            thinking_process = '\n\n'.join(thinking_matches)
            
            # thinking 태그 제거한 clean content
            clean_content = re.sub(self.thinking_pattern, '', response, flags=re.DOTALL)
            clean_content = clean_content.strip()
            
            return thinking_process.strip(), clean_content
        
        return "", response
    
    def validate_thinking_quality(self, thinking: str) -> float:
        """사고 과정의 품질 평가"""
        return self.quality_evaluator.evaluate(thinking)
    
    def _enhance_prompt_with_thinking(self, prompt: str, require_thinking: bool) -> str:
        """프롬프트에 사고 과정 요구사항 추가"""
        if not require_thinking:
            return prompt
            
        thinking_instruction = """
<instruction>
응답하기 전에 <thinking> 태그 안에서 다음 사항들을 고려해주세요:
1. 주제의 핵심 문제와 목표 파악
2. 논문 정보의 신뢰성과 적용 가능성 평가
3. 타겟 독자층의 수준과 관심사 고려
4. 콘텐츠 구성의 논리적 흐름 설계
5. 핵심 메시지와 실천 방안 도출

사고 과정은 구체적이고 단계적으로 작성해주세요.
</instruction>

"""
        return thinking_instruction + prompt
    
    def _retry_with_explicit_thinking(self, prompt: str) -> str:
        """명시적으로 사고 과정을 요구하는 재시도"""
        explicit_prompt = f"""
<thinking>
이 주제에 대해 깊이 있게 생각해보겠습니다.
먼저 핵심 문제를 파악하고, 논문 정보를 분석한 후,
최적의 콘텐츠 구성 방안을 도출하겠습니다.
</thinking>

{prompt}
"""
        return self._call_gemini_api(explicit_prompt)
    
    def _measure_thinking_depth(self, thinking: str) -> int:
        """사고 과정의 깊이 측정 (1-5 단계)"""
        if not thinking:
            return 0
            
        # 깊이 지표들
        depth_indicators = {
            'surface': ['간단히', '대략', '요약하면'],
            'basic': ['먼저', '다음으로', '마지막으로'],
            'intermediate': ['분석해보면', '고려하면', '비교하면'],
            'advanced': ['심층적으로', '다각도로', '통합적으로'],
            'expert': ['메타인지적으로', '비판적으로', '체계적으로']
        }
        
        # 사고 과정의 문장 수
        sentences = thinking.split('.')
        sentence_count = len([s for s in sentences if len(s.strip()) > 10])
        
        # 깊이 점수 계산
        depth_score = 1  # 기본 점수
        
        if sentence_count > 5:
            depth_score += 1
        if sentence_count > 10:
            depth_score += 1
            
        # 깊이 지표 확인
        for level, keywords in depth_indicators.items():
            if any(keyword in thinking for keyword in keywords):
                if level == 'intermediate':
                    depth_score = max(depth_score, 3)
                elif level == 'advanced':
                    depth_score = max(depth_score, 4)
                elif level == 'expert':
                    depth_score = 5
                    
        return min(depth_score, 5)
    
    def _extract_decision_points(self, thinking: str) -> List[str]:
        """사고 과정에서 주요 의사결정 포인트 추출"""
        decision_patterns = [
            r'따라서[^.]+\.',
            r'그래서[^.]+\.',
            r'결론적으로[^.]+\.',
            r'선택한 이유는[^.]+\.',
            r'최종적으로[^.]+\.'
        ]
        
        decision_points = []
        for pattern in decision_patterns:
            matches = re.findall(pattern, thinking)
            decision_points.extend(matches)
            
        return list(set(decision_points))  # 중복 제거
    
    def _call_gemini_api(self, prompt: str) -> str:
        """Gemini API 호출 (시뮬레이션)"""
        # 실제 구현에서는 google.genai.Client 사용
        return self._simulate_api_response(prompt)
    
    def _simulate_api_response(self, prompt: str) -> str:
        """API 응답 시뮬레이션"""
        return """
<thinking>
이 주제는 많은 사람들이 관심을 가지는 실용적인 내용입니다.
먼저 논문의 핵심 발견을 파악해보겠습니다:
1. HIIT가 일반 유산소보다 3배 효과적
2. 시간 효율성이 매우 높음
3. EPOC 효과로 운동 후에도 칼로리 소모 지속

타겟 독자층을 고려하면:
- 바쁜 현대인들이 주요 대상
- 실천 가능한 구체적 방법 제시 필요
- 과학적 근거와 실용성의 균형 중요

콘텐츠 구성 전략:
1. 흥미로운 훅으로 시작 (통계나 질문)
2. 논문 근거를 쉽게 풀어서 설명
3. 단계별 실천 가이드 제공
4. 주의사항으로 안전성 확보
5. 동기부여하는 마무리

이러한 구성으로 독자가 즉시 실천할 수 있는 가치 있는 콘텐츠를 만들겠습니다.
</thinking>

실제 콘텐츠 내용이 여기에 들어갑니다...
"""


class ThinkingQualityEvaluator:
    """사고 과정 품질 평가기"""
    
    def evaluate(self, thinking: str) -> float:
        """사고 과정의 품질을 0-100점으로 평가"""
        if not thinking:
            return 0.0
            
        score = 0.0
        
        # 1. 길이 평가 (20점)
        word_count = len(thinking.split())
        if word_count >= 100:
            score += 20
        elif word_count >= 50:
            score += 15
        elif word_count >= 20:
            score += 10
        else:
            score += 5
            
        # 2. 구조화 수준 (20점)
        structure_indicators = ['첫째', '둘째', '1.', '2.', '-', '•']
        structure_count = sum(1 for indicator in structure_indicators if indicator in thinking)
        score += min(structure_count * 5, 20)
        
        # 3. 분석적 사고 (20점)
        analytical_keywords = ['분석', '평가', '비교', '검토', '고려', '판단']
        analytical_count = sum(1 for keyword in analytical_keywords if keyword in thinking)
        score += min(analytical_count * 5, 20)
        
        # 4. 논리적 연결 (20점)
        logical_connectors = ['따라서', '그러므로', '왜냐하면', '때문에', '결과적으로']
        connector_count = sum(1 for connector in logical_connectors if connector in thinking)
        score += min(connector_count * 5, 20)
        
        # 5. 구체성 (20점)
        specific_indicators = ['예를 들어', '구체적으로', '실제로', '%', '분', '개']
        specific_count = sum(1 for indicator in specific_indicators if indicator in thinking)
        score += min(specific_count * 5, 20)
        
        return score


class InsightExtractor:
    """핵심 인사이트 추출기"""
    
    def extract_insights(self, thinking: str) -> List[str]:
        """사고 과정에서 핵심 인사이트 추출"""
        if not thinking:
            return []
            
        insights = []
        
        # 인사이트 패턴
        insight_patterns = [
            r'핵심은[^.]+\.',
            r'중요한 점은[^.]+\.',
            r'주목할 점은[^.]+\.',
            r'발견한 것은[^.]+\.',
            r'알 수 있는 것은[^.]+\.'
        ]
        
        for pattern in insight_patterns:
            matches = re.findall(pattern, thinking)
            insights.extend(matches)
            
        # 문장별 분석으로 추가 인사이트 추출
        sentences = thinking.split('.')
        for sentence in sentences:
            if len(sentence) > 20 and any(keyword in sentence for keyword in ['효과', '결과', '발견', '확인']):
                insights.append(sentence.strip() + '.')
                
        # 중복 제거 및 정제
        unique_insights = []
        for insight in insights:
            if insight not in unique_insights and len(insight) > 10:
                unique_insights.append(insight)
                
        return unique_insights[:5]  # 최대 5개