#!/usr/bin/env python3
"""Test script to verify English/International paper discovery"""

import os
import sys
from dotenv import load_dotenv
import asyncio

# Load environment variables
load_dotenv()

# Add the app directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.gemini_client import GeminiClient

async def test_english_paper_discovery():
    """Test if the system now discovers English/international papers"""
    try:
        print("Initializing Gemini client...")
        client = GeminiClient()
        print(f"✅ Client initialized with model: {client.model_name}\n")
        
        # Test categories
        test_categories = [
            "근력 운동과 근육 성장",
            "유산소 운동과 체지방 감소",
            "운동 영양과 보충제"
        ]
        
        for category in test_categories:
            print(f"\n{'='*60}")
            print(f"Testing category: {category}")
            print('='*60)
            
            # Generate subcategory topics
            print("\nGenerating subcategory topics...")
            topics = await client.generate_subcategory_topics(category, count=3)
            
            print(f"Generated {len(topics)} topics:")
            for i, topic in enumerate(topics, 1):
                print(f"{i}. {topic}")
            
            # Test paper discovery for the first topic
            if topics:
                print(f"\nSearching papers for: {topics[0]}")
                result = client.discover_papers_for_topic(category, topics[0])
                
                if result:
                    print(f"\n✅ Found subcategory: {result.name}")
                    print(f"Description: {result.description}")
                    print(f"Quality Score: {result.quality_score} ({result.quality_grade})")
                    print(f"\nPapers found ({len(result.papers)}):")
                    
                    for j, paper in enumerate(result.papers, 1):
                        print(f"\n📄 Paper {j}:")
                        print(f"   Title: {paper.title}")
                        print(f"   Authors: {paper.authors}")
                        print(f"   Journal: {paper.journal}")
                        print(f"   Year: {paper.year}")
                        print(f"   DOI: {paper.doi}")
                        print(f"   Impact Factor: {paper.impact_factor}")
                        print(f"   Citations: {paper.citations}")
                        print(f"   Type: {paper.paper_type}")
                        
                        # Check if it's an English paper
                        if any(korean_char in paper.journal for korean_char in "가나다라마바사아자차카타파하"):
                            print("   ⚠️  WARNING: Korean journal detected!")
                        else:
                            print("   ✅ English/International journal")
                else:
                    print("❌ No papers found for this topic")
        
        print("\n\n✅ Test completed!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_english_paper_discovery())