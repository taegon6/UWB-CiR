from __future__ import annotations

import argparse
import sys
from pathlib import Path

import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from uwb_cir.cir_io import load_cir_csv


def main() -> None:
    parser = argparse.ArgumentParser(description="Plot CIR snapshots from CSV")
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--row", type=int, default=0)
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args()

    _, cir = load_cir_csv(args.input)
    if args.row < 0 or args.row >= len(cir):
        raise ValueError("row index out of range")

    plt.figure()
    plt.plot(cir[args.row])
    plt.xlabel("CIR tap index")
    plt.ylabel("Magnitude")
    plt.title(f"CIR snapshot row {args.row}")
    plt.tight_layout()

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(args.output)
        print(f"saved: {args.output}")
    else:
        plt.show()


if __name__ == "__main__":
    main()
