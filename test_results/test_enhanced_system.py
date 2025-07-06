#!/usr/bin/env python3
"""
Enhanced Dynamic System v6.1 테스트 코드
설계도가 정상적으로 작동하는지 검증
"""

import os
import json
import re
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
from google import genai
from google.genai import types
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

@dataclass
class Paper:
    """논문 정보 데이터 모델"""
    title: str
    authors: str
    journal: str
    year: int
    doi: str = ""
    impact_factor: float = 0.0
    citations: int = 0
    paper_type: str = "Original"
    
@dataclass
class QualityInfo:
    """논문 품질 정보"""
    total_score: float
    quality_grade: str
    paper_type_score: float
    impact_factor_score: float
    citation_score: float
    recency_score: float

@dataclass
class Category:
    """카테고리 데이터 모델"""
    name: str
    description: str
    emoji: str = ""
    trend_score: float = 0.0
    research_activity: float = 0.0

@dataclass
class SubCategory:
    """서브카테고리 데이터 모델"""
    name: str
    description: str
    papers: List[Paper]
    quality_info: Optional[QualityInfo] = None
    expected_effect: str = ""

class GeminiClient:
    """Gemini API 클라이언트"""
    
    def __init__(self):
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        self.client = genai.Client(api_key=api_key)
        
    def generate_content(self, prompt: str) -> str:
        """컨텐츠 생성"""
        try:
            response = self.client.models.generate_content(
                model='gemini-2.0-flash-exp',
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.7,
                    max_output_tokens=4000
                )
            )
            return response.text
        except Exception as e:
            print(f"Gemini API 호출 오류: {e}")
            return ""

class PaperVerificationSystem:
    """논문 정보 검증 및 품질 평가"""
    
    def verify_paper_quality(self, paper: Paper) -> QualityInfo:
        """논문 품질 점수 계산"""
        
        quality_score = 0
        
        # 1. 논문 유형 점수
        paper_type_score = 0
        if 'systematic review' in paper.paper_type.lower():
            paper_type_score = 35
        elif 'meta-analysis' in paper.paper_type.lower():
            paper_type_score = 35
        elif 'review' in paper.paper_type.lower():
            paper_type_score = 20
        else:
            paper_type_score = 10
        quality_score += paper_type_score
            
        # 2. Impact Factor 점수
        if_score = min(paper.impact_factor * 2, 30)
        quality_score += if_score
        
        # 3. Citation 점수
        citation_score = min(paper.citations / 10, 20)
        quality_score += citation_score
        
        # 4. 최신성 점수
        years_old = 2024 - paper.year
        recency_score = max(15 - (years_old * 3), 0)
        quality_score += recency_score
        
        quality_grade = self._get_quality_grade(quality_score)
        
        return QualityInfo(
            total_score=quality_score,
            quality_grade=quality_grade,
            paper_type_score=paper_type_score,
            impact_factor_score=if_score,
            citation_score=citation_score,
            recency_score=recency_score
        )
    
    def _get_quality_grade(self, score: float) -> str:
        """품질 등급 판정"""
        if score >= 80:
            return "A+ (최상급 근거)"
        elif score >= 70:
            return "A (우수한 근거)"
        elif score >= 60:
            return "B+ (양호한 근거)"
        elif score >= 50:
            return "B (적절한 근거)"
        else:
            return "C (기본 근거)"

