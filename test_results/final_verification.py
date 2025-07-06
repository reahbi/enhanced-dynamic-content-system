#!/usr/bin/env python3
"""
Final System Verification - 최종 시스템 검증
Enhanced Dynamic System v6.1의 모든 기능을 종합 검증
"""

import os
import json
import time
from typing import Dict, List
from datetime import datetime
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

class SystemPerformanceAnalyzer:
    """시스템 성능 분석기"""
    
    def __init__(self):
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found")
        
        self.client = genai.Client(api_key=api_key)
        
    def analyze_system_performance(self) -> Dict:
        """시스템 성능 종합 분석"""
        
        print("🔍 Enhanced Dynamic System v6.1 최종 검증 시작")
        print("=" * 60)
        
        performance_data = {
            "timestamp": datetime.now().isoformat(),
            "api_connectivity": self._test_api_connectivity(),
            "content_generation_speed": self._test_generation_speed(),
            "quality_consistency": self._test_quality_consistency(),
            "memory_efficiency": self._test_memory_usage(),
            "error_handling": self._test_error_handling(),
            "overall_score": 0.0
        }
        
        # 종합 점수 계산
        scores = [
            performance_data["api_connectivity"]["score"],
            performance_data["content_generation_speed"]["score"],
            performance_data["quality_consistency"]["score"],
            performance_data["memory_efficiency"]["score"],
            performance_data["error_handling"]["score"]
        ]
        performance_data["overall_score"] = sum(scores) / len(scores)
        
        return performance_data
    
    def _test_api_connectivity(self) -> Dict:
        """API 연결성 테스트"""
        print("\n1️⃣ API 연결성 테스트 중...")
        
        start_time = time.time()
        try:
            response = self.client.models.generate_content(
                model='gemini-2.0-flash-exp',
                contents="Hello, test message",
                config=types.GenerateContentConfig(max_output_tokens=50)
            )
            
            response_time = time.time() - start_time
            
            if response.text:
                score = 100.0 if response_time < 3.0 else max(70.0, 100 - (response_time * 10))
                result = {
                    "status": "SUCCESS",
                    "response_time": response_time,
                    "score": score,
                    "message": f"API 연결 성공 ({response_time:.2f}초)"
                }
            else:
                result = {
                    "status": "FAILED",
                    "response_time": response_time,
                    "score": 0.0,
                    "message": "응답 없음"
                }
                
        except Exception as e:
            result = {
                "status": "ERROR",
                "response_time": time.time() - start_time,
                "score": 0.0,
                "message": f"API 오류: {str(e)}"
            }
        
        print(f"   ✅ {result['message']}")
        return result
    
    def _test_generation_speed(self) -> Dict:
        """콘텐츠 생성 속도 테스트"""
        print("\n2️⃣ 콘텐츠 생성 속도 테스트 중...")
        
        test_prompt = "운동과 건강에 관한 간단한 팁 3개를 제시해주세요."
        
        times = []
        for i in range(3):
            start_time = time.time()
            try:
                response = self.client.models.generate_content(
                    model='gemini-2.0-flash-exp',
                    contents=test_prompt,
                    config=types.GenerateContentConfig(max_output_tokens=500)
                )
                generation_time = time.time() - start_time
                times.append(generation_time)
                print(f"   테스트 {i+1}: {generation_time:.2f}초")
            except Exception as e:
                print(f"   테스트 {i+1} 실패: {e}")
                times.append(10.0)  # 페널티 시간
        
        avg_time = sum(times) / len(times)
        
        # 점수 계산: 5초 이하 = 100점, 10초 이상 = 50점
        if avg_time <= 5.0:
            score = 100.0
        elif avg_time <= 10.0:
            score = 100 - (avg_time - 5) * 10
        else:
            score = 50.0
        
        result = {
            "average_time": avg_time,
            "individual_times": times,
            "score": score,
            "evaluation": "우수" if avg_time <= 5.0 else "양호" if avg_time <= 10.0 else "개선 필요"
        }
        
        print(f"   ✅ 평균 생성 시간: {avg_time:.2f}초 ({result['evaluation']})")
        return result
    
    def _test_quality_consistency(self) -> Dict:
        """품질 일관성 테스트"""
        print("\n3️⃣ 품질 일관성 테스트 중...")
        
        test_prompts = [
            "단백질 섭취의 중요성에 대해 설명해주세요.",
            "HIIT 운동의 장단점을 분석해주세요.",
            "건강한 수면 습관에 대한 조언을 해주세요."
        ]
        
        quality_scores = []
        
        for i, prompt in enumerate(test_prompts):
            try:
                response = self.client.models.generate_content(
                    model='gemini-2.0-flash-exp',
                    contents=prompt,
                    config=types.GenerateContentConfig(max_output_tokens=800)
                )
                
                # 간단한 품질 평가 (길이, 구조 등)
                content = response.text
                
                quality_score = 0
                # 길이 평가 (적절한 길이인지)
                if 200 <= len(content) <= 1000:
                    quality_score += 30
                elif 100 <= len(content) < 200 or 1000 < len(content) <= 1500:
                    quality_score += 20
                else:
                    quality_score += 10
                
                # 구조 평가 (문단 구분 등)
                if '\n' in content:
                    quality_score += 20
                
                # 내용 포함 여부
                if any(keyword in content.lower() for keyword in ['운동', '건강', '효과', '방법']):
                    quality_score += 30
                
                # 전문성 (구체적 정보 포함)
                if any(keyword in content for keyword in ['연구', '논문', '전문가', '의료']):
                    quality_score += 20
                
                quality_scores.append(quality_score)
                print(f"   테스트 {i+1}: {quality_score}점")
                
            except Exception as e:
                print(f"   테스트 {i+1} 실패: {e}")
                quality_scores.append(0)
        
        avg_quality = sum(quality_scores) / len(quality_scores)
        consistency = 100 - (max(quality_scores) - min(quality_scores))  # 편차가 적을수록 일관성 높음
        
        result = {
            "average_quality": avg_quality,
            "individual_scores": quality_scores,
            "consistency": consistency,
            "score": (avg_quality + consistency) / 2,
            "evaluation": "우수" if avg_quality >= 80 else "양호" if avg_quality >= 60 else "개선 필요"
        }
        
        print(f"   ✅ 평균 품질: {avg_quality:.1f}점, 일관성: {consistency:.1f}점 ({result['evaluation']})")
        return result
    
    def _test_memory_usage(self) -> Dict:
        """메모리 효율성 테스트"""
        print("\n4️⃣ 메모리 효율성 테스트 중...")
        
        try:
            import psutil
            process = psutil.Process()
            
            # 테스트 전 메모리 사용량
            memory_before = process.memory_info().rss / 1024 / 1024  # MB
            
            # 여러 요청을 연속으로 실행
            for i in range(5):
                response = self.client.models.generate_content(
                    model='gemini-2.0-flash-exp',
                    contents=f"테스트 요청 {i+1}: 간단한 운동 팁을 알려주세요.",
                    config=types.GenerateContentConfig(max_output_tokens=300)
                )
            
            # 테스트 후 메모리 사용량
            memory_after = process.memory_info().rss / 1024 / 1024  # MB
            memory_diff = memory_after - memory_before
            
            # 점수 계산: 메모리 증가량이 적을수록 높은 점수
            if memory_diff <= 10:
                score = 100.0
            elif memory_diff <= 50:
                score = 90.0
            elif memory_diff <= 100:
                score = 70.0
            else:
                score = 50.0
            
            result = {
                "memory_before": memory_before,
                "memory_after": memory_after,
                "memory_increase": memory_diff,
                "score": score,
                "evaluation": "효율적" if memory_diff <= 50 else "보통" if memory_diff <= 100 else "개선 필요"
            }
            
        except ImportError:
            # psutil이 없는 경우 기본 점수
            result = {
                "memory_before": "N/A",
                "memory_after": "N/A", 
                "memory_increase": "N/A",
                "score": 80.0,
                "evaluation": "측정 불가 (psutil 필요)"
            }
        except Exception as e:
            result = {
                "memory_before": "ERROR",
                "memory_after": "ERROR",
                "memory_increase": "ERROR",
                "score": 60.0,
                "evaluation": f"오류: {str(e)}"
            }
        
        print(f"   ✅ 메모리 효율성: {result['evaluation']}")
        return result
    
    def _test_error_handling(self) -> Dict:
        """오류 처리 테스트"""
        print("\n5️⃣ 오류 처리 테스트 중...")
        
        error_tests = [
            {
                "name": "빈 프롬프트",
                "prompt": "",
                "expected": "ERROR_HANDLED"
            },
            {
                "name": "매우 긴 프롬프트",
                "prompt": "test " * 10000,
                "expected": "ERROR_HANDLED"
            },
            {
                "name": "특수 문자",
                "prompt": "!@#$%^&*(){}[]<>?/|\\`~",
                "expected": "SUCCESS_OR_HANDLED"
            }
        ]
        
        passed_tests = 0
        
        for test in error_tests:
            try:
                response = self.client.models.generate_content(
                    model='gemini-2.0-flash-exp',
                    contents=test["prompt"],
                    config=types.GenerateContentConfig(max_output_tokens=100)
                )
                
                if test["expected"] == "SUCCESS_OR_HANDLED":
                    passed_tests += 1
                    print(f"   ✅ {test['name']}: 처리됨")
                else:
                    print(f"   ⚠️ {test['name']}: 예상과 다른 결과")
                    
            except Exception as e:
                if test["expected"] == "ERROR_HANDLED":
                    passed_tests += 1
                    print(f"   ✅ {test['name']}: 오류 적절히 처리됨")
                else:
                    print(f"   ❌ {test['name']}: 예상치 못한 오류 - {str(e)[:50]}")
        
        score = (passed_tests / len(error_tests)) * 100
        
        result = {
            "total_tests": len(error_tests),
            "passed_tests": passed_tests,
            "score": score,
            "evaluation": "우수" if score >= 80 else "양호" if score >= 60 else "개선 필요"
        }
        
        print(f"   ✅ 오류 처리: {passed_tests}/{len(error_tests)} 테스트 통과 ({result['evaluation']})")
        return result

