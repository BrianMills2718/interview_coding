"""
Adaptive Report Generation System
Generates reports based on actual findings and detected domain
"""

import json
import logging
from typing import Dict, List, Optional
from pathlib import Path
from datetime import datetime
from jinja2 import Template, Environment, FileSystemLoader

logger = logging.getLogger(__name__)

class AdaptiveReportGenerator:
    """Generates reports adapted to domain and findings"""
    
    def __init__(self, templates_dir: str = "templates/reports"):
        self.templates_dir = Path(templates_dir)
        self.templates_dir.mkdir(parents=True, exist_ok=True)
        
        # Create Jinja2 environment
        self.env = Environment(
            loader=FileSystemLoader(str(self.templates_dir)),
            trim_blocks=True,
            lstrip_blocks=True
        )
        
        # Initialize default templates if they don't exist
        self._initialize_default_templates()
    
    def generate_report(self,
                       coding_results: List[Dict],
                       domain_info: Dict,
                       coverage_metrics: Dict,
                       validation_result: Dict,
                       transcript_info: Dict,
                       methodology: str = "unknown") -> str:
        """
        Generate adaptive report based on results
        
        Args:
            coding_results: Coding results
            domain_info: Domain detection results  
            coverage_metrics: Coverage analysis
            validation_result: Validation results
            transcript_info: Basic transcript information
            methodology: Methodology name
            
        Returns:
            Generated report as string
        """
        # Determine which template to use
        template_name = self._select_template(
            coding_results, 
            domain_info, 
            coverage_metrics,
            validation_result
        )
        
        # Prepare template context
        context = self._prepare_context(
            coding_results,
            domain_info,
            coverage_metrics,
            validation_result,
            transcript_info,
            methodology
        )
        
        # Render template
        try:
            template = self.env.get_template(template_name)
            return template.render(**context)
        except Exception as e:
            logger.error(f"Error rendering template {template_name}: {e}")
            return self._generate_fallback_report(context)
    
    def _select_template(self,
                        coding_results: List[Dict],
                        domain_info: Dict,
                        coverage_metrics: Dict,
                        validation_result: Dict) -> str:
        """Select appropriate template based on results"""
        
        # Check for various conditions
        if not coding_results or coverage_metrics.get("coverage_percent", 0) == 0:
            return "empty_results.md"
        
        if domain_info.get("detected_domain") == "unknown":
            return "unknown_domain.md"
        
        if domain_info.get("confidence", 1.0) < 0.7:
            return "low_confidence.md"
        
        if not validation_result.get("is_valid", True):
            return "validation_failed.md"
        
        # Use domain-specific template if available
        domain = domain_info.get("detected_domain", "generic")
        domain_template = f"{domain}_report.md"
        
        if (self.templates_dir / domain_template).exists():
            return domain_template
        else:
            return "generic_report.md"
    
    def _prepare_context(self,
                        coding_results: List[Dict],
                        domain_info: Dict,
                        coverage_metrics: Dict,
                        validation_result: Dict,
                        transcript_info: Dict,
                        methodology: str) -> Dict:
        """Prepare context for template rendering"""
        
        # Analyze coding results
        code_summary = self._summarize_codes(coding_results)
        
        # Prepare context
        context = {
            "report_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "methodology": methodology,
            "transcript_info": transcript_info,
            "domain": domain_info.get("detected_domain", "unknown"),
            "domain_confidence": domain_info.get("confidence", 0),
            "coverage_percent": coverage_metrics.get("coverage_percent", 0),
            "token_coverage_percent": coverage_metrics.get("token_coverage_percent", 0),
            "total_utterances": coverage_metrics.get("total_utterances", 0),
            "coded_utterances": coverage_metrics.get("coded_utterances", 0),
            "validation_passed": validation_result.get("is_valid", False),
            "validation_warnings": validation_result.get("warnings", []),
            "validation_errors": validation_result.get("errors", []),
            "code_summary": code_summary,
            "top_codes": code_summary.get("top_codes", []),
            "code_categories": code_summary.get("categories", {}),
            "recommendations": self._generate_recommendations(
                coding_results, domain_info, coverage_metrics, validation_result
            )
        }
        
        return context
    
    def _summarize_codes(self, coding_results: List[Dict]) -> Dict:
        """Summarize coding results"""
        from collections import Counter
        
        # Count codes
        code_counts = Counter(r.get("code") for r in coding_results if r.get("code"))
        
        # Group by category if available
        categories = {}
        for result in coding_results:
            code = result.get("code", "")
            if "::" in code:
                category, _ = code.split("::", 1)
                if category not in categories:
                    categories[category] = []
                categories[category].append(result)
        
        # Get top codes with examples
        top_codes = []
        for code, count in code_counts.most_common(10):
            # Find example quote
            example = next(
                (r.get("quote", "") for r in coding_results if r.get("code") == code),
                ""
            )
            top_codes.append({
                "code": code,
                "count": count,
                "percentage": (count / len(coding_results) * 100) if coding_results else 0,
                "example": example[:100] + "..." if len(example) > 100 else example
            })
        
        return {
            "total_codes": len(coding_results),
            "unique_codes": len(code_counts),
            "top_codes": top_codes,
            "categories": {cat: len(results) for cat, results in categories.items()}
        }
    
    def _generate_recommendations(self,
                                coding_results: List[Dict],
                                domain_info: Dict,
                                coverage_metrics: Dict,
                                validation_result: Dict) -> List[str]:
        """Generate contextual recommendations"""
        recommendations = []
        
        # Add validation recommendations
        recommendations.extend(validation_result.get("recommendations", []))
        
        # Add coverage-based recommendations
        coverage = coverage_metrics.get("coverage_percent", 0)
        if coverage < 50:
            recommendations.append("Consider reviewing uncoded segments for missed insights")
        
        # Add domain-based recommendations
        if domain_info.get("confidence", 0) < 0.8:
            recommendations.append("Low domain confidence - consider manual review of coding appropriateness")
        
        # Remove duplicates and return
        return list(set(recommendations))
    
    def _initialize_default_templates(self):
        """Create default templates if they don't exist"""
        
        # Generic report template
        generic_template = """# {{ transcript_info.name }} Analysis Report

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
"""
        
        # Empty results template
        empty_template = """# Analysis Report - No Results

**Generated**: {{ report_date }}  
**Methodology**: {{ methodology }}

## Summary

No codes were identified in this transcript.

### Possible Reasons:
1. Domain mismatch - detected domain "{{ domain }}" may not match content
2. Codebook incompatibility - current codes may not apply to this content  
3. Technical issue - review logs for errors

### Domain Analysis
- Detected Domain: {{ domain }}
- Confidence: {{ "%.1f"|format(domain_confidence * 100) }}%

## Recommendations
- Review transcript content manually
- Consider using emergent coding approach
- Verify domain detection accuracy
"""
        
        # Unknown domain template
        unknown_domain_template = """# Analysis Report - Unknown Domain

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
"""
        
        # Save templates
        templates = {
            "generic_report.md": generic_template,
            "empty_results.md": empty_template,
            "unknown_domain.md": unknown_domain_template
        }
        
        for filename, content in templates.items():
            template_path = self.templates_dir / filename
            if not template_path.exists():
                template_path.write_text(content)
    
    def _generate_fallback_report(self, context: Dict) -> str:
        """Generate basic report if template rendering fails"""
        return f"""# Analysis Report

**Generated**: {context.get('report_date')}
**Methodology**: {context.get('methodology')}

## Summary
- Domain: {context.get('domain')}
- Coverage: {context.get('coverage_percent', 0):.1f}%
- Total Codes: {context.get('code_summary', {}).get('total_codes', 0)}

## Status
Unable to generate full report due to template error.
Please check logs for details.
"""