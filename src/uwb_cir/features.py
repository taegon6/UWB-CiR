from __future__ import annotations

import numpy as np


def as_array(cir: np.ndarray | list[float]) -> np.ndarray:
    """Convert a CIR sequence to a 1D float numpy array."""
    arr = np.asarray(cir, dtype=float)
    if arr.ndim != 1:
        raise ValueError("CIR must be a 1D sequence")
    return arr


def l2_distance(a: np.ndarray | list[float], b: np.ndarray | list[float]) -> float:
    """Return the Euclidean distance between two CIR snapshots."""
    x = as_array(a)
    y = as_array(b)
    if x.shape != y.shape:
        raise ValueError("CIR arrays must have the same length")
    return float(np.linalg.norm(x - y))


def cosine_similarity(a: np.ndarray | list[float], b: np.ndarray | list[float]) -> float:
    """Return cosine similarity between two CIR snapshots."""
    x = as_array(a)
    y = as_array(b)
    if x.shape != y.shape:
        raise ValueError("CIR arrays must have the same length")
    denom = np.linalg.norm(x) * np.linalg.norm(y)
    if denom == 0:
        return 0.0
    return float(np.dot(x, y) / denom)


def total_energy(cir: np.ndarray | list[float]) -> float:
    """Return total CIR energy."""
    x = as_array(cir)
    return float(np.sum(x ** 2))


def peak_count(cir: np.ndarray | list[float], threshold_ratio: float = 0.5) -> int:
    """Count local peaks higher than max(cir) * threshold_ratio."""
    x = as_array(cir)
    if x.size < 3:
        return 0
    threshold = float(np.max(x) * threshold_ratio)
    peaks = (x[1:-1] > x[:-2]) & (x[1:-1] > x[2:]) & (x[1:-1] >= threshold)
    return int(np.sum(peaks))
