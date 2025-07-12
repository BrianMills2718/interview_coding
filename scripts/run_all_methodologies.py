#!/usr/bin/env python3
"""
Master Script for Running All Four LLM Methodologies
o3, Opus, Sonnet, and Gemini methodologies for comparative analysis

This script runs all four methodologies on the same transcripts to enable
comparative analysis of different LLM approaches to qualitative research.
"""

import os
import sys
import json
import logging
import subprocess
from pathlib import Path
from datetime import datetime
import argparse
from typing import Dict, List, Any
from concurrent.futures import ThreadPoolExecutor, as_completed

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('all_methodologies_analysis.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class MethodologyRunner:
    """Master runner for all four methodologies"""
    
    def __init__(self, transcript_dir: str = "data/processed"):
        self.transcript_dir = Path(transcript_dir)
        self.results = {}
        self.start_time = None
        
        # Define methodology configurations
        self.methodologies = {
            'o3': {
                'name': 'o3 Methodology',
                'description': 'Deductive and inductive coding with union merge logic',
                'script_dir': 'scripts/o3',
                'main_scripts': ['deductive_runner.py', 'inductive_runner.py'],
                'output_dir': 'data/analysis_outputs/o3',
                'status': 'ready'
            },
            'opus': {
                'name': 'Opus Methodology', 
                'description': 'Multi-LLM analysis with formal coding schema',
                'script_dir': 'scripts/opus',
                'main_scripts': ['enhanced_analyzer.py'],
                'output_dir': 'data/analysis_outputs/opus',
                'status': 'ready'
            },
            'sonnet': {
                'name': 'Sonnet Methodology',
                'description': 'Multi-LLM consensus with TAM/DOI framework',
                'script_dir': 'scripts/sonnet',
                'main_scripts': ['run_sonnet_analysis.py'],
                'output_dir': 'data/analysis_outputs/sonnet',
                'status': 'ready'
            },
            'gemini': {
                'name': 'Gemini Methodology',
                'description': 'Gemini-focused analysis with reliability metrics',
                'script_dir': 'scripts/gemini25',
                'main_scripts': ['main.py'],
                'output_dir': 'data/analysis_outputs/gemini',
                'status': 'ready'
            }
        }
    
    def check_environment(self) -> Dict[str, bool]:
        """Check environment and dependencies for all methodologies"""
        logger.info("Checking environment for all methodologies...")
        
        environment_status = {}
        
        # Check API keys
        api_keys = {
            'ANTHROPIC_API_KEY': os.getenv('ANTHROPIC_API_KEY'),
            'OPENAI_API_KEY': os.getenv('OPENAI_API_KEY'),
            'GOOGLE_API_KEY': os.getenv('GOOGLE_API_KEY')
        }
        
        for key, value in api_keys.items():
            environment_status[key] = bool(value)
            if value:
                logger.info(f"[OK] {key} found")
            else:
                logger.warning(f"[MISSING] {key} not found")
        
        # Check transcript directory
        if self.transcript_dir.exists():
            transcript_files = list(self.transcript_dir.glob('*.txt')) + list(self.transcript_dir.glob('*.csv'))
            environment_status['transcripts_available'] = len(transcript_files) > 0
            logger.info(f"[OK] Found {len(transcript_files)} transcript files")
        else:
            environment_status['transcripts_available'] = False
            logger.error(f"[ERROR] Transcript directory not found: {self.transcript_dir}")
        
        # Check methodology scripts
        for method, config in self.methodologies.items():
            script_dir = Path(config['script_dir'])
            if script_dir.exists():
                # Check if main scripts exist
                scripts_exist = all(
                    (script_dir / script).exists() 
                    for script in config['main_scripts']
                )
                environment_status[f'{method}_scripts'] = scripts_exist
                if scripts_exist:
                    logger.info(f"[OK] {method} scripts found")
                else:
                    logger.warning(f"[MISSING] {method} scripts missing")
            else:
                environment_status[f'{method}_scripts'] = False
                logger.error(f"[ERROR] {method} script directory not found")
        
        return environment_status
    
    def run_methodology(self, method: str) -> Dict[str, Any]:
        """Run a specific methodology"""
        if method not in self.methodologies:
            raise ValueError(f"Unknown methodology: {method}")
        
        config = self.methodologies[method]
        logger.info(f"Running {config['name']}...")
        
        start_time = datetime.now()
        result = {
            'methodology': method,
            'name': config['name'],
            'start_time': start_time.isoformat(),
            'status': 'running',
            'output': '',
            'error': None
        }
        
        try:
            # Create output directory
            output_dir = Path(config['output_dir'])
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Run the appropriate script based on methodology
            if method == 'o3':
                result = self._run_o3_methodology(result)
            elif method == 'opus':
                result = self._run_opus_methodology(result)
            elif method == 'sonnet':
                result = self._run_sonnet_methodology(result)
            elif method == 'gemini':
                result = self._run_gemini_methodology(result)
            
            end_time = datetime.now()
            result['end_time'] = end_time.isoformat()
            result['duration'] = str(end_time - start_time)
            result['status'] = 'completed'
            
            logger.info(f"[SUCCESS] {config['name']} completed successfully")
            
        except Exception as e:
            result['status'] = 'failed'
            result['error'] = str(e)
            logger.error(f"[ERROR] {config['name']} failed: {e}")
        
        return result
    
    def _run_o3_methodology(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Run o3 methodology"""
        script_dir = Path(self.methodologies['o3']['script_dir'])
        
        # Run deductive analysis
        deductive_cmd = [
            sys.executable, str(script_dir / 'deductive_runner.py'),
            '--transcript-dir', str(self.transcript_dir),
            '--output-dir', self.methodologies['o3']['output_dir']
        ]
        
        deductive_result = subprocess.run(
            deductive_cmd, 
            capture_output=True, 
            text=True, 
            cwd=Path.cwd()
        )
        
        if deductive_result.returncode != 0:
            raise RuntimeError(f"Deductive analysis failed: {deductive_result.stderr}")
        
        # Run inductive analysis
        inductive_cmd = [
            sys.executable, str(script_dir / 'inductive_runner.py'),
            '--transcript-dir', str(self.transcript_dir),
            '--output-dir', self.methodologies['o3']['output_dir']
        ]
        
        inductive_result = subprocess.run(
            inductive_cmd, 
            capture_output=True, 
            text=True, 
            cwd=Path.cwd()
        )
        
        if inductive_result.returncode != 0:
            raise RuntimeError(f"Inductive analysis failed: {inductive_result.stderr}")
        
        result['output'] = f"Deductive: {deductive_result.stdout}\nInductive: {inductive_result.stdout}"
        return result
    
    def _run_opus_methodology(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Run Opus methodology"""
        script_dir = Path(self.methodologies['opus']['script_dir'])
        
        cmd = [
            sys.executable, str(script_dir / 'enhanced_analyzer.py'),
            '--transcript-dir', str(self.transcript_dir),
            '--output-dir', self.methodologies['opus']['output_dir']
        ]
        
        process_result = subprocess.run(
            cmd, 
            capture_output=True, 
            text=True, 
            cwd=Path.cwd()
        )
        
        if process_result.returncode != 0:
            raise RuntimeError(f"Opus analysis failed: {process_result.stderr}")
        
        result['output'] = process_result.stdout
        return result
    
    def _run_sonnet_methodology(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Run Sonnet methodology"""
        script_dir = Path(self.methodologies['sonnet']['script_dir'])
        
        cmd = [
            sys.executable, str(script_dir / 'run_sonnet_analysis.py'),
            '--transcript-dir', str(self.transcript_dir),
            '--config', 'config/sonnet_config.json'
        ]
        
        process_result = subprocess.run(
            cmd, 
            capture_output=True, 
            text=True, 
            cwd=Path.cwd()
        )
        
        if process_result.returncode != 0:
            raise RuntimeError(f"Sonnet analysis failed: {process_result.stderr}")
        
        result['output'] = process_result.stdout
        return result
    
    def _run_gemini_methodology(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Run Gemini methodology"""
        script_dir = Path(self.methodologies['gemini']['script_dir'])
        
        cmd = [
            sys.executable, str(script_dir / 'main.py'),
            '--transcript-dir', str(self.transcript_dir),
            '--output-dir', self.methodologies['gemini']['output_dir']
        ]
        
        process_result = subprocess.run(
            cmd, 
            capture_output=True, 
            text=True, 
            cwd=Path.cwd()
        )
        
        if process_result.returncode != 0:
            raise RuntimeError(f"Gemini analysis failed: {process_result.stderr}")
        
        result['output'] = process_result.stdout
        return result
    
    def run_all_methodologies(self, methods: List[str] = None) -> Dict[str, Any]:
        """Run all or specified methodologies"""
        if methods is None:
            methods = list(self.methodologies.keys())
        
        logger.info(f"Running methodologies: {methods}")
        self.start_time = datetime.now()
        
        all_results = {}
        
        with ThreadPoolExecutor() as executor:
            futures = {
                executor.submit(self.run_methodology, method): method
                for method in methods
            }
            
            for future in as_completed(futures):
                method = futures[future]
                try:
                    result = future.result()
                    all_results[method] = result
                except Exception as e:
                    logger.error(f"Error running {method}: {e}")
                    all_results[method] = {
                        'methodology': method,
                        'name': self.methodologies[method]['name'],
                        'start_time': datetime.now().isoformat(),
                        'status': 'failed',
                        'output': '',
                        'error': str(e)
                    }
        
        # Generate comparative summary
        summary = self._generate_comparative_summary(all_results)
        
        # Save results
        self._save_results(all_results, summary)
        
        return {
            'methodologies': all_results,
            'summary': summary,
            'total_duration': str(datetime.now() - self.start_time)
        }
    
    def _generate_comparative_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comparative summary of all methodologies"""
        summary = {
            'total_methodologies': len(results),
            'successful_methodologies': sum(1 for r in results.values() if r['status'] == 'completed'),
            'failed_methodologies': sum(1 for r in results.values() if r['status'] == 'failed'),
            'methodology_comparison': {},
            'recommendations': []
        }
        
        # Compare methodologies
        for method, result in results.items():
            summary['methodology_comparison'][method] = {
                'status': result['status'],
                'duration': result.get('duration', 'N/A'),
                'output_files': self._count_output_files(method)
            }
        
        # Generate recommendations
        successful_methods = [m for m, r in results.items() if r['status'] == 'completed']
        if len(successful_methods) > 1:
            summary['recommendations'].append(
                "Multiple methodologies completed successfully. Consider comparative analysis."
            )
        elif len(successful_methods) == 1:
            summary['recommendations'].append(
                f"Only {successful_methods[0]} completed successfully. Review other methodologies."
            )
        else:
            summary['recommendations'].append(
                "No methodologies completed successfully. Check environment and dependencies."
            )
        
        return summary
    
    def _count_output_files(self, method: str) -> int:
        """Count output files for a methodology"""
        output_dir = Path(self.methodologies[method]['output_dir'])
        if output_dir.exists():
            return len(list(output_dir.rglob('*')))
        return 0
    
    def _save_results(self, results: Dict[str, Any], summary: Dict[str, Any]):
        """Save all results to file"""
        output_data = {
            'timestamp': datetime.now().isoformat(),
            'methodologies': results,
            'summary': summary,
            'total_duration': str(datetime.now() - self.start_time)
        }
        
        output_file = Path('data/analysis_outputs/comparative_analysis.json')
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w') as f:
            json.dump(output_data, f, indent=2, default=str)
        
        logger.info(f"Results saved to: {output_file}")

def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(description='Run All LLM Methodologies')
    parser.add_argument('--transcript-dir', default='data/processed',
                       help='Directory containing transcript files')
    parser.add_argument('--methods', nargs='+', 
                       choices=['o3', 'opus', 'sonnet', 'gemini'],
                       help='Specific methodologies to run (default: all)')
    parser.add_argument('--check-only', action='store_true',
                       help='Only check environment, don\'t run analysis')
    
    args = parser.parse_args()
    
    print("="*60)
    print("LLM METHODOLOGIES COMPARATIVE ANALYSIS")
    print("="*60)
    
    # Initialize runner
    runner = MethodologyRunner(args.transcript_dir)
    
    # Check environment
    env_status = runner.check_environment()
    
    if not env_status.get('transcripts_available', False):
        logger.error("No transcripts available. Please ensure transcript files exist.")
        return
    
    if args.check_only:
        print("\nEnvironment Check Complete:")
        for key, status in env_status.items():
            print(f"  {'✓' if status else '✗'} {key}")
        return
    
    # Run methodologies
    if args.methods:
        methods_to_run = args.methods
        print(f"\nRunning specified methodologies: {methods_to_run}")
    else:
        methods_to_run = None
        print("\nRunning all methodologies...")
    
    try:
        results = runner.run_all_methodologies(methods_to_run)
        
        # Print summary
        print("\n" + "="*60)
        print("ANALYSIS COMPLETE")
        print("="*60)
        print(f"Total duration: {results['total_duration']}")
        print(f"Successful methodologies: {results['summary']['successful_methodologies']}")
        print(f"Failed methodologies: {results['summary']['failed_methodologies']}")
        
        print("\nMethodology Results:")
        for method, result in results['methodologies'].items():
            status_icon = "✓" if result['status'] == 'completed' else "✗"
            print(f"  {status_icon} {result['name']}: {result['status']}")
            if result.get('duration'):
                print(f"    Duration: {result['duration']}")
        
        print(f"\nResults saved to: data/analysis_outputs/comparative_analysis.json")
        print("="*60)
        
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        print(f"\nAnalysis failed: {e}")

if __name__ == "__main__":
    main() 