"""
논문 품질 평가 시스템 - 학술 논문의 신뢰성과 영향력을 자동 평가
"""

from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import re

class QualityGrade(str, Enum):
    """논문 품질 등급"""
    A_PLUS = "A+"
    A = "A"
    B_PLUS = "B+"
    B = "B"
    C = "C"
    D = "D"

@dataclass
class QualityMetrics:
    """논문 품질 메트릭"""
    paper_type_score: float  # 논문 유형 점수 (최대 35점)
    impact_factor_score: float  # Impact Factor 점수 (최대 30점)
    citation_score: float  # 인용 수 점수 (최대 20점)
    recency_score: float  # 최신성 점수 (최대 15점)
    total_score: float  # 총점 (최대 100점)
    quality_grade: QualityGrade  # 등급 (A+, A, B+, B, C)
    
@dataclass
class PaperInfo:
    """논문 정보"""
    title: str
    authors: str
    journal: str
    year: int
    doi: str
    impact_factor: float
    citations: int
    paper_type: str

@dataclass
class QualityInfo:
    """논문 품질 평가 결과"""
    quality_score: float
    grade: QualityGrade
    details: Dict[str, float]
    strengths: List[str]
    weaknesses: List[str]

class PaperQualityEvaluator:
    """논문 품질 평가 엔진"""
    
    def __init__(self):
        # 논문 유형별 기본 점수
        self.paper_type_scores = {
            "Systematic Review": 35,
            "Meta-analysis": 35,
            "Systematic Review & Meta-analysis": 35,
            "Randomized Controlled Trial": 30,
            "RCT": 30,
            "Cohort Study": 25,
            "Case-Control Study": 20,
            "Cross-sectional Study": 15,
            "Case Report": 10,
            "Review": 20,
            "Research Article": 15,
            "Original Article": 15,
            "Clinical Trial": 25,
            "Longitudinal Study": 25,
            "Prospective Study": 25,
            "Retrospective Study": 20,
            "Observational Study": 15,
            "Pilot Study": 10,
            "Editorial": 5,
            "Letter": 5,
            "Commentary": 5
        }
        
        # 저널 Impact Factor 범위
        self.impact_factor_ranges = {
            "top_tier": 10.0,  # Nature, Science 등
            "high": 5.0,       # 주요 전문 저널
            "medium": 3.0,     # 일반 전문 저널
            "low": 1.0         # 기타 저널
        }
        
        # 현재 연도
        self.current_year = datetime.now().year
    
    def evaluate_paper_metrics(self, paper: PaperInfo) -> QualityMetrics:
        """논문 품질 종합 평가"""
        
        # 1. 논문 유형 점수 계산
        paper_type_score = self._calculate_paper_type_score(paper.paper_type)
        
        # 2. Impact Factor 점수 계산
        impact_factor_score = self._calculate_impact_factor_score(paper.impact_factor)
        
        # 3. 인용 수 점수 계산
        citation_score = self._calculate_citation_score(paper.citations, paper.year)
        
        # 4. 최신성 점수 계산
        recency_score = self._calculate_recency_score(paper.year)
        
        # 총점 계산
        total_score = (
            paper_type_score + 
            impact_factor_score + 
            citation_score + 
            recency_score
        )
        
        # 등급 할당
        quality_grade = self._assign_quality_grade(total_score)
        
        return QualityMetrics(
            paper_type_score=paper_type_score,
            impact_factor_score=impact_factor_score,
            citation_score=citation_score,
            recency_score=recency_score,
            total_score=total_score,
            quality_grade=quality_grade
        )
    
    def evaluate_paper(self, paper) -> QualityInfo:
        """논문 품질 평가 (API용)"""
        # PaperInfo 형식으로 변환 (필요한 경우)
        if not isinstance(paper, PaperInfo):
            paper_info = PaperInfo(
                title=getattr(paper, 'title', ''),
                authors=getattr(paper, 'authors', ''),
                journal=getattr(paper, 'journal', ''),
                year=getattr(paper, 'year', datetime.now().year),
                doi=getattr(paper, 'doi', ''),
                impact_factor=getattr(paper, 'impact_factor', 0.0),
                citations=getattr(paper, 'citations', 0),
                paper_type=getattr(paper, 'paper_type', 'Research Article')
            )
        else:
            paper_info = paper
        
        # 메트릭 계산
        metrics = self.evaluate_paper_metrics(paper_info)
        
        # 상세 정보
        details = {
            'paper_type_score': metrics.paper_type_score,
            'impact_factor_score': metrics.impact_factor_score,
            'citation_score': metrics.citation_score,
            'recency_score': metrics.recency_score
        }
        
        # 강점과 약점 분석
        strengths = []
        weaknesses = []
        
        # 논문 유형 평가
        if metrics.paper_type_score >= 30:
            strengths.append("높은 증거 수준의 연구 설계")
        elif metrics.paper_type_score <= 15:
            weaknesses.append("낮은 증거 수준의 연구 설계")
        
        # Impact Factor 평가
        if metrics.impact_factor_score >= 20:
            strengths.append("영향력 높은 저널에 게재")
        elif metrics.impact_factor_score <= 10:
            weaknesses.append("낮은 영향력의 저널")
        
        # 인용 수 평가
        if metrics.citation_score >= 15:
            strengths.append("높은 인용 수")
        elif metrics.citation_score <= 5:
            weaknesses.append("낮은 인용 수")
        
        # 최신성 평가
        if metrics.recency_score >= 12:
            strengths.append("최신 연구")
        elif metrics.recency_score <= 3:
            weaknesses.append("오래된 연구")
        
        return QualityInfo(
            quality_score=metrics.total_score,
            grade=metrics.quality_grade,
            details=details,
            strengths=strengths,
            weaknesses=weaknesses
        )
    
    def _calculate_paper_type_score(self, paper_type: str) -> float:
        """논문 유형별 점수 계산 (최대 35점)"""
        
        # 정확한 매칭 시도
        for type_key, score in self.paper_type_scores.items():
            if paper_type.lower() == type_key.lower():
                return float(score)
        
        # 부분 매칭 시도
        paper_type_lower = paper_type.lower()
        for type_key, score in self.paper_type_scores.items():
            if type_key.lower() in paper_type_lower or paper_type_lower in type_key.lower():
                return float(score)
        
        # 키워드 기반 매칭
        if "systematic" in paper_type_lower and "review" in paper_type_lower:
            return 35.0
        elif "meta" in paper_type_lower and "analysis" in paper_type_lower:
            return 35.0
        elif "randomized" in paper_type_lower or "rct" in paper_type_lower:
            return 30.0
        elif "cohort" in paper_type_lower:
            return 25.0
        elif "trial" in paper_type_lower:
            return 25.0
        elif "review" in paper_type_lower:
            return 20.0
        elif "study" in paper_type_lower:
            return 15.0
        else:
            return 10.0  # 기본값
    
    def _calculate_impact_factor_score(self, impact_factor: float) -> float:
        """Impact Factor 점수 계산 (최대 30점)"""
        
        # IF × 2, 최대 30점
        score = impact_factor * 2
        
        # 상한선 적용
        return min(score, 30.0)
    
    def _calculate_citation_score(self, citations: int, year: int) -> float:
        """인용 수 점수 계산 (최대 20점)"""
        
        # 연간 인용 수 계산 (논문 연령 고려)
        years_since_publication = max(1, self.current_year - year)
        annual_citations = citations / years_since_publication
        
        # 연간 인용 수 × 2, 최대 20점
        score = annual_citations * 2
        
        # 상한선 적용
        return min(score, 20.0)
    
    def _calculate_recency_score(self, year: int) -> float:
        """최신성 점수 계산 (최대 15점)"""
        
        years_old = self.current_year - year
        
        if years_old <= 1:
            return 15.0
        elif years_old <= 2:
            return 12.0
        elif years_old <= 3:
            return 9.0
        elif years_old <= 5:
            return 6.0
        elif years_old <= 7:
            return 3.0
        else:
            return 0.0
    
    def _assign_quality_grade(self, total_score: float) -> QualityGrade:
        """총점에 따른 등급 할당"""
        
        if total_score >= 80:
            return QualityGrade.A_PLUS
        elif total_score >= 70:
            return QualityGrade.A
        elif total_score >= 60:
            return QualityGrade.B_PLUS
        elif total_score >= 50:
            return QualityGrade.B
        elif total_score >= 30:
            return QualityGrade.C
        else:
            return QualityGrade.D
    
    def calculate_quality_score(self, metrics: Dict[str, float]) -> float:
        """메트릭 딕셔너리로부터 품질 점수 계산"""
        
        return sum(metrics.values())
    
    def evaluate_paper_set(self, papers: List[PaperInfo]) -> Dict[str, any]:
        """논문 세트 전체 평가"""
        
        if not papers:
            return {
                "average_score": 0,
                "average_grade": "N/A",
                "paper_count": 0,
                "quality_distribution": {}
            }
        
        # 각 논문 평가
        evaluations = [self.evaluate_paper_metrics(paper) for paper in papers]
        
        # 평균 점수
        average_score = sum(e.total_score for e in evaluations) / len(evaluations)
        
        # 등급 분포
        grade_distribution = {}
        for eval in evaluations:
            grade = eval.quality_grade.value  # Enum value 사용
            grade_distribution[grade] = grade_distribution.get(grade, 0) + 1
        
        # 대표 등급 (평균 점수 기반)
        average_grade = self._assign_quality_grade(average_score)
        
        return {
            "average_score": round(average_score, 1),
            "average_grade": average_grade,
            "paper_count": len(papers),
            "quality_distribution": grade_distribution,
            "evaluations": evaluations
        }
    
    def generate_quality_report(self, paper: PaperInfo, metrics: QualityMetrics) -> str:
        """논문 품질 평가 리포트 생성"""
        
        report = f"""
📊 논문 품질 평가 리포트
{'='*50}

📄 논문 정보:
- 제목: {paper.title}
- 저자: {paper.authors}
- 저널: {paper.journal} (IF: {paper.impact_factor})
- 발행연도: {paper.year}
- 인용횟수: {paper.citations}
- 논문유형: {paper.paper_type}

📈 품질 평가 결과:
- 논문 유형 점수: {metrics.paper_type_score}/35점
- Impact Factor 점수: {metrics.impact_factor_score:.1f}/30점
- 인용 수 점수: {metrics.citation_score:.1f}/20점
- 최신성 점수: {metrics.recency_score}/15점

✅ 총점: {metrics.total_score:.1f}/100점
⭐ 등급: {metrics.quality_grade}

💡 평가 해석:
"""
        
        # 등급별 해석 추가
        if metrics.total_score >= 80:
            report += "- 최고 수준의 근거를 제공하는 우수한 논문입니다.\n"
            report += "- 높은 신뢰도로 콘텐츠 생성에 활용할 수 있습니다."
        elif metrics.total_score >= 70:
            report += "- 신뢰할 수 있는 우수한 근거를 제공합니다.\n"
            report += "- 안심하고 콘텐츠 생성에 활용할 수 있습니다."
        elif metrics.total_score >= 60:
            report += "- 양호한 수준의 근거를 제공합니다.\n"
            report += "- 추가 논문과 함께 활용하면 더욱 좋습니다."
        elif metrics.total_score >= 50:
            report += "- 기본적인 근거는 제공하나 보완이 필요합니다.\n"
            report += "- 다른 고품질 논문과 함께 활용을 권장합니다."
        else:
            report += "- 근거 수준이 낮아 주의가 필요합니다.\n"
            report += "- 반드시 다른 논문들과 교차 검증이 필요합니다."
        
        return report