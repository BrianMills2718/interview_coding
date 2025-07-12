# LLM Qualitative Research Methodologies

A comprehensive framework for analyzing Microsoft Teams focus group transcripts using four different LLM methodologies: o3, Opus, Sonnet, and Gemini. This system enables comparative analysis of different approaches to qualitative research using large language models.

## 📁 Project Structure

```
Interviews/
├── 📄 README.md                           # This comprehensive documentation
├── 📄 METHODOLOGY_IMPLEMENTATION_GUIDE.md # Detailed implementation guide
├── 📄 requirements.txt                    # Python dependencies
├── 📄 main.py                            # Entry point for the application
├── 📄 quick_start.py                     # Quick setup and run script
├── 📄 all_methodologies_analysis.log     # Master analysis log
├── 📄 sonnet_analysis.log                # Sonnet methodology log
├── 📄 edits.md                           # Development notes and edits
├── 📄 problems.md                        # Known issues and problems
├── 📄 create_env.py                      # Environment setup script
├── 📄 fix_env.py                         # Environment fix script
├── 📄 update_env.py                      # Environment update script
├── 📄 update_env_final.py                # Final environment update
├── 📄 setup_clean_env.py                 # Clean environment setup
├── 📄 fix_pandas.py                      # Pandas compatibility fixes
│
├── 📁 data/                              # Data directory
│   ├── 📁 raw/                           # Original .docx transcript files
│   ├── 📁 processed/                     # Cleaned .txt/.csv transcript files
│   └── 📁 analysis_outputs/              # Analysis results
│       ├── 📄 comparative_analysis.json  # Cross-methodology comparison
│       ├── 📁 o3/                        # o3 methodology outputs
│       ├── 📁 opus/                      # Opus methodology outputs
│       ├── 📁 sonnet/                    # Sonnet methodology outputs
│       └── 📁 gemini/                    # Gemini methodology outputs
│
├── 📁 scripts/                           # Main methodology implementations
│   ├── 📄 run_all_methodologies.py       # Master orchestrator script
│   │
│   ├── 📁 o3/                           # o3 Methodology
│   │   ├── 📄 deductive_runner.py        # Deductive coding with predefined codes
│   │   ├── 📄 inductive_runner.py        # Inductive coding for novel themes
│   │   ├── 📄 merge_and_alpha.py         # Combines results and calculates reliability
│   │   ├── 📄 theme_matrix.py            # Generates prevalence matrices
│   │   ├── 📄 report_stub.py             # Creates executive briefs
│   │   ├── 📄 llm_utils.py               # LLM API utilities for o3
│   │   ├── 📄 batch_clean.py             # Data preprocessing
│   │   └── 📄 clean1_o3.py               # Additional cleaning utilities
│   │
│   ├── 📁 opus/                         # Opus Methodology
│   │   ├── 📄 enhanced_analyzer.py       # Main analysis engine
│   │   ├── 📄 opus_anayzer1.py          # Alternative analyzer implementation
│   │   ├── 📄 codebook.py               # Formal coding schema
│   │   ├── 📄 reliability_calculator.py # Inter-coder reliability metrics
│   │   └── 📄 report_generator.py       # Narrative report generation
│   │
│   ├── 📁 sonnet/                       # Sonnet Methodology
│   │   ├── 📄 run_sonnet_analysis.py    # Batch runner for Sonnet
│   │   ├── 📄 sonnet_analyzer.py        # Main consensus analyzer
│   │   └── 📄 README.md                 # Sonnet-specific documentation
│   │
│   └── 📁 gemini25/                     # Gemini Methodology
│       ├── 📄 main.py                   # Main orchestrator for Gemini
│       ├── 📄 batch_clean.py            # Data preprocessing
│       ├── 📄 reliability_calculator.py # Reliability metrics
│       ├── 📄 requirements.txt          # Gemini-specific dependencies
│       ├── 📄 README.md                 # Gemini-specific documentation
│       └── 📁 utils/                    # Gemini utilities
│           ├── 📄 llm_api_clients.py    # API clients for all LLMs
│           ├── 📄 codebook_definitions.py # Codebook definitions
│           └── 📄 __init__.py           # Package initialization
│
├── 📁 src/                               # Shared source code
│   ├── 📁 utils/                         # Shared utilities
│   │   ├── 📄 llm_utils.py              # Unified LLM client interface
│   │   ├── 📄 consensus.py              # Consensus building algorithms
│   │   ├── 📄 reliability.py            # Reliability calculation utilities
│   │   └── 📄 __init__.py               # Package initialization
│   │
│   ├── 📁 analysis/                     # Analysis components
│   │   ├── 📄 output_manager.py         # Comprehensive output management
│   │   ├── 📄 pipeline.py               # Analysis pipeline utilities
│   │   └── 📄 __init__.py               # Package initialization
│   │
│   ├── 📁 coding/                       # Coding utilities
│   │   ├── 📄 codebook.py               # Codebook management
│   │   ├── 📄 reliability.py            # Coding reliability metrics
│   │   └── 📄 __init__.py               # Package initialization
│   │
│   ├── 📁 models/                       # Model interfaces
│   │   ├── 📄 llm_interface.py          # LLM model interface
│   │   └── 📄 __init__.py               # Package initialization
│   │
│   ├── 📁 validation/                   # Validation utilities
│   │   └── 📄 __init__.py               # Package initialization
│   │
│   └── 📄 __init__.py                   # Main package initialization
│
├── 📁 config/                           # Configuration files
│   ├── 📄 sonnet_config.json            # Sonnet methodology configuration
│   ├── 📄 codebook.yaml                 # Codebook definitions
│   ├── 📄 prompts.yaml                  # Prompt templates
│   └── 📄 models.yaml                   # Model configurations
│
├── 📁 outputs/                          # Runtime outputs
│   ├── 📁 deductive/                    # o3 deductive coding results
│   ├── 📁 inductive/                    # o3 inductive coding results
│   ├── 📁 opus_enhanced/                # Opus methodology outputs
│   ├── 📁 coded_segments/               # Coded transcript segments
│   ├── 📁 reliability_reports/          # Reliability analysis reports
│   └── 📁 logs/                         # Runtime logs
│
├── 📁 docs/                             # Documentation (currently empty)
├── 📁 envs/                             # Environment files
└── 📁 Interviews/                       # Additional interview data
```

