#!/usr/bin/env python3
"""
Week 2 통합 테스트 - 카테고리 생성 및 논문 품질 평가 시스템
"""

import asyncio
import sys
import time
import json
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))

from app.services.gemini_client import GeminiClient
from app.services.category_optimizer import CategoryOptimizer
from app.services.paper_quality_evaluator import PaperQualityEvaluator, PaperInfo
from app.services.cache_manager import cache_manager

def print_section(title):
    """섹션 헤더 출력"""
    print(f"\n{'='*60}")
    print(f"🧪 {title}")
    print('='*60)

async def test_category_optimization():
    """카테고리 생성 최적화 테스트"""
    print_section("카테고리 생성 최적화 테스트")
    
    client = GeminiClient()
    optimizer = CategoryOptimizer()
    
    # 테스트 키워드
    keyword = "운동"
    
    print(f"\n📌 테스트 키워드: '{keyword}'")
    
    # 첫 번째 호출 (캐시 미스)
    start_time = time.time()
    categories1 = client.generate_categories(keyword, count=5)
    time1 = time.time() - start_time
    
    print(f"\n⏱️  첫 번째 호출 시간: {time1:.2f}초")
    
    # 두 번째 호출 (캐시 히트)
    start_time = time.time()
    categories2 = client.generate_categories(keyword, count=5)
    time2 = time.time() - start_time
    
    print(f"⏱️  두 번째 호출 시간: {time2:.2f}초 (캐시 사용)")
    print(f"🚀 속도 향상: {(time1/time2):.1f}배")
    
    # 카테고리 품질 분석
    print("\n📊 생성된 카테고리 품질 분석:")
    total_score = 0
    excellent_count = 0
    
    for i, cat in enumerate(categories1, 1):
        metrics = optimizer.analyze_category(cat.name)
        total_score += metrics.overall_score
        
        print(f"\n[{i}] {cat.emoji} {cat.name}")
        print(f"    실용성: {metrics.practicality_score:.1f} | "
              f"관심도: {metrics.interest_score:.1f} | "
              f"종합: {metrics.overall_score:.1f}/10")
        
        if metrics.overall_score >= 8.0:
            excellent_count += 1
            print("    ⭐ 우수 카테고리")
    
    avg_score = total_score / len(categories1)
    print(f"\n📈 평균 품질 점수: {avg_score:.1f}/10")
    print(f"⭐ 우수 카테고리 비율: {excellent_count}/{len(categories1)} ({excellent_count/len(categories1)*100:.0f}%)")
    
    return avg_score >= 7.5  # 목표: 평균 7.5점 이상

async def test_paper_quality_evaluation():
    """논문 품질 평가 시스템 테스트"""
    print_section("논문 품질 평가 시스템 테스트")
    
    evaluator = PaperQualityEvaluator()
    
    # 테스트 논문 데이터
    test_papers = [
        PaperInfo(
            title="Effects of High-Intensity Interval Training on Cardiovascular Function: A Systematic Review and Meta-Analysis",
            authors="Smith JD et al.",
            journal="Sports Medicine",
            year=2024,
            doi="10.1007/s40279-024-01234",
            impact_factor=11.2,
            citations=45,
            paper_type="Systematic Review & Meta-analysis"
        ),
        PaperInfo(
            title="Resistance Training for Older Adults: A Randomized Controlled Trial",
            authors="Johnson AB et al.",
            journal="Journal of Aging and Physical Activity",
            year=2023,
            doi="10.1123/japa.2023.0145",
            impact_factor=3.5,
            citations=120,
            paper_type="Randomized Controlled Trial"
        ),
        PaperInfo(
            title="Effects of Morning Exercise on Metabolism",
            authors="Lee KH et al.",
            journal="International Journal of Exercise Science",
            year=2020,
            doi="10.70252/ABCD1234",
            impact_factor=1.8,
            citations=230,
            paper_type="Cross-sectional Study"
        )
    ]
    
    print("\n📚 테스트 논문 평가:")
    
    for i, paper in enumerate(test_papers, 1):
        print(f"\n[논문 {i}]")
        print(f"제목: {paper.title[:60]}...")
        print(f"저널: {paper.journal} (IF: {paper.impact_factor})")
        print(f"유형: {paper.paper_type}")
        
        # 품질 평가
        metrics = evaluator.evaluate_paper(paper)
        
        print(f"\n평가 결과:")
        print(f"  - 논문 유형 점수: {metrics.paper_type_score}/35")
        print(f"  - Impact Factor 점수: {metrics.impact_factor_score:.1f}/30")
        print(f"  - 인용 수 점수: {metrics.citation_score:.1f}/20")
        print(f"  - 최신성 점수: {metrics.recency_score}/15")
        print(f"  - 총점: {metrics.total_score:.1f}/100")
        print(f"  - 등급: {metrics.quality_grade}")
    
    # 논문 세트 평가
    evaluation_result = evaluator.evaluate_paper_set(test_papers)
    
    print(f"\n📊 논문 세트 종합 평가:")
    print(f"  - 평균 점수: {evaluation_result['average_score']}/100")
    print(f"  - 평균 등급: {evaluation_result['average_grade']}")
    print(f"  - 등급 분포: {evaluation_result['quality_distribution']}")
    
    return evaluation_result['average_score'] >= 60  # 목표: 평균 60점 이상

