"""
Domain Detection System
Analyzes transcripts to determine appropriate coding domain
"""

import re
import json
import logging
from typing import Dict, List, Tuple, Optional
from pathlib import Path
from collections import Counter
import numpy as np

logger = logging.getLogger(__name__)

class DomainDetector:
    """Detects the domain of a transcript and suggests appropriate codebooks"""
    
    def __init__(self, profiles_path: str = "config/domain_profiles.json"):
        """Initialize with domain profiles"""
        self.profiles = self._load_domain_profiles(profiles_path)
        self.min_confidence = 0.7  # Minimum confidence to assign domain
        
    def _load_domain_profiles(self, profiles_path: str) -> Dict:
        """Load domain profiles from JSON config"""
        path = Path(profiles_path)
        if path.exists():
            with open(path, 'r') as f:
                return json.load(f)
        else:
            # Default profiles if config doesn't exist
            return {
                "ai_research": {
                    "keywords": ["AI", "artificial intelligence", "machine learning", "automation", 
                                "algorithm", "neural network", "deep learning", "NLP", "computer vision",
                                "RAND", "research method", "qualitative analysis"],
                    "patterns": [r"AI\s+adoption", r"machine\s+learning", r"automat\w+", r"research\s+method"],
                    "weight": 1.0,
                    "codebook": "config/codebooks/ai_research_codes.json"
                },
                "product_feedback": {
                    "keywords": ["interface", "feature", "user experience", "UX", "UI", "bug", 
                                "navigation", "usability", "design", "workflow", "integration",
                                "notification", "mobile", "desktop", "performance"],
                    "patterns": [r"user\s+experience", r"UI/UX", r"bug\s+report", r"feature\s+request"],
                    "weight": 1.0,
                    "codebook": "config/codebooks/product_feedback_codes.json"
                },
                "medical": {
                    "keywords": ["patient", "treatment", "diagnosis", "symptom", "medication",
                                "clinical", "therapy", "healthcare", "doctor", "nurse", "hospital"],
                    "patterns": [r"patient\s+care", r"clinical\s+trial", r"medical\s+record"],
                    "weight": 1.0,
                    "codebook": "config/codebooks/medical_codes.json"
                },
                "education": {
                    "keywords": ["student", "teacher", "learning", "curriculum", "assessment",
                                "classroom", "education", "pedagogy", "course", "lesson"],
                    "patterns": [r"student\s+learning", r"educational\s+outcome", r"teaching\s+method"],
                    "weight": 1.0,
                    "codebook": "config/codebooks/education_codes.json"
                },
                "customer_service": {
                    "keywords": ["customer", "service", "support", "complaint", "satisfaction",
                                "resolution", "ticket", "agent", "response time", "issue"],
                    "patterns": [r"customer\s+service", r"support\s+ticket", r"customer\s+satisfaction"],
                    "weight": 1.0,
                    "codebook": "config/codebooks/customer_service_codes.json"
                }
            }
    
    def analyze_transcript(self, transcript: str) -> Dict[str, any]:
        """
        Analyze transcript and determine most likely domain
        
        Returns:
            {
                "detected_domain": str,
                "confidence": float,
                "domain_scores": Dict[str, float],
                "recommended_codebook": str,
                "fallback_strategy": str
            }
        """
        # Preprocess text
        text_lower = transcript.lower()
        words = re.findall(r'\b\w+\b', text_lower)
        word_freq = Counter(words)
        
        # Score each domain
        domain_scores = {}
        for domain, profile in self.profiles.items():
            score = self._calculate_domain_score(text_lower, word_freq, profile)
            domain_scores[domain] = score
        
        # Find best match
        best_domain = max(domain_scores, key=domain_scores.get)
        best_score = domain_scores[best_domain]
        
        # Normalize scores to get confidence
        total_score = sum(domain_scores.values())
        confidence = best_score / total_score if total_score > 0 else 0
        
        # Determine strategy
        if confidence >= self.min_confidence:
            strategy = "deductive"
            recommended_codebook = self.profiles[best_domain]["codebook"]
        else:
            strategy = "emergent"
            recommended_codebook = None
            best_domain = "unknown"
        
        return {
            "detected_domain": best_domain,
            "confidence": confidence,
            "domain_scores": domain_scores,
            "recommended_codebook": recommended_codebook,
            "fallback_strategy": strategy,
            "top_keywords": self._get_top_keywords(word_freq, best_domain)
        }
    
    def _calculate_domain_score(self, text: str, word_freq: Counter, profile: Dict) -> float:
        """Calculate score for a specific domain"""
        score = 0.0
        
        # Keyword matching
        for keyword in profile["keywords"]:
            if keyword in text:
                # Weight by frequency
                count = text.count(keyword)
                score += count * profile["weight"]
        
        # Pattern matching
        for pattern in profile["patterns"]:
            matches = re.findall(pattern, text, re.IGNORECASE)
            score += len(matches) * profile["weight"] * 2  # Patterns weighted higher
        
        return score
    
    def _get_top_keywords(self, word_freq: Counter, domain: str) -> List[str]:
        """Get top keywords found for the domain"""
        if domain == "unknown":
            # Return most common words for emergent coding
            return [word for word, _ in word_freq.most_common(10)]
        
        profile = self.profiles.get(domain, {})
        found_keywords = []
        
        for keyword in profile.get("keywords", []):
            if keyword.lower() in word_freq:
                found_keywords.append(keyword)
        
        return found_keywords[:10]
    
    def suggest_codes_for_unknown(self, transcript: str) -> Dict[str, any]:
        """Suggest emergent codes for unknown domain"""
        # Extract key themes using simple NLP
        sentences = re.split(r'[.!?]', transcript)
        
        # Find recurring topics
        topics = []
        for sentence in sentences:
            # Extract noun phrases (simplified)
            words = re.findall(r'\b\w+\b', sentence.lower())
            if len(words) > 3:
                # Look for repeated phrases
                for i in range(len(words) - 2):
                    phrase = " ".join(words[i:i+3])
                    if transcript.lower().count(phrase) > 1:
                        topics.append(phrase)
        
        # Count and rank topics
        topic_counts = Counter(topics)
        
        return {
            "suggested_themes": [topic for topic, _ in topic_counts.most_common(10)],
            "coding_approach": "emergent",
            "instructions": "Use these themes as starting points for inductive coding"
        }


