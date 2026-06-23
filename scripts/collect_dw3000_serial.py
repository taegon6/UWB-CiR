from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from uwb_cir.cir_io import save_cir_csv
from uwb_cir.hardware.dw3000_serial import frames_to_matrix, read_frames_from_serial


def main() -> None:
    parser = argparse.ArgumentParser(description="Collect CIR frames from a DW3000 serial bridge")
    parser.add_argument("--port", required=True, help="Serial device path, for example /dev/ttyUSB0 or COM3")
    parser.add_argument("--baudrate", type=int, default=115200)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--max-samples", type=int, default=100)
    parser.add_argument("--timeout", type=float, default=2.0)
    parser.add_argument("--raw-log", type=Path, default=None)
    args = parser.parse_args()

    frames = read_frames_from_serial(
        port=args.port,
        baudrate=args.baudrate,
        max_samples=args.max_samples,
        timeout=args.timeout,
        raw_log=args.raw_log,
    )
    timestamps, matrix = frames_to_matrix(frames)
    save_cir_csv(args.output, matrix, timestamps=timestamps)
    print(f"saved {len(matrix)} CIR frames to {args.output}")


if __name__ == "__main__":
    main()