class HybridCategorySystem:
    """AI 생성 + 사용자 커스텀 하이브리드 시스템"""
    
    def __init__(self):
        self.gemini_client = GeminiClient()
        
    def discover_main_categories(self, seed_keyword: str, count: int = 10) -> List[Category]:
        """AI 기반 메인카테고리 생성"""
        
        prompt = f"""
        <thinking>
        사용자가 '{seed_keyword}'에 관심이 있다.
        추상적이거나 트렌디한 것보다는
        실제로 사람들이 바로 관심을 가지고 클릭하고 싶어할만한
        구체적이고 실용적인 주제들이 필요하다.
        
        예: 가슴운동, 노인운동법, 남녀운동차이, 운동세트수, 5분운동 등
        즉시 "아, 이거 궁금해!" 하고 클릭하고 싶어질만한 카테고리를 만들어야 한다.
        </thinking>
        
        키워드: {seed_keyword}
        
        '{seed_keyword}'과 관련하여 사람들이 **즉시 관심을 가지고 클릭하고 싶어할만한**
        구체적이고 실용적인 메인카테고리 {count}개를 생성해주세요.
        
        ✅ 좋은 예시 (클릭하고 싶어지는 구체적 주제):
        - 💪 가슴운동 완전정복
        - 🧓 60세 이후 안전운동법  
        - ♀️♂️ 남녀 운동차이 비교
        - 📱 5분 홈트레이닝
        - 🔢 운동세트수 최적화
        - 🏃‍♀️ 뱃살 빼는 유산소
        - 💊 운동 전후 영양섭취
        - 😴 잠자기 전 운동법
        - 🦵 하체비만 타파법
        - 💺 직장인 의자운동
        
        조건:
        1. **즉시 관심**: "오, 이거 나한테 필요해!" 하고 바로 느낄 수 있는 주제
        2. **구체적**: 추상적이지 않고 명확한 운동 관련 주제
        3. **실용적**: 당장 적용해볼 수 있는 내용
        4. **호기심 자극**: 클릭하고 싶어지는 제목
        5. **다양성**: 연령, 성별, 부위, 시간, 목적 등 다양한 관점
        
        형식:
        🎯 [카테고리명]: [설명] - [왜 지금 HOT한지]
        
        예시:
        🧬 바이오해킹 피트니스: 유전자 맞춤 운동법 - DNA 검사 기반 개인화 운동이 대세
        """
        
        response = self.gemini_client.generate_content(prompt)
        return self._parse_categories(response)
    
    def _parse_categories(self, response: str) -> List[Category]:
        """응답에서 카테고리 파싱"""
        categories = []
        lines = response.split('\n')
        
        for line in lines:
            line = line.strip()
            if line and ('🎯' in line or '💪' in line or '🔥' in line or '🧬' in line):
                # 이모지와 카테고리명 추출
                emoji_match = re.search(r'([🎯💪🔥🧬🤖🌱⏰🧠💊📊🎮🧘‍♂️🌙🎨🏃‍♀️])', line)
                if emoji_match:
                    emoji = emoji_match.group(1)
                    
                    # 카테고리명과 설명 분리
                    parts = line.split(':', 1)
                    if len(parts) >= 2:
                        name = parts[0].replace(emoji, '').strip()
                        description = parts[1].split('-')[0].strip() if '-' in parts[1] else parts[1].strip()
                        
                        categories.append(Category(
                            name=name,
                            description=description,
                            emoji=emoji,
                            trend_score=8.0,  # 기본값
                            research_activity=7.0  # 기본값
                        ))
        
        return categories[:10]  # 최대 10개

