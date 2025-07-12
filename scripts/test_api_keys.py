#!/usr/bin/env python3
"""Test API keys to ensure they work before running full pipeline"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_anthropic():
    """Test Anthropic API key"""
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        response = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=10,
            messages=[{"role": "user", "content": "Say 'API working'"}]
        )
        print("✓ Anthropic API key is valid")
        return True
    except Exception as e:
        print(f"✗ Anthropic API error: {str(e)}")
        return False

def test_openai():
    """Test OpenAI API key"""
    try:
        import openai
        client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Say 'API working'"}],
            max_tokens=10
        )
        print("✓ OpenAI API key is valid")
        return True
    except Exception as e:
        print(f"✗ OpenAI API error: {str(e)}")
        return False

def test_google():
    """Test Google API key"""
    try:
        import google.generativeai as genai
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content("Say 'API working'")
        print("✓ Google API key is valid")
        return True
    except Exception as e:
        print(f"✗ Google API error: {str(e)}")
        return False

def main():
    print("\n=== Testing API Keys ===\n")
    
    results = {
        "Anthropic": test_anthropic(),
        "OpenAI": test_openai(),
        "Google": test_google()
    }
    
    print("\n=== Summary ===")
    all_valid = all(results.values())
    
    if all_valid:
        print("\n✅ All API keys are valid and working!")
    else:
        print("\n❌ Some API keys failed. Please check the errors above.")
        failed = [k for k, v in results.items() if not v]
        print(f"Failed APIs: {', '.join(failed)}")
    
    return all_valid

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)