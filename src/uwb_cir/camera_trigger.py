from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass
class CameraEvent:
    active: bool
    reason: str
    score: float
    timestamp: str


def make_camera_event(reason: str, score: float) -> CameraEvent:
    """Create an event object for later camera handling."""
    return CameraEvent(
        active=True,
        reason=reason,
        score=float(score),
        timestamp=datetime.utcnow().isoformat(timespec="milliseconds") + "Z",
    )
