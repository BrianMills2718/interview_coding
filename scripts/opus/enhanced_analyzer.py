"""Enhanced analyzer for Opus methodology.

Main analysis pipeline that integrates codebook, reliability calculation, and reporting.
"""

import os
import json
import pandas as pd
from datetime import datetime
from typing import Dict, List, Any
import time
from pathlib import Path

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Import LLM libraries
import anthropic
import openai
from openai import OpenAI
import google.generativeai as genai

# Import local modules
from codebook import Codebook, create_coding_prompt
from reliability_calculator import ReliabilityCalculator, analyze_consensus
from report_generator import ReportGenerator, create_summary_report


class EnhancedFocusGroupAnalyzer:
    def __init__(self):
        """Initialize the enhanced analyzer with API keys and codebook."""
        # Set up API clients
        self.claude_client = anthropic.Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
        self.openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
        self.gemini_model = genai.GenerativeModel('gemini-1.5-pro')
        
        # Load codebook
        self.codebook = Codebook()
        
        # Create output directories
        self.output_dir = Path("outputs/opus_enhanced")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        (self.output_dir / "raw_outputs").mkdir(exist_ok=True)
        (self.output_dir / "structured_coding").mkdir(exist_ok=True)
        (self.output_dir / "reliability").mkdir(exist_ok=True)
        (self.output_dir / "reports").mkdir(exist_ok=True)
        
        # Initialize reliability calculator and report generator
        self.reliability_calc = ReliabilityCalculator()
        self.report_gen = ReportGenerator(self.codebook)

    def analyze_with_claude(self, transcript: str, transcript_name: str) -> Dict[str, Any]:
        """Analyze transcript using Claude with structured coding."""
        print(f"Analyzing {transcript_name} with Claude...")
        try:
            prompt = create_coding_prompt(self.codebook) + f"\n{transcript}"
            
            response = self.claude_client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=4000,
                temperature=0.1,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            # Parse response
            content = response.content[0].text
            parsed_result = self._parse_llm_response(content, "claude")
            
            return {
                "raw_response": content,
                "codes_found": parsed_result.get("codes_found", {}),
                "model": "claude"
            }
        except Exception as e:
            print(f"Error with Claude: {e}")
            return {"raw_response": f"Error: {str(e)}", "codes_found": {}, "model": "claude"}

    def analyze_with_gpt4(self, transcript: str, transcript_name: str) -> Dict[str, Any]:
        """Analyze transcript using GPT-4 with structured coding."""
        print(f"Analyzing {transcript_name} with GPT-4...")
        try:
            prompt = create_coding_prompt(self.codebook) + f"\n{transcript}"
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            # Parse response
            content = response.choices[0].message.content
            parsed_result = self._parse_llm_response(content, "gpt4")
            
            return {
                "raw_response": content,
                "codes_found": parsed_result.get("codes_found", {}),
                "model": "gpt4"
            }
        except Exception as e:
            print(f"Error with GPT-4: {e}")
            return {"raw_response": f"Error: {str(e)}", "codes_found": {}, "model": "gpt4"}

    def analyze_with_gemini(self, transcript: str, transcript_name: str) -> Dict[str, Any]:
        """Analyze transcript using Gemini with structured coding."""
        print(f"Analyzing {transcript_name} with Gemini...")
        try:
            prompt = create_coding_prompt(self.codebook) + f"\n{transcript}"
            
            response = self.gemini_model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.1,
                    max_output_tokens=4000,
                )
            )
            
            # Parse response
            content = response.text
            parsed_result = self._parse_llm_response(content, "gemini")
            
            return {
                "raw_response": content,
                "codes_found": parsed_result.get("codes_found", {}),
                "model": "gemini"
            }
        except Exception as e:
            print(f"Error with Gemini: {e}")
            return {"raw_response": f"Error: {str(e)}", "codes_found": {}, "model": "gemini"}

    def _parse_llm_response(self, response: str, model_name: str) -> Dict[str, Any]:
        """Parse LLM response to extract structured coding results."""
        try:
            # Clean up response (remove markdown code blocks if present)
            cleaned = response.strip()
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            cleaned = cleaned.strip()
            
            # Try to extract JSON object from response
            # Handle cases where model adds explanation after JSON
            if cleaned.startswith('{'):
                # Find the matching closing brace
                brace_count = 0
                json_end = -1
                for i, char in enumerate(cleaned):
                    if char == '{':
                        brace_count += 1
                    elif char == '}':
                        brace_count -= 1
                        if brace_count == 0:
                            json_end = i + 1
                            break
                
                if json_end > 0:
                    json_str = cleaned[:json_end]
                    result = json.loads(json_str)
                    return result
            
            # Fallback: try to parse the whole response
            result = json.loads(cleaned)
            return result
        except json.JSONDecodeError as e:
            print(f"Failed to parse {model_name} response: {e}")
            # Try to extract codes_found from raw response if possible
            if '"codes_found"' in response:
                try:
                    # Extract just the codes_found object
                    start = response.find('"codes_found"')
                    if start > 0:
                        # Find the object boundaries
                        obj_start = response.find('{', start)
                        if obj_start > 0:
                            brace_count = 1
                            i = obj_start + 1
                            while i < len(response) and brace_count > 0:
                                if response[i] == '{':
                                    brace_count += 1
                                elif response[i] == '}':
                                    brace_count -= 1
                                i += 1
                            if brace_count == 0:
                                codes_json = response[obj_start:i]
                                return {"codes_found": json.loads(codes_json)}
                except:
                    pass
            return {"codes_found": {}}
        except Exception as e:
            print(f"Error parsing {model_name} response: {e}")
            return {"codes_found": {}}

    def analyze_transcript(self, transcript_path: str) -> Dict[str, Any]:
        """Run a transcript through all three models with enhanced analysis."""
        # Read transcript
        with open(transcript_path, 'r', encoding='utf-8') as f:
            transcript = f.read()
        
        transcript_name = Path(transcript_path).stem
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        results = []
        
        # Analyze with each model
        results.append(self.analyze_with_claude(transcript, transcript_name))
        time.sleep(2)  # Avoid rate limits
        
        results.append(self.analyze_with_gpt4(transcript, transcript_name))
        time.sleep(2)
        
        results.append(self.analyze_with_gemini(transcript, transcript_name))
        
        # Save raw outputs
        for result in results:
            model = result['model']
            output_path = self.output_dir / "raw_outputs" / f"{transcript_name}_{model}_{timestamp}.json"
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2)
            print(f"Saved {model} output to {output_path}")
        
        # Save structured coding results
        for result in results:
            model = result['model']
            structured_path = self.output_dir / "structured_coding" / f"{transcript_name}_{model}_{timestamp}.json"
            with open(structured_path, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2)
        
        # Calculate reliability
        reliability_report = self.reliability_calc.create_reliability_report(
            results, transcript_name, self.codebook
        )
        
        # Save reliability report
        reliability_path = self.output_dir / "reliability" / f"reliability_report_{transcript_name}_{timestamp}.xlsx"
        self.reliability_calc.save_reliability_excel(reliability_report, reliability_path)
        
        # Analyze consensus
        consensus_analysis = analyze_consensus(results, transcript_name)
        consensus_path = self.output_dir / "structured_coding" / f"{transcript_name}_complete_{timestamp}.json"
        with open(consensus_path, 'w', encoding='utf-8') as f:
            json.dump(consensus_analysis, f, indent=2)
        
        # Generate narrative report
        narrative_report = self.report_gen.create_narrative_report(
            results, reliability_report, consensus_analysis, transcript_name
        )
        self.report_gen.save_report(narrative_report, transcript_name, self.output_dir / "reports")
        
        return {
            'transcript_id': transcript_name,
            'timestamp': timestamp,
            'individual_results': results,
            'reliability_report': reliability_report,
            'consensus_analysis': consensus_analysis,
            'overall_alpha': reliability_report['overall_alpha']
        }

    def run_analysis(self, transcripts_dir: str = "data/processed") -> None:
        """Run enhanced analysis on all transcripts."""
        transcripts_path = Path(transcripts_dir)
        transcript_files = list(transcripts_path.glob("*.txt"))
        
        if not transcript_files:
            print(f"No transcript files found in {transcripts_dir}")
            return
        
        print(f"Found {len(transcript_files)} transcript(s) for enhanced analysis")
        
        all_reports = []
        
        for transcript_file in transcript_files:
            print(f"\n{'='*50}")
            print(f"Processing: {transcript_file.name}")
            print('='*50)
            
            try:
                result = self.analyze_transcript(str(transcript_file))
                all_reports.append(result)
                print(f"Completed {transcript_file.name} - α = {result['overall_alpha']:.3f}")
            except Exception as e:
                print(f"Error processing {transcript_file.name}: {e}")
                continue
        
        # Create summary report
        if len(all_reports) > 1:
            create_summary_report(all_reports, self.output_dir / "reports")
        
        print(f"\n[SUCCESS] Enhanced analysis complete!")
        print(f"Check the '{self.output_dir}' directory for results")


def main():
    """Main execution function."""
    analyzer = EnhancedFocusGroupAnalyzer()
    analyzer.run_analysis()


if __name__ == "__main__":
    main() 