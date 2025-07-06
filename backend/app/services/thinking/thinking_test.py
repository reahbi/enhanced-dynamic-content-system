"""
Native Thinking Mode 테스트 및 검증
"""

import asyncio
from typing import Dict, List, Any
from datetime import datetime

from .thinking_integration import ThinkingEnabledContentGenerator
from .prompt_engineering import ContentType

class ThinkingModeTest:
    """Native Thinking Mode 테스트"""
    
    def __init__(self):
        self.generator = ThinkingEnabledContentGenerator()
        self.test_results = []
        
    async def run_all_tests(self):
        """모든 테스트 실행"""
        print("🧪 Native Thinking Mode 테스트 시작...")
        print("=" * 60)
        
        # 테스트 케이스들
        test_cases = [
            {
                'name': 'Shorts Script Generation',
                'content_type': ContentType.SHORTS,
                'topic': 'HIIT vs 일반 유산소: 뱃살 감량 효과',
                'papers': self._get_sample_papers(),
                'target_audience': 'general'
            },
            {
                'name': 'Article Generation',
                'content_type': ContentType.ARTICLE,
                'topic': '근육 성장을 위한 최적의 단백질 섭취 타이밍',
                'papers': self._get_sample_papers(),
                'target_audience': 'beginner'
            },
            {
                'name': 'Report Generation',
                'content_type': ContentType.REPORT,
                'topic': '웨이트 트레이닝이 노년층 건강에 미치는 영향',
                'papers': self._get_sample_papers(),
                'target_audience': 'expert'
            }
        ]
        
        for test_case in test_cases:
            await self._run_single_test(test_case)
            
        # 결과 요약
        self._print_summary()
        
    async def _run_single_test(self, test_case: Dict[str, Any]):
        """단일 테스트 실행"""
        print(f"\n📝 테스트: {test_case['name']}")
        print("-" * 40)
        
        start_time = datetime.now()
        
        try:
            # 콘텐츠 생성
            result = await self.generator.generate_with_thinking(
                content_type=test_case['content_type'],
                topic=test_case['topic'],
                papers=test_case['papers'],
                target_audience=test_case['target_audience']
            )
            
            end_time = datetime.now()
            elapsed_time = (end_time - start_time).total_seconds()
            
            # 결과 분석
            thinking_data = result['thinking']
            content_data = result['content']
            
            test_result = {
                'test_name': test_case['name'],
                'success': True,
                'thinking_quality': thinking_data['quality_score'],
                'thinking_depth': thinking_data['depth_level'],
                'thinking_patterns': thinking_data['patterns'],
                'content_quality': content_data.quality_score,
                'generation_time': elapsed_time,
                'key_insights': len(thinking_data['key_insights'])
            }
            
            self.test_results.append(test_result)
            
            # 결과 출력
            self._print_test_result(test_result, thinking_data)
            
        except Exception as e:
            print(f"❌ 테스트 실패: {str(e)}")
            self.test_results.append({
                'test_name': test_case['name'],
                'success': False,
                'error': str(e)
            })
    
    def _print_test_result(self, result: Dict[str, Any], thinking_data: Dict[str, Any]):
        """테스트 결과 출력"""
        print(f"✅ 테스트 성공")
        print(f"   - 사고 품질: {result['thinking_quality']:.1f}/100")
        print(f"   - 사고 깊이: {'⭐' * result['thinking_depth']} (Level {result['thinking_depth']})")
        print(f"   - 사고 패턴: {', '.join(result['thinking_patterns'])}")
        print(f"   - 핵심 인사이트: {result['key_insights']}개")
        print(f"   - 콘텐츠 품질: {result['content_quality']:.1f}/100")
        print(f"   - 생성 시간: {result['generation_time']:.2f}초")
        
        # 사고 과정 일부 출력
        analysis = thinking_data['analysis']
        if analysis.strengths:
            print(f"   - 강점: {', '.join(analysis.strengths[:3])}")
        if analysis.weaknesses:
            print(f"   - 개선점: {', '.join(analysis.weaknesses[:2])}")
    
    def _print_summary(self):
        """전체 테스트 요약"""
        print("\n" + "=" * 60)
        print("📊 테스트 요약")
        print("=" * 60)
        
        successful_tests = [t for t in self.test_results if t.get('success', False)]
        
        if successful_tests:
            avg_thinking_quality = sum(t['thinking_quality'] for t in successful_tests) / len(successful_tests)
            avg_thinking_depth = sum(t['thinking_depth'] for t in successful_tests) / len(successful_tests)
            avg_content_quality = sum(t['content_quality'] for t in successful_tests) / len(successful_tests)
            avg_generation_time = sum(t['generation_time'] for t in successful_tests) / len(successful_tests)
            
            print(f"성공률: {len(successful_tests)}/{len(self.test_results)} ({len(successful_tests)/len(self.test_results)*100:.1f}%)")
            print(f"평균 사고 품질: {avg_thinking_quality:.1f}/100")
            print(f"평균 사고 깊이: {avg_thinking_depth:.1f}/5")
            print(f"평균 콘텐츠 품질: {avg_content_quality:.1f}/100")
            print(f"평균 생성 시간: {avg_generation_time:.2f}초")
            
            # 가장 많이 사용된 사고 패턴
            all_patterns = []
            for test in successful_tests:
                all_patterns.extend(test.get('thinking_patterns', []))
            
            if all_patterns:
                from collections import Counter
                pattern_counts = Counter(all_patterns)
                print(f"\n주요 사고 패턴:")
                for pattern, count in pattern_counts.most_common(3):
                    print(f"   - {pattern}: {count}회")
        else:
            print("❌ 모든 테스트 실패")
    
    def _get_sample_papers(self) -> List[Any]:
        """테스트용 샘플 논문 데이터"""
        class SamplePaper:
            def __init__(self, title, authors, journal, year, impact_factor, key_findings):
                self.title = title
                self.authors = authors
                self.journal = journal
                self.year = year
                self.impact_factor = impact_factor
                self.key_findings = key_findings
        
        return [
            SamplePaper(
                title="High-intensity interval training reduces abdominal adipose tissue",
                authors="Smith, J. et al.",
                journal="Sports Medicine",
                year=2024,
                impact_factor=11.2,
                key_findings="HIIT showed 3x more effective fat loss compared to MICT"
            ),
            SamplePaper(
                title="Effects of exercise timing on muscle protein synthesis",
                authors="Johnson, K. et al.",
                journal="Journal of Sports Science",
                year=2023,
                impact_factor=3.5,
                key_findings="Post-workout protein intake within 30 minutes maximizes MPS"
            )
        ]


async def main():
    """메인 테스트 실행"""
    tester = ThinkingModeTest()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())