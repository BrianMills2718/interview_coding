# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a qualitative research framework for analyzing Microsoft Teams focus group transcripts using multiple LLM-based methodologies. The project implements four distinct methodologies for comparative analysis: o3 (deductive/inductive), Opus (formal coding), Sonnet (consensus-based), and Gemini (reliability-focused).

## Complete Analysis Pipeline

### 1. Environment Setup
```bash
# Create and activate virtual environment
python3 -m venv venv

# Activation - macOS/Linux:
source venv/bin/activate

# Activation - Windows:
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Data Preparation
```bash
# Place raw .docx transcripts in data/raw/
# Then run cleaning script:
python scripts/o3/batch_clean.py
# This creates cleaned versions in data/tidy/
```

### 3. Configuration
**CRITICAL**: You MUST configure real API keys and models in `.env` file:
```bash
# Required API Keys
ANTHROPIC_API_KEY=your_actual_anthropic_key
OPENAI_API_KEY=your_actual_openai_key
GOOGLE_API_KEY=your_actual_google_key

# Required Model Configurations
O3_CLAUDE_MODEL=claude-3-5-sonnet-20241022
O3_GPT4_MODEL=gpt-4o
O3_GEMINI_MODEL=gemini-1.5-pro
OPUS_CLAUDE_MODEL=claude-3-5-sonnet-20241022
OPUS_GPT4_MODEL=gpt-4o
OPUS_GEMINI_MODEL=gemini-1.5-pro
SONNET_CLAUDE_MODEL=claude-3-5-sonnet-20241022
SONNET_GPT4_MODEL=gpt-4o
SONNET_GEMINI_MODEL=gemini-1.5-pro
GEMINI_MODEL=gemini-1.5-pro
```

⚠️ **WARNING**: The pipeline will NOT work without valid API keys. Always test with real API calls before declaring success.

Optional: Review `config/prompts.yaml` and `config/sonnet_config.json` (defaults are suitable for first run)

### 4. Running the Complete Analysis
```bash
# Execute all four methodologies
python scripts/run_all_methodologies.py
```

### 5. Outputs
Results are organized in the `output/` directory:
- `output/o3/`: Deductive/inductive coding results, merged outputs, reliability scores
- `output/opus/`: Structured coding results, reliability analysis, narrative report
- `output/sonnet/`: Consensus-based coding, cross-transcript comparisons, batch analysis
- `output/gemini/`: Batch processing outputs, reliability metrics, CSV/JSON results

Refer to `preliminary_report.md` for synthesis template.

## Essential Commands

### Quick Commands
```bash
# Quick start - runs complete setup and all methodologies
python quick_start.py

# Run specific methodologies only
python scripts/run_all_methodologies.py --methods o3 sonnet

# Check environment setup only
python scripts/run_all_methodologies.py --check-only

# Run individual methodologies
python scripts/o3/deductive_runner.py --transcript-dir data/processed
python scripts/opus/enhanced_analyzer.py --transcript-dir data/processed
python scripts/sonnet/run_sonnet_analysis.py --transcript-dir data/processed
python scripts/gemini25/main.py --transcript-dir data/processed
```

### Testing
```bash
# Run a single test file
python -m pytest tests/test_specific_file.py

# Run tests for a specific methodology
python -m pytest tests/test_o3/
python -m pytest tests/test_sonnet/

# Run all tests
python -m pytest
```

## Architecture Overview

### Core Structure
- **Multi-Methodology Design**: Four independent methodologies that can run in parallel, each with distinct analysis approaches
- **Shared Infrastructure**: Common utilities in `/src` for LLM operations, data processing, and reliability calculations
- **Pipeline Pattern**: Each methodology follows input → processing → analysis → output flow with consistent interfaces

### Key Components
1. **LLM Abstraction Layer** (`src/models/`): Unified interface for Claude, GPT-4, and Gemini models
2. **Analysis Pipeline** (`src/analysis/`): Manages workflow from transcript processing to final outputs
3. **Reliability Framework** (`src/utils/reliability.py`): Calculates inter-coder agreement using Krippendorff's alpha
4. **Output Management**: Generates multiple formats (JSON, CSV, Excel, Markdown) with consistent structure

### Data Flow
1. Raw `.docx` transcripts → `scripts/o3/batch_clean.py` → cleaned `.txt` files
2. Cleaned transcripts → methodology-specific analysis → structured outputs
3. Individual outputs → aggregation/comparison → final reports

### Methodology Differences
- **o3**: Uses deductive coding (predefined codes) + inductive coding (emergent themes) with union merge
- **Opus**: Implements formal coding schema with multi-LLM validation
- **Sonnet**: Achieves consensus through multiple LLM iterations using TAM/DOI frameworks
- **Gemini**: Optimized for Gemini models with built-in reliability metrics

### Extension Points
- Add new methodologies by creating a new directory in `/scripts/` following existing patterns
- Extend codebooks via `config/codebook.yaml`
- Add new LLM providers by implementing the interface in `src/models/`
- Customize prompts in `config/prompts.yaml`

## Testing and Validation

### ⚠️ IMPORTANT: Always Test Before Declaring Success
1. **Never assume the pipeline works without testing**
2. **Always verify with real API calls**
3. **Check all outputs are generated correctly**
4. **Run the test suite**: `python scripts/test_pipeline.py`

### Real Testing Checklist
- [ ] API keys are valid and working
- [ ] Model configurations are set in .env
- [ ] Test transcript processes correctly
- [ ] All four methodologies produce outputs
- [ ] No API errors or rate limiting issues
- [ ] Outputs contain actual analysis (not empty)

## Troubleshooting

### Common Issues
- **Module not found errors**: Reinstall dependencies with `pip install -r requirements.txt`
- **API errors**: Verify API keys in `.env` are correct and have necessary permissions
- **Model not found**: Ensure model names in .env match available models
- **File path errors**: Check that file paths in configuration files match your directory structure
- **Missing outputs**: Ensure raw transcripts are in `data/raw/` before running batch_clean.py
- **Empty results**: Check API keys are valid and you're not hitting rate limits