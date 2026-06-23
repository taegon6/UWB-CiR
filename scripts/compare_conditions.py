from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from uwb_cir.anomaly import BaselineAnomalyDetector
from uwb_cir.cir_io import load_cir_csv, mean_baseline


METHODS = ("l2", "cosine", "energy")


@dataclass
class ScoreStats:
    mean: float
    max: float
    std: float
    min: float


def load_cir_matrix(path: Path) -> np.ndarray:
    if not path.exists():
        raise FileNotFoundError(f"missing real CSV file: {path}")
    _, cir = load_cir_csv(path)
    if len(cir) == 0:
        raise ValueError(f"CSV has no CIR rows: {path}")
    return cir


def score_matrix(baseline: np.ndarray, cir: np.ndarray, method: str) -> np.ndarray:
    detector = BaselineAnomalyDetector(baseline=baseline, threshold=0.0, method=method)
    return np.asarray([detector.score(row) for row in cir], dtype=float)


def summarize(scores: np.ndarray) -> ScoreStats:
    return ScoreStats(
        mean=float(np.mean(scores)),
        max=float(np.max(scores)),
        std=float(np.std(scores)),
        min=float(np.min(scores)),
    )


def suggested_threshold(normal_scores: np.ndarray, condition_scores: list[np.ndarray]) -> float:
    normal_max = float(np.max(normal_scores))
    condition_mins = [float(np.min(scores)) for scores in condition_scores if len(scores) > 0]
    separated_mins = [value for value in condition_mins if value > normal_max]
    if separated_mins:
        return (normal_max + min(separated_mins)) / 2.0
    return float(np.mean(normal_scores) + (3.0 * np.std(normal_scores)))


def separation_label(normal_scores: np.ndarray, condition_scores: np.ndarray, threshold: float) -> str:
    normal_max = float(np.max(normal_scores))
    condition_min = float(np.min(condition_scores))
    condition_mean = float(np.mean(condition_scores))

    if condition_min > normal_max:
        return "clear"
    if condition_mean > threshold:
        return "partial"
    return "overlap"


def print_method_report(
    method: str,
    normal_scores: np.ndarray,
    static_scores: np.ndarray,
    moving_scores: np.ndarray,
) -> None:
    threshold = suggested_threshold(normal_scores, [static_scores, moving_scores])
    groups = {
        "normal_empty": normal_scores,
        "cat_static": static_scores,
        "cat_moving": moving_scores,
    }

    print(f"\nmethod={method}")
    print(f"suggested_threshold={threshold:.6f}")
    for name, scores in groups.items():
        stats = summarize(scores)
        if name == "normal_empty":
            separation = "baseline"
        else:
            separation = separation_label(normal_scores, scores, threshold)
        print(
            f"{name}: mean={stats.mean:.6f}, max={stats.max:.6f}, "
            f"std={stats.std:.6f}, separation={separation}"
        )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Compare DW3000 CIR anomaly scores across real lab conditions"
    )
    parser.add_argument("--normal", type=Path, default=Path("data/raw/normal_empty.csv"))
    parser.add_argument("--cat-static", type=Path, default=Path("data/raw/cat_static.csv"))
    parser.add_argument("--cat-moving", type=Path, default=Path("data/raw/cat_moving.csv"))
    args = parser.parse_args()

    normal = load_cir_matrix(args.normal)
    cat_static = load_cir_matrix(args.cat_static)
    cat_moving = load_cir_matrix(args.cat_moving)

    baseline = mean_baseline(normal)
    for name, cir in {"cat_static": cat_static, "cat_moving": cat_moving}.items():
        if cir.shape[1] != baseline.shape[0]:
            raise ValueError(
                f"{name} CIR length ({cir.shape[1]}) does not match "
                f"normal baseline length ({baseline.shape[0]})"
            )

    for method in METHODS:
        normal_scores = score_matrix(baseline, normal, method)
        static_scores = score_matrix(baseline, cat_static, method)
        moving_scores = score_matrix(baseline, cat_moving, method)
        print_method_report(method, normal_scores, static_scores, moving_scores)


if __name__ == "__main__":
    main()
