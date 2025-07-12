"""
Test script for unified pipeline with all improvements
"""

import sys
import logging
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent))

from src.pipeline.unified_pipeline import UnifiedPipeline

def main():
    """Test the unified pipeline on the test transcript"""
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('unified_pipeline_test.log'),
            logging.StreamHandler()
        ]
    )
    
    logger = logging.getLogger(__name__)
    
    # Initialize pipeline
    logger.info("Initializing unified pipeline...")
    pipeline = UnifiedPipeline()
    
    # Test on the product feedback transcript
    transcript_path = "data/processed/test_transcript.txt"
    
    logger.info(f"Testing on {transcript_path}")
    logger.info("="*60)
    
    # Run analysis
    result = pipeline.analyze_transcript(
        transcript_path,
        methodology="unified_with_improvements"
    )
    
    # Display results
    print("\n" + "="*60)
    print("UNIFIED PIPELINE TEST RESULTS")
    print("="*60)
    
    print(f"\n✅ Success: {result['success']}")
    
    print(f"\n📊 Domain Detection:")
    print(f"  - Domain: {result['domain_info']['detected_domain']}")
    print(f"  - Confidence: {result['domain_info']['confidence']:.2f}")
    print(f"  - Strategy: {result['domain_info']['fallback_strategy']}")
    
    print(f"\n📝 Coding Results:")
    print(f"  - Total codes: {result['coding_results']['total_codes']}")
    print(f"  - Strategy: {result['coding_results']['strategy']}")
    print(f"  - Coverage improvement: +{result['coding_results']['coverage_improvement']:.1%}")
    
    print(f"\n📈 Coverage Metrics:")
    print(f"  - Utterance coverage: {result['coverage_metrics']['coverage_percent']:.1f}%")
    print(f"  - Token coverage: {result['coverage_metrics']['token_coverage_percent']:.1f}%")
    print(f"  - Domain match score: {result['coverage_metrics']['domain_match_score']:.2f}")
    
    print(f"\n✔️ Validation:")
    print(f"  - Valid: {result['validation']['is_valid']}")
    print(f"  - Confidence: {result['validation']['confidence_score']:.2f}")
    print(f"  - Warnings: {len(result['validation']['warnings'])}")
    print(f"  - Errors: {len(result['validation']['errors'])}")
    
    if result['validation']['warnings']:
        print("\n⚠️ Warnings:")
        for warning in result['validation']['warnings'][:3]:
            print(f"  - {warning}")
    
    print(f"\n📁 Output Files:")
    for file_type, path in result['output_paths'].items():
        print(f"  - {file_type}: {Path(path).name}")
    
    print(f"\n📄 Full report: {result['output_paths']['report']}")
    
    # Also test on a simulated AI research transcript
    print("\n" + "="*60)
    print("Testing with forced AI research domain...")
    print("="*60)
    
    result2 = pipeline.analyze_transcript(
        transcript_path,
        methodology="unified_forced_domain",
        force_domain="ai_research"
    )
    
    print(f"\n✅ Success: {result2['success']}")
    print(f"📊 Forced Domain: {result2['domain_info']['detected_domain']}")
    print(f"📝 Total codes: {result2['coding_results']['total_codes']}")
    print(f"📈 Coverage: {result2['coverage_metrics']['coverage_percent']:.1f}%")
    
    print("\n" + "="*60)
    print("COMPARISON:")
    print("="*60)
    print(f"Natural domain detection: {result['coding_results']['total_codes']} codes, "
          f"{result['coverage_metrics']['coverage_percent']:.1f}% coverage")
    print(f"Forced AI domain: {result2['coding_results']['total_codes']} codes, "
          f"{result2['coverage_metrics']['coverage_percent']:.1f}% coverage")
    
    improvement = result['coverage_metrics']['coverage_percent'] - result2['coverage_metrics']['coverage_percent']
    print(f"\nImprovement with domain detection: +{improvement:.1f} percentage points")


if __name__ == "__main__":
    main()