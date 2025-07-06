#!/usr/bin/env python3
"""
카테고리 생성 최적화 테스트
"""

import asyncio
import sys
from pathlib import Path
import json
import time

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))

from app.services.gemini_client import GeminiClient
from app.services.category_optimizer import CategoryOptimizer

def print_category_analysis(category_name: str, optimizer: CategoryOptimizer):
    """카테고리 상세 분석 출력"""
    metrics = optimizer.analyze_category(category_name)
    
    print(f"\n📊 카테고리 분석: {category_name}")
    print(f"  - 숫자/시간 포함: {'✅' if metrics.has_number else '❌'}")
    print(f"  - 대상 명시: {'✅' if metrics.has_target else '❌'}")
    print(f"  - 혜택 표현: {'✅' if metrics.has_benefit else '❌'}")
    print(f"  - 행동 가능: {'✅' if metrics.has_action else '❌'}")
    print(f"  - 구체성 점수: {metrics.specificity_score:.1f}/10")
    print(f"  - 클릭유도 점수: {metrics.clickability_score:.1f}/10")
    print(f"  - 실용성 점수: {metrics.practicality_score:.1f}/10")
    print(f"  - 관심도 점수: {metrics.interest_score:.1f}/10")
    print(f"  - **종합 점수: {metrics.overall_score:.1f}/10**")

async def test_category_generation():
    """카테고리 생성 테스트"""
    print("🧪 카테고리 생성 최적화 테스트")
    print("=" * 60)
    
    client = GeminiClient()
    optimizer = CategoryOptimizer()
    
    # 다양한 키워드 테스트
    test_keywords = ["운동", "다이어트", "건강", "피트니스"]
    
    all_results = []
    
    for keyword in test_keywords:
        print(f"\n\n🎯 키워드: '{keyword}'")
        print("-" * 40)
        
        start_time = time.time()
        
        # 카테고리 생성
        categories = client.generate_categories(keyword, count=5)
        
        generation_time = time.time() - start_time
        
        if categories:
            print(f"✅ {len(categories)}개 카테고리 생성 완료 (소요시간: {generation_time:.1f}초)")
            
            keyword_results = {
                "keyword": keyword,
                "generation_time": generation_time,
                "categories": []
            }
            
            for i, cat in enumerate(categories, 1):
                print(f"\n[{i}] {cat.emoji} {cat.name}")
                print(f"    {cat.description}")
                
                # 상세 분석
                print_category_analysis(cat.name, optimizer)
                
                # 결과 저장
                metrics = optimizer.analyze_category(cat.name)
                keyword_results["categories"].append({
                    "name": cat.name,
                    "description": cat.description,
                    "emoji": cat.emoji,
                    "metrics": {
                        "overall_score": round(metrics.overall_score, 1),
                        "practicality": round(metrics.practicality_score, 1),
                        "interest": round(metrics.interest_score, 1),
                        "clickability": round(metrics.clickability_score, 1),
                        "has_number": metrics.has_number,
                        "has_target": metrics.has_target,
                        "has_benefit": metrics.has_benefit,
                        "has_action": metrics.has_action
                    }
                })
            
            # 평균 점수 계산
            avg_score = sum(
                optimizer.analyze_category(cat.name).overall_score 
                for cat in categories
            ) / len(categories)
            
            keyword_results["average_score"] = round(avg_score, 1)
            all_results.append(keyword_results)
            
            print(f"\n📈 '{keyword}' 평균 점수: {avg_score:.1f}/10")
            
        else:
            print(f"❌ '{keyword}' 카테고리 생성 실패")
    
    # 전체 결과 저장
    print("\n\n" + "=" * 60)
    print("📊 전체 테스트 결과")
    print("=" * 60)
    
    total_categories = sum(len(r["categories"]) for r in all_results)
    overall_avg_score = sum(r["average_score"] for r in all_results) / len(all_results)
    
    print(f"✅ 총 {total_categories}개 카테고리 생성")
    print(f"📈 전체 평균 점수: {overall_avg_score:.1f}/10")
    
    # 우수 카테고리 (8점 이상)
    excellent_categories = []
    for result in all_results:
        for cat in result["categories"]:
            if cat["metrics"]["overall_score"] >= 8.0:
                excellent_categories.append(cat)
    
    print(f"⭐ 우수 카테고리 (8점 이상): {len(excellent_categories)}개")
    
    if excellent_categories:
        print("\n🏆 TOP 5 카테고리:")
        sorted_categories = sorted(
            excellent_categories, 
            key=lambda x: x["metrics"]["overall_score"], 
            reverse=True
        )[:5]
        
        for i, cat in enumerate(sorted_categories, 1):
            print(f"{i}. {cat['emoji']} {cat['name']} (점수: {cat['metrics']['overall_score']})")
    
    # 결과 파일 저장
    test_result = {
        "test_date": time.strftime("%Y-%m-%d %H:%M:%S"),
        "results_by_keyword": all_results,
        "summary": {
            "total_categories": total_categories,
            "overall_average_score": overall_avg_score,
            "excellent_count": len(excellent_categories),
            "test_keywords": test_keywords
        }
    }
    
    output_path = Path("test_results/category_optimization_test.json")
    output_path.parent.mkdir(exist_ok=True)
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(test_result, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 테스트 결과 저장: {output_path}")
    
    # 개선 제안
    print("\n\n💡 개선 제안:")
    if overall_avg_score < 7.5:
        print("- 전체 평균 점수가 낮습니다. 프롬프트 개선이 필요합니다.")
    
    low_scoring_patterns = []
    for result in all_results:
        for cat in result["categories"]:
            if cat["metrics"]["overall_score"] < 7.0:
                if not cat["metrics"]["has_number"]:
                    low_scoring_patterns.append("숫자 부족")
                if not cat["metrics"]["has_target"]:
                    low_scoring_patterns.append("대상 불명확")
                if not cat["metrics"]["has_benefit"]:
                    low_scoring_patterns.append("혜택 미표현")
    
    if low_scoring_patterns:
        from collections import Counter
        pattern_counts = Counter(low_scoring_patterns)
        print("- 주요 문제 패턴:")
        for pattern, count in pattern_counts.most_common(3):
            print(f"  • {pattern}: {count}회")

if __name__ == "__main__":
    asyncio.run(test_category_generation())