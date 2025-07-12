import os
import json
import pandas as pd
from datetime import datetime
from typing import Dict, List
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

class FocusGroupAnalyzer:
    def __init__(self):
        """Initialize the analyzer with API keys from environment variables"""
        # Set up API clients
        self.claude_client = anthropic.Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
        self.openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
        # Updated to latest Gemini model version (2.5)
        self.gemini_model = genai.GenerativeModel('gemini-1.5-pro')
        
        # Create output directories relative to project root
        ROOT_DIR       = Path(__file__).resolve().parents[2]
        OUTPUTS_DIR    = Path(os.getenv("OUTPUTS_DIR", ROOT_DIR / "outputs"))
        self.output_dir = OUTPUTS_DIR / "opus"
        (self.output_dir / "raw_outputs").mkdir(parents=True, exist_ok=True)
        (self.output_dir / "comparisons").mkdir(parents=True, exist_ok=True)
        
        # Standard analysis prompt
        self.analysis_prompt = """Analyze this focus group transcript about AI needs at RAND. Extract:

1. Research methods mentioned by participants
2. Specific challenges/pain points in their current work
3. AI applications or features participants suggested
4. Barriers to AI adoption they mentioned
5. What participants said about RAND's current AI tools (especially RandChat)
6. Suggestions participants made for training or support
7. Any other significant themes

For each finding, include:
- Direct quotes with speaker name
- Brief context if needed

Format your response as:
[THEME CATEGORY]
• Finding: [Brief description]
  Quote: "[Exact quote]" - [Speaker Name]
  
Be thorough and include ALL relevant quotes."""

    def analyze_with_claude(self, transcript: str, transcript_name: str) -> str:
        """Analyze transcript using Claude"""
        print(f"Analyzing {transcript_name} with Claude...")
        try:
            response = self.claude_client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=4000,
                temperature=0.2,
                messages=[
                    {
                        "role": "user",
                        "content": f"{self.analysis_prompt}\n\nTRANSCRIPT:\n{transcript}"
                    }
                ]
            )
            return response.content[0].text
        except Exception as e:
            print(f"Error with Claude: {e}")
            return f"Error: {str(e)}"

    def analyze_with_gpt4(self, transcript: str, transcript_name: str) -> str:
        """Analyze transcript using GPT-4"""
        print(f"Analyzing {transcript_name} with GPT-4...")
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {
                        "role": "user",
                        "content": f"{self.analysis_prompt}\n\nTRANSCRIPT:\n{transcript}"
                    }
                ]
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error with GPT-4: {e}")
            return f"Error: {str(e)}"

    def analyze_with_gemini(self, transcript: str, transcript_name: str) -> str:
        """Analyze transcript using Gemini"""
        print(f"Analyzing {transcript_name} with Gemini...")
        try:
            response = self.gemini_model.generate_content(
                f"{self.analysis_prompt}\n\nTRANSCRIPT:\n{transcript}",
                generation_config=genai.types.GenerationConfig(
                    temperature=0.2,
                    max_output_tokens=4000,
                )
            )
            return response.text
        except Exception as e:
            print(f"Error with Gemini: {e}")
            return f"Error: {str(e)}"

    def analyze_transcript(self, transcript_path: str) -> Dict[str, str]:
        """Run a transcript through all three models"""
        # Read transcript
        with open(transcript_path, 'r', encoding='utf-8') as f:
            transcript = f.read()
        
        transcript_name = Path(transcript_path).stem
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        results = {}
        
        # Analyze with each model
        results['claude'] = self.analyze_with_claude(transcript, transcript_name)
        time.sleep(2)  # Avoid rate limits
        
        results['gpt4'] = self.analyze_with_gpt4(transcript, transcript_name)
        time.sleep(2)
        
        results['gemini'] = self.analyze_with_gemini(transcript, transcript_name)
        
        # Save raw outputs
        for model, output in results.items():
            output_path = self.output_dir / "raw_outputs" / f"{transcript_name}_{model}_{timestamp}.txt"
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(output)
            print(f"Saved {model} output to {output_path}")
        
        return results

    def compare_results(self, results: Dict[str, str], transcript_name: str):
        """Create a comparison of findings across models"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        comparison = {
            'transcript': transcript_name,
            'timestamp': timestamp,
            'models_analyzed': list(results.keys()),
            'theme_comparison': []
        }
        
        # This is a simple comparison - you can make it more sophisticated
        themes = [
            "Research methods",
            "Challenges/pain points", 
            "AI applications suggested",
            "Barriers to adoption",
            "RandChat feedback",
            "Training suggestions"
        ]
        
        for theme in themes:
            theme_data = {
                'theme': theme,
                'found_by': []
            }
            
            for model, output in results.items():
                if theme.lower() in output.lower():
                    theme_data['found_by'].append(model)
            
            comparison['theme_comparison'].append(theme_data)
        
        # Save comparison
        comparison_path = self.output_dir / "comparisons" / f"{transcript_name}_comparison_{timestamp}.json"
        with open(comparison_path, 'w', encoding='utf-8') as f:
            json.dump(comparison, f, indent=2)
        
        print(f"\nComparison saved to {comparison_path}")
        return comparison

    def create_summary_spreadsheet(self, all_comparisons: List[Dict]):
        """Create a summary spreadsheet of all analyses"""
        data = []
        
        for comp in all_comparisons:
            for theme_data in comp['theme_comparison']:
                data.append({
                    'Transcript': comp['transcript'],
                    'Theme': theme_data['theme'],
                    'Claude': 'Yes' if 'claude' in theme_data['found_by'] else 'No',
                    'GPT-4': 'Yes' if 'gpt4' in theme_data['found_by'] else 'No',
                    'Gemini': 'Yes' if 'gemini' in theme_data['found_by'] else 'No',
                    'Consensus': 'Yes' if len(theme_data['found_by']) == 3 else 'Partial' if len(theme_data['found_by']) > 1 else 'No'
                })
        
        df = pd.DataFrame(data)
        summary_path = self.output_dir / f"analysis_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        df.to_excel(summary_path, index=False)
        print(f"\nSummary spreadsheet saved to {summary_path}")
        return df

def main():
    """Main execution function"""
    analyzer = FocusGroupAnalyzer()
    
    # Create a transcripts directory if it doesn't exist
    ROOT_DIR = Path(__file__).resolve().parents[2]
    PROCESSED_DIR = Path(os.getenv("PROCESSED_DIR", ROOT_DIR / "data" / "processed"))
    transcripts_dir = PROCESSED_DIR
    transcripts_dir.mkdir(parents=True, exist_ok=True)
    
    print("Multi-LLM Focus Group Analyzer")
    print("==============================")
    print(f"Place your transcript files in the '{transcripts_dir}' directory")
    print("Supported formats: .txt files")
    
    # Find all transcript files
    transcript_files = list(transcripts_dir.glob("*.txt"))
    
    if not transcript_files:
        print(f"\nNo transcript files found in {transcripts_dir}")
        print("Please add your transcript files and run again.")
        return
    
    print(f"\nFound {len(transcript_files)} transcript(s)")
    
    all_comparisons = []
    
    # Process each transcript
    for transcript_file in transcript_files:
        print(f"\n{'='*50}")
        print(f"Processing: {transcript_file.name}")
        print('='*50)
        
        try:
            # Analyze with all models
            results = analyzer.analyze_transcript(str(transcript_file))
            
            # Compare results
            comparison = analyzer.compare_results(results, transcript_file.stem)
            all_comparisons.append(comparison)
            
        except Exception as e:
            print(f"Error processing {transcript_file.name}: {e}")
            continue
    
    # Create summary spreadsheet if we processed multiple transcripts
    if len(all_comparisons) > 1:
        analyzer.create_summary_spreadsheet(all_comparisons)
    
    print("\n✅ Analysis complete!")
    print(f"Check the '{analyzer.output_dir}' directory for results")

if __name__ == "__main__":
    main()