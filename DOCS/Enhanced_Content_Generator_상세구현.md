# Enhanced Content Generator 상세 구현

## Phase 3: Enhanced Generation 활용 (완전 구현)

```python
class EnhancedContentGenerator:
    def __init__(self):
        self.native_thinking_client = NativeThinkingGeminiClient()
        self.token_tracker = TokenUsageTracker()
        
    def generate_with_category_context(self, topic, papers, category):
        """카테고리 컨텍스트를 반영한 콘텐츠 생성"""
        
        category_context = INTEGRATED_CATEGORIES[category]
        
        # 1. 논문 분석 단계
        paper_analysis = self.analyze_papers_with_thinking(papers, category_context)
        
        # 2. 카테고리별 특화 콘텐츠 생성
        contents = self.generate_specialized_contents(
            topic, paper_analysis, category_context
        )
        
        return contents
    
    def analyze_papers_with_thinking(self, papers, category_context):
        """Native Thinking Mode로 논문 분석"""
        
        analysis_prompt = f"""
        <thinking>
        논문들을 분석하여 {category_context['description']} 관점에서 
        핵심 인사이트를 도출해야 합니다.
        
        타겟 키워드: {', '.join(category_context['target_keywords'])}
        특화 관점: {category_context['specialized_perspective']}
        </thinking>
        
        다음 논문들을 분석하여 주요 발견사항과 실용적 인사이트를 정리해주세요:
        
        {self.format_papers_for_analysis(papers)}
        
        분석 요구사항:
        1. 핵심 연구 결과 요약
        2. 실무 적용 가능한 인사이트
        3. 20-40대 타겟층에게 유용한 포인트
        4. 카테고리별 특화 관점 반영
        """
        
        return self.native_thinking_client.generate_content(analysis_prompt)
    
    def generate_specialized_contents(self, topic, paper_analysis, category_context):
        """카테고리별 특화 콘텐츠 생성"""
        
        contents = {}
        
        # 숏츠 스크립트 생성
        contents['shorts'] = self.generate_category_shorts(
            topic, paper_analysis, category_context
        )
        
        # 상세 아티클 생성  
        contents['article'] = self.generate_category_article(
            topic, paper_analysis, category_context
        )
        
        # 종합 리포트 생성
        contents['report'] = self.generate_comprehensive_report(
            topic, paper_analysis, category_context
        )
        
        return contents
    
    def generate_category_shorts(self, topic, paper_analysis, category_context):
        """카테고리별 특화 숏츠 스크립트"""
        
        shorts_styles = {
            "💪 근성장 & 근력": {
                "hook": "근육 키우고 싶다면 이것부터!",
                "tone": "동기부여형, 실용적",
                "cta": "지금 바로 시도해보세요!",
                "target_audience": "근성장을 원하는 헬린이부터 중급자"
            },
            "🔥 다이어트 & 체지방감소": {
                "hook": "살 빼는 진짜 비밀 공개!",
                "tone": "충격적, 즉시 행동 유도",
                "cta": "오늘부터 시작하세요!",
                "target_audience": "체지방 감소를 원하는 20-40대"
            },
            "🍽️ 식단 & 영양": {
                "hook": "이 음식의 놀라운 진실!",
                "tone": "정보전달형, 신뢰성 강조",
                "cta": "식단에 추가해보세요!",
                "target_audience": "건강한 식단을 원하는 직장인"
            },
            "🏃 운동방법 & 기법": {
                "hook": "운동 효과 10배 늘리는 방법!",
                "tone": "기술적, 전문적",
                "cta": "다음 운동에 적용하세요!",
                "target_audience": "운동 효율성을 높이고 싶은 중급자"
            },
            "📋 운동계획 & 설계": {
                "hook": "완벽한 운동 계획 세우기!",
                "tone": "체계적, 계획적",
                "cta": "내 계획을 세워보세요!",
                "target_audience": "체계적 운동을 원하는 계획파"
            },
            "🧘 회복 & 컨디셔닝": {
                "hook": "회복이 근성장의 80%!",
                "tone": "치유적, 건강 중심",
                "cta": "회복에 투자하세요!",
                "target_audience": "지속가능한 운동을 원하는 성인"
            },
            "🧠 멘탈 & 동기부여": {
                "hook": "운동 포기하고 싶을 때!",
                "tone": "영감적, 감정적",
                "cta": "마음가짐을 바꿔보세요!",
                "target_audience": "운동 동기 부족으로 고민인 사람"
            },
            "🚑 부상 방지 & 재활": {
                "hook": "부상 없이 평생 운동하기!",
                "tone": "안전 중심, 예방적",
                "cta": "안전하게 운동하세요!",
                "target_audience": "부상 경험이 있거나 예방을 원하는 사람"
            },
            "💡 운동 장비 & 보조제": {
                "hook": "이 장비/보조제 효과 실화?",
                "tone": "분석적, 비교 검토",
                "cta": "현명하게 선택하세요!",
                "target_audience": "장비나 보조제 구매를 고려하는 사람"
            },
            "👩‍🏫 특정 그룹별 맞춤 정보": {
                "hook": "당신에게 딱 맞는 운동법!",
                "tone": "개인화, 맞춤형",
                "cta": "내 상황에 적용하세요!",
                "target_audience": "특정 조건이나 제약이 있는 사람"
            }
        }
        
        style = shorts_styles.get(category_context['name'], shorts_styles["💪 근성장 & 근력"])
        
        shorts_prompt = f"""
        <thinking>
        {category_context['name']} 카테고리에 특화된 숏츠 콘텐츠를 만들어야 합니다.
        
        스타일: {style['tone']}
        훅: {style['hook']}
        CTA: {style['cta']}
        타겟: {style['target_audience']}
        
        논문 분석 결과를 바탕으로 해당 카테고리 특성에 맞는 
        임팩트 있는 숏츠를 제작해야 합니다.
        </thinking>
        
        주제: {topic}
        카테고리: {category_context['name']}
        
        논문 분석 결과:
        {paper_analysis}
        
        위 내용을 바탕으로 {category_context['name']} 특화 숏츠 스크립트를 작성해주세요.
        
        스타일 가이드:
        - 훅: {style['hook']} 스타일
        - 톤: {style['tone']}
        - CTA: {style['cta']} 형태
        - 길이: 45-60초 분량
        - 타겟: {style['target_audience']}
        
        구조:
        1. 강력한 오프닝 (0-3초)
        2. 핵심 정보 전달 (3-45초)  
        3. 명확한 행동 지침 (45-60초)
        
        출력 형식:
        [오프닝]
        [메인 콘텐츠]
        [클로징 & CTA]
        """
        
        return self.native_thinking_client.generate_content(shorts_prompt)
    
    def generate_category_article(self, topic, paper_analysis, category_context):
        """카테고리별 특화 상세 아티클"""
        
        article_templates = {
            "💪 근성장 & 근력": {
                "sections": ["운동 메커니즘", "실제 적용법", "주의사항", "진척 측정"],
                "focus": "과학적 근거 + 실무 적용",
                "writing_style": "동기부여적이면서 전문적"
            },
            "🔥 다이어트 & 체지방감소": {
                "sections": ["체지방 감소 원리", "식단 전략", "운동 방법", "일상 적용"],
                "focus": "즉시 실행 가능한 방법",
                "writing_style": "행동 중심적이고 구체적"
            },
            "🍽️ 식단 & 영양": {
                "sections": ["영양학적 분석", "식단 구성법", "타이밍", "개인 맞춤화"],
                "focus": "구체적 식단 가이드",
                "writing_style": "정보 중심적이고 신뢰성 있게"
            },
            "🏃 운동방법 & 기법": {
                "sections": ["동작 분석", "기법 설명", "단계별 진행", "응용 방법"],
                "focus": "정확한 수행법",
                "writing_style": "기술적이고 단계별"
            },
            "📋 운동계획 & 설계": {
                "sections": ["계획 수립 원칙", "주기화 방법", "개인화 전략", "모니터링"],
                "focus": "체계적 접근법",
                "writing_style": "논리적이고 구조적"
            },
            "🧘 회복 & 컨디셔닝": {
                "sections": ["회복 과학", "실제 방법론", "라이프스타일", "장기 관리"],
                "focus": "지속가능한 건강관리",
                "writing_style": "치유적이고 균형잡힌"
            },
            "🧠 멘탈 & 동기부여": {
                "sections": ["심리학적 배경", "동기 유지법", "목표 설정", "습관 형성"],
                "focus": "마인드셋 변화",
                "writing_style": "영감적이고 공감적"
            },
            "🚑 부상 방지 & 재활": {
                "sections": ["부상 메커니즘", "예방 전략", "재활 프로세스", "복귀 가이드"],
                "focus": "안전한 운동 환경",
                "writing_style": "신중하고 안전 중심적"
            },
            "💡 운동 장비 & 보조제": {
                "sections": ["과학적 분석", "효과 검증", "선택 가이드", "사용법"],
                "focus": "객관적 평가와 가이드",
                "writing_style": "분석적이고 중립적"
            },
            "👩‍🏫 특정 그룹별 맞춤 정보": {
                "sections": ["그룹 특성 분석", "맞춤 전략", "실행 방법", "케이스 스터디"],
                "focus": "개인화된 솔루션",
                "writing_style": "맞춤형이고 포용적"
            }
        }
        
        template = article_templates.get(
            category_context['name'], 
            article_templates["💪 근성장 & 근력"]
        )
        
        article_prompt = f"""
        <thinking>
        {category_context['name']} 카테고리에 특화된 상세 아티클을 작성해야 합니다.
        
        섹션 구성: {', '.join(template['sections'])}
        포커스: {template['focus']}
        글쓰기 스타일: {template['writing_style']}
        
        논문 분석을 바탕으로 해당 카테고리의 특성을 살린
        실용적이고 전문적인 아티클을 만들어야 합니다.
        </thinking>
        
        주제: {topic}
        카테고리: {category_context['name']}
        
        논문 분석 결과:
        {paper_analysis}
        
        위 내용을 바탕으로 {category_context['name']} 특화 상세 아티클을 작성해주세요.
        
        아티클 구성:
        {self.format_article_sections(template['sections'])}
        
        작성 가이드:
        - 포커스: {template['focus']}
        - 글쓰기 스타일: {template['writing_style']}
        - 길이: 2000-3000자
        - 타겟: 20-40대 운동 관심층
        - 톤: 전문적이지만 이해하기 쉽게
        - 구조: 논리적 흐름 + 실용적 정보
        
        특별 요구사항:
        - 각 섹션마다 실행 가능한 팁 포함
        - 논문 근거를 자연스럽게 인용
        - 독자의 수준에 맞는 설명
        - 안전성과 효과성 균형
        """
        
        return self.native_thinking_client.generate_content(article_prompt)
    
    def generate_comprehensive_report(self, topic, paper_analysis, category_context):
        """종합 리포트 생성"""
        
        report_prompt = f"""
        <thinking>
        종합 리포트는 모든 정보를 통합하여 완전한 가이드를 제공해야 합니다.
        
        카테고리별 특화 요소:
        - {category_context['name']}의 고유 특성
        - 타겟 오디언스의 니즈
        - 실무 적용 가능성
        
        논문 기반의 신뢰할 수 있는 정보와 
        실제 적용 가능한 가이드를 모두 포함해야 합니다.
        </thinking>
        
        주제: {topic}
        카테고리: {category_context['name']}
        
        논문 분석 결과:
        {paper_analysis}
        
        위 내용을 바탕으로 종합 리포트를 작성해주세요.
        
        리포트 구성:
        1. 🎯 연구 배경 및 목적
        2. 📊 주요 연구 결과 종합
        3. 💡 실무 적용 가이드라인
        4. 🔥 카테고리별 특화 인사이트
        5. 📋 실행 계획 및 로드맵
        6. ⚠️ 주의사항 및 제한점
        7. 🚀 결론 및 권장사항
        
        특화 요소:
        - 카테고리: {category_context['name']}
        - 타겟: 20-40대 운동 관심층
        - 키워드: {', '.join(category_context.get('target_keywords', []))}
        - 관점: 과학적 근거 + 실무 적용
        
        작성 지침:
        - 각 섹션을 명확히 구분
        - 논문 인용을 적절히 포함
        - 실행 가능한 구체적 지침 제공
        - 독자 수준에 맞는 설명
        - 안전성 강조
        """
        
        return self.native_thinking_client.generate_content(report_prompt)
    
    def format_papers_for_analysis(self, papers):
        """논문 정보 분석용 포맷팅"""
        formatted = []
        for i, paper in enumerate(papers, 1):
            formatted.append(f"""
            📋 논문 {i}:
            제목: {paper.get('title', 'N/A')}
            저자: {paper.get('authors', 'N/A')}
            발행년도: {paper.get('year', 'N/A')}
            저널: {paper.get('journal', 'N/A')}
            요약: {paper.get('summary', 'N/A')}
            주요 결과: {paper.get('key_findings', 'N/A')}
            """)
        return '\n'.join(formatted)
    
    def format_article_sections(self, sections):
        """아티클 섹션 포맷팅"""
        formatted_sections = []
        for i, section in enumerate(sections, 1):
            formatted_sections.append(f"""
            {i}. {section}
               - 핵심 내용 설명
               - 실용적 적용 방법
               - 주의사항 및 팁
            """)
        return '\n'.join(formatted_sections)

# 카테고리 정의 (완전 확장)
INTEGRATED_CATEGORIES = {
    "💪 근성장 & 근력": {
        "name": "💪 근성장 & 근력",
        "description": "근육 성장, 근력 향상, 웨이트 트레이닝과 관련된 모든 주제",
        "target_keywords": ["근성장", "근력", "muscle", "strength", "hypertrophy", "웨이트"],
        "specialized_perspective": "과학적 근거 기반 근성장 최적화",
        "target_audience": "근성장을 원하는 헬린이부터 중급자"
    },
    "🔥 다이어트 & 체지방감소": {
        "name": "🔥 다이어트 & 체지방감소",
        "description": "체지방 감소, 체중 관리, 다이어트 전략과 관련된 주제",
        "target_keywords": ["다이어트", "체지방", "weight loss", "fat burning", "칼로리"],
        "specialized_perspective": "지속가능한 체지방 감소 전략",
        "target_audience": "체지방 감소를 원하는 20-40대"
    },
    "🍽️ 식단 & 영양": {
        "name": "🍽️ 식단 & 영양",
        "description": "영양학, 식단 구성, 영양 타이밍과 관련된 주제",
        "target_keywords": ["영양", "식단", "nutrition", "diet", "단백질", "탄수화물"],
        "specialized_perspective": "운동 효과 극대화를 위한 영양 전략",
        "target_audience": "건강한 식단을 원하는 직장인"
    },
    "🏃 운동방법 & 기법": {
        "name": "🏃 운동방법 & 기법",
        "description": "운동 기술, 폼 교정, 운동 기법 개선과 관련된 주제",
        "target_keywords": ["운동방법", "기법", "form", "technique", "운동자세"],
        "specialized_perspective": "정확하고 효율적인 운동 수행법",
        "target_audience": "운동 효율성을 높이고 싶은 중급자"
    },
    "📋 운동계획 & 설계": {
        "name": "📋 운동계획 & 설계",
        "description": "운동 프로그램 설계, 주기화, 계획 수립과 관련된 주제",
        "target_keywords": ["운동계획", "프로그램", "periodization", "planning", "스케줄"],
        "specialized_perspective": "개인 맞춤형 운동 프로그램 설계",
        "target_audience": "체계적 운동을 원하는 계획파"
    },
    "🧘 회복 & 컨디셔닝": {
        "name": "🧘 회복 & 컨디셔닝",
        "description": "운동 후 회복, 컨디셔닝, 피로 관리와 관련된 주제",
        "target_keywords": ["회복", "컨디셔닝", "recovery", "conditioning", "피로"],
        "specialized_perspective": "최적 회복을 통한 지속가능한 운동",
        "target_audience": "지속가능한 운동을 원하는 성인"
    },
    "🧠 멘탈 & 동기부여": {
        "name": "🧠 멘탈 & 동기부여",
        "description": "운동 동기, 심리적 요소, 마인드셋과 관련된 주제",
        "target_keywords": ["동기부여", "멘탈", "motivation", "mindset", "습관"],
        "specialized_perspective": "운동 지속을 위한 심리적 전략",
        "target_audience": "운동 동기 부족으로 고민인 사람"
    },
    "🚑 부상 방지 & 재활": {
        "name": "🚑 부상 방지 & 재활",
        "description": "부상 예방, 재활 운동, 안전한 운동과 관련된 주제",
        "target_keywords": ["부상예방", "재활", "injury prevention", "rehabilitation", "안전"],
        "specialized_perspective": "부상 없는 평생 운동을 위한 전략",
        "target_audience": "부상 경험이 있거나 예방을 원하는 사람"
    },
    "💡 운동 장비 & 보조제": {
        "name": "💡 운동 장비 & 보조제",
        "description": "운동 기구, 보조제, 운동 도구와 관련된 주제",
        "target_keywords": ["운동장비", "보조제", "equipment", "supplements", "기구"],
        "specialized_perspective": "과학적 근거 기반 장비/보조제 선택",
        "target_audience": "장비나 보조제 구매를 고려하는 사람"
    },
    "👩‍🏫 특정 그룹별 맞춤 정보": {
        "name": "👩‍🏫 특정 그룹별 맞춤 정보",
        "description": "연령별, 성별, 직업별 맞춤 운동 정보",
        "target_keywords": ["맞춤운동", "그룹별", "customized", "specific", "개인화"],
        "specialized_perspective": "개인 특성을 고려한 맞춤형 접근",
        "target_audience": "특정 조건이나 제약이 있는 사람"
    }
}
```

## 🎯 핵심 특징

### 1. **카테고리별 완전 특화**
- 10개 카테고리마다 고유한 스타일과 접근법
- 타겟 오디언스별 맞춤 콘텐츠
- 카테고리 특성을 반영한 글쓰기 스타일

### 2. **Native Thinking Mode 완전 활용**
- 논문 분석에서 깊이 있는 사고 과정
- 카테고리 컨텍스트를 반영한 콘텐츠 생성
- 각 단계별 체계적인 thinking 프로세스

### 3. **3단계 콘텐츠 생성**
- **숏츠 스크립트**: 카테고리별 특화 스타일 (45-60초)
- **상세 아티클**: 카테고리별 섹션 구성 (2000-3000자)
- **종합 리포트**: 통합 가이드 (완전한 실행 계획)

### 4. **실무 중심 접근**
- 모든 콘텐츠에 실행 가능한 팁 포함
- 안전성과 효과성의 균형
- 독자 수준에 맞는 맞춤형 설명

이제 다른 폴더에서 이 완전한 설계를 바탕으로 하이브리드 시스템을 구현하실 수 있습니다! 🚀