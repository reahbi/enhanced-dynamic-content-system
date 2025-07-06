# Shorts 프롬프트 백업

## 원본 프롬프트 (gemini_client.py)

```python
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
```

## 백업 날짜: 2025-07-06

### 제거 이유
- 프롬프트가 너무 길어서 토큰 소비가 많음
- HTML 형식 요구사항이 과도하게 상세함
- 500 오류의 원인이 될 수 있음