class HighQualityPaperSelector:
    """고품질 논문 우선 선별 시스템"""
    
    def __init__(self):
        self.gemini_client = GeminiClient()
        self.paper_verifier = PaperVerificationSystem()
        
    def generate_subcategories_with_papers(self, main_category: str, count: int = 5) -> List[SubCategory]:
        """고품질 논문 기반 서브카테고리 생성"""
        
        prompt = f"""
        <thinking>
        {main_category}에 대한 서브카테고리를 생성할 때
        가능하다면 고품질 논문을 기반으로 해야 한다.
        리뷰 논문, 높은 인용수, 높은 Impact Factor를 우선시한다.
        실제로 존재할 법한 논문 정보를 제공해야 한다.
        </thinking>
        
        메인카테고리: {main_category}
        
        이 카테고리에서 고품질 논문을 기반으로 한 
        서브카테고리 {count}개를 생성해주세요.
        
        필수 조건:
        1. 구체적이고 실행 가능한 주제
        2. 다음 우선순위로 논문 선별:
           - Systematic Review / Meta-analysis
           - Citation 50회 이상
           - Impact Factor 5.0 이상 저널
           - 최근 5년 이내 발표
        3. 즉시 효과를 볼 수 있는 실용적 주제
        4. 호기심을 자극하는 네이밍
        
        출력 형식:
        📌 [서브카테고리명]
        - 핵심 내용: [간단한 설명]
        - 근거 논문:
          • 제목: "[정확한 논문 제목]"
          • 저자: [First Author et al.]
          • 저널: [저널명] (IF: X.X)
          • 발행: [년도]
          • DOI: [DOI 번호]
          • 인용수: [횟수]
          • 논문 유형: [Review/Original/Meta-analysis]
        - 기대 효과: [구체적 효과]
        
        예시:
        📌 HIIT vs 지구력 운동의 미토콘드리아 생합성 효과
        - 핵심 내용: 고강도 인터벌과 지속적 유산소 운동의 세포 수준 비교
        - 근거 논문:
          • 제목: "High-intensity interval training versus moderate-intensity continuous training"
          • 저자: Weston KS et al.
          • 저널: British Journal of Sports Medicine (IF: 13.2)
          • 발행: 2023
          • DOI: 10.1136/bjsports-2022-106355
          • 인용수: 127
          • 논문 유형: Systematic Review
        - 기대 효과: 주 3회 20분 HIIT로 지구력 운동 1시간 효과
        """
        
        response = self.gemini_client.generate_content(prompt)
        return self._parse_subcategories(response)
    
    def _parse_subcategories(self, response: str) -> List[SubCategory]:
        """응답에서 서브카테고리 파싱"""
        subcategories = []
        current_subcategory = None
        current_paper = None
        
        lines = response.split('\n')
        
        for line in lines:
            line = line.strip()
            
            # 서브카테고리 시작
            if line.startswith('📌'):
                if current_subcategory and current_paper:
                    # 이전 서브카테고리 저장
                    current_subcategory.papers.append(current_paper)
                    # 품질 검증
                    if current_subcategory.papers:
                        quality = self.paper_verifier.verify_paper_quality(current_subcategory.papers[0])
                        current_subcategory.quality_info = quality
                    subcategories.append(current_subcategory)
                
                # 새 서브카테고리 시작
                name = line.replace('📌', '').strip()
                current_subcategory = SubCategory(
                    name=name,
                    description="",
                    papers=[],
                    expected_effect=""
                )
                current_paper = None
                
            elif line.startswith('- 핵심 내용:'):
                if current_subcategory:
                    current_subcategory.description = line.replace('- 핵심 내용:', '').strip()
                    
            elif line.startswith('- 기대 효과:'):
                if current_subcategory:
                    current_subcategory.expected_effect = line.replace('- 기대 효과:', '').strip()
                    
            elif '제목:' in line:
                title = re.search(r'"([^"]+)"', line)
                if title:
                    current_paper = Paper(
                        title=title.group(1),
                        authors="",
                        journal="",
                        year=2023,
                        paper_type="Original"
                    )
                    
            elif '저자:' in line and current_paper:
                authors = line.split('저자:')[1].strip()
                current_paper.authors = authors
                
            elif '저널:' in line and current_paper:
                journal_info = line.split('저널:')[1].strip()
                # IF 추출
                if_match = re.search(r'IF: ([\d.]+)', journal_info)
                if if_match:
                    current_paper.impact_factor = float(if_match.group(1))
                current_paper.journal = journal_info.split('(IF:')[0].strip()
                
            elif '발행:' in line and current_paper:
                year_match = re.search(r'(\d{4})', line)
                if year_match:
                    current_paper.year = int(year_match.group(1))
                    
            elif 'DOI:' in line and current_paper:
                doi = line.split('DOI:')[1].strip()
                current_paper.doi = doi
                
            elif '인용수:' in line and current_paper:
                citations_match = re.search(r'(\d+)', line)
                if citations_match:
                    current_paper.citations = int(citations_match.group(1))
                    
            elif '논문 유형:' in line and current_paper:
                paper_type = line.split('논문 유형:')[1].strip()
                current_paper.paper_type = paper_type
        
        # 마지막 서브카테고리 처리
        if current_subcategory and current_paper:
            current_subcategory.papers.append(current_paper)
            if current_subcategory.papers:
                quality = self.paper_verifier.verify_paper_quality(current_subcategory.papers[0])
                current_subcategory.quality_info = quality
            subcategories.append(current_subcategory)
        
        return subcategories

