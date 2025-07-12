#!/usr/bin/env python3
"""
Quick Start Script for LLM Methodologies
Guides users through the complete setup and execution process
"""

import os
import sys
import subprocess
from pathlib import Path
import argparse

def print_header(title):
    """Print a formatted header"""
    print("\n" + "="*60)
    print(f" {title}")
    print("="*60)

def print_step(step_num, description):
    """Print a formatted step"""
    print(f"\n{step_num}. {description}")
    print("-" * 40)

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    return True

def install_dependencies():
    """Install required dependencies"""
    print_step(1, "Installing Dependencies")
    
    dependencies = [
        'anthropic',
        'openai', 
        'google-generativeai',
        'pandas',
        'numpy',
        'openpyxl',
        'python-docx'
    ]
    
    print("Installing required packages...")
    
    # First, try to fix pandas if there's a version conflict
    try:
        print("Checking for pandas version conflicts...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', '--force-reinstall', 'pandas'], 
                      capture_output=True, check=True)
        print("✅ pandas reinstalled to fix version conflicts")
    except subprocess.CalledProcessError:
        print("⚠️  pandas reinstall failed, continuing with other packages...")
    
    for dep in dependencies:
        try:
            if dep == 'pandas':
                # Skip pandas since we already handled it
                continue
            subprocess.run([sys.executable, '-m', 'pip', 'install', dep], 
                         capture_output=True, check=True)
            print(f"✅ {dep}")
        except subprocess.CalledProcessError:
            print(f"❌ Failed to install {dep}")
            return False
    
    return True

def check_api_keys():
    """Check if API keys are set"""
    print_step(2, "Checking API Keys")
    
    api_keys = {
        'ANTHROPIC_API_KEY': 'Claude/Anthropic',
        'OPENAI_API_KEY': 'GPT-4/OpenAI',
        'GOOGLE_API_KEY': 'Gemini/Google'
    }
    
    missing_keys = []
    for key, provider in api_keys.items():
        if os.getenv(key):
            print(f"✅ {provider} API key found")
        else:
            print(f"❌ {provider} API key missing")
            missing_keys.append(key)
    
    if missing_keys:
        print(f"\n⚠️  Missing API keys: {', '.join(missing_keys)}")
        print("Please set the following environment variables:")
        for key in missing_keys:
            print(f"   export {key}='your_api_key_here'")
        return False
    
    return True

def check_data_files():
    """Check if transcript files exist"""
    print_step(3, "Checking Data Files")
    
    # Check raw data
    raw_dir = Path("data/raw")
    if raw_dir.exists():
        docx_files = list(raw_dir.glob("*.docx"))
        if docx_files:
            print(f"✅ Found {len(docx_files)} .docx files in data/raw/")
            for file in docx_files:
                print(f"   - {file.name}")
        else:
            print("❌ No .docx files found in data/raw/")
            return False
    else:
        print("❌ data/raw/ directory not found")
        return False
    
    # Check processed data
    processed_dir = Path("data/processed")
    if processed_dir.exists():
        processed_files = list(processed_dir.glob("*.txt")) + list(processed_dir.glob("*.csv"))
        if processed_files:
            print(f"✅ Found {len(processed_files)} processed files in data/processed/")
        else:
            print("⚠️  No processed files found - will run data cleaning")
    else:
        print("⚠️  data/processed/ directory not found - will create during cleaning")
    
    return True

def clean_data():
    """Clean raw transcript data"""
    print_step(4, "Cleaning Transcript Data")
    
    try:
        # First, test if pandas import works
        print("Testing pandas import...")
        test_result = subprocess.run([
            sys.executable, '-c', 'import pandas; print("pandas import successful")'
        ], capture_output=True, text=True, timeout=30)
        
        if test_result.returncode != 0:
            print("❌ pandas import test failed")
            print("Attempting to fix pandas installation...")
            
            # Try to fix pandas
            subprocess.run([
                sys.executable, '-m', 'pip', 'install', '--force-reinstall', '--no-deps', 'pandas'
            ], capture_output=True, check=True)
            
            # Test again
            test_result = subprocess.run([
                sys.executable, '-c', 'import pandas; print("pandas import successful")'
            ], capture_output=True, text=True, timeout=30)
            
            if test_result.returncode != 0:
                print("❌ pandas still not working after reinstall")
                print("Please try: pip install --force-reinstall pandas")
                return False
        
        print("✅ pandas import test successful")
        
        # Now run the data cleaning
        result = subprocess.run([
            sys.executable, "scripts/o3/batch_clean.py"
        ], capture_output=True, text=True, check=True, timeout=300)
        
        print("✅ Data cleaning completed successfully")
        if result.stdout:
            print(result.stdout)
        return True
        
    except subprocess.TimeoutExpired:
        print("❌ Data cleaning timed out")
        return False
    except subprocess.CalledProcessError as e:
        print(f"❌ Data cleaning failed: {e.stderr}")
        return False

