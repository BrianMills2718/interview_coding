#!/usr/bin/env python3
"""
Batch processing script for all transcripts using the optimized o3 methodology.
Runs both deductive and inductive analysis on all available transcripts.
"""

import os
import sys
import time
from pathlib import Path
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed

# Add the parent directory to the path so we can import our modules
sys.path.append(str(Path(__file__).parent.parent))

from o3.single_transcript_deductive import process_single_transcript, call_claude_sonnet, call_gpt4o, call_gemini
from o3.single_transcript_inductive import process_inductive_analysis

# Configuration
PROC_DIR = Path("data/processed")
OUTPUT_DIR = Path("outputs")
DEDUCTIVE_DIR = OUTPUT_DIR / "deductive"
INDUCTIVE_DIR = OUTPUT_DIR / "inductive"

def get_all_transcripts():
    """Get all available transcript IDs from the processed directory."""
    transcripts = []
    for csv_file in PROC_DIR.glob("*_tidy.csv"):
        transcript_id = csv_file.stem.replace("_tidy", "")
        transcripts.append(transcript_id)
    return sorted(transcripts)

def process_transcript_deductive(transcript_id):
    """Process a single transcript with deductive analysis."""
    print(f"\n{'='*60}")
    print(f"PROCESSING DEDUCTIVE: {transcript_id}")
    print(f"{'='*60}")
    
    try:
        process_single_transcript(transcript_id)
        print(f"✅ DEDUCTIVE COMPLETED: {transcript_id}")
        return transcript_id, "deductive", "success"
    except Exception as e:
        print(f"❌ DEDUCTIVE FAILED: {transcript_id} - {e}")
        return transcript_id, "deductive", "failed"

def process_transcript_inductive(transcript_id):
    """Process a single transcript with inductive analysis."""
    print(f"\n{'='*60}")
    print(f"PROCESSING INDUCTIVE: {transcript_id}")
    print(f"{'='*60}")
    
    try:
        process_inductive_analysis(transcript_id)
        print(f"✅ INDUCTIVE COMPLETED: {transcript_id}")
        return transcript_id, "inductive", "success"
    except Exception as e:
        print(f"❌ INDUCTIVE FAILED: {transcript_id} - {e}")
        return transcript_id, "inductive", "failed"

def save_progress(completed_tasks, filename="batch_progress.txt"):
    """Save progress to a file in case of interruption."""
    with open(filename, 'w') as f:
        for task in completed_tasks:
            f.write(f"{task[0]},{task[1]},{task[2]}\n")
    print(f"💾 Progress saved to {filename}")

def load_progress(filename="batch_progress.txt"):
    """Load progress from file if it exists."""
    completed = set()
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            for line in f:
                parts = line.strip().split(',')
                if len(parts) == 3:
                    completed.add((parts[0], parts[1]))
        print(f"📋 Loaded {len(completed)} completed tasks from {filename}")
    return completed

def main():
    """Main batch processing function."""
    print("🚀 BATCH PROCESSING ALL TRANSCRIPTS")
    print("="*60)
    
    # Get all transcripts
    transcripts = get_all_transcripts()
    print(f"Found {len(transcripts)} transcripts: {transcripts}")
    
    # Load previous progress
    completed_tasks = load_progress()
    
    # Create all tasks
    all_tasks = []
    for transcript_id in transcripts:
        # Deductive analysis
        if (transcript_id, "deductive") not in completed_tasks:
            all_tasks.append(("deductive", transcript_id))
        
        # Inductive analysis  
        if (transcript_id, "inductive") not in completed_tasks:
            all_tasks.append(("inductive", transcript_id))
    
    print(f"📋 {len(all_tasks)} tasks remaining to process")
    
    if not all_tasks:
        print("✅ All tasks already completed!")
        return
    
    # Process tasks
    completed_results = []
    
    for i, (analysis_type, transcript_id) in enumerate(all_tasks, 1):
        print(f"\n🔄 Task {i}/{len(all_tasks)}: {analysis_type.upper()} - {transcript_id}")
        
        if analysis_type == "deductive":
            result = process_transcript_deductive(transcript_id)
        else:
            result = process_transcript_inductive(transcript_id)
        
        completed_results.append(result)
        
        # Save progress every 5 tasks
        if i % 5 == 0:
            save_progress(completed_results)
        
        # Small delay between tasks
        time.sleep(1)
    
    # Final progress save
    save_progress(completed_results)
    
    # Summary
    print(f"\n{'='*60}")
    print("📊 BATCH PROCESSING SUMMARY")
    print(f"{'='*60}")
    
    success_count = sum(1 for r in completed_results if r[2] == "success")
    failed_count = sum(1 for r in completed_results if r[2] == "failed")
    
    print(f"✅ Successful: {success_count}")
    print(f"❌ Failed: {failed_count}")
    print(f"📁 Results saved to: {OUTPUT_DIR}")
    
    if failed_count > 0:
        print("\n❌ Failed tasks:")
        for result in completed_results:
            if result[2] == "failed":
                print(f"  - {result[1]} ({result[0]})")

if __name__ == "__main__":
    main() 