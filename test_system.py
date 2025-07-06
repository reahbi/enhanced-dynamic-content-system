#!/usr/bin/env python3
"""
Enhanced Dynamic Content System v6.1 - 통합 테스트 스크립트
"""

import os
import sys
import time
import json
import asyncio
from pathlib import Path

# Add backend to path
sys.path.append(str(Path(__file__).parent / "backend"))

from backend.app.services.gemini_client import GeminiClient

def print_section(title):
    """섹션 제목 출력"""
    print(f"\n{'='*60}")
    print(f"🧪 {title}")
    print('='*60)

async def test_category_generation():
    """카테고리 생성 테스트"""
    print_section("카테고리 생성 테스트")
    
    client = GeminiClient()
    
    # 테스트 1: 기본 카테고리 생성
    print("\n1. '운동' 키워드로 카테고리 생성...")
    categories = client.generate_categories("운동", count=3)
    
    if categories:
        print(f"✅ {len(categories)}개 카테고리 생성 성공!")
        for i, cat in enumerate(categories, 1):
            print(f"\n  [{i}] {cat.emoji} {cat.name}")
            print(f"      {cat.description}")
            print(f"      실용성: {cat.trend_score}/10, 연구활발도: {cat.research_activity}/10")
        
        # 테스트 2: 실용성 평가
        print("\n2. 실용성 평가 테스트...")
        score = client.evaluate_practicality(categories[0].name)
        print(f"✅ '{categories[0].name}' 실용성 점수: {score}/10")
        
        return categories[0]  # 첫 번째 카테고리 반환
    else:
        print("❌ 카테고리 생성 실패")
        return None

async def test_paper_discovery(category):
    """논문 검색 테스트"""
    print_section("논문 검색 테스트")
    
    if not category:
        print("❌ 카테고리가 없어 테스트 불가")
        return None
    
    client = GeminiClient()
    
    # 다양한 주제로 시도
    topics = ["아침 운동 효과", "7분 운동법", "운동 세트수 최적화"]
    
    for topic in topics:
        print(f"\n주제 '{topic}' 검색 중...")
        result = client.discover_papers_for_topic(category.name, topic)
        
        if result:
            print(f"✅ 논문 검색 성공!")
            print(f"   서브카테고리: {result.name}")
            print(f"   설명: {result.description}")
            print(f"   품질 등급: {result.quality_grade} ({result.quality_score}/100)")
            print(f"   논문 수: {len(result.papers)}개")
            
            for i, paper in enumerate(result.papers, 1):
                print(f"\n   논문 {i}:")
                print(f"   - 제목: {paper.title}")
                print(f"   - 저자: {paper.authors}")
                print(f"   - 저널: {paper.journal} ({paper.year})")
                print(f"   - Impact Factor: {paper.impact_factor}")
            
            print(f"\n   기대 효과: {result.expected_effect}")
            return result
        else:
            print(f"⚠️  '{topic}' 주제로는 논문을 찾을 수 없음")
    
    return None

async def test_content_generation(subcategory):
    """콘텐츠 생성 테스트"""
    print_section("콘텐츠 생성 테스트")
    
    if not subcategory:
        print("❌ 서브카테고리가 없어 테스트 불가")
        return
    
    client = GeminiClient()
    
    # 각 형식별로 콘텐츠 생성
    content_types = ["shorts", "article"]  # report는 시간이 오래 걸려서 제외
    
    for content_type in content_types:
        print(f"\n{content_type.upper()} 형식 생성 중...")
        start_time = time.time()
        
        result = client.generate_content(subcategory, content_type)
        
        generation_time = time.time() - start_time
        
        print(f"✅ {content_type} 생성 완료! (소요시간: {generation_time:.1f}초)")
        print(f"   품질 점수: {result['quality_score']}/100")
        print(f"   콘텐츠 길이: {len(result['content'])}자")
        print(f"\n   [미리보기]")
        print(f"   {result['content'][:200]}...")

def test_system_info():
    """시스템 정보 출력"""
    print_section("시스템 정보")
    
    # 환경 변수 확인
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key:
        print("✅ GEMINI_API_KEY 설정됨")
    else:
        print("❌ GEMINI_API_KEY 없음")
    
    # 파일 구조 확인
    paths = [
        "backend/app/main.py",
        "backend/data",
        "frontend/package.json",
        ".env"
    ]
    
    print("\n파일 구조 확인:")
    for path in paths:
        exists = Path(path).exists()
        status = "✅" if exists else "❌"
        print(f"{status} {path}")

async def main():
    """메인 테스트 실행"""
    print("🚀 Enhanced Dynamic Content System v6.1 - 통합 테스트")
    print("=" * 60)
    
    # 시스템 정보
    test_system_info()
    
    try:
        # 1. 카테고리 생성
        category = await test_category_generation()
        
        # 2. 논문 검색
        subcategory = await test_paper_discovery(category)
        
        # 3. 콘텐츠 생성
        await test_content_generation(subcategory)
        
        # 테스트 결과 저장
        print_section("테스트 완료")
        
        if category and subcategory:
            test_result = {
                "test_date": time.strftime("%Y-%m-%d %H:%M:%S"),
                "category": {
                    "name": category.name,
                    "description": category.description,
                    "practicality_score": category.trend_score
                },
                "subcategory": {
                    "name": subcategory.name,
                    "papers_count": len(subcategory.papers),
                    "quality_grade": subcategory.quality_grade
                },
                "status": "SUCCESS"
            }
            
            # 결과 저장
            os.makedirs("test_results", exist_ok=True)
            with open("test_results/system_test_result.json", "w", encoding="utf-8") as f:
                json.dump(test_result, f, ensure_ascii=False, indent=2)
            
            print("✅ 모든 테스트 성공!")
            print(f"📁 결과 저장: test_results/system_test_result.json")
        else:
            print("⚠️  일부 테스트 실패")
            
    except Exception as e:
        print(f"\n❌ 테스트 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())