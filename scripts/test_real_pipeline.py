#!/usr/bin/env python3
"""Test real pipeline with API calls"""

import os
import sys
from dotenv import load_dotenv
import anthropic
import openai
import google.generativeai as genai
import json
from datetime import datetime

# Load environment variables
load_dotenv()

def test_simple_analysis():
    """Test a simple analysis with each API"""
    
    test_text = "The collaboration features are excellent, but the notification system needs improvement."
    
    results = {
        "timestamp": datetime.now().isoformat(),
        "test_text": test_text,
        "api_results": {}
    }
    
    # Test Anthropic
    try:
        print("Testing Anthropic API...")
        client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        response = client.messages.create(
            model="claude-3-haiku-20240307",  # Using a simpler model for testing
            max_tokens=100,
            messages=[{
                "role": "user", 
                "content": f"Analyze this feedback and identify key themes (respond with JSON): {test_text}"
            }]
        )
        results["api_results"]["anthropic"] = {
            "status": "success",
            "response": response.content[0].text[:200]
        }
        print("✓ Anthropic API working")
    except Exception as e:
        results["api_results"]["anthropic"] = {
            "status": "error",
            "error": str(e)
        }
        print(f"✗ Anthropic error: {e}")
    
    # Test OpenAI
    try:
        print("Testing OpenAI API...")
        client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{
                "role": "user",
                "content": f"Analyze this feedback and identify key themes (respond with JSON): {test_text}"
            }],
            max_tokens=100
        )
        results["api_results"]["openai"] = {
            "status": "success",
            "response": response.choices[0].message.content[:200]
        }
        print("✓ OpenAI API working")
    except Exception as e:
        results["api_results"]["openai"] = {
            "status": "error",
            "error": str(e)
        }
        print(f"✗ OpenAI error: {e}")
    
    # Test Google
    try:
        print("Testing Google API...")
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(
            f"Analyze this feedback and identify key themes (respond with JSON): {test_text}"
        )
        results["api_results"]["google"] = {
            "status": "success",
            "response": response.text[:200]
        }
        print("✓ Google API working")
    except Exception as e:
        results["api_results"]["google"] = {
            "status": "error", 
            "error": str(e)
        }
        print(f"✗ Google error: {e}")
    
    # Save results
    output_path = "test_real_pipeline_results.json"
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\nResults saved to {output_path}")
    
    # Summary
    success_count = sum(1 for r in results["api_results"].values() if r["status"] == "success")
    print(f"\nSummary: {success_count}/3 APIs working correctly")
    
    return success_count == 3

if __name__ == "__main__":
    print("\n=== Testing Real Pipeline with Live APIs ===\n")
    success = test_simple_analysis()
    print("\n✅ All APIs tested successfully!" if success else "\n❌ Some APIs failed")
    sys.exit(0 if success else 1)