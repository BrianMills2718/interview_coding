#!/usr/bin/env python3
"""
Script to create .env file with correct model names and API key placeholders
"""

env_content = """# API Keys - Replace with your actual keys
ANTHROPIC_API_KEY=your_anthropic_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
GOOGLE_API_KEY=your_google_api_key_here

# o3 Methodology Model Names
O3_CLAUDE_MODEL=claude-3-5-sonnet-20241022
O3_GPT4_MODEL=gpt-4o
O3_GEMINI_MODEL=gemini-1.5-pro

# Opus Methodology Model Names
OPUS_CLAUDE_MODEL=claude-3-5-sonnet-20241022
OPUS_GPT4_MODEL=gpt-4o
OPUS_GEMINI_MODEL=gemini-1.5-pro

# Sonnet Methodology Model Names
SONNET_CLAUDE_MODEL=claude-3-5-sonnet-20241022
SONNET_GPT4_MODEL=gpt-4o
SONNET_GEMINI_MODEL=gemini-1.5-pro

# Gemini Methodology Model Names
GEMINI_CLAUDE_MODEL=claude-3-5-sonnet-20241022
GEMINI_GPT4_MODEL=gpt-4o
GEMINI_GEMINI_MODEL=gemini-1.5-pro
"""

with open('.env', 'w') as f:
    f.write(env_content)

print("Created .env file with correct model names and API key placeholders.")
print("Please replace the placeholder API keys with your actual keys.") 