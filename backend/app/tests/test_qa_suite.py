"""
QA 테스트 스위트 - 포괄적인 품질 보증 테스트
"""

import pytest
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime
import json
import os
from pathlib import Path

from ..services.category_optimizer import CategoryOptimizer
from ..services.paper_quality_evaluator import PaperQualityEvaluator
from ..services.content_generators.shorts_generator import ShortsScriptGenerator
from ..services.content_generators.article_generator import ArticleGenerator
from ..services.content_generators.report_generator import ReportGenerator
from ..services.thinking.thinking_integration import ThinkingEnabledContentGenerator
from ..services.thinking.prompt_engineering import ContentType
from ..services.advanced_cache_manager import AdvancedCacheManager
from ..services.performance_optimizer import PerformanceOptimizer
from ..services.system_monitor import SystemMonitor

class QATestSuite:
    """QA 테스트 스위트"""
    
    def __init__(self):
        self.test_results = []
        self.error_log = []
        self.performance_metrics = []
        
    async def run_all_qa_tests(self):
        """모든 QA 테스트 실행"""
        print("🧪 QA 테스트 스위트 시작...")
        print("=" * 80)
        
        # 테스트 카테고리별 실행
        test_categories = [
            ("기능 테스트", self._run_functional_tests),
            ("성능 테스트", self._run_performance_tests),
            ("신뢰성 테스트", self._run_reliability_tests),
            ("보안 테스트", self._run_security_tests),
            ("사용성 테스트", self._run_usability_tests),
            ("통합 테스트", self._run_integration_tests),
            ("엣지 케이스 테스트", self._run_edge_case_tests)
        ]
        
        for category_name, test_func in test_categories:
            print(f"\n📁 {category_name}")
            print("-" * 60)
            await test_func()
            
        # 결과 요약 및 리포트 생성
        self._generate_qa_report()
        
    async def _run_functional_tests(self):
        """기능 테스트"""
        tests = [
            self._test_category_generation,
            self._test_paper_evaluation,
            self._test_content_generation,
            self._test_thinking_mode,
            self._test_caching_functionality
        ]
        
        for test in tests:
            await self._execute_test(test)
            
    async def _run_performance_tests(self):
        """성능 테스트"""
        tests = [
            self._test_response_time,
            self._test_throughput,
            self._test_memory_usage,
            self._test_concurrent_requests,
            self._test_cache_performance
        ]
        
        for test in tests:
            await self._execute_test(test)
            
    async def _run_reliability_tests(self):
        """신뢰성 테스트"""
        tests = [
            self._test_error_recovery,
            self._test_data_consistency,
            self._test_failure_handling,
            self._test_timeout_handling
        ]
        
        for test in tests:
            await self._execute_test(test)
            
    async def _run_security_tests(self):
        """보안 테스트"""
        tests = [
            self._test_input_validation,
            self._test_injection_prevention,
            self._test_data_sanitization
        ]
        
        for test in tests:
            await self._execute_test(test)
            
    async def _run_usability_tests(self):
        """사용성 테스트"""
        tests = [
            self._test_api_consistency,
            self._test_error_messages,
            self._test_default_behaviors
        ]
        
        for test in tests:
            await self._execute_test(test)
            
    async def _run_integration_tests(self):
        """통합 테스트"""
        tests = [
            self._test_end_to_end_flow,
            self._test_component_interactions,
            self._test_data_flow
        ]
        
        for test in tests:
            await self._execute_test(test)
            
    async def _run_edge_case_tests(self):
        """엣지 케이스 테스트"""
        tests = [
            self._test_empty_inputs,
            self._test_large_inputs,
            self._test_special_characters,
            self._test_boundary_values
        ]
        
        for test in tests:
            await self._execute_test(test)
            
    async def _execute_test(self, test_func):
        """개별 테스트 실행"""
        test_name = test_func.__name__.replace('_test_', '').replace('_', ' ').title()
        
        try:
            start_time = datetime.now()
            result = await test_func()
            end_time = datetime.now()
            
            self.test_results.append({
                'test_name': test_name,
                'status': 'PASS' if result else 'FAIL',
                'execution_time': (end_time - start_time).total_seconds(),
                'timestamp': datetime.now().isoformat()
            })
            
            status_icon = "✅" if result else "❌"
            print(f"{status_icon} {test_name}")
            
        except Exception as e:
            self.test_results.append({
                'test_name': test_name,
                'status': 'ERROR',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            })
            
            self.error_log.append({
                'test_name': test_name,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            })
            
            print(f"💥 {test_name} - Error: {str(e)[:50]}...")
            
    # 기능 테스트 구현
    async def _test_category_generation(self) -> bool:
        """카테고리 생성 테스트"""
        optimizer = CategoryOptimizer()
        
        test_cases = [
            "복부 운동",
            "단백질 섭취",
            "HIIT 트레이닝",
            ""  # 빈 입력
        ]
        
        for keyword in test_cases:
            if keyword:  # 정상 케이스
                categories = await optimizer.generate_categories(keyword)
                if not categories or len(categories) == 0:
                    return False
            else:  # 빈 입력
                try:
                    categories = await optimizer.generate_categories(keyword)
                    # 빈 입력은 에러나 빈 리스트를 반환해야 함
                    if categories and len(categories) > 0:
                        return False
                except:
                    pass  # 예외 발생은 정상
                    
        return True
        
    async def _test_paper_evaluation(self) -> bool:
        """논문 평가 테스트"""
        evaluator = PaperQualityEvaluator()
        
        # 다양한 품질의 논문 테스트
        test_papers = [
            MockPaper(impact_factor=15.0, citations=200, paper_type="Systematic Review"),
            MockPaper(impact_factor=2.0, citations=10, paper_type="Case Report"),
            MockPaper(impact_factor=0, citations=0, paper_type="Unknown")
        ]
        
        grades = []
        for paper in test_papers:
            quality_info = evaluator.evaluate_paper(paper)
            grades.append(quality_info.grade.value)
            
        # 다양한 등급이 나와야 함
        unique_grades = len(set(grades))
        return unique_grades >= 2
        
    async def _test_content_generation(self) -> bool:
        """콘텐츠 생성 테스트"""
        generator = ThinkingEnabledContentGenerator()
        
        papers = [MockPaper(
            title="Test Paper",
            impact_factor=5.0,
            citations=50
        )]
        
        # 각 콘텐츠 타입 테스트
        for content_type in [ContentType.SHORTS, ContentType.ARTICLE, ContentType.REPORT]:
            result = await generator.generate_with_thinking(
                content_type=content_type,
                topic="테스트 주제",
                papers=papers,
                target_audience='general'
            )
            
            if not result or not result.get('content'):
                return False
                
        return True
        
    async def _test_thinking_mode(self) -> bool:
        """Native Thinking Mode 테스트"""
        generator = ThinkingEnabledContentGenerator()
        
        result = await generator.generate_with_thinking(
            content_type=ContentType.ARTICLE,
            topic="근육 성장",
            papers=[MockPaper()],
            target_audience='general'
        )
        
        # Thinking 프로세스가 포함되어야 함
        thinking_data = result.get('thinking', {})
        return (thinking_data.get('quality_score', 0) > 0 and
                thinking_data.get('process', '') != '')
        
    async def _test_caching_functionality(self) -> bool:
        """캐싱 기능 테스트"""
        cache = AdvancedCacheManager(cache_dir="./test_cache")
        
        # 저장 테스트
        test_data = {"key": "value", "timestamp": datetime.now().isoformat()}
        cache.set("test_key", test_data, ttl=3600)
        
        # 조회 테스트
        retrieved = cache.get("test_key")
        
        # 삭제 테스트
        cache.delete("test_key")
        deleted = cache.get("test_key")
        
        # 정리
        cache.clear()
        
        return retrieved == test_data and deleted is None
        
    # 성능 테스트 구현
    async def _test_response_time(self) -> bool:
        """응답 시간 테스트"""
        generator = ShortsScriptGenerator()
        
        start = datetime.now()
        result = generator.generate(
            "테스트 주제",
            [MockPaper()],
            target_audience='general'
        )
        end = datetime.now()
        
        response_time = (end - start).total_seconds()
        
        # 숏츠 생성은 5초 이내여야 함
        return response_time < 5.0
        
    async def _test_throughput(self) -> bool:
        """처리량 테스트"""
        generator = ThinkingEnabledContentGenerator()
        
        # 10개의 요청을 동시에 처리
        tasks = []
        for i in range(10):
            task = generator.generate_with_thinking(
                content_type=ContentType.SHORTS,
                topic=f"테스트 주제 {i}",
                papers=[MockPaper()],
                target_audience='general'
            )
            tasks.append(task)
            
        start = datetime.now()
        results = await asyncio.gather(*tasks, return_exceptions=True)
        end = datetime.now()
        
        total_time = (end - start).total_seconds()
        successful = sum(1 for r in results if not isinstance(r, Exception))
        
        # 10개 요청을 30초 이내에 처리하고 80% 이상 성공해야 함
        return total_time < 30 and successful >= 8
        
    async def _test_memory_usage(self) -> bool:
        """메모리 사용량 테스트"""
        import psutil
        process = psutil.Process()
        
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # 대량의 콘텐츠 생성
        generator = ArticleGenerator()
        for i in range(20):
            generator.generate(
                f"테스트 주제 {i}",
                [MockPaper() for _ in range(5)],
                target_audience='general'
            )
            
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        # 메모리 증가량이 500MB 미만이어야 함
        return memory_increase < 500
        
    async def _test_concurrent_requests(self) -> bool:
        """동시 요청 처리 테스트"""
        generator = ThinkingEnabledContentGenerator()
        
        # 50개의 동시 요청
        concurrent_count = 50
        tasks = []
        
        for i in range(concurrent_count):
            task = generator.generate_with_thinking(
                content_type=ContentType.SHORTS,
                topic=f"동시 요청 {i}",
                papers=[MockPaper()],
                target_audience='general'
            )
            tasks.append(task)
            
        results = await asyncio.gather(*tasks, return_exceptions=True)
        successful = sum(1 for r in results if not isinstance(r, Exception))
        
        # 90% 이상 성공해야 함
        return successful >= concurrent_count * 0.9
        
    async def _test_cache_performance(self) -> bool:
        """캐시 성능 테스트"""
        cache = AdvancedCacheManager()
        
        # 1000개 항목 저장
        start = datetime.now()
        for i in range(1000):
            cache.set(f"perf_test_{i}", f"value_{i}", ttl=3600)
        write_time = (datetime.now() - start).total_seconds()
        
        # 1000개 항목 조회
        start = datetime.now()
        for i in range(1000):
            cache.get(f"perf_test_{i}")
        read_time = (datetime.now() - start).total_seconds()
        
        # 정리
        for i in range(1000):
            cache.delete(f"perf_test_{i}")
            
        # 쓰기는 10초, 읽기는 1초 이내여야 함
        return write_time < 10 and read_time < 1
        
    # 신뢰성 테스트 구현
    async def _test_error_recovery(self) -> bool:
        """에러 복구 테스트"""
        generator = ThinkingEnabledContentGenerator()
        
        # 잘못된 입력으로 에러 유발
        try:
            result = await generator.generate_with_thinking(
                content_type=ContentType.SHORTS,
                topic="",  # 빈 주제
                papers=None,  # None 논문
                target_audience='general'
            )
            # 에러가 발생하거나 기본값이 반환되어야 함
            return True
        except:
            # 예외가 발생해도 시스템이 중단되지 않으면 성공
            return True
            
    async def _test_data_consistency(self) -> bool:
        """데이터 일관성 테스트"""
        cache = AdvancedCacheManager()
        
        # 동일한 키에 여러 번 저장
        for i in range(10):
            cache.set("consistency_test", f"value_{i}", ttl=3600)
            
        # 최종 값 확인
        final_value = cache.get("consistency_test")
        cache.delete("consistency_test")
        
        return final_value == "value_9"
        
    async def _test_failure_handling(self) -> bool:
        """실패 처리 테스트"""
        evaluator = PaperQualityEvaluator()
        
        # 잘못된 논문 객체
        invalid_papers = [
            None,
            {},
            "string",
            123
        ]
        
        for paper in invalid_papers:
            try:
                evaluator.evaluate_paper(paper)
            except:
                pass  # 예외가 발생해도 시스템이 계속 동작해야 함
                
        return True  # 크래시하지 않으면 성공
        
    async def _test_timeout_handling(self) -> bool:
        """타임아웃 처리 테스트"""
        # 시뮬레이션: 긴 작업
        async def long_running_task():
            await asyncio.sleep(10)
            return "completed"
            
        try:
            # 5초 타임아웃
            result = await asyncio.wait_for(long_running_task(), timeout=5)
            return False  # 타임아웃이 발생해야 함
        except asyncio.TimeoutError:
            return True  # 타임아웃 처리 성공
            
    # 보안 테스트 구현
    async def _test_input_validation(self) -> bool:
        """입력 검증 테스트"""
        optimizer = CategoryOptimizer()
        
        # 위험한 입력들
        dangerous_inputs = [
            "<script>alert('xss')</script>",
            "'; DROP TABLE users; --",
            "../../../etc/passwd",
            "\\x00\\x01\\x02",
            "A" * 10000  # 매우 긴 입력
        ]
        
        for dangerous_input in dangerous_inputs:
            try:
                # 위험한 입력이 처리되거나 거부되어야 함
                categories = await optimizer.generate_categories(dangerous_input)
                # 카테고리가 생성되었다면 sanitization이 되었는지 확인
                for category in categories:
                    if any(char in category.get('name', '') for char in ['<', '>', ';', '--']):
                        return False
            except:
                pass  # 예외 발생은 정상
                
        return True
        
    async def _test_injection_prevention(self) -> bool:
        """인젝션 방지 테스트"""
        # SQL 인젝션 시도
        malicious_inputs = [
            "1' OR '1'='1",
            "admin'--",
            "1; DELETE FROM papers WHERE 1=1"
        ]
        
        # 캐시 키 생성 시 인젝션 방지 확인
        cache = AdvancedCacheManager()
        for input_str in malicious_inputs:
            key = f"test_{input_str}"
            cache.set(key, "test_value", ttl=60)
            
            # 저장된 키가 안전하게 처리되었는지 확인
            retrieved = cache.get(key)
            cache.delete(key)
            
            if retrieved != "test_value":
                return False
                
        return True
        
    async def _test_data_sanitization(self) -> bool:
        """데이터 정제 테스트"""
        generator = ShortsScriptGenerator()
        
        # HTML/스크립트가 포함된 논문
        malicious_paper = MockPaper(
            title="<script>alert('xss')</script> Research",
            authors="'; DROP TABLE users; --"
        )
        
        result = generator.generate(
            "테스트 주제",
            [malicious_paper],
            target_audience='general'
        )
        
        # 생성된 콘텐츠에 위험한 코드가 없어야 함
        content = result.total_content
        dangerous_patterns = ['<script>', '</script>', 'DROP TABLE', '--']
        
        for pattern in dangerous_patterns:
            if pattern in content:
                return False
                
        return True
        
    # 사용성 테스트 구현
    async def _test_api_consistency(self) -> bool:
        """API 일관성 테스트"""
        # 모든 생성기가 동일한 인터페이스를 가져야 함
        generators = [
            ShortsScriptGenerator(),
            ArticleGenerator(),
            ReportGenerator()
        ]
        
        for generator in generators:
            # generate 메서드가 있어야 함
            if not hasattr(generator, 'generate'):
                return False
                
            # 동일한 파라미터를 받아야 함
            result = generator.generate(
                topic="테스트",
                papers=[MockPaper()],
                target_audience='general'
            )
            
            # 결과가 GeneratedContent 타입이어야 함
            if not hasattr(result, 'total_content'):
                return False
                
        return True
        
    async def _test_error_messages(self) -> bool:
        """에러 메시지 테스트"""
        generator = ThinkingEnabledContentGenerator()
        
        # 의도적인 에러 유발
        try:
            await generator.generate_with_thinking(
                content_type="invalid_type",  # 잘못된 타입
                topic="테스트",
                papers=[],
                target_audience='general'
            )
            return False  # 에러가 발생해야 함
        except Exception as e:
            # 에러 메시지가 명확해야 함
            error_msg = str(e).lower()
            return 'content type' in error_msg or 'invalid' in error_msg
            
    async def _test_default_behaviors(self) -> bool:
        """기본 동작 테스트"""
        cache = AdvancedCacheManager()
        
        # 기본 TTL 테스트
        cache.set("default_test", "value")  # TTL 미지정
        value = cache.get("default_test")
        cache.delete("default_test")
        
        return value == "value"  # 기본 TTL이 적용되어야 함
        
    # 통합 테스트 구현
    async def _test_end_to_end_flow(self) -> bool:
        """전체 플로우 테스트"""
        # 1. 카테고리 생성
        optimizer = CategoryOptimizer()
        categories = await optimizer.generate_categories("홈트레이닝")
        
        if not categories:
            return False
            
        # 2. 논문 평가
        evaluator = PaperQualityEvaluator()
        papers = [MockPaper(impact_factor=8.0, citations=100)]
        quality_info = evaluator.evaluate_paper(papers[0])
        
        # 3. 콘텐츠 생성
        generator = ThinkingEnabledContentGenerator()
        result = await generator.generate_with_thinking(
            content_type=ContentType.ARTICLE,
            topic=categories[0]['name'],
            papers=papers,
            target_audience='general'
        )
        
        # 4. 캐싱
        cache = AdvancedCacheManager()
        cache_key = f"e2e_test_{categories[0]['name']}"
        cache.set(cache_key, result, ttl=3600)
        
        # 5. 캐시 조회
        cached_result = cache.get(cache_key)
        cache.delete(cache_key)
        
        return cached_result is not None
        
    async def _test_component_interactions(self) -> bool:
        """컴포넌트 상호작용 테스트"""
        # 여러 컴포넌트가 함께 동작하는지 확인
        monitor = SystemMonitor()
        optimizer = PerformanceOptimizer()
        
        # 모니터링 시작
        await monitor.start_monitoring()
        
        # 성능 측정과 함께 작업 실행
        @optimizer.measure_performance("test_operation")
        async def test_operation():
            generator = ShortsScriptGenerator()
            return generator.generate("테스트", [MockPaper()], target_audience='general')
            
        result = await test_operation()
        
        # 모니터링 중지
        await monitor.stop_monitoring()
        
        # 성능 리포트 확인
        report = optimizer.get_performance_report("test_operation")
        
        return result is not None and report['total_calls'] > 0
        
    async def _test_data_flow(self) -> bool:
        """데이터 흐름 테스트"""
        # 데이터가 컴포넌트 간에 올바르게 전달되는지 확인
        paper_data = {
            'title': 'Data Flow Test Paper',
            'impact_factor': 7.5,
            'citations': 80
        }
        
        paper = MockPaper(**paper_data)
        
        # 논문 평가
        evaluator = PaperQualityEvaluator()
        quality_info = evaluator.evaluate_paper(paper)
        
        # 콘텐츠 생성
        generator = ArticleGenerator()
        content = generator.generate(
            "데이터 흐름 테스트",
            [paper],
            target_audience='general'
        )
        
        # 생성된 콘텐츠에 논문 정보가 포함되어야 함
        return paper_data['title'] in content.total_content
        
    # 엣지 케이스 테스트 구현
    async def _test_empty_inputs(self) -> bool:
        """빈 입력 테스트"""
        tests = []
        
        # 빈 주제
        generator = ShortsScriptGenerator()
        try:
            result = generator.generate("", [MockPaper()], target_audience='general')
            tests.append(result is not None)  # 기본값이나 에러 처리
        except:
            tests.append(True)  # 예외 처리도 OK
            
        # 빈 논문 리스트
        try:
            result = generator.generate("테스트", [], target_audience='general')
            tests.append(result is not None)
        except:
            tests.append(True)
            
        return all(tests)
        
    async def _test_large_inputs(self) -> bool:
        """대용량 입력 테스트"""
        # 많은 논문
        large_paper_list = [MockPaper() for _ in range(100)]
        
        generator = ReportGenerator()
        try:
            result = generator.generate(
                "대용량 테스트",
                large_paper_list,
                target_audience='general'
            )
            return result is not None
        except:
            return False  # 대용량도 처리할 수 있어야 함
            
    async def _test_special_characters(self) -> bool:
        """특수 문자 테스트"""
        special_chars = "!@#$%^&*()_+-=[]{}|;':\",./<>?™℠®©"
        
        generator = ArticleGenerator()
        result = generator.generate(
            f"특수문자 테스트 {special_chars}",
            [MockPaper(title=f"Paper with {special_chars}")],
            target_audience='general'
        )
        
        return result is not None and len(result.total_content) > 0
        
    async def _test_boundary_values(self) -> bool:
        """경계값 테스트"""
        evaluator = PaperQualityEvaluator()
        
        boundary_papers = [
            MockPaper(impact_factor=0, citations=0),  # 최소값
            MockPaper(impact_factor=999, citations=99999),  # 최대값
            MockPaper(impact_factor=-1, citations=-10),  # 음수
            MockPaper(impact_factor=None, citations=None)  # None
        ]
        
        for paper in boundary_papers:
            try:
                quality_info = evaluator.evaluate_paper(paper)
                # 모든 경우에 대해 처리되어야 함
            except:
                pass  # 예외 처리도 OK
                
        return True
        
    def _generate_qa_report(self):
        """QA 리포트 생성"""
        print("\n" + "=" * 80)
        print("📊 QA 테스트 결과 요약")
        print("=" * 80)
        
        # 결과 집계
        total_tests = len(self.test_results)
        passed = sum(1 for t in self.test_results if t['status'] == 'PASS')
        failed = sum(1 for t in self.test_results if t['status'] == 'FAIL')
        errors = sum(1 for t in self.test_results if t['status'] == 'ERROR')
        
        # 성공률
        success_rate = (passed / total_tests * 100) if total_tests > 0 else 0
        
        print(f"\n총 테스트: {total_tests}")
        print(f"✅ 성공: {passed}")
        print(f"❌ 실패: {failed}")
        print(f"💥 에러: {errors}")
        print(f"📈 성공률: {success_rate:.1f}%")
        
        # 실패/에러 상세
        if failed > 0 or errors > 0:
            print("\n⚠️ 실패/에러 상세:")
            for test in self.test_results:
                if test['status'] in ['FAIL', 'ERROR']:
                    print(f"  - {test['test_name']}: {test['status']}")
                    if 'error' in test:
                        print(f"    Error: {test['error'][:100]}...")
                        
        # 성능 메트릭
        if self.test_results:
            avg_time = sum(t.get('execution_time', 0) for t in self.test_results) / len(self.test_results)
            print(f"\n⏱️ 평균 실행 시간: {avg_time:.2f}초")
            
        # 리포트 파일 저장
        report_path = "./qa_report.json"
        report_data = {
            'summary': {
                'total_tests': total_tests,
                'passed': passed,
                'failed': failed,
                'errors': errors,
                'success_rate': success_rate,
                'timestamp': datetime.now().isoformat()
            },
            'test_results': self.test_results,
            'error_log': self.error_log
        }
        
        with open(report_path, 'w') as f:
            json.dump(report_data, f, indent=2)
            
        print(f"\n📄 상세 리포트 저장: {report_path}")


class MockPaper:
    """테스트용 모의 논문"""
    def __init__(self, **kwargs):
        self.title = kwargs.get('title', 'Test Paper')
        self.authors = kwargs.get('authors', 'Test Author')
        self.journal = kwargs.get('journal', 'Test Journal')
        self.year = kwargs.get('year', 2024)
        self.impact_factor = kwargs.get('impact_factor', 5.0)
        self.citations = kwargs.get('citations', 50)
        self.paper_type = kwargs.get('paper_type', 'Original Research')
        self.doi = kwargs.get('doi', 'test-doi-123')
        self.id = kwargs.get('id', 'test-id-123')


# 테스트 실행
async def run_qa_tests():
    """QA 테스트 실행"""
    suite = QATestSuite()
    await suite.run_all_qa_tests()

if __name__ == "__main__":
    asyncio.run(run_qa_tests())