class DomainValidator:
    """Validates that coding results match the detected domain"""
    
    def __init__(self):
        self.warning_threshold = 0.3  # Warn if >30% codes don't match domain
        
    def validate_coding_results(self, 
                              coding_results: List[Dict],
                              detected_domain: str,
                              domain_confidence: float) -> Dict[str, any]:
        """Validate that coding results align with detected domain"""
        
        if not coding_results:
            return {
                "valid": False,
                "warnings": ["No coding results to validate"],
                "recommendations": ["Consider using emergent coding approach"]
            }
        
        # Check for suspicious patterns
        warnings = []
        
        # Check for 100% or 0% coding
        if all(result.get("confidence", 0) == 1.0 for result in coding_results):
            warnings.append("All codes have 100% confidence - possible overfitting")
        
        if all(result.get("confidence", 0) == 0.0 for result in coding_results):
            warnings.append("All codes have 0% confidence - domain mismatch likely")
        
        # Check domain alignment
        if detected_domain == "unknown" and len(coding_results) > 0:
            warnings.append("Unknown domain but codes were applied - verify appropriateness")
        
        # Check coverage
        total_utterances = max(result.get("utterance_id", 0) for result in coding_results) + 1
        coded_utterances = len(set(result.get("utterance_id") for result in coding_results))
        coverage = coded_utterances / total_utterances if total_utterances > 0 else 0
        
        if coverage < 0.1:
            warnings.append(f"Low coverage: only {coverage:.1%} of utterances coded")
        
        return {
            "valid": len(warnings) == 0,
            "warnings": warnings,
            "coverage": coverage,
            "domain_confidence": domain_confidence,
            "recommendations": self._generate_recommendations(warnings, coverage)
        }
    
    def _generate_recommendations(self, warnings: List[str], coverage: float) -> List[str]:
        """Generate recommendations based on validation results"""
        recommendations = []
        
        if coverage < 0.5:
            recommendations.append("Consider using emergent coding for better coverage")
        
        if "domain mismatch" in " ".join(warnings).lower():
            recommendations.append("Re-run with domain-appropriate codebook")
        
        if "100% confidence" in " ".join(warnings):
            recommendations.append("Review codes for over-generalization")
        
        return recommendations