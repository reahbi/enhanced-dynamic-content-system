"""
프롬프트 엔지니어링 - 콘텐츠 타입별 맞춤 프롬프트 설계
"""

from typing import Dict, List, Any, Optional
from enum import Enum

class ContentType(Enum):
    """콘텐츠 타입"""
    SHORTS = "shorts"
    ARTICLE = "article"
    REPORT = "report"
    CATEGORY = "category"
    SUBCATEGORY = "subcategory"

class ThinkingPromptEngineer:
    """사고 과정을 유도하는 프롬프트 엔지니어"""
    
    def __init__(self):
        self.thinking_templates = self._initialize_templates()
        
    def create_thinking_prompt(self, 
                             content_type: ContentType,
                             topic: str,
                             context: Dict[str, Any]) -> str:
        """콘텐츠 타입별 사고 유도 프롬프트 생성"""
        
        base_template = self.thinking_templates.get(content_type)
        if not base_template:
            raise ValueError(f"Unknown content type: {content_type}")
            
        # 컨텍스트 정보 추출
        papers = context.get('papers', [])
        target_audience = context.get('target_audience', 'general')
        category = context.get('category', '')
        
        # 템플릿 채우기
        prompt = base_template.format(
            topic=topic,
            paper_count=len(papers),
            target_audience=target_audience,
            category=category,
            papers=self._format_papers(papers)
        )
        
        return prompt
    
    def _initialize_templates(self) -> Dict[ContentType, str]:
        """콘텐츠 타입별 템플릿 초기화"""
        
        templates = {
            ContentType.SHORTS: """
<thinking>
주제: {topic}
타겟: {target_audience}
논문 수: {paper_count}

YouTube Shorts 스크립트 작성을 위한 사고 과정:

1. 핵심 메시지 도출
   - 이 주제에서 가장 임팩트 있는 정보는 무엇인가?
   - 45-60초 안에 전달할 수 있는 핵심은?
   - 시청자가 즉시 실천할 수 있는 팁은?

2. 훅(Hook) 전략
   - 첫 5초에 시청자를 사로잡을 방법은?
   - 호기심을 유발하는 질문이나 통계는?
   - 타겟층의 pain point와 연결점은?

3. 콘텐츠 구성
   - 논문의 핵심 발견을 어떻게 쉽게 설명할까?
   - 시각적으로 표현하기 좋은 내용은?
   - 기억하기 쉬운 3가지 포인트는?

4. CTA 설계
   - 시청자가 바로 행동할 수 있는 것은?
   - 다음 콘텐츠로 유도하는 방법은?
   - 댓글이나 좋아요를 유도하는 멘트는?

논문 정보:
{papers}
</thinking>
""",
            
            ContentType.ARTICLE: """
<thinking>
주제: {topic}
타겟: {target_audience}
논문 수: {paper_count}

2000-3000자 아티클 작성을 위한 사고 과정:

1. 독자 분석
   - {target_audience} 독자층의 지식 수준은?
   - 이들이 가장 궁금해하는 점은?
   - 어떤 톤으로 소통해야 효과적일까?

2. 구조 설계
   - 도입부: 어떤 스토리나 통계로 시작할까?
   - 본문: 논문 내용을 어떤 순서로 전개할까?
   - 실용 파트: 어떤 구체적 실천법을 제시할까?
   - 마무리: 어떤 메시지로 행동을 유도할까?

3. 논문 활용 전략
   - 각 논문의 핵심 발견을 어떻게 연결할까?
   - 전문 용어를 어떻게 쉽게 설명할까?
   - 신뢰성을 높이는 인용 방법은?

4. 차별화 포인트
   - 기존 콘텐츠와 어떻게 차별화할까?
   - 독자에게 새로운 인사이트는 무엇일까?
   - 실생활 적용의 구체적 예시는?

논문 정보:
{papers}
</thinking>
""",
            
            ContentType.REPORT: """
<thinking>
주제: {topic}
타겟: {target_audience}
논문 수: {paper_count}

전문 리포트 작성을 위한 사고 과정:

1. 리포트 목적 명확화
   - 이 리포트의 핵심 목표는?
   - {target_audience}가 기대하는 인사이트는?
   - 의사결정에 필요한 정보는?

2. 분석 프레임워크
   - 논문들을 어떤 기준으로 비교 분석할까?
   - 방법론적 강점과 한계는 무엇인가?
   - 결과의 일관성과 차이점은?

3. 종합적 해석
   - 개별 연구를 넘어선 통합적 시각은?
   - 실무 적용 시 고려사항은?
   - 향후 연구 방향은?

4. 권고사항 도출
   - 구체적이고 실행 가능한 제안은?
   - 위험 요소와 대응 방안은?
   - ROI나 기대 효과는?

5. 품질 검증
   - 논리적 일관성이 유지되는가?
   - 근거가 충분히 제시되었는가?
   - 전문가 수준의 깊이가 있는가?

논문 정보:
{papers}
</thinking>
""",
            
            ContentType.CATEGORY: """
<thinking>
키워드: {topic}
카테고리: {category}

실용적 카테고리 생성을 위한 사고 과정:

1. 사용자 니즈 분석
   - 이 키워드를 검색하는 사람들의 목적은?
   - 즉시 실천 가능한 정보를 원하는가?
   - 어떤 문제를 해결하려고 하는가?

2. 카테고리 실용성 평가
   - 논문으로 뒷받침 가능한 주제인가?
   - 구체적인 방법론이 존재하는가?
   - 측정 가능한 결과가 있는가?

3. 차별화 전략
   - 기존 콘텐츠와 어떻게 차별화할까?
   - 독특하면서도 유용한 관점은?
   - 트렌드와 연결점은?

4. 콘텐츠 확장성
   - 시리즈로 만들 수 있는가?
   - 다양한 포맷으로 변환 가능한가?
   - 장기적 가치가 있는가?
</thinking>
""",
            
            ContentType.SUBCATEGORY: """
<thinking>
메인 카테고리: {category}
주제: {topic}

논문 기반 서브카테고리 생성을 위한 사고 과정:

1. 논문 검증
   - 이 주제에 관한 학술 연구가 존재하는가?
   - 연구의 질과 신뢰성은 충분한가?
   - 실용적 인사이트를 도출할 수 있는가?

2. 서브카테고리 구체화
   - 메인 카테고리와의 연관성은?
   - 구체적이고 실행 가능한 내용인가?
   - 타겟층의 관심을 끌 수 있는가?

3. 기대 효과 설정
   - 이 서브카테고리로 얻을 수 있는 것은?
   - 측정 가능한 결과는 무엇인가?
   - 실천 난이도는 적절한가?

4. 콘텐츠 방향성
   - 어떤 스토리로 풀어갈까?
   - 핵심 메시지는 무엇인가?
   - 행동 변화를 유도하는 방법은?
</thinking>
"""
        }
        
        return templates
    
    def _format_papers(self, papers: List[Any]) -> str:
        """논문 정보 포맷팅"""
        if not papers:
            return "논문 정보 없음"
            
        formatted = []
        for i, paper in enumerate(papers, 1):
            paper_info = f"""
{i}. {getattr(paper, 'title', 'Unknown Title')}
   - 저자: {getattr(paper, 'authors', 'Unknown')}
   - 저널: {getattr(paper, 'journal', 'Unknown')} ({getattr(paper, 'year', 'Unknown')})
   - IF: {getattr(paper, 'impact_factor', 'N/A')}
   - 주요 발견: {getattr(paper, 'key_findings', 'N/A')}"""
            formatted.append(paper_info)
            
        return "\n".join(formatted)
    
    def enhance_with_step_by_step_thinking(self, prompt: str) -> str:
        """단계별 사고 과정 강화"""
        enhancement = """
<instruction>
각 단계별로 구체적으로 사고해주세요:
1. 문제 정의: 무엇을 해결하려고 하는가?
2. 정보 분석: 주어진 데이터에서 핵심은 무엇인가?
3. 옵션 탐색: 가능한 접근 방법들은 무엇인가?
4. 평가 기준: 어떤 기준으로 선택할 것인가?
5. 최적 선택: 왜 이 방법이 최선인가?
6. 실행 계획: 구체적으로 어떻게 구현할 것인가?
</instruction>

"""
        return enhancement + prompt
    
    def add_quality_check_thinking(self, prompt: str) -> str:
        """품질 검증 사고 과정 추가"""
        quality_check = """
<quality_check>
콘텐츠 생성 후 다음 사항을 검토해주세요:
- 논문 인용의 정확성
- 논리적 일관성
- 실용성과 구체성
- 타겟 독자층 적합성
- 차별화 요소
</quality_check>

"""
        return prompt + quality_check


