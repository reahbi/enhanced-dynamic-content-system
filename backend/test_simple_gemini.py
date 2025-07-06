#!/usr/bin/env python3
"""Simple test for Gemini API"""

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

# Test with a simple prompt
try:
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents="Hello, what model are you?"
    )
    print(f"Response: {response.text}")
    
    # Log token usage
    if hasattr(response, 'usage_metadata'):
        usage = response.usage_metadata
        logger.info(f"[Gemini API - gemini-2.0-flash] Token usage: "
                   f"prompt_tokens={usage.prompt_token_count}, "
                   f"response_tokens={usage.candidates_token_count}, "
                   f"total_tokens={usage.total_token_count}")
    else:
        logger.warning("[Gemini API - gemini-2.0-flash] No token usage metadata available")
except Exception as e:
    print(f"Error: {e}")
    # Try other model names
    for model in ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-pro"]:
        try:
            print(f"\nTrying model: {model}")
            response = client.models.generate_content(
                model=model,
                contents="Hello, what model are you?"
            )
            print(f"Success with {model}!")
            print(f"Response: {response.text[:100]}...")
            
            # Log token usage
            if hasattr(response, 'usage_metadata'):
                usage = response.usage_metadata
                logger.info(f"[Gemini API - {model}] Token usage: "
                           f"prompt_tokens={usage.prompt_token_count}, "
                           f"response_tokens={usage.candidates_token_count}, "
                           f"total_tokens={usage.total_token_count}")
            else:
                logger.warning(f"[Gemini API - {model}] No token usage metadata available")
            break
        except Exception as e2:
            print(f"Failed with {model}: {e2}")