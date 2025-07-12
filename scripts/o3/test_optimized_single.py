"""Test script for optimized single transcript analysis.

Runs both deductive and inductive coding on one transcript for fast iteration.
"""

import subprocess
import sys
from pathlib import Path
import json
import pandas as pd
from collections import defaultdict

def run_deductive_analysis(transcript_id: str = "RAND_METHODS_ALICE_HUGUET"):
    """Run optimized deductive analysis."""
    print("="*60)
    print("RUNNING OPTIMIZED DEDUCTIVE ANALYSIS")
    print("="*60)
    
    script_path = Path(__file__).parent / "single_transcript_deductive.py"
    result = subprocess.run([
        sys.executable, str(script_path), 
        "--transcript", transcript_id
    ], capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✅ Deductive analysis completed successfully")
        print(result.stdout)
    else:
        print("❌ Deductive analysis failed")
        print("STDOUT:", result.stdout)
        print("STDERR:", result.stderr)
    
    return result.returncode == 0


def run_inductive_analysis(transcript_id: str = "RAND_METHODS_ALICE_HUGUET"):
    """Run optimized inductive analysis."""
    print("="*60)
    print("RUNNING OPTIMIZED INDUCTIVE ANALYSIS")
    print("="*60)
    
    script_path = Path(__file__).parent / "single_transcript_inductive.py"
    result = subprocess.run([
        sys.executable, str(script_path), 
        "--transcript", transcript_id
    ], capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✅ Inductive analysis completed successfully")
        print(result.stdout)
    else:
        print("❌ Inductive analysis failed")
        print("STDOUT:", result.stdout)
        print("STDERR:", result.stderr)
    
    return result.returncode == 0


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


def analyze_results(transcript_id: str = "RAND_METHODS_ALICE_HUGUET"):
    """Analyze the results from both analyses."""
    print("="*60)
    print("ANALYZING RESULTS")
    print("="*60)
    
    root = Path(__file__).resolve().parents[2]
    deductive_dir = root / "outputs" / "deductive"
    inductive_dir = root / "outputs" / "inductive"
    
    # Read deductive results
    claude_deductive = read_jsonl(deductive_dir / f"{transcript_id}_tags_CLAUDE.jsonl")
    gpt_deductive = read_jsonl(deductive_dir / f"{transcript_id}_tags_GPT.jsonl")
    gemini_deductive = read_jsonl(deductive_dir / f"{transcript_id}_tags_GEMINI.jsonl")
    
    # Read inductive results
    claude_inductive = read_jsonl(inductive_dir / f"{transcript_id}_inductive_CLAUDE.jsonl")
    gpt_inductive = read_jsonl(inductive_dir / f"{transcript_id}_inductive_GPT.jsonl")
    
    print(f"DEDUCTIVE RESULTS:")
    print(f"  Claude-Sonnet: {len(claude_deductive)} codes")
    print(f"  GPT-4o: {len(gpt_deductive)} codes")
    print(f"  Gemini: {len(gemini_deductive)} codes")
    
    print(f"\nINDUCTIVE RESULTS:")
    print(f"  Claude-Sonnet: {len(claude_inductive)} themes")
    print(f"  GPT-4o: {len(gpt_inductive)} themes")
    
    # Analyze deductive code distribution
    deductive_codes = defaultdict(int)
    for item in claude_deductive + gpt_deductive + gemini_deductive:
        if 'code' in item:
            deductive_codes[item['code']] += 1
    
    if deductive_codes:
        print(f"\nTOP DEDUCTIVE CODES:")
        sorted_codes = sorted(deductive_codes.items(), key=lambda x: x[1], reverse=True)
        for code, count in sorted_codes[:10]:
            print(f"  {code}: {count} instances")
    
    # Analyze inductive themes
    inductive_themes = defaultdict(int)
    for item in claude_inductive + gpt_inductive:
        if 'new_code' in item:
            inductive_themes[item['new_code']] += 1
    
    if inductive_themes:
        print(f"\nTOP INDUCTIVE THEMES:")
        sorted_themes = sorted(inductive_themes.items(), key=lambda x: x[1], reverse=True)
        for theme, count in sorted_themes[:10]:
            print(f"  {theme}: {count} instances")
    
    # Compare with previous results
    print(f"\n=== COMPARISON WITH PREVIOUS RESULTS ===")
    print("Previous deductive results (before optimization):")
    print("  Claude-Sonnet: ~4 codes")
    print("  GPT-4o: ~16 codes") 
    print("  Gemini: ~13 codes")
    
    current_total = len(claude_deductive) + len(gpt_deductive) + len(gemini_deductive)
    previous_total = 4 + 16 + 13  # Previous results
    
    print(f"\nCurrent total: {current_total} codes")
    print(f"Previous total: {previous_total} codes")
    
    if current_total > previous_total:
        improvement = ((current_total - previous_total) / previous_total) * 100
        print(f"✅ IMPROVEMENT: +{improvement:.1f}% more codes detected")
    else:
        print(f"❌ No improvement detected")
    
    return {
        'deductive_total': current_total,
        'inductive_total': len(claude_inductive) + len(gpt_inductive),
        'deductive_codes': dict(deductive_codes),
        'inductive_themes': dict(inductive_themes)
    }


def main():
    """Run complete optimized analysis test."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Test Optimized Single Transcript Analysis')
    parser.add_argument('--transcript', default='RAND_METHODS_ALICE_HUGUET',
                       help='Transcript ID to process')
    parser.add_argument('--deductive-only', action='store_true',
                       help='Run only deductive analysis')
    parser.add_argument('--inductive-only', action='store_true',
                       help='Run only inductive analysis')
    
    args = parser.parse_args()
    
    print("🚀 OPTIMIZED SINGLE TRANSCRIPT ANALYSIS TEST")
    print(f"📄 Transcript: {args.transcript}")
    print(f"🔧 Expanded codebook with research methods from inductive analysis")
    print(f"💡 Enhanced prompts with RAND focus group context")
    
    success = True
    
    if not args.inductive_only:
        success &= run_deductive_analysis(args.transcript)
    
    if not args.deductive_only:
        success &= run_inductive_analysis(args.transcript)
    
    if success:
        results = analyze_results(args.transcript)
        print(f"\n🎉 ANALYSIS COMPLETE!")
        print(f"📊 Total codes found: {results['deductive_total']}")
        print(f"🔍 New themes discovered: {results['inductive_total']}")
    else:
        print(f"\n❌ ANALYSIS FAILED - Check error messages above")


if __name__ == "__main__":
    main() 