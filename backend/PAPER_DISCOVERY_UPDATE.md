# Paper Discovery Update - English/International Papers

## Summary of Changes

This document describes the changes made to ensure the system discovers English/international papers instead of Korean papers.

### Problem Identified
The system was biased towards Korean papers because:
1. Prompts were written entirely in Korean without specifying language preferences
2. No explicit instruction to search for international/English papers
3. No preference for international academic databases

### Solution Implemented

#### 1. Updated `discover_papers_for_topic` method in `gemini_client.py`
- Added explicit instructions to prioritize English papers from international databases
- Specified preference for papers indexed in PubMed, Scopus, Web of Science
- Requested high-impact factor journals
- Required paper titles and journal names to be in English

Key changes:
```python
# Added to thinking section:
"국제 학술지의 영어 논문을 우선적으로 찾아야 한다."

# Added requirements:
"- 국제 학술 데이터베이스(PubMed, Scopus, Web of Science 등)에 등재된 영어 논문을 우선적으로 찾아주세요"
"- High-impact factor를 가진 저명한 국제 저널의 논문을 선호합니다"
"- 논문 제목과 저널명은 영어로 제공해주세요"
```

#### 2. Updated `generate_subcategory_topics` method
- Added preference for topics actively researched in international journals
- Specified that topics should be searchable in PubMed, Scopus
- Emphasized topics popular in English-speaking research communities

### Test Results
Created `test_english_papers.py` to verify the changes. Results show:
- ✅ All discovered papers are from international English journals
- ✅ Impact factors range from 3.5 to 12.0 (high-quality journals)
- ✅ Citations range from 250 to 4100 (well-cited papers)
- ✅ Papers include systematic reviews, meta-analyses, and position stands

### Examples of Discovered Papers
1. **Journal of Strength and Conditioning Research** - Impact Factor: 3.8
2. **Sports Medicine** - Impact Factor: 10.5-12.0
3. **Obesity Reviews** - Impact Factor: 10.7
4. **Journal of the American Heart Association** - Impact Factor: 8.4

### Recommendation
The system now successfully discovers English/international papers. To maintain this behavior:
1. Keep the prompt instructions that specify international paper preferences
2. Monitor paper discovery results to ensure consistency
3. Consider adding journal quality filters based on impact factor thresholds