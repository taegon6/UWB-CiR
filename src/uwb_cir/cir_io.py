from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


def load_cir_csv(path: str | Path) -> tuple[pd.Series | None, np.ndarray]:
    """Load CIR snapshots from a CSV file.

    Expected format:
        timestamp,cir_0,cir_1,...,cir_N

    The timestamp column is optional. All columns starting with "cir_" are used
    as CIR taps.
    """
    df = pd.read_csv(path)
    cir_columns = [col for col in df.columns if col.startswith("cir_")]
    if not cir_columns:
        numeric_cols = df.select_dtypes(include="number").columns.tolist()
        if not numeric_cols:
            raise ValueError("No CIR columns found")
        cir_columns = numeric_cols

    timestamps = df["timestamp"] if "timestamp" in df.columns else None
    cir = df[cir_columns].to_numpy(dtype=float)
    return timestamps, cir


def save_cir_csv(path: str | Path, cir: np.ndarray, timestamps: list[str] | None = None) -> None:
    """Save CIR snapshots to a CSV file."""
    arr = np.asarray(cir, dtype=float)
    if arr.ndim == 1:
        arr = arr.reshape(1, -1)
    if arr.ndim != 2:
        raise ValueError("cir must be a 1D or 2D array")

    data = {f"cir_{idx}": arr[:, idx] for idx in range(arr.shape[1])}
    df = pd.DataFrame(data)
    if timestamps is not None:
        if len(timestamps) != len(df):
            raise ValueError("timestamps length must match number of CIR rows")
        df.insert(0, "timestamp", timestamps)
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)


def mean_baseline(cir_snapshots: np.ndarray) -> np.ndarray:
    """Create a baseline CIR from multiple normal snapshots."""
    arr = np.asarray(cir_snapshots, dtype=float)
    if arr.ndim != 2:
        raise ValueError("cir_snapshots must be a 2D array")
    return np.mean(arr, axis=0)
