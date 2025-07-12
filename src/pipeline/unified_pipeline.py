"""
Unified Analysis Pipeline
Integrates domain detection, validation, coverage analysis, and adaptive reporting
"""

import json
import logging
from typing import Dict, List, Optional, Tuple
from pathlib import Path
from datetime import datetime
import sys

# Add src to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.domain.domain_detector import DomainDetector, DomainValidator
from src.metrics.coverage_analyzer import CoverageAnalyzer
from src.validation.output_validator import OutputValidator
from src.reporting.adaptive_report_generator import AdaptiveReportGenerator
from src.coding.hybrid_coder import HybridCoder
from src.utils.llm_utils import LLMClient

logger = logging.getLogger(__name__)

class UnifiedPipeline:
    """Orchestrates the complete analysis pipeline with all improvements"""
    
    def __init__(self, config_path: str = "config/pipeline_config.json"):
        """Initialize pipeline components"""
        self.config = self._load_config(config_path)
        
        # Initialize components
        self.domain_detector = DomainDetector()
        self.domain_validator = DomainValidator()
        self.coverage_analyzer = CoverageAnalyzer()
        self.output_validator = OutputValidator()
        self.report_generator = AdaptiveReportGenerator()
        self.hybrid_coder = HybridCoder()
        self.llm_client = LLMClient()
        
        # Initialize output directory
        self.output_dir = Path(self.config.get("output_dir", "outputs/unified"))
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def _load_config(self, config_path: str) -> Dict:
        """Load pipeline configuration"""
        path = Path(config_path)
        if path.exists():
            with open(path, 'r') as f:
                return json.load(f)
        else:
            # Default configuration
            return {
                "output_dir": "outputs/unified",
                "enable_caching": True,
                "parallel_processing": True,
                "validation_threshold": 0.7,
                "coverage_warning_threshold": 0.5
            }
    
    def analyze_transcript(self, 
                          transcript_path: str,
                          methodology: str = "unified",
                          force_domain: Optional[str] = None) -> Dict:
        """
        Complete analysis pipeline for a single transcript
        
        Args:
            transcript_path: Path to transcript file
            methodology: Name of methodology (for reporting)
            force_domain: Optional domain override
            
        Returns:
            Dictionary with all analysis results
        """
        logger.info(f"Starting unified analysis of {transcript_path}")
        
        # Load transcript
        transcript = self._load_transcript(transcript_path)
        transcript_info = {
            "name": Path(transcript_path).stem,
            "path": transcript_path,
            "utterances": len(transcript),
            "speakers": len(set(utt.get("speaker") for utt in transcript))
        }
        
        # Step 1: Domain Detection
        logger.info("Step 1: Detecting domain...")
        domain_info = self._detect_domain(transcript, force_domain)
        
        # Step 2: Apply Hybrid Coding
        logger.info("Step 2: Applying hybrid coding strategy...")
        coding_results = self._apply_hybrid_coding(transcript, domain_info)
        
        # Step 3: Coverage Analysis
        logger.info("Step 3: Analyzing coverage...")
        coverage_metrics = self.coverage_analyzer.analyze_coverage(
            transcript,
            coding_results.merged_codes,
            domain_info.get("confidence", 1.0)
        )
        
        # Step 4: Output Validation
        logger.info("Step 4: Validating outputs...")
        validation_result = self.output_validator.validate_results(
            coding_results.merged_codes,
            transcript,
            domain_info,
            methodology
        )
        
        # Step 5: Generate Adaptive Report
        logger.info("Step 5: Generating adaptive report...")
        report = self._generate_report(
            coding_results,
            domain_info,
            coverage_metrics,
            validation_result,
            transcript_info,
            methodology
        )
        
        # Step 6: Save Results
        logger.info("Step 6: Saving results...")
        output_paths = self._save_results(
            coding_results,
            domain_info,
            coverage_metrics,
            validation_result,
            report,
            transcript_info
        )
        
        # Return comprehensive results
        return {
            "success": validation_result.is_valid,
            "transcript_info": transcript_info,
            "domain_info": domain_info,
            "coding_results": {
                "total_codes": len(coding_results.merged_codes),
                "strategy": coding_results.coding_strategy,
                "coverage_improvement": coding_results.coverage_improvement
            },
            "coverage_metrics": {
                "coverage_percent": coverage_metrics.coverage_percent,
                "token_coverage_percent": coverage_metrics.token_coverage_percent,
                "domain_match_score": coverage_metrics.domain_match_score
            },
            "validation": {
                "is_valid": validation_result.is_valid,
                "confidence_score": validation_result.confidence_score,
                "warnings": validation_result.warnings,
                "errors": validation_result.errors
            },
            "output_paths": output_paths
        }
    
    def _load_transcript(self, transcript_path: str) -> List[Dict]:
        """Load and parse transcript"""
        transcript = []
        
        with open(transcript_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Parse different formats
        if transcript_path.endswith('.json'):
            transcript = json.loads(content)
        else:
            # Parse text format with utterance IDs
            lines = content.strip().split('\n')
            for i, line in enumerate(lines):
                if line.strip():
                    # Extract utterance ID, speaker, and text
                    if '] ' in line:
                        parts = line.split('] ', 1)
                        utt_id = parts[0].strip('[')
                        
                        if ': ' in parts[1]:
                            speaker, text = parts[1].split(': ', 1)
                        else:
                            speaker = "Unknown"
                            text = parts[1]
                    else:
                        utt_id = f"UTT_{i:06d}"
                        speaker = "Unknown"
                        text = line
                    
                    transcript.append({
                        "utterance_id": utt_id,
                        "speaker": speaker.strip(),
                        "text": text.strip()
                    })
        
        return transcript
    
    def _detect_domain(self, transcript: List[Dict], force_domain: Optional[str]) -> Dict:
        """Detect or use forced domain"""
        if force_domain:
            return {
                "detected_domain": force_domain,
                "confidence": 1.0,
                "domain_scores": {force_domain: 1.0},
                "recommended_codebook": f"{force_domain}_codes.json",
                "fallback_strategy": "deductive"
            }
        
        # Combine all transcript text
        full_text = " ".join(utt.get("text", "") for utt in transcript)
        
        # Detect domain
        domain_info = self.domain_detector.analyze_transcript(full_text)
        
        # Log domain detection results
        logger.info(f"Detected domain: {domain_info['detected_domain']} "
                   f"(confidence: {domain_info['confidence']:.2f})")
        
        return domain_info
    
    def _apply_hybrid_coding(self, transcript: List[Dict], domain_info: Dict):
        """Apply hybrid coding based on domain confidence"""
        
        # Import the improved coders
        from src.coding.improved_deductive_coder import ImprovedDeductiveCoder
        from src.coding.improved_inductive_coder import ImprovedInductiveCoder
        
        deductive_coder = ImprovedDeductiveCoder()
        inductive_coder = ImprovedInductiveCoder()
        
        # Apply hybrid coding
        coding_results = self.hybrid_coder.code_transcript(
            transcript,
            domain_info,
            deductive_coder,
            inductive_coder,
            self.llm_client
        )
        
        return coding_results
    
    def _generate_report(self,
                        coding_results,
                        domain_info: Dict,
                        coverage_metrics,
                        validation_result,
                        transcript_info: Dict,
                        methodology: str) -> str:
        """Generate adaptive report"""
        
        # Convert objects to dicts for template
        coverage_dict = {
            "coverage_percent": coverage_metrics.coverage_percent,
            "token_coverage_percent": coverage_metrics.token_coverage_percent,
            "total_utterances": coverage_metrics.total_utterances,
            "coded_utterances": coverage_metrics.coded_utterances
        }
        
        validation_dict = {
            "is_valid": validation_result.is_valid,
            "warnings": validation_result.warnings,
            "errors": validation_result.errors,
            "recommendations": validation_result.recommendations
        }
        
        report = self.report_generator.generate_report(
            coding_results.merged_codes,
            domain_info,
            coverage_dict,
            validation_dict,
            transcript_info,
            methodology
        )
        
        # Add sections for coverage and validation reports
        report += "\n\n---\n\n"
        report += self.coverage_analyzer.generate_coverage_report(coverage_metrics)
        report += "\n\n---\n\n"
        report += self.output_validator.generate_validation_report(validation_result)
        report += "\n\n---\n\n"
        report += self.hybrid_coder.generate_strategy_report(coding_results)
        
        return report
    
    def _save_results(self,
                     coding_results,
                     domain_info: Dict,
                     coverage_metrics,
                     validation_result,
                     report: str,
                     transcript_info: Dict) -> Dict[str, str]:
        """Save all results to files"""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        transcript_name = transcript_info["name"]
        
        output_paths = {}
        
        # Save coding results
        coding_path = self.output_dir / f"{transcript_name}_coding_{timestamp}.json"
        with open(coding_path, 'w') as f:
            json.dump({
                "merged_codes": coding_results.merged_codes,
                "deductive_codes": coding_results.deductive_codes,
                "inductive_codes": coding_results.inductive_codes,
                "strategy": coding_results.coding_strategy
            }, f, indent=2)
        output_paths["coding"] = str(coding_path)
        
        # Save domain analysis
        domain_path = self.output_dir / f"{transcript_name}_domain_{timestamp}.json"
        with open(domain_path, 'w') as f:
            json.dump(domain_info, f, indent=2)
        output_paths["domain"] = str(domain_path)
        
        # Save coverage analysis
        coverage_path = self.output_dir / f"{transcript_name}_coverage_{timestamp}.json"
        with open(coverage_path, 'w') as f:
            json.dump({
                "metrics": {
                    "coverage_percent": coverage_metrics.coverage_percent,
                    "token_coverage_percent": coverage_metrics.token_coverage_percent,
                    "domain_match_score": coverage_metrics.domain_match_score,
                    "confidence_distribution": coverage_metrics.confidence_distribution
                },
                "uncoded_segments": coverage_metrics.uncoded_segments
            }, f, indent=2)
        output_paths["coverage"] = str(coverage_path)
        
        # Save validation results
        validation_path = self.output_dir / f"{transcript_name}_validation_{timestamp}.json"
        with open(validation_path, 'w') as f:
            json.dump({
                "is_valid": validation_result.is_valid,
                "confidence_score": validation_result.confidence_score,
                "warnings": validation_result.warnings,
                "errors": validation_result.errors,
                "recommendations": validation_result.recommendations,
                "detailed_checks": validation_result.detailed_checks
            }, f, indent=2)
        output_paths["validation"] = str(validation_path)
        
        # Save report
        report_path = self.output_dir / f"{transcript_name}_report_{timestamp}.md"
        with open(report_path, 'w') as f:
            f.write(report)
        output_paths["report"] = str(report_path)
        
        logger.info(f"Results saved to {self.output_dir}")
        
        return output_paths
    
    def batch_analyze(self, transcript_dir: str) -> List[Dict]:
        """Analyze multiple transcripts"""
        results = []
        
        transcript_path = Path(transcript_dir)
        transcript_files = list(transcript_path.glob("*.txt")) + list(transcript_path.glob("*.json"))
        
        logger.info(f"Found {len(transcript_files)} transcripts to analyze")
        
        for transcript_file in transcript_files:
            logger.info(f"\nAnalyzing {transcript_file.name}...")
            try:
                result = self.analyze_transcript(str(transcript_file))
                results.append(result)
            except Exception as e:
                logger.error(f"Failed to analyze {transcript_file.name}: {e}")
                results.append({
                    "success": False,
                    "transcript_info": {"name": transcript_file.stem},
                    "error": str(e)
                })
        
        # Generate summary report
        self._generate_batch_summary(results)
        
        return results
    
    def _generate_batch_summary(self, results: List[Dict]):
        """Generate summary of batch analysis"""
        summary = []
        summary.append("# Batch Analysis Summary\n")
        summary.append(f"**Total Transcripts**: {len(results)}")
        summary.append(f"**Successful**: {sum(1 for r in results if r.get('success', False))}")
        summary.append(f"**Failed**: {sum(1 for r in results if not r.get('success', False))}\n")
        
        # Domain distribution
        summary.append("## Domain Distribution")
        domains = {}
        for result in results:
            if result.get("success"):
                domain = result.get("domain_info", {}).get("detected_domain", "unknown")
                domains[domain] = domains.get(domain, 0) + 1
        
        for domain, count in sorted(domains.items(), key=lambda x: x[1], reverse=True):
            summary.append(f"- {domain}: {count} transcripts")
        
        # Coverage statistics
        summary.append("\n## Coverage Statistics")
        coverages = [
            r.get("coverage_metrics", {}).get("coverage_percent", 0)
            for r in results if r.get("success")
        ]
        if coverages:
            summary.append(f"- Average Coverage: {sum(coverages)/len(coverages):.1f}%")
            summary.append(f"- Min Coverage: {min(coverages):.1f}%")
            summary.append(f"- Max Coverage: {max(coverages):.1f}%")
        
        # Save summary
        summary_path = self.output_dir / f"batch_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        with open(summary_path, 'w') as f:
            f.write("\n".join(summary))
        
        logger.info(f"Batch summary saved to {summary_path}")


def main():
    """Main entry point for unified pipeline"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Unified Analysis Pipeline")
    parser.add_argument("transcript", help="Path to transcript or directory")
    parser.add_argument("--methodology", default="unified", help="Methodology name")
    parser.add_argument("--domain", help="Force specific domain")
    parser.add_argument("--batch", action="store_true", help="Process directory of transcripts")
    
    args = parser.parse_args()
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Run pipeline
    pipeline = UnifiedPipeline()
    
    if args.batch:
        results = pipeline.batch_analyze(args.transcript)
    else:
        result = pipeline.analyze_transcript(
            args.transcript,
            methodology=args.methodology,
            force_domain=args.domain
        )
        
        if result["success"]:
            print(f"\n✅ Analysis successful!")
            print(f"Report: {result['output_paths']['report']}")
        else:
            print(f"\n❌ Analysis failed!")
            print(f"Errors: {result['validation']['errors']}")


if __name__ == "__main__":
    main()