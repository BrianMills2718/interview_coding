# LLM Methodologies Implementation Guide

## Overview

This guide covers how to implement and run all four LLM methodologies (o3, Opus, Sonnet, and Gemini) for analyzing Microsoft Teams transcripts. Each methodology provides a different approach to qualitative research using large language models.

## Methodology Summary

| Methodology | Approach | Key Features | Status |
|-------------|----------|--------------|---------|
| **o3** | Deductive + Inductive | Union merge logic, Krippendorff's alpha | ✅ Implemented |
| **Opus** | Multi-LLM Analysis | Formal coding schema, reliability metrics | ✅ Implemented |
| **Sonnet** | Multi-LLM Consensus | TAM/DOI framework, consensus building | ✅ Implemented |
| **Gemini** | Gemini-focused | Reliability calculator, batch processing | ✅ Implemented |

## Prerequisites

### 1. Environment Setup

```bash
# Install all required dependencies
pip install anthropic openai google-generativeai pandas numpy openpyxl python-docx

# Set environment variables
export ANTHROPIC_API_KEY="your_anthropic_key"
export OPENAI_API_KEY="your_openai_key" 
export GOOGLE_API_KEY="your_google_key"
```

### 2. Data Preparation

Ensure your transcripts are in the correct format:
- Raw transcripts: `data/raw/*.docx` (Microsoft Teams exports)
- Processed transcripts: `data/processed/*.txt` or `data/processed/*.csv`

### 3. Directory Structure

```
project/
├── data/
│   ├── raw/                    # Original .docx files
│   ├── processed/              # Cleaned .txt/.csv files
│   └── analysis_outputs/       # Analysis results
│       ├── o3/
│       ├── opus/
│       ├── sonnet/
│       └── gemini/
├── scripts/
│   ├── o3/                     # o3 methodology
│   ├── opus/                   # Opus methodology
│   ├── sonnet/                 # Sonnet methodology
│   ├── gemini25/               # Gemini methodology
│   └── run_all_methodologies.py # Master runner
└── config/
    └── sonnet_config.json      # Sonnet configuration
```

## Step-by-Step Implementation

### Step 1: Data Cleaning

First, clean your raw transcripts:

```bash
# Clean all .docx files in data/raw/
python scripts/o3/batch_clean.py
```

This will:
- Process all `.docx` files in `data/raw/`
- Generate clean `.txt` and `.csv` files in `data/processed/`
- Create unique slugs for each transcript

### Step 2: Environment Check

Check that everything is properly configured:

```bash
# Check environment for all methodologies
python scripts/run_all_methodologies.py --check-only
```

This will verify:
- API keys are set
- Transcript files exist
- All scripts are available
- Dependencies are installed

### Step 3: Run Individual Methodologies

#### Option A: Run All Methodologies

```bash
# Run all four methodologies
python scripts/run_all_methodologies.py
```

#### Option B: Run Specific Methodologies

```bash
# Run only o3 and Sonnet
python scripts/run_all_methodologies.py --methods o3 sonnet

# Run only Opus
python scripts/run_all_methodologies.py --methods opus
```

#### Option C: Run Methodologies Individually

**o3 Methodology:**
```bash
# Run deductive analysis
python scripts/o3/deductive_runner.py --transcript-dir data/processed

# Run inductive analysis  
python scripts/o3/inductive_runner.py --transcript-dir data/processed

# Generate theme matrix
python scripts/o3/theme_matrix.py

# Generate report
python scripts/o3/report_stub.py
```

**Opus Methodology:**
```bash
# Run enhanced analyzer
python scripts/opus/enhanced_analyzer.py --transcript-dir data/processed
```

**Sonnet Methodology:**
```bash
# Run Sonnet analysis
python scripts/sonnet/run_sonnet_analysis.py --transcript-dir data/processed
```

**Gemini Methodology:**
```bash
# Run Gemini analysis
python scripts/gemini25/main.py --transcript-dir data/processed
```

## Methodology Details

### o3 Methodology

**Approach:** Deductive and inductive coding with union merge logic

**Key Components:**
- `deductive_runner.py`: Applies predefined codes
- `inductive_runner.py`: Discovers new codes
- `merge_and_alpha.py`: Combines results and calculates reliability
- `theme_matrix.py`: Generates prevalence matrices
- `report_stub.py`: Creates executive briefs

**Output:** Excel files with theme matrices, reliability metrics, and reports

### Opus Methodology

**Approach:** Multi-LLM analysis with formal coding schema

