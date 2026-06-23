from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


def main() -> None:
    try:
        from serial.tools import list_ports
    except ImportError as exc:
        raise SystemExit("pyserial is required. Install requirements-hardware.txt first.") from exc

    ports = list(list_ports.comports())
    if not ports:
        print("No serial ports found.")
        return

    for port in ports:
        print(f"{port.device}\t{port.description}\t{port.hwid}")


if __name__ == "__main__":
    main()
