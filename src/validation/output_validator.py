"""
Output Validation System
Validates coding outputs for quality and sanity
"""

import json
import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from collections import Counter
import numpy as np

logger = logging.getLogger(__name__)

@dataclass 
class ValidationResult:
    """Container for validation results"""
    is_valid: bool
    warnings: List[str]
    errors: List[str]
    recommendations: List[str]
    confidence_score: float
    detailed_checks: Dict[str, bool]

class OutputValidator:
    """Validates coding outputs for common issues and impossibilities"""
    
    def __init__(self):
        self.validation_rules = {
            "check_coverage": self._check_coverage,
            "check_confidence_distribution": self._check_confidence_distribution,
            "check_code_distribution": self._check_code_distribution,
            "check_domain_alignment": self._check_domain_alignment,
            "check_statistical_validity": self._check_statistical_validity,
            "check_output_consistency": self._check_output_consistency
        }
        
    def validate_results(self,
                        coding_results: List[Dict],
                        transcript: List[Dict],
                        domain_info: Dict,
                        methodology: str = "unknown") -> ValidationResult:
        """
        Comprehensive validation of coding results
        
        Args:
            coding_results: List of coding results
            transcript: Original transcript
            domain_info: Domain detection results
            methodology: Name of methodology used
            
        Returns:
            ValidationResult with detailed findings
        """
        warnings = []
        errors = []
        recommendations = []
        detailed_checks = {}
        
        # Run all validation checks
        for check_name, check_func in self.validation_rules.items():
            try:
                check_result = check_func(coding_results, transcript, domain_info)
                detailed_checks[check_name] = check_result["passed"]
                
                if not check_result["passed"]:
                    if check_result.get("severity") == "error":
                        errors.extend(check_result.get("messages", []))
                    else:
                        warnings.extend(check_result.get("messages", []))
                    
                    recommendations.extend(check_result.get("recommendations", []))
                    
            except Exception as e:
                logger.error(f"Validation check {check_name} failed: {e}")
                detailed_checks[check_name] = False
                errors.append(f"Validation check {check_name} failed with error")
        
        # Calculate overall confidence score
        confidence_score = self._calculate_confidence_score(detailed_checks, warnings, errors)
        
        # Determine if results are valid
        is_valid = len(errors) == 0 and confidence_score > 0.5
        
        return ValidationResult(
            is_valid=is_valid,
            warnings=warnings,
            errors=errors,
            recommendations=list(set(recommendations)),  # Remove duplicates
            confidence_score=confidence_score,
            detailed_checks=detailed_checks
        )
    
    def _check_coverage(self, coding_results: List[Dict], 
                       transcript: List[Dict], 
                       domain_info: Dict) -> Dict:
        """Check if coverage is reasonable"""
        if not transcript:
            return {
                "passed": False,
                "severity": "error",
                "messages": ["No transcript provided"],
                "recommendations": []
            }
        
        coded_utterances = set(r.get("utterance_id") for r in coding_results if r.get("utterance_id") is not None)
        coverage = len(coded_utterances) / len(transcript) if transcript else 0
        
        messages = []
        recommendations = []
        passed = True
        
        if coverage == 0:
            passed = False
            messages.append("No utterances were coded (0% coverage)")
            recommendations.append("Check if domain mismatch or codebook is appropriate")
        elif coverage < 0.1:
            passed = False
            messages.append(f"Extremely low coverage: {coverage:.1%}")
            recommendations.append("Consider using emergent coding approach")
        elif coverage < 0.3:
            messages.append(f"Low coverage: {coverage:.1%}")
            recommendations.append("Review uncoded segments for missed opportunities")
        elif coverage == 1.0:
            messages.append("100% coverage is suspicious - verify coding quality")
            recommendations.append("Review if all utterances truly contain codeable content")
        
        return {
            "passed": passed,
            "severity": "error" if coverage < 0.1 else "warning",
            "messages": messages,
            "recommendations": recommendations
        }
    
    def _check_confidence_distribution(self, coding_results: List[Dict], 
                                     transcript: List[Dict], 
                                     domain_info: Dict) -> Dict:
        """Check if confidence scores are distributed reasonably"""
        confidences = [r.get("confidence", 0) for r in coding_results]
        
        if not confidences:
            return {
                "passed": True,
                "messages": [],
                "recommendations": []
            }
        
        messages = []
        recommendations = []
        passed = True
        
        # Check for all same confidence
        if len(set(confidences)) == 1:
            passed = False
            messages.append(f"All codes have identical confidence ({confidences[0]})")
            recommendations.append("Review confidence calculation logic")
        
        # Check for all perfect confidence
        if all(c == 1.0 for c in confidences):
            passed = False
            messages.append("All codes have 100% confidence - likely overfitting")
            recommendations.append("Add uncertainty to coding process")
        
        # Check for all low confidence
        avg_confidence = np.mean(confidences)
        if avg_confidence < 0.5:
            messages.append(f"Low average confidence: {avg_confidence:.2f}")
            recommendations.append("Consider if domain/codebook is appropriate")
        
        return {
            "passed": passed,
            "severity": "error" if not passed else "warning",
            "messages": messages,
            "recommendations": recommendations
        }
    
    def _check_code_distribution(self, coding_results: List[Dict], 
                               transcript: List[Dict], 
                               domain_info: Dict) -> Dict:
        """Check if code distribution is reasonable"""
        code_counts = Counter(r.get("code") for r in coding_results)
        
        if not code_counts:
            return {
                "passed": True,
                "messages": [],
                "recommendations": []
            }
        
        messages = []
        recommendations = []
        passed = True
        
        # Check if one code dominates
        total_codes = sum(code_counts.values())
        max_code_count = max(code_counts.values())
        
        if max_code_count / total_codes > 0.8:
            most_common_code = max(code_counts, key=code_counts.get)
            messages.append(f"Code '{most_common_code}' represents {max_code_count/total_codes:.0%} of all codes")
            recommendations.append("Review if coding is too broad or generic")
        
        # Check if too many unique codes
        if len(code_counts) > len(transcript) * 2:
            messages.append(f"Too many unique codes ({len(code_counts)}) for {len(transcript)} utterances")
            recommendations.append("Consider consolidating similar codes")
        
        return {
            "passed": passed,
            "severity": "warning",
            "messages": messages,
            "recommendations": recommendations
        }
    
    def _check_domain_alignment(self, coding_results: List[Dict], 
                              transcript: List[Dict], 
                              domain_info: Dict) -> Dict:
        """Check if results align with detected domain"""
        domain_confidence = domain_info.get("confidence", 0)
        detected_domain = domain_info.get("detected_domain", "unknown")
        
        messages = []
        recommendations = []
        passed = True
        
        if detected_domain == "unknown" and len(coding_results) > 0:
            messages.append("Codes applied despite unknown domain")
            recommendations.append("Verify codes are appropriate for content")
        
        if domain_confidence < 0.7 and len(coding_results) > len(transcript) / 2:
            messages.append(f"Many codes applied despite low domain confidence ({domain_confidence:.2f})")
            recommendations.append("Consider using emergent coding for uncertain domains")
        
        return {
            "passed": passed,
            "severity": "warning",
            "messages": messages,
            "recommendations": recommendations
        }
    
    def _check_statistical_validity(self, coding_results: List[Dict], 
                                  transcript: List[Dict], 
                                  domain_info: Dict) -> Dict:
        """Check if statistical measures are valid"""
        messages = []
        recommendations = []
        passed = True
        
        # Check if enough data for statistics
        if len(coding_results) < 10 and len(transcript) < 10:
            messages.append("Limited data for meaningful statistical analysis")
            recommendations.append("Interpret reliability metrics with caution")
        
        # Check for impossible statistics
        # This would be expanded based on specific statistical measures
        
        return {
            "passed": passed,
            "severity": "warning", 
            "messages": messages,
            "recommendations": recommendations
        }
    
    def _check_output_consistency(self, coding_results: List[Dict], 
                                transcript: List[Dict], 
                                domain_info: Dict) -> Dict:
        """Check internal consistency of outputs"""
        messages = []
        recommendations = []
        passed = True
        
        # Check for duplicate codes on same utterance
        utterance_codes = {}
        for result in coding_results:
            utt_id = result.get("utterance_id")
            code = result.get("code")
            
            if utt_id and code:
                if utt_id not in utterance_codes:
                    utterance_codes[utt_id] = []
                utterance_codes[utt_id].append(code)
        
        for utt_id, codes in utterance_codes.items():
            if len(codes) != len(set(codes)):
                messages.append(f"Duplicate codes on utterance {utt_id}")
                passed = False
        
        if not passed:
            recommendations.append("Remove duplicate codes from results")
        
        return {
            "passed": passed,
            "severity": "error" if not passed else "warning",
            "messages": messages,
            "recommendations": recommendations
        }
    
    def _calculate_confidence_score(self, 
                                  detailed_checks: Dict[str, bool],
                                  warnings: List[str],
                                  errors: List[str]) -> float:
        """Calculate overall confidence score for validation"""
        # Start with base score
        score = 1.0
        
        # Deduct for failed checks
        checks_passed = sum(1 for passed in detailed_checks.values() if passed)
        check_penalty = (len(detailed_checks) - checks_passed) * 0.15
        score -= check_penalty
        
        # Deduct for warnings and errors
        score -= len(warnings) * 0.05
        score -= len(errors) * 0.2
        
        # Ensure score is between 0 and 1
        return max(0.0, min(1.0, score))
    
    def generate_validation_report(self, validation_result: ValidationResult) -> str:
        """Generate human-readable validation report"""
        report = []
        report.append("# Output Validation Report\n")
        
        # Overall status
        status_emoji = "✅" if validation_result.is_valid else "❌"
        report.append(f"## Overall Status: {status_emoji} {'VALID' if validation_result.is_valid else 'INVALID'}")
        report.append(f"**Confidence Score**: {validation_result.confidence_score:.2f}\n")
        
        # Detailed checks
        report.append("## Validation Checks")
        for check, passed in validation_result.detailed_checks.items():
            check_name = check.replace("_", " ").title()
            status = "✅ Passed" if passed else "❌ Failed"
            report.append(f"- {check_name}: {status}")
        report.append("")
        
        # Errors
        if validation_result.errors:
            report.append("## 🚨 Errors")
            for error in validation_result.errors:
                report.append(f"- {error}")
            report.append("")
        
        # Warnings
        if validation_result.warnings:
            report.append("## ⚠️ Warnings")
            for warning in validation_result.warnings:
                report.append(f"- {warning}")
            report.append("")
        
        # Recommendations
        if validation_result.recommendations:
            report.append("## 💡 Recommendations")
            for rec in validation_result.recommendations:
                report.append(f"- {rec}")
        
        return "\n".join(report)