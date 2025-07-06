# 🔬 Enhanced Dynamic System v6.1 - 고품질 논문 기반 설계서

## 1. 핵심 개선사항

### 1.1 논문 품질 보증 시스템
- **리뷰 논문 우선**: Systematic Review, Meta-analysis 우선 참조
- **Citation 기반 선별**: 피인용수 상위 논문 우선
- **Impact Factor 고려**: IF 5.0 이상 저널 우선
- **정확한 출처 명시**: DOI, 저자, 저널명, 발행년도 필수

### 1.2 유연한 카테고리 시스템
- **AI 자동 생성**: Gemini가 트렌디한 카테고리 추천
- **커스텀 입력**: 사용자가 직접 메인카테고리 생성 가능
- **하이브리드 모드**: AI 추천 + 사용자 정의 혼합

## 2. 개선된 논문 기반 서브카테고리 생성

### 2.1 고품질 논문 우선 선별 시스템

```python
class HighQualityPaperSelector:
    """고품질 논문 우선 선별 시스템"""
    
    def __init__(self):
        self.quality_criteria = {
            "review_paper_weight": 3.0,  # 리뷰 논문 가중치
            "citation_threshold": 50,     # 최소 피인용수
            "impact_factor_min": 5.0,     # 최소 Impact Factor
            "recency_years": 5           # 최근 5년 이내 논문
        }
    
    def generate_subcategories_with_papers(self, main_category: str, count: int = 5):
        """고품질 논문 기반 서브카테고리 생성"""
        
        prompt = f"""
        <thinking>
        {main_category}에 대한 서브카테고리를 생성할 때
        가능하다면 고품질 논문을 기반으로 해야 한다.
        리뷰 논문, 높은 인용수, 높은 Impact Factor를 우선시한다.
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
          • 제목: "High-intensity interval training versus moderate-intensity continuous training: superior metabolic benefits in obese individuals"
          • 저자: Weston KS et al.
          • 저널: British Journal of Sports Medicine (IF: 13.2)
          • 발행: 2023
          • DOI: 10.1136/bjsports-2022-106355
          • 인용수: 127
          • 논문 유형: Systematic Review
        - 기대 효과: 주 3회 20분 HIIT로 지구력 운동 1시간 효과
        """
        
        return self.gemini_client.generate_content(prompt)
```

### 2.2 논문 검증 시스템

```python
class PaperVerificationSystem:
    """논문 정보 검증 및 품질 평가"""
    
    def verify_paper_quality(self, paper_info: Dict) -> Dict:
        """논문 품질 점수 계산"""
        
        quality_score = 0
        verification_details = {}
        
        # 1. 논문 유형 점수
        if paper_info['type'] == 'Systematic Review':
            quality_score += 30
        elif paper_info['type'] == 'Meta-analysis':
            quality_score += 35
        elif paper_info['type'] == 'Review':
            quality_score += 20
        else:
            quality_score += 10
            
        # 2. Impact Factor 점수
        if_score = min(paper_info['impact_factor'] * 2, 30)
        quality_score += if_score
        
        # 3. Citation 점수
        citation_score = min(paper_info['citations'] / 10, 20)
        quality_score += citation_score
        
        # 4. 최신성 점수
        years_old = 2024 - paper_info['year']
        recency_score = max(15 - (years_old * 3), 0)
        quality_score += recency_score
        
        verification_details = {
            'total_score': quality_score,
            'paper_type_score': 30 if 'Review' in paper_info['type'] else 10,
            'impact_factor_score': if_score,
            'citation_score': citation_score,
            'recency_score': recency_score,
            'quality_grade': self._get_quality_grade(quality_score)
        }
        
        return verification_details
    
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
```

## 3. 유연한 메인카테고리 시스템

### 3.1 하이브리드 카테고리 생성

