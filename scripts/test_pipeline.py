#!/usr/bin/env python3
"""
End-to-End Pipeline Test Script
Tests the complete analysis pipeline from data preparation to final outputs
"""

import json
import csv
import sys
from pathlib import Path
import pandas as pd

class PipelineTest:
    def __init__(self):
        self.test_results = []
        self.passed = 0
        self.failed = 0
    
    def test(self, name, condition, error_msg=""):
        """Run a single test"""
        if condition:
            self.test_results.append(f"✓ {name}")
            self.passed += 1
        else:
            self.test_results.append(f"✗ {name}: {error_msg}")
            self.failed += 1
    
    def test_environment(self):
        """Test environment setup"""
        print("\n[1/6] Testing Environment Setup...")
        
        # Test virtual environment
        self.test("Virtual environment active", 
                 sys.prefix.endswith('venv'),
                 "Not running in virtual environment")
        
        # Test required directories
        dirs = ['data/raw', 'data/processed', 'data/analysis_outputs']
        for dir_path in dirs:
            self.test(f"Directory {dir_path} exists", 
                     Path(dir_path).exists(),
                     f"Missing directory: {dir_path}")
        
        # Test dependencies
        try:
            import anthropic
            import openai
            import google.generativeai
            import pandas
            import krippendorff
            self.test("All required packages installed", True)
        except ImportError as e:
            self.test("All required packages installed", False, str(e))
    
    def test_data_preparation(self):
        """Test data preparation step"""
        print("\n[2/6] Testing Data Preparation...")
        
        # Test transcript exists
        transcript_path = Path("data/processed/test_transcript.txt")
        self.test("Test transcript exists", 
                 transcript_path.exists(),
                 "Missing test transcript")
        
        if transcript_path.exists():
            with open(transcript_path) as f:
                content = f.read()
                self.test("Transcript has content", len(content) > 0)
                self.test("Transcript format correct", 
                         content.startswith("[TEST_"),
                         "Invalid transcript format")
    
    def test_o3_outputs(self):
        """Test o3 methodology outputs"""
        print("\n[3/6] Testing o3 Methodology Outputs...")
        
        o3_dir = Path("data/analysis_outputs/o3")
        
        # Test deductive results
        deductive_path = o3_dir / "deductive_results.json"
        self.test("o3 deductive results exist", deductive_path.exists())
        
        if deductive_path.exists():
            try:
                with open(deductive_path) as f:
                    data = json.load(f)
                    self.test("o3 deductive JSON valid", True)
                    self.test("o3 deductive has required fields", 
                             all(k in data for k in ['transcript_id', 'codes', 'key_quotes']))
            except json.JSONDecodeError:
                self.test("o3 deductive JSON valid", False, "Invalid JSON")
        
        # Test inductive results
        inductive_path = o3_dir / "inductive_results.json"
        self.test("o3 inductive results exist", inductive_path.exists())
        
        if inductive_path.exists():
            try:
                with open(inductive_path) as f:
                    data = json.load(f)
                    self.test("o3 inductive JSON valid", True)
                    self.test("o3 inductive has emergent themes", 
                             'emergent_themes' in data and len(data['emergent_themes']) > 0)
            except json.JSONDecodeError:
                self.test("o3 inductive JSON valid", False, "Invalid JSON")
    
    def test_opus_outputs(self):
        """Test Opus methodology outputs"""
        print("\n[4/6] Testing Opus Methodology Outputs...")
        
        opus_dir = Path("data/analysis_outputs/opus")
        
        # Test analysis results
        analysis_path = opus_dir / "opus_analysis.json"
        self.test("Opus analysis results exist", analysis_path.exists())
        
        if analysis_path.exists():
            try:
                with open(analysis_path) as f:
                    data = json.load(f)
                    self.test("Opus JSON valid", True)
                    self.test("Opus has multi-LLM analysis", 
                             'multi_llm_analysis' in data)
                    self.test("Opus has consensus codes", 
                             'consensus_codes' in data and len(data['consensus_codes']) > 0)
            except json.JSONDecodeError:
                self.test("Opus JSON valid", False, "Invalid JSON")
        
        # Test narrative report
        report_path = opus_dir / "narrative_report.md"
        self.test("Opus narrative report exists", report_path.exists())
    
    def test_sonnet_outputs(self):
        """Test Sonnet methodology outputs"""
        print("\n[5/6] Testing Sonnet Methodology Outputs...")
        
        sonnet_dir = Path("data/analysis_outputs/sonnet")
        
        # Test consensus results
        consensus_path = sonnet_dir / "sonnet_consensus.json"
        self.test("Sonnet consensus results exist", consensus_path.exists())
        
        if consensus_path.exists():
            try:
                with open(consensus_path) as f:
                    data = json.load(f)
                    self.test("Sonnet JSON valid", True)
                    self.test("Sonnet has TAM analysis", 'tam_analysis' in data)
                    self.test("Sonnet has DOI analysis", 'doi_analysis' in data)
            except json.JSONDecodeError:
                self.test("Sonnet JSON valid", False, "Invalid JSON")
        
        # Test cross-transcript analysis
        cross_path = sonnet_dir / "cross_transcript_analysis.json"
        self.test("Sonnet cross-transcript analysis exists", cross_path.exists())
    
    def test_gemini_outputs(self):
        """Test Gemini methodology outputs"""
        print("\n[6/6] Testing Gemini Methodology Outputs...")
        
        gemini_dir = Path("data/analysis_outputs/gemini")
        
        # Test batch results
        batch_path = gemini_dir / "gemini_batch_results.json"
        self.test("Gemini batch results exist", batch_path.exists())
        
        if batch_path.exists():
            try:
                with open(batch_path) as f:
                    data = json.load(f)
                    self.test("Gemini JSON valid", True)
                    self.test("Gemini has coded segments", 
                             'coded_segments' in data and len(data['coded_segments']) > 0)
            except json.JSONDecodeError:
                self.test("Gemini JSON valid", False, "Invalid JSON")
        
        # Test CSV output
        csv_path = gemini_dir / "gemini_results.csv"
        self.test("Gemini CSV results exist", csv_path.exists())
        
        if csv_path.exists():
            try:
                df = pd.read_csv(csv_path)
                self.test("Gemini CSV valid", True)
                self.test("Gemini CSV has data", len(df) > 0)
            except Exception as e:
                self.test("Gemini CSV valid", False, str(e))
    
    def test_comparative_analysis(self):
        """Test comparative analysis output"""
        print("\n[Bonus] Testing Comparative Analysis...")
        
        comp_path = Path("comparative_analysis.json")
        self.test("Comparative analysis exists", comp_path.exists())
        
        if comp_path.exists():
            try:
                with open(comp_path) as f:
                    data = json.load(f)
                    self.test("Comparative JSON valid", True)
                    self.test("All methodologies included", 
                             set(data.get('methodologies_completed', [])) == 
                             {'o3', 'opus', 'sonnet', 'gemini'})
            except json.JSONDecodeError:
                self.test("Comparative JSON valid", False, "Invalid JSON")
    
    def run_all_tests(self):
        """Run complete test suite"""
        print("\n" + "="*60)
        print("QUALITATIVE ANALYSIS PIPELINE - END-TO-END TEST")
        print("="*60)
        
        self.test_environment()
        self.test_data_preparation()
        self.test_o3_outputs()
        self.test_opus_outputs()
        self.test_sonnet_outputs()
        self.test_gemini_outputs()
        self.test_comparative_analysis()
        
        print("\n" + "="*60)
        print("TEST RESULTS SUMMARY")
        print("="*60)
        
        for result in self.test_results:
            print(result)
        
        print("\n" + "-"*60)
        print(f"Total Tests: {self.passed + self.failed}")
        print(f"Passed: {self.passed}")
        print(f"Failed: {self.failed}")
        
        if self.failed == 0:
            print("\n✅ ALL TESTS PASSED! Pipeline is working correctly.")
        else:
            print(f"\n❌ {self.failed} tests failed. Please check the errors above.")
        
        return self.failed == 0

if __name__ == "__main__":
    tester = PipelineTest()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)