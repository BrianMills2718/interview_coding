# Gemini25 Methodology

A comprehensive programmatic approach to qualitative coding using multiple LLMs (OpenAI, Anthropic Claude, Google Gemini) with systematic reliability analysis.

## Overview

This methodology implements a structured approach to qualitative analysis with clear separation between automated LLM processing and human-in-the-loop review steps. It provides:

- **Modular Design**: Separate concerns for API calls, data processing, and coding logic
- **Reproducibility**: Version control, explicit configurations, and consistent output formats
- **Iterative Learning**: Clear steps for human review, comparison, and feedback loops
- **Reliability Analysis**: Cohen's Kappa and Fleiss' Kappa calculations for inter-rater agreement

## Directory Structure

```
scripts/gemini25/
├── __init__.py
├── main.py                    # Main orchestrator
├── batch_clean.py            # Transcript preprocessing
├── reliability_calculator.py # Reliability analysis
├── requirements.txt          # Dependencies
├── README.md                # This file
└── utils/
    ├── __init__.py
    ├── llm_api_clients.py    # API client functions
    └── codebook_definitions.py # Codebook and definitions
```

## Setup

1. **Install Dependencies**:
   ```bash
   pip install -r scripts/gemini25/requirements.txt
   ```

2. **Environment Variables**:
   Create a `.env` file in your project root with:
   ```
   OPENAI_API_KEY=your_openai_key
   ANTHROPIC_API_KEY=your_anthropic_key
   GOOGLE_API_KEY=your_google_key
   ```

3. **Codebook Configuration**:
   Edit `utils/codebook_definitions.py` to customize your CODEBOOK dictionary and ANALYSIS_START_MARKER.

## Workflow

### Phase 1: Human Pre-processing & Codebook Refinement
1. **Transcript Hygiene**: Run `batch_clean.py` to clean and standardize transcripts
2. **Codebook Finalization**: Define and refine the CODEBOOK structure
3. **Analysis Marker**: Set the ANALYSIS_START_MARKER for where analytical discussion begins

### Phase 2: LLM Coding Passes (Automated)
1. **Quote Extraction**: LLMs identify relevant text segments
2. **Code Assignment**: Apply pre-defined codes to extracted quotes
3. **Emergent Theme Suggestion**: Identify patterns not fitting existing codes
4. **Structured Output**: Generate machine-readable JSON format

### Phase 3: Collaborative Review & Human Coding
1. **LLM Output Evaluation**: Critically assess accuracy and completeness
2. **Emergent Theme Validation**: Review and merge suggested themes
3. **Independent Human Coding**: Perform "gold standard" coding
4. **Discrepancy Analysis**: Investigate differences between LLM and human coding
5. **Reliability Calculation**: Execute chosen reliability metrics
6. **Iteration & Refinement**: Provide feedback for process improvement

## Usage

### 1. Clean Transcripts
```bash
cd scripts/gemini25
python batch_clean.py
```

### 2. Run LLM Analysis
```bash
python main.py
```

### 3. Calculate Reliability
```bash
python reliability_calculator.py
```

## Output Structure

```
outputs/
├── coded_segments/
│   ├── openai_focus_group_1_coded.csv
│   ├── anthropic_focus_group_1_coded.csv
│   ├── gemini_focus_group_1_coded.csv
│   ├── openai_focus_group_1_themes.csv
│   └── ...
├── reliability_reports/
│   ├── focus_group_1_reliability_report.json
│   ├── focus_group_1_reliability_summary.csv
│   └── ...
└── logs/
    ├── openai_api_log.jsonl
    ├── anthropic_api_log.jsonl
    └── gemini_api_log.jsonl
```

## Codebook Structure

The CODEBOOK dictionary should follow this format:

```python
CODEBOOK = {
    "CODE_NAME": {
        "definition": "Single sentence definition of the code",
        "description": "Detailed description for reference"
    },
    # ... more codes
}
```

## Reliability Metrics

- **Cohen's Kappa**: For pairwise agreement (Human vs. LLM)
- **Fleiss' Kappa**: For agreement among all raters (Human + all LLMs)

### Interpretation Guidelines:
- 0.81-1.00: Almost perfect agreement
- 0.61-0.80: Substantial agreement
- 0.41-0.60: Moderate agreement
- 0.21-0.40: Fair agreement
- 0.01-0.20: Slight agreement
- <0.01: Poor agreement

## Customization

### Adding New Models
1. Add API client function in `utils/llm_api_clients.py`
2. Update model selection in `main.py`
3. Add model-specific prompt formatting if needed

### Modifying Codebook
1. Edit `utils/codebook_definitions.py`
2. Update CODEBOOK dictionary
3. Modify ANALYSIS_START_MARKER if needed

### Custom Prompts
1. Modify `generate_coding_prompt()` in `main.py`
2. Adjust JSON output format as needed
3. Update parsing logic in `parse_coding_response()`

## Troubleshooting

### API Errors
- Verify API keys in `.env` file
- Check API rate limits and quotas
- Review API response logs in `outputs/logs/`

### Parsing Errors
- Check JSON format in LLM responses
- Review raw responses in API logs
- Verify prompt structure

### Reliability Calculation Issues
- Ensure coded segments are properly aligned
- Check for empty or malformed data
- Verify codebook consistency across models

## Best Practices

1. **Start Small**: Test with a single transcript before batch processing
2. **Review Outputs**: Always review LLM outputs before proceeding
3. **Iterate**: Use human feedback to improve prompts and codebook
4. **Document Changes**: Keep track of codebook modifications and prompt updates
5. **Validate Quality**: Use reliability metrics to assess consistency

## Contributing

When modifying this methodology:
1. Maintain the modular structure
2. Update documentation for any changes
3. Test with sample data before deployment
4. Preserve the human-in-the-loop approach 