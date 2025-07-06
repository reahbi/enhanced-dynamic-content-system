"""
통합 테스트 - 전체 시스템 검증
"""

import pytest
import asyncio
from typing import List, Dict, Any
from datetime import datetime

from ..services.category_optimizer import CategoryOptimizer
from ..services.paper_quality_evaluator import PaperQualityEvaluator, QualityGrade
from ..services.cache_manager import CacheManager
from ..services.content_generators.shorts_generator import ShortsScriptGenerator
from ..services.content_generators.article_generator import ArticleGenerator
from ..services.content_generators.report_generator import ReportGenerator
from ..services.thinking.thinking_integration import ThinkingEnabledContentGenerator
from ..services.thinking.prompt_engineering import ContentType

class IntegrationTestSuite:
    """통합 테스트 스위트"""
    
    def __init__(self):
        self.category_optimizer = CategoryOptimizer()
        self.paper_evaluator = PaperQualityEvaluator()
        self.cache_manager = CacheManager()
        self.thinking_generator = ThinkingEnabledContentGenerator()
        self.test_results = []
        
    async def run_all_tests(self):
        """모든 통합 테스트 실행"""
        print("🧪 통합 테스트 시작...")
        print("=" * 80)
        
        # 테스트 시나리오들
        test_scenarios = [
            self.test_category_to_content_flow,
            self.test_paper_quality_integration,
            self.test_cache_performance,
            self.test_thinking_mode_integration,
            self.test_multi_format_generation,
            self.test_error_handling,
            self.test_performance_benchmarks
        ]
        
        for test_func in test_scenarios:
            await test_func()
            
        # 결과 요약
        self._print_test_summary()
        
    async def test_category_to_content_flow(self):
        """카테고리 생성부터 콘텐츠 생성까지 전체 플로우 테스트"""
        print("\n📝 테스트 1: 카테고리 → 콘텐츠 전체 플로우")
        print("-" * 60)
        
        start_time = datetime.now()
        
        try:
            # 1. 카테고리 생성
            categories = await self.category_optimizer.generate_categories("복부 운동")
            assert len(categories) > 0, "카테고리 생성 실패"
            
            selected_category = categories[0]
            print(f"✅ 카테고리 생성: {selected_category['name']}")
            
            # 2. 논문 검색 및 평가
            papers = self._get_mock_papers()
            evaluated_papers = []
            
            for paper in papers:
                quality_info = self.paper_evaluator.evaluate_paper(paper)
                if quality_info.grade in [QualityGrade.A_PLUS, QualityGrade.A, QualityGrade.B_PLUS]:
                    evaluated_papers.append(paper)
                    
            print(f"✅ 고품질 논문 선별: {len(evaluated_papers)}개")
            
            # 3. 콘텐츠 생성
            result = await self.thinking_generator.generate_with_thinking(
                content_type=ContentType.SHORTS,
                topic=selected_category['name'],
                papers=evaluated_papers,
                target_audience='general'
            )
            
            assert result['content'] is not None, "콘텐츠 생성 실패"
            print(f"✅ 콘텐츠 생성 완료 (품질: {result['content'].quality_score:.1f}/100)")
            
            elapsed = (datetime.now() - start_time).total_seconds()
            
            self.test_results.append({
                'test': 'category_to_content_flow',
                'success': True,
                'elapsed_time': elapsed,
                'details': {
                    'categories_generated': len(categories),
                    'papers_evaluated': len(papers),
                    'quality_papers': len(evaluated_papers),
                    'content_quality': result['content'].quality_score
                }
            })
            
        except Exception as e:
            print(f"❌ 테스트 실패: {str(e)}")
            self.test_results.append({
                'test': 'category_to_content_flow',
                'success': False,
                'error': str(e)
            })
    
    async def test_paper_quality_integration(self):
        """논문 품질 평가 시스템 통합 테스트"""
        print("\n📝 테스트 2: 논문 품질 평가 통합")
        print("-" * 60)
        
        try:
            papers = self._get_diverse_papers()
            quality_distribution = {
                'A+': 0, 'A': 0, 'B+': 0, 'B': 0, 'C': 0, 'D': 0
            }
            
            for paper in papers:
                quality_info = self.paper_evaluator.evaluate_paper(paper)
                quality_distribution[quality_info.grade.value] += 1
                
            print("✅ 품질 등급 분포:")
            for grade, count in quality_distribution.items():
                if count > 0:
                    print(f"   - {grade} 등급: {count}개")
                    
            # 검증: 다양한 등급이 나왔는지
            unique_grades = sum(1 for count in quality_distribution.values() if count > 0)
            assert unique_grades >= 3, "품질 평가가 너무 단순함"
            
            self.test_results.append({
                'test': 'paper_quality_integration',
                'success': True,
                'details': quality_distribution
            })
            
        except Exception as e:
            print(f"❌ 테스트 실패: {str(e)}")
            self.test_results.append({
                'test': 'paper_quality_integration',
                'success': False,
                'error': str(e)
            })
    
    async def test_cache_performance(self):
        """캐시 성능 테스트"""
        print("\n📝 테스트 3: 캐시 성능")
        print("-" * 60)
        
        try:
            # 캐시 없이 생성
            topic = "HIIT 운동법"
            
            start_no_cache = datetime.now()
            result1 = await self._generate_content_no_cache(topic)
            time_no_cache = (datetime.now() - start_no_cache).total_seconds()
            
            # 캐시에 저장
            cache_key = f"content_{topic}_shorts"
            self.cache_manager.set(cache_key, result1, ttl=3600)
            
            # 캐시에서 읽기
            start_with_cache = datetime.now()
            cached_result = self.cache_manager.get(cache_key)
            time_with_cache = (datetime.now() - start_with_cache).total_seconds()
            
            assert cached_result is not None, "캐시 읽기 실패"
            
            improvement = ((time_no_cache - time_with_cache) / time_no_cache) * 100
            print(f"✅ 캐시 없이: {time_no_cache:.3f}초")
            print(f"✅ 캐시 사용: {time_with_cache:.3f}초")
            print(f"✅ 성능 향상: {improvement:.1f}%")
            
            self.test_results.append({
                'test': 'cache_performance',
                'success': True,
                'details': {
                    'time_no_cache': time_no_cache,
                    'time_with_cache': time_with_cache,
                    'improvement_percent': improvement
                }
            })
            
        except Exception as e:
            print(f"❌ 테스트 실패: {str(e)}")
            self.test_results.append({
                'test': 'cache_performance',
                'success': False,
                'error': str(e)
            })
    
    async def test_thinking_mode_integration(self):
        """Native Thinking Mode 통합 테스트"""
        print("\n📝 테스트 4: Native Thinking Mode 통합")
        print("-" * 60)
        
        try:
            papers = self._get_mock_papers()[:2]
            
            # Thinking Mode 활성화
            result_with = await self.thinking_generator.generate_with_thinking(
                content_type=ContentType.ARTICLE,
                topic="근육 회복을 위한 영양 전략",
                papers=papers,
                target_audience='general'
            )
            
            thinking_quality = result_with['thinking']['quality_score']
            content_quality = result_with['content'].quality_score
            
            print(f"✅ 사고 품질: {thinking_quality:.1f}/100")
            print(f"✅ 콘텐츠 품질: {content_quality:.1f}/100")
            print(f"✅ 사고 패턴: {', '.join(result_with['thinking']['patterns'])}")
            
            assert thinking_quality >= 60, "사고 품질이 너무 낮음"
            assert content_quality >= 70, "콘텐츠 품질이 너무 낮음"
            
            self.test_results.append({
                'test': 'thinking_mode_integration',
                'success': True,
                'details': {
                    'thinking_quality': thinking_quality,
                    'content_quality': content_quality,
                    'thinking_patterns': result_with['thinking']['patterns']
                }
            })
            
        except Exception as e:
            print(f"❌ 테스트 실패: {str(e)}")
            self.test_results.append({
                'test': 'thinking_mode_integration',
                'success': False,
                'error': str(e)
            })
    
    async def test_multi_format_generation(self):
        """멀티 포맷 생성 테스트"""
        print("\n📝 테스트 5: 멀티 포맷 생성")
        print("-" * 60)
        
        try:
            topic = "코어 강화 운동의 중요성"
            papers = self._get_mock_papers()[:2]
            
            formats = [ContentType.SHORTS, ContentType.ARTICLE, ContentType.REPORT]
            results = {}
            
            for format_type in formats:
                result = await self.thinking_generator.generate_with_thinking(
                    content_type=format_type,
                    topic=topic,
                    papers=papers,
                    target_audience='general'
                )
                
                results[format_type.value] = {
                    'quality': result['content'].quality_score,
                    'length': len(result['content'].total_content)
                }
                
            print("✅ 생성 결과:")
            for format_name, data in results.items():
                print(f"   - {format_name}: 품질 {data['quality']:.1f}/100, 길이 {data['length']}자")
                
            # 각 포맷이 적절한 길이인지 검증
            assert 200 <= results['shorts']['length'] <= 500, "숏츠 길이 부적절"
            assert 1500 <= results['article']['length'] <= 3500, "아티클 길이 부적절"
            assert 3000 <= results['report']['length'] <= 6000, "리포트 길이 부적절"
            
            self.test_results.append({
                'test': 'multi_format_generation',
                'success': True,
                'details': results
            })
            
        except Exception as e:
            print(f"❌ 테스트 실패: {str(e)}")
            self.test_results.append({
                'test': 'multi_format_generation',
                'success': False,
                'error': str(e)
            })
    
    async def test_error_handling(self):
        """에러 처리 테스트"""
        print("\n📝 테스트 6: 에러 처리")
        print("-" * 60)
        
        error_cases = []
        
        # 케이스 1: 빈 논문 리스트
        try:
            result = await self.thinking_generator.generate_with_thinking(
                content_type=ContentType.SHORTS,
                topic="테스트 주제",
                papers=[],  # 빈 리스트
                target_audience='general'
            )
            error_cases.append(('empty_papers', 'handled'))
        except Exception:
            error_cases.append(('empty_papers', 'error'))
            
        # 케이스 2: 잘못된 콘텐츠 타입
        try:
            result = await self.thinking_generator.generate_with_thinking(
                content_type="invalid_type",  # 잘못된 타입
                topic="테스트 주제",
                papers=self._get_mock_papers(),
                target_audience='general'
            )
            error_cases.append(('invalid_type', 'handled'))
        except Exception:
            error_cases.append(('invalid_type', 'error'))
            
        print("✅ 에러 처리 결과:")
        for case, result in error_cases:
            print(f"   - {case}: {result}")
            
        self.test_results.append({
            'test': 'error_handling',
            'success': True,
            'details': dict(error_cases)
        })
    
    async def test_performance_benchmarks(self):
        """성능 벤치마크 테스트"""
        print("\n📝 테스트 7: 성능 벤치마크")
        print("-" * 60)
        
        try:
            benchmarks = {}
            papers = self._get_mock_papers()[:3]
            
            # 각 콘텐츠 타입별 생성 시간 측정
            for content_type in [ContentType.SHORTS, ContentType.ARTICLE, ContentType.REPORT]:
                start_time = datetime.now()
                
                result = await self.thinking_generator.generate_with_thinking(
                    content_type=content_type,
                    topic="벤치마크 테스트",
                    papers=papers,
                    target_audience='general'
                )
                
                elapsed = (datetime.now() - start_time).total_seconds()
                benchmarks[content_type.value] = elapsed
                
            print("✅ 생성 시간:")
            for content_type, time in benchmarks.items():
                print(f"   - {content_type}: {time:.2f}초")
                
            # 성능 기준 검증
            assert benchmarks['shorts'] < 5, "숏츠 생성이 너무 느림"
            assert benchmarks['article'] < 10, "아티클 생성이 너무 느림"
            assert benchmarks['report'] < 15, "리포트 생성이 너무 느림"
            
            self.test_results.append({
                'test': 'performance_benchmarks',
                'success': True,
                'details': benchmarks
            })
            
        except Exception as e:
            print(f"❌ 테스트 실패: {str(e)}")
            self.test_results.append({
                'test': 'performance_benchmarks',
                'success': False,
                'error': str(e)
            })
    
    def _print_test_summary(self):
        """테스트 결과 요약"""
        print("\n" + "=" * 80)
        print("📊 통합 테스트 결과 요약")
        print("=" * 80)
        
        successful = sum(1 for t in self.test_results if t.get('success', False))
        total = len(self.test_results)
        
        print(f"성공: {successful}/{total} ({successful/total*100:.1f}%)")
        print("\n상세 결과:")
        
        for result in self.test_results:
            status = "✅" if result.get('success') else "❌"
            print(f"{status} {result['test']}")
            
            if result.get('success') and 'details' in result:
                for key, value in result['details'].items():
                    print(f"   - {key}: {value}")
            elif 'error' in result:
                print(f"   - Error: {result['error']}")
                
    async def _generate_content_no_cache(self, topic: str):
        """캐시 없이 콘텐츠 생성 (테스트용)"""
        papers = self._get_mock_papers()[:2]
        generator = ShortsScriptGenerator()
        return generator.generate(topic, papers, target_audience='general')
    
    def _get_mock_papers(self) -> List[Any]:
        """테스트용 모의 논문 데이터"""
        class MockPaper:
            def __init__(self, **kwargs):
                self.title = kwargs.get('title')
                self.authors = kwargs.get('authors')
                self.journal = kwargs.get('journal')
                self.year = kwargs.get('year')
                self.impact_factor = kwargs.get('impact_factor')
                self.citations = kwargs.get('citations', 0)
                self.paper_type = kwargs.get('paper_type', 'Original Research')
                self.doi = kwargs.get('doi', 'mock-doi')
                
        return [
            MockPaper(
                title="Effects of HIIT on Abdominal Fat Loss",
                authors="Smith J, Johnson K",
                journal="Sports Medicine",
                year=2024,
                impact_factor=11.2,
                citations=45,
                paper_type="Systematic Review"
            ),
            MockPaper(
                title="Protein Timing for Muscle Recovery",
                authors="Lee S, Park H",
                journal="Journal of Sports Science",
                year=2023,
                impact_factor=3.5,
                citations=22,
                paper_type="RCT"
            ),
            MockPaper(
                title="Core Training Methods Comparison",
                authors="Wilson R, Davis M",
                journal="Exercise Science Review",
                year=2023,
                impact_factor=5.8,
                citations=67,
                paper_type="Meta-analysis"
            )
        ]
    
    def _get_diverse_papers(self) -> List[Any]:
        """다양한 품질의 논문 데이터"""
        base_papers = self._get_mock_papers()
        
        # 다양한 품질의 논문 추가
        class MockPaper:
            def __init__(self, **kwargs):
                for key, value in kwargs.items():
                    setattr(self, key, value)
                    
        diverse_papers = base_papers + [
            MockPaper(
                title="Low Quality Study",
                authors="Unknown",
                journal="Predatory Journal",
                year=2020,
                impact_factor=0.5,
                citations=2,
                paper_type="Case Report"
            ),
            MockPaper(
                title="Medium Quality Research",
                authors="Brown A",
                journal="Regional Sports Journal",
                year=2022,
                impact_factor=2.1,
                citations=15,
                paper_type="Cross-sectional"
            )
        ]
        
        return diverse_papers


# 테스트 실행 함수
async def run_integration_tests():
    """통합 테스트 실행"""
    suite = IntegrationTestSuite()
    await suite.run_all_tests()

if __name__ == "__main__":
    asyncio.run(run_integration_tests())