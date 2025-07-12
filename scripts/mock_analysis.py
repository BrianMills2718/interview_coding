#!/usr/bin/env python3
"""
Mock Analysis Runner for Demonstrating the Pipeline
This creates sample outputs for all four methodologies without requiring API keys
"""

import json
import csv
from pathlib import Path
from datetime import datetime
import random

def create_mock_o3_outputs():
    """Create mock outputs for o3 methodology"""
    output_dir = Path("data/analysis_outputs/o3")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Mock deductive coding results
    deductive_results = {
        "transcript_id": "test_transcript",
        "timestamp": datetime.now().isoformat(),
        "codes": {
            "collaboration_effectiveness": 0.85,
            "user_satisfaction": 0.72,
            "interface_usability": 0.78,
            "feature_requests": ["better_mobile", "improved_notifications", "workflow_customization"]
        },
        "key_quotes": [
            "The real-time editing is fantastic",
            "The commenting system could be improved",
            "Integration with our existing tools has been seamless"
        ]
    }
    
    with open(output_dir / "deductive_results.json", "w") as f:
        json.dump(deductive_results, f, indent=2)
    
    # Mock inductive coding results
    inductive_results = {
        "transcript_id": "test_transcript",
        "timestamp": datetime.now().isoformat(),
        "emergent_themes": [
            {"theme": "learning_curve", "prevalence": 0.45},
            {"theme": "notification_issues", "prevalence": 0.67},
            {"theme": "mobile_experience", "prevalence": 0.58}
        ],
        "reliability_score": 0.82
    }
    
    with open(output_dir / "inductive_results.json", "w") as f:
        json.dump(inductive_results, f, indent=2)
    
    print("✓ Created o3 methodology outputs")

def create_mock_opus_outputs():
    """Create mock outputs for Opus methodology"""
    output_dir = Path("data/analysis_outputs/opus")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Mock formal coding results
    opus_results = {
        "transcript_id": "test_transcript",
        "timestamp": datetime.now().isoformat(),
        "multi_llm_analysis": {
            "claude": {
                "primary_codes": ["usability", "collaboration", "integration"],
                "confidence": 0.88
            },
            "gpt4": {
                "primary_codes": ["usability", "notifications", "mobile"],
                "confidence": 0.85
            },
            "gemini": {
                "primary_codes": ["collaboration", "customization", "integration"],
                "confidence": 0.83
            }
        },
        "consensus_codes": ["usability", "collaboration", "integration"],
        "inter_coder_agreement": 0.79
    }
    
    with open(output_dir / "opus_analysis.json", "w") as f:
        json.dump(opus_results, f, indent=2)
    
    # Create narrative report
    with open(output_dir / "narrative_report.md", "w") as f:
        f.write("# Opus Methodology Analysis Report\n\n")
        f.write("## Executive Summary\n")
        f.write("The focus group revealed strong positive feedback about collaboration features ")
        f.write("while identifying areas for improvement in notifications and mobile experience.\n\n")
        f.write("## Key Findings\n")
        f.write("- High satisfaction with real-time collaboration\n")
        f.write("- Notification system needs refinement\n")
        f.write("- Mobile experience requires enhancement\n")
    
    print("✓ Created Opus methodology outputs")

def create_mock_sonnet_outputs():
    """Create mock outputs for Sonnet methodology"""
    output_dir = Path("data/analysis_outputs/sonnet")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Mock TAM/DOI analysis
    sonnet_results = {
        "transcript_id": "test_transcript",
        "timestamp": datetime.now().isoformat(),
        "tam_analysis": {
            "perceived_usefulness": 0.82,
            "perceived_ease_of_use": 0.75,
            "behavioral_intention": 0.79
        },
        "doi_analysis": {
            "relative_advantage": 0.85,
            "compatibility": 0.88,
            "complexity": 0.32,  # Lower is better
            "trialability": 0.76,
            "observability": 0.81
        },
        "consensus_themes": [
            "strong_collaboration_features",
            "notification_improvements_needed",
            "mobile_enhancement_priority"
        ]
    }
    
    with open(output_dir / "sonnet_consensus.json", "w") as f:
        json.dump(sonnet_results, f, indent=2)
    
    # Create cross-transcript comparison
    comparison = {
        "transcripts_analyzed": ["test_transcript"],
        "common_themes": ["collaboration", "notifications", "mobile"],
        "theme_prevalence": {
            "collaboration": 0.85,
            "notifications": 0.67,
            "mobile": 0.58
        }
    }
    
    with open(output_dir / "cross_transcript_analysis.json", "w") as f:
        json.dump(comparison, f, indent=2)
    
    print("✓ Created Sonnet methodology outputs")

def create_mock_gemini_outputs():
    """Create mock outputs for Gemini methodology"""
    output_dir = Path("data/analysis_outputs/gemini")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Mock Gemini analysis
    gemini_results = {
        "transcript_id": "test_transcript",
        "timestamp": datetime.now().isoformat(),
        "coded_segments": [
            {
                "text": "The real-time editing is fantastic",
                "codes": ["positive_feedback", "collaboration_feature"],
                "confidence": 0.92
            },
            {
                "text": "The commenting system could be improved",
                "codes": ["improvement_needed", "notification_system"],
                "confidence": 0.88
            }
        ],
        "reliability_metrics": {
            "internal_consistency": 0.84,
            "code_frequency": {
                "positive_feedback": 6,
                "improvement_needed": 4,
                "feature_request": 3
            }
        }
    }
    
    with open(output_dir / "gemini_batch_results.json", "w") as f:
        json.dump(gemini_results, f, indent=2)
    
    # Create CSV output
    with open(output_dir / "gemini_results.csv", "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["segment", "codes", "confidence"])
        for segment in gemini_results["coded_segments"]:
            writer.writerow([
                segment["text"],
                "|".join(segment["codes"]),
                segment["confidence"]
            ])
    
    print("✓ Created Gemini methodology outputs")

def create_comparative_analysis():
    """Create comparative analysis across all methodologies"""
    comparative = {
        "analysis_timestamp": datetime.now().isoformat(),
        "methodologies_completed": ["o3", "opus", "sonnet", "gemini"],
        "common_findings": {
            "positive_aspects": ["collaboration_features", "integration"],
            "improvement_areas": ["notifications", "mobile_experience"],
            "consensus_level": 0.81
        },
        "methodology_comparison": {
            "o3": {"reliability": 0.82, "themes_identified": 6},
            "opus": {"reliability": 0.79, "themes_identified": 5},
            "sonnet": {"reliability": 0.85, "themes_identified": 7},
            "gemini": {"reliability": 0.84, "themes_identified": 5}
        }
    }
    
    with open("comparative_analysis.json", "w") as f:
        json.dump(comparative, f, indent=2)
    
    print("✓ Created comparative analysis")

def main():
    print("\n=== Mock Analysis Pipeline ===\n")
    print("Creating sample outputs for all methodologies...\n")
    
    create_mock_o3_outputs()
    create_mock_opus_outputs()
    create_mock_sonnet_outputs()
    create_mock_gemini_outputs()
    create_comparative_analysis()
    
    print("\n✓ Mock analysis complete!")
    print("\nOutputs created in:")
    print("  - data/analysis_outputs/o3/")
    print("  - data/analysis_outputs/opus/")
    print("  - data/analysis_outputs/sonnet/")
    print("  - data/analysis_outputs/gemini/")
    print("  - comparative_analysis.json")

if __name__ == "__main__":
    main()