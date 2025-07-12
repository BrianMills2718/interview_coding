# Sonnet Methodology Implementation

## Overview

The Sonnet methodology implements a multi-LLM consensus approach for analyzing Microsoft Teams transcripts using the Technology Acceptance Model (TAM) and Diffusion of Innovation (DOI) frameworks. This methodology uses Claude 3 Sonnet, GPT-4, and Gemini Pro to achieve high-reliability qualitative coding through consensus building.

## Key Features

- **Multi-LLM Consensus**: Uses three state-of-the-art LLMs for robust coding
- **TAM/DOI Framework**: Based on established theoretical frameworks for technology adoption
- **Reliability Metrics**: Implements Krippendorff's alpha and agreement ratios
- **Comprehensive Output**: Generates detailed reports, visualizations, and human review exports
- **Quality Assessment**: Built-in quality metrics and disagreement analysis

## Architecture

```
scripts/sonnet/
├── sonnet_analyzer.py      # Main analyzer class
├── run_sonnet_analysis.py  # Batch runner script
└── README.md              # This file

src/
├── analysis/
│   └── output_manager.py   # Output management and reporting
└── utils/
    ├── llm_utils.py        # LLM client interface
    ├── reliability.py      # Reliability calculations
    └── consensus.py        # Consensus building logic

config/
└── sonnet_config.json     # Configuration settings
```

## Installation

1. **Install Dependencies**:
   ```bash
   pip install anthropic openai google-generativeai pandas numpy openpyxl
   ```

2. **Set Environment Variables**:
   ```bash
   export ANTHROPIC_API_KEY="your_anthropic_key"
   export OPENAI_API_KEY="your_openai_key"
   export GOOGLE_API_KEY="your_google_key"
   ```

3. **Verify Installation**:
   ```bash
   python scripts/sonnet/run_sonnet_analysis.py --check-only
   ```

## Usage

### Basic Usage

Run analysis on all transcripts in the default directory:
```bash
python scripts/sonnet/run_sonnet_analysis.py
```

### Advanced Usage

Specify custom directories and configuration:
```bash
python scripts/sonnet/run_sonnet_analysis.py \
    --transcript-dir data/processed \
    --config config/sonnet_config.json \
    --output-path data/analysis_outputs/sonnet
```

### Single File Analysis

Analyze a single transcript file:
```bash
python scripts/sonnet/sonnet_analyzer.py --single-file data/processed/transcript1.txt
```

## Configuration

The `config/sonnet_config.json` file contains all configuration settings:

### LLM Models
- `claude-3-sonnet`: Anthropic's Claude 3 Sonnet
- `gpt-4`: OpenAI's GPT-4
- `gemini-pro`: Google's Gemini Pro

### Consensus Settings
- `consensus_threshold`: 0.7 (70% agreement required for consensus)
- `krippendorff_alpha_threshold`: 0.6 (minimum acceptable reliability)

### Coding Schema

The methodology uses a comprehensive coding schema based on TAM and DOI frameworks:

#### Technology Acceptance Model (TAM)
- **Perceived Usefulness**: BENEFIT_EFFICIENCY, BENEFIT_CAPABILITY, BENEFIT_QUALITY, BENEFIT_COST_SAVINGS
- **Perceived Ease of Use**: BARRIER_TRAINING, BARRIER_TECHNICAL, AI_USAGE_WRITING, AI_USAGE_CODING
- **Perceived Barriers**: BARRIER_QUALITY, BARRIER_ACCESS, CONCERN_VALIDITY, CONCERN_ETHICS, CONCERN_JOBS
- **Usage Behavior**: AI_USAGE_CODING, AI_USAGE_ANALYSIS, AI_USAGE_WRITING, AI_USAGE_LITERATURE

#### Diffusion of Innovation (DOI)
- **Relative Advantage**: BENEFIT_EFFICIENCY, BENEFIT_CAPABILITY, PAIN_ANALYSIS, PAIN_WRITING
- **Complexity**: BARRIER_TRAINING, CONCERN_VALIDITY, BARRIER_TECHNICAL
- **Compatibility**: METHODS_MIXED, ORG_SUPPORT, WORKFLOW_INTEGRATION
- **Observability**: AI_USAGE_CODING, AI_USAGE_ANALYSIS, SUCCESS_STORIES
- **Trialability**: BARRIER_ACCESS, ORG_BARRIERS, PILOT_PROGRAMS

