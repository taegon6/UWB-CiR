from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from uwb_cir.cir_io import load_cir_csv, mean_baseline, save_cir_csv


def main() -> None:
    parser = argparse.ArgumentParser(description="Create a mean baseline CIR from normal samples")
    parser.add_argument("--input", type=Path, required=True, help="Normal CIR CSV file")
    parser.add_argument("--output", type=Path, default=Path("data/processed/baseline.csv"))
    args = parser.parse_args()

    _, cir = load_cir_csv(args.input)
    baseline = mean_baseline(cir)
    save_cir_csv(args.output, baseline)
    print(f"saved baseline: {args.output}")


if __name__ == "__main__":
    main()
