"""
카테고리 최적화 모듈 - 실용성과 즉시관심도를 우선시하는 개선된 알고리즘
"""

from typing import List, Dict, Any, Tuple
from dataclasses import dataclass
import re
import json

@dataclass
class CategoryMetrics:
    """카테고리 평가 메트릭"""
    has_number: bool  # 구체적 숫자 포함 여부
    has_target: bool  # 명확한 대상 포함 여부
    has_benefit: bool  # 즉각적 혜택 표현 여부
    has_action: bool  # 실행 가능한 동작 포함 여부
    specificity_score: float  # 구체성 점수 (0-10)
    clickability_score: float  # 클릭 유도 점수 (0-10)
    practicality_score: float  # 실용성 점수 (0-10)
    interest_score: float  # 즉시관심도 점수 (0-10)
    overall_score: float  # 종합 점수 (0-10)

class CategoryOptimizer:
    """카테고리 생성 최적화 클래스"""
    
    def __init__(self):
        # 실용적 키워드 패턴
        self.practical_patterns = {
            'numbers': r'\d+',  # 숫자
            'time': r'(\d+분|\d+시간|\d+일|\d+주|\d+개월)',  # 시간 표현
            'targets': r'(초보|중급|고급|남성|여성|시니어|직장인|학생|주부)',  # 대상
            'benefits': r'(효과|개선|향상|감소|증가|해결|극복|완치|성공)',  # 혜택
            'actions': r'(하는법|방법|가이드|팁|비법|전략|루틴|프로그램)'  # 행동
        }
        
        # 카테고리 템플릿
        self.category_templates = [
            "{number}{time} {keyword} {benefit}",
            "{target}을 위한 {keyword} {action}",
            "{keyword} {problem} 해결하는 {number}가지 방법",
            "{time}만에 끝내는 {keyword} {routine}",
            "{expert}가 추천하는 {keyword} {tips}"
        ]
        
        # 실용적 단어 사전
        self.practical_words = {
            'numbers': ['3', '5', '7', '10', '15', '30'],
            'times': ['5분', '10분', '15분', '30분', '7일', '14일', '30일'],
            'targets': ['초보자', '여성', '남성', '50대', '60대', '직장인', '아침형', '저녁형'],
            'benefits': ['완벽정복', '마스터', '해결법', '비밀', '꿀팁', '필수지식'],
            'actions': ['가이드', '운동법', '루틴', '프로그램', '전략', '비법'],
            'problems': ['뱃살', '팔뚝살', '허벅지', '어깨통증', '허리통증', '불면증']
        }
    
    def analyze_category(self, category_name: str) -> CategoryMetrics:
        """카테고리 이름 분석 및 메트릭 계산"""
        
        # 패턴 매칭
        has_number = bool(re.search(self.practical_patterns['numbers'], category_name))
        has_time = bool(re.search(self.practical_patterns['time'], category_name))
        has_target = bool(re.search(self.practical_patterns['targets'], category_name))
        has_benefit = bool(re.search(self.practical_patterns['benefits'], category_name))
        has_action = bool(re.search(self.practical_patterns['actions'], category_name))
        
        # 점수 계산
        specificity_score = (
            (3 if has_number or has_time else 0) +
            (2 if has_target else 0) +
            (2 if has_action else 0) +
            (3 if len(category_name) > 10 else 1)
        )
        
        clickability_score = (
            (3 if has_benefit else 0) +
            (2 if has_number else 0) +
            (2 if '완전정복' in category_name or '비밀' in category_name else 0) +
            (3 if '?' in category_name or '!' in category_name else 1)
        )
        
        practicality_score = (
            (2.5 if has_action else 0) +
            (2.5 if has_target else 0) +
            (2.5 if has_time else 0) +
            (2.5 if '방법' in category_name or '가이드' in category_name else 0)
        )
        
        interest_score = (
            (3 if has_number else 0) +
            (3 if has_benefit else 0) +
            (2 if has_target else 0) +
            (2 if '최신' in category_name or '2024' in category_name else 0)
        )
        
        overall_score = (
            specificity_score * 0.2 +
            clickability_score * 0.3 +
            practicality_score * 0.3 +
            interest_score * 0.2
        )
        
        return CategoryMetrics(
            has_number=has_number or has_time,
            has_target=has_target,
            has_benefit=has_benefit,
            has_action=has_action,
            specificity_score=min(specificity_score, 10),
            clickability_score=min(clickability_score, 10),
            practicality_score=min(practicality_score, 10),
            interest_score=min(interest_score, 10),
            overall_score=min(overall_score, 10)
        )
    
    def filter_categories(self, categories: List[Dict[str, Any]], 
                         min_score: float = 7.0) -> List[Dict[str, Any]]:
        """카테고리 필터링 및 품질 보장"""
        
        filtered = []
        seen_patterns = set()
        
        for cat in categories:
            # 메트릭 분석
            metrics = self.analyze_category(cat['name'])
            
            # 최소 점수 필터
            if metrics.overall_score < min_score:
                continue
            
            # 중복 패턴 체크
            pattern = self._extract_pattern(cat['name'])
            if pattern in seen_patterns:
                continue
            seen_patterns.add(pattern)
            
            # 메트릭 정보 추가
            cat['metrics'] = {
                'overall_score': round(metrics.overall_score, 1),
                'practicality': round(metrics.practicality_score, 1),
                'interest': round(metrics.interest_score, 1),
                'clickability': round(metrics.clickability_score, 1)
            }
            
            filtered.append(cat)
        
        # 점수 기준 정렬
        filtered.sort(key=lambda x: x['metrics']['overall_score'], reverse=True)
        
        return filtered
    
    def _extract_pattern(self, category_name: str) -> str:
        """카테고리에서 핵심 패턴 추출 (중복 체크용)"""
        # 숫자 제거
        pattern = re.sub(r'\d+', 'N', category_name)
        # 시간 표현 통일
        pattern = re.sub(r'(분|시간|일|주|개월)', 'T', pattern)
        # 대상 표현 통일
        pattern = re.sub(r'(초보|중급|고급|남성|여성|시니어)', 'P', pattern)
        
        return pattern.lower()
    
    def enhance_prompt(self, base_prompt: str) -> str:
        """프롬프트 개선 - 실용성과 구체성 강조"""
        
        enhancement = """
<thinking>
사용자가 정말로 클릭하고 싶어할 카테고리를 만들어야 한다.
추상적이거나 애매한 표현은 피하고, 구체적이고 즉시 실행 가능한 카테고리를 생성한다.

좋은 예시:
- 💪 5분 가슴운동 루틴 
- 🧓 60대 안전 근력운동 가이드
- 🔥 뱃살 빼는 7가지 과학적 방법
- ⏱️ 아침 10분 전신운동 프로그램
- 💊 운동 전후 영양제 완벽정리

피해야 할 예시:
- 혁신적인 운동법
- 미래형 피트니스
- 트렌디한 헬스케어
- 창의적 운동 솔루션
</thinking>

카테고리 생성 규칙:
1. 반드시 구체적인 숫자나 시간을 포함 (5분, 7가지, 30일 등)
2. 명확한 대상이나 문제를 명시 (초보자, 뱃살, 어깨통증 등)
3. 즉각적인 혜택이나 결과를 표현 (완벽정복, 해결법, 마스터 등)
4. 실행 가능한 행동을 포함 (운동법, 가이드, 루틴 등)
5. 이모지로 시각적 어필 강화

"""
        return base_prompt + enhancement
    
    def validate_category_set(self, categories: List[Dict[str, Any]]) -> Tuple[bool, List[str]]:
        """카테고리 세트 전체 검증"""
        
        issues = []
        
        # 다양성 체크
        targets = set()
        benefits = set()
        
        for cat in categories:
            # 대상 추출
            for target in re.findall(self.practical_patterns['targets'], cat['name']):
                targets.add(target)
            
            # 혜택 추출
            for benefit in re.findall(self.practical_patterns['benefits'], cat['name']):
                benefits.add(benefit)
        
        # 다양성 부족 체크
        if len(targets) < 3:
            issues.append("대상 그룹이 다양하지 않음")
        
        if len(benefits) < 3:
            issues.append("제공하는 혜택이 다양하지 않음")
        
        # 전체 품질 체크
        avg_score = sum(cat.get('metrics', {}).get('overall_score', 0) 
                       for cat in categories) / len(categories)
        
        if avg_score < 7.5:
            issues.append(f"평균 품질 점수 부족: {avg_score:.1f}/10")
        
        # 실용성 체크
        practical_count = sum(1 for cat in categories 
                            if cat.get('metrics', {}).get('practicality', 0) >= 8)
        
        if practical_count < len(categories) * 0.7:
            issues.append("실용적인 카테고리 비율 부족")
        
        return len(issues) == 0, issues
    
    async def generate_categories(self, keyword: str, count: int = 10) -> List[Dict[str, Any]]:
        """키워드를 기반으로 카테고리 생성"""
        from datetime import datetime
        import uuid
        
        # 기본 카테고리 템플릿
        base_categories = [
            {"name": f"💪 {keyword} 기본 루틴", "emoji": "💪", "description": f"{keyword}의 기본 동작과 루틴"},
            {"name": f"🔥 효과적인 {keyword} 방법", "emoji": "🔥", "description": f"{keyword}을 위한 효과적인 방법론"},
            {"name": f"🍽️ {keyword}를 위한 영양 관리", "emoji": "🍽️", "description": f"{keyword} 목적에 맞는 영양 섭취"},
            {"name": f"🏃 {keyword} 고급 기법", "emoji": "🏃", "description": f"{keyword}의 고급 테크닉과 팁"},
            {"name": f"📋 {keyword} 계획 수립", "emoji": "📋", "description": f"{keyword}을 위한 체계적인 계획"},
            {"name": f"🧘 {keyword} 회복 관리", "emoji": "🧘", "description": f"{keyword} 후 효과적인 회복 방법"},
            {"name": f"🧠 {keyword} 멘탈 관리", "emoji": "🧠", "description": f"{keyword}을 위한 정신적 준비"},
            {"name": f"🚑 {keyword} 부상 예방", "emoji": "🚑", "description": f"{keyword} 시 부상 방지 요령"},
            {"name": f"💡 {keyword} 장비 활용", "emoji": "💡", "description": f"{keyword}에 필요한 장비와 도구"},
            {"name": f"👩‍🏫 초보자를 위한 {keyword}", "emoji": "👩‍🏫", "description": f"{keyword} 입문자를 위한 가이드"}
        ]
        
        categories = []
        for i, template in enumerate(base_categories[:count]):
            # 카테고리 메트릭 분석
            metrics = self.analyze_category(template["name"])
            
            category = {
                "id": f"cat_{uuid.uuid4().hex[:8]}",
                "name": template["name"],
                "emoji": template["emoji"],
                "description": template["description"],
                "practicality_score": 8.0,  # 기본값
                "interest_score": 8.0,  # 기본값
                "created_at": datetime.now().isoformat(),
                "metrics": {
                    "has_number": metrics.has_number,
                    "has_target": metrics.has_target,
                    "has_benefit": metrics.has_benefit,
                    "has_action": metrics.has_action,
                    "specificity_score": metrics.specificity_score,
                    "clickability_score": metrics.clickability_score,
                    "overall_score": metrics.overall_score
                }
            }
            categories.append(category)
        
        return categories
    
    async def generate_subcategories(self, category: str, topic: str) -> Dict[str, Any]:
        """주제에 맞는 논문 검색 및 서브카테고리 생성
        
        Args:
            category: 메인 카테고리 이름
            topic: 세부 주제
            
        Returns:
            서브카테고리 정보 또는 None
        """
        from .gemini_client import GeminiClient
        
        # Gemini 클라이언트 초기화
        gemini_client = GeminiClient()
        
        # 논문 검색 및 서브카테고리 생성
        subcategory_result = gemini_client.discover_papers_for_topic(category, topic)
        
        if subcategory_result:
            return {
                "name": subcategory_result.name,
                "description": subcategory_result.description,
                "papers": [{
                    "title": p.title,
                    "authors": p.authors,
                    "journal": p.journal,
                    "publication_year": p.year,
                    "doi": p.doi,
                    "impact_factor": p.impact_factor,
                    "citations": p.citations,
                    "paper_type": p.paper_type
                } for p in subcategory_result.papers],
                "expected_effect": subcategory_result.expected_effect,
                "quality_score": subcategory_result.quality_score,
                "quality_grade": subcategory_result.quality_grade
            }
        
        return None