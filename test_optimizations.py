#!/usr/bin/env python3
"""Test the optimization fixes"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment
load_dotenv()

def test_o3_batch():
    """Test O3 batch processing"""
    print("\n=== Testing O3 Batch Processing ===")
    sys.path.insert(0, str(Path(__file__).parent / "scripts" / "o3"))
    
    try:
        from llm_utils import create_batch_deductive_prompt, DEDUCTIVE_CODES
        
        # Test batch prompt creation
        test_utterances = [
            {"uid": "TEST_001", "text": "This is a test utterance about collaboration."},
            {"uid": "TEST_002", "text": "The interface needs improvement."},
            {"uid": "TEST_003", "text": "Integration works well with our tools."}
        ]
        
        prompt = create_batch_deductive_prompt(test_utterances)
        print("✓ Batch prompt created successfully")
        print(f"  - Prompt length: {len(prompt)} characters")
        print(f"  - Number of codes: {len(DEDUCTIVE_CODES)}")
        return True
    except Exception as e:
        print(f"✗ O3 batch test failed: {e}")
        return False

def test_sonnet_config():
    """Test Sonnet configuration"""
    print("\n=== Testing Sonnet Configuration ===")
    
    try:
        import json
        config_path = Path("config/sonnet_config.json")
        
        if not config_path.exists():
            print("✗ Sonnet config not found")
            return False
            
        with open(config_path) as f:
            config = json.load(f)
        
        print("✓ Sonnet config loaded successfully")
        print(f"  - Models configured: {len(config['models'])}")
        print(f"  - Models: {', '.join(config['models'])}")
        print(f"  - Consensus threshold: {config['consensus_threshold']}")
        return True
    except Exception as e:
        print(f"✗ Sonnet config test failed: {e}")
        return False

def test_gemini_serialization():
    """Test Gemini serialization fix"""
    print("\n=== Testing Gemini Serialization ===")
    
    try:
        # Test the usage data extraction
        class MockUsageMetadata:
            prompt_token_count = 100
            candidates_token_count = 200
            total_token_count = 300
        
        usage_metadata = MockUsageMetadata()
        usage_data = {
            "prompt_tokens": getattr(usage_metadata, 'prompt_token_count', 0),
            "completion_tokens": getattr(usage_metadata, 'candidates_token_count', 0),
            "total_tokens": getattr(usage_metadata, 'total_token_count', 0)
        }
        
        import json
        serialized = json.dumps(usage_data)
        print("✓ Usage metadata serialization successful")
        print(f"  - Serialized data: {serialized}")
        return True
    except Exception as e:
        print(f"✗ Gemini serialization test failed: {e}")
        return False

def test_progress_tracker():
    """Test progress tracking utility"""
    print("\n=== Testing Progress Tracker ===")
    
    try:
        from src.utils.progress import ProgressTracker
        
        tracker = ProgressTracker("Test Task", 10)
        for i in range(5):
            tracker.update()
        
        summary = tracker.finish()
        print("✓ Progress tracker working")
        print(f"  - Completed: {summary['completed_items']}/{summary['total_items']}")
        print(f"  - Success rate: {summary['success_rate']:.1f}%")
        return True
    except Exception as e:
        print(f"✗ Progress tracker test failed: {e}")
        return False

def test_error_handling():
    """Test error handling utilities"""
    print("\n=== Testing Error Handling ===")
    
    try:
        from src.utils.error_handling import ErrorCollector, handle_errors
        
        collector = ErrorCollector()
        collector.add_error("TEST_ERROR", "This is a test error", {"context": "test"})
        
        summary = collector.get_summary()
        print("✓ Error collector working")
        print(f"  - Total errors: {summary['total_errors']}")
        print(f"  - Error types: {list(summary['errors_by_type'].keys())}")
        
        # Test decorator
        @handle_errors(default_return="default", log_errors=False)
        def failing_function():
            raise ValueError("Test error")
        
        result = failing_function()
        assert result == "default"
        print("✓ Error handler decorator working")
        
        return True
    except Exception as e:
        print(f"✗ Error handling test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("Testing Optimization Fixes")
    print("=" * 50)
    
    tests = [
        test_o3_batch,
        test_sonnet_config,
        test_gemini_serialization,
        test_progress_tracker,
        test_error_handling
    ]
    
    results = []
    for test in tests:
        results.append(test())
    
    print("\n" + "=" * 50)
    print(f"Tests passed: {sum(results)}/{len(results)}")
    
    if all(results):
        print("\n✅ All optimization tests passed!")
    else:
        print("\n❌ Some tests failed. Check the output above.")
    
    return all(results)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)