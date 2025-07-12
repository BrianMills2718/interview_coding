"""Single transcript deductive coding runner for o3 methodology.

Optimized version for testing with expanded codebook and improved prompts.
Processes just one transcript for faster iteration.
"""

import pandas as pd
from pathlib import Path
import os
import json
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dotenv import load_dotenv
import anthropic
import openai
import google.generativeai as genai

load_dotenv()

# Model assignments
MODEL_CLAUDE = os.getenv("O3_CLAUDE_MODEL", "claude-3-5-sonnet-20241022")
MODEL_GPT = os.getenv("O3_GPT4_MODEL", "gpt-4o")
MODEL_GEMINI = os.getenv("O3_GEMINI_MODEL", "gemini-1.5-pro")

# Expanded code list based on inductive analysis
DEDUCTIVE_CODES = [
    # Research Methods - Core
    "RM_METHOD::Qual_Interview",
    "RM_METHOD::Survey", 
    "RM_METHOD::Simulation",
    "RM_METHOD::Econometric",
    
    # Research Methods - Discovered via Inductive Analysis
    "RM_METHOD::Case_Study",
    "RM_METHOD::Literature_Review", 
    "RM_METHOD::Mixed_Methods",
    "RM_METHOD::Focus_Group",
    "RM_METHOD::Think_Aloud",
    "RM_METHOD::Process_Tracing",
    "RM_METHOD::Statistical_Test",
    
    # Research Steps and Workflow
    "RM_STEP_DIFFICULT",
    "RM_STEP::Survey_Design",
    "RM_STEP::Data_Collection",
    "RM_STEP::Analysis",
    "RM_STEP::Writing",
    
    # AI Pain Points
    "AI_PAIN_POINT::Coding",
    "AI_PAIN_POINT::Transcription", 
    "AI_PAIN_POINT::Scheduling",
    "AI_PAIN_POINT::Data_Quality",
    "AI_PAIN_POINT::Analysis_Limitations",
    
    # AI Barriers
    "AI_BARRIER::Security",
    "AI_BARRIER::Training",
    "AI_BARRIER::Licensing",
    "AI_BARRIER::Privacy",
    "AI_BARRIER::Technical",
    "AI_BARRIER::Access",
    
    # AI Benefits and Capabilities
    "AI_BENEFIT::Efficiency",
    "AI_BENEFIT::Transcription_Quality",
    "AI_BENEFIT::Data_Processing",
    "AI_BENEFIT::Analysis_Support",
    
    # AI Usage Patterns
    "AI_USAGE::Coding",
    "AI_USAGE::Analysis", 
    "AI_USAGE::Writing",
    "AI_USAGE::Chat_Tools",
    
    # Concerns and Ethics
    "ETHICS_CONCERN",
    "CONCERN::Validity",
    "CONCERN::Overreliance",
    "CONCERN::Information_Integrity",
    
    # Training and Support
    "TRAINING_NEED",
    "TRAINING::Policy_Guidance",
    "TRAINING::Direct_Training",
    
    # Tools and Gaps
    "TOOL_GAP",
    "EMERGING_TOOL",
    "ADOPTION_RECOMMEND",
    
    # Organizational Factors
    "ORG::Capacity_Constraint",
    "ORG::Collaboration",
    "ORG::Support_Needed"
]

# Initialize clients
claude_client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
openai_client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
gemini_model = genai.GenerativeModel(MODEL_GEMINI)

ROOT = Path(__file__).resolve().parents[2]
PROC_DIR = Path(os.getenv("PROCESSED_DIR", ROOT / "data" / "processed"))
OUTPUT_DIR = Path(os.getenv("OUTPUTS_DIR", ROOT / "outputs")) / "deductive"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def create_optimized_deductive_prompt(uid: str, text: str) -> str:
    """Create optimized deductive prompt with expanded context."""
    codes_json = json.dumps(DEDUCTIVE_CODES, indent=2)
    return f"""You are an expert qualitative researcher analyzing transcripts from a RAND Corporation focus group study about research methods and AI adoption.

STUDY CONTEXT:
This focus group explored how RAND researchers currently conduct their work and how AI tools might enhance their research capabilities. The study aimed to:
- Identify commonly used research methods and workflow steps
- Understand pain points and time-consuming aspects of research
- Explore potential AI applications and benefits
- Identify barriers to AI adoption (technical, training, ethical, accessibility)
- Assess training needs and support requirements
- Identify gaps in current AI tools and recommendations for improvements

CODING TASK:
Analyze this speaker turn and identify ALL applicable codes from the predefined list below. Be thorough and inclusive - if a speaker mentions research methods, pain points, AI usage, barriers, benefits, or any related themes, code them appropriately.

SPECIFIC GUIDANCE:
- Research Methods: Look for any mention of interviews, surveys, case studies, literature reviews, mixed methods, focus groups, statistical tests, simulations, etc.
- Pain Points: Identify time-consuming steps, difficult processes, workflow challenges, data quality issues
- AI Applications: Note any discussion of AI for coding, analysis, transcription, writing, chat tools, data processing
- Barriers: Technical difficulties, training needs, security concerns, access limitations, privacy issues
- Benefits: Efficiency gains, quality improvements, capability enhancements, transcription quality
- Training: Policy guidance needs, direct training requirements, skill gaps
- Ethics: Validity concerns, overreliance issues, information integrity, bias concerns

IMPORTANT: Be generous in your coding - if content relates to the themes above, apply the relevant codes. Multiple codes can apply to a single speaker turn.

Available codes:
{codes_json}

Analyze this speaker turn:
UID: {uid}
Text: {text}

Return a JSON object for each code that applies:
{{
  "uid": "{uid}",
  "code": "CODE_NAME",
  "prob": 1.0
}}

If no codes apply, return an empty array []. Apply codes liberally when content is relevant to the study themes."""


