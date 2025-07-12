"""Deductive coding runner for o3 methodology.

Processes all tidy CSV files in data/processed/ and runs deterministic coding
with Claude-Sonnet (Model-A), GPT-4o (Model-B), and Gemini (Model-C).
"""

import pandas as pd
from pathlib import Path
import os
from dotenv import load_dotenv
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

from llm_utils import (
    call_claude_sonnet, 
    call_gpt4o, 
    call_gemini,
    create_deductive_prompt,
    create_batch_deductive_prompt, 
    parse_llm_response, 
    write_jsonl
)

load_dotenv()

ROOT = Path(__file__).resolve().parents[2]
PROC_DIR = Path(os.getenv("PROCESSED_DIR", ROOT / "data" / "processed"))
OUTPUT_DIR = Path(os.getenv("OUTPUTS_DIR", ROOT / "outputs")) / "deductive"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Thread-local storage for rate limiting
thread_local = threading.local()


def process_with_model(model_name: str, model_func, df: pd.DataFrame, transcript_id: str, batch_size: int = 10) -> list:
    """Process transcript with a specific model using batch processing."""
    print(f"Running {model_name} with batch size {batch_size}...")
    results = []
    
    # Process in batches
    for i in range(0, len(df), batch_size):
        batch_df = df.iloc[i:i+batch_size]
        utterances = [
            {'uid': row['uid'], 'text': row['text']} 
            for _, row in batch_df.iterrows()
        ]
        
        # Create batch prompt
        prompt = create_batch_deductive_prompt(utterances)
        
        # Add timeout protection
        try:
            response = model_func(prompt, temperature=0.0)
            
            if response:
                parsed = parse_llm_response(response)
                results.extend(parsed)
        except Exception as e:
            print(f"  {model_name}: Error processing batch {i//batch_size + 1}: {e}")
            # Continue with next batch instead of failing completely
            continue
        
        # Progress update
        processed = min(i + batch_size, len(df))
        print(f"  {model_name}: Processed {processed}/{len(df)} turns")
        
        # Rate limiting between batches
        if i + batch_size < len(df):
            time.sleep(0.5)
    
    # Write results
    output_file = OUTPUT_DIR / f"{transcript_id}_tags_{model_name.split('-')[0].upper()}.jsonl"
    write_jsonl(results, output_file)
    
    return results


def process_transcript(csv_path: Path) -> None:
    """Process a single transcript CSV file with all 3 models in parallel."""
    transcript_id = csv_path.stem.replace("_tidy", "")
    print(f"\nProcessing {transcript_id}...")
    
    # Read tidy CSV
    df = pd.read_csv(csv_path)
    print(f"Found {len(df)} speaker turns")
    
    # Define models to run
    models = [
        ("Claude-Sonnet", call_claude_sonnet),
        ("GPT-4o", call_gpt4o),
        ("Gemini", call_gemini)
    ]
    
    # Process with all models in parallel
    results = {}
    with ThreadPoolExecutor(max_workers=3) as executor:
        # Submit all model processing tasks
        future_to_model = {
            executor.submit(process_with_model, model_name, model_func, df, transcript_id): model_name
            for model_name, model_func in models
        }
        
        # Collect results as they complete
        for future in as_completed(future_to_model):
            model_name = future_to_model[future]
            try:
                model_results = future.result()
                results[model_name] = model_results
                print(f"[SUCCESS] {model_name} completed: {len(model_results)} tags")
            except Exception as e:
                print(f"[ERROR] {model_name} failed: {e}")
                results[model_name] = []
    
    # Summary
    summary = ", ".join([f"{len(results[model_name])} {model_name.split('-')[0]} tags" for model_name in results.keys()])
    print(f"Completed {transcript_id}: {summary}")


def main():
    """Process all tidy CSV files."""
    csv_files = list(PROC_DIR.glob("*_tidy.csv"))
    
    if not csv_files:
        print(f"No tidy CSV files found in {PROC_DIR}")
        return
    
    print(f"Found {len(csv_files)} transcript(s) to process")
    
    for csv_file in csv_files:
        process_transcript(csv_file)
    
    print(f"\nAll deductive coding complete. Results in {OUTPUT_DIR}")


if __name__ == "__main__":
    main() 