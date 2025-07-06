import os
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from google import genai
from google.genai import types
import json
import re
import logging
from dotenv import load_dotenv
# Removed CategoryOptimizer as we're not using filtering anymore
from .paper_quality_evaluator import PaperQualityEvaluator, QualityMetrics, PaperInfo as PaperQualityInfo
from .cache_manager import cache_manager
from ..utils.token_tracker import token_tracker

# Configure logging
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

@dataclass
class CategoryResult:
    """Category generation result"""
    name: str
    description: str
    emoji: str
    trend_score: float
    research_activity: float

@dataclass
class PaperInfo:
    """Paper information"""
    title: str
    authors: str
    journal: str
    year: int
    doi: str
    impact_factor: float
    citations: int
    paper_type: str

@dataclass
class SubcategoryResult:
    """Subcategory with paper information"""
    name: str
    description: str
    papers: List[PaperInfo]
    expected_effect: str
    quality_score: float
    quality_grade: str

class GeminiClient:
    """Client for Google Gemini API with Native Thinking Mode support"""
    
    def __init__(self):
        # Configure API
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        # Initialize client with API key
        self.client = genai.Client(api_key=api_key)
        
        # Using Gemini 2.5 Flash for cost optimization
        self.model_name = "gemini-2.5-flash"  # Using Flash model
        
        # Generation config
        self.generation_config = types.GenerateContentConfig(
            temperature=0.9,
            top_p=0.95,
            top_k=40,
            max_output_tokens=8192,
        )
        
        # CategoryOptimizer removed - AI직접 판단 방식으로 변경
        
        # Initialize paper quality evaluator
        self.paper_evaluator = PaperQualityEvaluator()
    
    def generate_categories(self, keyword: str, count: int = 5) -> List[CategoryResult]:
        """Generate practical main categories based on keyword"""
        
        # 캐싱 비활성화 - 매번 새로 생성
        # cache_params = {"keyword": keyword, "count": count}
        # cached_result = cache_manager.get("categories", cache_params)
        # if cached_result:
        #     print(f"캐시 히트: 카테고리 '{keyword}'")
        #     return cached_result
        
        base_prompt = f"""
'{keyword}'과 관련하여 사람들이 관심을 가질만한 **광범위하고 포괄적인 메인카테고리** {count + 3}개를 생성해주세요.
각 카테고리는 여러 세부 주제를 포함할 수 있는 큰 주제여야 합니다.
"""
        
        # 프롬프트 직접 구성 (CategoryOptimizer 제거)
        prompt = base_prompt + f"""
<thinking>
메인카테고리는 광범위한 주제를 다루어야 한다.
너무 구체적이거나 좁은 주제가 아닌, 여러 서브카테고리를 포함할 수 있는 큰 틀이어야 한다.

좋은 예시 (운동 키워드의 경우):
- 💪 효율적인 운동 방법론
- 🥗 운동과 영양 최적화
- 🏋️ 근력운동 완벽 가이드
- 🏃 유산소운동 마스터하기
- 🧘 몸과 마음의 균형 운동

나쁜 예시 (너무 구체적):
- 5분 복근운동 루틴
- 거북목 해결 스트레칭
- 30일 스쿼트 챌린지
- 아침 10분 운동법
</thinking>

카테고리 생성 규칙:
1. 포괄적이고 광범위한 주제로 생성
2. 여러 세부 주제를 포함할 수 있는 큰 카테고리
3. 특정 운동이나 시간대가 아닌 전반적인 영역을 다루기
4. 학문적 깊이가 있는 주제 선정
5. 이모지로 카테고리 특성 표현

JSON 형식으로 응답해주세요:
{{
  "categories": [
    {{
      "name": "포괄적인 카테고리명",
      "description": "카테고리가 다루는 범위에 대한 설명",
      "emoji": "관련 이모지",
      "trend_score": 8.5,  // 현재 트렌드 점수 (1-10)
      "research_activity": 7.0  // 연구 활발도 (1-10)
    }}
  ]
}}

예시 (운동 키워드):
- "💪 효율적인 운동 방법론" - 운동의 원리, 계획, 기법 등을 포괄
- "🥗 운동과 영양 최적화" - 영양학, 보충제, 식단 계획 등을 포괄
- "🏋️ 근력운동 완벽 가이드" - 웨이트, 맨몸운동, 기구운동 등을 포괄
- "🏃 유산소운동 마스터하기" - 달리기, 수영, 사이클 등을 포괄
- "🧘 몸과 마음의 균형 운동" - 요가, 필라테스, 명상 등을 포괄
"""
        
        # 재시도 로직 (응답 시간 단축을 위해 2회로 축소)
        max_attempts = 2
        for attempt in range(max_attempts):
            try:
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=prompt,
                    config=self.generation_config
                )
                
                # Log token usage
                if hasattr(response, 'usage_metadata'):
                    usage = response.usage_metadata
                    logger.info(f"[Gemini API - generate_categories] Token usage: "
                               f"prompt_tokens={usage.prompt_token_count}, "
                               f"response_tokens={usage.candidates_token_count}, "
                               f"total_tokens={usage.total_token_count}")
                    token_tracker.add_usage(
                        "generate_categories",
                        usage.prompt_token_count,
                        usage.candidates_token_count,
                        usage.total_token_count
                    )
                else:
                    logger.warning("[Gemini API - generate_categories] No token usage metadata available")
                
                # Parse JSON response
                text = response.text
                json_match = re.search(r'\{.*\}', text, re.DOTALL)
                if json_match:
                    data = json.loads(json_match.group())
                    raw_categories = []
                    
                    for cat in data.get("categories", []):
                        raw_categories.append({
                            "name": cat["name"],
                            "description": cat["description"],
                            "emoji": cat["emoji"],
                            "trend_score": float(cat.get("trend_score", 7.0)),
                            "research_activity": float(cat.get("research_activity", 7.0))
                        })
                    
                    # AI가 생성한 카테고리를 그대로 사용 (필터링 없음)
                    result_categories = []
                    for cat in raw_categories[:count]:  # 요청한 개수만큼만 사용
                        result_categories.append(CategoryResult(
                            name=cat["name"],
                            description=cat["description"],
                            emoji=cat["emoji"],
                            trend_score=cat["trend_score"],
                            research_activity=cat["research_activity"]
                        ))
                    
                    if len(result_categories) >= count:
                        return result_categories[:count]
                    
            except Exception as e:
                print(f"카테고리 생성 오류 (시도 {attempt + 1}): {e}")
                if attempt == max_attempts - 1:
                    print(f"응답 텍스트: {text if 'text' in locals() else 'N/A'}")
                    # 모든 시도 실패시 에러 발생
                    raise Exception(f"카테고리 생성에 실패했습니다. 다시 시도해주세요. (오류: {str(e)})")
    
    def evaluate_practicality(self, category: str) -> float:
        """Evaluate practicality score of a category - AI 직접 평가로 변경"""
        
        # AI가 이미 평가한 점수를 그대로 사용
        return 8.0  # 기본값 반환 (AI가 이미 trend_score, research_activity로 평가함)
    
    def discover_papers_for_topic(self, category: str, subcategory_topic: str) -> Optional[SubcategoryResult]:
        """Discover papers and generate subcategory information"""
        
        prompt = f"""
<thinking>
카테고리: {category}
주제: {subcategory_topic}

이 주제에 대한 실제 학술 논문을 찾고, 논문 기반으로 서브카테고리를 생성해야 한다.
논문이 존재하지 않는 주제라면 null을 반환해야 한다.
</thinking>

"{category}" 카테고리의 "{subcategory_topic}" 주제에 대해:

1. 관련된 실제 학술 논문을 1-3개 찾아주세요
2. 논문 정보를 기반으로 매력적인 서브카테고리를 생성해주세요
3. 기대 효과를 구체적으로 설명해주세요

**중요**: 실제로 존재하는 논문만 제시해야 합니다. 논문을 찾을 수 없다면 null을 반환하세요.

JSON 형식으로 응답해주세요:
{{
  "subcategory": {{
    "name": "매력적인 서브카테고리 제목",
    "description": "논문 기반 설명",
    "papers": [
      {{
        "title": "논문 제목",
        "authors": "저자명 et al.",
        "journal": "저널명",
        "year": 2020,
        "doi": "10.xxxx/xxxxx",
        "impact_factor": 5.2,
        "citations": 150,
        "paper_type": "Systematic Review"
      }}
    ],
    "expected_effect": "구체적인 기대 효과",
    "quality_score": 75.5,
    "quality_grade": "A"
  }}
}} 

또는 논문이 없으면: null
"""
        
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=prompt,
            config=self.generation_config
        )
        
        # Log token usage
        if hasattr(response, 'usage_metadata'):
            usage = response.usage_metadata
            logger.info(f"[Gemini API - discover_papers_for_topic] Token usage: "
                       f"prompt_tokens={usage.prompt_token_count}, "
                       f"response_tokens={usage.candidates_token_count}, "
                       f"total_tokens={usage.total_token_count}")
            token_tracker.add_usage(
                "discover_papers_for_topic",
                usage.prompt_token_count,
                usage.candidates_token_count,
                usage.total_token_count
            )
        else:
            logger.warning("[Gemini API - discover_papers_for_topic] No token usage metadata available")
        
        try:
            text = response.text.strip()
            
            # Check for null or no paper indicators
            if "null" in text.lower() or "논문이 없" in text or "찾을 수 없" in text:
                return None
            
            # Parse JSON
            json_match = re.search(r'\{.*\}', text, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
                sub = data.get("subcategory")
                if sub and sub.get("papers"):
                    papers = []
                    for p in sub["papers"]:
                        papers.append(PaperInfo(
                            title=p["title"],
                            authors=p["authors"],
                            journal=p["journal"],
                            year=p["year"],
                            doi=p["doi"],
                            impact_factor=p.get("impact_factor", 3.0),
                            citations=p.get("citations", 50),
                            paper_type=p.get("paper_type", "Research Article")
                        ))
                    
                    # 논문 품질 평가
                    paper_quality_infos = []
                    for p in papers:
                        paper_quality_infos.append(PaperQualityInfo(
                            title=p.title,
                            authors=p.authors,
                            journal=p.journal,
                            year=p.year,
                            doi=p.doi,
                            impact_factor=p.impact_factor,
                            citations=p.citations,
                            paper_type=p.paper_type
                        ))
                    
                    # 논문 세트 평가
                    evaluation_result = self.paper_evaluator.evaluate_paper_set(paper_quality_infos)
                    
                    return SubcategoryResult(
                        name=sub["name"],
                        description=sub["description"],
                        papers=papers,
                        expected_effect=sub["expected_effect"],
                        quality_score=evaluation_result["average_score"],
                        quality_grade=evaluation_result["average_grade"]
                    )
        except Exception as e:
            print(f"Error parsing subcategory: {e}")
            print(f"Response: {text}")
        
        return None
    
    def generate_content(self, subcategory: SubcategoryResult, content_type: str) -> Dict[str, Any]:
        """Generate content based on paper-backed subcategory"""
        
        # Prepare paper information
        paper_info = "\n".join([
            f"- {p.title} ({p.authors}, {p.journal}, {p.year})"
            for p in subcategory.papers
        ])
        
        if content_type == "shorts":
            prompt = f"""
<thinking>
서브카테고리: {subcategory.name}
논문 정보: {paper_info}
기대 효과: {subcategory.expected_effect}

45-60초 분량의 숏츠 스크립트를 작성해야 한다.
논문의 핵심 내용을 쉽고 재미있게 전달해야 한다.
네이버 블로그에 복사 가능한 HTML 형식으로 작성해야 한다.
</thinking>

다음 논문들을 기반으로 45-60초 YouTube Shorts 스크립트를 HTML 형식으로 작성해주세요:

제목: {subcategory.name}
논문:
{paper_info}

스크립트 구성:
1. 훅 (0-5초): 시선을 끄는 질문이나 사실
2. 문제 제기 (5-15초): 왜 중요한지
3. 해결책 (15-40초): 논문 기반 핵심 내용
4. 실천 방법 (40-50초): 구체적인 행동 지침
5. 마무리 (50-60초): 핵심 메시지 요약

[작성 스타일]
- 친근하고 대화하듯 자연스러운 어조로 작성
- "안녕하세요!", "~하시나요?", "~해보세요!" 등 친근한 표현 사용
- 이모지를 적절히 활용하여 시각적 재미 추가
- 전문 용어는 쉽게 풀어서 설명

[HTML 형식 요구사항]
- 모든 스타일은 인라인 style 속성 사용
- 타임라인은 표 형식으로 제공:
  <table style="border-collapse: collapse; width: 100%; margin: 20px 0;">
- 각 섹션은 배경색이 있는 div로 구분:
  <div style="background-color: #f0f8ff; padding: 15px; margin: 10px 0; border-radius: 8px;">
- 중요한 내용은 <strong> 태그로 강조
- 글자 크기: <span style="font-size: 18px;">
"""
        
        elif content_type == "article":
            prompt = f"""
<thinking>
서브카테고리: {subcategory.name}
논문 정보: {paper_info}
기대 효과: {subcategory.expected_effect}

2000-3000자 분량의 상세 아티클을 작성해야 한다.
논문의 내용을 깊이 있게 다루면서도 일반인이 이해하기 쉽게 설명해야 한다.
</thinking>

다음 논문들을 기반으로 네이버 블로그 스타일의 상세 아티클을 작성해주세요:

제목: {subcategory.name}
논문:
{paper_info}

아티클 구성:
1. 도입부: 주제의 중요성과 배경
2. 연구 내용: 논문의 핵심 발견
3. 과학적 원리: 작동 메커니즘 설명
4. 실용적 적용: 일상에서의 활용법
5. 주의사항: 고려해야 할 점들
6. 결론: 핵심 메시지와 실천 방안

[작성 스타일]
- 네이버 블로그처럼 친근하고 읽기 쉬운 어조
- "안녕하세요!", "오늘은 ~에 대해 알아보겠습니다" 등으로 시작
- 독자를 '여러분'으로 지칭하며 대화하듯 설명
- 💡 팁박스, ⚠️ 주의사항, ✅ 체크포인트 등을 활용
- 중요한 내용은 **굵게** 표시하거나 ~~형광펜~~ 효과 사용
- 복잡한 내용은 예시를 들어 쉽게 설명
- 문단은 짧게 나누어 가독성 향상
- 전문 용어 사용 시 괄호로 쉬운 설명 추가

2000-3000자로 작성하세요.
"""
        
        else:  # report
            prompt = f"""
<thinking>
서브카테고리: {subcategory.name}
논문 정보: {paper_info}
기대 효과: {subcategory.expected_effect}

종합 리포트를 작성해야 한다.
여러 논문의 내용을 종합하여 깊이 있는 분석을 제공해야 한다.
</thinking>

다음 논문들을 기반으로 네이버 블로그 스타일의 종합 리포트를 작성해주세요:

제목: {subcategory.name}
논문:
{paper_info}

리포트 구성:
1. 요약 (Executive Summary)
2. 연구 배경 및 목적
3. 주요 연구 결과 분석
4. 논문별 비교 분석
5. 실무 적용 가이드
6. 향후 연구 방향
7. 참고문헌

[작성 스타일]
- 전문성을 유지하되 네이버 블로그의 친근한 어조 활용
- "안녕하세요! 오늘은 ~에 대한 종합 리포트를 준비했습니다" 형식으로 시작
- 각 섹션 시작 시 "## 제목" 형식 사용 (큰 제목)
- 중요 수치나 결과는 **굵게** 강조
- 복잡한 표는 간단하게 정리하여 제시
- 💡 핵심 포인트, ⚠️ 주의사항, ✅ 실천 가이드 등 시각적 요소 활용
- 전문 용어는 처음 사용 시 쉬운 설명 병기
- 긴 문단은 2-3개 문장으로 나누어 가독성 향상
- 마무리에는 독자에게 도움이 되는 실용적 조언 포함

전문적이면서도 읽기 쉽게 작성하세요.
"""
        
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=prompt,
            config=self.generation_config
        )
        
        # Log token usage
        if hasattr(response, 'usage_metadata'):
            usage = response.usage_metadata
            logger.info(f"[Gemini API - generate_content ({content_type})] Token usage: "
                       f"prompt_tokens={usage.prompt_token_count}, "
                       f"response_tokens={usage.candidates_token_count}, "
                       f"total_tokens={usage.total_token_count}")
            token_tracker.add_usage(
                f"generate_content_{content_type}",
                usage.prompt_token_count,
                usage.candidates_token_count,
                usage.total_token_count
            )
        else:
            logger.warning(f"[Gemini API - generate_content ({content_type})] No token usage metadata available")
        
        return {
            "content_type": content_type,
            "content": response.text,
            "subcategory": subcategory.name,
            "papers_used": len(subcategory.papers),
            "quality_score": subcategory.quality_score
        }
    
    async def generate_subcategory_topics(self, category_name: str, count: int = 5) -> List[str]:
        """카테고리에 대한 서브카테고리 주제 생성"""
        
        prompt = f"""
<thinking>
카테고리: {category_name}
이 카테고리에 대해 사람들이 가장 관심을 가질 만한 구체적인 주제를 생성해야 한다.
각 주제는 실제 학술 논문이 존재할 가능성이 높은 것들이어야 한다.
</thinking>

"{category_name}" 카테고리에 대해 사람들이 가장 궁금해하는 구체적인 세부 주제 {count + 2}개를 생성해주세요.

요구사항:
1. 각 주제는 구체적이고 실용적이어야 함
2. 학술 논문이 존재할 가능성이 높은 주제
3. 사람들이 즉시 관심을 가질 만한 주제

JSON 형식으로 응답:
{{
  "topics": [
    "구체적인 주제 1",
    "구체적인 주제 2",
    ...
  ]
}}

예시:
- "벤치프레스 각도별 효과"
- "스쿼트 자세와 무릎 부상의 관계"
- "단백질 섭취 타이밍과 근성장"
"""
        
        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=self.generation_config
            )
            
            # Log token usage
            if hasattr(response, 'usage_metadata'):
                usage = response.usage_metadata
                logger.info(f"[Gemini API - generate_subcategory_topics] Token usage: "
                           f"prompt_tokens={usage.prompt_token_count}, "
                           f"response_tokens={usage.candidates_token_count}, "
                           f"total_tokens={usage.total_token_count}")
                token_tracker.add_usage(
                    "generate_subcategory_topics",
                    usage.prompt_token_count,
                    usage.candidates_token_count,
                    usage.total_token_count
                )
            else:
                logger.warning("[Gemini API - generate_subcategory_topics] No token usage metadata available")
            
            text = response.text
            json_match = re.search(r'\{.*\}', text, re.DOTALL)
            
            if json_match:
                data = json.loads(json_match.group())
                topics = data.get("topics", [])[:count]
                return topics
                
        except Exception as e:
            print(f"서브카테고리 주제 생성 오류: {e}")
        
        # 기본 주제 반환
        base_topics = [
            "효과적인 방법",
            "초보자 가이드",
            "고급 테크닉",
            "흔한 실수와 해결법",
            "과학적 원리"
        ]
        return base_topics[:count]