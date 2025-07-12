"""
Coverage Analysis System
Tracks and reports coding coverage metrics
"""

import json
import logging
from typing import Dict, List, Set, Tuple, Optional
from dataclasses import dataclass
from collections import defaultdict
import pandas as pd

logger = logging.getLogger(__name__)

@dataclass
class CoverageMetrics:
    """Container for coverage metrics"""
    total_utterances: int
    coded_utterances: int
    total_tokens: int
    coded_tokens: int
    coverage_percent: float
    token_coverage_percent: float
    confidence_distribution: Dict[str, int]
    uncoded_segments: List[Dict]
    codes_per_utterance: float
    domain_match_score: float

class CoverageAnalyzer:
    """Analyzes coding coverage and identifies gaps"""
    
    def __init__(self):
        self.confidence_bins = {
            "high": (0.8, 1.0),
            "medium": (0.6, 0.8),
            "low": (0.0, 0.6)
        }
    
    def analyze_coverage(self, 
                        transcript: List[Dict], 
                        coding_results: List[Dict],
                        domain_confidence: float = 1.0) -> CoverageMetrics:
        """
        Analyze coverage of coding results against transcript
        
        Args:
            transcript: List of utterance dicts with 'text', 'speaker', 'utterance_id'
            coding_results: List of coding dicts with 'utterance_id', 'code', 'confidence'
            domain_confidence: Confidence in domain detection
            
        Returns:
            CoverageMetrics object
        """
        # Basic counts
        total_utterances = len(transcript)
        coded_utterance_ids = set(result.get("utterance_id") for result in coding_results)
        coded_utterances = len(coded_utterance_ids)
        
        # Token-level coverage
        total_tokens = sum(len(utt.get("text", "").split()) for utt in transcript)
        coded_tokens = sum(
            len(utt.get("text", "").split()) 
            for utt in transcript 
            if utt.get("utterance_id") in coded_utterance_ids
        )
        
        # Coverage percentages
        coverage_percent = (coded_utterances / total_utterances * 100) if total_utterances > 0 else 0
        token_coverage_percent = (coded_tokens / total_tokens * 100) if total_tokens > 0 else 0
        
        # Confidence distribution
        confidence_dist = self._calculate_confidence_distribution(coding_results)
        
        # Find uncoded segments
        uncoded_segments = self._identify_uncoded_segments(transcript, coded_utterance_ids)
        
        # Codes per utterance
        codes_per_utterance = len(coding_results) / coded_utterances if coded_utterances > 0 else 0
        
        # Domain match score (combination of coverage and domain confidence)
        domain_match_score = (coverage_percent / 100) * domain_confidence
        
        return CoverageMetrics(
            total_utterances=total_utterances,
            coded_utterances=coded_utterances,
            total_tokens=total_tokens,
            coded_tokens=coded_tokens,
            coverage_percent=coverage_percent,
            token_coverage_percent=token_coverage_percent,
            confidence_distribution=confidence_dist,
            uncoded_segments=uncoded_segments,
            codes_per_utterance=codes_per_utterance,
            domain_match_score=domain_match_score
        )
    
    def _calculate_confidence_distribution(self, coding_results: List[Dict]) -> Dict[str, int]:
        """Calculate distribution of confidence scores"""
        distribution = defaultdict(int)
        
        for result in coding_results:
            confidence = result.get("confidence", 0)
            for bin_name, (low, high) in self.confidence_bins.items():
                if low <= confidence <= high:
                    distribution[bin_name] += 1
                    break
        
        return dict(distribution)
    
    def _identify_uncoded_segments(self, 
                                  transcript: List[Dict], 
                                  coded_ids: Set) -> List[Dict]:
        """Identify uncoded segments and their characteristics"""
        uncoded = []
        
        for utterance in transcript:
            utt_id = utterance.get("utterance_id")
            if utt_id not in coded_ids:
                uncoded.append({
                    "utterance_id": utt_id,
                    "speaker": utterance.get("speaker", "Unknown"),
                    "text": utterance.get("text", ""),
                    "tokens": len(utterance.get("text", "").split()),
                    "reason": self._guess_uncoded_reason(utterance)
                })
        
        return uncoded
    
    def _guess_uncoded_reason(self, utterance: Dict) -> str:
        """Guess why an utterance wasn't coded"""
        text = utterance.get("text", "").lower()
        
        # Check for common uncoded patterns
        if len(text.split()) < 5:
            return "too_short"
        elif any(word in text for word in ["hello", "thank you", "goodbye", "thanks"]):
            return "greeting_closing"
        elif text.strip().endswith("?") and len(text.split()) < 10:
            return "short_question"
        else:
            return "no_matching_codes"
    
    def generate_coverage_report(self, metrics: CoverageMetrics) -> str:
        """Generate human-readable coverage report"""
        report = []
        report.append("# Coding Coverage Report\n")
        
        # Summary statistics
        report.append("## Summary Statistics")
        report.append(f"- Total utterances: {metrics.total_utterances}")
        report.append(f"- Coded utterances: {metrics.coded_utterances} ({metrics.coverage_percent:.1f}%)")
        report.append(f"- Total tokens: {metrics.total_tokens}")
        report.append(f"- Coded tokens: {metrics.coded_tokens} ({metrics.token_coverage_percent:.1f}%)")
        report.append(f"- Average codes per utterance: {metrics.codes_per_utterance:.2f}")
        report.append(f"- Domain match score: {metrics.domain_match_score:.2f}\n")
        
        # Confidence distribution
        report.append("## Confidence Distribution")
        for level, count in metrics.confidence_distribution.items():
            report.append(f"- {level.capitalize()} confidence: {count} codes")
        report.append("")
        
        # Coverage warnings
        warnings = self._generate_coverage_warnings(metrics)
        if warnings:
            report.append("## ⚠️ Coverage Warnings")
            for warning in warnings:
                report.append(f"- {warning}")
            report.append("")
        
        # Uncoded segments summary
        if metrics.uncoded_segments:
            report.append("## Uncoded Segments Analysis")
            reason_counts = defaultdict(int)
            for segment in metrics.uncoded_segments:
                reason_counts[segment["reason"]] += 1
            
            report.append("### Reasons for uncoded content:")
            for reason, count in sorted(reason_counts.items(), key=lambda x: x[1], reverse=True):
                reason_display = reason.replace("_", " ").title()
                report.append(f"- {reason_display}: {count} utterances")
            report.append("")
            
            # Sample uncoded content
            report.append("### Sample uncoded utterances:")
            for segment in metrics.uncoded_segments[:3]:
                text_preview = segment["text"][:100] + "..." if len(segment["text"]) > 100 else segment["text"]
                report.append(f'- {segment["speaker"]}: "{text_preview}"')
        
        return "\n".join(report)
    
    def _generate_coverage_warnings(self, metrics: CoverageMetrics) -> List[str]:
        """Generate warnings based on coverage metrics"""
        warnings = []
        
        if metrics.coverage_percent < 50:
            warnings.append(f"Low coverage: Only {metrics.coverage_percent:.1f}% of utterances coded")
        
        if metrics.token_coverage_percent < 40:
            warnings.append(f"Low token coverage: Only {metrics.token_coverage_percent:.1f}% of content coded")
        
        if metrics.domain_match_score < 0.5:
            warnings.append(f"Poor domain match: Score of {metrics.domain_match_score:.2f} suggests domain mismatch")
        
        high_conf = metrics.confidence_distribution.get("high", 0)
        total_codes = sum(metrics.confidence_distribution.values())
        if total_codes > 0 and high_conf / total_codes < 0.5:
            warnings.append("Low confidence: Less than 50% of codes have high confidence")
        
        if metrics.codes_per_utterance > 5:
            warnings.append(f"Over-coding: Average of {metrics.codes_per_utterance:.1f} codes per utterance")
        
        return warnings
    
    def export_coverage_data(self, metrics: CoverageMetrics, output_path: str):
        """Export coverage data to CSV for further analysis"""
        # Create DataFrame with uncoded segments
        if metrics.uncoded_segments:
            df = pd.DataFrame(metrics.uncoded_segments)
            df.to_csv(output_path, index=False)
            logger.info(f"Exported uncoded segments to {output_path}")
    
    def compare_methodology_coverage(self, 
                                   methodology_metrics: Dict[str, CoverageMetrics]) -> pd.DataFrame:
        """Compare coverage across different methodologies"""
        comparison_data = []
        
        for methodology, metrics in methodology_metrics.items():
            comparison_data.append({
                "methodology": methodology,
                "coverage_percent": metrics.coverage_percent,
                "token_coverage_percent": metrics.token_coverage_percent,
                "high_confidence_codes": metrics.confidence_distribution.get("high", 0),
                "domain_match_score": metrics.domain_match_score,
                "codes_per_utterance": metrics.codes_per_utterance
            })
        
        return pd.DataFrame(comparison_data)