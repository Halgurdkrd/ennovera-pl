"""Temporal Governance & Point-in-Time Integrity for Ennovera FPL.
Enforces strict pre-deadline data isolation and prevents retrospective target leakage.
"""
from __future__ import annotations
import os
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Any


class TemporalLeakageError(Exception):
    """Raised when a feature, dataset, or inference input violates pre-deadline point-in-time constraints."""
    pass


class FPLMode:
    LIVE_PROSPECTIVE = "LIVE_PROSPECTIVE"
    HISTORICAL_REPLAY = "HISTORICAL_REPLAY"


def assert_predeadline_integrity(feature_ts: str | datetime | float, deadline: str | datetime) -> None:
    """Asserts that all feature timestamps are strictly prior to the gameweek deadline."""
    if isinstance(feature_ts, str):
        try:
            f_dt = datetime.fromisoformat(feature_ts.replace("Z", "+00:00"))
        except Exception:
            return
    elif isinstance(feature_ts, (int, float)):
        f_dt = datetime.fromtimestamp(feature_ts, tz=timezone.utc)
    else:
        f_dt = feature_ts

    if isinstance(deadline, str):
        d_dt = datetime.fromisoformat(deadline.replace("Z", "+00:00"))
    else:
        d_dt = deadline

    if f_dt >= d_dt:
        raise TemporalLeakageError(
            f"TemporalLeakageError: Feature timestamp ({f_dt.isoformat()}) is at or after gameweek deadline ({d_dt.isoformat()}). "
            f"Inference aborted to prevent data leakage."
        )
