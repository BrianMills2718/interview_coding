#!/usr/bin/env python3
"""
Clean Environment Setup Script
Creates a fresh conda environment for LLM methodologies
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(cmd, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=True)
        print(f"✅ {description} completed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e.stderr}")
        return False

def create_clean_environment():
    """Create a clean conda environment"""
    env_name = "llm-methodologies"
    
    print("="*60)
    print("CLEAN ENVIRONMENT SETUP")
    print("="*60)
    
    # Check if conda is available
    if not run_command("conda --version", "Checking conda availability"):
        print("❌ Conda not found. Please install Anaconda or Miniconda first.")
        return False
    
    # Remove existing environment if it exists
    print("🔄 Checking for existing environment...")
    result = subprocess.run(f"conda env list | grep {env_name}", shell=True, capture_output=True)
    if result.returncode == 0:
        print(f"🔄 Removing existing {env_name} environment...")
        if not run_command(f"conda env remove -n {env_name} -y", f"Removing {env_name} environment"):
            return False
    
    # Create new environment with Python 3.11 (more stable)
    print(f"🔄 Creating new {env_name} environment...")
    if not run_command(f"conda create -n {env_name} python=3.11 -y", f"Creating {env_name} environment"):
        return False
    
    # Activate environment and install packages
    print("🔄 Installing packages in clean environment...")
    
    # Install core packages with conda first
    conda_packages = [
        "pandas",
        "numpy", 
        "openpyxl",
        "pip"
    ]
    
    for package in conda_packages:
        if not run_command(f"conda activate {env_name} && conda install {package} -y", f"Installing {package} with conda"):
            return False
    
    # Install LLM packages with pip
    pip_packages = [
        "anthropic",
        "openai",
        "google-generativeai", 
        "python-docx"
    ]
    
    for package in pip_packages:
        if not run_command(f"conda activate {env_name} && pip install {package}", f"Installing {package} with pip"):
            return False
    
    # Test the environment
    print("🔄 Testing environment...")
    test_script = f"""
import pandas as pd
import numpy as np
import anthropic
import openai
import google.generativeai as genai
from docx import Document
print("✅ All packages imported successfully!")
"""
    
    test_file = Path("test_env.py")
    with open(test_file, "w") as f:
        f.write(test_script)
    
    if run_command(f"conda activate {env_name} && python test_env.py", "Testing package imports"):
        test_file.unlink()  # Clean up test file
        print("\n🎉 Clean environment setup completed successfully!")
        print(f"\n📋 To activate the environment:")
        print(f"   conda activate {env_name}")
        print(f"\n📋 To run the methodologies:")
        print(f"   conda activate {env_name}")
        print(f"   python quick_start.py")
        return True
    else:
        test_file.unlink()  # Clean up test file
        print("❌ Environment test failed")
        return False

def main():
    """Main execution function"""
    print("This script will create a clean conda environment for the LLM methodologies project.")
    print("This will avoid the pandas and dependency conflicts you're experiencing.")
    
    response = input("\nDo you want to proceed? (y/n): ").lower().strip()
    if response != 'y':
        print("Setup cancelled.")
        return
    
    if create_clean_environment():
        print("\n" + "="*60)
        print("SETUP COMPLETE!")
        print("="*60)
        print("Next steps:")
        print("1. Activate the environment: conda activate llm-methodologies")
        print("2. Run the analysis: python quick_start.py")
        print("3. Or check environment: python quick_start.py --check-only")
    else:
        print("\n❌ Setup failed. Please check the error messages above.")

if __name__ == "__main__":
    main() 