class ThinkingPatternLibrary:
    """사고 패턴 라이브러리"""
    
    @staticmethod
    def get_analytical_pattern() -> str:
        """분석적 사고 패턴"""
        return """
1. 현상 파악: 무엇이 일어나고 있는가?
2. 원인 분석: 왜 이런 일이 발생하는가?
3. 영향 평가: 어떤 결과를 가져오는가?
4. 대안 탐색: 다른 방법은 없는가?
5. 최적안 선택: 가장 효과적인 방법은?
"""
    
    @staticmethod
    def get_creative_pattern() -> str:
        """창의적 사고 패턴"""
        return """
1. 기존 틀 깨기: 관습적 접근의 한계는?
2. 새로운 연결: 서로 다른 개념을 어떻게 연결할까?
3. 시각 전환: 다른 관점에서 보면?
4. 은유 활용: 이것을 무엇에 비유할 수 있을까?
5. 극단 상상: 최고/최악의 시나리오는?
"""
    
    @staticmethod
    def get_practical_pattern() -> str:
        """실용적 사고 패턴"""
        return """
1. 목표 명확화: 달성하려는 것은 무엇인가?
2. 자원 파악: 활용 가능한 자원은?
3. 제약 확인: 어떤 제한사항이 있는가?
4. 단계 설정: 어떤 순서로 진행할까?
5. 위험 대비: 예상되는 문제와 대응은?
"""
    
    @staticmethod
    def get_critical_pattern() -> str:
        """비판적 사고 패턴"""
        return """
1. 가정 검토: 당연하게 받아들이는 것은?
2. 근거 평가: 충분히 신뢰할 만한가?
3. 논리 검증: 추론 과정에 오류는 없는가?
4. 편향 인식: 어떤 편견이 작용하는가?
5. 대안 고려: 반대 의견의 타당성은?
"""