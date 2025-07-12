"""Fast single-transcript merge for o3 methodology.

Optimized version for testing one transcript quickly.
"""

import json
import pandas as pd
import numpy as np
from pathlib import Path
import os
from dotenv import load_dotenv
from collections import defaultdict

load_dotenv()

ROOT = Path(__file__).resolve().parents[2]
DEDUCTIVE_DIR = Path(os.getenv("OUTPUTS_DIR", ROOT / "outputs")) / "deductive"
INDUCTIVE_DIR = Path(os.getenv("OUTPUTS_DIR", ROOT / "outputs")) / "inductive"
OUTPUT_DIR = Path(os.getenv("OUTPUTS_DIR", ROOT / "outputs"))

# Parameters from o3 spec
CONFIDENCE_THRESH = 0.80


def read_jsonl(filepath: Path) -> list:
    """Read JSONL file into list of dicts."""
    if not filepath.exists():
        return []
    
    data = []
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    data.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    return data


def pivot_to_wide(long_data: list, transcript_id: str) -> pd.DataFrame:
    """Convert long format to wide format: uid × code."""
    if not long_data:
        return pd.DataFrame()
    
    df = pd.DataFrame(long_data)
    if df.empty:
        return df
    
    # Ensure prob column exists (default to 1.0 if missing)
    if 'prob' not in df.columns:
        df['prob'] = 1.0
    
    # Pivot to wide format: uid × code
    wide = df.pivot(index='uid', columns='code', values='prob')
    
    # Fill missing values with 0.0 (absence)
    wide = wide.fillna(0.0)
    
    # Reset index to make uid a column
    wide = wide.reset_index()
    
    return wide


def merge_all_models(transcript_id: str) -> pd.DataFrame:
    """Merge results from all 3 models (Claude, GPT, Gemini)."""
    print(f"Merging results for {transcript_id}...")
    
    # Read all model results
    claude_data = read_jsonl(DEDUCTIVE_DIR / f"{transcript_id}_tags_CLAUDE.jsonl")
    gpt_data = read_jsonl(DEDUCTIVE_DIR / f"{transcript_id}_tags_GPT.jsonl")
    gemini_data = read_jsonl(DEDUCTIVE_DIR / f"{transcript_id}_tags_GEMINI.jsonl")
    
    print(f"Claude: {len(claude_data)} codes, GPT: {len(gpt_data)} codes, Gemini: {len(gemini_data)} codes")
    
    # Convert to wide format
    wide_claude = pivot_to_wide(claude_data, transcript_id)
    wide_gpt = pivot_to_wide(gpt_data, transcript_id)
    wide_gemini = pivot_to_wide(gemini_data, transcript_id)
    
    # Get all unique UIDs and codes
    all_uids = set()
    all_codes = set()
    
    for df in [wide_claude, wide_gpt, wide_gemini]:
        if not df.empty:
            all_uids.update(df['uid'].tolist())
            all_codes.update(df.columns)
    
    all_codes.discard('uid')
    
    print(f"Total unique UIDs: {len(all_uids)}, Total unique codes: {len(all_codes)}")
    
    # Create merged dataframe with union logic
    merged_data = []
    for uid in all_uids:
        row = {'uid': uid}
        for code in all_codes:
            # Use .get() with default 0.0 to avoid KeyError
            prob_claude = (
                wide_claude.loc[wide_claude['uid'] == uid, code].iloc[0]
                if not wide_claude.empty and uid in wide_claude['uid'].values and code in wide_claude.columns
                else 0.0
            )
            prob_gpt = (
                wide_gpt.loc[wide_gpt['uid'] == uid, code].iloc[0]
                if not wide_gpt.empty and uid in wide_gpt['uid'].values and code in wide_gpt.columns
                else 0.0
            )
            prob_gemini = (
                wide_gemini.loc[wide_gemini['uid'] == uid, code].iloc[0]
                if not wide_gemini.empty and uid in wide_gemini['uid'].values and code in wide_gemini.columns
                else 0.0
            )
            # Apply union logic: 1 if ANY model >= threshold
            merged_prob = 1.0 if (prob_claude >= CONFIDENCE_THRESH or prob_gpt >= CONFIDENCE_THRESH or prob_gemini >= CONFIDENCE_THRESH) else 0.0
            row[code] = merged_prob
        merged_data.append(row)
    return pd.DataFrame(merged_data)


def process_inductive_suggestions(transcript_id: str) -> list:
    """Pool inductive suggestions and keep tags mentioned >= 2 times."""
    inductive_a = read_jsonl(INDUCTIVE_DIR / f"{transcript_id}_inductive_A.jsonl")
    inductive_b = read_jsonl(INDUCTIVE_DIR / f"{transcript_id}_inductive_B.jsonl")
    
    print(f"Inductive A: {len(inductive_a)} suggestions, Inductive B: {len(inductive_b)} suggestions")
    
    # Count occurrences of each new_code
    code_counts = defaultdict(int)
    all_suggestions = []
    
    for item in inductive_a + inductive_b:
        if 'new_code' in item:
            code_counts[item['new_code']] += 1
            all_suggestions.append(item)
    
    # Keep codes mentioned >= 2 times
    frequent_codes = {code: count for code, count in code_counts.items() if count >= 2}
    
    print(f"Frequent codes (≥2 mentions): {len(frequent_codes)}")
    for code, count in frequent_codes.items():
        print(f"  {code}: {count} mentions")
    
    # Return suggestions for frequent codes
    return [item for item in all_suggestions if item['new_code'] in frequent_codes]


def main():
    """Process single transcript for testing."""
    # Use RAND_METHODS_ALICE_HUGUET as test case
    transcript_id = "RAND_METHODS_ALICE_HUGUET"
    
    print(f"=== FAST SINGLE TRANSCRIPT MERGE ===")
    print(f"Processing: {transcript_id}")
    
    # Merge all model results
    merged = merge_all_models(transcript_id)
    
    if not merged.empty:
        # Save merged wide format
        merged_path = OUTPUT_DIR / f"{transcript_id}_tags_merged.csv"
        merged.to_csv(merged_path, index=False)
        print(f"✅ Saved merged tags to {merged_path}")
        print(f"   Shape: {merged.shape[0]} UIDs × {merged.shape[1]-1} codes")
        
        # Show summary of merged codes
        codes = [col for col in merged.columns if col != 'uid']
        print(f"   Codes found: {len(codes)}")
        for code in sorted(codes):
            count = merged[code].sum()
            if count > 0:
                print(f"     {code}: {int(count)} instances")
    
    # Process inductive suggestions
    frequent_suggestions = process_inductive_suggestions(transcript_id)
    if frequent_suggestions:
        inductive_path = OUTPUT_DIR / f"{transcript_id}_inductive_frequent.jsonl"
        with open(inductive_path, 'w', encoding='utf-8') as f:
            for item in frequent_suggestions:
                f.write(json.dumps(item) + '\n')
        print(f"✅ Saved {len(frequent_suggestions)} frequent inductive suggestions to {inductive_path}")
    
    print(f"\n=== COMPLETE ===")
    print(f"Results in: {OUTPUT_DIR}")


if __name__ == "__main__":
    main() 