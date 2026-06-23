from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Iterable

import numpy as np


@dataclass
class CirFrame:
    """One CIR frame received from a DW3000/DWM3000 serial bridge."""

    timestamp: str
    cir: np.ndarray
    metadata: dict = field(default_factory=dict)


def utc_timestamp() -> str:
    return datetime.utcnow().isoformat(timespec="milliseconds") + "Z"


def parse_cir_line(line: str) -> CirFrame:
    """Parse one serial line into a CirFrame.

    Supported input formats:

    JSON:
        {"timestamp":"...","cir":[0.1,0.2],"rx_power":-70.0}

    CSV:
        timestamp,0.1,0.2,0.3
        0.1,0.2,0.3
    """
    text = line.strip()
    if not text:
        raise ValueError("empty serial line")

    if text.startswith("{"):
        return _parse_json_line(text)
    return _parse_csv_line(text)


def _parse_json_line(text: str) -> CirFrame:
    payload = json.loads(text)
    if "cir" not in payload:
        raise ValueError("JSON line must contain a 'cir' field")

    cir = np.asarray(payload["cir"], dtype=float)
    if cir.ndim != 1:
        raise ValueError("JSON 'cir' field must be a 1D array")

    timestamp = str(payload.get("timestamp") or utc_timestamp())
    metadata = {k: v for k, v in payload.items() if k not in {"timestamp", "cir"}}
    return CirFrame(timestamp=timestamp, cir=cir, metadata=metadata)


def _parse_csv_line(text: str) -> CirFrame:
    parts = [p.strip() for p in text.split(",") if p.strip() != ""]
    if not parts:
        raise ValueError("empty CSV line")

    timestamp = utc_timestamp()
    values = parts

    try:
        float(parts[0])
    except ValueError:
        timestamp = parts[0]
        values = parts[1:]

    if not values:
        raise ValueError("CSV line has no CIR values")

    cir = np.asarray([float(v) for v in values], dtype=float)
    return CirFrame(timestamp=timestamp, cir=cir, metadata={})


def frames_to_matrix(frames: Iterable[CirFrame]) -> tuple[list[str], np.ndarray]:
    frame_list = list(frames)
    if not frame_list:
        raise ValueError("no CIR frames")

    lengths = [len(frame.cir) for frame in frame_list]
    target_len = max(set(lengths), key=lengths.count)

    timestamps: list[str] = []
    rows: list[np.ndarray] = []
    for frame in frame_list:
        cir = frame.cir
        if len(cir) > target_len:
            cir = cir[:target_len]
        elif len(cir) < target_len:
            cir = np.pad(cir, (0, target_len - len(cir)), mode="constant")
        timestamps.append(frame.timestamp)
        rows.append(cir)

    return timestamps, np.vstack(rows)


def read_frames_from_serial(
    port: str,
    baudrate: int = 115200,
    max_samples: int | None = None,
    timeout: float = 2.0,
    raw_log: str | Path | None = None,
) -> list[CirFrame]:
    """Read CIR frames from a serial port.

    This function imports pyserial lazily so unit tests can run without hardware.
    """
    try:
        import serial
    except ImportError as exc:
        raise RuntimeError("pyserial is required. Install requirements.txt first.") from exc

    frames: list[CirFrame] = []
    raw_path = Path(raw_log) if raw_log else None
    if raw_path:
        raw_path.parent.mkdir(parents=True, exist_ok=True)

    with serial.Serial(port=port, baudrate=baudrate, timeout=timeout) as ser:
        while max_samples is None or len(frames) < max_samples:
            raw = ser.readline()
            if not raw:
                continue

            line = raw.decode("utf-8", errors="replace").strip()
            if raw_path:
                with raw_path.open("a", encoding="utf-8") as fp:
                    fp.write(line + "\n")

            try:
                frames.append(parse_cir_line(line))
            except Exception as exc:
                print(f"[parse-skip] {exc}: {line[:120]}")

    return frames
