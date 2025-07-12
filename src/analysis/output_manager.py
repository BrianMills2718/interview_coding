import json
import csv
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
import yaml

class CodingResult:
    def __init__(self, model_name: str, coding_type: str, codes: Dict[str, Any], 
                 confidence: float, transcript_id: str):
        self.model_name = model_name
        self.coding_type = coding_type
        self.codes = codes
        self.confidence = confidence
        self.transcript_id = transcript_id
    
    def dict(self):
        return {
            'model_name': self.model_name,
            'coding_type': self.coding_type,
            'codes': self.codes,
            'confidence': self.confidence,
            'transcript_id': self.transcript_id,
            'timestamp': datetime.now().isoformat()
        }

class OutputManager:
    def __init__(self, output_base_path: str = "data/analysis_outputs"):
        self.output_base_path = Path(output_base_path)
        self.output_base_path.mkdir(parents=True, exist_ok=True)
        
        # Create subdirectories
        self.paths = {
            'raw_coding': self.output_base_path / "raw_coding",
            'consensus': self.output_base_path / "consensus",
            'reliability': self.output_base_path / "reliability",
            'reports': self.output_base_path / "reports",
            'validation': self.output_base_path / "validation",
            'visualizations': self.output_base_path / "visualizations"
        }
        
        for path in self.paths.values():
            path.mkdir(exist_ok=True)
    
    def save_individual_coding_result(self, result: CodingResult, transcript_id: str):
        """Save individual LLM coding result"""
        filename = f"{transcript_id}_{result.model_name}_{result.coding_type}.json"
        filepath = self.paths['raw_coding'] / filename
        
        with open(filepath, 'w') as f:
            json.dump(result.dict(), f, indent=2, default=str)
    
    def save_consensus_result(self, consensus_data: Dict[str, Any], transcript_id: str):
        """Save consensus coding result"""
        filename = f"{transcript_id}_consensus.json"
        filepath = self.paths['consensus'] / filename
        
        with open(filepath, 'w') as f:
            json.dump(consensus_data, f, indent=2, default=str)
    
    def save_reliability_analysis(self, reliability_data: Dict[str, Any], analysis_id: str):
        """Save reliability analysis results"""
        filename = f"{analysis_id}_reliability.json"
        filepath = self.paths['reliability'] / filename
        
        with open(filepath, 'w') as f:
            json.dump(reliability_data, f, indent=2, default=str)
    
    def generate_cross_transcript_analysis(self, all_consensus_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate analysis across all transcripts"""
        
        # Aggregate code frequencies
        code_frequencies = {}
        code_confidences = {}
        
        for result in all_consensus_results:
            transcript_id = result.get('transcript_id', 'unknown')
            consensus_codes = result.get('consensus_codes', {})
            
            for code, data in consensus_codes.items():
                if code not in code_frequencies:
                    code_frequencies[code] = {'present': 0, 'total': 0, 'confidences': []}
                
                code_frequencies[code]['total'] += 1
                if data.get('present', False):
                    code_frequencies[code]['present'] += 1
                
                code_frequencies[code]['confidences'].append(data.get('confidence', 0.0))
        
        # Calculate aggregate statistics
        aggregate_stats = {}
        for code, stats in code_frequencies.items():
            aggregate_stats[code] = {
                'frequency': stats['present'] / stats['total'] if stats['total'] > 0 else 0,
                'avg_confidence': np.mean(stats['confidences']) if stats['confidences'] else 0,
                'present_in_n_transcripts': stats['present'],
                'total_transcripts': stats['total']
            }
        
        # Generate insights
        insights = self._generate_insights(aggregate_stats, all_consensus_results)
        
        cross_analysis = {
            'analysis_date': datetime.now().isoformat(),
            'total_transcripts': len(all_consensus_results),
            'code_frequencies': aggregate_stats,
            'insights': insights,
            'methodological_summary': self._generate_methodological_summary(all_consensus_results)
        }
        
        return cross_analysis
    
    def _generate_insights(self, aggregate_stats: Dict[str, Any], all_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate key insights from cross-transcript analysis"""
        
        insights = {
            'most_common_codes': [],
            'least_common_codes': [],
            'high_confidence_codes': [],
            'low_confidence_codes': [],
            'consensus_quality': {},
            'theoretical_implications': []
        }
        
        # Sort codes by frequency
        sorted_by_freq = sorted(aggregate_stats.items(), key=lambda x: x[1]['frequency'], reverse=True)
        insights['most_common_codes'] = sorted_by_freq[:5]
        insights['least_common_codes'] = sorted_by_freq[-5:]
        
        # High/low confidence codes
        high_conf = [(code, stats) for code, stats in aggregate_stats.items() if stats['avg_confidence'] > 0.8]
        low_conf = [(code, stats) for code, stats in aggregate_stats.items() if stats['avg_confidence'] < 0.5]
        
        insights['high_confidence_codes'] = high_conf
        insights['low_confidence_codes'] = low_conf
        
        # Theoretical implications based on TAM/DOI
        tam_patterns = self._analyze_tam_patterns(aggregate_stats)
        doi_patterns = self._analyze_doi_patterns(aggregate_stats)
        
        insights['theoretical_implications'] = {
            'tam_patterns': tam_patterns,
            'doi_patterns': doi_patterns
        }
        
        return insights
    
    def _analyze_tam_patterns(self, aggregate_stats: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze patterns related to Technology Acceptance Model"""
        
        tam_codes = {
            'perceived_usefulness': ['BENEFIT_EFFICIENCY', 'BENEFIT_CAPABILITY', 'BENEFIT_QUALITY'],
            'perceived_ease_of_use': ['BARRIER_TRAINING', 'AI_USAGE_WRITING'],
            'perceived_barriers': ['BARRIER_QUALITY', 'BARRIER_ACCESS', 'CONCERN_VALIDITY'],
            'usage_behavior': ['AI_USAGE_CODING', 'AI_USAGE_ANALYSIS', 'AI_USAGE_WRITING']
        }
        
        tam_analysis = {}
        for construct, codes in tam_codes.items():
            construct_scores = []
            for code in codes:
                if code in aggregate_stats:
                    construct_scores.append(aggregate_stats[code]['frequency'])
            
            if construct_scores:
                tam_analysis[construct] = {
                    'avg_frequency': np.mean(construct_scores),
                    'individual_codes': {code: aggregate_stats.get(code, {}).get('frequency', 0) for code in codes}
                }
        
        return tam_analysis
    
    def _analyze_doi_patterns(self, aggregate_stats: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze patterns related to Diffusion of Innovation"""
        
        doi_codes = {
            'relative_advantage': ['BENEFIT_EFFICIENCY', 'BENEFIT_CAPABILITY', 'PAIN_ANALYSIS'],
            'complexity': ['BARRIER_TRAINING', 'CONCERN_VALIDITY'],
            'compatibility': ['METHODS_MIXED', 'ORG_SUPPORT'],
            'observability': ['AI_USAGE_CODING', 'AI_USAGE_ANALYSIS'],
            'trialability': ['BARRIER_ACCESS', 'ORG_BARRIERS']
        }
        
        doi_analysis = {}
        for construct, codes in doi_codes.items():
            construct_scores = []
            for code in codes:
                if code in aggregate_stats:
                    construct_scores.append(aggregate_stats[code]['frequency'])
            
            if construct_scores:
                doi_analysis[construct] = {
                    'avg_frequency': np.mean(construct_scores),
                    'individual_codes': {code: aggregate_stats.get(code, {}).get('frequency', 0) for code in codes}
                }
        
        return doi_analysis
    
    def _generate_methodological_summary(self, all_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate methodological summary"""
        return {
            'total_transcripts_analyzed': len(all_results),
            'consensus_threshold': 0.7,  # Default threshold
            'models_used': ['claude-3-sonnet', 'gpt-4', 'gemini-pro'],
            'coding_schema': 'TAM/DOI-based qualitative coding',
            'reliability_metrics': 'Krippendorff\'s alpha and agreement ratios'
        }
    
    def generate_final_report(self, cross_analysis: Dict[str, Any], 
                            all_consensus_results: List[Dict[str, Any]], 
                            reliability_summary: Dict[str, Any]) -> str:
        """Generate comprehensive final report"""
        
        report_data = {
            'executive_summary': self._generate_executive_summary(cross_analysis),
            'methodology': self._generate_methodology_section(reliability_summary),
            'findings': self._generate_findings_section(cross_analysis),
            'recommendations': self._generate_recommendations(cross_analysis),
            'limitations': self._generate_limitations(reliability_summary),
            'appendices': {
                'detailed_code_frequencies': cross_analysis['code_frequencies'],
                'reliability_metrics': reliability_summary,
                'quality_assessment': self._generate_quality_assessment(all_consensus_results)
            }
        }
        
        # Save as JSON
        report_path = self.paths['reports'] / f"final_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_path, 'w') as f:
            json.dump(report_data, f, indent=2, default=str)
        
        # Generate human-readable report
        readable_report = self._generate_readable_report(report_data)
        readable_path = self.paths['reports'] / f"final_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        with open(readable_path, 'w') as f:
            f.write(readable_report)
        
        return str(readable_path)
    
    def _generate_executive_summary(self, cross_analysis: Dict[str, Any]) -> str:
        """Generate executive summary"""
        
        insights = cross_analysis.get('insights', {})
        most_common = insights.get('most_common_codes', [])
        
        summary = f"""
        # Executive Summary
        
        Analysis of {cross_analysis.get('total_transcripts', 0)} focus group transcripts reveals key patterns in AI adoption among RAND researchers.
        
        ## Key Findings:
        
        **Most Common Themes:**
        """
        
        for code, stats in most_common:
            summary += f"- {code}: {stats['frequency']:.1%} of transcripts\n"
        
        tam_patterns = insights.get('theoretical_implications', {}).get('tam_patterns', {})
        if tam_patterns:
            summary += f"""
        **Technology Acceptance Patterns:**
        - Perceived Usefulness: {tam_patterns.get('perceived_usefulness', {}).get('avg_frequency', 0):.1%}
        - Usage Behavior: {tam_patterns.get('usage_behavior', {}).get('avg_frequency', 0):.1%}
        - Perceived Barriers: {tam_patterns.get('perceived_barriers', {}).get('avg_frequency', 0):.1%}
        """
        
        return summary
    
    def _generate_methodology_section(self, reliability_summary: Dict[str, Any]) -> str:
        """Generate methodology section"""
        return f"""
        # Methodology
        
        This analysis employed a multi-LLM consensus approach using Claude 3 Sonnet, GPT-4, and Gemini Pro.
        
        **Reliability Metrics:**
        - Overall Krippendorff's Alpha: {reliability_summary.get('overall_alpha', 'N/A')}
        - Average Agreement Ratio: {reliability_summary.get('avg_agreement_ratio', 'N/A')}
        - Consensus Threshold: 70%
        
        **Coding Schema:**
        Based on Technology Acceptance Model (TAM) and Diffusion of Innovation (DOI) frameworks.
        """
    
    def _generate_findings_section(self, cross_analysis: Dict[str, Any]) -> str:
        """Generate findings section"""
        insights = cross_analysis.get('insights', {})
        
        findings = """
        # Findings
        
        ## Code Frequency Analysis
        """
        
        code_freqs = cross_analysis.get('code_frequencies', {})
        for code, stats in sorted(code_freqs.items(), key=lambda x: x[1]['frequency'], reverse=True):
            findings += f"- {code}: {stats['frequency']:.1%} ({stats['present_in_n_transcripts']}/{stats['total_transcripts']} transcripts)\n"
        
        return findings
    
    def _generate_recommendations(self, cross_analysis: Dict[str, Any]) -> str:
        """Generate recommendations section"""
        return """
        # Recommendations
        
        Based on the analysis of AI adoption patterns among RAND researchers:
        
        1. **Training and Support**: Address identified barriers through targeted training programs
        2. **Quality Assurance**: Implement validation processes for AI-assisted analysis
        3. **Organizational Support**: Provide institutional backing for AI adoption initiatives
        4. **Mixed Methods**: Encourage integration of AI with traditional qualitative methods
        """
    
    def _generate_limitations(self, reliability_summary: Dict[str, Any]) -> str:
        """Generate limitations section"""
        return f"""
        # Limitations
        
        1. **Sample Size**: Limited to focus group participants from RAND
        2. **Reliability**: Overall alpha of {reliability_summary.get('overall_alpha', 'N/A')} indicates moderate agreement
        3. **Context Specificity**: Findings may not generalize to other research organizations
        4. **LLM Limitations**: Analysis dependent on current LLM capabilities and biases
        """
    
    def _generate_quality_assessment(self, all_consensus_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate quality assessment"""
        return {
            'total_consensus_decisions': len(all_consensus_results),
            'avg_confidence_score': np.mean([r.get('avg_confidence', 0) for r in all_consensus_results]),
            'consensus_quality_distribution': {
                'high_confidence': len([r for r in all_consensus_results if r.get('avg_confidence', 0) > 0.8]),
                'medium_confidence': len([r for r in all_consensus_results if 0.5 <= r.get('avg_confidence', 0) <= 0.8]),
                'low_confidence': len([r for r in all_consensus_results if r.get('avg_confidence', 0) < 0.5])
            }
        }
    
    def _generate_readable_report(self, report_data: Dict[str, Any]) -> str:
        """Generate human-readable markdown report"""
        report = ""
        report += report_data.get('executive_summary', '')
        report += "\n\n"
        report += report_data.get('methodology', '')
        report += "\n\n"
        report += report_data.get('findings', '')
        report += "\n\n"
        report += report_data.get('recommendations', '')
        report += "\n\n"
        report += report_data.get('limitations', '')
        
        return report
    
    def save_validation_data(self, validation_data: Dict[str, Any], validation_type: str):
        """Save validation data (member checking, expert review)"""
        filename = f"{validation_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = self.paths['validation'] / filename
        
        with open(filepath, 'w') as f:
            json.dump(validation_data, f, indent=2, default=str)
    
    def export_for_human_review(self, consensus_results: List[Dict[str, Any]]) -> str:
        """Export data in format suitable for human review"""
        
        # Create Excel file with multiple sheets
        excel_path = self.paths['validation'] / f"human_review_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        
        with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
            
            # Summary sheet
            summary_data = []
            for result in consensus_results:
                transcript_id = result.get('transcript_id', 'unknown')
                consensus_codes = result.get('consensus_codes', {})
                
                for code, data in consensus_codes.items():
                    if data.get('present', False):
                        summary_data.append({
                            'Transcript': transcript_id,
                            'Code': code,
                            'Confidence': data.get('confidence', 0.0),
                            'Agreement_Ratio': data.get('agreement_ratio', 0.0)
                        })
            
            summary_df = pd.DataFrame(summary_data)
            summary_df.to_excel(writer, sheet_name='Summary', index=False)
            
            # Detailed quotes sheet
            quotes_data = []
            for result in consensus_results:
                transcript_id = result.get('transcript_id', 'unknown')
                consensus_quotes = result.get('consensus_quotes', {})
                
                for code, quotes in consensus_quotes.items():
                    for quote in quotes:
                        quotes_data.append({
                            'Transcript': transcript_id,
                            'Code': code,
                            'Quote': quote.get('text', ''),
                            'Speaker': quote.get('speaker', ''),
                            'Timestamp': quote.get('timestamp', ''),
                            'Source_Model': quote.get('source_model', '')
                        })
            
            quotes_df = pd.DataFrame(quotes_data)
            quotes_df.to_excel(writer, sheet_name='Quotes', index=False)
        
        return str(excel_path) 