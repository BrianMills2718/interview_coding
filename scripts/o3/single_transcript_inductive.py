"""Single transcript inductive coding runner for o3 methodology.

Optimized version for testing with improved prompts for theme discovery.
Processes just one transcript for faster iteration.
"""

import pandas as pd
from pathlib import Path
import os
import json
import time
from dotenv import load_dotenv
import anthropic
import openai

load_dotenv()

# Model assignments
MODEL_CLAUDE = os.getenv("O3_CLAUDE_MODEL", "claude-3-5-sonnet-20241022")
MODEL_GPT = os.getenv("O3_GPT4_MODEL", "gpt-4o")

# Expanded deductive codes for reference
EXISTING_CODES = [
    "RM_METHOD::Qual_Interview", "RM_METHOD::Survey", "RM_METHOD::Simulation", "RM_METHOD::Econometric",
    "RM_METHOD::Case_Study", "RM_METHOD::Literature_Review", "RM_METHOD::Mixed_Methods", "RM_METHOD::Focus_Group",
    "RM_METHOD::Think_Aloud", "RM_METHOD::Process_Tracing", "RM_METHOD::Statistical_Test",
    "RM_STEP_DIFFICULT", "RM_STEP::Survey_Design", "RM_STEP::Data_Collection", "RM_STEP::Analysis", "RM_STEP::Writing",
    "AI_PAIN_POINT::Coding", "AI_PAIN_POINT::Transcription", "AI_PAIN_POINT::Scheduling", "AI_PAIN_POINT::Data_Quality",
    "AI_PAIN_POINT::Analysis_Limitations", "AI_BARRIER::Security", "AI_BARRIER::Training", "AI_BARRIER::Licensing",
    "AI_BARRIER::Privacy", "AI_BARRIER::Technical", "AI_BARRIER::Access", "AI_BENEFIT::Efficiency",
    "AI_BENEFIT::Transcription_Quality", "AI_BENEFIT::Data_Processing", "AI_BENEFIT::Analysis_Support",
    "AI_USAGE::Coding", "AI_USAGE::Analysis", "AI_USAGE::Writing", "AI_USAGE::Chat_Tools",
    "ETHICS_CONCERN", "CONCERN::Validity", "CONCERN::Overreliance", "CONCERN::Information_Integrity",
    "TRAINING_NEED", "TRAINING::Policy_Guidance", "TRAINING::Direct_Training",
    "TOOL_GAP", "EMERGING_TOOL", "ADOPTION_RECOMMEND",
    "ORG::Capacity_Constraint", "ORG::Collaboration", "ORG::Support_Needed"
]

# Initialize clients
claude_client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
openai_client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

ROOT = Path(__file__).resolve().parents[2]
PROC_DIR = Path(os.getenv("PROCESSED_DIR", ROOT / "data" / "processed"))
OUTPUT_DIR = Path(os.getenv("OUTPUTS_DIR", ROOT / "outputs")) / "inductive"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def create_optimized_inductive_prompt(uid: str, text: str) -> str:
    """Create optimized inductive prompt for theme discovery."""
    codes_json = json.dumps(EXISTING_CODES, indent=2)
    return f"""You are an expert qualitative researcher conducting exploratory analysis of RAND Corporation focus group transcripts about research methods and AI adoption.

STUDY CONTEXT:
This focus group explored how RAND researchers currently conduct their work and how AI tools might enhance their research capabilities. You are looking for NEW themes and patterns that might not be captured by existing codes.

DISCOVERY TASK:
Analyze this speaker turn for novel themes, patterns, or concepts that are NOT already covered by the existing codebook. Look for:

1. SPECIFIC RESEARCH METHODS not in the existing list (e.g., ethnography, content analysis, network analysis, etc.)
2. UNIQUE WORKFLOW STEPS or research processes (e.g., data validation, peer review, stakeholder engagement)
3. NOVEL AI APPLICATIONS or use cases (e.g., AI for literature search, hypothesis generation, data visualization)
4. SPECIFIC BARRIERS or challenges (e.g., institutional policies, client expectations, funding constraints)
5. UNIQUE BENEFITS or impacts (e.g., democratization of research, new research questions, methodological innovation)
6. EMERGENT THEMES around research culture, collaboration patterns, or future visions

FOCUS AREAS FOR NEW THEMES:
- Research methodology innovations
- Workflow optimization strategies  
- AI integration patterns
- Organizational dynamics
- Quality assurance processes
- Stakeholder engagement approaches
- Knowledge management practices
- Research dissemination methods

EXISTING CODES (do not repeat these):
{codes_json}

Analyze this speaker turn:
UID: {uid}
Text: {text}

Return a JSON object for each NEW theme you discover:
{{
  "uid": "{uid}",
  "new_code": "DESCRIPTIVE_TAG_NAME",
  "evidence": "exact quote from the text that supports this theme",
  "confidence": 0.75,
  "rationale": "brief explanation of why this is a distinct new theme"
}}

GUIDELINES:
- Tag names should be descriptive and specific (≤ 5 words)
- Only suggest themes that are clearly distinct from existing codes
- Provide exact quotes as evidence
- Suggest up to 4 themes if the content is rich
- Return empty array [] if no new themes emerge

Focus on discovering themes that would be valuable additions to the research methods and AI adoption framework."""


