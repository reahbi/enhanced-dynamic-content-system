#!/usr/bin/env python3
"""Test subcategory generation"""

import asyncio
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the app directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.gemini_client import GeminiClient

async def test_subcategory_generation():
    """Test subcategory topic generation"""
    try:
        print("Initializing Gemini client...")
        client = GeminiClient()
        
        category_name = "💪 5분 가슴운동 완벽 루틴"
        print(f"\nGenerating subcategory topics for: {category_name}")
        
        # Generate topics
        topics = await client.generate_subcategory_topics(category_name, count=3)
        
        print(f"\nGenerated {len(topics)} topics:")
        for i, topic in enumerate(topics, 1):
            print(f"{i}. {topic}")
        
        # Try to discover papers for first topic
        if topics:
            print(f"\nSearching papers for first topic: {topics[0]}")
            result = client.discover_papers_for_topic(category_name, topics[0])
            
            if result:
                print(f"\n✅ Found subcategory: {result.name}")
                print(f"   Papers found: {len(result.papers)}")
                print(f"   Quality Grade: {result.quality_grade}")
            else:
                print("❌ No papers found for this topic")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_subcategory_generation())