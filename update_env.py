#!/usr/bin/env python3
"""
Script to add O3 model environment variables to .env file
"""

import os
from pathlib import Path

def update_env_file():
    """Add O3 model variables to .env file"""
    env_path = Path('.env')
    
    # Variables to add
    new_vars = {
        'O3_CLAUDE_MODEL': 'claude-3-5-sonnet-20241022',
        'O3_GPT4_MODEL': 'gpt-4o'
    }
    
    # Read existing .env file
    existing_vars = {}
    if env_path.exists():
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    existing_vars[key] = value
    
    # Add new variables (don't overwrite if they exist)
    updated = False
    for key, value in new_vars.items():
        if key not in existing_vars:
            existing_vars[key] = value
            updated = True
            print(f"Added: {key}={value}")
        else:
            print(f"Already exists: {key}={existing_vars[key]}")
    
    # Write back to .env file
    if updated:
        with open(env_path, 'w', encoding='utf-8') as f:
            for key, value in existing_vars.items():
                f.write(f"{key}={value}\n")
        print(f"\n✅ Updated .env file with O3 model variables")
    else:
        print(f"\n✅ All O3 model variables already exist in .env file")

if __name__ == "__main__":
    update_env_file() 