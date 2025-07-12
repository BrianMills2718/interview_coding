"""Report generator for Opus methodology.

Creates structured narrative reports in Markdown format.
"""

import pandas as pd
from typing import Dict, List, Any
from pathlib import Path
from datetime import datetime
from collections import defaultdict


class ReportGenerator:
    """Generate narrative reports from coding results."""
    
    def __init__(self, codebook):
        self.codebook = codebook
    
    def create_narrative_report(self, coding_results: List[Dict[str, Any]], 
                              reliability_report: Dict[str, Any],
                              consensus_analysis: Dict[str, Any],
                              transcript_id: str) -> str:
        """Create comprehensive narrative report in Markdown."""
        
        # Header
        report = f"""# AI Needs Assessment for RAND Research Methods
*Generated: {datetime.now().strftime('%B %d, %Y')}*

## Executive Summary
This analysis synthesized insights from focus group transcripts to understand current research methods and opportunities for AI enhancement.

**Inter-rater Reliability**: Krippendorff's α = {reliability_report.get('overall_alpha', 0):.3f}

"""
        
        # Key Findings by Category
        report += "## Key Findings by Category\n\n"
        
        # Group codes by category
        category_findings = defaultdict(list)
        
        for result in coding_results:
            if 'codes_found' in result:
                for code_id, instances in result['codes_found'].items():
                    code_def = self.codebook.get_code_by_id(code_id)
                    if code_def:
                        category_findings[code_def.category].append({
                            'code_id': code_id,
                            'label': code_def.label,
                            'instances': instances
                        })
        
        # Process each category
        for category_id, codes in category_findings.items():
            category_info = self.codebook.categories.get(category_id, {})
            category_name = category_info.get('name', category_id.title())
            
            report += f"### {category_name}\n"
            
            # Count unique codes found
            unique_codes = {code['code_id'] for code in codes}
            report += f"**{len(unique_codes)} unique codes identified**\n\n"
            
            # Process each code
            for code in codes:
                code_id = code['code_id']
                label = code['label']
                
                # Count total instances across all models
                total_instances = sum(len(code['instances']) for code in codes if code['code_id'] == code_id)
                
                report += f"**{code_id}: {label}** (Found in {total_instances} instances)\n"
                report += f"- {self.codebook.get_code_by_id(code_id).description}\n"
                
                # Get exemplar quotes
                exemplar_quotes = []
                for code_data in codes:
                    if code_data['code_id'] == code_id:
                        for instance in code_data['instances']:
                            if 'quote' in instance and 'speaker' in instance:
                                exemplar_quotes.append(f'"{instance["quote"]}" - {instance["speaker"]}')
                
                if exemplar_quotes:
                    report += f"- Example: {exemplar_quotes[0]}\n"
                
                report += "\n"
        
        # Consensus Analysis
        if consensus_analysis and 'consensus_codes' in consensus_analysis:
            report += "## Consensus Analysis\n\n"
            report += "Codes with high agreement across models:\n\n"
            
            for code_id, consensus_data in consensus_analysis['consensus_codes'].items():
                consensus_level = consensus_data['consensus_level']
                code_def = self.codebook.get_code_by_id(code_id)
                
                if code_def:
                    report += f"**{code_id}: {code_def.label}** ({consensus_level})\n"
                    
                    # Show evidence
                    evidence = consensus_data['evidence']
                    if evidence['quotes']:
                        report += f"- Evidence: {evidence['quotes'][0]['quote']} - {evidence['quotes'][0]['speaker']}\n"
                    
                    report += "\n"
        
        # Reliability Details
        if reliability_report:
            report += "## Reliability Details\n\n"
            
            # Category-level reliability
            if 'category_summary' in reliability_report:
                report += "### Agreement by Category\n\n"
                for category in reliability_report['category_summary']:
                    report += f"**{category['Category']}**: {category['Agreement_Rate_mean']:.3f} mean agreement "
                    report += f"(range: {category['Agreement_Rate_min']:.3f} - {category['Agreement_Rate_max']:.3f})\n\n"
            
            # Code-level reliability
            if 'code_level' in reliability_report:
                report += "### Agreement by Code\n\n"
                for code_data in reliability_report['code_level']:
                    report += f"**{code_data['Code']}: {code_data['Label']}** - {code_data['Agreement_Rate']:.3f} agreement\n"
                
                report += "\n"
        
        # Methodology
        report += """## Methodology

This analysis used multiple large language models (Claude, GPT-4, Gemini) to code focus group transcripts according to a formal codebook. Inter-rater reliability was calculated using Krippendorff's alpha to ensure coding consistency.

### Analysis Steps:
1. **Transcript Preparation**: Raw transcripts were cleaned and formatted for analysis
2. **Multi-Model Coding**: Three LLMs independently coded each transcript
3. **Reliability Assessment**: Agreement rates and Krippendorff's alpha calculated
4. **Consensus Analysis**: High-agreement codes identified for confidence
5. **Narrative Synthesis**: Key themes and findings compiled into structured report

"""
        
        return report
    
    def save_report(self, report_content: str, transcript_id: str, output_dir: Path) -> None:
        """Save narrative report to file."""
        output_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = output_dir / f"final_report_{transcript_id}_{timestamp}.md"
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        print(f"Saved narrative report to {output_path}")


