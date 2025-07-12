"""Async analysis pipeline coordinating multiple LLM coders."""

from __future__ import annotations

import asyncio
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

import numpy as np

from src.models.llm_interface import LLMCoder, ClaudeCoder, OpenAICoder, GeminiCoder, CodingResult
from src.coding.codebook import Codebook
from src.coding.reliability import ReliabilityAnalyzer


class AnalysisPipeline:
    def __init__(self, codebook_path: str):
        self.codebook = Codebook.load(codebook_path)
        self.coders: List[LLMCoder] = [
            ClaudeCoder(),
            OpenAICoder(),
            GeminiCoder(),
        ]
        self.reliability_analyzer = ReliabilityAnalyzer()
        self.results_storage: Dict[str, Any] = {}
        self.current_transcript: str = ""

    async def process_transcript(self, transcript_id: str, transcript_text: str) -> Dict[str, Any]:
        self.current_transcript = transcript_text
        coding_tasks = [
            asyncio.create_task(self._code_with_llm(c, transcript_id, transcript_text))
            for c in self.coders
        ]
        coding_results = await asyncio.gather(*coding_tasks)
        reliability = self.reliability_analyzer.calculate_inter_llm_reliability(coding_results)
        result = {
            "transcript_id": transcript_id,
            "timestamp": datetime.now().isoformat(),
            "individual_results": [r.dict() for r in coding_results],
            "reliability_scores": reliability,
        }
        self.results_storage[transcript_id] = result
        return result

    async def _code_with_llm(self, coder: LLMCoder, transcript_id: str, transcript_text: str) -> CodingResult:
        prompt_template = """{{codebook}}\n\nTRANSCRIPT:\n{{transcript}}"""
        return coder.code_transcript(transcript_text, self.codebook.dict(), prompt_template) 