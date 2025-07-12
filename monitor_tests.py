#!/usr/bin/env python3
"""Monitor background methodology tests"""

import os
import time
from pathlib import Path
from datetime import datetime

def check_process(pid_file):
    """Check if a process is running"""
    if not os.path.exists(pid_file):
        return False, None
    
    try:
        with open(pid_file) as f:
            pid = int(f.read().strip())
        os.kill(pid, 0)  # Check if process exists
        return True, pid
    except (OSError, ValueError):
        return False, None

def tail_log(log_file, n=5):
    """Get last n lines of log"""
    if not os.path.exists(log_file):
        return ["Log file not found"]
    
    try:
        with open(log_file) as f:
            lines = f.readlines()
            return lines[-n:] if lines else ["Empty log file"]
    except Exception as e:
        return [f"Error reading log: {e}"]

def check_outputs(methodology):
    """Check if outputs were created"""
    output_patterns = {
        'o3': ['outputs/deductive/*.jsonl', 'outputs/inductive/*.jsonl'],
        'opus': ['outputs/opus_enhanced/raw_outputs/*.json'],
        'sonnet': ['data/analysis_outputs/sonnet/*.json'],
        'gemini': ['outputs/coded_segments/*.csv', 'data/analysis_outputs/gemini/*.json']
    }
    
    patterns = output_patterns.get(methodology, [])
    files_found = []
    
    for pattern in patterns:
        from glob import glob
        matches = glob(pattern)
        files_found.extend(matches)
    
    return len(files_found)

def monitor_all():
    """Monitor all running tests"""
    methodologies = ['o3', 'opus', 'sonnet', 'gemini']
    
    print("\n" + "="*60)
    print(f"Methodology Test Monitor - {datetime.now().strftime('%H:%M:%S')}")
    print("="*60)
    
    all_complete = True
    
    for method in methodologies:
        pid_file = f"test_{method}.pid"
        log_file = f"test_{method}_background.log"
        
        running, pid = check_process(pid_file)
        output_count = check_outputs(method)
        
        print(f"\n{method.upper()} Methodology:")
        print(f"  Status: {'RUNNING' if running else 'COMPLETED/STOPPED'}")
        if pid:
            print(f"  PID: {pid}")
        print(f"  Outputs created: {output_count}")
        
        print("  Recent log:")
        for line in tail_log(log_file, 3):
            print(f"    {line.strip()}")
        
        # Check for errors
        if os.path.exists(log_file):
            with open(log_file) as f:
                content = f.read()
                error_count = content.lower().count('error')
                if error_count > 0:
                    print(f"  ⚠️  Errors found: {error_count}")
        
        if running:
            all_complete = False
    
    return all_complete

def main():
    """Main monitoring loop"""
    print("Starting test monitoring...")
    print("Press Ctrl+C to stop\n")
    
    try:
        while True:
            all_complete = monitor_all()
            
            if all_complete:
                print("\n✅ All tests completed!")
                break
            
            time.sleep(10)  # Check every 10 seconds
            os.system('clear' if os.name == 'posix' else 'cls')  # Clear screen
            
    except KeyboardInterrupt:
        print("\n\nMonitoring stopped.")

if __name__ == "__main__":
    main()