def call_claude_sonnet(prompt: str, temperature: float = 0.0) -> str:
    """Call Claude Sonnet with retry logic."""
    try:
        response = claude_client.messages.create(
            model=MODEL_CLAUDE,
            max_tokens=1000,
            temperature=temperature,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text
    except Exception as e:
        print(f"Claude error: {e}")
        return None


def call_gpt4o(prompt: str, temperature: float = 0.0) -> str:
    """Call GPT-4o with retry logic."""
    try:
        response = openai_client.chat.completions.create(
            model=MODEL_GPT,
            messages=[{"role": "user", "content": prompt}],
            max_completion_tokens=1000
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"GPT-4o error: {e}")
        return None


def call_gemini(prompt: str, temperature: float = 0.0) -> str:
    """Call Gemini with retry logic."""
    try:
        response = gemini_model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=temperature,
                max_output_tokens=1000
            )
        )
        return response.text
    except Exception as e:
        print(f"Gemini error: {e}")
        return None


def parse_llm_response(response: str) -> list:
    """Parse LLM response into structured format."""
    if not response:
        return []
    
    try:
        # Try to parse as JSON array first
        parsed = json.loads(response)
        if isinstance(parsed, list):
            return parsed
        elif isinstance(parsed, dict):
            return [parsed]
        else:
            return []
    except json.JSONDecodeError:
        # If JSON parsing fails, try to extract JSON from text
        try:
            start = response.find('[')
            end = response.rfind(']') + 1
            if start != -1 and end != 0:
                json_str = response[start:end]
                return json.loads(json_str)
        except:
            pass
        return []


def write_jsonl(data: list, filepath: Path) -> None:
    """Write data to JSONL file."""
    with open(filepath, 'w', encoding='utf-8') as f:
        for item in data:
            f.write(json.dumps(item) + '\n')


def process_with_model(model_name: str, model_func, df: pd.DataFrame, transcript_id: str) -> list:
    """Process transcript with a specific model."""
    print(f"Running {model_name}...")
    results = []
    
    for idx, row in df.iterrows():
        uid = row['uid']
        text = row['text']
        
        prompt = create_optimized_deductive_prompt(uid, text)
        if model_name == "GPT-4o":
            response = model_func(prompt)
        else:
            response = model_func(prompt, temperature=0.0)
        
        if response:
            parsed = parse_llm_response(response)
            results.extend(parsed)
        
        # Rate limiting
        if (idx + 1) % 10 == 0:
            print(f"  {model_name}: Processed {idx + 1}/{len(df)} turns")
            time.sleep(0.1)  # Minimal sleep for testing
    
    # Write results
    model_short = model_name.split('-')[0].upper()
    output_file = OUTPUT_DIR / f"{transcript_id}_tags_{model_short}.jsonl"
    write_jsonl(results, output_file)
    
    return results


def process_single_transcript(transcript_id: str = "RAND_METHODS_ALICE_HUGUET") -> None:
    """Process a single transcript CSV file with all 3 models in parallel."""
    csv_path = PROC_DIR / f"{transcript_id}_tidy.csv"
    
    if not csv_path.exists():
        print(f"Transcript file not found: {csv_path}")
        return
    
    print(f"\n=== OPTIMIZED SINGLE TRANSCRIPT DEDUCTIVE ANALYSIS ===")
    print(f"Processing: {transcript_id}")
    print(f"Expanded codebook: {len(DEDUCTIVE_CODES)} codes")
    
    # Read tidy CSV
    df = pd.read_csv(csv_path)
    print(f"Found {len(df)} speaker turns")
    
    # Define models to run
    models = [
        ("Claude-Sonnet", call_claude_sonnet),
        ("GPT-4o", call_gpt4o),
        ("Gemini", call_gemini)
    ]
    
    # Process with all models in parallel
    results = {}
    with ThreadPoolExecutor(max_workers=3) as executor:
        # Submit all model processing tasks
        future_to_model = {
            executor.submit(process_with_model, model_name, model_func, df, transcript_id): model_name
            for model_name, model_func in models
        }
        
        # Collect results as they complete
        for future in as_completed(future_to_model):
            model_name = future_to_model[future]
            try:
                model_results = future.result()
                results[model_name] = model_results
                print(f"[SUCCESS] {model_name} completed: {len(model_results)} tags")
            except Exception as e:
                print(f"[ERROR] {model_name} failed: {e}")
                results[model_name] = []
    
    # Summary
    summary = ", ".join([f"{len(results[model_name])} {model_name.split('-')[0]} tags" for model_name in results.keys()])
    print(f"\n=== RESULTS ===")
    print(f"Completed {transcript_id}: {summary}")
    
    # Show code distribution
    all_codes = set()
    for model_results in results.values():
        for item in model_results:
            if 'code' in item:
                all_codes.add(item['code'])
    
    print(f"Unique codes found: {len(all_codes)}")
    if all_codes:
        print("Codes applied:")
        for code in sorted(all_codes):
            print(f"  - {code}")
    
    print(f"\nResults saved to: {OUTPUT_DIR}")


def main():
    """Main function for single transcript testing."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Single Transcript Deductive Coding')
    parser.add_argument('--transcript', default='RAND_METHODS_ALICE_HUGUET',
                       help='Transcript ID to process')
    
    args = parser.parse_args()
    
    process_single_transcript(args.transcript)


if __name__ == "__main__":
    main() 