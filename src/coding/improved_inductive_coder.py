"""
Improved Inductive Coder
Emergent coding with theme extraction
"""

import json
import logging
from typing import Dict, List, Optional, Set
from collections import Counter

logger = logging.getLogger(__name__)

class ImprovedInductiveCoder:
    """Inductive coder for emergent theme discovery"""
    
    def __init__(self):
        self.min_theme_occurrences = 2
        self.similarity_threshold = 0.8
        
    def code_transcript(self,
                       transcript: List[Dict],
                       llm_client,
                       existing_codes: Optional[List[str]] = None) -> List[Dict]:
        """
        Apply inductive coding to discover emergent themes
        
        Args:
            transcript: List of utterances
            llm_client: LLM client for coding
            existing_codes: Optional list of codes to consider
            
        Returns:
            List of coding results
        """
        # First pass: Extract initial themes
        initial_themes = self._extract_initial_themes(transcript, llm_client)
        
        # Second pass: Consolidate similar themes
        consolidated_themes = self._consolidate_themes(initial_themes, llm_client)
        
        # Third pass: Apply consolidated themes to transcript
        coding_results = self._apply_themes(
            transcript,
            consolidated_themes,
            llm_client,
            existing_codes
        )
        
        return coding_results
    
    def code_segments(self,
                     segments: List[Dict],
                     llm_client,
                     existing_codes: Optional[List[str]] = None) -> List[Dict]:
        """Code specific segments (for hybrid approach)"""
        return self.code_transcript(segments, llm_client, existing_codes)
    
    def _extract_initial_themes(self,
                              transcript: List[Dict],
                              llm_client) -> List[Dict]:
        """Extract initial themes from transcript"""
        
        # Format transcript
        transcript_text = "\n".join([
            f"[{utt.get('utterance_id')}] {utt.get('speaker')}: {utt.get('text')}"
            for utt in transcript
        ])
        
        prompt = f"""Analyze this transcript and identify emergent themes or patterns.
Focus on recurring topics, concerns, or ideas expressed by participants.

Transcript:
{transcript_text}

For each theme identified:
1. Provide a short descriptive name (2-4 words)
2. Write a clear definition
3. List example quotes that illustrate this theme
4. Note which utterances contain this theme

Return as JSON array:
[
  {{
    "theme_name": "Brief Theme Name",
    "definition": "Clear definition of what this theme represents",
    "examples": ["quote 1", "quote 2"],
    "utterance_ids": ["TEST_0000000", "TEST_0060000"]
  }}
]

Important:
- Focus on themes that appear multiple times
- Be specific rather than overly broad
- Extract themes from actual content, not your assumptions
"""
        
        try:
            response = llm_client.query_model("gpt-4", prompt)
            themes = json.loads(response)
            return themes
        except Exception as e:
            logger.error(f"Failed to extract initial themes: {e}")
            return []
    
    def _consolidate_themes(self,
                          initial_themes: List[Dict],
                          llm_client) -> List[Dict]:
        """Consolidate similar themes"""
        
        if len(initial_themes) <= 5:
            return initial_themes  # No need to consolidate
        
        themes_json = json.dumps(initial_themes, indent=2)
        
        prompt = f"""Review these emergent themes and consolidate similar or overlapping ones.

Themes:
{themes_json}

Consolidate themes that:
1. Address the same underlying concept
2. Have significant overlap in examples
3. Could be merged without losing important nuance

Return consolidated themes as JSON array with same structure.
Aim for 5-15 distinct themes.
"""
        
        try:
            response = llm_client.query_model("gpt-4", prompt)
            consolidated = json.loads(response)
            return consolidated
        except Exception as e:
            logger.error(f"Failed to consolidate themes: {e}")
            return initial_themes
    
    def _apply_themes(self,
                     transcript: List[Dict],
                     themes: List[Dict],
                     llm_client,
                     existing_codes: Optional[List[str]] = None) -> List[Dict]:
        """Apply themes to transcript for final coding"""
        
        # Create theme codebook
        theme_codebook = self._create_theme_codebook(themes)
        
        # Format for coding
        transcript_text = "\n".join([
            f"[{utt.get('utterance_id')}] {utt.get('speaker')}: {utt.get('text')}"
            for utt in transcript
        ])
        
        existing_note = ""
        if existing_codes:
            existing_note = f"""
Also consider these existing codes if relevant:
{json.dumps(existing_codes)}
"""
        
        prompt = f"""Apply these emergent themes to code the transcript.

## Emergent Themes
{json.dumps(theme_codebook, indent=2)}

{existing_note}

## Transcript
{transcript_text}

## Task
Code relevant segments using the emergent themes. For each code:
1. Quote the exact text (minimum 20 characters)
2. Specify the theme name
3. Provide confidence score (0.0-1.0)
4. Explain why this theme applies

Return as JSON array:
[
  {{
    "utterance_id": "TEST_0000000",
    "quote": "exact quote from transcript",
    "code": "EMERGENT::THEME_NAME",
    "confidence": 0.85,
    "reasoning": "brief explanation",
    "theme_definition": "definition of the theme"
  }}
]
"""
        
        try:
            response = llm_client.query_model("gpt-4", prompt)
            results = json.loads(response)
            
            # Validate and clean results
            validated = self._validate_inductive_results(results, transcript, themes)
            return validated
            
        except Exception as e:
            logger.error(f"Failed to apply themes: {e}")
            return []
    
    def _create_theme_codebook(self, themes: List[Dict]) -> Dict:
        """Convert themes to codebook format"""
        codebook = {
            "domain": "emergent",
            "categories": {
                "EMERGENT": {
                    "description": "Themes discovered through inductive analysis",
                    "codes": {}
                }
            }
        }
        
        for theme in themes:
            theme_name = theme.get("theme_name", "").upper().replace(" ", "_")
            codebook["categories"]["EMERGENT"]["codes"][theme_name] = {
                "label": theme.get("theme_name"),
                "definition": theme.get("definition"),
                "examples": theme.get("examples", [])
            }
        
        return codebook
    
    def _validate_inductive_results(self,
                                   results: List[Dict],
                                   transcript: List[Dict],
                                   themes: List[Dict]) -> List[Dict]:
        """Validate inductive coding results"""
        
        validated = []
        utterance_texts = {
            utt.get("utterance_id"): utt.get("text", "")
            for utt in transcript
        }
        
        # Create theme lookup
        valid_themes = {
            theme.get("theme_name", "").upper().replace(" ", "_"): theme
            for theme in themes
        }
        
        for result in results:
            # Validate utterance
            utt_id = result.get("utterance_id")
            if utt_id not in utterance_texts:
                continue
            
            # Validate quote
            quote = result.get("quote", "")
            if len(quote) < 20 or quote not in utterance_texts[utt_id]:
                continue
            
            # Validate theme
            code = result.get("code", "")
            theme_name = code.replace("EMERGENT::", "")
            
            if theme_name not in valid_themes:
                # Try to match partial
                matched = False
                for valid_theme in valid_themes:
                    if valid_theme in theme_name or theme_name in valid_theme:
                        theme_name = valid_theme
                        matched = True
                        break
                
                if not matched:
                    continue
            
            # Add validated result
            validated.append({
                "utterance_id": utt_id,
                "quote": quote,
                "code": f"EMERGENT::{theme_name}",
                "confidence": result.get("confidence", 0.7),
                "reasoning": result.get("reasoning", ""),
                "theme_definition": valid_themes[theme_name].get("definition", ""),
                "inductive": True
            })
        
        return validated
    
    def generate_theme_summary(self, themes: List[Dict]) -> str:
        """Generate summary of discovered themes"""
        
        summary = []
        summary.append("## Discovered Themes\n")
        
        for i, theme in enumerate(themes, 1):
            summary.append(f"### {i}. {theme.get('theme_name', 'Unnamed Theme')}")
            summary.append(f"**Definition**: {theme.get('definition', 'No definition provided')}")
            
            examples = theme.get('examples', [])
            if examples:
                summary.append("**Examples**:")
                for example in examples[:3]:
                    summary.append(f'- "{example}"')
            
            summary.append("")
        
        return "\n".join(summary)