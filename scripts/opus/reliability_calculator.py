"""Reliability calculator for Opus methodology.

Implements Krippendorff's alpha and agreement rate calculations.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Tuple
from collections import defaultdict
import json
from pathlib import Path


class ReliabilityCalculator:
    """Calculate inter-rater reliability metrics."""
    
    def __init__(self):
        self.agreement_matrix = {}
        self.kappa_scores = {}
    
    def calculate_agreement_rates(self, coding_results: List[Dict[str, Any]]) -> Dict[str, float]:
        """Calculate agreement rates between models for each code."""
        if len(coding_results) < 2:
            return {}
        
        # Extract all unique codes across all models
        all_codes = set()
        for result in coding_results:
            if 'codes_found' in result:
                all_codes.update(result['codes_found'].keys())
        
        agreement_rates = {}
        
        for code_id in all_codes:
            # Check which models found this code
            models_found = []
            for i, result in enumerate(coding_results):
                if 'codes_found' in result and code_id in result['codes_found']:
                    models_found.append(f"model_{i+1}")
            
            # Calculate agreement rate
            total_models = len(coding_results)
            agreement_rate = len(models_found) / total_models
            agreement_rates[code_id] = agreement_rate
        
        return agreement_rates
    
    def calculate_krippendorff_alpha(self, coding_results: List[Dict[str, Any]]) -> float:
        """Calculate Krippendorff's alpha for multiple coders."""
        if len(coding_results) < 2:
            return 0.0
        
        # Extract all unique codes and units
        all_codes = set()
        all_units = set()
        
        for result in coding_results:
            if 'codes_found' in result:
                all_codes.update(result['codes_found'].keys())
                for code_id, instances in result['codes_found'].items():
                    for instance in instances:
                        if 'quote' in instance:
                            all_units.add(instance['quote'])
        
        if not all_codes or not all_units:
            return 0.0
        
        # Create coincidence matrix
        n_units = len(all_units)
        n_codes = len(all_codes)
        
        if n_units == 0 or n_codes == 0:
            return 0.0
        
        # Calculate observed disagreements
        Do_total = 0
        De_total = 0
        
        for code_id in all_codes:
            # Count how many models found this code
            code_count = 0
            for result in coding_results:
                if 'codes_found' in result and code_id in result['codes_found']:
                    code_count += 1
            
            # Observed disagreements
            Do = n_units * (len(coding_results) - code_count)
            Do_total += Do
            
            # Expected disagreements (assuming random chance)
            p = code_count / len(coding_results)  # prevalence
            De = 2 * p * (1 - p) * n_units
            De_total += De
        
        # Calculate alpha
        if De_total > 0:
            alpha = 1 - (Do_total / De_total)
        else:
            alpha = 1.0
        
        return max(0.0, min(1.0, alpha))  # Clamp between 0 and 1
    
    def create_reliability_report(self, coding_results: List[Dict[str, Any]], 
                                transcript_id: str, codebook) -> Dict[str, Any]:
        """Create comprehensive reliability report."""
        agreement_rates = self.calculate_agreement_rates(coding_results)
        overall_alpha = self.calculate_krippendorff_alpha(coding_results)
        
        # Create code-level report
        code_level_data = []
        for code_id, agreement_rate in agreement_rates.items():
            code_def = codebook.get_code_by_id(code_id)
            if code_def:
                code_level_data.append({
                    'Transcript': transcript_id,
                    'Code': code_id,
                    'Label': code_def.label,
                    'Category': code_def.category,
                    'Models_Agreed': int(agreement_rate * len(coding_results)),
                    'Agreement_Rate': agreement_rate
                })
        
        # Create category summary
        category_data = defaultdict(list)
        for item in code_level_data:
            category_data[item['Category']].append(item['Agreement_Rate'])
        
        category_summary = []
        for category, rates in category_data.items():
            category_summary.append({
                'Category': category,
                'Agreement_Rate_mean': np.mean(rates),
                'Agreement_Rate_std': np.std(rates),
                'Agreement_Rate_min': np.min(rates),
                'Agreement_Rate_max': np.max(rates)
            })
        
        return {
            'overall_alpha': overall_alpha,
            'code_level': code_level_data,
            'category_summary': category_summary,
            'n_models': len(coding_results),
            'transcript_id': transcript_id
        }
    
    def save_reliability_excel(self, report: Dict[str, Any], output_path: Path) -> None:
        """Save reliability report to Excel with multiple sheets."""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            # Code-level sheet
            code_df = pd.DataFrame(report['code_level'])
            if not code_df.empty:
                code_df.to_excel(writer, sheet_name='Code_Level', index=False)
            
            # Category summary sheet
            category_df = pd.DataFrame(report['category_summary'])
            if not category_df.empty:
                category_df.to_excel(writer, sheet_name='Category_Summary', index=False)
            
            # Ensure at least one sheet exists
            if code_df.empty and category_df.empty:
                placeholder_df = pd.DataFrame({
                    'Note': ['No coding data available for reliability analysis'],
                    'Reason': ['All models found no codes or there was no agreement between models']
                })
                placeholder_df.to_excel(writer, sheet_name='No_Data', index=False)
        
        print(f"Saved reliability report to {output_path}")


def analyze_consensus(coding_results: List[Dict[str, Any]], transcript_id: str) -> Dict[str, Any]:
    """Analyze consensus between models."""
    if len(coding_results) < 2:
        return {}
    
    # Extract all unique codes
    all_codes = set()
    for result in coding_results:
        if 'codes_found' in result:
            all_codes.update(result['codes_found'].keys())
    
    consensus_codes = {}
    
    for code_id in all_codes:
        # Find which models found this code
        models_found = []
        all_quotes = []
        all_speakers = set()
        
        for i, result in enumerate(coding_results):
            model_name = f"model_{i+1}"
            if 'codes_found' in result and code_id in result['codes_found']:
                models_found.append(model_name)
                
                # Collect quotes and speakers
                for instance in result['codes_found'][code_id]:
                    if 'quote' in instance:
                        all_quotes.append({
                            'quote': instance['quote'],
                            'speaker': instance.get('speaker', 'Unknown'),
                            'model': model_name
                        })
                        all_speakers.add(instance.get('speaker', 'Unknown'))
        
        # Determine consensus level
        total_models = len(coding_results)
        consensus_level = f"{len(models_found)}/{total_models} models"
        
        consensus_codes[code_id] = {
            'consensus_level': consensus_level,
            'evidence': {
                'models': models_found,
                'quotes': all_quotes,
                'speakers': list(all_speakers)
            }
        }
    
    # Calculate overall reliability
    calculator = ReliabilityCalculator()
    overall_alpha = calculator.calculate_krippendorff_alpha(coding_results)
    
    return {
        'transcript': transcript_id,
        'consensus_codes': consensus_codes,
        'reliability': overall_alpha,
        'n_speakers': len(set().union(*[set(c['evidence']['speakers']) for c in consensus_codes.values()]))
    } 