def create_summary_report(all_reports: List[Dict[str, Any]], output_dir: Path) -> None:
    """Create a summary report across all transcripts."""
    
    # Collect summary statistics
    total_transcripts = len(all_reports)
    total_alpha = sum(report.get('reliability', {}).get('overall_alpha', 0) for report in all_reports)
    avg_alpha = total_alpha / total_transcripts if total_transcripts > 0 else 0
    
    # Count unique codes found
    all_codes = set()
    for report in all_reports:
        if 'consensus_codes' in report:
            all_codes.update(report['consensus_codes'].keys())
    
    # Create summary report
    summary = f"""# Summary Report: AI Needs Assessment for RAND Research Methods
*Generated: {datetime.now().strftime('%B %d, %Y')}*

## Overview
Analysis of {total_transcripts} focus group transcripts using multi-model qualitative coding.

## Key Statistics
- **Total Transcripts Analyzed**: {total_transcripts}
- **Average Krippendorff's α**: {avg_alpha:.3f}
- **Unique Codes Identified**: {len(all_codes)}

## Reliability Summary
- **High Reliability** (α ≥ 0.8): {sum(1 for report in all_reports if report.get('reliability', {}).get('overall_alpha', 0) >= 0.8)} transcripts
- **Moderate Reliability** (0.6 ≤ α < 0.8): {sum(1 for report in all_reports if 0.6 <= report.get('reliability', {}).get('overall_alpha', 0) < 0.8)} transcripts
- **Low Reliability** (α < 0.6): {sum(1 for report in all_reports if report.get('reliability', {}).get('overall_alpha', 0) < 0.6)} transcripts

## Most Common Codes
"""
    
    # Count code frequency across transcripts
    code_counts = defaultdict(int)
    for report in all_reports:
        if 'consensus_codes' in report:
            for code_id in report['consensus_codes'].keys():
                code_counts[code_id] += 1
    
    # Sort by frequency
    sorted_codes = sorted(code_counts.items(), key=lambda x: x[1], reverse=True)
    
    for code_id, count in sorted_codes[:10]:  # Top 10
        summary += f"- **{code_id}**: Found in {count}/{total_transcripts} transcripts\n"
    
    summary += f"""
## Recommendations
Based on the analysis of {total_transcripts} transcripts with an average reliability of {avg_alpha:.3f}, the following recommendations are made:

1. **Focus on High-Agreement Themes**: Prioritize codes with strong consensus across models
2. **Validate Key Findings**: Conduct manual review of high-prevalence codes
3. **Consider Context**: Review exemplar quotes to understand nuance and context
4. **Iterate Codebook**: Refine coding schema based on emergent themes

## Next Steps
- Manual validation of automated coding results
- Stakeholder review of key themes and recommendations
- Development of AI implementation roadmap based on identified opportunities
"""
    
    # Save summary report
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    summary_path = output_dir / f"summary_report_{timestamp}.md"
    
    with open(summary_path, 'w', encoding='utf-8') as f:
        f.write(summary)
    
    print(f"Saved summary report to {summary_path}") 