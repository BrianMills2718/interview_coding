"""Formal coding schema for Opus methodology.

Defines the coding categories and codes used in the enhanced analyzer.
"""

from typing import Dict, List, Any
from dataclasses import dataclass
import json
from pathlib import Path


@dataclass
class CodeDefinition:
    """Definition of a single code."""
    code_id: str
    label: str
    category: str
    description: str
    inclusion_criteria: str
    exclusion_criteria: str
    examples: List[str]


class Codebook:
    """Formal coding schema with categories and codes."""
    
    def __init__(self):
        self.categories = {
            "research_methods": {
                "name": "Research Methods",
                "description": "Methods and approaches used in research projects"
            },
            "pain_points": {
                "name": "Pain Points", 
                "description": "Challenges and difficulties in current research processes"
            },
            "ai_opportunities": {
                "name": "AI Opportunities",
                "description": "Potential applications of AI to enhance research"
            }
        }
        
        # Initialize with placeholder codes - these can be customized
        self.codes = [
            CodeDefinition(
                code_id="RM001",
                label="Qualitative Interviews",
                category="research_methods",
                description="Any mention of conducting interviews, focus groups, or qualitative data collection with human subjects",
                inclusion_criteria="Direct references to interviewing, focus groups, or qualitative data collection",
                exclusion_criteria="Mention of interviews without actually conducting them",
                examples=["most projects I've done probably have had subject matter expert interviews"]
            ),
            CodeDefinition(
                code_id="RM002", 
                label="Quantitative Analysis",
                category="research_methods",
                description="Statistical analysis, modeling, or numerical data processing",
                inclusion_criteria="References to statistical analysis, modeling, or numerical processing",
                exclusion_criteria="General mentions of data without specific analysis",
                examples=["I'm a optimizer. I do a lot of modeling, simulation coding"]
            ),
            CodeDefinition(
                code_id="PP001",
                label="Time-Consuming Processes", 
                category="pain_points",
                description="Specific mentions of tasks that take excessive time",
                inclusion_criteria="Direct complaints about time-consuming tasks or processes",
                exclusion_criteria="General statements about time without specific tasks",
                examples=["Just to get our survey to OMB took over a year"]
            ),
            CodeDefinition(
                code_id="PP002",
                label="Protocol Development",
                category="pain_points", 
                description="Challenges in designing research instruments or protocols",
                inclusion_criteria="Specific difficulties in designing research instruments",
                exclusion_criteria="General research challenges not related to protocols",
                examples=["the hardest is to find the right questions"]
            ),
            CodeDefinition(
                code_id="AI001",
                label="Automated Coding/Analysis",
                category="ai_opportunities",
                description="Using AI for qualitative or quantitative data analysis",
                inclusion_criteria="Specific mentions of AI for data analysis or coding",
                exclusion_criteria="General AI mentions without analysis context",
                examples=["if you could have AI go through the interviews as the first step"]
            ),
            CodeDefinition(
                code_id="AI002",
                label="Project Management Support",
                category="ai_opportunities",
                description="AI assistance with planning, scheduling, or coordination",
                inclusion_criteria="AI for project management, planning, or coordination",
                exclusion_criteria="General AI mentions without management context",
                examples=["figuring out what are the critical paths"]
            )
        ]
    
    def get_codes_by_category(self, category: str) -> List[CodeDefinition]:
        """Get all codes for a specific category."""
        return [code for code in self.codes if code.category == category]
    
    def get_code_by_id(self, code_id: str) -> CodeDefinition:
        """Get a specific code by its ID."""
        for code in self.codes:
            if code.code_id == code_id:
                return code
        return None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert codebook to dictionary for JSON serialization."""
        return {
            "categories": self.categories,
            "codes": [
                {
                    "code_id": code.code_id,
                    "label": code.label,
                    "category": code.category,
                    "description": code.description,
                    "inclusion_criteria": code.inclusion_criteria,
                    "exclusion_criteria": code.exclusion_criteria,
                    "examples": code.examples
                }
                for code in self.codes
            ]
        }
    
    def save(self, filepath: Path) -> None:
        """Save codebook to JSON file."""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=2)
    
    @classmethod
    def load(cls, filepath: Path) -> 'Codebook':
        """Load codebook from JSON file."""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        codebook = cls()
        codebook.categories = data.get('categories', {})
        
        codes = []
        for code_data in data.get('codes', []):
            code = CodeDefinition(
                code_id=code_data['code_id'],
                label=code_data['label'],
                category=code_data['category'],
                description=code_data['description'],
                inclusion_criteria=code_data['inclusion_criteria'],
                exclusion_criteria=code_data['exclusion_criteria'],
                examples=code_data['examples']
            )
            codes.append(code)
        
        codebook.codes = codes
        return codebook


def create_coding_prompt(codebook: Codebook) -> str:
    """Create the coding prompt for LLMs."""
    prompt = """You are an expert qualitative researcher conducting a rigorous analysis of focus group transcripts about AI adoption in research organizations.

TASK: Code this transcript according to the provided codebook. For each code that applies:

1. Extract the exact quote that supports the code
2. Identify the speaker who made the statement
3. Provide confidence in your coding (0-1 scale)

CODEBOOK:
"""
    
    # Add categories and codes
    for category_id, category_info in codebook.categories.items():
        prompt += f"\n## {category_info['name']}\n"
        prompt += f"{category_info['description']}\n\n"
        
        codes = codebook.get_codes_by_category(category_id)
        for code in codes:
            prompt += f"**{code.code_id}: {code.label}**\n"
            prompt += f"Description: {code.description}\n"
            prompt += f"Inclusion: {code.inclusion_criteria}\n"
            prompt += f"Exclusion: {code.exclusion_criteria}\n"
            if code.examples:
                prompt += f"Examples: {', '.join(code.examples)}\n"
            prompt += "\n"
    
    prompt += """
OUTPUT FORMAT: Return valid JSON with this structure:
{
  "codes_found": {
    "CODE_ID": [
      {
        "label": "Code Label",
        "quote": "exact quote from transcript",
        "speaker": "Speaker Name",
        "confidence": 0.95
      }
    ]
  }
}

Only include codes that are clearly present in the transcript. If no codes apply, return an empty "codes_found" object.

TRANSCRIPT TO CODE:
"""
    
    return prompt 