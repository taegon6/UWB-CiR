from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from uwb_cir.anomaly import BaselineAnomalyDetector
from uwb_cir.camera_trigger import make_camera_event
from uwb_cir.cir_io import load_cir_csv, mean_baseline


def synthetic_cir(length: int = 128, anomaly: bool = False) -> np.ndarray:
    x = np.linspace(-3.0, 3.0, length)
    base = np.exp(-(x ** 2))
    noise = np.random.default_rng(42).normal(0, 0.01, length)
    cir = base + noise
    if anomaly:
        cir[80:90] += 0.25
    return cir


def run_demo() -> None:
    baseline = synthetic_cir(anomaly=False)
    detector = BaselineAnomalyDetector(baseline=baseline, threshold=0.2, method="l2")

    normal = synthetic_cir(anomaly=False)
    abnormal = synthetic_cir(anomaly=True)

    for name, cir in [("normal", normal), ("abnormal", abnormal)]:
        result = detector.predict(cir)
        print(f"{name}: score={result.score:.6f}, anomaly={result.is_anomaly}")
        if result.is_anomaly:
            event = make_camera_event(reason="uwb_cir_anomaly", score=result.score)
            print(event)


def run_from_csv(input_path: Path, baseline_rows: int, threshold: float, method: str) -> None:
    _, cir = load_cir_csv(input_path)
    if len(cir) <= baseline_rows:
        raise ValueError("CSV must contain more rows than baseline_rows")

    baseline = mean_baseline(cir[:baseline_rows])
    detector = BaselineAnomalyDetector(baseline=baseline, threshold=threshold, method=method)

    for idx, snapshot in enumerate(cir[baseline_rows:], start=baseline_rows):
        result = detector.predict(snapshot)
        print(f"row={idx}, score={result.score:.6f}, anomaly={result.is_anomaly}")
        if result.is_anomaly:
            event = make_camera_event(reason=f"uwb_cir_anomaly_row_{idx}", score=result.score)
            print(event)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run UWB CIR anomaly detection")
    parser.add_argument("--demo", action="store_true", help="Run with synthetic CIR data")
    parser.add_argument("--input", type=Path, help="Input CIR CSV file")
    parser.add_argument("--baseline-rows", type=int, default=10, help="Rows used to build baseline")
    parser.add_argument("--threshold", type=float, default=0.2, help="Anomaly threshold")
    parser.add_argument("--method", choices=["l2", "cosine", "energy"], default="l2")
    args = parser.parse_args()

    if args.demo:
        run_demo()
        return
    if args.input is None:
        parser.error("Use --demo or provide --input")
    run_from_csv(args.input, args.baseline_rows, args.threshold, args.method)


if __name__ == "__main__":
    main()
