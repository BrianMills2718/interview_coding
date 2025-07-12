# {{ transcript_info.name }} Analysis Report

**Generated**: {{ report_date }}  
**Methodology**: {{ methodology }}  
**Domain**: {{ domain }} ({{ "%.1f"|format(domain_confidence * 100) }}% confidence)

## Executive Summary

Analysis of {{ total_utterances }} utterances resulted in {{ coded_utterances }} coded segments ({{ "%.1f"|format(coverage_percent) }}% coverage).

## Key Findings

### Most Common Codes
{% for code in top_codes[:5] %}
- **{{ code.code }}** ({{ code.count }} occurrences, {{ "%.1f"|format(code.percentage) }}%)
  - Example: "{{ code.example }}"
{% endfor %}

### Coverage Analysis
- Utterance Coverage: {{ "%.1f"|format(coverage_percent) }}%
- Token Coverage: {{ "%.1f"|format(token_coverage_percent) }}%

## Validation Status

{% if validation_passed %}
✅ Output validation passed
{% else %}
❌ Output validation failed
{% endif %}

{% if validation_warnings %}
### Warnings
{% for warning in validation_warnings %}
- {{ warning }}
{% endfor %}
{% endif %}

{% if recommendations %}
## Recommendations
{% for rec in recommendations %}
- {{ rec }}
{% endfor %}
{% endif %}
