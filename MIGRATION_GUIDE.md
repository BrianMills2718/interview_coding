# Migration Guide: Integrating Improvements into Existing Methodologies

## Overview

This guide explains how to integrate the new domain detection, validation, and reporting improvements into the existing O3, Opus, Sonnet, and Gemini methodologies.

## Core Components to Integrate

1. **Domain Detection** - Identify appropriate analysis domain
2. **Coverage Metrics** - Track and report coding coverage
3. **Output Validation** - Validate results for sanity
4. **Adaptive Reporting** - Generate context-aware reports
5. **Hybrid Coding** - Combine approaches based on confidence

## Integration Patterns

### Pattern 1: Wrapper Approach (Recommended)

Create a wrapper around existing methodology that adds improvements:

```python
from src.domain.domain_detector import DomainDetector
from src.metrics.coverage_analyzer import CoverageAnalyzer
from src.validation.output_validator import OutputValidator
from src.reporting.adaptive_report_generator import AdaptiveReportGenerator

class ImprovedMethodologyWrapper:
    def __init__(self):
        self.domain_detector = DomainDetector()
        self.coverage_analyzer = CoverageAnalyzer()
        self.output_validator = OutputValidator()
        self.report_generator = AdaptiveReportGenerator()
        self.original_methodology = OriginalMethodology()
    
    def analyze(self, transcript_path):
        # 1. Load transcript
        transcript = self.load_transcript(transcript_path)
        
        # 2. Detect domain
        domain_info = self.domain_detector.analyze_transcript(
            " ".join(utt["text"] for utt in transcript)
        )
        
        # 3. Run original methodology
        results = self.original_methodology.analyze(transcript_path)
        
        # 4. Analyze coverage
        coverage = self.coverage_analyzer.analyze_coverage(
            transcript, results, domain_info["confidence"]
        )
        
        # 5. Validate
        validation = self.output_validator.validate_results(
            results, transcript, domain_info
        )
        
        # 6. Generate report
        report = self.report_generator.generate_report(
            results, domain_info, coverage, validation,
            {"name": Path(transcript_path).stem}
        )
        
        return {
            "results": results,
            "domain": domain_info,
            "coverage": coverage,
            "validation": validation,
            "report": report
        }
```

### Pattern 2: Direct Integration

Modify existing methodology code directly:

```python
# In existing methodology file
from src.domain.domain_detector import DomainDetector

class ExistingMethodology:
    def __init__(self):
        # Add new components
        self.domain_detector = DomainDetector()
        # ... existing init code ...
    
    def analyze(self, transcript):
        # Add domain detection
        domain_info = self.domain_detector.analyze_transcript(transcript)
        
        # Adjust existing logic based on domain
        if domain_info["confidence"] < 0.7:
            self.adjust_confidence_thresholds()
        
        # ... existing analysis code ...
```

## Methodology-Specific Integration

### O3 Methodology

**Key Changes:**
1. Add domain detection before deductive coding
2. Use domain-specific codebooks if available
3. Apply hybrid approach for low-confidence domains
4. Add coverage reporting to both deductive and inductive results

**Example:** See `scripts/o3/improved_o3_wrapper.py`

### Opus Methodology

**Key Changes:**
1. Replace hardcoded RAND/AI context with dynamic domain
2. Use adaptive report templates
3. Add validation before Excel generation
4. Track coverage across all three models

**Integration Points:**
- In `enhanced_analyzer.py`: Add domain detection before analysis
- In `report_generator.py`: Use adaptive templates
- In `reliability_calculator.py`: Add coverage metrics

### Sonnet Methodology

**Key Changes:**
1. Load appropriate TAM/DOI codes based on domain
2. Validate multi-model consensus meaningfulness
3. Report actual findings vs template assumptions
4. Add coverage tracking per model

**Integration Points:**
- In `sonnet_analyzer.py`: Domain-aware code loading
- In `run_sonnet_analysis.py`: Add validation checks
- Replace fixed report template with adaptive generation