## Output Structure

The analysis generates a comprehensive output structure:

```
data/analysis_outputs/sonnet/
├── raw_coding/           # Individual LLM coding results
├── consensus/            # Consensus coding results
├── reliability/          # Reliability analysis
├── reports/              # Final reports (JSON and Markdown)
├── validation/           # Human review exports
└── visualizations/       # Charts and graphs
```

### Key Output Files

1. **Individual Results**: `{transcript_id}_{model}_{type}.json`
2. **Consensus Results**: `{transcript_id}_consensus.json`
3. **Reliability Analysis**: `sonnet_overall_reliability.json`
4. **Final Report**: `final_report_{timestamp}.md`
5. **Human Review**: `human_review_{timestamp}.xlsx`

## Methodology Details

### Consensus Building Process

1. **Individual Coding**: Each LLM independently codes the transcript using the TAM/DOI schema
2. **Decision Aggregation**: Coding decisions are aggregated across all models
3. **Consensus Calculation**: Agreement ratios are calculated for each code
4. **Threshold Application**: Codes meeting the consensus threshold (70%) are accepted
5. **Confidence Weighting**: For codes without consensus, confidence-weighted decisions are used

### Reliability Metrics

- **Krippendorff's Alpha**: Measures inter-coder reliability
- **Agreement Ratio**: Percentage of models agreeing on each code
- **Pairwise Agreements**: Agreement between each pair of models
- **Overall Confidence**: Average confidence across all models

### Quality Assessment

The methodology includes comprehensive quality assessment:

- **Consensus Quality**: Measures the strength of consensus decisions
- **Disagreement Analysis**: Identifies areas of model disagreement
- **Resolution Strategies**: Suggests approaches for resolving disagreements
- **Validation Exports**: Formats data for human review

## Theoretical Framework

### Technology Acceptance Model (TAM)

The TAM framework examines how users come to accept and use technology:

- **Perceived Usefulness**: The degree to which a person believes that using AI will enhance their job performance
- **Perceived Ease of Use**: The degree to which a person believes that using AI will be free of effort
- **Usage Behavior**: Actual usage patterns and intentions

### Diffusion of Innovation (DOI)

The DOI framework explains how innovations spread through social systems:

- **Relative Advantage**: The degree to which AI is perceived as better than existing methods
- **Complexity**: The degree to which AI is perceived as difficult to understand and use
- **Compatibility**: The degree to which AI fits with existing values and experiences
- **Observability**: The degree to which AI results are visible to others
- **Trialability**: The degree to which AI can be experimented with on a limited basis

## Troubleshooting

### Common Issues

1. **API Key Errors**: Ensure all environment variables are set correctly
2. **Import Errors**: Verify all dependencies are installed
3. **File Not Found**: Check that transcript files exist in the specified directory
4. **Memory Issues**: For large transcripts, consider chunking the analysis

### Debug Mode

Enable detailed logging:
```bash
export LOG_LEVEL=DEBUG
python scripts/sonnet/run_sonnet_analysis.py
```

### Performance Optimization

- Use smaller transcript chunks for memory-constrained environments
- Adjust `max_tokens` in configuration for faster processing
- Consider running individual model analyses in parallel

## Validation and Quality Assurance

### Human Review Process

1. **Export Review Data**: Use the Excel export for human review
2. **Review Consensus Decisions**: Check high-confidence codes for accuracy
3. **Resolve Disagreements**: Manually review codes with low agreement
4. **Update Schema**: Refine coding schema based on review findings

### Quality Metrics

- **Target Alpha**: > 0.6 (acceptable reliability)
- **Target Agreement**: > 0.7 (strong consensus)
- **Target Confidence**: > 0.8 (high confidence decisions)

## Future Enhancements

- **Additional Models**: Support for more LLM providers
- **Custom Schemas**: User-defined coding schemas
- **Real-time Analysis**: Live transcript analysis capabilities
- **Advanced Visualizations**: Interactive charts and dashboards
- **API Integration**: REST API for programmatic access

## Citation

When using this methodology, please cite:

```
Sonnet Methodology: Multi-LLM Consensus Analysis for Qualitative Research
RAND Corporation, 2024
```

## Support

For questions or issues with the Sonnet methodology implementation, please refer to the project documentation or contact the development team. 