def call_claude_sonnet(prompt: str, temperature: float = 0.7) -> str:
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


def call_gpt4o(prompt: str, temperature: float = 0.7) -> str:
    """Call GPT-4o with retry logic."""
    try:
        response = openai_client.chat.completions.create(
            model=MODEL_GPT,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
            max_tokens=1000
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"GPT-4o error: {e}")
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


def process_single_transcript(transcript_id: str = "RAND_METHODS_ALICE_HUGUET") -> None:
    """Process a single transcript CSV file with Claude and GPT-4o."""
    csv_path = PROC_DIR / f"{transcript_id}_tidy.csv"
    
    if not csv_path.exists():
        print(f"Transcript file not found: {csv_path}")
        return
    
    print(f"\n=== OPTIMIZED SINGLE TRANSCRIPT INDUCTIVE ANALYSIS ===")
    print(f"Processing: {transcript_id}")
    print(f"Discovering themes beyond {len(EXISTING_CODES)} existing codes")
    
    # Read tidy CSV
    df = pd.read_csv(csv_path)
    print(f"Found {len(df)} speaker turns")
    
    # Process with Claude-Sonnet
    print("\nRunning Claude-Sonnet - exploratory...")
    claude_results = []
    for idx, row in df.iterrows():
        uid = row['uid']
        text = row['text']
        
        prompt = create_optimized_inductive_prompt(uid, text)
        response = call_claude_sonnet(prompt, temperature=0.7)
        
        if response:
            parsed = parse_llm_response(response)
            claude_results.extend(parsed)
        
        # Rate limiting
        if (idx + 1) % 10 == 0:
            print(f"  Claude: Processed {idx + 1}/{len(df)} turns")
            time.sleep(0.5)
    
    # Write Claude results
    claude_output = OUTPUT_DIR / f"{transcript_id}_inductive_CLAUDE.jsonl"
    write_jsonl(claude_results, claude_output)
    
    # Process with GPT-4o
    print("\nRunning GPT-4o - exploratory...")
    gpt_results = []
    for idx, row in df.iterrows():
        uid = row['uid']
        text = row['text']
        
        prompt = create_optimized_inductive_prompt(uid, text)
        response = call_gpt4o(prompt, temperature=0.7)
        
        if response:
            parsed = parse_llm_response(response)
            gpt_results.extend(parsed)
        
        # Rate limiting
        if (idx + 1) % 10 == 0:
            print(f"  GPT-4o: Processed {idx + 1}/{len(df)} turns")
            time.sleep(0.5)
    
    # Write GPT results
    gpt_output = OUTPUT_DIR / f"{transcript_id}_inductive_GPT.jsonl"
    write_jsonl(gpt_results, gpt_output)
    
    print(f"\n=== RESULTS ===")
    print(f"Claude suggestions: {len(claude_results)}")
    print(f"GPT-4o suggestions: {len(gpt_results)}")
    
    # Analyze themes
    all_themes = set()
    for item in claude_results + gpt_results:
        if 'new_code' in item:
            all_themes.add(item['new_code'])
    
    print(f"Unique themes discovered: {len(all_themes)}")
    if all_themes:
        print("New themes found:")
        for theme in sorted(all_themes):
            print(f"  - {theme}")
    
    # Find frequent themes (mentioned by both models)
    claude_themes = {item['new_code'] for item in claude_results if 'new_code' in item}
    gpt_themes = {item['new_code'] for item in gpt_results if 'new_code' in item}
    common_themes = claude_themes & gpt_themes
    
    if common_themes:
        print(f"\nThemes found by both models ({len(common_themes)}):")
        for theme in sorted(common_themes):
            print(f"  - {theme}")
    
    print(f"\nResults saved to: {OUTPUT_DIR}")


def main():
    """Main function for single transcript testing."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Single Transcript Inductive Coding')
    parser.add_argument('--transcript', default='RAND_METHODS_ALICE_HUGUET',
                       help='Transcript ID to process')
    
    args = parser.parse_args()
    
    process_single_transcript(args.transcript)


if __name__ == "__main__":
    main() 