def run_methodologies(methods=None):
    """Run the specified methodologies"""
    print_step(5, "Running LLM Methodologies")
    
    if methods is None:
        methods = ['o3', 'opus', 'sonnet', 'gemini']
    
    print(f"Running methodologies: {', '.join(methods)}")
    
    try:
        cmd = [sys.executable, "scripts/run_all_methodologies.py"]
        if methods:
            cmd.extend(['--methods'] + methods)
        
        result = subprocess.run(cmd, capture_output=True, text=True, check=True, timeout=1800)
        
        print("✅ All methodologies completed successfully")
        if result.stdout:
            print(result.stdout)
        return True
        
    except subprocess.TimeoutExpired:
        print("❌ Methodology execution timed out")
        return False
    except subprocess.CalledProcessError as e:
        print(f"❌ Methodology execution failed: {e.stderr}")
        return False

def show_results():
    """Show where to find results"""
    print_step(6, "Results Summary")
    
    output_dirs = {
        'o3': 'data/analysis_outputs/o3/',
        'opus': 'data/analysis_outputs/opus/',
        'sonnet': 'data/analysis_outputs/sonnet/',
        'gemini': 'data/analysis_outputs/gemini/'
    }
    
    print("📁 Analysis results are available in:")
    for method, path in output_dirs.items():
        if Path(path).exists():
            files = list(Path(path).rglob('*'))
            print(f"   {method.upper()}: {path} ({len(files)} files)")
        else:
            print(f"   {method.upper()}: {path} (not found)")
    
    comparative_file = Path("data/analysis_outputs/comparative_analysis.json")
    if comparative_file.exists():
        print(f"\n📊 Comparative analysis: {comparative_file}")
    
    print("\n📖 Next steps:")
    print("   1. Review individual methodology outputs")
    print("   2. Check comparative analysis results")
    print("   3. Validate findings with human review")
    print("   4. Refine prompts and configurations as needed")

def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(description='Quick Start for LLM Methodologies')
    parser.add_argument('--skip-install', action='store_true',
                       help='Skip dependency installation')
    parser.add_argument('--skip-clean', action='store_true',
                       help='Skip data cleaning')
    parser.add_argument('--methods', nargs='+',
                       choices=['o3', 'opus', 'sonnet', 'gemini'],
                       help='Specific methodologies to run')
    parser.add_argument('--check-only', action='store_true',
                       help='Only check environment, don\'t run analysis')
    parser.add_argument('--fix-pandas', action='store_true',
                       help='Force reinstall pandas to fix version conflicts')
    
    args = parser.parse_args()
    
    print_header("LLM METHODOLOGIES QUICK START")
    print("This script will guide you through the complete setup and execution process.")
    
    # Check Python version
    if not check_python_version():
        return
    
    # Install dependencies
    if not args.skip_install:
        if not install_dependencies():
            print("❌ Failed to install dependencies. Please install manually.")
            return
    else:
        print_step(1, "Skipping Dependency Installation")
        print("⚠️  Dependencies installation skipped")
    
    # Check API keys
    if not check_api_keys():
        print("❌ Please set all required API keys before continuing.")
        return
    
    # Check data files
    if not check_data_files():
        print("❌ Please ensure transcript files are available in data/raw/")
        return
    
    if args.check_only:
        print("\n✅ Environment check completed successfully!")
        print("You can now run the analysis with: python quick_start.py")
        return
    
    # Clean data
    if not args.skip_clean:
        if not clean_data():
            print("❌ Data cleaning failed. Please check your transcript files.")
            print("\n💡 If you're having pandas issues, try:")
            print("   python quick_start.py --fix-pandas")
            print("   or manually run: pip install --force-reinstall pandas")
            return
    else:
        print_step(4, "Skipping Data Cleaning")
        print("⚠️  Data cleaning skipped")
    
    # Run methodologies
    if not run_methodologies(args.methods):
        print("❌ Methodology execution failed. Check logs for details.")
        return
    
    # Show results
    show_results()
    
    print_header("QUICK START COMPLETE")
    print("🎉 All methodologies have been executed successfully!")
    print("Check the output directories for detailed results.")

if __name__ == "__main__":
    main() 