**Key Components:**
- `enhanced_analyzer.py`: Main analysis engine
- `codebook.py`: Formal coding schema
- `reliability_calculator.py`: Inter-coder reliability
- `report_generator.py`: Narrative reports

**Output:** JSON results, reliability metrics, and narrative reports

### Sonnet Methodology

**Approach:** Multi-LLM consensus with TAM/DOI framework

**Key Components:**
- `sonnet_analyzer.py`: Main consensus analyzer
- `run_sonnet_analysis.py`: Batch runner
- `output_manager.py`: Comprehensive output management
- TAM/DOI coding schema

**Output:** Consensus results, reliability metrics, cross-transcript analysis

### Gemini Methodology

**Approach:** Gemini-focused analysis with reliability metrics

**Key Components:**
- `main.py`: Main analysis script
- `reliability_calculator.py`: Reliability metrics
- `batch_clean.py`: Data preprocessing

**Output:** Gemini-specific analysis results and reliability metrics

## Output Analysis

### Understanding Results

Each methodology produces different types of outputs:

1. **Raw Coding Results**: Individual LLM coding decisions
2. **Consensus/Combined Results**: Aggregated coding decisions
3. **Reliability Metrics**: Inter-coder agreement statistics
4. **Reports**: Human-readable summaries and insights
5. **Visualizations**: Charts, matrices, and graphs

### Comparative Analysis

The master runner (`run_all_methodologies.py`) creates a comparative analysis:

```bash
# View comparative results
cat data/analysis_outputs/comparative_analysis.json
```

This includes:
- Success/failure status for each methodology
- Duration comparisons
- Output file counts
- Recommendations for further analysis

## Troubleshooting

### Common Issues

1. **API Key Errors**
   ```bash
   # Check environment variables
   echo $ANTHROPIC_API_KEY
   echo $OPENAI_API_KEY
   echo $GOOGLE_API_KEY
   ```

2. **Missing Dependencies**
   ```bash
   # Reinstall dependencies
   pip install -r requirements.txt
   ```

3. **Transcript Not Found**
   ```bash
   # Check transcript directory
   ls data/processed/
   ```

4. **Script Errors**
   ```bash
   # Check script permissions
   chmod +x scripts/*/*.py
   ```

### Debug Mode

Enable detailed logging:
```bash
export LOG_LEVEL=DEBUG
python scripts/run_all_methodologies.py
```

### Performance Optimization

- **Parallel Processing**: Run methodologies in parallel if you have multiple API keys
- **Chunking**: For large transcripts, consider processing in chunks
- **Caching**: Results are cached to avoid re-processing

## Advanced Usage

### Custom Configuration

Each methodology can be customized:

**Sonnet Configuration:**
```bash
# Edit Sonnet config
nano config/sonnet_config.json
```

**o3 Configuration:**
```bash
# Edit o3 prompts
nano scripts/o3/llm_utils.py
```

### Adding New Methodologies

To add a new methodology:

1. Create a new directory in `scripts/`
2. Implement the required scripts
3. Add configuration to `run_all_methodologies.py`
4. Update this guide

### Integration with Other Tools

The outputs can be integrated with:
- **R**: For statistical analysis
- **Tableau**: For visualization
- **NVivo**: For qualitative analysis
- **Excel**: For manual review

## Quality Assurance

### Validation Steps

1. **Human Review**: Use exported Excel files for manual review
2. **Cross-Validation**: Compare results across methodologies
3. **Reliability Checks**: Ensure Krippendorff's alpha > 0.6
4. **Consensus Validation**: Review low-agreement codes

### Best Practices

1. **Start Small**: Test with 1-2 transcripts first
2. **Monitor Costs**: Track API usage and costs
3. **Document Changes**: Keep track of configuration changes
4. **Backup Results**: Save important outputs
5. **Iterate**: Refine prompts and configurations based on results

## Next Steps

After running all methodologies:

1. **Compare Results**: Analyze differences between methodologies
2. **Validate Findings**: Conduct human review of key findings
3. **Refine Approach**: Adjust prompts and configurations
4. **Scale Up**: Apply to larger datasets
5. **Publish Results**: Document findings and methodology

## Support

For questions or issues:
1. Check the logs in `*.log` files
2. Review the methodology-specific README files
3. Check the `problems.md` file for known issues
4. Consult the `edits.md` file for recent changes

## Citation

When using these methodologies, please cite:

```
Multi-LLM Methodologies for Qualitative Research Analysis
RAND Corporation, 2024
```

This guide provides a comprehensive approach to implementing all four LLM methodologies for comparative qualitative research analysis. 