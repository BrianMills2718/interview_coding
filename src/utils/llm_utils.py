"""
LLM Utilities Module
Provides unified interface for different LLM providers (Claude, GPT-4, Gemini)
"""

import os
import json
import logging
from typing import Dict, Any, Optional
from pathlib import Path
from dotenv import load_dotenv
import anthropic
import openai
import google.generativeai as genai

# Load environment variables
env_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(env_path)

logger = logging.getLogger(__name__)

class LLMClient:
    """Unified client for different LLM providers"""
    
    def __init__(self):
        self.claude_client = None
        self.openai_client = None
        self.gemini_client = None
        
        # Initialize clients based on available API keys
        self._init_claude()
        self._init_openai()
        self._init_gemini()
    
    def _init_claude(self):
        """Initialize Anthropic Claude client"""
        api_key = os.getenv('ANTHROPIC_API_KEY')
        if api_key:
            try:
                self.claude_client = anthropic.Anthropic(api_key=api_key)
                logger.info("Claude client initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Claude client: {e}")
        else:
            logger.warning("ANTHROPIC_API_KEY not found")
    
    def _init_openai(self):
        """Initialize OpenAI client"""
        api_key = os.getenv('OPENAI_API_KEY')
        if api_key:
            try:
                self.openai_client = openai.OpenAI(api_key=api_key)
                logger.info("OpenAI client initialized")
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI client: {e}")
        else:
            logger.warning("OPENAI_API_KEY not found")
    
    def _init_gemini(self):
        """Initialize Google Gemini client"""
        api_key = os.getenv('GOOGLE_API_KEY')
        if api_key:
            try:
                genai.configure(api_key=api_key)
                # Use model from environment or default to newer version
                model_name = os.getenv('GEMINI_MODEL', 'gemini-1.5-flash')
                self.gemini_client = genai.GenerativeModel(model_name)
                logger.info("Gemini client initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Gemini client: {e}")
        else:
            logger.warning("GOOGLE_API_KEY not found")
    
    def query_model(self, model: str, prompt: str, **kwargs) -> str:
        """
        Query a specific LLM model
        
        Args:
            model: Model identifier (claude-3-sonnet, gpt-4, gemini-pro, o3, etc)
            prompt: Input prompt
            **kwargs: Additional parameters
            
        Returns:
            Model response as string
        """
        try:
            if model.startswith('claude'):
                return self._query_claude(model, prompt, **kwargs)
            elif model.startswith('gpt') or model == 'o3':
                return self._query_openai(model, prompt, **kwargs)
            elif model.startswith('gemini'):
                return self._query_gemini(model, prompt, **kwargs)
            else:
                raise ValueError(f"Unknown model: {model}")
        except Exception as e:
            logger.error(f"Error querying {model}: {e}")
            raise
    
    def _query_claude(self, model: str, prompt: str, **kwargs) -> str:
        """Query Claude model"""
        if not self.claude_client:
            raise RuntimeError("Claude client not initialized")
        
        try:
            response = self.claude_client.messages.create(
                model=model,
                max_tokens=kwargs.get('max_tokens', 4000),
                temperature=kwargs.get('temperature', 0.1),
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text
        except Exception as e:
            logger.error(f"Claude API error: {e}")
            raise
    
    def _query_openai(self, model: str, prompt: str, **kwargs) -> str:
        """Query OpenAI model"""
        if not self.openai_client:
            raise RuntimeError("OpenAI client not initialized")
        
        try:
            response = self.openai_client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise
    
    def _query_gemini(self, model: str, prompt: str, **kwargs) -> str:
        """Query Gemini model"""
        if not self.gemini_client:
            raise RuntimeError("Gemini client not initialized")
        
        try:
            response = self.gemini_client.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=kwargs.get('max_tokens', 4000),
                    temperature=kwargs.get('temperature', 0.1)
                )
            )
            return response.text
        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            raise
    
    def get_available_models(self) -> Dict[str, bool]:
        """Get list of available models and their status"""
        return {
            'claude-sonnet-4-20250514': self.claude_client is not None,
            'o3': self.openai_client is not None,
            'gemini-2.5-pro': self.gemini_client is not None
        } 