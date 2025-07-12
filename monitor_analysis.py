#!/usr/bin/env python3
"""Monitor the background analysis progress"""

import os
import time
import json
from pathlib import Path
from datetime import datetime

def check_process():
    """Check if the analysis process is still running"""
    if os.path.exists("analysis.pid"):
        with open("analysis.pid") as f:
            pid = int(f.read().strip())
        # Check if process exists
        try:
            os.kill(pid, 0)
            return True, pid
        except OSError:
            return False, pid
    return False, None

def check_outputs():
    """Check what outputs have been created"""
    output_dirs = {
        "o3": Path("data/analysis_outputs/o3"),
        "opus": Path("data/analysis_outputs/opus"),
        "sonnet": Path("data/analysis_outputs/sonnet"),
        "gemini": Path("data/analysis_outputs/gemini")
    }
    
    outputs = {}
    for method, dir_path in output_dirs.items():
        if dir_path.exists():
            files = list(dir_path.glob("*"))
            outputs[method] = len(files)
        else:
            outputs[method] = 0
    
    return outputs

def tail_log(n=10):
    """Get last n lines of log file"""
    if os.path.exists("background_analysis.log"):
        with open("background_analysis.log") as f:
            lines = f.readlines()
            return lines[-n:]
    return []

def main():
    print("\n=== Analysis Pipeline Monitor ===")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Check process status
    running, pid = check_process()
    if running:
        print(f"\n✓ Process Status: RUNNING (PID: {pid})")
    else:
        print(f"\n✗ Process Status: NOT RUNNING" + (f" (was PID: {pid})" if pid else ""))
    
    # Check outputs
    print("\nOutput Files Created:")
    outputs = check_outputs()
    for method, count in outputs.items():
        status = "✓" if count > 0 else "⏳"
        print(f"  {status} {method}: {count} files")
    
    # Show recent log entries
    print("\nRecent Log Entries:")
    recent_logs = tail_log(10)
    for line in recent_logs:
        print(f"  {line.strip()}")
    
    # Check for errors
    print("\nChecking for Errors:")
    error_count = 0
    if os.path.exists("background_analysis.log"):
        with open("background_analysis.log") as f:
            for line in f:
                if "ERROR" in line or "error" in line.lower():
                    error_count += 1
    
    if error_count > 0:
        print(f"  ⚠️  Found {error_count} error messages in log")
    else:
        print("  ✓ No errors detected")
    
    # Check comparative analysis
    comp_path = Path("data/analysis_outputs/comparative_analysis.json")
    if comp_path.exists():
        print("\n✓ Comparative Analysis: COMPLETE")
        with open(comp_path) as f:
            data = json.load(f)
            if "methodologies_completed" in data:
                print(f"  Completed: {', '.join(data['methodologies_completed'])}")
    else:
        print("\n⏳ Comparative Analysis: Not yet created")

if __name__ == "__main__":
    main()