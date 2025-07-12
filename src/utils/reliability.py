"""
Reliability Calculator Module
Implements Krippendorff's alpha and agreement ratio calculations for multi-LLM consensus
"""

import numpy as np
import logging
from typing import Dict, List, Any, Optional
from analysis.output_manager import CodingResult

logger = logging.getLogger(__name__)

class ReliabilityCalculator:
    """Calculate reliability metrics for multi-LLM coding results"""
    
    def __init__(self):
        pass
    
    def calculate_reliability(self, individual_results: List[CodingResult]) -> Dict[str, Any]:
        """
        Calculate reliability metrics for a set of individual coding results
        
        Args:
            individual_results: List of CodingResult objects from different LLMs
            
        Returns:
            Dictionary containing reliability metrics
        """
        if len(individual_results) < 2:
            return {
                'krippendorff_alpha': 0.0,
                'agreement_ratio': 0.0,
                'pairwise_agreements': {},
                'overall_confidence': 0.0
            }
        
        # Extract codes from all results
        all_codes = set()
        for result in individual_results:
            all_codes.update(result.codes.keys())
        
        # Create coding matrix
        coding_matrix = self._create_coding_matrix(individual_results, all_codes)
        
        # Calculate Krippendorff's alpha
        alpha = self._calculate_krippendorff_alpha(coding_matrix)
        
        # Calculate agreement ratios
        agreement_ratios = self._calculate_agreement_ratios(individual_results, all_codes)
        
        # Calculate pairwise agreements
        pairwise_agreements = self._calculate_pairwise_agreements(individual_results)
        
        # Calculate overall confidence
        overall_confidence = np.mean([r.confidence for r in individual_results])
        
        return {
            'krippendorff_alpha': alpha,
            'agreement_ratio': np.mean(list(agreement_ratios.values())),
            'agreement_ratios_by_code': agreement_ratios,
            'pairwise_agreements': pairwise_agreements,
            'overall_confidence': overall_confidence,
            'num_coders': len(individual_results),
            'num_codes': len(all_codes)
        }
    
    def _create_coding_matrix(self, results: List[CodingResult], all_codes: set) -> np.ndarray:
        """
        Create coding matrix for Krippendorff's alpha calculation
        
        Args:
            results: List of coding results
            all_codes: Set of all possible codes
            
        Returns:
            Matrix where rows are coders and columns are codes
        """
        num_coders = len(results)
        num_codes = len(all_codes)
        
        # Create mapping from codes to indices
        code_to_idx = {code: idx for idx, code in enumerate(sorted(all_codes))}
        
        # Initialize matrix
        matrix = np.zeros((num_coders, num_codes))
        
        # Fill matrix with coding decisions (1 for present, 0 for absent)
        for i, result in enumerate(results):
            for code, data in result.codes.items():
                if code in code_to_idx:
                    matrix[i, code_to_idx[code]] = 1 if data.get('present', False) else 0
        
        return matrix
    
    def _calculate_krippendorff_alpha(self, coding_matrix: np.ndarray) -> float:
        """
        Calculate Krippendorff's alpha for nominal data
        
        Args:
            coding_matrix: Matrix where rows are coders and columns are codes
            
        Returns:
            Krippendorff's alpha value
        """
        try:
            # For binary coding (present/absent), we can use a simplified version
            # This is an approximation of Krippendorff's alpha for nominal data
            
            n_coders, n_codes = coding_matrix.shape
            
            if n_coders < 2 or n_codes < 2:
                return 0.0
            
            # Calculate observed agreement
            observed_agreement = 0
            total_pairs = 0
            
            for code_idx in range(n_codes):
                code_values = coding_matrix[:, code_idx]
                present_count = np.sum(code_values)
                absent_count = n_coders - present_count
                
                # Agreement when both coders say present or both say absent
                present_agreement = present_count * (present_count - 1) / 2
                absent_agreement = absent_count * (absent_count - 1) / 2
                
                observed_agreement += present_agreement + absent_agreement
                total_pairs += n_coders * (n_coders - 1) / 2
            
            if total_pairs == 0:
                return 0.0
            
            observed_agreement = observed_agreement / total_pairs
            
            # Calculate expected agreement (assuming random chance)
            expected_agreement = 0.5  # For binary coding, random chance is 0.5
            
            # Calculate alpha
            if expected_agreement == 1:
                return 1.0 if observed_agreement == 1 else 0.0
            
            alpha = (observed_agreement - expected_agreement) / (1 - expected_agreement)
            
            return max(0.0, min(1.0, alpha))  # Clamp between 0 and 1
            
        except Exception as e:
            logger.error(f"Error calculating Krippendorff's alpha: {e}")
            return 0.0
    
    def _calculate_agreement_ratios(self, results: List[CodingResult], all_codes: set) -> Dict[str, float]:
        """
        Calculate agreement ratio for each code
        
        Args:
            results: List of coding results
            all_codes: Set of all possible codes
            
        Returns:
            Dictionary mapping codes to agreement ratios
        """
        agreement_ratios = {}
        
        for code in all_codes:
            # Get coding decisions for this code
            decisions = []
            for result in results:
                if code in result.codes:
                    decisions.append(result.codes[code].get('present', False))
                else:
                    decisions.append(False)  # Default to absent if not coded
            
            if len(decisions) < 2:
                agreement_ratios[code] = 0.0
                continue
            
            # Calculate agreement ratio
            present_count = sum(decisions)
            absent_count = len(decisions) - present_count
            
            # Agreement is the maximum of present agreement or absent agreement
            present_agreement = present_count / len(decisions) if present_count > 0 else 0
            absent_agreement = absent_count / len(decisions) if absent_count > 0 else 0
            
            agreement_ratios[code] = max(present_agreement, absent_agreement)
        
        return agreement_ratios
    
    def _calculate_pairwise_agreements(self, results: List[CodingResult]) -> Dict[str, float]:
        """
        Calculate pairwise agreement between each pair of coders
        
        Args:
            results: List of coding results
            
        Returns:
            Dictionary mapping coder pairs to agreement scores
        """
        pairwise_agreements = {}
        
        for i in range(len(results)):
            for j in range(i + 1, len(results)):
                coder1 = results[i]
                coder2 = results[j]
                
                # Get all codes that both coders evaluated
                common_codes = set(coder1.codes.keys()) & set(coder2.codes.keys())
                
                if not common_codes:
                    pairwise_agreements[f"{coder1.model_name}_vs_{coder2.model_name}"] = 0.0
                    continue
                
                # Calculate agreement for common codes
                agreements = 0
                for code in common_codes:
                    decision1 = coder1.codes[code].get('present', False)
                    decision2 = coder2.codes[code].get('present', False)
                    if decision1 == decision2:
                        agreements += 1
                
                agreement_ratio = agreements / len(common_codes)
                pairwise_agreements[f"{coder1.model_name}_vs_{coder2.model_name}"] = agreement_ratio
        
        return pairwise_agreements
    
    def calculate_overall_reliability(self, reliability_metrics_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculate overall reliability across multiple transcripts
        
        Args:
            reliability_metrics_list: List of reliability metrics from individual transcripts
            
        Returns:
            Overall reliability summary
        """
        if not reliability_metrics_list:
            return {
                'overall_alpha': 0.0,
                'overall_agreement': 0.0,
                'overall_confidence': 0.0,
                'num_transcripts': 0
            }
        
        # Aggregate metrics
        alphas = [m.get('krippendorff_alpha', 0.0) for m in reliability_metrics_list]
        agreements = [m.get('agreement_ratio', 0.0) for m in reliability_metrics_list]
        confidences = [m.get('overall_confidence', 0.0) for m in reliability_metrics_list]
        
        # Calculate overall statistics
        overall_alpha = np.mean(alphas)
        overall_agreement = np.mean(agreements)
        overall_confidence = np.mean(confidences)
        
        # Calculate standard deviations
        alpha_std = np.std(alphas)
        agreement_std = np.std(agreements)
        confidence_std = np.std(confidences)
        
        return {
            'overall_alpha': overall_alpha,
            'overall_agreement': overall_agreement,
            'overall_confidence': overall_confidence,
            'alpha_std': alpha_std,
            'agreement_std': agreement_std,
            'confidence_std': confidence_std,
            'num_transcripts': len(reliability_metrics_list),
            'alpha_range': (min(alphas), max(alphas)),
            'agreement_range': (min(agreements), max(agreements)),
            'confidence_range': (min(confidences), max(confidences))
        } 