class EnhancedDynamicSystem:
    """Enhanced Dynamic System v6.1 메인 클래스"""
    
    def __init__(self):
        self.category_system = HybridCategorySystem()
        self.paper_selector = HighQualityPaperSelector()
        
    def run_test_workflow(self, seed_keyword: str = "운동"):
        """테스트 워크플로우 실행"""
        
        print(f"🚀 Enhanced Dynamic System v6.1 테스트 시작")
        print(f"📝 시드 키워드: {seed_keyword}")
        print("=" * 60)
        
        # Step 1: AI 메인카테고리 생성
        print("\n1️⃣ AI 메인카테고리 생성 중...")
        main_categories = self.category_system.discover_main_categories(seed_keyword, count=5)
        
        print(f"✅ {len(main_categories)}개 카테고리 생성 완료:")
        for i, cat in enumerate(main_categories, 1):
            print(f"   {i}. {cat.emoji} {cat.name}: {cat.description}")
        
        # Step 2: 첫 번째 카테고리로 서브카테고리 생성 테스트
        if main_categories:
            selected_category = main_categories[0]
            print(f"\n2️⃣ '{selected_category.name}' 서브카테고리 생성 중...")
            
            subcategories = self.paper_selector.generate_subcategories_with_papers(
                selected_category.name, 
                count=3
            )
            
            print(f"✅ {len(subcategories)}개 서브카테고리 생성 완료:")
            
            for i, subcat in enumerate(subcategories, 1):
                print(f"\n   📌 {subcat.name}")
                print(f"      내용: {subcat.description}")
                print(f"      효과: {subcat.expected_effect}")
                
                if subcat.papers:
                    paper = subcat.papers[0]
                    print(f"      논문: {paper.title}")
                    print(f"      저자: {paper.authors}")
                    print(f"      저널: {paper.journal} (IF: {paper.impact_factor})")
                    print(f"      인용: {paper.citations}회")
                    
                    if subcat.quality_info:
                        print(f"      품질: {subcat.quality_info.quality_grade} ({subcat.quality_info.total_score:.1f}점)")
        
        # Step 3: 결과 저장
        self._save_test_results(main_categories, subcategories if 'subcategories' in locals() else [])
        
        print(f"\n🎉 테스트 완료! 결과가 저장되었습니다.")
        
    def _save_test_results(self, categories: List[Category], subcategories: List[SubCategory]):
        """테스트 결과 저장"""
        
        results = {
            "test_timestamp": datetime.now().isoformat(),
            "main_categories": [asdict(cat) for cat in categories],
            "subcategories": []
        }
        
        for subcat in subcategories:
            subcat_dict = asdict(subcat)
            results["subcategories"].append(subcat_dict)
        
        # 결과 저장
        os.makedirs("test_results", exist_ok=True)
        with open("test_results/enhanced_system_test.json", 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)

def main():
    """메인 테스트 함수"""
    try:
        system = EnhancedDynamicSystem()
        system.run_test_workflow("운동")
    except Exception as e:
        print(f"❌ 테스트 실행 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()