"""Codebook data classes and helper utilities."""

from __future__ import annotations

from datetime import datetime
from typing import List

import yaml
from pydantic import BaseModel

# ---------------------------------------------------------------------------
# Code definitions
# ---------------------------------------------------------------------------

class CodeDefinition(BaseModel):
    code_name: str
    description: str
    operational_definition: str
    examples: List[str]
    exclusion_criteria: List[str]
    theoretical_basis: str


class Codebook(BaseModel):
    version: str
    created_date: str
    theoretical_framework: str
    codes: List[CodeDefinition]
    reliability_threshold: float = 0.8

    # ---------------------------------------------------------------------
    # Persistence helpers
    # ---------------------------------------------------------------------
    def save(self, filepath: str) -> None:
        with open(filepath, "w", encoding="utf-8") as f:
            yaml.dump(self.dict(), f, default_flow_style=False, allow_unicode=True)

    @classmethod
    def load(cls, filepath: str) -> "Codebook":
        with open(filepath, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        return cls(**data)


# ---------------------------------------------------------------------------
# Example initial codebook (placeholder – edit in config/codebook.yaml)
# ---------------------------------------------------------------------------

INITIAL_CODEBOOK = Codebook(
    version="1.0",
    created_date=datetime.now().isoformat(),
    theoretical_framework="Technology Acceptance Model + Diffusion of Innovation Theory",
    codes=[],
) 