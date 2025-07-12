# CLAUDE.md

This file provides implementation instructions for Claude Code (claude.ai/code) to execute the qualitative analysis pipeline.

## Quick Start

```bash
# 1. Setup environment
python3 -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate
pip install -r requirements.txt

# 2. Configure API keys in .env
ANTHROPIC_API_KEY=your_key
OPENAI_API_KEY=your_key
GOOGLE_API_KEY=your_key

# 3. Prepare transcripts
# Place .docx files in data/raw/, then:
python scripts/o3/batch_clean.py

# 4. Run unified pipeline (RECOMMENDED)
python test_unified_pipeline.py

# 5. Or run all original methodologies
python scripts/run_all_methodologies.py
```

## Primary Implementation: Unified Pipeline

The unified pipeline integrates domain detection, validation, and adaptive reporting:

```bash
# Single transcript analysis
python -m src.pipeline.unified_pipeline data/processed/your_transcript.txt

# Batch analysis
python -m src.pipeline.unified_pipeline --batch data/processed/

# Force specific domain
python -m src.pipeline.unified_pipeline --domain product_feedback transcript.txt
```

### Key Features
- **Domain Detection**: Automatically identifies transcript domain (AI research, product feedback, medical, etc.)
- **Hybrid Coding**: Combines deductive/inductive based on domain confidence
- **Coverage Metrics**: Reports what percentage was coded and why
- **Output Validation**: Checks for impossible results
- **Adaptive Reports**: No hallucinated findings

## Individual Methodologies (Legacy)

### O3 Methodology
```bash
# Run with improvements
python scripts/o3/improved_o3_wrapper.py --transcript data/processed/test_transcript.txt

# Or original version
python scripts/o3/deductive_runner.py
python scripts/o3/inductive_runner.py
```

### Opus Methodology
```bash
cd scripts/opus && python enhanced_analyzer.py
```

### Sonnet Methodology
```bash
python scripts/sonnet/run_sonnet_analysis.py
```

### Gemini Methodology
```bash
python scripts/gemini25/main.py
```

## Domain-Specific Analysis

### 1. Product Feedback
```bash
# Codebook: config/codebooks/product_feedback_codes.json
python -m src.pipeline.unified_pipeline --domain product_feedback transcript.txt
```

### 2. AI Research
```bash
# Codebook: config/codebooks/ai_research_codes.json
python -m src.pipeline.unified_pipeline --domain ai_research transcript.txt
```

### 3. Unknown Domain (Emergent Coding)
```bash
# Let system detect and use emergent coding
python -m src.pipeline.unified_pipeline transcript.txt
```

## Adding New Domains

1. Create codebook in `config/codebooks/your_domain_codes.json`:
```json
{
  "name": "Your Domain Codebook",
  "domain": "your_domain",
  "categories": {
    "CATEGORY_NAME": {
      "description": "Category description",
      "codes": {
        "CODE_NAME": {
          "label": "Human-readable label",
          "description": "When to apply this code",
          "examples": ["example 1", "example 2"]
        }
      }
    }
  }
}
```

2. Add domain profile to `src/domain/domain_detector.py`:
```python
"your_domain": {
    "keywords": ["domain", "specific", "terms"],
    "patterns": [r"domain\s+pattern"],
    "codebook": "your_domain_codes.json"
}
```

## Output Structure

```
outputs/unified/
├── transcript_name_coding_TIMESTAMP.json    # All coding results
├── transcript_name_domain_TIMESTAMP.json    # Domain detection info
├── transcript_name_coverage_TIMESTAMP.json  # Coverage metrics
├── transcript_name_validation_TIMESTAMP.json # Validation results
└── transcript_name_report_TIMESTAMP.md      # Human-readable report
```

## Validation Checks

The pipeline automatically validates:
- ✓ Coverage > 10% (warns if low)
- ✓ No 100% identical codes
- ✓ Domain alignment
- ✓ Statistical validity
- ✓ Output consistency

## Troubleshooting

### No codes found
- Check domain detection: Is the detected domain correct?
- Try forcing correct domain: `--domain your_domain`
- Use emergent coding for unknown content

### Low coverage warnings
- Review uncoded segments in coverage report
- Consider if codebook matches content
- May need domain-specific codebook

### Validation failures
- Check validation report for specific issues
- Review recommendations provided
- May indicate fundamental mismatch

## Testing

```bash
# Test unified pipeline
python test_unified_pipeline.py

# Test specific components
python -m pytest tests/test_domain_detector.py
python -m pytest tests/test_coverage_analyzer.py
python -m pytest tests/test_output_validator.py
```

## Background Execution

For long transcripts, run in background:
```bash
nohup python -m src.pipeline.unified_pipeline --batch data/processed/ > analysis.log 2>&1 &
tail -f analysis.log  # Monitor progress
```

## Key Improvements Over Original

1. **Domain Awareness**: No more forcing AI research analysis on product feedback
2. **Coverage Visibility**: Know exactly what wasn't coded and why
3. **No Hallucination**: Reports only what's actually in the transcript
4. **Validation**: Automatic quality checks
5. **Flexibility**: Easy to add new domains

## Model Configuration

Current supported models (update in .env as needed):
- Claude: claude-sonnet-4-20250514
- OpenAI: o3
- Gemini: gemini-2.5-pro

## Next Steps

1. Run unified pipeline on your transcripts
2. Review coverage and validation reports
3. Add domain-specific codebooks as needed
4. Iterate based on results