# Optimization Action Plan

## Phase 1: Individual Methodology Optimization

### O3 Methodology Optimization

#### Immediate Fixes
- [ ] Fix timeout issue in deductive_runner.py
  - Add batch processing instead of individual utterance processing
  - Implement configurable timeout with graceful termination
- [ ] Update model configurations to use working models
- [ ] Add progress logging to track which transcript/utterance is being processed

#### Code Changes Needed
1. **Batch Processing** (`llm_utils.py`)
   ```python
   def process_utterances_batch(utterances, model_func, batch_size=10):
       # Process multiple utterances in single API call
   ```

2. **Configurable Prompts** (`config/o3_prompts.yaml`)
   ```yaml
   domains:
     research_methods:
       prompt: "Analyzing research methods focus group..."
     collaboration_tools:
       prompt: "Analyzing collaboration tool feedback..."
   ```

3. **Progress Tracking** (`deductive_runner.py`)
   ```python
   logger.info(f"Processing {transcript_id}: {current}/{total} utterances")
   ```

### Opus Methodology Optimization

#### Immediate Fixes
- [ ] Fix JSON parsing to handle multiple objects and extra text
- [ ] Fix Excel generation error handling
- [ ] Ensure all three LLMs actually run

#### Code Changes Needed
1. **Robust JSON Extraction** (`enhanced_analyzer.py`)
   ```python
   def extract_json_from_response(response):
       # Use regex to find JSON blocks
       # Validate before parsing
       # Handle multiple JSON objects
   ```

2. **Excel Error Handling**
   ```python
   try:
       save_to_excel(data)
   except:
       logger.warning("Excel failed, falling back to CSV")
       save_to_csv(data)
   ```

### Sonnet Methodology Optimization

#### Immediate Fixes
- [ ] Fix multi-model execution (currently only GPT-4 runs)
- [ ] Fix reliability calculations when multiple models run
- [ ] Make report templates domain-aware

#### Code Changes Needed
1. **Multi-Model Execution** (`run_sonnet_analysis.py`)
   ```python
   models = ['claude-3-5-sonnet', 'gpt-4', 'gemini-1.5-pro']
   results = {}
   for model in models:
       if check_model_available(model):
           results[model] = run_analysis(model, transcript)
   ```

2. **Domain-Aware Reporting**
   ```python
   def generate_report(results, domain_type):
       template = load_template(f"reports/{domain_type}_template.md")
       return template.render(results)
   ```

### Gemini Methodology Optimization

#### Immediate Fixes
- [ ] Fix serialization error with UsageMetadata
- [ ] Investigate why only 2/19 segments were processed
- [ ] Add completion verification

#### Code Changes Needed
1. **Fix Serialization** (`main.py`)
   ```python
   def serialize_gemini_response(response):
       # Extract only serializable parts
       return {
           'text': response.text,
           'candidates': [c.content for c in response.candidates]
       }
   ```

2. **Coverage Tracking**
   ```python
   total_segments = len(transcript_segments)
   processed_segments = 0
   for segment in transcript_segments:
       result = process_segment(segment)
       processed_segments += 1
       logger.info(f"Progress: {processed_segments}/{total_segments}")
   ```

## Phase 2: Standardization Across Methodologies

### 1. Unified Configuration Structure
Create `config/unified_config.yaml`:
```yaml
models:
  claude:
    primary: "claude-3-5-sonnet-20241022"
    fallback: "claude-3-haiku-20240307"
  openai:
    primary: "gpt-4-turbo-preview"
    fallback: "gpt-3.5-turbo"
  gemini:
    primary: "gemini-1.5-pro"
    fallback: "gemini-1.5-flash"

processing:
  batch_size: 10
  timeout_seconds: 300
  max_retries: 3
  
domains:
  - research_methods
  - collaboration_tools
  - customer_feedback
  - user_interviews
```

### 2. Shared Utilities Library
Create `src/shared/`:
- `json_utils.py` - Robust JSON extraction and validation
- `model_utils.py` - Model availability checking and fallbacks
- `progress_utils.py` - Unified progress tracking
- `error_utils.py` - Standardized error handling

### 3. Common Output Format
```python
@dataclass
class AnalysisResult:
    methodology: str
    transcript_id: str
    timestamp: datetime
    coverage: float  # % of transcript analyzed
    segments_processed: int
    segments_total: int
    codes_found: Dict[str, List[CodeInstance]]
    reliability_metrics: ReliabilityMetrics
    errors: List[Error]
    warnings: List[Warning]
```

## Phase 3: Testing Framework

### 1. Unit Tests for Each Methodology
```python
# tests/test_o3.py
def test_batch_processing():
    # Test that batching works correctly
    
def test_timeout_handling():
    # Test graceful timeout

def test_empty_transcript():
    # Test edge case handling
```

### 2. Integration Tests
```python
# tests/test_integration.py
def test_all_methodologies_same_transcript():
    # Run all 4 on same content
    # Compare coverage and findings
    
def test_domain_switching():
    # Test with different domain configs
```

### 3. Performance Benchmarks
```python
# tests/benchmark.py
def benchmark_methodology(methodology, transcript_sizes=[10, 50, 100, 500]):
    # Measure time, API calls, memory usage
```

## Phase 4: Domain Adaptation System

### 1. Content Type Detection
```python
def detect_content_type(transcript):
    # Use keywords and patterns to identify domain
    # Return confidence scores for each domain
```

### 2. Dynamic Code Loading
```python
def load_codes_for_domain(domain):
    # Load appropriate codebook
    # Validate against transcript
```

### 3. Prompt Template System
```python
class PromptTemplate:
    def __init__(self, domain):
        self.domain = domain
        self.base_prompt = load_prompt(domain)
    
    def generate(self, context):
        return self.base_prompt.format(**context)
```

## Implementation Timeline

### Week 1: Emergency Fixes
- Fix all broken API calls
- Update model names
- Basic error handling

### Week 2: Individual Optimization
- Implement batch processing for O3
- Fix JSON parsing for Opus
- Fix multi-model for Sonnet
- Fix serialization for Gemini

### Week 3: Standardization
- Create shared utilities
- Implement unified config
- Standardize outputs

### Week 4: Testing
- Write unit tests
- Run integration tests
- Performance benchmarking

### Week 5: Domain Adaptation
- Build content detection
- Create prompt templates
- Test on multiple domains

## Success Metrics

### For Each Methodology
1. **Coverage**: >90% of transcript segments analyzed
2. **Reliability**: Inter-coder agreement >0.70
3. **Performance**: <60s for 100-segment transcript
4. **Robustness**: 95% success rate across different content types
5. **Accuracy**: 85% agreement with human coding (when available)

### For Combined System
1. **Best-of-breed**: Outperform any individual methodology
2. **Flexibility**: Handle 5+ different domain types
3. **Scalability**: Process 1000+ transcripts in batch
4. **Maintainability**: Easy to add new domains/models
5. **Transparency**: Clear audit trail of decisions

## Risk Mitigation

### Technical Risks
1. **API Changes**: Use versioned APIs, test regularly
2. **Model Deprecation**: Always have fallback models
3. **Rate Limits**: Implement proper backoff and queuing
4. **Data Loss**: Save intermediate results frequently

### Quality Risks
1. **Bias**: Use multiple models to reduce single-model bias
2. **Overfitting**: Test on diverse content types
3. **Drift**: Regular validation against human coding
4. **Inconsistency**: Standardize all processing steps

This plan provides a systematic approach to optimizing each methodology while building toward a unified, best-of-breed system.