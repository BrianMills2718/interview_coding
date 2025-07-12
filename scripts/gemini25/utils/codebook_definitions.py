"""
Codebook Definitions for Gemini25 Methodology
Contains the CODEBOOK dictionary with code definitions for qualitative analysis
"""

# CODEBOOK Dictionary - Customize this with your specific codes and definitions
CODEBOOK = {
    "AI_IMPACT": {
        "definition": "Discussions about the impact of AI on research methods and processes",
        "description": "References to how AI affects or could affect research methodology, data analysis, or research outcomes"
    },
    "METHODOLOGY_CONCERNS": {
        "definition": "Expressed concerns or skepticism about AI in research methodology",
        "description": "Worries about reliability, validity, bias, or other methodological issues with AI"
    },
    "ADOPTION_BARRIERS": {
        "definition": "Obstacles or challenges to adopting AI in research",
        "description": "Technical, organizational, ethical, or resource barriers to AI implementation"
    },
    "TRAINING_NEEDS": {
        "definition": "Discussion of training requirements for AI use in research",
        "description": "Skills, knowledge, or education needed to effectively use AI tools"
    },
    "ETHICAL_CONSIDERATIONS": {
        "definition": "Ethical implications and considerations of AI in research",
        "description": "Privacy, bias, transparency, accountability, or other ethical concerns"
    },
    "EFFICIENCY_GAINS": {
        "definition": "Perceived or actual efficiency improvements from AI use",
        "description": "Time savings, productivity increases, or workflow improvements"
    },
    "QUALITY_IMPROVEMENTS": {
        "definition": "Enhancements to research quality through AI",
        "description": "Better accuracy, consistency, or depth in analysis or data processing"
    },
    "COLLABORATION": {
        "definition": "AI's role in facilitating or changing research collaboration",
        "description": "How AI affects teamwork, communication, or interdisciplinary work"
    },
    "FUTURE_VISION": {
        "definition": "Predictions or visions for AI's future role in research",
        "description": "Long-term expectations, possibilities, or scenarios for AI in research"
    },
    "INSTITUTIONAL_FACTORS": {
        "definition": "Organizational or institutional factors affecting AI adoption",
        "description": "Policies, culture, leadership, or structural considerations"
    }
}

# ANALYSIS_START_MARKER - Define where analytical discussion begins in transcripts
ANALYSIS_START_MARKER = "Thinking about curious thinking about high impact work at Rand"

def get_codebook_summary() -> str:
    """
    Generate a formatted summary of the codebook for prompts
    
    Returns:
        Formatted string of codebook codes and definitions
    """
    summary = "CODEBOOK:\n"
    for code, details in CODEBOOK.items():
        summary += f"- {code}: {details['definition']}\n"
    return summary

def validate_codebook() -> bool:
    """
    Validate that the codebook has required structure
    
    Returns:
        True if valid, False otherwise
    """
    for code, details in CODEBOOK.items():
        if not isinstance(details, dict):
            return False
        if 'definition' not in details:
            return False
        if not isinstance(details['definition'], str):
            return False
    return True 