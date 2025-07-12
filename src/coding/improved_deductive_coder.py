"""
Improved Deductive Coder
Domain-aware deductive coding with validation
"""

import json
import logging
from typing import Dict, List, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

class ImprovedDeductiveCoder:
    """Deductive coder with domain awareness and validation"""
    
    def __init__(self):
        self.confidence_penalty_wrong_domain = 0.3
        self.min_quote_length = 20
        
    def code_transcript(self,
                       transcript: List[Dict],
                       codebook_path: str,
                       llm_client,
                       domain_confidence: float = 1.0) -> List[Dict]:
        """
        Apply deductive coding with domain awareness
        
        Args:
            transcript: List of utterances
            codebook_path: Path to domain-specific codebook
            llm_client: LLM client for coding
            domain_confidence: Confidence in domain match
            
        Returns:
            List of coding results
        """
        if not codebook_path or not Path(codebook_path).exists():
            logger.warning(f"Codebook not found: {codebook_path}")
            return []
        
        # Load codebook
        with open(codebook_path, 'r') as f:
            codebook = json.load(f)
        
        # Build coding prompt with domain awareness
        prompt = self._build_coding_prompt(transcript, codebook, domain_confidence)
        
        # Get coding from LLM
        try:
            response = llm_client.query_model("gpt-4", prompt)
            raw_results = json.loads(response)
        except Exception as e:
            logger.error(f"Failed to get deductive coding: {e}")
            return []
        
        # Process and validate results
        validated_results = self._validate_results(
            raw_results,
            transcript,
            codebook,
            domain_confidence
        )
        
        return validated_results
    
    def _build_coding_prompt(self,
                           transcript: List[Dict],
                           codebook: Dict,
                           domain_confidence: float) -> str:
        """Build domain-aware coding prompt"""
        
        # Extract codebook details
        domain = codebook.get("domain", "general")
        instructions = codebook.get("coding_instructions", "")
        
        # Format codes
        codes_text = self._format_codebook(codebook)
        
        # Format transcript
        transcript_text = self._format_transcript(transcript)
        
        # Build prompt with domain awareness
        if domain_confidence < 0.8:
            confidence_note = f"""
Note: Domain confidence is {domain_confidence:.2f}. 
Only apply codes when there is clear evidence in the text.
Express uncertainty in confidence scores when domain match is unclear.
"""
        else:
            confidence_note = ""
        
        prompt = f"""You are an expert qualitative researcher performing deductive coding.

Domain: {domain}
{confidence_note}

## Codebook
{codes_text}

## Coding Instructions
{instructions}

## Transcript
{transcript_text}

## Task
Code each utterance using the provided codebook. For each code applied:
1. Quote the exact text being coded (minimum 20 characters)
2. Specify the code category and code name
3. Provide confidence score (0.0-1.0)
4. Explain why this code applies

Return results as JSON array:
[
  {{
    "utterance_id": "TEST_0000000",
    "quote": "exact quote from transcript",
    "code": "CATEGORY::CODE_NAME",
    "confidence": 0.85,
    "reasoning": "brief explanation"
  }}
]

Important:
- Only code content that clearly matches code definitions
- If domain seems mismatched, use lower confidence scores
- Skip utterances with no applicable codes
- Ensure quotes are verbatim from transcript
"""
        
        return prompt
    
    def _format_codebook(self, codebook: Dict) -> str:
        """Format codebook for prompt"""
        lines = []
        
        for category_name, category in codebook.get("categories", {}).items():
            lines.append(f"\n### {category_name}: {category.get('description', '')}")
            
            for code_name, code_info in category.get("codes", {}).items():
                lines.append(f"\n**{code_name}**")
                lines.append(f"- Label: {code_info.get('label', code_name)}")
                lines.append(f"- Description: {code_info.get('description', '')}")
                
                examples = code_info.get("examples", [])
                if examples:
                    lines.append(f"- Examples: {', '.join(examples[:3])}")
        
        return "\n".join(lines)
    
    def _format_transcript(self, transcript: List[Dict]) -> str:
        """Format transcript for prompt"""
        lines = []
        
        for utt in transcript:
            utt_id = utt.get("utterance_id", "")
            speaker = utt.get("speaker", "Unknown")
            text = utt.get("text", "")
            
            lines.append(f"[{utt_id}] {speaker}: {text}")
        
        return "\n".join(lines)
    
    def _validate_results(self,
                         raw_results: List[Dict],
                         transcript: List[Dict],
                         codebook: Dict,
                         domain_confidence: float) -> List[Dict]:
        """Validate and clean coding results"""
        
        validated = []
        utterance_texts = {
            utt.get("utterance_id"): utt.get("text", "")
            for utt in transcript
        }
        
        # Get valid codes from codebook
        valid_codes = set()
        for category in codebook.get("categories", {}).values():
            for code_name in category.get("codes", {}).keys():
                valid_codes.add(f"{category}::{code_name}")
                valid_codes.add(code_name)  # Allow without category prefix
        
        for result in raw_results:
            # Validate utterance ID
            utt_id = result.get("utterance_id")
            if utt_id not in utterance_texts:
                logger.warning(f"Invalid utterance ID: {utt_id}")
                continue
            
            # Validate quote
            quote = result.get("quote", "")
            if len(quote) < self.min_quote_length:
                logger.warning(f"Quote too short: {quote}")
                continue
            
            # Check quote exists in utterance
            if quote not in utterance_texts[utt_id]:
                logger.warning(f"Quote not found in utterance: {quote}")
                continue
            
            # Validate code
            code = result.get("code", "")
            if not any(valid in code for valid in valid_codes):
                logger.warning(f"Invalid code: {code}")
                continue
            
            # Adjust confidence based on domain match
            confidence = result.get("confidence", 0.5)
            if domain_confidence < 0.8:
                confidence *= (0.7 + 0.3 * domain_confidence)
            
            # Add validated result
            validated.append({
                "utterance_id": utt_id,
                "quote": quote,
                "code": code,
                "confidence": min(1.0, confidence),
                "reasoning": result.get("reasoning", ""),
                "domain_adjusted": domain_confidence < 0.8
            })
        
        return validated