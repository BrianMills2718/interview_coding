"""
Main Orchestrator for Gemini25 Methodology
Handles transcript processing, LLM coding passes, and output generation
"""

import os
import json
import csv
import time
from typing import Dict, List, Any, Optional
from pathlib import Path

# Import our utilities
from utils.llm_api_clients import (
    call_openai_api, 
    call_anthropic_api, 
    call_gemini_api, 
    parse_coding_response,
    save_api_log
)
from utils.codebook_definitions import CODEBOOK, ANALYSIS_START_MARKER, get_codebook_summary

class Gemini25Analyzer:
    def __init__(self, data_dir: str = "data", outputs_dir: str = "outputs"):
        """
        Initialize the Gemini25 analyzer
        
        Args:
            data_dir: Directory containing processed transcripts
            outputs_dir: Directory for output files
        """
        self.data_dir = Path(data_dir)
        self.outputs_dir = Path(outputs_dir)
        self.coded_segments_dir = self.outputs_dir / "coded_segments"
        self.reliability_reports_dir = self.outputs_dir / "reliability_reports"
        self.logs_dir = self.outputs_dir / "logs"
        
        # Create output directories
        self.coded_segments_dir.mkdir(parents=True, exist_ok=True)
        self.reliability_reports_dir.mkdir(parents=True, exist_ok=True)
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        
        # Validate codebook
        if not self._validate_codebook():
            raise ValueError("Invalid codebook structure")
    
    def _validate_codebook(self) -> bool:
        """Validate the codebook structure"""
        for code, details in CODEBOOK.items():
            if not isinstance(details, dict):
                return False
            if 'definition' not in details:
                return False
        return True
    
    def load_transcript(self, transcript_file: str) -> str:
        """
        Load and preprocess transcript
        
        Args:
            transcript_file: Name of transcript file in data/processed/
            
        Returns:
            Processed transcript content
        """
        transcript_path = self.data_dir / "processed" / transcript_file
        
        if not transcript_path.exists():
            raise FileNotFoundError(f"Transcript file not found: {transcript_path}")
        
        with open(transcript_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find analysis start marker
        marker_pos = content.find(ANALYSIS_START_MARKER)
        if marker_pos != -1:
            content = content[marker_pos:]
        
        return content
    
    def generate_coding_prompt(self, transcript_content: str, model_name: str) -> str:
        """
        Generate the coding prompt for LLM analysis
        
        Args:
            transcript_content: The transcript content to analyze
            model_name: Name of the LLM model being used
            
        Returns:
            Formatted prompt for the LLM
        """
        codebook_summary = get_codebook_summary()
        
        prompt = f"""You are an expert qualitative researcher performing systematic coding of focus group transcripts.

TASK: Analyze the following transcript and extract relevant quotes, assign codes, and suggest emergent themes.

CODEBOOK:
{codebook_summary}

INSTRUCTIONS:
1. Read through the transcript carefully
2. Extract relevant quotes (segments of text) that relate to the research topic
3. For each quote, assign one or more codes from the CODEBOOK above
4. If you encounter content that doesn't fit existing codes, suggest new emergent themes
5. Provide your analysis in the following JSON format:

{{
    "coded_segments": [
        {{
            "quote": "exact text from transcript",
            "start_context": "brief context before quote",
            "end_context": "brief context after quote",
            "assigned_codes": ["CODE1", "CODE2"],
            "confidence": 0.85,
            "reasoning": "brief explanation of code assignment"
        }}
    ],
    "emergent_themes": [
        {{
            "theme_name": "NEW_THEME_NAME",
            "definition": "clear definition of the new theme",
            "example_quotes": ["quote1", "quote2"],
            "rationale": "why this theme is distinct from existing codes"
        }}
    ],
    "analysis_summary": {{
        "total_segments_coded": 15,
        "most_frequent_codes": ["CODE1", "CODE2"],
        "key_insights": ["insight1", "insight2"],
        "data_quality_notes": "any observations about transcript quality or coding challenges"
    }}
}}

TRANSCRIPT:
{transcript_content}

Please provide your analysis in the exact JSON format specified above. Ensure all quotes are exact text from the transcript."""
        
        return prompt
    
    def run_llm_coding(self, transcript_file: str, models: List[str] = None) -> Dict[str, Any]:
        """
        Run LLM coding analysis on a transcript
        
        Args:
            transcript_file: Name of transcript file
            models: List of models to use (default: all three)
            
        Returns:
            Dictionary with results from each model
        """
        if models is None:
            models = ["openai", "anthropic", "gemini"]
        
        # Load transcript
        transcript_content = self.load_transcript(transcript_file)
        
        results = {}
        
        for model in models:
            print(f"Running {model} analysis...")
            
            # Generate prompt
            prompt = self.generate_coding_prompt(transcript_content, model)
            
            # Call appropriate API
            if model == "openai":
                api_response = call_openai_api(prompt)
            elif model == "anthropic":
                api_response = call_anthropic_api(prompt)
            elif model == "gemini":
                api_response = call_gemini_api(prompt)
            else:
                print(f"Unknown model: {model}")
                continue
            
            # Parse response
            if api_response["success"]:
                parsed_data = parse_coding_response(api_response["content"])
                results[model] = {
                    "success": True,
                    "data": parsed_data,
                    "api_response": api_response
                }
                
                # Save to CSV
                self._save_to_csv(parsed_data, transcript_file, model)
                
                # Log API call
                log_data = {
                    "timestamp": time.time(),
                    "model": model,
                    "transcript": transcript_file,
                    "api_response": api_response
                }
                save_api_log(log_data, str(self.logs_dir / f"{model}_api_log.jsonl"))
                
            else:
                results[model] = {
                    "success": False,
                    "error": api_response["error"],
                    "api_response": api_response
                }
                print(f"Error with {model}: {api_response['error']}")
            
            # Rate limiting
            time.sleep(2)
        
        return results
    
    def _save_to_csv(self, parsed_data: Dict[str, Any], transcript_file: str, model: str):
        """
        Save parsed coding data to CSV
        
        Args:
            parsed_data: Parsed coding data
            transcript_file: Original transcript filename
            model: Model name
        """
        if not parsed_data.get("success", True):
            return
        
        # Extract base filename
        base_name = Path(transcript_file).stem
        
        # Save coded segments
        if "coded_segments" in parsed_data:
            csv_file = self.coded_segments_dir / f"{model}_{base_name}_coded.csv"
            
            with open(csv_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'quote', 'start_context', 'end_context', 
                    'assigned_codes', 'confidence', 'reasoning'
                ])
                
                for segment in parsed_data["coded_segments"]:
                    writer.writerow([
                        segment.get('quote', ''),
                        segment.get('start_context', ''),
                        segment.get('end_context', ''),
                        ';'.join(segment.get('assigned_codes', [])),
                        segment.get('confidence', ''),
                        segment.get('reasoning', '')
                    ])
        
        # Save emergent themes
        if "emergent_themes" in parsed_data:
            themes_file = self.coded_segments_dir / f"{model}_{base_name}_themes.csv"
            
            with open(themes_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'theme_name', 'definition', 'example_quotes', 'rationale'
                ])
                
                for theme in parsed_data["emergent_themes"]:
                    writer.writerow([
                        theme.get('theme_name', ''),
                        theme.get('definition', ''),
                        ';'.join(theme.get('example_quotes', [])),
                        theme.get('rationale', '')
                    ])
    
    def generate_reliability_report(self, transcript_file: str, human_coding_file: str = None) -> Dict[str, Any]:
        """
        Generate reliability report comparing LLM codings
        
        Args:
            transcript_file: Name of transcript file
            human_coding_file: Optional human coding file for comparison
            
        Returns:
            Reliability analysis results
        """
        # This would implement Cohen's Kappa and Fleiss' Kappa calculations
        # For now, return a placeholder structure
        return {
            "transcript": transcript_file,
            "reliability_metrics": {
                "cohens_kappa": {},
                "fleiss_kappa": {}
            },
            "agreement_analysis": {},
            "discrepancy_analysis": {}
        }

def main():
    """Main execution function"""
    analyzer = Gemini25Analyzer()
    
    # Get list of processed transcripts
    processed_dir = Path("data/processed")
    if not processed_dir.exists():
        print("No processed transcripts found. Please run batch_clean.py first.")
        return
    
    transcript_files = list(processed_dir.glob("*.txt"))
    
    if not transcript_files:
        print("No .txt files found in data/processed/")
        return
    
    print(f"Found {len(transcript_files)} transcript(s) to analyze")
    
    for transcript_file in transcript_files:
        print(f"\nAnalyzing {transcript_file.name}...")
        
        try:
            results = analyzer.run_llm_coding(transcript_file.name)
            
            # Print summary
            print(f"Analysis complete for {transcript_file.name}:")
            for model, result in results.items():
                if result["success"]:
                    print(f"  ✓ {model}: Success")
                else:
                    print(f"  ✗ {model}: {result['error']}")
                    
        except Exception as e:
            print(f"Error analyzing {transcript_file.name}: {e}")

if __name__ == "__main__":
    main() 