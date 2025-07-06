#!/usr/bin/env python3
"""Test Gemini 2.5 Pro integration"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the app directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.gemini_client import GeminiClient

def test_gemini_client():
    """Test basic Gemini client functionality"""
    try:
        print("Initializing Gemini client...")
        client = GeminiClient()
        print(f"✅ Client initialized with model: {client.model_name}")
        
        # Test category generation
        print("\nTesting category generation...")
        categories = client.generate_categories("운동", count=3)
        
        print(f"\n✅ Generated {len(categories)} categories:")
        for i, cat in enumerate(categories, 1):
            print(f"{i}. {cat.emoji} {cat.name}")
            print(f"   Description: {cat.description}")
            print(f"   Trend Score: {cat.trend_score}")
            print(f"   Research Activity: {cat.research_activity}")
            print()
        
        # Test paper discovery
        if categories:
            print("\nTesting paper discovery...")
            category_name = categories[0].name
            topic = "효과적인 방법"
            
            print(f"Searching papers for: {category_name} / {topic}")
            result = client.discover_papers_for_topic(category_name, topic)
            
            if result:
                print(f"\n✅ Found subcategory: {result.name}")
                print(f"   Description: {result.description}")
                print(f"   Papers found: {len(result.papers)}")
                print(f"   Quality Score: {result.quality_score}")
                print(f"   Quality Grade: {result.quality_grade}")
                
                for paper in result.papers:
                    print(f"\n   📄 {paper.title}")
                    print(f"      Authors: {paper.authors}")
                    print(f"      Journal: {paper.journal} ({paper.year})")
                    print(f"      Impact Factor: {paper.impact_factor}")
            else:
                print("❌ No papers found for this topic")
        
        print("\n✅ All tests passed!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_gemini_client()