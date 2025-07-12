#!/usr/bin/env python3
"""
Sonnet Analysis Batch Runner
Runs the complete Sonnet methodology on all available transcripts
"""

import os
import sys
import json
import logging
from pathlib import Path
from datetime import datetime
import argparse

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from scripts.sonnet.sonnet_analyzer import SonnetAnalyzer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('sonnet_batch_analysis.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def check_environment():
    """Check if environment is properly configured"""
    logger.info("Checking environment configuration...")
    
    # Check API keys
    api_keys = {
        'ANTHROPIC_API_KEY': os.getenv('ANTHROPIC_API_KEY'),
        'OPENAI_API_KEY': os.getenv('OPENAI_API_KEY'),
        'GOOGLE_API_KEY': os.getenv('GOOGLE_API_KEY')
    }
    
    available_models = []
    for key, value in api_keys.items():
        if value:
            logger.info(f"✓ {key} found")
            if 'ANTHROPIC' in key:
                available_models.append('claude-3-sonnet')
            elif 'OPENAI' in key:
                available_models.append('gpt-4')
            elif 'GOOGLE' in key:
                available_models.append('gemini-pro')
        else:
            logger.warning(f"✗ {key} not found")
    
    logger.info(f"Available models: {available_models}")
    return available_models

def check_transcripts(transcript_dir: str):
    """Check if transcript files are available"""
    logger.info(f"Checking transcripts in: {transcript_dir}")
    
    transcript_dir = Path(transcript_dir)
    if not transcript_dir.exists():
        logger.error(f"Transcript directory not found: {transcript_dir}")
        return []
    
    # Find transcript files
    transcript_files = []
    for ext in ['.txt', '.csv']:
        transcript_files.extend(transcript_dir.glob(f'*{ext}'))
    
    logger.info(f"Found {len(transcript_files)} transcript files:")
    for file in transcript_files:
        logger.info(f"  - {file.name}")
    
    return transcript_files

def run_analysis(transcript_dir: str, config_path: str, output_path: str = None):
    """Run the complete Sonnet analysis"""
    logger.info("Starting Sonnet analysis...")
    
    # Initialize analyzer
    analyzer = SonnetAnalyzer(config_path)
    
    # Check available models
    available_models = analyzer.llm_client.get_available_models()
    logger.info(f"Available LLM models: {available_models}")
    
    # Check transcripts
    transcript_files = check_transcripts(transcript_dir)
    if not transcript_files:
        logger.error("No transcript files found. Exiting.")
        return
    
    # Run batch analysis
    logger.info("Running batch analysis...")
    start_time = datetime.now()
    
    results = analyzer.run_batch_analysis(transcript_dir)
    
    end_time = datetime.now()
    duration = end_time - start_time
    
    logger.info(f"Batch analysis completed in {duration}")
    logger.info(f"Successfully analyzed {len(results)} transcripts")
    
    if results:
        # Generate cross-analysis
        logger.info("Generating cross-transcript analysis...")
        cross_results = analyzer.generate_cross_analysis(results)
        
        logger.info("Analysis complete!")
        logger.info(f"Report generated: {cross_results['report_path']}")
        logger.info(f"Human review export: {cross_results['review_path']}")
        
        # Print summary
        print("\n" + "="*60)
        print("SONNET ANALYSIS SUMMARY")
        print("="*60)
        print(f"Transcripts analyzed: {len(results)}")
        print(f"Models used: {list(available_models.keys())}")
        print(f"Analysis duration: {duration}")
        print(f"Report location: {cross_results['report_path']}")
        print(f"Review export: {cross_results['review_path']}")
        
        # Print key findings
        cross_analysis = cross_results['cross_analysis']
        insights = cross_analysis.get('insights', {})
        
        print("\nKEY FINDINGS:")
        most_common = insights.get('most_common_codes', [])
        for code, stats in most_common[:3]:
            print(f"  - {code}: {stats['frequency']:.1%} of transcripts")
        
        reliability = cross_results['reliability_summary']
        print(f"\nRELIABILITY:")
        print(f"  - Overall Alpha: {reliability.get('overall_alpha', 0):.3f}")
        print(f"  - Overall Agreement: {reliability.get('overall_agreement', 0):.3f}")
        print(f"  - Overall Confidence: {reliability.get('overall_confidence', 0):.3f}")
        
        print("="*60)
    else:
        logger.error("No results generated. Check logs for errors.")

def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(description='Sonnet Methodology Batch Analysis')
    parser.add_argument('--transcript-dir', default='data/processed',
                       help='Directory containing transcript files')
    parser.add_argument('--config', default='config/sonnet_config.json',
                       help='Configuration file path')
    parser.add_argument('--output-path', 
                       help='Custom output path (overrides config)')
    parser.add_argument('--check-only', action='store_true',
                       help='Only check environment and transcripts, don\'t run analysis')
    
    args = parser.parse_args()
    
    print("Sonnet Methodology Analysis")
    print("="*40)
    
    # Check environment
    available_models = check_environment()
    if not available_models:
        logger.error("No LLM API keys found. Please set environment variables.")
        return
    
    # Check transcripts
    transcript_files = check_transcripts(args.transcript_dir)
    if not transcript_files:
        logger.error("No transcript files found.")
        return
    
    if args.check_only:
        logger.info("Environment check complete. Use --check-only=false to run analysis.")
        return
    
    # Run analysis
    run_analysis(args.transcript_dir, args.config, args.output_path)

if __name__ == "__main__":
    main() 