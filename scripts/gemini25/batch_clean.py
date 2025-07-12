"""
Batch Cleaning Script for Gemini25 Methodology
Handles transcript preprocessing and hygiene
"""

import os
import re
from pathlib import Path
from typing import List, Dict, Any
import pandas as pd

def clean_transcript_text(text: str) -> str:
    """
    Clean and standardize transcript text
    
    Args:
        text: Raw transcript text
        
    Returns:
        Cleaned transcript text
    """
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Standardize speaker identification
    # Look for patterns like "Speaker 1:", "Participant A:", etc.
    text = re.sub(r'(Speaker|Participant|Person)\s*(\d+|[A-Z]):', r'Speaker \2:', text, flags=re.IGNORECASE)
    
    # Remove timestamps if present (format: [00:00:00] or similar)
    text = re.sub(r'\[\d{1,2}:\d{2}:\d{2}\]', '', text)
    text = re.sub(r'\(\d{1,2}:\d{2}:\d{2}\)', '', text)
    
    # Remove other common transcript artifacts
    text = re.sub(r'\[.*?\]', '', text)  # Remove bracketed text
    text = re.sub(r'\(.*?\)', '', text)  # Remove parenthetical text
    
    # Clean up line breaks and formatting
    text = re.sub(r'\n\s*\n', '\n\n', text)  # Remove excessive line breaks
    text = text.strip()
    
    return text

def extract_speaker_segments(text: str) -> List[Dict[str, Any]]:
    """
    Extract speaker segments from transcript
    
    Args:
        text: Cleaned transcript text
        
    Returns:
        List of speaker segments with metadata
    """
    segments = []
    
    # Split by speaker identification
    speaker_pattern = r'(Speaker \d+:)(.*?)(?=Speaker \d+:|$)'
    matches = re.finditer(speaker_pattern, text, re.DOTALL)
    
    for match in matches:
        speaker = match.group(1).strip()
        content = match.group(2).strip()
        
        if content:  # Only include non-empty segments
            segments.append({
                'speaker': speaker,
                'content': content,
                'start_pos': match.start(),
                'end_pos': match.end()
            })
    
    return segments

def validate_transcript_quality(segments: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Validate transcript quality and provide feedback
    
    Args:
        segments: List of speaker segments
        
    Returns:
        Quality assessment dictionary
    """
    if not segments:
        return {
            'valid': False,
            'issues': ['No speaker segments found'],
            'recommendations': ['Check transcript format and speaker identification']
        }
    
    total_content = sum(len(seg['content']) for seg in segments)
    avg_segment_length = total_content / len(segments)
    
    issues = []
    recommendations = []
    
    # Check for very short segments (potential transcription errors)
    short_segments = [seg for seg in segments if len(seg['content']) < 10]
    if short_segments:
        issues.append(f'{len(short_segments)} very short segments found')
        recommendations.append('Review short segments for transcription accuracy')
    
    # Check for very long segments (potential formatting issues)
    long_segments = [seg for seg in segments if len(seg['content']) > 1000]
    if long_segments:
        issues.append(f'{len(long_segments)} very long segments found')
        recommendations.append('Consider breaking up long segments for better analysis')
    
    # Check speaker distribution
    speaker_counts = {}
    for seg in segments:
        speaker = seg['speaker']
        speaker_counts[speaker] = speaker_counts.get(speaker, 0) + 1
    
    if len(speaker_counts) < 2:
        issues.append('Only one speaker detected')
        recommendations.append('Verify speaker identification in transcript')
    
    return {
        'valid': len(issues) == 0,
        'issues': issues,
        'recommendations': recommendations,
        'statistics': {
            'total_segments': len(segments),
            'total_content_length': total_content,
            'avg_segment_length': avg_segment_length,
            'speaker_count': len(speaker_counts),
            'speaker_distribution': speaker_counts
        }
    }

def process_transcript_file(input_file: Path, output_dir: Path) -> Dict[str, Any]:
    """
    Process a single transcript file
    
    Args:
        input_file: Path to input transcript file
        output_dir: Directory for output files
        
    Returns:
        Processing results dictionary
    """
    try:
        # Read input file
        with open(input_file, 'r', encoding='utf-8') as f:
            raw_text = f.read()
        
        # Clean text
        cleaned_text = clean_transcript_text(raw_text)
        
        # Extract segments
        segments = extract_speaker_segments(cleaned_text)
        
        # Validate quality
        quality_assessment = validate_transcript_quality(segments)
        
        # Create output filename
        output_file = output_dir / f"{input_file.stem}.txt"
        
        # Save cleaned transcript
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(cleaned_text)
        
        # Save segments as CSV for reference
        segments_file = output_dir / f"{input_file.stem}_segments.csv"
        if segments:
            segments_df = pd.DataFrame(segments)
            segments_df.to_csv(segments_file, index=False)
        
        return {
            'success': True,
            'input_file': str(input_file),
            'output_file': str(output_file),
            'segments_file': str(segments_file) if segments else None,
            'quality_assessment': quality_assessment,
            'statistics': {
                'original_length': len(raw_text),
                'cleaned_length': len(cleaned_text),
                'segment_count': len(segments)
            }
        }
        
    except Exception as e:
        return {
            'success': False,
            'input_file': str(input_file),
            'error': str(e)
        }

def batch_clean_transcripts(input_dir: str = "data/raw", 
                          output_dir: str = "data/processed") -> Dict[str, Any]:
    """
    Clean all transcript files in batch
    
    Args:
        input_dir: Directory containing raw transcript files
        output_dir: Directory for cleaned output files
        
    Returns:
        Batch processing results
    """
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    
    # Create output directory
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Find transcript files
    transcript_extensions = ['.txt', '.docx', '.doc']
    transcript_files = []
    
    for ext in transcript_extensions:
        transcript_files.extend(input_path.glob(f"*{ext}"))
    
    if not transcript_files:
        return {
            'success': False,
            'error': f'No transcript files found in {input_dir}'
        }
    
    # Process each file
    results = []
    successful_count = 0
    
    for transcript_file in transcript_files:
        print(f"Processing {transcript_file.name}...")
        
        result = process_transcript_file(transcript_file, output_path)
        results.append(result)
        
        if result['success']:
            successful_count += 1
            print(f"  ✓ Success: {result['statistics']['segment_count']} segments")
            
            if not result['quality_assessment']['valid']:
                print(f"  ⚠ Quality issues: {', '.join(result['quality_assessment']['issues'])}")
        else:
            print(f"  ✗ Error: {result['error']}")
    
    # Generate summary
    summary = {
        'total_files': len(transcript_files),
        'successful_files': successful_count,
        'failed_files': len(transcript_files) - successful_count,
        'results': results
    }
    
    # Save summary report
    summary_file = output_path / "cleaning_summary.json"
    import json
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    
    return summary

def main():
    """Main execution function"""
    print("Starting batch transcript cleaning...")
    
    summary = batch_clean_transcripts()
    
    if summary['success'] is False:
        print(f"Error: {summary['error']}")
        return
    
    print(f"\nBatch cleaning complete!")
    print(f"Total files: {summary['total_files']}")
    print(f"Successful: {summary['successful_files']}")
    print(f"Failed: {summary['failed_files']}")
    
    if summary['failed_files'] > 0:
        print("\nFailed files:")
        for result in summary['results']:
            if not result['success']:
                print(f"  - {result['input_file']}: {result['error']}")

if __name__ == "__main__":
    main() 