### Gemini Methodology

**Key Changes:**
1. Detect if content matches AI research domain
2. For non-matching domains, use emergent coding
3. Report theme coverage vs segment coverage
4. Validate theme quality

**Integration Points:**
- In methodology runner: Add domain check
- Adjust prompts based on domain confidence
- Add coverage metrics for themes

## Configuration Updates

### 1. Domain Profiles Configuration

Create `config/domain_profiles.json`:
```json
{
  "domains": {
    "your_domain": {
      "keywords": ["domain", "specific", "terms"],
      "patterns": ["regex patterns"],
      "codebook": "your_domain_codes.json"
    }
  }
}
```

### 2. Pipeline Configuration

Create `config/pipeline_config.json`:
```json
{
  "validation_threshold": 0.7,
  "coverage_warning_threshold": 0.5,
  "enable_caching": true,
  "report_templates_dir": "templates/reports"
}
```

### 3. Update Model Configurations

Add domain awareness to prompts:
```python
if domain_confidence < 0.8:
    prompt += "\nNote: Domain confidence is low. Only code with high certainty."
```

## Testing Integration

### 1. Unit Tests

Test each component individually:
```python
def test_domain_detection():
    detector = DomainDetector()
    result = detector.analyze_transcript("AI research transcript...")
    assert result["detected_domain"] == "ai_research"
    assert result["confidence"] > 0.8
```

### 2. Integration Tests

Test full pipeline:
```python
def test_methodology_with_improvements():
    wrapper = ImprovedMethodologyWrapper()
    result = wrapper.analyze("test_transcript.txt")
    assert result["validation"]["is_valid"]
    assert result["coverage"]["coverage_percent"] > 50
```

### 3. Regression Tests

Ensure existing functionality still works:
```python
def test_backward_compatibility():
    # Original methodology should still work
    original = OriginalMethodology()
    result = original.analyze("transcript.txt")
    assert result is not None
```

## Common Issues and Solutions

### Issue 1: Import Errors
**Solution:** Add src to Python path:
```python
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
```

### Issue 2: Missing Codebooks
**Solution:** Create default codebook or use emergent coding:
```python
if not Path(codebook_path).exists():
    logger.warning("Using emergent coding - no codebook found")
    return self.emergent_coder.code_transcript(transcript)
```

### Issue 3: Performance Impact
**Solution:** Use caching for repeated analyses:
```python
from functools import lru_cache

@lru_cache(maxsize=100)
def detect_domain(transcript_hash):
    return self.domain_detector.analyze_transcript(transcript)
```

## Rollout Strategy

### Phase 1: Testing (Week 1)
1. Create wrapper for one methodology
2. Test on diverse transcripts
3. Compare results with original
4. Tune parameters

### Phase 2: Integration (Week 2)
1. Integrate improvements into all methodologies
2. Update documentation
3. Create migration scripts
4. Train users

### Phase 3: Optimization (Week 3)
1. Analyze performance metrics
2. Optimize slow components
3. Add caching where beneficial
4. Fine-tune thresholds

## Backwards Compatibility

Maintain compatibility by:
1. Keeping original method signatures
2. Adding optional parameters for new features
3. Providing migration scripts
4. Supporting old output formats

Example:
```python
def analyze(self, transcript, use_improvements=True):
    if use_improvements:
        return self.analyze_with_improvements(transcript)
    else:
        return self.original_analyze(transcript)
```

## Benefits After Migration

1. **Domain Awareness**: Appropriate analysis for any content type
2. **Coverage Visibility**: Know what was missed
3. **Quality Assurance**: Automatic validation
4. **Honest Reporting**: No hallucinated findings
5. **Flexibility**: Adapt to new domains easily

## Support

For questions or issues during migration:
1. Check error logs for specific problems
2. Review test cases for examples
3. Use validation reports to debug
4. Start with wrapper approach for safety