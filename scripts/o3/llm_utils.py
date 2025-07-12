"""LLM utility functions for o3 methodology.

Implements the exact API calls and output formats specified by ChatGPT-o3.
"""

import json
import os
import time
from pathlib import Path
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv
import anthropic
import openai
import google.generativeai as genai

load_dotenv()

# Model assignments per o3 spec
MODEL_A = os.getenv("O3_CLAUDE_MODEL", "claude-3-5-sonnet-20241022")  # Claude-Sonnet
MODEL_B = os.getenv("O3_GPT4_MODEL", "gpt-4o")         # GPT-4o
MODEL_C = os.getenv("O3_GEMINI_MODEL", "gemini-1.5-pro")  # Gemini

# Code list from o3 methodology - EXPANDED VERSION
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
gemini_model = genai.GenerativeModel(MODEL_C)


def is_retryable_error(error: Exception) -> bool:
    """Check if error is retryable (rate limit, timeout) vs unresolvable (model not found, auth)."""
    error_str = str(error).lower()
    
    # Unresolvable errors - don't retry
    unresolvable_patterns = [
        'model not found',
        'not_found_error',
        'invalid_request_error',
        'authentication_error',
        'invalid_api_key',
        'model: claude-4-opus',  # Old model name
        'unsupported parameter'
    ]
    
    for pattern in unresolvable_patterns:
        if pattern in error_str:
            return False
    
    # Retryable errors
    retryable_patterns = [
        'rate limit',
        'timeout',
        'server error',
        'internal error',
        'temporary'
    ]
    
    for pattern in retryable_patterns:
        if pattern in error_str:
            return True
    
    return False


def call_with_retry(func, *args, max_retries=3, base_delay=0.0, **kwargs):
    """Call function with retry logic for rate limits, quick fail for unresolvable errors."""
    for attempt in range(max_retries + 1):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            if not is_retryable_error(e):
                print(f"Unresolvable error, not retrying: {e}")
                return None
            
            if attempt < max_retries:
                delay = base_delay  # No exponential backoff, no delay
                print(f"Retryable error (attempt {attempt + 1}/{max_retries + 1}), retrying immediately: {e}")
                if delay > 0:
                    time.sleep(delay)
            else:
                print(f"Max retries exceeded: {e}")
                return None


def call_claude_sonnet(prompt: str, temperature: float = 0.0) -> Optional[str]:
    """Call Claude-Sonnet with retry logic."""
    def _call():
        response = claude_client.messages.create(
            model=MODEL_A,
            max_tokens=4096,
            temperature=temperature,
            messages=[
                {
                    "role": "user", 
                    "content": prompt
                }
            ]
        )
        return response.content[0].text
    
    return call_with_retry(_call)


def call_gpt4o(prompt: str, temperature: float = 0.0) -> Optional[str]:
    """Call GPT-4o with retry logic."""
    def _call():
        response = openai_client.chat.completions.create(
            model=MODEL_B,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )
        return response.choices[0].message.content
    
    return call_with_retry(_call)


def call_gemini(prompt: str, temperature: float = 0.0) -> Optional[str]:
    """Call Gemini with retry logic."""
    def _call():
        response = gemini_model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=temperature,
                max_output_tokens=4096
            )
        )
        return response.text
    
    return call_with_retry(_call)


def create_deductive_prompt(uid: str, text: str) -> str:
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

def create_inductive_prompt(uid: str, text: str) -> str:
    codes_json = json.dumps(DEDUCTIVE_CODES, indent=2)
    return f"""You are an exploratory coder analyzing a transcript from a RAND focus group about research methods and AI. \
The goal is to discover new, meaningful themes related to:
- Research methods and workflow steps
- Pain points and time-consuming steps
- Aspects of research that could benefit from AI
- Barriers and challenges to AI adoption (technical, training, ethical, accessibility)
- Training needs
- Gaps in current AI tools
- Recommendations for new/emerging AI tools

Suggest up to four novel topical tags (up to 5 words each) not found in the code list. For each, quote evidence from the text.

Existing codes (do not repeat these):
{codes_json}

Analyze this speaker turn:
UID: {uid}
Text: {text}

Return a JSON object for each new tag you suggest:
{{
  "uid": "{uid}",
  "new_code": "TAG_NAME",
  "evidence": "exact quote from the text",
  "confidence": 0.82
}}

If no new tags emerge, return an empty array []. Tag names should be ≤ 5 words. Suggest up to 4 tags if the content is rich."""


def parse_llm_response(response: str) -> List[Dict[str, Any]]:
    """Parse LLM response into list of JSON objects."""
    if not response:
        return []
    
    # Clean up response (remove markdown code blocks if present)
    cleaned = response.strip()
    if cleaned.startswith("```json"):
        cleaned = cleaned[7:]
    if cleaned.endswith("```"):
        cleaned = cleaned[:-3]
    cleaned = cleaned.strip()
    
    try:
        # Try parsing as single object
        obj = json.loads(cleaned)
        if isinstance(obj, dict):
            return [obj]
        elif isinstance(obj, list):
            return obj
        else:
            return []
    except json.JSONDecodeError:
        # Try parsing as JSONL (one JSON per line)
        results = []
        for line in cleaned.split('\n'):
            line = line.strip()
            if line:
                try:
                    obj = json.loads(line)
                    results.append(obj)
                except json.JSONDecodeError:
                    continue
        return results


def write_jsonl(data: List[Dict[str, Any]], filepath: Path) -> None:
    """Write list of dicts to JSONL file."""
    filepath.parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        for item in data:
            f.write(json.dumps(item) + '\n')
    print(f"Wrote {len(data)} items to {filepath}")


def create_batch_deductive_prompt(utterances: List[Dict[str, str]]) -> str:
    """Create a batch prompt for multiple utterances."""
    codes_json = json.dumps(DEDUCTIVE_CODES, indent=2)
    utterances_text = "\n".join([f"UID: {u['uid']}\nText: {u['text']}\n" for u in utterances])
    
    return f"""You are an expert qualitative researcher analyzing transcripts.

CODING TASK:
Analyze these speaker turns and identify ALL applicable codes from the predefined list below.

Available codes:
{codes_json}

Analyze these speaker turns:
{utterances_text}

Return a JSON array with one object for each code that applies to each utterance:
[
  {{
    "uid": "utterance_uid",
    "code": "CODE_NAME",
    "prob": 1.0
  }},
  ...
]

If no codes apply to any utterance, return an empty array [].""" 