## 🎯 Methodology Overview

### 1. **o3 Methodology** (`scripts/o3/`)
**Approach**: Deductive and inductive coding with union merge logic
- **Deductive Analysis**: Applies predefined codes from a structured codebook
- **Inductive Analysis**: Discovers novel themes and codes
- **Union Merge**: Combines results using union logic
- **Reliability**: Calculates Krippendorff's alpha for inter-coder agreement

**Key Files**:
- `deductive_runner.py`: Processes transcripts with 3 LLMs (Claude-Sonnet, GPT-4o, Gemini)
- `inductive_runner.py`: Discovers new codes with 2 LLMs (Claude-Sonnet, GPT-4o)
- `merge_and_alpha.py`: Combines results and calculates reliability metrics
- `theme_matrix.py`: Generates prevalence matrices for themes
- `report_stub.py`: Creates executive briefs and summaries

### 2. **Opus Methodology** (`scripts/opus/`)
**Approach**: Multi-LLM analysis with formal coding schema
- **Formal Codebook**: Structured coding schema with definitions
- **Multi-LLM**: Uses Claude, GPT-4, and Gemini simultaneously
- **Reliability Metrics**: Inter-coder agreement calculations
- **Narrative Reports**: Human-readable analysis summaries

**Key Files**:
- `enhanced_analyzer.py`: Main analysis engine with all three LLMs
- `codebook.py`: Formal coding schema with definitions
- `reliability_calculator.py`: Inter-coder reliability metrics
- `report_generator.py`: Narrative report generation

### 3. **Sonnet Methodology** (`scripts/sonnet/`)
**Approach**: Multi-LLM consensus with TAM/DOI framework
- **TAM/DOI Framework**: Technology Acceptance Model and Diffusion of Innovation
- **Consensus Building**: Agreement-based coding decisions
- **Cross-Transcript Analysis**: Comparative analysis across transcripts
- **Comprehensive Outputs**: Multiple output formats and visualizations

**Key Files**:
- `sonnet_analyzer.py`: Main consensus analyzer with TAM/DOI schema
- `run_sonnet_analysis.py`: Batch runner for multiple transcripts
- `config/sonnet_config.json`: Configuration with TAM/DOI coding schema

