#!/usr/bin/env python3
"""Test Gemini 2.5 Pro model availability"""

import os
import logging
from dotenv import load_dotenv
from google import genai

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Get API key
api_key = os.getenv("GEMINI_API_KEY")
print(f"API Key found: {api_key[:10]}...")

# Initialize client
client = genai.Client(api_key=api_key)

# Test different model names
models_to_test = [
    "gemini-2.5-pro",
    "gemini-2.5-pro-latest", 
    "models/gemini-2.5-pro",
    "gemini-2.0-flash",
    "gemini-1.5-pro",
    "gemini-1.5-pro-latest"
]

for model_name in models_to_test:
    try:
        print(f"\nTesting model: {model_name}")
        response = client.models.generate_content(
            model=model_name,
            contents="What version and model are you?"
        )
        print(f"✅ Success with {model_name}!")
        print(f"Response: {response.text[:100]}...")
        
        # Log token usage
        if hasattr(response, 'usage_metadata'):
            usage = response.usage_metadata
            logger.info(f"[Gemini API - {model_name}] Token usage: "
                       f"prompt_tokens={usage.prompt_token_count}, "
                       f"response_tokens={usage.candidates_token_count}, "
                       f"total_tokens={usage.total_token_count}")
        else:
            logger.warning(f"[Gemini API - {model_name}] No token usage metadata available")
        break
    except Exception as e:
        print(f"❌ Failed with {model_name}: {str(e)[:100]}...")