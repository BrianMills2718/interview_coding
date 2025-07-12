#!/usr/bin/env python3
"""
Pandas Fix Script
Fixes pandas version conflicts in conda environments
"""

import subprocess
import sys
import os

def fix_pandas():
    """Fix pandas installation issues"""
    print("🔧 Fixing pandas installation...")
    
    try:
        # First, uninstall pandas from conda
        print("1. Uninstalling pandas from conda...")
        subprocess.run([sys.executable, '-m', 'conda', 'remove', 'pandas', '-y'], 
                      capture_output=True)
        print("✅ pandas uninstalled from conda")
    except:
        print("⚠️  Could not uninstall pandas from conda (continuing...)")
    
    try:
        # Install pandas with pip
        print("2. Installing pandas with pip...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'pandas'], 
                      capture_output=True, check=True)
        print("✅ pandas installed with pip")
    except subprocess.CalledProcessError:
        print("❌ Failed to install pandas with pip")
        return False
    
    # Test the installation
    print("3. Testing pandas import...")
    try:
        result = subprocess.run([
            sys.executable, '-c', 'import pandas; print("pandas import successful")'
        ], capture_output=True, text=True, check=True)
        print("✅ pandas import test successful")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ pandas import test failed: {e.stderr}")
        return False

def main():
    print("="*50)
    print("PANDAS FIX SCRIPT")
    print("="*50)
    
    if fix_pandas():
        print("\n🎉 pandas has been fixed successfully!")
        print("You can now run: python quick_start.py")
    else:
        print("\n❌ Failed to fix pandas")
        print("Please try manually:")
        print("   pip install --force-reinstall pandas")

if __name__ == "__main__":
    main() 