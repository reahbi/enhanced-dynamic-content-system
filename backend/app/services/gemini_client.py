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
        logger.info(f"Initialized GeminiClient with model: {self.model_name}")
        
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
국제 학술지의 영어 논문을 우선적으로 찾아야 한다.
하지만 서브카테고리 제목과 설명은 한국어로 일반인이 이해하기 쉽게 작성해야 한다.
</thinking>

"{category}" 카테고리의 "{subcategory_topic}" 주제에 대해:

1. 관련된 실제 학술 논문을 1-3개 찾아주세요 (영어 논문)
2. 논문 정보를 기반으로 매력적인 서브카테고리를 생성해주세요
   - 서브카테고리 제목은 반드시 한국어로 작성하세요
   - 일반 운동 애호가가 흥미를 느낄 수 있는 쉽고 친근한 제목을 만드세요
   - 학술적이거나 전문적인 용어는 피하고, 실용적이고 흥미로운 표현을 사용하세요
3. 기대 효과를 구체적으로 설명해주세요 (한국어로)

**중요 요구사항**:
- 실제로 존재하는 논문만 제시해야 합니다
- 국제 학술 데이터베이스(PubMed, Scopus, Web of Science 등)에 등재된 영어 논문을 우선적으로 찾아주세요
- High-impact factor를 가진 저명한 국제 저널의 논문을 선호합니다
- 논문 제목과 저널명은 영어로 제공해주세요
- 한국어 저널이나 한국어로 작성된 논문은 절대 포함하지 마세요
- 반드시 영어로 작성된 국제 논문만 포함하세요
- DOI는 국제 표준인 10.으로 시작해야 합니다
- Impact Factor가 명시된 국제 저널의 논문을 우선시하세요
- 논문을 찾을 수 없다면 null을 반환하세요

