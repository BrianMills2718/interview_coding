#!/usr/bin/env python3
"""
Add missing O3_GEMINI_MODEL to .env file
"""

from pathlib import Path

def add_missing_vars():
    """Add missing environment variables"""
    env_path = Path('.env')
    
    if not env_path.exists():
        print("❌ .env file not found. Run create_env.py first.")
        return
    
    # Read existing content
    with open(env_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if O3_GEMINI_MODEL already exists
    if 'O3_GEMINI_MODEL' not in content:
        # Add it after O3_GPT4_MODEL
        lines = content.split('\n')
        new_lines = []
        
        for line in lines:
            new_lines.append(line)
            if line.strip() == 'O3_GPT4_MODEL=gpt-4o':
                new_lines.append('O3_GEMINI_MODEL=gemini-1.5-pro')
        
        # Write back
        with open(env_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(new_lines))
        
        print("✅ Added O3_GEMINI_MODEL=gemini-1.5-pro to .env file")
    else:
        print("✅ O3_GEMINI_MODEL already exists in .env file")

if __name__ == "__main__":
    add_missing_vars() 