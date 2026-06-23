from __future__ import annotations

import json
import math
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Iterable, Sequence

import numpy as np


@dataclass
class CirFrame:
    """One CIR frame received from a DW3000/DWM3000 serial bridge."""

    timestamp: str
    cir: np.ndarray
    metadata: dict = field(default_factory=dict)


def utc_timestamp() -> str:
    return datetime.now(UTC).isoformat(timespec="milliseconds").replace("+00:00", "Z")


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

    cir = _cir_values_to_magnitude(payload["cir"])
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

    cir = _csv_values_to_magnitude(values)
    return CirFrame(timestamp=timestamp, cir=cir, metadata={})


def _cir_values_to_magnitude(values: object) -> np.ndarray:
    """Convert real or complex-like CIR values into a 1D magnitude array."""
    if not isinstance(values, Sequence) or isinstance(values, (str, bytes)):
        raise ValueError("CIR values must be a sequence")

    magnitudes: list[float] = []
    for item in values:
        if isinstance(item, dict):
            real = item.get("real", item.get("re", item.get("i")))
            imag = item.get("imag", item.get("im", item.get("q", 0.0)))
            magnitudes.append(math.hypot(float(real), float(imag)))
        elif isinstance(item, Sequence) and not isinstance(item, (str, bytes)):
            pair = list(item)
            if len(pair) == 2:
                magnitudes.append(math.hypot(float(pair[0]), float(pair[1])))
            elif len(pair) == 1:
                magnitudes.append(float(pair[0]))
            else:
                raise ValueError("complex CIR entries must be [real, imag] pairs")
        else:
            magnitudes.append(float(item))
    return np.asarray(magnitudes, dtype=float)


def _csv_values_to_magnitude(values: list[str]) -> np.ndarray:
    parsed = [float(v) for v in values]
    return np.asarray(parsed, dtype=float)


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
    idle_timeout: float | None = None,
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
        raw_path.touch()

    with serial.Serial(port=port, baudrate=baudrate, timeout=timeout) as ser:
        last_rx = datetime.now(UTC)
        while max_samples is None or len(frames) < max_samples:
            raw = ser.readline()
            if not raw:
                if idle_timeout is not None:
                    idle_seconds = (datetime.now(UTC) - last_rx).total_seconds()
                    if idle_seconds >= idle_timeout:
                        break
                continue

            last_rx = datetime.now(UTC)
            line = raw.decode("utf-8", errors="replace").strip()
            if raw_path:
                with raw_path.open("a", encoding="utf-8") as fp:
                    fp.write(line + "\n")

            try:
                frames.append(parse_cir_line(line))
            except Exception as exc:
                print(f"[parse-skip] {exc}: {line[:120]}")

    return frames
