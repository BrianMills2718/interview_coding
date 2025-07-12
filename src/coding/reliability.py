"""Inter-LLM reliability utilities."""

from __future__ import annotations

from itertools import combinations
from typing import Dict, List

import numpy as np
from sklearn.metrics import cohen_kappa_score  # noqa: F401 (may use later)
import krippendorff  # noqa: F401 (optional dependency)

from src.models.llm_interface import CodingResult


class ReliabilityAnalyzer:
    """Calculate agreement metrics between LLM coders."""

    def calculate_inter_llm_reliability(self, coding_results: List[CodingResult]) -> Dict[str, float]:
        reliability_scores: Dict[str, float] = {}
        models = [r.model_name for r in coding_results]
        for model_a, model_b in combinations(models, 2):
            # Placeholder logic: 1.0 if identical codes else 0.0 average
            res_a = next(r for r in coding_results if r.model_name == model_a)
            res_b = next(r for r in coding_results if r.model_name == model_b)
            overlap = set(res_a.codes.keys()) & set(res_b.codes.keys())
            if not overlap:
                reliability_scores[f"{model_a}_{model_b}"] = 0.0
                continue
            matches = [1.0 if res_a.codes[c] == res_b.codes[c] else 0.0 for c in overlap]
            reliability_scores[f"{model_a}_{model_b}"] = float(np.mean(matches))
        return reliability_scores

    def calculate_krippendorff_alpha(self, all_results: List[List[CodingResult]]) -> float:
        # TODO: implement full Krippendorff alpha across coders and units
        raise NotImplementedError 