```python
class HybridCategorySystem:
    """AI 생성 + 사용자 커스텀 하이브리드 시스템"""
    
    def __init__(self):
        self.ai_generator = DynamicCategoryDiscovery()
        self.custom_categories = []
        
    def get_main_categories(self, 
                          seed_keyword: str, 
                          mode: str = 'hybrid',
                          custom_categories: List[str] = None) -> List[Category]:
        """
        메인카테고리 획득 (3가지 모드 지원)
        
        Args:
            mode: 'ai_only', 'custom_only', 'hybrid'
            custom_categories: 사용자 정의 카테고리 리스트
        """
        
        categories = []
        
        if mode in ['ai_only', 'hybrid']:
            # AI 생성 카테고리
            ai_categories = self.ai_generator.discover_main_categories(
                seed_keyword, 
                count=10 if mode == 'ai_only' else 7
            )
            categories.extend(ai_categories)
            
        if mode in ['custom_only', 'hybrid'] and custom_categories:
            # 사용자 커스텀 카테고리
            for custom_cat in custom_categories:
                categories.append(self._create_custom_category(custom_cat))
                
        return self._validate_and_enrich_categories(categories)
    
    def _create_custom_category(self, category_name: str) -> Category:
        """사용자 정의 카테고리를 표준 형식으로 변환"""
        
        # AI를 활용해 커스텀 카테고리 보강
        enrichment_prompt = f"""
        사용자가 입력한 카테고리: {category_name}
        
        이 카테고리를 다음 형식으로 보강해주세요:
        - 적절한 이모지 추가
        - 매력적인 설명 추가
        - 트렌드 점수 평가 (1-10)
        - 연구 활성도 평가 (1-10)
        """
        
        enriched = self.gemini_client.generate_content(enrichment_prompt)
        return self._parse_enriched_category(enriched)
```

### 3.2 사용자 인터페이스 설계

```python
class CategorySelectionUI:
    """카테고리 선택 사용자 인터페이스"""
    
    def show_category_options(self, seed_keyword: str):
        """카테고리 선택 옵션 표시"""
        
        print(f"\n🎯 '{seed_keyword}' 관련 카테고리 설정\n")
        print("1. AI 추천 카테고리만 사용")
        print("2. 내가 직접 카테고리 입력")
        print("3. AI 추천 + 내 카테고리 혼합")
        
        mode = input("\n선택하세요 (1-3): ")
        
        if mode == '1':
            return self._ai_only_mode(seed_keyword)
        elif mode == '2':
            return self._custom_only_mode()
        elif mode == '3':
            return self._hybrid_mode(seed_keyword)
    
    def _custom_only_mode(self):
        """사용자 커스텀 카테고리 입력"""
        
        print("\n📝 카테고리를 직접 입력하세요")
        print("(예: 홈트레이닝, 체형교정, 스포츠 영양학)")
        
        custom_categories = []
        while len(custom_categories) < 10:
            cat = input(f"\n카테고리 {len(custom_categories)+1} (완료: Enter): ")
            if not cat:
                break
            custom_categories.append(cat)
            
        return custom_categories
    
    def _hybrid_mode(self, seed_keyword):
        """AI + 커스텀 혼합 모드"""
        
        # AI 추천 7개
        ai_categories = self._get_ai_categories(seed_keyword, count=7)
        print("\n🤖 AI 추천 카테고리:")
        for i, cat in enumerate(ai_categories):
            print(f"{i+1}. {cat}")
            
        # 사용자 추가 3개
        print("\n📝 추가하고 싶은 카테고리 3개를 입력하세요:")
        custom_categories = []
        for i in range(3):
            cat = input(f"추가 카테고리 {i+1}: ")
            if cat:
                custom_categories.append(cat)
                
        return ai_categories + custom_categories
```

## 4. 통합 워크플로우

### 4.1 개선된 전체 플로우

```python
class EnhancedDynamicWorkflow:
    """논문 품질 보증 + 유연한 카테고리 시스템"""
    
    def __init__(self):
        self.category_system = HybridCategorySystem()
        self.paper_selector = HighQualityPaperSelector()
        self.paper_verifier = PaperVerificationSystem()
        self.content_generator = EnhancedContentGenerator()
        
    def run_enhanced_workflow(self, seed_keyword: str):
        """개선된 워크플로우 실행"""
        
        # Step 1: 메인카테고리 설정 (AI/커스텀/혼합)
        main_categories = self.category_system.get_main_categories(
            seed_keyword,
            mode='hybrid'  # 사용자가 선택
        )
        
        # Step 2: 사용자가 5-10개 선택
        selected_categories = self.show_selection_ui(main_categories)
        
        # Step 3: 고품질 논문 기반 서브카테고리 생성
        subcategories_with_papers = {}
        for category in selected_categories:
            subs = self.paper_selector.generate_subcategories_with_papers(
                category,
                count=5
            )
            
            # 논문 품질 검증
            verified_subs = []
            for sub in subs:
                quality = self.paper_verifier.verify_paper_quality(sub['paper'])
                if quality['quality_grade'] in ['A+', 'A', 'B+']:
                    sub['quality_info'] = quality
                    verified_subs.append(sub)
                    
            subcategories_with_papers[category] = verified_subs
        
        # Step 4: 콘텐츠 생성 (논문 출처 명시)
        contents = self.content_generator.generate_with_citations(
            subcategories_with_papers
        )
        
        return contents
```

