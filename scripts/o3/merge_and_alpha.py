"""Merge and reliability analysis for o3 methodology.

Implements the exact merge logic and Krippendorff's alpha calculation
specified by ChatGPT-o3.
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
PROC_DIR = Path(os.getenv("PROCESSED_DIR", ROOT / "data" / "processed"))

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
    """Convert long-format JSONL to wide matrix with 0.0 for missing codes."""
    if not long_data:
        return pd.DataFrame()
    
    # Create pivot table
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


def merge_tags(wide_a: pd.DataFrame, wide_b: pd.DataFrame, transcript_id: str) -> pd.DataFrame:
    """Apply o3 merge logic: union on prob >= threshold."""
    if wide_a.empty and wide_b.empty:
        return pd.DataFrame()
    
    # Get all unique UIDs
    uids_a = set(wide_a['uid'].tolist()) if not wide_a.empty else set()
    uids_b = set(wide_b['uid'].tolist()) if not wide_b.empty else set()
    all_uids = uids_a | uids_b
    
    # Get all unique codes
    codes_a = set(wide_a.columns) - {'uid'} if not wide_a.empty else set()
    codes_b = set(wide_b.columns) - {'uid'} if not wide_b.empty else set()
    all_codes = codes_a | codes_b
    
    # Create merged dataframe
    merged_data = []
    for uid in all_uids:
        row = {'uid': uid}
        
        for code in all_codes:
            # Get probabilities from each model
            prob_a = wide_a.loc[wide_a['uid'] == uid, code].iloc[0] if not wide_a.empty and uid in wide_a['uid'].values else 0.0
            prob_b = wide_b.loc[wide_b['uid'] == uid, code].iloc[0] if not wide_b.empty and uid in wide_b['uid'].values else 0.0
            
            # Apply union logic: 1 if either model >= threshold
            merged_prob = 1.0 if (prob_a >= CONFIDENCE_THRESH or prob_b >= CONFIDENCE_THRESH) else 0.0
            row[code] = merged_prob
        
        merged_data.append(row)
    
    return pd.DataFrame(merged_data)


def krippendorff_alpha(df: pd.DataFrame, codes: list) -> dict:
    """Calculate Krippendorff's alpha per o3 specification."""
    if df.empty or not codes:
        return {
            "overall_alpha": 0.0,
            "code_level": {},
            "n_units": 0,
            "n_coders": 2,
            "units_dropped_missing": 0
        }
    
    N = len(df)  # number of units
    n = len(codes)  # number of categories
    Do_total = 0  # observed disagreements
    De_total = 0  # expected disagreements
    units_dropped = 0
    
    code_alphas = {}
    
    for code in codes:
        if code not in df.columns:
            code_alphas[code] = 0.0
            continue
        
        # Count agreements (both = 1)
        coinc = df[code].sum()
        
        # Observed disagreements
        Do = N - coinc
        
        # Prevalence
        p = df[code].mean()
        
        # Expected disagreements
        De = 2 * p * (1 - p) * N
        
        # Calculate alpha for this code
        if De > 0:
            alpha = 1 - (Do / De)
        else:
            alpha = 1.0
        
        code_alphas[code] = alpha
        Do_total += Do
        De_total += De
    
    # Overall alpha
    if De_total > 0:
        overall_alpha = 1 - (Do_total / De_total)
    else:
        overall_alpha = 1.0
    
    return {
        "overall_alpha": overall_alpha,
        "code_level": code_alphas,
        "n_units": N,
        "n_coders": 2,
        "units_dropped_missing": units_dropped
    }


def process_inductive_suggestions(transcript_id: str) -> list:
    """Pool inductive suggestions and keep tags mentioned >= 2 times."""
    inductive_a = read_jsonl(INDUCTIVE_DIR / f"{transcript_id}_inductive_A.jsonl")
    inductive_b = read_jsonl(INDUCTIVE_DIR / f"{transcript_id}_inductive_B.jsonl")
    
    # Count occurrences of each new_code
    code_counts = defaultdict(int)
    all_suggestions = []
    
    for item in inductive_a + inductive_b:
        if 'new_code' in item:
            code_counts[item['new_code']] += 1
            all_suggestions.append(item)
    
    # Keep codes mentioned >= 2 times
    frequent_codes = {code: count for code, count in code_counts.items() if count >= 2}
    
    # Return suggestions for frequent codes
    return [item for item in all_suggestions if item['new_code'] in frequent_codes]


def process_transcript(transcript_id: str) -> None:
    """Process a single transcript's deductive and inductive results."""
    print(f"\nProcessing {transcript_id}...")
    
    # Read deductive results
    tags_a = read_jsonl(DEDUCTIVE_DIR / f"{transcript_id}_tags_A.jsonl")
    tags_b = read_jsonl(DEDUCTIVE_DIR / f"{transcript_id}_tags_B.jsonl")
    
    print(f"Model-A tags: {len(tags_a)}, Model-B tags: {len(tags_b)}")
    
    # Pivot to wide format
    wide_a = pivot_to_wide(tags_a, transcript_id)
    wide_b = pivot_to_wide(tags_b, transcript_id)
    
    # Merge tags
    merged = merge_tags(wide_a, wide_b, transcript_id)
    
    if not merged.empty:
        # Save merged wide format
        merged_path = OUTPUT_DIR / f"{transcript_id}_tags_merged.csv"
        merged.to_csv(merged_path, index=False)
        print(f"Saved merged tags to {merged_path}")
        
        # Calculate Krippendorff's alpha
        codes = [col for col in merged.columns if col != 'uid']
        alpha_results = krippendorff_alpha(merged, codes)
        
        # Save alpha report
        alpha_path = OUTPUT_DIR / f"{transcript_id}_alpha.json"
        with open(alpha_path, 'w', encoding='utf-8') as f:
            json.dump(alpha_results, f, indent=2)
        print(f"Saved alpha report to {alpha_path}")
        print(f"Overall alpha: {alpha_results['overall_alpha']:.3f}")
    
    # Process inductive suggestions
    frequent_suggestions = process_inductive_suggestions(transcript_id)
    if frequent_suggestions:
        inductive_path = OUTPUT_DIR / f"{transcript_id}_inductive_frequent.jsonl"
        with open(inductive_path, 'w', encoding='utf-8') as f:
            for item in frequent_suggestions:
                f.write(json.dumps(item) + '\n')
        print(f"Saved {len(frequent_suggestions)} frequent inductive suggestions to {inductive_path}")


def main():
    """Process all transcripts."""
    # Find all transcript IDs from deductive outputs
    deductive_files = list(DEDUCTIVE_DIR.glob("*_tags_A.jsonl"))
    transcript_ids = [f.stem.replace("_tags_A", "") for f in deductive_files]
    
    if not transcript_ids:
        print(f"No deductive results found in {DEDUCTIVE_DIR}")
        return
    
    print(f"Found {len(transcript_ids)} transcript(s) to merge")
    
    for transcript_id in transcript_ids:
        process_transcript(transcript_id)
    
    print(f"\nAll merge and alpha calculations complete. Results in {OUTPUT_DIR}")


if __name__ == "__main__":
    main() 