### 4. **Gemini Methodology** (`scripts/gemini25/`)
**Approach**: Gemini-focused analysis with reliability metrics
- **Gemini-Centric**: Optimized for Google's Gemini model
- **Batch Processing**: Efficient processing of multiple transcripts
- **Reliability Calculator**: Comprehensive reliability metrics
- **Structured Outputs**: CSV and JSON outputs for analysis

**Key Files**:
- `main.py`: Main orchestrator for Gemini analysis
- `reliability_calculator.py`: Reliability metrics and calculations
- `utils/llm_api_clients.py`: API clients for all LLM providers
- `utils/codebook_definitions.py`: Codebook definitions

## 🔧 Setup and Installation

### Prerequisites
```bash
# Install Python dependencies
pip install -r requirements.txt

# Required packages:
# - anthropic>=0.18.0 (Claude API)
# - openai>=1.12.0 (GPT-4 API)
# - google-generativeai>=0.3.0 (Gemini API)
# - pandas>=2.0.0 (Data manipulation)
# - openpyxl>=3.1.0 (Excel output)
# - python-dotenv>=1.0.0 (Environment variables)
# - pydantic>=2.0.0 (Data validation)
# - numpy>=1.24.0 (Numerical computing)
# - scikit-learn>=1.3.0 (Machine learning)
# - pyyaml>=6.0.0 (YAML parsing)
# - krippendorff>=0.5.0 (Reliability calculations)
```

### Environment Configuration
```bash
# Set up environment variables
export ANTHROPIC_API_KEY="your_anthropic_key"
export OPENAI_API_KEY="your_openai_key"
export GOOGLE_API_KEY="your_google_key"

# Or use the setup scripts:
python create_env.py
python fix_env.py
```

### Data Preparation
1. Place raw Microsoft Teams transcripts in `data/raw/` (`.docx` format)
2. Run data cleaning: `python scripts/o3/batch_clean.py`
3. Cleaned transcripts will be in `data/processed/` (`.txt` and `.csv` format)

## 🚀 Usage

### Quick Start
```bash
# Run all methodologies
python quick_start.py

# Or run the master orchestrator
python scripts/run_all_methodologies.py
```

### Individual Methodologies

#### o3 Methodology
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

#### Opus Methodology
```bash
# Run enhanced analyzer
python scripts/opus/enhanced_analyzer.py --transcript-dir data/processed
```

#### Sonnet Methodology
```bash
# Run Sonnet analysis
python scripts/sonnet/run_sonnet_analysis.py --transcript-dir data/processed
```

#### Gemini Methodology
```bash
# Run Gemini analysis
python scripts/gemini25/main.py --transcript-dir data/processed
```

### Selective Execution
```bash
# Run specific methodologies
python scripts/run_all_methodologies.py --methods o3 sonnet

# Run only Opus
python scripts/run_all_methodologies.py --methods opus
```

## 📊 Output Structure

### o3 Methodology Outputs
- `outputs/deductive/`: Deductive coding results (JSONL format)
- `outputs/inductive/`: Inductive coding results (JSONL format)
- `data/analysis_outputs/o3/`: Final merged results and reports

### Opus Methodology Outputs
- `outputs/opus_enhanced/raw_outputs/`: Raw LLM responses
- `outputs/opus_enhanced/structured_coding/`: Structured coding results
- `outputs/opus_enhanced/reliability/`: Reliability reports (Excel)
- `outputs/opus_enhanced/reports/`: Narrative reports (Markdown)

### Sonnet Methodology Outputs
- `data/analysis_outputs/sonnet/`: Consensus results and reliability metrics
- TAM/DOI framework analysis
- Cross-transcript comparative analysis

### Gemini Methodology Outputs
- `outputs/coded_segments/`: Coded transcript segments (CSV)
- `outputs/reliability_reports/`: Reliability analysis reports
- `outputs/logs/`: API call logs

### Comparative Analysis
- `data/analysis_outputs/comparative_analysis.json`: Cross-methodology comparison
- Success/failure status for each methodology
- Duration comparisons and output file counts

## 🔍 Key Features

