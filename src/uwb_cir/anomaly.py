from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .features import cosine_similarity, l2_distance, total_energy


@dataclass
class AnomalyResult:
    is_anomaly: bool
    score: float
    threshold: float
    method: str


@dataclass
class BaselineAnomalyDetector:
    """Simple baseline-based CIR anomaly detector.

    The detector compares the current CIR snapshot with a baseline CIR snapshot.
    It is intended as a first implementation before using SVM, autoencoders, or CNNs.
    """

    baseline: np.ndarray
    threshold: float = 0.2
    method: str = "l2"

    def __post_init__(self) -> None:
        self.baseline = np.asarray(self.baseline, dtype=float)
        if self.baseline.ndim != 1:
            raise ValueError("baseline must be 1D")
        if self.method not in {"l2", "cosine", "energy"}:
            raise ValueError("method must be one of: l2, cosine, energy")

    def score(self, current: np.ndarray | list[float]) -> float:
        current_arr = np.asarray(current, dtype=float)
        if current_arr.shape != self.baseline.shape:
            raise ValueError("current CIR must have the same shape as baseline")

        if self.method == "l2":
            return l2_distance(current_arr, self.baseline)
        if self.method == "cosine":
            return 1.0 - cosine_similarity(current_arr, self.baseline)
        if self.method == "energy":
            base_energy = total_energy(self.baseline)
            curr_energy = total_energy(current_arr)
            if base_energy == 0:
                return curr_energy
            return abs(curr_energy - base_energy) / base_energy

        raise RuntimeError("unreachable")

    def predict(self, current: np.ndarray | list[float]) -> AnomalyResult:
        score = self.score(current)
        return AnomalyResult(
            is_anomaly=score >= self.threshold,
            score=score,
            threshold=self.threshold,
            method=self.method,
        )
