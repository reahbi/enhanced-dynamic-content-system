"""
베이스 콘텐츠 생성기 - 모든 콘텐츠 형식의 기본 클래스
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import re
import time

@dataclass
class ContentSection:
    """콘텐츠 섹션"""
    title: str
    content: str
    duration: Optional[int] = None  # 초 단위 (숏츠용)
    word_count: Optional[int] = None  # 글자수 (아티클용)

@dataclass
class GeneratedContent:
    """생성된 콘텐츠"""
    content_type: str
    title: str
    sections: List[ContentSection]
    total_content: str
    metadata: Dict[str, Any]
    thinking_process: str
    generation_time: float
    quality_score: float

class BaseContentGenerator(ABC):
    """콘텐츠 생성기 베이스 클래스"""
    
    def __init__(self):
        self.content_type = "base"
        self.thinking_markers = ["<thinking>", "</thinking>"]
        
    @abstractmethod
    def generate(self, topic: str, papers: List[Any], **kwargs) -> GeneratedContent:
        """콘텐츠 생성 - 서브클래스에서 구현"""
        pass
    
    @abstractmethod
    def create_prompt(self, topic: str, papers: List[Any], **kwargs) -> str:
        """프롬프트 생성 - 서브클래스에서 구현"""
        pass
    
    @abstractmethod
    def parse_response(self, response: str) -> Dict[str, Any]:
        """응답 파싱 - 서브클래스에서 구현"""
        pass
    
    def extract_thinking_process(self, response: str) -> tuple[str, str]:
        """사고 과정 추출"""
        thinking_pattern = r'<thinking>(.*?)</thinking>'
        thinking_matches = re.findall(thinking_pattern, response, re.DOTALL)
        
        if thinking_matches:
            thinking_process = '\n'.join(thinking_matches)
            # 사고 과정 제거한 콘텐츠
            clean_content = re.sub(thinking_pattern, '', response, flags=re.DOTALL)
            return thinking_process.strip(), clean_content.strip()
        
        return "", response
    
    def calculate_quality_score(self, content: str, papers: List[Any]) -> float:
        """콘텐츠 품질 점수 계산"""
        score = 0.0
        
        # 1. 논문 인용 확인 (30점)
        paper_citations = sum(1 for paper in papers if any(
            keyword in content.lower() 
            for keyword in [paper.title.lower()[:20], paper.authors.split()[0].lower()]
        ))
        score += min(paper_citations * 10, 30)
        
        # 2. 구조화 수준 (20점)
        structure_keywords = ['첫째', '둘째', '1.', '2.', '단계', '방법', '팁', '결론']
        structure_count = sum(1 for keyword in structure_keywords if keyword in content)
        score += min(structure_count * 5, 20)
        
        # 3. 실용성 키워드 (20점)
        practical_keywords = ['하는법', '방법', '꿀팁', '주의사항', '추천', '가이드']
        practical_count = sum(1 for keyword in practical_keywords if keyword in content)
        score += min(practical_count * 5, 20)
        
        # 4. 적절한 길이 (15점)
        if self.content_type == "shorts":
            ideal_length = 300  # 45-60초 분량
            length_ratio = min(len(content) / ideal_length, ideal_length / len(content))
            score += length_ratio * 15
        elif self.content_type == "article":
            ideal_length = 2500  # 2000-3000자
            if 2000 <= len(content) <= 3000:
                score += 15
            else:
                score += max(0, 15 - abs(len(content) - ideal_length) / 100)
        
        # 5. 가독성 (15점)
        sentences = content.split('.')
        avg_sentence_length = sum(len(s) for s in sentences) / max(len(sentences), 1)
        if 20 <= avg_sentence_length <= 40:  # 이상적인 문장 길이
            score += 15
        else:
            score += max(0, 15 - abs(avg_sentence_length - 30) / 2)
        
        return min(score, 100)
    
    def format_paper_info(self, papers: List[Any]) -> str:
        """논문 정보 포맷팅"""
        paper_info = []
        for i, paper in enumerate(papers, 1):
            info = f"{i}. {paper.title}\n"
            info += f"   - 저자: {paper.authors}\n"
            info += f"   - 저널: {paper.journal} ({paper.year})\n"
            info += f"   - 주요 발견: {getattr(paper, 'key_findings', 'N/A')}"
            paper_info.append(info)
        
        return "\n\n".join(paper_info)
    
    def apply_tone_and_style(self, content: str, target_audience: str = "general") -> str:
        """타겟 청중에 맞는 톤앤매너 적용"""
        tone_adjustments = {
            "general": {
                "replacements": [
                    ("연구에 따르면", "최신 연구에서 밝혀진 바로는"),
                    ("결과적으로", "그 결과"),
                    ("따라서", "그래서")
                ],
                "prefix": "",
                "suffix": ""
            },
            "beginner": {
                "replacements": [
                    ("유산소 운동", "심장을 뛰게 하는 운동"),
                    ("근력 운동", "근육을 키우는 운동"),
                    ("대사율", "칼로리 소모 속도")
                ],
                "prefix": "💡 초보자도 쉽게 이해할 수 있도록 설명드릴게요!\n\n",
                "suffix": "\n\n🎯 천천히 따라해보세요!"
            },
            "expert": {
                "replacements": [
                    ("효과가 있다", "통계적으로 유의미한 효과가 관찰되었다"),
                    ("증가했다", "유의미한 증가를 보였다"),
                    ("감소했다", "통계적으로 유의한 감소가 나타났다")
                ],
                "prefix": "📊 전문가를 위한 심화 분석\n\n",
                "suffix": "\n\n📈 추가 연구 자료는 참고문헌을 확인하세요."
            }
        }
        
        adjustments = tone_adjustments.get(target_audience, tone_adjustments["general"])
        
        # 치환 적용
        adjusted_content = content
        for old, new in adjustments["replacements"]:
            adjusted_content = adjusted_content.replace(old, new)
        
        # 접두사/접미사 추가
        return adjustments["prefix"] + adjusted_content + adjustments["suffix"]