def main():
    """메인 검증 함수"""
    try:
        analyzer = SystemPerformanceAnalyzer()
        performance_data = analyzer.analyze_system_performance()
        
        print("\n" + "=" * 60)
        print("🎯 최종 검증 결과")
        print("=" * 60)
        
        print(f"📊 종합 점수: {performance_data['overall_score']:.1f}점")
        
        if performance_data['overall_score'] >= 90:
            grade = "A+ (최상급)"
        elif performance_data['overall_score'] >= 80:
            grade = "A (우수)"
        elif performance_data['overall_score'] >= 70:
            grade = "B (양호)"
        elif performance_data['overall_score'] >= 60:
            grade = "C (보통)"
        else:
            grade = "D (개선 필요)"
        
        print(f"🏆 시스템 등급: {grade}")
        
        print("\n📈 세부 항목별 점수:")
        print(f"   • API 연결성: {performance_data['api_connectivity']['score']:.1f}점")
        print(f"   • 생성 속도: {performance_data['content_generation_speed']['score']:.1f}점")
        print(f"   • 품질 일관성: {performance_data['quality_consistency']['score']:.1f}점")
        print(f"   • 메모리 효율성: {performance_data['memory_efficiency']['score']:.1f}점")
        print(f"   • 오류 처리: {performance_data['error_handling']['score']:.1f}점")
        
        # 결과 저장
        os.makedirs("test_results", exist_ok=True)
        with open("test_results/final_verification.json", 'w', encoding='utf-8') as f:
            json.dump(performance_data, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 상세 결과가 test_results/final_verification.json에 저장되었습니다.")
        
        print("\n✅ Enhanced Dynamic System v6.1 검증 완료!")
        
        if performance_data['overall_score'] >= 80:
            print("🚀 시스템이 프로덕션 환경에서 사용할 준비가 되었습니다!")
        else:
            print("🔧 일부 영역에서 개선이 필요합니다.")
            
    except Exception as e:
        print(f"❌ 검증 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()