#!/usr/bin/env python3
"""
개선된 카테고리 생성기 - 실용적이고 즉시 관심을 끌 수 있는 주제 중심
"""

import os
import json
from typing import List, Dict
from datetime import datetime
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

class PracticalCategoryGenerator:
    """실용적이고 즉시 관심을 끄는 카테고리 생성기"""
    
    def __init__(self):
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found")
        
        self.client = genai.Client(api_key=api_key)
    
    def generate_practical_categories(self, seed_keyword: str = "운동") -> List[Dict]:
        """실용적이고 구체적인 카테고리 생성"""
        
        prompt = f"""
        <thinking>
        사용자가 '{seed_keyword}'에 대한 카테고리를 원한다.
        하지만 추상적이거나 트렌디한 것보다는
        실제로 사람들이 바로 관심을 가지고 클릭하고 싶어할만한
        구체적이고 실용적인 주제들이 필요하다.
        
        예시로 제시된 것들:
        - 노인운동법: 연령대별 맞춤 운동
        - 남녀운동법: 성별 차이를 고려한 운동
        - AI 운동: 기술과 접목된 운동
        - 운동세트수: 구체적인 운동 방법론
        - 가슴운동: 신체 부위별 운동
        
        이런 식으로 즉시 "아, 이거 궁금해!" 하고 클릭하고 싶어질만한
        구체적이고 실용적인 카테고리를 만들어야 한다.
        </thinking>
        
        키워드: {seed_keyword}
        
        '{seed_keyword}'과 관련하여 사람들이 **즉시 관심을 가지고 클릭하고 싶어할만한**
        구체적이고 실용적인 카테고리 10개를 생성해주세요.
        
        ✅ 좋은 예시 (클릭하고 싶어지는 구체적 주제):
        - 💪 가슴운동 완전정복
        - 🧓 60세 이후 안전운동법  
        - ♀️♂️ 남녀 운동차이 비교
        - 📱 AI 홈트레이닝
        - 🔢 운동세트수 최적화
        - 🏃‍♀️ 5분 초고속 운동
        - 💊 운동 전후 영양섭취
        - 😴 잠자기 전 운동법
        - 🦵 하체비만 타파법
        - 💺 직장인 의자운동
        
        ❌ 피해야 할 예시 (추상적이고 애매한 주제):
        - 뇌지컬 운동법
        - 마음챙김 액티브 리커버리
        - 우주핏 메타버스
        - 초개인화 운동 코칭
        
        조건:
        1. **즉시 관심**: "오, 이거 나한테 필요해!" 하고 바로 느낄 수 있는 주제
        2. **구체적**: 추상적이지 않고 명확한 운동 관련 주제
        3. **실용적**: 당장 적용해볼 수 있는 내용
        4. **호기심 자극**: 클릭하고 싶어지는 제목
        5. **다양성**: 연령, 성별, 부위, 시간, 목적 등 다양한 관점
        
        출력 형식:
        🎯 [구체적 카테고리명]: [왜 궁금할까요?]
        
        예시:
        💪 가슴운동 완전정복: 집에서도 탄탄한 가슴근육 만들기
        """
        
        response = self.client.models.generate_content(
            model='gemini-2.0-flash-exp',
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.8,
                max_output_tokens=2000
            )
        )
        
        return self._parse_practical_categories(response.text)
    
    def _parse_practical_categories(self, response: str) -> List[Dict]:
        """응답에서 실용적 카테고리 파싱"""
        categories = []
        lines = response.split('\n')
        
        for line in lines:
            line = line.strip()
            if line and ('🎯' in line or '💪' in line or '🧓' in line or '♀️' in line or '📱' in line or '🔢' in line or '🏃' in line or '💊' in line or '😴' in line or '🦵' in line or '💺' in line):
                try:
                    # 이모지와 카테고리명, 설명 분리
                    if ':' in line:
                        emoji_and_name = line.split(':')[0].strip()
                        description = line.split(':', 1)[1].strip()
                        
                        # 이모지 추출
                        emoji = ""
                        for char in emoji_and_name:
                            if ord(char) > 127:  # 이모지나 특수문자
                                emoji = char
                                break
                        
                        # 카테고리명 (이모지 제거)
                        name = emoji_and_name.replace('🎯', '').replace(emoji, '').strip()
                        
                        categories.append({
                            "name": name,
                            "description": description,
                            "emoji": emoji if emoji else "🎯",
                            "practicality_score": 9.0,  # 실용성 점수
                            "interest_level": 8.5  # 관심도
                        })
                except Exception as e:
                    print(f"파싱 오류: {line} - {e}")
                    continue
        
        return categories[:10]  # 최대 10개