JSON 형식으로 응답해주세요:
{{
  "subcategory": {{
    "name": "일반인이 이해하기 쉬운 한국어 서브카테고리 제목 (예: '스마트워치로 확인하는 내 몸 상태')",
    "description": "논문 기반 설명 (한국어로 쉽게 풀어서)",
    "papers": [
      {{
        "title": "Effects of High-Intensity Interval Training on Cardiovascular Function: A Systematic Review and Meta-Analysis",
        "authors": "Johnson AB, Smith CD, Williams EF et al.",
        "journal": "Journal of Applied Physiology",
        "year": 2023,
        "doi": "10.1152/japplphysiol.00384.2023",
        "impact_factor": 5.2,
        "citations": 150,
        "paper_type": "Systematic Review"
      }}
    ],
    "expected_effect": "구체적인 기대 효과 (한국어로 일반인이 이해하기 쉽게)",
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
            # Shorts 생성은 현재 지원하지 않음
            raise NotImplementedError("Shorts 콘텐츠 생성은 현재 지원하지 않습니다.")
        
        elif content_type == "article":
            prompt = f"""
<thinking>
서브카테고리: {subcategory.name}
논문 정보: {paper_info}
기대 효과: {subcategory.expected_effect}

2000-3000자 분량의 상세 아티클을 작성해야 한다.
논문의 내용을 깊이 있게 다루면서도 일반인이 이해하기 쉽게 설명해야 한다.
네이버 블로그에 복사 가능한 HTML 형식으로 작성해야 한다.
참조된 논문들은 모두 국제 저널에 발표된 영어 논문들이다.
</thinking>

다음 국제 학술지 논문들을 기반으로 네이버 블로그 스타일의 상세 아티클을 HTML 형식으로 작성해주세요:

제목: {subcategory.name}
참조 논문 (모두 영어로 작성된 국제 저널 논문):
{paper_info}

아티클 구성 (더 친근하고 실용적으로):
1. 🎯 이게 뭔가요? - 오늘의 주제를 쉽게 소개
2. 🤔 왜 이게 중요한가요? - 일상 생활과의 연관성
3. 🔬 과학이 밝혀낸 놀라운 사실들 - 연구 결과를 쉽게 풀어서
4. 💪 실전! 이렇게 해보세요 - 구체적인 실천 방법
5. 🌟 성공 꿀팁 - 더 효과적으로 하는 방법
6. ⚠️ 이것만은 주의하세요 - 안전하게 실천하기
7. ❓ 자주 묻는 질문들 - Q&A 형식
8. 📌 오늘의 핵심 정리 - 꼭 기억해야 할 것들

[작성 스타일]
- 네이버 블로그처럼 친근하고 읽기 쉬운 어조
- "안녕하세요!", "오늘은 ~에 대해 알아보겠습니다" 등으로 시작
- 독자를 '여러분'으로 지칭하며 대화하듯 설명
- 어려운 용어는 쉽게 풀어서 설명 (예: "인슐린 저항성" → "몸이 인슐린에 잘 반응하지 않는 상태")
- 논문은 자연스럽게 언급 (예: "최근 연구에 따르면~", "전문가들이 발견한 바로는~")
- 실제 경험담처럼 작성 (예: "많은 분들이 이렇게 하시더라고요~")
- 질문을 던지며 독자 참여 유도 (예: "혹시 이런 경험 있으신가요?")
- 각 섹션은 짧은 단락으로 구성해서 읽기 편하게

[HTML 형식 요구사항]
- 모든 스타일은 인라인 style 속성 사용
- 제목: <h2 style="color: #333; font-size: 24px; margin: 20px 0;">
- 팁박스: <div style="background-color: #e3f2fd; border-left: 4px solid #2196F3; padding: 15px; margin: 20px 0;">
  <strong>💡 팁:</strong> 내용
</div>
- 주의사항: <div style="background-color: #fff3cd; border: 1px solid #ffeaa7; border-radius: 4px; padding: 15px; margin: 20px 0;">
  <strong>⚠️ 주의사항:</strong> 내용
</div>
- 체크포인트: <div style="background-color: #d4edda; border: 1px solid #c3e6cb; border-radius: 4px; padding: 15px; margin: 20px 0;">
  <strong>✅ 체크포인트:</strong> 내용
</div>
- Q&A 박스: <div style="background-color: #f8f9fa; border-left: 4px solid #6c757d; padding: 15px; margin: 20px 0;">
  <strong>Q:</strong> 질문 내용<br>
  <strong>A:</strong> 답변 내용
</div>
- 핵심 정리: <div style="background-color: #ffe5e5; border: 2px dashed #ff6b6b; border-radius: 8px; padding: 20px; margin: 30px 0;">
  <h3 style="color: #ff6b6b; margin-top: 0;">📌 핵심 포인트</h3>
  <ul style="margin: 10px 0; padding-left: 20px;">
    <li>첫 번째 핵심</li>
    <li>두 번째 핵심</li>
  </ul>
</div>
- 실천 체크리스트: <div style="background-color: #f0f4ff; border: 1px solid #4a69bd; border-radius: 8px; padding: 20px; margin: 20px 0;">
  <h3 style="color: #4a69bd; margin-top: 0;">✔️ 실천 체크리스트</h3>
  <div style="margin: 10px 0;">
    <input type="checkbox" style="margin-right: 8px;">첫 번째 할 일<br>
    <input type="checkbox" style="margin-right: 8px;">두 번째 할 일<br>
  </div>
</div>
- 경험담 박스: <div style="background-color: #fef9e7; border-left: 4px solid #f9ca24; padding: 15px; margin: 20px 0; font-style: italic;">
  "실제로 이렇게 해보니..." 형식의 경험담
</div>
- 중요한 내용: <strong style="color: #d63031;">강조할 내용</strong>
- 형광펜 효과: <span style="background-color: #ffeaa7; padding: 2px 5px;">강조 내용</span>
- 글자 크기: <span style="font-size: 18px;">큰 글자</span>
- 문단: <p style="line-height: 1.8; margin: 15px 0;">

2000-3000자로 작성하세요.

[추가 요구사항]
- 연구 결과 수치는 표가 아닌 자연스러운 문장으로 표현
  예: "연구진이 12주간 관찰한 결과, 참가자의 85%가 개선을 경험했다고 해요!"
- 복잡한 데이터는 이해하기 쉬운 비유로 설명
  예: "이 효과는 매일 계단 10층을 오르는 것과 비슷한 운동량이에요"
- 논문 인용은 자연스럽게 녹여서 표현
  예: "최근 스포츠 의학 저널에 발표된 연구에서 놀라운 사실이 밝혀졌어요"
"""
        
        else:  # report
            prompt = f"""
<thinking>
서브카테고리: {subcategory.name}
논문 정보: {paper_info}
기대 효과: {subcategory.expected_effect}

종합 리포트를 작성해야 한다.
여러 논문의 내용을 종합하여 깊이 있는 분석을 제공해야 한다.
네이버 블로그에 복사 가능한 HTML 형식으로 작성해야 한다.
참조된 논문들은 모두 국제 저널에 발표된 영어 논문들이다.
</thinking>

다음 국제 학술지 논문들을 기반으로 네이버 블로그 스타일의 종합 리포트를 HTML 형식으로 작성해주세요:

제목: {subcategory.name}
참조 논문 (모두 영어로 작성된 국제 저널 논문):
{paper_info}

리포트 구성 (더 친근하고 실용적으로):
1. 📋 한눈에 보는 핵심 요약 - 바쁜 분들을 위한 3줄 요약
2. 🤷 왜 이 주제가 중요할까? - 우리 일상과의 연결고리
3. 🔍 연구에서 발견한 놀라운 사실들 - 주요 연구 결과 정리
4. 🆚 연구 대결! 뭐가 더 효과적일까? - 여러 연구 비교 분석
5. 💯 오늘부터 시작하는 실천법 - 검증된 실용 가이드
6. 🤔 전문가들의 추가 조언 - 더 알아두면 좋은 팁
7. 🚀 앞으로 더 기대되는 것들 - 미래 전망
8. 📚 더 궁금하신 분들을 위한 자료 - 참고문헌

[작성 스타일]
- 전문성을 유지하되 네이버 블로그의 친근한 어조 활용
- "안녕하세요! 오늘은 ~에 대한 꿀정보를 총정리해드릴게요" 형식으로 시작
- 독자를 '여러분'으로 지칭하며 친근하게 대화
- "~라고 하네요", "~더라고요", "~해보시는 건 어떨까요?" 등 부드러운 어미 사용
- 중요 수치는 이해하기 쉽게 변환 (예: "70% 개선" → "10명 중 7명이 좋아졌어요")
- 복잡한 연구 방법은 간단한 비유로 설명
- 💡 꿀팁, ⚠️ 주의사항, ✅ 실천 체크리스트 등 시각적 요소 활용
- 전문 용어는 처음 사용 시 쉬운 설명 병기
- 짧은 문단과 충분한 여백으로 읽기 편하게
- 마무리는 격려와 응원의 메시지로

[HTML 형식 요구사항]
- 모든 스타일은 인라인 style 속성 사용
- 섹션 제목: <h2 style="color: #2c3e50; font-size: 26px; margin: 30px 0 15px 0; padding-bottom: 10px; border-bottom: 2px solid #3498db;">
- 요약 박스: <div style="background-color: #ecf0f1; border: 1px solid #bdc3c7; border-radius: 8px; padding: 20px; margin: 20px 0;">
- 핵심 발견: <div style="background-color: #e8f5e9; border-left: 5px solid #4caf50; padding: 15px; margin: 20px 0;">
- 연구 비교 표:
<table style="border-collapse: collapse; width: 100%; margin: 20px 0; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
  <thead>
    <tr style="background-color: #34495e; color: white;">
      <th style="border: 1px solid #ddd; padding: 15px; text-align: left;">연구</th>
      <th style="border: 1px solid #ddd; padding: 15px; text-align: center;">방법론</th>
      <th style="border: 1px solid #ddd; padding: 15px; text-align: center;">주요 발견</th>
      <th style="border: 1px solid #ddd; padding: 15px; text-align: center;">실용적 시사점</th>
    </tr>
  </thead>
</table>
- 실천 가이드: <div style="background-color: #fff8e1; border: 2px solid #ffc107; border-radius: 8px; padding: 20px; margin: 20px 0;">
  <h3 style="color: #f57c00; margin-top: 0;">✅ 실천 가이드</h3>
</div>

전문적이면서도 읽기 쉽게 작성하세요.

[추가 요구사항]
- 연구 비교는 표보다는 스토리텔링 형식으로
  예: "A 연구팀은 이렇게 했는데, B 연구팀은 또 다른 방법을 시도했어요. 결과는..."
- 숫자와 통계는 일상적인 비유로 설명
  예: "효과 크기가 0.8이라는 건, 대략 키 170cm인 사람이 175cm가 되는 정도의 차이예요"
- 각 섹션 마지막에 "한 줄 정리" 추가
- 전체적으로 정보 전달보다는 독자의 실천을 돕는 것에 초점
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
        except Exception as e:
            logger.error(f"[Gemini API - generate_content ({content_type})] Error: {str(e)}")
            logger.error(f"[Gemini API - generate_content ({content_type})] Model: {self.model_name}")
            logger.error(f"[Gemini API - generate_content ({content_type})] Prompt length: {len(prompt)} chars")
            raise
    
    async def generate_subcategory_topics(self, category_name: str, count: int = 5) -> List[str]:
        """카테고리에 대한 서브카테고리 주제 생성"""
        
        prompt = f"""
<thinking>
카테고리: {category_name}
이 카테고리에 대해 사람들이 가장 관심을 가질 만한 구체적인 주제를 생성해야 한다.
각 주제는 실제 학술 논문이 존재할 가능성이 높은 것들이어야 한다.
국제 학술지에 많이 연구되는 주제들을 우선적으로 선택해야 한다.
</thinking>

"{category_name}" 카테고리에 대해 사람들이 가장 궁금해하는 구체적인 세부 주제 {count + 2}개를 생성해주세요.

요구사항:
1. 각 주제는 구체적이고 실용적이어야 함
2. 국제 학술지에 연구가 활발한 주제 우선
3. PubMed, Scopus 등에서 검색 가능한 주제
4. 사람들이 즉시 관심을 가질 만한 주제
5. 영어권에서 연구가 활발한 주제들
6. 하지만 주제명은 한국어로 일반인이 이해하기 쉽게 표현
7. 너무 학술적이거나 어려운 용어는 피하고 친근하게 표현

JSON 형식으로 응답:
{{
  "topics": [
    "구체적인 주제 1",
    "구체적인 주제 2",
    ...
  ]
}}

좋은 예시 (일반인 친화적):
- "고강도 운동 vs 가벼운 유산소, 뱃살 빼는데 뭐가 더 좋을까?"
- "운동 후 언제 단백질 먹어야 근육이 가장 잘 붙을까?"
- "잠을 잘 자야 운동 효과가 좋아진다는데 정말일까?"

나쁜 예시 (너무 학술적):
- "Biometric Data Analysis for Health Optimization"
- "Genomic-Metabolomic Biomarker Prediction Models"
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
        
        return [f"{category_name} - {topic}" for topic in base_topics[:count]]
    
    def transform_content(self, content: str, transformation_type: str, prompt: str) -> str:
        """Transform existing content with a different style"""
        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=self.generation_config
            )
            
            # Log token usage
            usage = response.usage_metadata
            if usage:
                logger.info(f"[Gemini API - transform_content ({transformation_type})] Token usage: prompt_tokens={usage.prompt_token_count}, response_tokens={usage.candidates_token_count}, total_tokens={usage.total_token_count}")
                token_tracker.add_usage(
                    f"transform_content_{transformation_type}",
                    usage.prompt_token_count,
                    usage.candidates_token_count,
                    usage.total_token_count
                )
            
            transformed_content = response.text.strip()
            
            # Ensure HTML format is preserved
            if '<div' in content or '<h' in content:
                # If original was HTML but transformed is not, wrap it
                if not ('<div' in transformed_content or '<h' in transformed_content):
                    transformed_content = f'<div class="transformed-content">{transformed_content}</div>'
            
            return transformed_content
            
        except Exception as e:
            logger.error(f"콘텐츠 변환 실패: {e}")
            # 실패 시 원본 반환
            return content