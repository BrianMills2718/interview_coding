"""Inductive coding runner for o3 methodology.

Processes all tidy CSV files in data/processed/ and runs exploratory coding
with Claude-Sonnet (Model-A) and GPT-4o (Model-B) to surface new themes.
"""

import pandas as pd
from pathlib import Path
import os
from dotenv import load_dotenv
import time

from llm_utils import (
    call_claude_sonnet, 
    call_gpt4o, 
    create_inductive_prompt, 
    parse_llm_response, 
    write_jsonl
)

load_dotenv()

ROOT = Path(__file__).resolve().parents[2]
PROC_DIR = Path(os.getenv("PROCESSED_DIR", ROOT / "data" / "processed"))
OUTPUT_DIR = Path(os.getenv("OUTPUTS_DIR", ROOT / "outputs")) / "inductive"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def process_transcript(csv_path: Path) -> None:
    """Process a single transcript CSV file."""
    transcript_id = csv_path.stem.replace("_tidy", "")
    print(f"\nProcessing {transcript_id}...")
    
    # Read tidy CSV
    df = pd.read_csv(csv_path)
    print(f"Found {len(df)} speaker turns")
    
    # Process with Model-A (Claude-Sonnet)
    print("Running Model-A (Claude-Sonnet) - exploratory...")
    model_a_results = []
    for idx, row in df.iterrows():
        uid = row['uid']
        text = row['text']
        
        prompt = create_inductive_prompt(uid, text)
        response = call_claude_sonnet(prompt, temperature=0.7)
        
        if response:
            parsed = parse_llm_response(response)
            model_a_results.extend(parsed)
        
        # Rate limiting
        if (idx + 1) % 10 == 0:
            print(f"  Processed {idx + 1}/{len(df)} turns")
            time.sleep(1)
    
    # Write Model-A results
    output_a = OUTPUT_DIR / f"{transcript_id}_inductive_A.jsonl"
    write_jsonl(model_a_results, output_a)
    
    # Process with Model-B (GPT-4o)
    print("Running Model-B (GPT-4o) - exploratory...")
    model_b_results = []
    for idx, row in df.iterrows():
        uid = row['uid']
        text = row['text']
        
        prompt = create_inductive_prompt(uid, text)
        response = call_gpt4o(prompt, temperature=0.7)
        
        if response:
            parsed = parse_llm_response(response)
            model_b_results.extend(parsed)
        
        # Rate limiting
        if (idx + 1) % 10 == 0:
            print(f"  Processed {idx + 1}/{len(df)} turns")
            time.sleep(1)
    
    # Write Model-B results
    output_b = OUTPUT_DIR / f"{transcript_id}_inductive_B.jsonl"
    write_jsonl(model_b_results, output_b)
    
    print(f"Completed {transcript_id}: {len(model_a_results)} Model-A suggestions, {len(model_b_results)} Model-B suggestions")


def main():
    """Process all tidy CSV files."""
    csv_files = list(PROC_DIR.glob("*_tidy.csv"))
    
    if not csv_files:
        print(f"No tidy CSV files found in {PROC_DIR}")
        return
    
    print(f"Found {len(csv_files)} transcript(s) to process")
    
    for csv_file in csv_files:
        process_transcript(csv_file)
    
    print(f"\nAll inductive coding complete. Results in {OUTPUT_DIR}")


if __name__ == "__main__":
    main() 