### 4.2 논문 출처 명시 콘텐츠 생성

```python
class CitationAwareContentGenerator:
    """정확한 논문 출처를 포함한 콘텐츠 생성"""
    
    def generate_with_citations(self, topic_with_papers: Dict):
        """출처가 명시된 콘텐츠 생성"""
        
        content_prompt = f"""
        주제: {topic_with_papers['title']}
        
        근거 논문:
        {self._format_paper_citations(topic_with_papers['papers'])}
        
        위 고품질 논문들을 기반으로 콘텐츠를 생성하되,
        반드시 다음 사항을 포함하세요:
        
        1. 주요 연구 결과를 인용할 때 (저자, 년도) 형식 사용
        2. 구체적인 수치나 결과 언급 시 출처 명시
        3. 각 섹션마다 근거 논문 표시
        4. 마지막에 참고문헌 목록 포함
        
        예시:
        "최근 메타분석에 따르면(Weston et al., 2023), HIIT는 
        전통적 유산소 운동 대비 2.5배 높은 미토콘드리아 생합성을 
        유도하는 것으로 나타났다."
        """
        
        return self.generate_formatted_content(content_prompt)
    
    def _format_paper_citations(self, papers: List[Dict]) -> str:
        """논문 인용 형식 정리"""
        citations = []
        for i, paper in enumerate(papers, 1):
            citation = f"""
            [{i}] {paper['authors']} ({paper['year']}). 
                {paper['title']}. 
                {paper['journal']}, {paper['volume']}({paper['issue']}), {paper['pages']}.
                DOI: {paper['doi']}
                Impact Factor: {paper['impact_factor']} | Citations: {paper['citations']}
            """
            citations.append(citation)
        return '\n'.join(citations)
```

## 5. 예시: 실제 작동 시나리오

### 5.1 사용자 시나리오

```
사용자: "운동" 입력

시스템: 카테고리 설정 옵션 제공
1. AI 추천만
2. 직접 입력
3. 혼합

사용자: 3 (혼합) 선택

AI 추천 카테고리 (7개):
🧬 바이오해킹 피트니스
🤖 AI 퍼스널 트레이닝
🌱 지속가능한 웰니스
⏰ 마이크로 워크아웃
🧠 뉴로피트니스
💊 운동 약물학
📊 데이터 드리븐 운동

사용자 추가 (3개):
- 시니어 피트니스
- 임산부 운동
- 재활 트레이닝

선택된 카테고리의 서브카테고리 (논문 기반):

🧬 바이오해킹 피트니스
└── 📌 유전자 맞춤 운동 프로토콜
    - 근거 논문:
      • "Genetic polymorphisms and exercise performance: A systematic review"
      • Nature Reviews Genetics (IF: 59.6), 2023
      • Citations: 234
      • Grade: A+ (최상급 근거)
```

## 6. 기술적 장점

### 6.1 v5 대비 개선사항
- ✅ **논문 품질 보증**: 리뷰논문, 높은 IF/Citation 우선
- ✅ **정확한 출처 명시**: DOI, 저자, 저널 정보 완전 포함
- ✅ **유연한 카테고리**: AI 자동 + 사용자 커스텀 지원
- ✅ **품질 등급 시스템**: A+~C 등급으로 근거 수준 명시

### 6.2 신뢰성 강화
- 모든 콘텐츠에 논문 출처 명시
- 품질 검증된 논문만 사용
- 투명한 근거 수준 표시
- 학술적 인용 형식 준수

이 설계는 기존 v5의 장점을 유지하면서도, 논문 품질과 출처 명시를 크게 강화하고, 사용자가 원하는 카테고리를 직접 입력할 수 있는 유연성을 제공합니다! 🔬