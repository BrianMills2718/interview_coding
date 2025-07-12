#!/usr/bin/env python3
"""
Sonnet Methodology Implementation
Multi-LLM Consensus Analysis with TAM/DOI Coding Schema

This script implements the Sonnet methodology for analyzing Microsoft Teams transcripts
using a consensus-based approach with Claude 3 Sonnet, GPT-4, and Gemini Pro.
"""

import os
import sys
import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
import pandas as pd
import numpy as np
from datetime import datetime

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent / "src"))

from analysis.output_manager import OutputManager, CodingResult
from utils.llm_utils import LLMClient
from utils.reliability import ReliabilityCalculator
from utils.consensus import ConsensusBuilder

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('sonnet_analysis.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class SonnetAnalyzer:
    """
    Main analyzer class for the Sonnet methodology
    Implements multi-LLM consensus analysis with TAM/DOI coding schema
    """
    
    def __init__(self, config_path: str = "config/sonnet_config.json"):
        self.config = self._load_config(config_path)
        self.output_manager = OutputManager(self.config.get('output_path', 'data/analysis_outputs/sonnet'))
        self.llm_client = LLMClient()
        self.reliability_calc = ReliabilityCalculator()
        self.consensus_builder = ConsensusBuilder()
        
        # TAM/DOI coding schema
        self.coding_schema = {
            'TAM': {
                'perceived_usefulness': [
                    'BENEFIT_EFFICIENCY',
                    'BENEFIT_CAPABILITY', 
                    'BENEFIT_QUALITY',
                    'BENEFIT_COST_SAVINGS'
                ],
                'perceived_ease_of_use': [
                    'BARRIER_TRAINING',
                    'BARRIER_TECHNICAL',
                    'AI_USAGE_WRITING',
                    'AI_USAGE_CODING'
                ],
                'perceived_barriers': [
                    'BARRIER_QUALITY',
                    'BARRIER_ACCESS',
                    'CONCERN_VALIDITY',
                    'CONCERN_ETHICS',
                    'CONCERN_JOBS'
                ],
                'usage_behavior': [
                    'AI_USAGE_CODING',
                    'AI_USAGE_ANALYSIS',
                    'AI_USAGE_WRITING',
                    'AI_USAGE_LITERATURE'
                ]
            },
            'DOI': {
                'relative_advantage': [
                    'BENEFIT_EFFICIENCY',
                    'BENEFIT_CAPABILITY',
                    'PAIN_ANALYSIS',
                    'PAIN_WRITING'
                ],
                'complexity': [
                    'BARRIER_TRAINING',
                    'CONCERN_VALIDITY',
                    'BARRIER_TECHNICAL'
                ],
                'compatibility': [
                    'METHODS_MIXED',
                    'ORG_SUPPORT',
                    'WORKFLOW_INTEGRATION'
                ],
                'observability': [
                    'AI_USAGE_CODING',
                    'AI_USAGE_ANALYSIS',
                    'SUCCESS_STORIES'
                ],
                'trialability': [
                    'BARRIER_ACCESS',
                    'ORG_BARRIERS',
                    'PILOT_PROGRAMS'
                ]
            }
        }
        
        # All unique codes
        self.all_codes = set()
        for framework in self.coding_schema.values():
            for category in framework.values():
                self.all_codes.update(category)
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration file"""
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.warning(f"Config file {config_path} not found, using defaults")
            return {
                'models': ['claude-3-sonnet', 'gpt-4', 'gemini-pro'],
                'consensus_threshold': 0.7,
                'output_path': 'data/analysis_outputs/sonnet',
                'transcript_path': 'data/processed'
            }
    
    def analyze_transcript(self, transcript_path: str, transcript_id: str) -> Dict[str, Any]:
        """
        Analyze a single transcript using the Sonnet methodology
        
        Args:
            transcript_path: Path to the transcript file
            transcript_id: Unique identifier for the transcript
            
        Returns:
            Dictionary containing consensus results and metadata
        """
        logger.info(f"Analyzing transcript: {transcript_id}")
        
        # Load transcript
        transcript_text = self._load_transcript(transcript_path)
        if not transcript_text:
            logger.error(f"Failed to load transcript: {transcript_path}")
            return {}
        
        # Get individual LLM coding results
        individual_results = []
        for model in self.config['models']:
            try:
                result = self._code_with_llm(model, transcript_text, transcript_id)
                if result:
                    individual_results.append(result)
                    self.output_manager.save_individual_coding_result(result, transcript_id)
            except Exception as e:
                logger.error(f"Error coding with {model}: {e}")
        
        if not individual_results:
            logger.error(f"No successful coding results for {transcript_id}")
            return {}
        
        # Build consensus
        consensus_result = self.consensus_builder.build_consensus(
            individual_results, 
            self.config['consensus_threshold']
        )
        
        # Calculate reliability metrics
        reliability_metrics = self.reliability_calc.calculate_reliability(individual_results)
        
        # Prepare final result
        final_result = {
            'transcript_id': transcript_id,
            'analysis_date': datetime.now().isoformat(),
            'models_used': [r.model_name for r in individual_results],
            'consensus_codes': consensus_result['codes'],
            'consensus_quotes': consensus_result['quotes'],
            'reliability_metrics': reliability_metrics,
            'individual_results': [r.dict() for r in individual_results]
        }
        
        # Save consensus result
        self.output_manager.save_consensus_result(final_result, transcript_id)
        
        logger.info(f"Completed analysis for {transcript_id}")
        return final_result
    
    def _load_transcript(self, transcript_path: str) -> Optional[str]:
        """Load transcript text from file"""
        try:
            if transcript_path.endswith('.txt'):
                with open(transcript_path, 'r', encoding='utf-8') as f:
                    return f.read()
            elif transcript_path.endswith('.csv'):
                df = pd.read_csv(transcript_path)
                if 'text' in df.columns:
                    return ' '.join(df['text'].dropna().astype(str))
                elif 'content' in df.columns:
                    return ' '.join(df['content'].dropna().astype(str))
            else:
                logger.error(f"Unsupported file format: {transcript_path}")
                return None
        except Exception as e:
            logger.error(f"Error loading transcript {transcript_path}: {e}")
            return None
    
    def _code_with_llm(self, model: str, transcript_text: str, transcript_id: str) -> Optional[CodingResult]:
        """
        Code transcript with a specific LLM using TAM/DOI schema
        
        Args:
            model: LLM model name
            transcript_text: Text content of transcript
            transcript_id: Transcript identifier
            
        Returns:
            CodingResult object with codes and confidence scores
        """
        prompt = self._build_coding_prompt(transcript_text)
        
        try:
            response = self.llm_client.query_model(model, prompt)
            codes = self._parse_coding_response(response, model)
            
            # Calculate overall confidence
            confidence_scores = [data.get('confidence', 0.0) for data in codes.values()]
            overall_confidence = np.mean(confidence_scores) if confidence_scores else 0.0
            
            return CodingResult(
                model_name=model,
                coding_type='TAM_DOI',
                codes=codes,
                confidence=overall_confidence,
                transcript_id=transcript_id
            )
            
        except Exception as e:
            logger.error(f"Error coding with {model}: {e}")
            return None
    
    def _build_coding_prompt(self, transcript_text: str) -> str:
        """Build the coding prompt for TAM/DOI analysis"""
        
        prompt = f"""
You are a qualitative researcher analyzing focus group transcripts about AI adoption in research organizations. 
Please code the following transcript using the Technology Acceptance Model (TAM) and Diffusion of Innovation (DOI) frameworks.

TRANSCRIPT:
{transcript_text[:8000]}  # Limit length for API constraints

CODING SCHEMA:

TECHNOLOGY ACCEPTANCE MODEL (TAM):
- Perceived Usefulness: BENEFIT_EFFICIENCY, BENEFIT_CAPABILITY, BENEFIT_QUALITY, BENEFIT_COST_SAVINGS
- Perceived Ease of Use: BARRIER_TRAINING, BARRIER_TECHNICAL, AI_USAGE_WRITING, AI_USAGE_CODING  
- Perceived Barriers: BARRIER_QUALITY, BARRIER_ACCESS, CONCERN_VALIDITY, CONCERN_ETHICS, CONCERN_JOBS
- Usage Behavior: AI_USAGE_CODING, AI_USAGE_ANALYSIS, AI_USAGE_WRITING, AI_USAGE_LITERATURE

DIFFUSION OF INNOVATION (DOI):
- Relative Advantage: BENEFIT_EFFICIENCY, BENEFIT_CAPABILITY, PAIN_ANALYSIS, PAIN_WRITING
- Complexity: BARRIER_TRAINING, CONCERN_VALIDITY, BARRIER_TECHNICAL
- Compatibility: METHODS_MIXED, ORG_SUPPORT, WORKFLOW_INTEGRATION
- Observability: AI_USAGE_CODING, AI_USAGE_ANALYSIS, SUCCESS_STORIES
- Trialability: BARRIER_ACCESS, ORG_BARRIERS, PILOT_PROGRAMS

INSTRUCTIONS:
1. For each code, determine if it is present in the transcript (true/false)
2. Provide a confidence score (0.0-1.0) for each code
3. Include relevant quotes that support each code
4. Return results in JSON format

RESPONSE FORMAT:
{{
    "BENEFIT_EFFICIENCY": {{
        "present": true/false,
        "confidence": 0.85,
        "quotes": [
            {{"text": "quote text", "speaker": "speaker name", "timestamp": "approximate location"}}
        ]
    }},
    // ... repeat for all codes
}}

Please analyze the transcript and return the coding results in the specified JSON format.
"""
        return prompt
    
    def _parse_coding_response(self, response: str, model: str) -> Dict[str, Any]:
        """Parse LLM response into structured coding data"""
        try:
            # Extract JSON from response
            if '```json' in response:
                json_start = response.find('```json') + 7
                json_end = response.find('```', json_start)
                json_str = response[json_start:json_end].strip()
            elif '{' in response and '}' in response:
                json_start = response.find('{')
                json_end = response.rfind('}') + 1
                json_str = response[json_start:json_end]
            else:
                logger.error(f"Could not extract JSON from {model} response")
                return {}
            
            codes = json.loads(json_str)
            
            # Validate and normalize codes
            normalized_codes = {}
            for code, data in codes.items():
                if code in self.all_codes:
                    normalized_codes[code] = {
                        'present': bool(data.get('present', False)),
                        'confidence': float(data.get('confidence', 0.0)),
                        'quotes': data.get('quotes', [])
                    }
            
            return normalized_codes
            
        except Exception as e:
            logger.error(f"Error parsing {model} response: {e}")
            return {}
    
    def run_batch_analysis(self, transcript_dir: str) -> List[Dict[str, Any]]:
        """
        Run analysis on all transcripts in a directory
        
        Args:
            transcript_dir: Directory containing transcript files
            
        Returns:
            List of analysis results for all transcripts
        """
        transcript_dir = Path(transcript_dir)
        results = []
        
        # Find all transcript files
        transcript_files = []
        for ext in ['.txt', '.csv']:
            transcript_files.extend(transcript_dir.glob(f'*{ext}'))
        
        logger.info(f"Found {len(transcript_files)} transcript files")
        
        for transcript_file in transcript_files:
            transcript_id = transcript_file.stem
            result = self.analyze_transcript(str(transcript_file), transcript_id)
            if result:
                results.append(result)
        
        return results
    
    def generate_cross_analysis(self, all_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate cross-transcript analysis and final report"""
        logger.info("Generating cross-transcript analysis")
        
        # Generate cross-transcript analysis
        cross_analysis = self.output_manager.generate_cross_transcript_analysis(all_results)
        
        # Calculate overall reliability
        all_reliability_metrics = [r.get('reliability_metrics', {}) for r in all_results]
        overall_reliability = self.reliability_calc.calculate_overall_reliability(all_reliability_metrics)
        
        # Save reliability analysis
        self.output_manager.save_reliability_analysis(overall_reliability, 'sonnet_overall')
        
        # Generate final report
        report_path = self.output_manager.generate_final_report(
            cross_analysis, all_results, overall_reliability
        )
        
        # Export for human review
        review_path = self.output_manager.export_for_human_review(all_results)
        
        logger.info(f"Cross-analysis complete. Report: {report_path}")
        logger.info(f"Human review export: {review_path}")
        
        return {
            'cross_analysis': cross_analysis,
            'reliability_summary': overall_reliability,
            'report_path': report_path,
            'review_path': review_path
        }

def main():
    """Main execution function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Sonnet Methodology Analysis')
    parser.add_argument('--transcript-dir', default='data/processed', 
                       help='Directory containing transcript files')
    parser.add_argument('--config', default='config/sonnet_config.json',
                       help='Configuration file path')
    parser.add_argument('--single-file', help='Analyze single transcript file')
    
    args = parser.parse_args()
    
    # Initialize analyzer
    analyzer = SonnetAnalyzer(args.config)
    
    if args.single_file:
        # Analyze single file
        transcript_id = Path(args.single_file).stem
        result = analyzer.analyze_transcript(args.single_file, transcript_id)
        if result:
            print(f"Analysis complete for {transcript_id}")
            print(f"Results saved to: {analyzer.output_manager.output_base_path}")
    else:
        # Batch analysis
        results = analyzer.run_batch_analysis(args.transcript_dir)
        if results:
            print(f"Batch analysis complete. Processed {len(results)} transcripts")
            
            # Generate cross-analysis
            cross_results = analyzer.generate_cross_analysis(results)
            print(f"Cross-analysis complete. Report: {cross_results['report_path']}")

if __name__ == "__main__":
    main() 