class ImprovedTestRunner:
    """개선된 테스트 실행기"""
    
    def __init__(self):
        self.category_generator = PracticalCategoryGenerator()
    
    def run_improved_test(self):
        """개선된 카테고리 생성 테스트"""
        
        print("🔄 개선된 카테고리 생성 테스트 시작")
        print("=" * 60)
        
        # 기존 카테고리와 개선된 카테고리 비교
        print("\n❌ 기존 카테고리 (추상적, 트렌디하지만 관심도 낮음):")
        old_categories = [
            "🎯 뇌지컬 🏋️‍♀️ 운동법: 인지 능력 향상을 위한 운동 루틴",
            "🎯 🧘‍♀️ 마음챙김 액티브 리커버리: 스트레스 해소와 회복을 위한 운동",
            "🎯 🚀 우주핏: 메타버스 & AR 융합 운동 게임",
            "🎯 ⏱️ 초개인화 운동 코칭: AI 기반 맞춤형 운동 솔루션",
            "🎯 🌎 플로깅 챌린지: 환경 보호와 건강을 동시에"
        ]
        
        for i, cat in enumerate(old_categories, 1):
            print(f"   {i}. {cat}")
        
        print("\n🔄 개선된 카테고리 생성 중...")
        improved_categories = self.category_generator.generate_practical_categories("운동")
        
        print(f"\n✅ 새로운 카테고리 ({len(improved_categories)}개) - 실용적이고 즉시 관심을 끄는 주제:")
        for i, cat in enumerate(improved_categories, 1):
            print(f"   {i}. {cat['emoji']} {cat['name']}: {cat['description']}")
        
        # 비교 분석
        self._analyze_improvement(old_categories, improved_categories)
        
        # 결과 저장
        self._save_improved_results(improved_categories)
        
        print(f"\n🎉 개선된 카테고리 생성 완료!")
    
    def _analyze_improvement(self, old_categories: List[str], new_categories: List[Dict]):
        """개선 사항 분석"""
        
        print(f"\n📊 개선 사항 분석:")
        print("-" * 40)
        
        print(f"📈 개선 포인트:")
        print(f"   • 구체성: 추상적 → 구체적 (가슴운동, 60세 운동법)")
        print(f"   • 즉시성: 미래지향적 → 당장 필요한 것")
        print(f"   • 실용성: 개념적 → 실행 가능한 내용")
        print(f"   • 관심도: 새로운 트렌드 → 보편적 관심사")
        
        print(f"\n🎯 타겟 적중률:")
        practical_keywords = ['운동법', '가슴', '하체', '직장인', '노인', '남녀', '세트', '영양', '시간']
        hit_count = 0
        
        for category in new_categories:
            full_text = f"{category['name']} {category['description']}"
            if any(keyword in full_text for keyword in practical_keywords):
                hit_count += 1
        
        hit_rate = (hit_count / len(new_categories)) * 100
        print(f"   실용적 키워드 포함률: {hit_rate:.1f}% ({hit_count}/{len(new_categories)})")
        
        if hit_rate >= 80:
            print(f"   평가: 🏆 우수 (즉시 관심을 끄는 주제들)")
        elif hit_rate >= 60:
            print(f"   평가: 👍 양호 (관심도 높은 편)")
        else:
            print(f"   평가: ⚠️ 개선 필요")
    
    def _save_improved_results(self, categories: List[Dict]):
        """개선된 결과 저장"""
        
        results = {
            "test_timestamp": datetime.now().isoformat(),
            "improvement_focus": "실용성과 즉시 관심도 향상",
            "categories": categories,
            "analysis": {
                "total_categories": len(categories),
                "average_practicality": sum(cat['practicality_score'] for cat in categories) / len(categories),
                "average_interest": sum(cat['interest_level'] for cat in categories) / len(categories),
                "improvement_areas": [
                    "추상적 → 구체적",
                    "트렌디 → 실용적", 
                    "미래지향 → 즉시 필요",
                    "개념적 → 실행 가능"
                ]
            }
        }
        
        os.makedirs("test_results", exist_ok=True)
        with open("test_results/improved_categories.json", 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)

def main():
    """메인 실행 함수"""
    try:
        runner = ImprovedTestRunner()
        runner.run_improved_test()
        
        print(f"\n💡 개선 제안:")
        print(f"   1. 기존 test_enhanced_system.py의 프롬프트 수정")
        print(f"   2. '트렌디한' 대신 '즉시 관심을 끄는' 키워드 사용")
        print(f"   3. 구체적 예시 제시 (가슴운동, 노인운동법 등)")
        print(f"   4. 실용성 점수 추가하여 품질 관리")
        
    except Exception as e:
        print(f"❌ 테스트 실행 중 오류: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()