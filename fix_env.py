#!/usr/bin/env python3
"""
Fix .env file with correct model names and API key placeholders
"""

from pathlib import Path

def fix_env_file():
    """Create proper .env file"""
    env_content = """# LLM Methodologies Environment Configuration
# API Keys (REQUIRED - Replace with your actual keys)
ANTHROPIC_API_KEY=your_anthropic_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
GOOGLE_API_KEY=your_google_api_key_here

# Model Names (Current defaults)
O3_CLAUDE_MODEL=claude-3-5-sonnet-20241022
O3_GPT4_MODEL=gpt-4o
O3_GEMINI_MODEL=gemini-1.5-pro

OPUS_CLAUDE_MODEL=claude-3-5-sonnet-20241022
OPUS_GPT4_MODEL=gpt-4o
OPUS_GEMINI_MODEL=gemini-1.5-pro

SONNET_CLAUDE_MODEL=claude-3-5-sonnet-20241022
SONNET_GPT4_MODEL=gpt-4o
SONNET_GEMINI_MODEL=gemini-1.5-pro

GEMINI_CLAUDE_MODEL=claude-3-5-sonnet-20241022
GEMINI_GPT4_MODEL=gpt-4o
GEMINI_GEMINI_MODEL=gemini-1.5-pro
"""
    
    with open('.env', 'w', encoding='utf-8') as f:
        f.write(env_content)
    
    print("[SUCCESS] .env file updated with correct model names")
    print("\nIMPORTANT: You need to add your actual API keys:")
    print("1. ANTHROPIC_API_KEY - Get from https://console.anthropic.com/")
    print("2. OPENAI_API_KEY - Get from https://platform.openai.com/api-keys")
    print("3. GOOGLE_API_KEY - Get from https://makersuite.google.com/app/apikey")
    print("\nReplace the 'your_*_api_key_here' placeholders with your actual keys")

if __name__ == "__main__":
    fix_env_file() 