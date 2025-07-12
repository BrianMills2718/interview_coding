"""
Consensus Builder Module
Implements consensus logic for combining multiple LLM coding results
"""

import numpy as np
import logging
from typing import Dict, List, Any, Optional
from analysis.output_manager import CodingResult

logger = logging.getLogger(__name__)

class ConsensusBuilder:
    """Build consensus from multiple LLM coding results"""
    
    def __init__(self):
        pass
    
    def build_consensus(self, individual_results: List[CodingResult], 
                       threshold: float = 0.7) -> Dict[str, Any]:
        """
        Build consensus from individual LLM coding results
        
        Args:
            individual_results: List of CodingResult objects from different LLMs
            threshold: Consensus threshold (default 0.7)
            
        Returns:
            Dictionary containing consensus codes and quotes
        """
        if not individual_results:
            return {'codes': {}, 'quotes': {}}
        
        # Get all unique codes
        all_codes = set()
        for result in individual_results:
            all_codes.update(result.codes.keys())
        
        consensus_codes = {}
        consensus_quotes = {}
        
        for code in all_codes:
            # Get coding decisions and confidences for this code
            decisions = []
            confidences = []
            quotes = []
            
            for result in individual_results:
                if code in result.codes:
                    code_data = result.codes[code]
                    decisions.append(code_data.get('present', False))
                    confidences.append(code_data.get('confidence', 0.0))
                    quotes.extend(code_data.get('quotes', []))
                else:
                    # If code not found, assume absent with low confidence
                    decisions.append(False)
                    confidences.append(0.1)
            
            # Calculate consensus metrics
            present_count = sum(decisions)
            total_count = len(decisions)
            agreement_ratio = present_count / total_count if total_count > 0 else 0.0
            avg_confidence = np.mean(confidences) if confidences else 0.0
            
            # Determine consensus decision
            if agreement_ratio >= threshold:
                # Consensus reached - code is present
                consensus_present = True
                consensus_confidence = avg_confidence
            elif agreement_ratio <= (1 - threshold):
                # Consensus reached - code is absent
                consensus_present = False
                consensus_confidence = avg_confidence
            else:
                # No consensus - use confidence-weighted decision
                weighted_score = np.average(decisions, weights=confidences)
                consensus_present = weighted_score > 0.5
                consensus_confidence = avg_confidence * 0.8  # Reduce confidence for no consensus
            
            # Store consensus result
            consensus_codes[code] = {
                'present': consensus_present,
                'confidence': consensus_confidence,
                'agreement_ratio': agreement_ratio,
                'num_models': total_count,
                'present_count': present_count,
                'individual_decisions': decisions,
                'individual_confidences': confidences
            }
            
            # Store consensus quotes (only for present codes)
            if consensus_present and quotes:
                consensus_quotes[code] = self._select_best_quotes(quotes, confidences)
        
        return {
            'codes': consensus_codes,
            'quotes': consensus_quotes,
            'consensus_threshold': threshold,
            'num_models': len(individual_results)
        }
    
    def _select_best_quotes(self, quotes: List[Dict[str, Any]], 
                           confidences: List[float]) -> List[Dict[str, Any]]:
        """
        Select the best quotes based on model confidence
        
        Args:
            quotes: List of quote dictionaries
            confidences: List of confidence scores for each model
            
        Returns:
            List of selected quotes with metadata
        """
        if not quotes:
            return []
        
        # Add confidence information to quotes
        enhanced_quotes = []
        for i, quote in enumerate(quotes):
            enhanced_quote = quote.copy()
            enhanced_quote['model_confidence'] = confidences[i] if i < len(confidences) else 0.0
            enhanced_quotes.append(enhanced_quote)
        
        # Sort by confidence and select top quotes
        enhanced_quotes.sort(key=lambda x: x.get('model_confidence', 0.0), reverse=True)
        
        # Select top 3 quotes or all if fewer than 3
        selected_quotes = enhanced_quotes[:3]
        
        # Add consensus metadata
        for quote in selected_quotes:
            quote['consensus_selected'] = True
            quote['selection_criteria'] = 'high_confidence'
        
        return selected_quotes
    
    def calculate_consensus_quality(self, consensus_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate quality metrics for consensus results
        
        Args:
            consensus_result: Result from build_consensus method
            
        Returns:
            Dictionary containing quality metrics
        """
        codes = consensus_result.get('codes', {})
        
        if not codes:
            return {
                'overall_quality': 0.0,
                'high_consensus_codes': 0,
                'low_consensus_codes': 0,
                'avg_confidence': 0.0,
                'avg_agreement': 0.0
            }
        
        # Calculate quality metrics
        confidences = [data.get('confidence', 0.0) for data in codes.values()]
        agreements = [data.get('agreement_ratio', 0.0) for data in codes.values()]
        
        avg_confidence = np.mean(confidences)
        avg_agreement = np.mean(agreements)
        
        # Count high/low consensus codes
        threshold = consensus_result.get('consensus_threshold', 0.7)
        high_consensus = sum(1 for data in codes.values() 
                           if data.get('agreement_ratio', 0.0) >= threshold)
        low_consensus = sum(1 for data in codes.values() 
                          if data.get('agreement_ratio', 0.0) < threshold)
        
        # Overall quality score (weighted average of confidence and agreement)
        overall_quality = (avg_confidence * 0.6) + (avg_agreement * 0.4)
        
        return {
            'overall_quality': overall_quality,
            'high_consensus_codes': high_consensus,
            'low_consensus_codes': low_consensus,
            'avg_confidence': avg_confidence,
            'avg_agreement': avg_agreement,
            'consensus_threshold': threshold,
            'total_codes': len(codes)
        }
    
    def identify_disagreements(self, individual_results: List[CodingResult]) -> Dict[str, Any]:
        """
        Identify areas of disagreement between LLMs
        
        Args:
            individual_results: List of coding results from different LLMs
            
        Returns:
            Dictionary containing disagreement analysis
        """
        if len(individual_results) < 2:
            return {
                'disagreement_codes': [],
                'disagreement_summary': {},
                'model_disagreements': {}
            }
        
        # Get all codes
        all_codes = set()
        for result in individual_results:
            all_codes.update(result.codes.keys())
        
        disagreement_codes = []
        model_disagreements = {result.model_name: {} for result in individual_results}
        
        for code in all_codes:
            # Get decisions for this code
            decisions = {}
            for result in individual_results:
                if code in result.codes:
                    decisions[result.model_name] = result.codes[code].get('present', False)
                else:
                    decisions[result.model_name] = False
            
            # Check for disagreements
            unique_decisions = set(decisions.values())
            if len(unique_decisions) > 1:  # Disagreement found
                disagreement_codes.append({
                    'code': code,
                    'decisions': decisions,
                    'disagreement_type': 'present_vs_absent' if len(unique_decisions) == 2 else 'mixed'
                })
                
                # Track disagreements by model
                for model, decision in decisions.items():
                    if model not in model_disagreements:
                        model_disagreements[model] = {}
                    model_disagreements[model][code] = decision
        
        # Calculate disagreement summary
        disagreement_summary = {
            'total_disagreements': len(disagreement_codes),
            'disagreement_rate': len(disagreement_codes) / len(all_codes) if all_codes else 0.0,
            'codes_with_disagreement': [d['code'] for d in disagreement_codes],
            'models_involved': list(set().union(*[set(d['decisions'].keys()) for d in disagreement_codes]))
        }
        
        return {
            'disagreement_codes': disagreement_codes,
            'disagreement_summary': disagreement_summary,
            'model_disagreements': model_disagreements
        }
    
    def suggest_resolution_strategies(self, disagreements: Dict[str, Any]) -> Dict[str, Any]:
        """
        Suggest strategies for resolving coding disagreements
        
        Args:
            disagreements: Result from identify_disagreements method
            
        Returns:
            Dictionary containing resolution strategies
        """
        disagreement_codes = disagreements.get('disagreement_codes', [])
        
        strategies = {
            'high_priority': [],
            'medium_priority': [],
            'low_priority': [],
            'general_recommendations': []
        }
        
        for disagreement in disagreement_codes:
            code = disagreement['code']
            decisions = disagreement['decisions']
            
            # Count present vs absent decisions
            present_count = sum(decisions.values())
            total_count = len(decisions)
            
            # Determine priority based on disagreement pattern
            if present_count == 1 and total_count > 2:
                # One model disagrees with others - high priority
                strategies['high_priority'].append({
                    'code': code,
                    'reason': 'single_model_disagreement',
                    'suggestion': 'Review specific model output for this code'
                })
            elif present_count == total_count // 2:
                # Split decision - high priority
                strategies['high_priority'].append({
                    'code': code,
                    'reason': 'split_decision',
                    'suggestion': 'Manual review required - no clear consensus'
                })
            elif present_count == 1 or present_count == total_count - 1:
                # Near consensus - medium priority
                strategies['medium_priority'].append({
                    'code': code,
                    'reason': 'near_consensus',
                    'suggestion': 'Review with confidence threshold adjustment'
                })
            else:
                # Other patterns - low priority
                strategies['low_priority'].append({
                    'code': code,
                    'reason': 'mixed_pattern',
                    'suggestion': 'Consider code definition clarification'
                })
        
        # General recommendations
        if disagreement_codes:
            strategies['general_recommendations'] = [
                'Review coding schema definitions for ambiguous codes',
                'Consider adjusting consensus threshold',
                'Implement confidence-weighted voting',
                'Add human review for high-disagreement codes'
            ]
        
        return strategies 