### Multi-LLM Support
- **Claude 3.5 Sonnet**: Anthropic's latest model
- **GPT-4o**: OpenAI's latest model
- **Gemini 1.5 Pro**: Google's latest model

### Reliability Metrics
- **Krippendorff's Alpha**: Inter-coder agreement
- **Consensus Building**: Agreement-based decisions
- **Confidence Scores**: Model confidence in coding decisions

### Output Formats
- **JSON/JSONL**: Structured data outputs
- **CSV**: Tabular data for analysis
- **Excel**: Formatted reports with multiple sheets
- **Markdown**: Human-readable narrative reports

### Parallel Processing
- **Concurrent LLM Calls**: Multiple models run simultaneously
- **Batch Processing**: Efficient handling of multiple transcripts
- **Rate Limiting**: Built-in API rate limiting

## 🛠️ Configuration

### Model Configuration
Models are configured via environment variables:
```bash
# o3 Methodology
O3_CLAUDE_MODEL=claude-3-5-sonnet-20241022
O3_GPT4_MODEL=gpt-4o
O3_GEMINI_MODEL=gemini-1.5-pro

# Opus Methodology
OPUS_CLAUDE_MODEL=claude-3-5-sonnet-20241022
OPUS_GPT4_MODEL=gpt-4o
OPUS_GEMINI_MODEL=gemini-1.5-pro
```

### Sonnet Configuration
`config/sonnet_config.json` contains:
- Model specifications
- Consensus thresholds
- TAM/DOI coding schema
- Output format preferences

## 🐛 Troubleshooting

### Common Issues
1. **API Key Errors**: Ensure all API keys are set in environment variables
2. **Missing Dependencies**: Run `pip install -r requirements.txt`
3. **Transcript Not Found**: Check `data/processed/` directory
4. **Encoding Issues**: Ensure UTF-8 encoding for transcript files

### Debug Mode
```bash
# Enable debug logging
export DEBUG=1
python scripts/run_all_methodologies.py
```

### Environment Check
```bash
# Check environment setup
python scripts/run_all_methodologies.py --check-only
```

## 📈 Analysis Results

### What Each Methodology Provides

#### o3 Methodology
- **Deductive Codes**: Predefined research method codes, AI pain points, barriers
- **Inductive Codes**: Novel themes discovered during analysis
- **Reliability Metrics**: Krippendorff's alpha for inter-coder agreement
- **Theme Matrices**: Prevalence of themes across transcripts

#### Opus Methodology
- **Structured Coding**: Formal codebook-based analysis
- **Multi-LLM Comparison**: Results from all three models
- **Reliability Reports**: Inter-coder agreement statistics
- **Narrative Reports**: Human-readable analysis summaries

#### Sonnet Methodology
- **TAM/DOI Analysis**: Technology acceptance and diffusion insights
- **Consensus Results**: Agreement-based coding decisions
- **Cross-Transcript Analysis**: Comparative insights across focus groups
- **Comprehensive Metrics**: Multiple reliability and agreement measures

#### Gemini Methodology
- **Gemini-Optimized**: Results specifically from Gemini model
- **Structured Segments**: Coded transcript segments with context
- **Reliability Metrics**: Comprehensive reliability analysis
- **Batch Processing**: Efficient handling of large datasets

## 🔄 Workflow

1. **Data Preparation**: Clean raw transcripts using `batch_clean.py`
2. **Environment Setup**: Configure API keys and dependencies
3. **Methodology Selection**: Choose one or more methodologies to run
4. **Analysis Execution**: Run selected methodologies
5. **Results Review**: Examine outputs in respective directories
6. **Comparative Analysis**: Review `comparative_analysis.json` for cross-methodology insights

## 📝 Development Notes

- **Modular Design**: Each methodology is self-contained
- **Shared Utilities**: Common functionality in `src/` directory
- **Configuration-Driven**: Extensive use of configuration files
- **Logging**: Comprehensive logging for debugging and monitoring
- **Error Handling**: Robust error handling and recovery

## 🤝 Contributing

1. Follow the modular structure for new methodologies
2. Use shared utilities from `src/` directory
3. Maintain consistent output formats
4. Add comprehensive logging and error handling
5. Update configuration files for new features

## 📄 License

This project is designed for research purposes. Please ensure compliance with API usage terms for all LLM providers. 