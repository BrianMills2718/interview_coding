from __future__ import annotations

"""LLM interface definitions for the Sonnet qualitative analysis system."""

from abc import ABC, abstractmethod
from typing import Dict, Any, List
from datetime import datetime
import os

from pydantic import BaseModel
from dotenv import load_dotenv

import anthropic
import openai
import google.generativeai as genai

load_dotenv()

# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

class CodingResult(BaseModel):
    """Normalized result returned by each LLM coder."""

    model_name: str
    transcript_id: str
    timestamp: str
    codes: Dict[str, Any]
    confidence_scores: Dict[str, float]
    quotes: List[Dict[str, str]]
    reasoning: str


# ---------------------------------------------------------------------------
# Abstract base class
# ---------------------------------------------------------------------------

class LLMCoder(ABC):
    """Abstract base for a model-specific coder wrapper."""

    def __init__(self, model_name: str):
        self.model_name = model_name

    @abstractmethod
    def code_transcript(self, transcript: str, codebook: Dict[str, Any], prompt_template: str) -> CodingResult:  # noqa: D401,E501
        """Return a CodingResult for *transcript* using *codebook* and *prompt_template*."""


# ---------------------------------------------------------------------------
# Concrete implementations (place-holders for now)
# ---------------------------------------------------------------------------

class ClaudeCoder(LLMCoder):
    def __init__(self, model_name: str = "claude-3-5-sonnet-20241022") -> None:
        super().__init__(model_name)
        self.client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    def code_transcript(self, transcript: str, codebook: Dict[str, Any], prompt_template: str) -> CodingResult:  # noqa: D401,E501
        # TODO: implement real call. For now, raise so we notice unimplemented usage.
        raise NotImplementedError("ClaudeCoder.code_transcript not implemented yet")


class OpenAICoder(LLMCoder):
    def __init__(self, model_name: str = "gpt-4-turbo-preview") -> None:
        super().__init__(model_name)
        self.client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def code_transcript(self, transcript: str, codebook: Dict[str, Any], prompt_template: str) -> CodingResult:  # noqa: D401,E501
        raise NotImplementedError("OpenAICoder.code_transcript not implemented yet")


class GeminiCoder(LLMCoder):
    def __init__(self, model_name: str = "gemini-pro") -> None:
        super().__init__(model_name)
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        self.model = genai.GenerativeModel(model_name)

    def code_transcript(self, transcript: str, codebook: Dict[str, Any], prompt_template: str) -> CodingResult:  # noqa: D401,E501
        raise NotImplementedError("GeminiCoder.code_transcript not implemented yet") 