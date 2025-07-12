"""
LLM API Clients for Gemini25 Methodology
Handles API calls to OpenAI, Anthropic, and Gemini for qualitative coding
"""

import os
import json
import time
from typing import Dict, List, Any, Optional
import openai
from anthropic import Anthropic
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure API clients
openai_client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
anthropic_client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))

def call_openai_api(prompt: str, model: str = "gpt-4o", temperature: float = 0.1) -> Dict[str, Any]:
    """
    Call OpenAI API for coding analysis
    
    Args:
        prompt: The prompt to send to the model
        model: Model to use (default: gpt-4o)
        temperature: Temperature for response generation
        
    Returns:
        Dictionary containing the API response
    """
    try:
        response = openai_client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are an expert qualitative researcher performing systematic coding of focus group transcripts."},
                {"role": "user", "content": prompt}
            ]
        )
        
        return {
            "success": True,
            "content": response.choices[0].message.content,
            "model": model,
            "usage": {
                "prompt_tokens": getattr(response.usage, 'prompt_tokens', 0),
                "completion_tokens": getattr(response.usage, 'completion_tokens', 0),
                "total_tokens": getattr(response.usage, 'total_tokens', 0)
            }
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "model": model
        }

def call_anthropic_api(prompt: str, model: str = "claude-3-5-sonnet-20241022", temperature: float = 0.1) -> Dict[str, Any]:
    """
    Call Anthropic API for coding analysis
    
    Args:
        prompt: The prompt to send to the model
        model: Model to use (default: claude-3-5-sonnet-20241022)
        temperature: Temperature for response generation
        
    Returns:
        Dictionary containing the API response
    """
    try:
        response = anthropic_client.messages.create(
            model=model,
            max_tokens=4000,
            temperature=temperature,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        return {
            "success": True,
            "content": response.content[0].text,
            "model": model,
            "usage": {
                "input_tokens": getattr(response.usage, 'input_tokens', 0),
                "output_tokens": getattr(response.usage, 'output_tokens', 0)
            }
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "model": model
        }

def call_gemini_api(prompt: str, model: str = "gemini-1.5-pro", temperature: float = 0.1) -> Dict[str, Any]:
    """
    Call Google Gemini API for coding analysis
    
    Args:
        prompt: The prompt to send to the model
        model: Model to use (default: gemini-1.5-pro)
        temperature: Temperature for response generation
        
    Returns:
        Dictionary containing the API response
    """
    try:
        model_instance = genai.GenerativeModel(model)
        
        response = model_instance.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=temperature,
                max_output_tokens=4000
            )
        )
        
        return {
            "success": True,
            "content": response.text,
            "model": model,
            "usage": getattr(response, 'usage_metadata', None)
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "model": model
        }

def parse_coding_response(response_content: str) -> Dict[str, Any]:
    """
    Parse the JSON response from LLM coding
    
    Args:
        response_content: Raw response content from LLM
        
    Returns:
        Parsed coding data
    """
    try:
        # Try to extract JSON from the response
        start_idx = response_content.find('{')
        end_idx = response_content.rfind('}') + 1
        
        if start_idx != -1 and end_idx != 0:
            json_str = response_content[start_idx:end_idx]
            return json.loads(json_str)
        else:
            return {
                "success": False,
                "error": "No JSON found in response",
                "raw_content": response_content
            }
    except json.JSONDecodeError as e:
        return {
            "success": False,
            "error": f"JSON parsing error: {str(e)}",
            "raw_content": response_content
        }

def save_api_log(log_data: Dict[str, Any], log_file: str):
    """
    Save API call logs for debugging and analysis
    
    Args:
        log_data: Log data to save
        log_file: Path to log file
    """
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(json.dumps(log_data, ensure_ascii=False) + '\n') 