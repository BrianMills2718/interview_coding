# Analysis Report - Unknown Domain

**Generated**: {{ report_date }}  
**Methodology**: {{ methodology }}

## Summary

The domain of this transcript could not be determined with confidence.

### Analysis Results
- Total Utterances: {{ total_utterances }}
- Coding Attempted: {{ "Yes" if code_summary.total_codes > 0 else "No" }}

{% if code_summary.total_codes > 0 %}
### Emergent Themes
{% for code in top_codes[:10] %}
- {{ code.code }} ({{ code.count }} occurrences)
{% endfor %}
{% endif %}

## Recommendations
1. Review transcript for domain-specific vocabulary
2. Consider adding new domain profile if this is a common transcript type
3. Use emergent coding to identify themes
