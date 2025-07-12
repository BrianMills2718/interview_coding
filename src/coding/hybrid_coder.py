"""
Hybrid Coding System
Combines deductive and inductive coding approaches based on domain confidence
"""

import json
import logging
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from collections import Counter

logger = logging.getLogger(__name__)

@dataclass
class HybridCodingResult:
    """Container for hybrid coding results"""
    deductive_codes: List[Dict]
    inductive_codes: List[Dict]
    merged_codes: List[Dict]
    coding_strategy: str
    domain_confidence: float
    coverage_improvement: float

class HybridCoder:
    """Implements adaptive hybrid coding based on domain confidence"""
    
    def __init__(self):
        self.high_confidence_threshold = 0.8
        self.low_confidence_threshold = 0.5
        self.min_quote_length = 20
        
    def code_transcript(self,
                       transcript: List[Dict],
                       domain_info: Dict,
                       deductive_coder,
                       inductive_coder,
                       llm_client) -> HybridCodingResult:
        """
        Apply hybrid coding strategy based on domain confidence
        
        Args:
            transcript: List of utterances
            domain_info: Domain detection results
            deductive_coder: Deductive coding function/class
            inductive_coder: Inductive coding function/class  
            llm_client: LLM client for coding
            
        Returns:
            HybridCodingResult with merged results
        """
        domain_confidence = domain_info.get("confidence", 0)
        
        # Determine strategy
        if domain_confidence >= self.high_confidence_threshold:
            strategy = "deductive_primary"
            result = self._deductive_with_supplement(
                transcript, domain_info, deductive_coder, inductive_coder, llm_client
            )
        elif domain_confidence >= self.low_confidence_threshold:
            strategy = "balanced"
            result = self._balanced_approach(
                transcript, domain_info, deductive_coder, inductive_coder, llm_client
            )
        else:
            strategy = "inductive_primary"
            result = self._inductive_with_mapping(
                transcript, domain_info, deductive_coder, inductive_coder, llm_client
            )
        
        # Calculate coverage improvement
        coverage_improvement = self._calculate_coverage_improvement(
            result.deductive_codes,
            result.merged_codes,
            len(transcript)
        )
        
        result.coding_strategy = strategy
        result.domain_confidence = domain_confidence
        result.coverage_improvement = coverage_improvement
        
        return result
    
    def _deductive_with_supplement(self,
                                  transcript: List[Dict],
                                  domain_info: Dict,
                                  deductive_coder,
                                  inductive_coder,
                                  llm_client) -> HybridCodingResult:
        """High confidence: Use deductive as primary, supplement with inductive"""
        
        # Apply deductive coding
        deductive_results = deductive_coder.code_transcript(
            transcript, 
            domain_info.get("recommended_codebook"),
            llm_client
        )
        
        # Find uncoded segments
        coded_utterances = set(r.get("utterance_id") for r in deductive_results)
        uncoded_segments = [
            utt for utt in transcript 
            if utt.get("utterance_id") not in coded_utterances
        ]
        
        # Apply inductive coding to uncoded segments
        inductive_results = []
        if uncoded_segments:
            inductive_results = inductive_coder.code_segments(
                uncoded_segments,
                llm_client,
                existing_codes=self._extract_code_list(deductive_results)
            )
        
        # Merge results
        merged = self._merge_results(
            deductive_results,
            inductive_results,
            prefer_deductive=True
        )
        
        return HybridCodingResult(
            deductive_codes=deductive_results,
            inductive_codes=inductive_results,
            merged_codes=merged,
            coding_strategy="",  # Set by caller
            domain_confidence=0,  # Set by caller
            coverage_improvement=0  # Set by caller
        )
    
    def _balanced_approach(self,
                          transcript: List[Dict],
                          domain_info: Dict,
                          deductive_coder,
                          inductive_coder,
                          llm_client) -> HybridCodingResult:
        """Medium confidence: Apply both approaches equally"""
        
        # Apply both coding approaches
        deductive_results = deductive_coder.code_transcript(
            transcript,
            domain_info.get("recommended_codebook"),
            llm_client
        )
        
        inductive_results = inductive_coder.code_transcript(
            transcript,
            llm_client
        )
        
        # Merge with equal weight
        merged = self._merge_results(
            deductive_results,
            inductive_results,
            prefer_deductive=False
        )
        
        return HybridCodingResult(
            deductive_codes=deductive_results,
            inductive_codes=inductive_results,
            merged_codes=merged,
            coding_strategy="",
            domain_confidence=0,
            coverage_improvement=0
        )
    
    def _inductive_with_mapping(self,
                               transcript: List[Dict],
                               domain_info: Dict,
                               deductive_coder,
                               inductive_coder,
                               llm_client) -> HybridCodingResult:
        """Low confidence: Lead with inductive, try to map to deductive"""
        
        # Apply inductive coding first
        inductive_results = inductive_coder.code_transcript(
            transcript,
            llm_client
        )
        
        # Try to map inductive codes to deductive codebook
        deductive_results = []
        if domain_info.get("recommended_codebook"):
            deductive_results = self._map_to_deductive(
                inductive_results,
                domain_info.get("recommended_codebook"),
                llm_client
            )
        
        # Merge, preferring inductive
        merged = self._merge_results(
            deductive_results,
            inductive_results,
            prefer_deductive=False
        )
        
        return HybridCodingResult(
            deductive_codes=deductive_results,
            inductive_codes=inductive_results,
            merged_codes=merged,
            coding_strategy="",
            domain_confidence=0,
            coverage_improvement=0
        )
    
    def _merge_results(self,
                      deductive: List[Dict],
                      inductive: List[Dict],
                      prefer_deductive: bool = True) -> List[Dict]:
        """Merge deductive and inductive results intelligently"""
        
        merged = []
        seen_segments = set()
        
        # Process preferred results first
        primary = deductive if prefer_deductive else inductive
        secondary = inductive if prefer_deductive else deductive
        
        # Add all primary results
        for result in primary:
            key = (result.get("utterance_id"), result.get("quote", "")[:50])
            if key not in seen_segments:
                result["source"] = "deductive" if prefer_deductive else "inductive"
                merged.append(result)
                seen_segments.add(key)
        
        # Add secondary results that don't overlap
        for result in secondary:
            key = (result.get("utterance_id"), result.get("quote", "")[:50])
            if key not in seen_segments:
                result["source"] = "inductive" if prefer_deductive else "deductive"
                # Slightly lower confidence for secondary
                result["confidence"] = result.get("confidence", 0.8) * 0.9
                merged.append(result)
                seen_segments.add(key)
        
        # Sort by utterance ID for consistency
        merged.sort(key=lambda x: (x.get("utterance_id", 0), x.get("code", "")))
        
        return merged
    
    def _extract_code_list(self, coding_results: List[Dict]) -> List[str]:
        """Extract unique codes from results"""
        return list(set(r.get("code") for r in coding_results if r.get("code")))
    
    def _map_to_deductive(self,
                         inductive_results: List[Dict],
                         codebook_path: str,
                         llm_client) -> List[Dict]:
        """Map inductive codes to deductive codebook"""
        
        # Load codebook
        try:
            with open(codebook_path, 'r') as f:
                codebook = json.load(f)
        except Exception as e:
            logger.error(f"Failed to load codebook: {e}")
            return []
        
        # Create mapping prompt
        inductive_codes = self._extract_code_list(inductive_results)
        
        mapping_prompt = f"""
        Map these emergent codes to the formal codebook where appropriate:
        
        Emergent codes: {json.dumps(inductive_codes)}
        
        Formal codebook: {json.dumps(codebook, indent=2)}
        
        For each emergent code, provide the best matching formal code or "NO_MATCH".
        Return as JSON: {{"emergent_code": "formal_code"}}
        """
        
        # Get mapping from LLM
        try:
            response = llm_client.query_model("gpt-4", mapping_prompt)
            mappings = json.loads(response)
        except Exception as e:
            logger.error(f"Failed to get code mappings: {e}")
            return []
        
        # Apply mappings
        mapped_results = []
        for result in inductive_results:
            emergent_code = result.get("code")
            if emergent_code in mappings and mappings[emergent_code] != "NO_MATCH":
                mapped_result = result.copy()
                mapped_result["code"] = mappings[emergent_code]
                mapped_result["original_code"] = emergent_code
                mapped_result["mapping_confidence"] = 0.8
                mapped_results.append(mapped_result)
        
        return mapped_results
    
    def _calculate_coverage_improvement(self,
                                      deductive: List[Dict],
                                      merged: List[Dict],
                                      total_utterances: int) -> float:
        """Calculate how much coverage improved with hybrid approach"""
        
        if total_utterances == 0:
            return 0.0
        
        deductive_coverage = len(set(r.get("utterance_id") for r in deductive)) / total_utterances
        merged_coverage = len(set(r.get("utterance_id") for r in merged)) / total_utterances
        
        improvement = merged_coverage - deductive_coverage
        return max(0.0, improvement)
    
    def generate_strategy_report(self, result: HybridCodingResult) -> str:
        """Generate report explaining the hybrid strategy used"""
        
        report = []
        report.append("## Hybrid Coding Strategy\n")
        
        # Explain strategy
        if result.coding_strategy == "deductive_primary":
            report.append(f"**Strategy**: Deductive-Primary (domain confidence: {result.domain_confidence:.2f})")
            report.append("- Applied formal codebook as primary approach")
            report.append("- Used emergent coding for uncoded segments")
        elif result.coding_strategy == "balanced":
            report.append(f"**Strategy**: Balanced (domain confidence: {result.domain_confidence:.2f})")
            report.append("- Applied both deductive and inductive coding")
            report.append("- Merged results with equal weight")
        else:
            report.append(f"**Strategy**: Inductive-Primary (domain confidence: {result.domain_confidence:.2f})")
            report.append("- Started with emergent coding")
            report.append("- Mapped results to formal codes where possible")
        
        report.append("")
        
        # Results summary
        report.append("### Results Summary")
        report.append(f"- Deductive codes: {len(result.deductive_codes)}")
        report.append(f"- Inductive codes: {len(result.inductive_codes)}")
        report.append(f"- Merged total: {len(result.merged_codes)}")
        report.append(f"- Coverage improvement: +{result.coverage_improvement:.1%}")
        
        # Code source breakdown
        sources = Counter(r.get("source") for r in result.merged_codes)
        report.append("\n### Code Sources")
        for source, count in sources.items():
            percentage = count / len(result.merged_codes) * 100 if result.merged_codes else 0
            report.append(f"- {source.title()}: {count} ({percentage:.1f}%)")
        
        return "\n".join(report)