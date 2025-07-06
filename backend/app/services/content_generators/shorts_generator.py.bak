"""
숏츠 스크립트 생성기 - 45-60초 분량의 짧은 영상 스크립트 생성
"""

from typing import List, Dict, Any, Optional
import time
from dataclasses import dataclass
from types import SimpleNamespace

@dataclass
class SubcategoryInfo:
    """서브카테고리 정보"""
    name: str
    description: str
    papers: List[Dict[str, Any]]
    expected_effect: str
    quality_score: float
    quality_grade: str

class ShortsScriptGenerator:
    """YouTube Shorts 스크립트 생성기"""
    
    def __init__(self):
        self.content_type = "shorts"
        
    def generate(self, topic: str, papers: List[Any], 
                 category_id: str = None,
                 additional_context: str = None, **kwargs) -> Any:
        """숏츠 스크립트 생성"""
        
        # GeminiClient import
        from ..gemini_client import GeminiClient, SubcategoryResult, PaperInfo
        
        # additional_context에서 실제 정보 추출
        import json
        context_data = {}
        if additional_context:
            try:
                context_data = json.loads(additional_context)
            except json.JSONDecodeError:
                pass
        
        # SubcategoryResult 객체 생성
        paper_objects = []
        for paper in papers:
            if isinstance(paper, dict):
                paper_objects.append(PaperInfo(
                    title=paper.get('title', 'Unknown Title'),
                    authors=paper.get('authors', 'Unknown Authors'),
                    journal=paper.get('journal', 'Unknown Journal'),
                    year=paper.get('publication_year', paper.get('year', 2024)),
                    doi=paper.get('doi', ''),
                    impact_factor=paper.get('impact_factor', 0.0),
                    citations=paper.get('citations', 0),
                    paper_type=paper.get('paper_type', 'research')
                ))
        
        # 서브카테고리 결과 생성
        subcategory = SubcategoryResult(
            name=topic,
            description=context_data.get('subcategory_description', ''),
            papers=paper_objects,
            expected_effect=context_data.get('expected_effect', ''),
            quality_score=context_data.get('quality_score', 80.0),
            quality_grade=context_data.get('quality_grade', 'B')
        )
        
        # Gemini API를 사용하여 콘텐츠 생성
        gemini_client = GeminiClient()
        result = gemini_client.generate_content(subcategory, 'shorts')
        
        # API가 기대하는 형식으로 반환
        return SimpleNamespace(
            content=result.get('content', ''),
            tone='general',  # 기본 톤
            quality_score=result.get('quality_score', 80.0),
            metadata={
                "content_type": "shorts",
                "topic": topic,
                "papers_used": len(papers),
                "generation_time": time.time()
            }
        )