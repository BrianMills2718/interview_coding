"""
Reliability Calculator for Gemini25 Methodology
Implements Cohen's Kappa and Fleiss' Kappa for inter-rater reliability analysis
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Tuple
from pathlib import Path
import json
from sklearn.metrics import cohen_kappa_score
from collections import defaultdict

class ReliabilityCalculator:
    def __init__(self, outputs_dir: str = "outputs"):
        """
        Initialize the reliability calculator
        
        Args:
            outputs_dir: Directory containing coded outputs
        """
        self.outputs_dir = Path(outputs_dir)
        self.coded_segments_dir = self.outputs_dir / "coded_segments"
        self.reliability_reports_dir = self.outputs_dir / "reliability_reports"
        
        # Create reliability reports directory
        self.reliability_reports_dir.mkdir(parents=True, exist_ok=True)
    
    def load_coded_data(self, transcript_file: str, models: List[str]) -> Dict[str, pd.DataFrame]:
        """
        Load coded data from CSV files
        
        Args:
            transcript_file: Name of transcript file
            models: List of model names to load
            
        Returns:
            Dictionary mapping model names to DataFrames
        """
        base_name = Path(transcript_file).stem
        coded_data = {}
        
        for model in models:
            csv_file = self.coded_segments_dir / f"{model}_{base_name}_coded.csv"
            
            if csv_file.exists():
                df = pd.read_csv(csv_file)
                coded_data[model] = df
            else:
                print(f"Warning: No coded data found for {model}")
        
        return coded_data
    
    def normalize_segments(self, coded_data: Dict[str, pd.DataFrame]) -> pd.DataFrame:
        """
        Normalize segments across different models for comparison
        
        Args:
            coded_data: Dictionary of coded data from different models
            
        Returns:
            Normalized DataFrame with segments aligned
        """
        # This is a simplified approach - in practice, you might need more sophisticated
        # text matching or fuzzy matching to align segments across models
        
        all_segments = []
        
        for model, df in coded_data.items():
            for _, row in df.iterrows():
                segment_info = {
                    'quote': row['quote'],
                    'model': model,
                    'codes': row['assigned_codes'].split(';') if pd.notna(row['assigned_codes']) else [],
                    'confidence': row['confidence'],
                    'reasoning': row['reasoning']
                }
                all_segments.append(segment_info)
        
        return pd.DataFrame(all_segments)
    
    def calculate_cohens_kappa(self, rater1_codes: List[str], rater2_codes: List[str]) -> float:
        """
        Calculate Cohen's Kappa for two raters
        
        Args:
            rater1_codes: Codes assigned by first rater
            rater2_codes: Codes assigned by second rater
            
        Returns:
            Cohen's Kappa score
        """
        # Create binary vectors for each code
        all_codes = list(set(rater1_codes + rater2_codes))
        
        rater1_vector = [1 if code in rater1_codes else 0 for code in all_codes]
        rater2_vector = [1 if code in rater2_codes else 0 for code in all_codes]
        
        if len(set(rater1_vector + rater2_vector)) == 1:
            # All values are the same (perfect agreement or perfect disagreement)
            return 1.0 if rater1_vector == rater2_vector else 0.0
        
        return cohen_kappa_score(rater1_vector, rater2_vector)
    
    def calculate_fleiss_kappa(self, all_raters_codes: List[List[str]]) -> float:
        """
        Calculate Fleiss' Kappa for multiple raters
        
        Args:
            all_raters_codes: List of code lists, one per rater
            
        Returns:
            Fleiss' Kappa score
        """
        # Get all unique codes
        all_codes = list(set([code for rater_codes in all_raters_codes for code in rater_codes]))
        
        # Create matrix where rows are segments and columns are codes
        n_raters = len(all_raters_codes)
        n_codes = len(all_codes)
        
        if n_codes == 0:
            return 1.0  # No codes to compare
        
        # Create binary matrix
        matrix = np.zeros((1, n_codes))
        
        for rater_codes in all_raters_codes:
            for code in rater_codes:
                if code in all_codes:
                    code_idx = all_codes.index(code)
                    matrix[0, code_idx] += 1
        
        # Calculate Fleiss' Kappa
        n = matrix.shape[0]  # number of subjects
        k = matrix.shape[1]  # number of categories
        
        if n == 0 or k == 0:
            return 1.0
        
        # Calculate P_j (proportion of assignments to category j)
        P_j = np.sum(matrix, axis=0) / (n * n_raters)
        
        # Calculate P_i (proportion of agreement for subject i)
        P_i = np.sum(matrix * (matrix - 1), axis=1) / (n_raters * (n_raters - 1))
        
        # Calculate P_bar (mean of P_i)
        P_bar = np.mean(P_i)
        
        # Calculate P_e (expected agreement by chance)
        P_e = np.sum(P_j ** 2)
        
        # Calculate Fleiss' Kappa
        if P_e == 1:
            return 1.0
        
        kappa = (P_bar - P_e) / (1 - P_e)
        
        return float(kappa)
    
    def analyze_reliability(self, transcript_file: str, models: List[str] = None, 
                          human_coding_file: str = None) -> Dict[str, Any]:
        """
        Perform comprehensive reliability analysis
        
        Args:
            transcript_file: Name of transcript file
            models: List of models to analyze (default: all available)
            human_coding_file: Optional human coding file for comparison
            
        Returns:
            Reliability analysis results
        """
        if models is None:
            models = ["openai", "anthropic", "gemini"]
        
        # Load coded data
        coded_data = self.load_coded_data(transcript_file, models)
        
        if not coded_data:
            return {"error": "No coded data found"}
        
        # Normalize segments
        normalized_data = self.normalize_segments(coded_data)
        
        # Calculate pairwise Cohen's Kappa
        pairwise_kappa = {}
        model_names = list(coded_data.keys())
        
        for i, model1 in enumerate(model_names):
            for j, model2 in enumerate(model_names[i+1:], i+1):
                pair_name = f"{model1}_vs_{model2}"
                
                # Get codes for this pair
                model1_codes = []
                model2_codes = []
                
                for _, row in normalized_data.iterrows():
                    if row['model'] == model1:
                        model1_codes.extend(row['codes'])
                    elif row['model'] == model2:
                        model2_codes.extend(row['codes'])
                
                kappa = self.calculate_cohens_kappa(model1_codes, model2_codes)
                pairwise_kappa[pair_name] = kappa
        
        # Calculate Fleiss' Kappa for all models
        all_raters_codes = []
        for model in model_names:
            model_codes = []
            for _, row in normalized_data.iterrows():
                if row['model'] == model:
                    model_codes.extend(row['codes'])
            all_raters_codes.append(model_codes)
        
        fleiss_kappa = self.calculate_fleiss_kappa(all_raters_codes)
        
        # Generate report
        report = {
            "transcript_file": transcript_file,
            "models_analyzed": model_names,
            "pairwise_cohens_kappa": pairwise_kappa,
            "fleiss_kappa": fleiss_kappa,
            "interpretation": self._interpret_kappa_scores(pairwise_kappa, fleiss_kappa),
            "summary_statistics": {
                "mean_pairwise_kappa": np.mean(list(pairwise_kappa.values())),
                "min_pairwise_kappa": min(pairwise_kappa.values()) if pairwise_kappa else 0,
                "max_pairwise_kappa": max(pairwise_kappa.values()) if pairwise_kappa else 0
            }
        }
        
        # Save report
        self._save_reliability_report(report, transcript_file)
        
        return report
    
    def _interpret_kappa_scores(self, pairwise_kappa: Dict[str, float], 
                               fleiss_kappa: float) -> Dict[str, str]:
        """
        Interpret Kappa scores according to standard guidelines
        
        Args:
            pairwise_kappa: Dictionary of pairwise Cohen's Kappa scores
            fleiss_kappa: Fleiss' Kappa score
            
        Returns:
            Dictionary with interpretations
        """
        def interpret_kappa(kappa: float) -> str:
            if kappa < 0:
                return "Poor (worse than chance)"
            elif kappa < 0.01:
                return "Poor"
            elif kappa < 0.20:
                return "Slight"
            elif kappa < 0.40:
                return "Fair"
            elif kappa < 0.60:
                return "Moderate"
            elif kappa < 0.80:
                return "Substantial"
            elif kappa < 0.90:
                return "Almost Perfect"
            else:
                return "Perfect"
        
        interpretations = {
            "fleiss_kappa_interpretation": interpret_kappa(fleiss_kappa)
        }
        
        for pair, kappa in pairwise_kappa.items():
            interpretations[f"{pair}_interpretation"] = interpret_kappa(kappa)
        
        return interpretations
    
    def _save_reliability_report(self, report: Dict[str, Any], transcript_file: str):
        """
        Save reliability report to file
        
        Args:
            report: Reliability analysis report
            transcript_file: Name of transcript file
        """
        base_name = Path(transcript_file).stem
        report_file = self.reliability_reports_dir / f"{base_name}_reliability_report.json"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        # Also save as CSV for easy viewing
        csv_file = self.reliability_reports_dir / f"{base_name}_reliability_summary.csv"
        
        summary_data = []
        for pair, kappa in report["pairwise_cohens_kappa"].items():
            summary_data.append({
                "comparison": pair,
                "kappa_score": kappa,
                "interpretation": report["interpretation"][f"{pair}_interpretation"]
            })
        
        summary_data.append({
            "comparison": "all_models",
            "kappa_score": report["fleiss_kappa"],
            "interpretation": report["interpretation"]["fleiss_kappa_interpretation"]
        })
        
        summary_df = pd.DataFrame(summary_data)
        summary_df.to_csv(csv_file, index=False)

def main():
    """Main execution function for reliability analysis"""
    calculator = ReliabilityCalculator()
    
    # Get list of transcript files
    processed_dir = Path("data/processed")
    if not processed_dir.exists():
        print("No processed transcripts found.")
        return
    
    transcript_files = list(processed_dir.glob("*.txt"))
    
    if not transcript_files:
        print("No transcript files found.")
        return
    
    for transcript_file in transcript_files:
        print(f"Analyzing reliability for {transcript_file.name}...")
        
        try:
            report = calculator.analyze_reliability(transcript_file.name)
            
            if "error" not in report:
                print(f"✓ Reliability analysis complete for {transcript_file.name}")
                print(f"  Fleiss' Kappa: {report['fleiss_kappa']:.3f}")
                print(f"  Mean pairwise Kappa: {report['summary_statistics']['mean_pairwise_kappa']:.3f}")
            else:
                print(f"✗ Error: {report['error']}")
                
        except Exception as e:
            print(f"Error analyzing reliability for {transcript_file.name}: {e}")

if __name__ == "__main__":
    main() 