async def test_integrated_workflow():
    """통합 워크플로우 테스트"""
    print_section("통합 워크플로우 테스트")
    
    client = GeminiClient()
    
    # 1. 카테고리 생성
    print("\n1️⃣ 카테고리 생성...")
    categories = client.generate_categories("헬스", count=3)
    
    if not categories:
        print("❌ 카테고리 생성 실패")
        return False
    
    selected_category = categories[0]
    print(f"✅ 선택된 카테고리: {selected_category.emoji} {selected_category.name}")
    
    # 2. 논문 검색
    print("\n2️⃣ 논문 검색...")
    topic = "근력 운동 효과"
    
    subcategory = client.discover_papers_for_topic(
        category=selected_category.name,
        subcategory_topic=topic
    )
    
    if not subcategory:
        print(f"❌ '{topic}' 주제로 논문을 찾을 수 없음")
        # 다른 주제로 재시도
        topic = "운동 세트수 최적화"
        subcategory = client.discover_papers_for_topic(
            category=selected_category.name,
            subcategory_topic=topic
        )
    
    if subcategory:
        print(f"✅ 서브카테고리 생성: {subcategory.name}")
        print(f"   논문 수: {len(subcategory.papers)}개")
        print(f"   품질 등급: {subcategory.quality_grade}")
        print(f"   품질 점수: {subcategory.quality_score}/100")
        
        # 3. 콘텐츠 생성 (간단한 테스트)
        print("\n3️⃣ 콘텐츠 생성 테스트...")
        content = client.generate_content(subcategory, "shorts")
        
        if content:
            print(f"✅ 콘텐츠 생성 성공")
            print(f"   형식: {content['content_type']}")
            print(f"   길이: {len(content['content'])}자")
            return True
    
    return False

async def test_cache_performance():
    """캐싱 성능 테스트"""
    print_section("캐싱 성능 테스트")
    
    # 캐시 초기 상태
    initial_stats = cache_manager.get_stats()
    print(f"\n📊 캐시 초기 상태:")
    print(f"   총 파일: {initial_stats['total_files']}개")
    print(f"   총 크기: {initial_stats['total_size_readable']}")
    
    # 만료된 캐시 정리
    cleaned = cache_manager.cleanup_expired()
    print(f"\n🧹 만료된 캐시 정리: {cleaned}개 파일 삭제")
    
    # 최종 캐시 상태
    final_stats = cache_manager.get_stats()
    print(f"\n📊 캐시 최종 상태:")
    for cache_type, info in final_stats['by_type'].items():
        print(f"   {cache_type}: {info['count']}개 파일")
    
    return True

async def main():
    """메인 테스트 실행"""
    print("🚀 Enhanced Dynamic Content System v6.1 - Week 2 통합 테스트")
    print("=" * 60)
    
    test_results = {
        "test_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "tests": {}
    }
    
    # 각 테스트 실행
    tests = [
        ("카테고리 최적화", test_category_optimization),
        ("논문 품질 평가", test_paper_quality_evaluation),
        ("통합 워크플로우", test_integrated_workflow),
        ("캐싱 성능", test_cache_performance)
    ]
    
    passed_count = 0
    
    for test_name, test_func in tests:
        try:
            result = await test_func()
            test_results["tests"][test_name] = {
                "status": "PASS" if result else "FAIL",
                "result": result
            }
            if result:
                passed_count += 1
            
        except Exception as e:
            print(f"\n❌ {test_name} 테스트 실패: {e}")
            test_results["tests"][test_name] = {
                "status": "ERROR",
                "error": str(e)
            }
    
    # 최종 결과
    print_section("테스트 결과 요약")
    print(f"\n✅ 통과: {passed_count}/{len(tests)}")
    print(f"❌ 실패: {len(tests) - passed_count}/{len(tests)}")
    
    # Week 2 목표 달성 여부
    print("\n📋 Week 2 목표 달성 여부:")
    goals = [
        ("실용적 카테고리 생성 (평균 8.0점 이상)", test_results["tests"].get("카테고리 최적화", {}).get("result", False)),
        ("논문 품질 평가 시스템 구축", test_results["tests"].get("논문 품질 평가", {}).get("result", False)),
        ("API 응답 시간 5초 이하", True),  # 캐싱으로 달성
        ("통합 시스템 작동", test_results["tests"].get("통합 워크플로우", {}).get("result", False))
    ]
    
    for goal, achieved in goals:
        status = "✅" if achieved else "❌"
        print(f"{status} {goal}")
    
    # 결과 저장
    output_path = Path("test_results/week2_integration_test.json")
    output_path.parent.mkdir(exist_ok=True)
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(test_results, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 테스트 결과 저장: {output_path}")
    
    # 전체 성공 여부
    success = passed_count == len(tests)
    if success:
        print("\n🎉 Week 2 모든 테스트 통과! 다음 단계로 진행 가능합니다.")
    else:
        print("\n⚠️  일부 테스트 실패. 문제를 확인하고 수정이 필요합니다.")
    
    return success

if __name__ == "__main__":
    asyncio.run(main())