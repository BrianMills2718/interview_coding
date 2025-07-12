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
Before running analysis, configure API keys in `config/model_config.yaml`:
- Add your Anthropic API key
- Add your OpenAI API key  
- Add your Google API key

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

## Troubleshooting

### Common Issues
- **Module not found errors**: Reinstall dependencies with `pip install -r requirements.txt`
- **API errors**: Verify API keys in `config/model_config.yaml` are correct and have necessary permissions
- **File path errors**: Check that file paths in configuration files match your directory structure
- **Missing outputs**: Ensure raw transcripts are in `data/raw/` before running batch_clean.py